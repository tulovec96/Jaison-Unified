"""
Discord Bot Main Class to interface with Discord

This module provides the main Discord bot implementation for interfacing with
the AI response pipeline. It handles:
- Text message responses via Discord channels
- Voice chat with speech-to-text and text-to-speech
- WebSocket event handling for real-time AI responses
"""

import discord
import asyncio
from asyncio import CancelledError
import os
import json
import requests
import base64
import websockets
import websockets.exceptions
import logging
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum, auto
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from commands import add_commands
from audio.sink import BufferSink, UserAudioBuffer
from audio.source import PCMByteBufferAudio
from utils.config import config
from utils.helper.audio import format_audio
from utils.time import get_current_time

AUDIO_PACKET_SIZE = 4096


class ConnectionState(Enum):
    """Enum representing the current connection state."""

    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()


@dataclass
class JobData:
    """Data class for tracking response jobs."""

    output_text: bool = False
    include_audio: bool = False
    text_channel: Optional[discord.TextChannel] = None
    text_content: str = ""


@dataclass
class ConnectionConfig:
    """Configuration for connection retry behavior."""

    max_retry_attempts: int = 5
    base_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    connection_timeout: float = 30.0


class DiscordBot(discord.Client):
    """
    Discord Bot implementation for AI VTuber interactions.

    This bot handles both text and voice interactions with Discord users,
    forwarding conversations to the AI backend and playing audio responses.

    Attributes:
        config: Bot configuration settings
        connection_state: Current WebSocket connection state to AI backend
        vc: Active voice client connection, if any
    """

    # Constants
    MAX_MESSAGE_LENGTH = 2000  # Discord message limit
    RECONNECT_DELAY = 5.0  # Seconds between reconnect attempts

    def __init__(self):
        if config.opus_filepath is not None:
            discord.opus.load_opus(config.opus_filepath)

        logging.debug("Activating with all intents...")
        super().__init__(intents=discord.Intents.all())
        logging.debug("Reloading command tree...")
        self.tree, self.tree_params = add_commands(self, os.getenv("DISCORD_SERVER_ID"))
        self.config = config

        # Connection tracking
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self._retry_count: int = 0
        self._connection_config = ConnectionConfig()

        # Stubs before readying
        self.job_data: Dict[str, JobData] = {}
        self.jaison_event_task: Optional[asyncio.Task] = None
        self.DEFAULT_TEXT_CHANNEL: Optional[discord.TextChannel] = None

        self.scheduler: Optional[AsyncIOScheduler] = None

        self.vc: Optional[discord.VoiceClient] = None
        self.audio_input_queue: Optional[asyncio.Queue] = None
        self.audio_input_task: Optional[asyncio.Task] = None
        self.audio_output_job_id: Optional[str] = None
        self.audio_output_complete_event: Optional[asyncio.Event] = None
        self.audio_player_task: Optional[asyncio.Task] = None
        self.audio_output: Optional[PCMByteBufferAudio] = None
        self.audio_ready: Optional[asyncio.Event] = None

        self.response_request_id: int = 0

        # Health monitoring
        self._last_heartbeat: float = 0.0
        self._is_healthy: bool = False

    @property
    def is_connected_to_ai(self) -> bool:
        """Check if connected to the AI backend WebSocket."""
        return self.connection_state == ConnectionState.CONNECTED

    @property
    def is_in_voice(self) -> bool:
        """Check if currently connected to a voice channel."""
        return self.vc is not None and self.vc.is_connected()

    @property
    def is_healthy(self) -> bool:
        """Check if the bot is in a healthy operational state."""
        return self._is_healthy and self.is_ready()

    async def get_status(self) -> Dict[str, Any]:
        """Get current bot status for health monitoring."""
        return {
            "is_ready": self.is_ready(),
            "connection_state": self.connection_state.name,
            "is_connected_to_ai": self.is_connected_to_ai,
            "is_in_voice": self.is_in_voice,
            "active_jobs": len(self.job_data),
            "retry_count": self._retry_count,
            "is_healthy": self.is_healthy,
        }

    async def send_text_to_channel(
        self, channel: discord.TextChannel, message: str
    ) -> None:
        """
        Send a text message to a Discord channel, handling message length limits.

        Args:
            channel: Target Discord channel
            message: Message content to send
        """
        if not message:
            return

        # Split long messages to respect Discord's character limit
        for i in range(0, len(message), self.MAX_MESSAGE_LENGTH):
            chunk = message[i : i + self.MAX_MESSAGE_LENGTH]
            await channel.send(chunk)

    # Handler for bot activation
    async def on_ready(self) -> None:
        """Handler called when bot successfully connects to Discord."""
        await self.tree.sync(**self.tree_params)
        logging.debug(f"Command tree resynced with params: {self.tree_params}")

        logging.debug("Starting tasks...")
        self.job_data = {}
        self.jaison_event_task = asyncio.create_task(self._event_listener())
        self.DEFAULT_TEXT_CHANNEL = discord.Object(
            os.getenv("DISCORD_DEFAULT_TEXT_CHANNEL")
        )

        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

        self.vc = None
        self.audio_input_queue = asyncio.Queue()
        self.audio_input_task = asyncio.create_task(self._input_audio_loop())
        self.audio_output_job_id = None
        self.audio_output_complete_event = asyncio.Event()
        self.audio_output_complete_event.set()

        self.audio_player_task = asyncio.create_task(self._play_audio_loop())
        self.audio_output = PCMByteBufferAudio()
        self.audio_ready = asyncio.Event()

        self._is_healthy = True

        logging.info("Discord Bot is ready!")

    async def on_message(self, message: discord.Message) -> None:
        """
        Handler for incoming Discord messages.

        Responds to text messages from users by forwarding them to the AI
        backend for processing.

        Args:
            message: The Discord message received
        """
        # Skip messages from self
        if self.application_id == message.author.id:
            return

        # Generate response
        user = message.author.display_name or message.author.global_name
        content = message.content
        logging.debug(f"Message by user {user}: {content}")

        await message.channel.typing()

        try:
            response = requests.post(
                self.config.jaison_api_endpoint + "/api/context/conversation/text",
                headers={"Content-type": "application/json"},
                json={
                    "user": user,
                    "timestamp": get_current_time(),
                    "content": content,
                },
                timeout=30,
            ).json()
        except requests.RequestException as e:
            logging.error(f"Failed to communicate with AI backend: {e}")
            await self.send_text_to_channel(
                message.channel,
                "Sorry, I'm having trouble connecting to my AI backend right now.",
            )
            return

        if response["status"] != 200:
            reply = f"Failed to start a text message: {response['status']} {response['message']}"
            logging.error(reply)
            await self.send_text_to_channel(message.channel, reply)
            return

        try:
            response = requests.post(
                self.config.jaison_api_endpoint + "/api/response",
                headers={"Content-type": "application/json"},
                json={"include_audio": False},
                timeout=30,
            ).json()
        except requests.RequestException as e:
            logging.error(f"Failed to request AI response: {e}")
            await self.send_text_to_channel(
                message.channel,
                "Sorry, I couldn't generate a response. Please try again.",
            )
            return

        if response["status"] != 200:
            reply = f"Failed to start a texting response job: {response['status']} {response['message']}"
            logging.error(reply)
            await self.send_text_to_channel(message.channel, reply)
            return

        self._add_text_job(
            response["response"]["job_id"],
            output_text=True,
            text_channel=message.channel,
        )

    def _add_text_job(
        self,
        job_id: str,
        output_text: bool = False,
        include_audio: bool = False,
        text_channel: Optional[discord.TextChannel] = None,
    ) -> None:
        """
        Track a text response job for completion handling.

        Args:
            job_id: Unique identifier for the job
            output_text: Whether to output text response
            include_audio: Whether response includes audio
            text_channel: Discord channel to send response to
        """
        self.job_data[job_id] = {
            "output_text": output_text,
            "include_audio": include_audio,
            "text_content": "",
            "text_channel": text_channel,
        }

    async def voice_cb(self) -> None:
        """
        Callback triggered during pause in voice conversation.

        Initiates response generation when user stops speaking.
        """
        self.response_request_id += 1
        await self.audio_input_queue.put(
            {
                "type": "response_request",
                "response_request_id": self.response_request_id,
            }
        )

    def cancel_inflight_response(self) -> None:
        """Cancel any in-progress response job to prevent interruption."""
        if (
            self.audio_output_job_id is not None
            and self.audio_output_complete_event.is_set()
        ):
            try:
                requests.delete(
                    self.config.jaison_api_endpoint + "/api/job",
                    headers={"Content-type": "application/json"},
                    json={
                        "job_id": self.audio_output_job_id,
                        "reason": "Preventing interruption in conversation",
                    },
                    timeout=10,
                )
            except requests.RequestException as e:
                logging.warning(f"Failed to cancel in-flight response: {e}")
            finally:
                self.audio_output_job_id = None

    async def _input_audio_loop(self) -> None:
        """Process incoming audio from voice chat asynchronously."""
        while True:
            try:
                input_d = await self.audio_input_queue.get()
                if input_d["type"] == "audio_input":
                    response = requests.post(
                        self.config.jaison_api_endpoint
                        + "/api/context/conversation/audio",
                        headers={"Content-type": "application/json"},
                        json={
                            "user": input_d["name"],
                            "timestamp": input_d["timestamp"],
                            "audio_bytes": base64.b64encode(
                                input_d["audio_bytes"]
                            ).decode("utf-8"),
                            "sr": input_d["sr"],
                            "sw": input_d["sw"],
                            "ch": input_d["ch"],
                        },
                    ).json()

                    if response["status"] != 200:
                        raise Exception(
                            f"Failed to start add voice data to conversation: {response['status']} {response['message']}"
                        )
                elif input_d["type"] == "response_request":
                    if input_d["response_request_id"] == self.response_request_id:
                        self.cancel_inflight_response()
                        await self.audio_output_complete_event.wait()
                        response = requests.post(
                            self.config.jaison_api_endpoint + "/api/response",
                            headers={"Content-type": "application/json"},
                            json={"include_audio": True},
                        ).json()

                        if response["status"] != 200:
                            raise Exception(
                                f"Failed to start a response job: {response['status']} {response['message']}"
                            )

                        self.audio_output_job_id = response["response"]["job_id"]
                else:
                    raise Exception(f"Unexpected input dictionary in queue: {input_d}")
            except CancelledError:
                raise
            except Exception as err:
                logging.error("Error occured while processing job queue", exc_info=True)

    """Save dialogue per person when the individual finishes speaking"""

    async def user_timeout_cb(self, user_audio_buf: UserAudioBuffer, sink: BufferSink):
        sink.buf_d.pop(user_audio_buf.name)
        await self.audio_input_queue.put(
            {
                "type": "audio_input",
                "name": user_audio_buf.name,
                "timestamp": user_audio_buf.timestamp,
                "audio_bytes": user_audio_buf.audio_bytes,
                "sr": sink.sample_rate,
                "sw": sink.sample_width,
                "ch": sink.channels,
            }
        )

    async def queue_audio(
        self, job_id, audio_bytes: bytes = b"", sr: int = -1, sw: int = -1, ch: int = -1
    ):
        audio = format_audio(audio_bytes, sr, sw, ch)
        self.audio_output.write(audio)
        self.audio_ready.set()

    async def _play_audio_loop(self) -> None:
        """Continuously play audio from the output buffer when available."""
        while True:
            if len(self.audio_output.stream) == 0:
                self.audio_ready.clear()
                await self.audio_ready.wait()

            if self.vc and not self.vc.is_playing():
                self.audio_output_complete_event.clear()
                self.vc.play(self.audio_output, after=self._create_cb())
                await self.audio_output_complete_event.wait()

    def _create_cb(self):
        """Create callback to signal audio playback completion."""

        def cb(error: Optional[Exception] = None) -> None:
            if error:
                logging.error(f"Something went wrong playing audio: {error}")
            self.audio_output_complete_event.set()

        return cb

    async def _event_listener(self) -> None:
        """
        Main event-listening loop for handling AI backend responses.

        Maintains a persistent WebSocket connection to the AI backend,
        processing response events and handling reconnection on failures.
        """
        while True:
            try:
                self.connection_state = ConnectionState.CONNECTING
                async with websockets.connect(
                    self.config.jaison_ws_endpoint,
                    ping_interval=20,
                    ping_timeout=10,
                ) as ws:
                    self.connection_state = ConnectionState.CONNECTED
                    self._retry_count = 0
                    logging.info("Connected to JAIson ws server")

                    while True:
                        data = json.loads(await ws.recv())
                        self._last_heartbeat = time.time()

                        event, status = data[0], data[1]
                        response = event.get("response", {})
                        job_id = response.get("job_id")
                        result = response.get("result", {})

                        if job_id is None:
                            logging.warning(f"Got unexpected event: {str(event)}")
                            continue

                        await self._handle_response_event(
                            event, response, job_id, result
                        )

            except websockets.exceptions.ConnectionClosed as e:
                logging.warning(f"WebSocket connection closed: {e}")
                self.connection_state = ConnectionState.RECONNECTING
                self._retry_count += 1
                delay = min(
                    self._connection_config.base_retry_delay * (2**self._retry_count),
                    self._connection_config.max_retry_delay,
                )
                logging.info(f"Attempting reconnect in {delay:.1f} seconds...")
                self.job_data = {}
                await asyncio.sleep(delay)
            except OSError as e:
                logging.error(
                    f"Server connection error: {e}. Attempting reconnect in 5 seconds",
                    exc_info=True,
                )
                self.connection_state = ConnectionState.RECONNECTING
                self.job_data = {}
                await asyncio.sleep(self.RECONNECT_DELAY)
            except Exception as err:
                logging.error("Event listener encountered an error", exc_info=True)
                self.connection_state = ConnectionState.DISCONNECTED
                self.job_data = {}
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def _handle_response_event(
        self,
        event: Dict[str, Any],
        response: Dict[str, Any],
        job_id: str,
        result: Dict[str, Any],
    ) -> None:
        """
        Handle individual response events from the AI backend.

        Args:
            event: Full event data
            response: Response portion of the event
            job_id: Unique job identifier
            result: Result data from the response
        """
        match event.get("message", ""):
            case "response":
                # Initialize job tracking if this is a new job
                if "start" in response and job_id not in self.job_data:
                    self._add_text_job(
                        job_id,
                        output_text=False,
                        include_audio=response.get("start", {}).get(
                            "include_audio", False
                        ),
                        text_channel=self.DEFAULT_TEXT_CHANNEL,
                    )

                # Accumulate text content
                if "content" in result and job_id in self.job_data:
                    self.job_data[job_id]["text_content"] += " " + result["content"]

                # Queue audio for playback
                if "audio_bytes" in result:
                    await self.queue_audio(
                        job_id,
                        audio_bytes=base64.b64decode(result["audio_bytes"]),
                        sr=result["sr"],
                        sw=result["sw"],
                        ch=result["ch"],
                    )

                # Handle job completion
                if response.get("finished", False) and job_id in self.job_data:
                    if (
                        response.get("success", False)
                        and self.job_data[job_id]["output_text"]
                    ):
                        text_content = (
                            self.job_data[job_id]["text_content"].strip()
                            or "Something went wrong with my AI response"
                        )
                        await self.send_text_to_channel(
                            self.job_data[job_id]["text_channel"],
                            text_content,
                        )
                    # Clean up completed job
                    del self.job_data[job_id]
            case _:
                pass
