import websockets
import websockets.exceptions
import asyncio
import json
import random
import os
import copy
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from utils.logging import logger


class ConnectionState(Enum):
    """Enum representing the current connection state of the VTS plugin."""

    DISCONNECTED = auto()
    CONNECTING = auto()
    AUTHENTICATING = auto()
    CONNECTED = auto()
    RECONNECTING = auto()


@dataclass
class PluginInfo:
    """Data class for VTS plugin metadata."""

    name: str
    developer: str

    def to_dict(self) -> Dict[str, str]:
        return {"pluginName": self.name, "pluginDeveloper": self.developer}


@dataclass
class VTSConfig:
    """Configuration settings for VTS connection."""

    vts_url: str = "ws://localhost:8001"
    jaison_ws_endpoint: str = "ws://localhost:7272/ws"
    hotkey_config_file: str = ""
    max_retry_attempts: int = 5
    base_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    connection_timeout: float = 10.0
    hotkey_queue_size: int = 10


# Make sure VTube Studio is running and API is enabled to port 8001
class VTSHotkeyPlugin:
    """
    VTube Studio Hotkey Plugin for controlling VTuber expressions and animations.

    This plugin connects to VTube Studio's API to trigger hotkeys based on
    detected emotions from the AI response pipeline.

    Attributes:
        config: Configuration dictionary for the plugin
        connection_state: Current connection state of the plugin
        main_ws: WebSocket connection for hotkey commands
        event_ws: WebSocket connection for event subscriptions
    """

    # API Constants
    API_NAME = "VTubeStudioPublicAPI"
    API_VERSION = "1.0"

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._vts_config = VTSConfig(
            vts_url=config.get("vts_url", "ws://localhost:8001"),
            jaison_ws_endpoint=config.get(
                "jaison_ws_endpoint", "ws://localhost:7272/ws"
            ),
            hotkey_config_file=config.get("vts_hotkey_config_file", ""),
        )

        # Connection state tracking
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self._retry_count: int = 0

        # Metadata
        self.main_plugin_info = PluginInfo(
            name="J.A.I.son Hotkeyer", developer="Limit Cant Code"
        )
        self.event_plugin_info = PluginInfo(
            name="J.A.I.son Event Manager", developer="Limit Cant Code"
        )

        # Debugging metrics
        self.debug_unseen_emotions: Optional[Set[str]] = None
        self.debug_unseen_hotkeys: Optional[Set[str]] = None
        self.debug_nonexist_emotions: Optional[Set[str]] = None
        self.debug_nonexist_hotkeys: Optional[Set[str]] = None

        # Animations setup
        self.emotion_map: Dict[str, List[str]] = {}
        self.hotkey_map: Dict[str, List[str]] = {}
        self.animations: List[str] = []
        self.DEFAULT_HOTKEY_SET: Optional[str] = None
        self.hotkey_queue: List[str] = []

        self.run_data: Dict[str, Any] = {}

        self.main_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.event_ws: Optional[websockets.WebSocketClientProtocol] = None
        self._trigger_hotkey_awaitable: Optional[asyncio.Future] = None

        self.hotkey_execution_task: Optional[asyncio.Task] = None
        self.event_listener_task: Optional[asyncio.Task] = None
        self.message_listener_task: Optional[asyncio.Task] = None

        self.response_job_id: Optional[str] = None
        self.response_emotion_gotten: bool = False

        # Health monitoring
        self._last_heartbeat: float = 0.0
        self._is_healthy: bool = False

    def _create_api_request(
        self,
        message_type: str,
        request_id: str = "request",
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a standardized VTS API request."""
        return {
            "apiName": self.API_NAME,
            "apiVersion": self.API_VERSION,
            "requestID": request_id,
            "messageType": message_type,
            "data": data or {},
        }

    async def _connect_with_retry(
        self, url: str, max_attempts: Optional[int] = None
    ) -> websockets.WebSocketClientProtocol:
        """
        Connect to WebSocket with exponential backoff retry logic.

        Args:
            url: WebSocket URL to connect to
            max_attempts: Maximum number of retry attempts (None for infinite)

        Returns:
            Connected WebSocket client

        Raises:
            ConnectionError: If unable to connect after max attempts
        """
        max_attempts = max_attempts or self._vts_config.max_retry_attempts
        attempt = 0

        while True:
            try:
                self.connection_state = ConnectionState.CONNECTING
                ws = await asyncio.wait_for(
                    websockets.connect(url), timeout=self._vts_config.connection_timeout
                )
                self._retry_count = 0
                return ws
            except (
                websockets.exceptions.WebSocketException,
                asyncio.TimeoutError,
                OSError,
            ) as e:
                attempt += 1
                if max_attempts and attempt >= max_attempts:
                    self.connection_state = ConnectionState.DISCONNECTED
                    raise ConnectionError(
                        f"Failed to connect to {url} after {max_attempts} attempts: {e}"
                    )

                delay = min(
                    self._vts_config.base_retry_delay * (2**attempt),
                    self._vts_config.max_retry_delay,
                )
                logger.warning(
                    f"Connection attempt {attempt} failed, retrying in {delay:.1f}s: {e}"
                )
                self.connection_state = ConnectionState.RECONNECTING
                await asyncio.sleep(delay)

    @property
    def is_connected(self) -> bool:
        """Check if both WebSocket connections are active."""
        return (
            self.main_ws is not None
            and self.event_ws is not None
            and self.connection_state == ConnectionState.CONNECTED
        )

    @property
    def is_healthy(self) -> bool:
        """Check if the plugin is in a healthy state."""
        return self._is_healthy and self.is_connected

    async def get_status(self) -> Dict[str, Any]:
        """Get current plugin status for health monitoring."""
        return {
            "connection_state": self.connection_state.name,
            "is_connected": self.is_connected,
            "is_healthy": self.is_healthy,
            "hotkey_queue_length": len(self.hotkey_queue),
            "default_hotkey_set": self.DEFAULT_HOTKEY_SET,
            "emotion_sets_loaded": len(self.emotion_map),
            "hotkey_sets_loaded": len(self.hotkey_map),
        }

    async def start(self) -> None:
        """
        Initialize and start the VTS Hotkey Plugin.

        Sets up WebSocket connections, parses hotkey configuration,
        and starts background tasks for hotkey execution and event listening.
        """
        logger.info("Starting VTS Hotkey Plugin...")

        try:
            self.main_ws = await self._setup_ws(
                os.path.join(os.getcwd(), "tokens", "vts_token_main.txt"),
                self.main_plugin_info,
            )
            self.event_ws = await self._setup_ws(
                os.path.join(os.getcwd(), "tokens", "vts_token_events.txt"),
                self.event_plugin_info,
            )
            self.connection_state = ConnectionState.CONNECTED
            self._is_healthy = True
            logger.info(f"Plugins successfully connected to {self.config['vts_url']}")
        except Exception as e:
            logger.error(f"Failed to connect to VTS: {e}")
            self.connection_state = ConnectionState.DISCONNECTED
            raise

        await self._parse_hotkeys()
        logger.debug("Parsing keys finished with the following results:")
        logger.debug(f"Unused emotions: {self.debug_unseen_emotions}")
        logger.debug(f"Unused hotkeys: {self.debug_unseen_hotkeys}")
        logger.debug(f"Non-existent emotions: {self.debug_nonexist_emotions}")
        logger.debug(f"Non-existent hotkeys: {self.debug_nonexist_hotkeys}")

        self.hotkey_execution_task = asyncio.create_task(self._hotkey_exec_loop())
        logger.debug("Hotkey execution loop task initialized!")
        self.event_listener_task = asyncio.create_task(self._event_listener())
        logger.debug("Event listener task thread initialized!")
        self.message_listener_task = asyncio.create_task(self._message_listener())
        logger.debug("Message listener task initialized!")

        logger.info("VTS Hotkey Plugins successfully initialized!")

    async def stop(self) -> None:
        """Gracefully stop the VTS Hotkey Plugin and clean up resources."""
        logger.info("Stopping VTS Hotkey Plugin...")

        # Cancel all running tasks
        tasks = [
            self.hotkey_execution_task,
            self.event_listener_task,
            self.message_listener_task,
        ]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Close WebSocket connections
        if self.main_ws:
            await self.main_ws.close()
            self.main_ws = None
        if self.event_ws:
            await self.event_ws.close()
            self.event_ws = None

        self.connection_state = ConnectionState.DISCONNECTED
        self._is_healthy = False
        logger.info("VTS Hotkey Plugin stopped")

    async def _setup_ws(
        self, token_filename: str, plugin_info: PluginInfo
    ) -> websockets.WebSocketClientProtocol:
        """
        Setup and authenticate WebSocket connection to VTube Studio API.

        Args:
            token_filename: Path to the file storing the authentication token
            plugin_info: Plugin metadata for authentication

        Returns:
            Authenticated WebSocket connection

        Raises:
            Exception: If authentication fails
        """
        try:
            self.connection_state = ConnectionState.AUTHENTICATING
            plugin_dict = plugin_info.to_dict()

            # Connect to VTS API
            logger.debug(
                f"Setting up websocket {plugin_dict} on {self.config['vts_url']}"
            )
            ws = await websockets.connect(self.config["vts_url"])

            # Authenticate this Plugin
            auth_token: Optional[str] = None
            if os.path.isfile(token_filename):
                # Get token from file if saved previously
                logger.debug(
                    f"Found token file {token_filename}. Authenticating using cached token..."
                )
                with open(token_filename, "r") as token_file:
                    auth_token = token_file.read().strip()

                request = self._create_api_request(
                    "AuthenticationRequest",
                    "authenticate-plugin",
                    {**plugin_dict, "authenticationToken": auth_token},
                )
                await ws.send(json.dumps(request))
                response = json.loads(await ws.recv())
                if response["data"]["authenticated"]:
                    return ws

            logger.debug(
                f"Token file {token_filename} doesn't exist or auth failed. Getting new token..."
            )

            # If no token file or authentication with saved token fails, reauthenticate
            # Authentication request (must accept on VTS GUI)
            request = self._create_api_request(
                "AuthenticationTokenRequest", "get-auth-token", plugin_dict
            )
            await ws.send(json.dumps(request))
            response = json.loads(await ws.recv())

            if "authenticationToken" in response["data"]:
                # Save token to file
                logger.debug(f"Saving new token to {token_filename}")
                auth_token = response["data"]["authenticationToken"]
                os.makedirs(os.path.dirname(token_filename), exist_ok=True)
                with open(token_filename, "w") as token_file:
                    token_file.write(auth_token)
            else:
                raise Exception(f"Failed to get authentication token: {response}")

            # Authenticate with new token
            logger.debug("Authenticating with new token...")
            request = self._create_api_request(
                "AuthenticationRequest",
                "authenticate-plugin",
                {**plugin_dict, "authenticationToken": auth_token},
            )
            await ws.send(json.dumps(request))
            response = json.loads(await ws.recv())
            if not response["data"]["authenticated"]:
                raise Exception(
                    "Failed to authenticate VTS plugin: {}".format(response)
                )

            return ws
        except Exception as err:
            logger.error(f"Failed to setup websocket {plugin_info}: {err}")
            raise err

    # Parse configured hotkeys configuration for use by this plugin
    async def _parse_hotkeys(self):
        try:
            # Info for debugging
            POSSIBLE_EMOTION_LABELS = set(
                [
                    "admiration",
                    "amusement",
                    "approval",
                    "caring",
                    "desire",
                    "excitement",
                    "gratitude",
                    "joy",
                    "love",
                    "optimism",
                    "pride",
                    "anger",
                    "annoyance",
                    "disappointment",
                    "disapproval",
                    "embarrassment",
                    "fear",
                    "disgust",
                    "grief",
                    "nervousness",
                    "remorse",
                    "sadness",
                    "confusion",
                    "curiosity",
                    "realization",
                    "relief",
                    "surprise",
                    "neutral",
                ]
            )
            vts_info = await self._get_vts_info()
            POSSIBLE_HOTKEYS = set([hotkey[0] for hotkey in vts_info["hotkeys"]])
            self.animations = [hotkey[0] for hotkey in vts_info["hotkeys"] if hotkey[1]]

            # Config checks
            if self.config["vts_hotkey_config_file"] is None:
                raise Exception('"vts_hotkey_config_file" no configured...')
            vts_hotkey_config_filepath = os.path.join(
                self.config["vts_hotkey_config_file"]
            )
            if not os.path.isfile(vts_hotkey_config_filepath):
                raise Exception(
                    'Compiled filepath: "{}" does not exist'.format(
                        vts_hotkey_config_filepath
                    )
                )
            elif not self.config["vts_hotkey_config_file"].lower().endswith(".json"):
                raise Exception(
                    'Configured file: "{}" is not a json'.format(
                        self.config["vts_hotkey_config_file"]
                    )
                )

            # Load and parse
            with open(vts_hotkey_config_filepath, "r") as hotkey_file:
                hotkey_dict = json.load(hotkey_file)
            self.debug_unseen_emotions = copy.copy(POSSIBLE_EMOTION_LABELS)
            self.debug_unseen_hotkeys = copy.copy(POSSIBLE_HOTKEYS)
            self.debug_nonexist_emotions = set()
            self.debug_nonexist_hotkeys = set()
            for hotkey_set in hotkey_dict:
                # Add to object map attributes
                self.emotion_map[hotkey_set] = hotkey_dict[hotkey_set]["emotions"]
                self.hotkey_map[hotkey_set] = hotkey_dict[hotkey_set]["hotkeys"]

                # set default set for idle
                if self.DEFAULT_HOTKEY_SET is None:
                    self.DEFAULT_HOTKEY_SET = hotkey_set

                # Tracking unused and non-existing for preemptive debugging
                self.debug_unseen_emotions = self.debug_unseen_emotions - set(
                    hotkey_dict[hotkey_set]["emotions"]
                )
                self.debug_unseen_hotkeys = self.debug_unseen_hotkeys - set(
                    hotkey_dict[hotkey_set]["hotkeys"]
                )
                self.debug_nonexist_emotions = (
                    self.debug_nonexist_emotions
                    | set(hotkey_dict[hotkey_set]["emotions"]) - POSSIBLE_EMOTION_LABELS
                )
                self.debug_nonexist_hotkeys = (
                    self.debug_nonexist_hotkeys
                    | set(hotkey_dict[hotkey_set]["hotkeys"]) - POSSIBLE_HOTKEYS
                )

        except Exception as err:
            logger.error(f"Failed to parse hotkeys: {err}")
            raise err

    # Get general info from VTS
    async def _get_vts_info(self):
        try:
            request = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "SomeID",
                "messageType": "HotkeysInCurrentModelRequest",
                "data": {},
            }

            await self.main_ws.send(json.dumps(request))
            response = json.loads(await self.main_ws.recv())
            output = {
                "model_ready": response["data"]["modelLoaded"],
                "model_name": response["data"]["modelName"],
                "model_id": response["data"]["modelID"],
                "hotkeys": [
                    (hotkey_obj["name"], hotkey_obj["type"] == "TriggerAnimation")
                    for hotkey_obj in response["data"]["availableHotkeys"]
                ],  # hotkey[1] is True when hotkey triggers an animation
            }
        except Exception as err:
            logger.error(f"Failed to get general information from VTS: {err}")
            raise err

        return output

    # Hotkeyer that runs in a separate thread
    # Continuously trigger configured VTube Studio hotkeys queued in self.hotkey_queue
    # Will keep self.hotkey_queue filled with idle animations so queue is never empty
    # Will iterate only once when awoken by _trigger_hotkey_awaitable
    async def _hotkey_exec_loop(self):
        while True:
            logger.debug("Hotkey execution loop starting next iteration...")

            self._trigger_hotkey_awaitable = asyncio.Future()

            # Populate queue initially so there is something to play
            while len(self.hotkey_queue) < 10:
                self.hotkey_queue.append(
                    random.choice(self.hotkey_map[self.DEFAULT_HOTKEY_SET])
                )

            # Request hotkey execution to VTS
            try:
                hotkey = self.hotkey_queue.pop(0)
                logger.debug(f"Requesting next hotkey: {hotkey}")
                request = json.dumps(
                    {
                        "apiName": "VTubeStudioPublicAPI",
                        "apiVersion": "1.0",
                        "requestID": "message_hotkey",
                        "messageType": "HotkeyTriggerRequest",
                        "data": {
                            "hotkeyID": hotkey,
                        },
                    }
                )
                await self.main_ws.send(request)
                response = await self.main_ws.recv()
                response = json.loads(response)

                if "hotkeyID" not in response["data"]:
                    logger.error(f"Failed to play hotkey: {response}")

                # Wait for next call to run hotkey if hotkey was not an animation
                # (non-animations are instant hotkeys that don't need to wait to finish)
                if hotkey in self.animations:
                    await self._trigger_hotkey_awaitable

            except Exception as err:
                logger.error(
                    f"Error occured while playing hotkey this iteration: {err}"
                )

    # Event listener that runs in a separate thread
    # Waits for currently playing animation to end (not overwritten by another animation)
    # Then triggers next hotkey to be pressed
    async def _event_listener(self):
        # Subscribe to hotkey end event
        try:
            request = json.dumps(
                {
                    "apiName": "VTubeStudioPublicAPI",
                    "apiVersion": "1.0",
                    "requestID": "event_subscribe_anim_end",
                    "messageType": "EventSubscriptionRequest",
                    "data": {
                        "eventName": "ModelAnimationEvent",
                        "subscribe": True,
                        "config": {
                            "ignoreLive2DItems": True,
                            "ignoreIdleAnimations": True,
                        },
                    },
                }
            )
            await self.event_ws.send(request)
            response = await self.event_ws.recv()
            response = json.loads(response)

            if "subscribedEventCount" not in response["data"]:
                raise Exception(
                    "VTS Hotkey Thread did not subscribe to event: {}".format(response)
                )

            logger.debug("Event listener subscribed to events")
        except asyncio.InvalidStateError:
            pass
        except Exception as err:
            logger.error(f"Event listener could not subscribe to events: {err}")
            raise err

        # Event loop
        while True:
            event = json.loads(await self.event_ws.recv())
            logger.debug(f"Event received {event}")
            if event["data"]["animationEventType"] == "End":
                self._trigger_hotkey_awaitable.set_result(None)

    def play_hotkey_using_message(self, label: str):
        try:
            logger.debug(f"Playing hotkey on label: {label}")

            # Get hotkeys corresponding to emotion
            set_name = self.DEFAULT_HOTKEY_SET
            for set_key in self.emotion_map:
                if label in self.emotion_map[set_key]:
                    set_name = set_key
                    break

            # Select random hotkey from options
            hotkey = random.choice(self.hotkey_map[set_name])
            logger.debug(f"Selected hotkey: {hotkey}")

            # Add to hotkey queue
            self.hotkey_queue.insert(0, hotkey)
            self._trigger_hotkey_awaitable.set_result(None)
        except asyncio.InvalidStateError:
            pass
        except Exception as err:
            logger.error(f"Error occured while playing animation on message: {err}")
            raise err

    # Interprets emotion of input message and queues the corresponding hotkey in front # TODO
    async def _message_listener(self):
        while True:
            try:
                async with websockets.connect(self.config["jaison_ws_endpoint"]) as ws:
                    logger.info("Connected to JAIson ws server")
                    while True:
                        data = json.loads(await ws.recv())
                        event, status = data[0], data[1]
                        logger.debug(f"Event received {str(event):.200}")

                        status, message, response = (
                            event.get("status", 500),
                            event.get("message", "unknown"),
                            event.get("response", {}),
                        )
                        match message:
                            case "response":
                                if self.response_job_id != response.get("job_id", None):
                                    self.response_job_id = response.get("job_id", None)
                                    self.response_emotion_gotten = False

                                if (not self.response_emotion_gotten) and response.get(
                                    "result", {}
                                ).get("emotion", None):
                                    self.play_hotkey_using_message(
                                        response.get("result", {}).get("emotion", None)
                                    )
                                    self.response_emotion_gotten = True
                            case _:
                                pass
            except OSError:
                logger.error(
                    "Server closed suddenly. Attempting reconnect in 5 seconds",
                    exc_info=True,
                )
                self.run_data = dict()
                await asyncio.sleep(5)
            except Exception as err:
                logger.error("Event listener encountered an error", exc_info=True)
                self.run_data = dict()
