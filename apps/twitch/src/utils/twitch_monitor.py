"""
Twitch Context Monitor for tracking chat history and stream events.

This module provides the TwitchContextMonitor class for interfacing with Twitch
to track chat history and stream events using WebSockets. It uses Twitch's
EventSub API for real-time event notifications.

For reference: https://dev.twitch.tv/docs/eventsub/

We get user app tokens using OAuth code grant flow:
https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#authorization-code-grant-flow

Usage:
- FOR CHAT HISTORY: call self.get_chat_history()
- FOR TWITCH EVENTS: subscribe to events through the WebSocket connection
"""

import websockets
import websockets.exceptions
import requests
import json
import urllib
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import yaml
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from enum import IntEnum, auto

from utils.logging import logger
from utils.helper import get_twitch_sub_tier


class ChatModeEnum(IntEnum):
    """
    Enum defining chat interaction modes.

    ALL: Respond to all chat messages
    KEYWORD: Only respond to messages containing configured keywords
    HIGHLIGHT: Only respond to highlighted messages and bit donations
    BITS: Only respond to bit donations
    DISABLE: Disable chat responses entirely
    """

    ALL = 1
    KEYWORD = 2
    HIGHLIGHT = 3
    BITS = 4
    DISABLE = 5


class ConnectionState(IntEnum):
    """Enum representing the current connection state."""

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    RECONNECTING = 3


@dataclass
class TwitchConfig:
    """Configuration settings for Twitch connection."""

    broadcaster_id: str
    bot_id: str
    jaison_api_endpoint: str
    jaison_ws_endpoint: str
    chat_mode: ChatModeEnum = ChatModeEnum.HIGHLIGHT
    keywords: List[str] = field(default_factory=list)
    bits_threshold: int = 0
    max_chat_length: int = 40
    max_retry_attempts: int = 5
    base_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    summary_interval_minutes: int = 5


@dataclass
class ChatMessage:
    """Data class for storing chat messages."""

    name: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "message": self.message}


class TwitchContextMonitor:
    """
    Monitor Twitch chat and stream events for AI integration.

    This class maintains a connection to Twitch's EventSub API to receive
    real-time notifications about chat messages, follows, subscriptions,
    raids, and other stream events. It also summarizes chat activity
    periodically using the AI backend.

    Attributes:
        connection_state: Current WebSocket connection state
        chat_history: Recent chat messages
        chat_summary: AI-generated summary of recent chat
    """

    # Class constants
    CLIENT_ID = os.getenv("TWITCH_APP_ID")
    CLIENT_SECRET = os.getenv("TWITCH_APP_TOKEN")
    MAX_CHAT_LENGTH = 40

    # OAuth URLs
    OAUTH_REDIRECT_CODE = "http://localhost:5000/auth/redirect/code"
    OAUTH_REDIRECT_TOKENS = "http://localhost:5000/auth/redirect/tokens"
    OAUTH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    OAUTH_AUTHORIZE_URL = "https://id.twitch.tv/oauth2/authorize?{}".format(
        urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "redirect_uri": OAUTH_REDIRECT_CODE,
                "response_type": "code",
                "scope": "user:read:chat moderator:read:followers bits:read channel:read:subscriptions channel:read:charity channel:read:hype_train channel:read:redemptions",
            }
        )
    )

    # AI Summarization prompt
    SUMMARIZATION_PROMPT = """
You are generating a summary of a Twitch chat making use of the previously generated summary and all the latest Twitch chat messages since then.
The user will provide the summary under the header "### Previous summary ###" and the latest messages under "### New messages ###"

For example, the user may input:

### Previous summary ###
The chat is all saying hi.

### New messages ###
[limit]: What are we doing this stream?


You will then output something like the following:

Chat is now asking what is going on in stream.


Please keep these summaries to 6 sentences or less.
"""

    def __init__(self):
        """Initialize the Twitch Context Monitor."""
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.TOKEN_FILE = os.path.join(os.getcwd(), "tokens", "twitch_api_tokens.json")

        # Parse configuration
        self._twitch_config = TwitchConfig(
            broadcaster_id=str(self.config["twitch-target-id"]),
            bot_id=str(self.config["twitch-bot-id"]),
            jaison_api_endpoint=str(self.config["jaison-api-endpoint"]),
            jaison_ws_endpoint=str(self.config["jaison-ws-endpoint"]),
            chat_mode=getattr(
                ChatModeEnum, str(self.config.get("chat-mode", "HIGHLIGHT"))
            ),
            keywords=[
                k.strip()
                for k in self.config.get("chat-keywords", "").split(",")
                if k.strip()
            ],
            bits_threshold=self.config.get("chat-bits-threshold", 0),
        )

        # Legacy compatibility
        self.broadcaster_id = self._twitch_config.broadcaster_id
        self.user_id = self._twitch_config.bot_id
        self.jaison_api_endpoint = self._twitch_config.jaison_api_endpoint
        self.jaison_ws_endpoint = self._twitch_config.jaison_ws_endpoint

        # Token management
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self._load_tokens()

        # Chat settings
        self.chatting_method = self._twitch_config.chat_mode
        self.keywords = self._twitch_config.keywords
        self.bits_threshold = self._twitch_config.bits_threshold

        # Connection state tracking
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self._retry_count: int = 0

        # WebSocket references
        self.event_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.event_sub_data: List[Dict[str, Any]] = []

        # Health monitoring
        self._last_heartbeat: float = 0.0
        self._is_healthy: bool = False

    @property
    def is_connected(self) -> bool:
        """Check if the WebSocket connection is active."""
        return self.connection_state == ConnectionState.CONNECTED

    @property
    def is_healthy(self) -> bool:
        """Check if the monitor is in a healthy operational state."""
        return self._is_healthy and self.is_connected

    async def get_status(self) -> Dict[str, Any]:
        """Get current monitor status for health checking."""
        return {
            "connection_state": self.connection_state.name,
            "is_connected": self.is_connected,
            "is_healthy": self.is_healthy,
            "chat_mode": self.chatting_method.name,
            "chat_history_length": len(getattr(self, "chat_history", [])),
            "retry_count": self._retry_count,
        }

    async def run(self) -> None:
        """
        Start the Twitch Context Monitor.

        Initializes chat summary context, starts the event loop,
        and begins periodic chat summarization.
        """
        logger.info("Starting Twitch Context Monitor...")

        # Twitch chat summary context setup
        self.context_id = "twitch-chat-monitor-lcc"
        self.context_name = "Twitch Chat Summary"
        self.context_description = """This is a summary of changes in Twitch chat since the last Twitch Chat Summary."""
        self.chat_history: List[Dict[str, str]] = []

        self.chat_summary: str = "No previous summary"
        summary_interval = self.config.get("summary-interval", 0)

        if summary_interval > 0:
            self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
            self.scheduler.start()
            self.chat_update_timer = self.scheduler.add_job(
                self._interval_chat_context_updater,
                "interval",
                seconds=summary_interval,
                args=[],
                id="chat_update_timer",
                replace_existing=True,
            )
            logger.debug(
                f"Chat summary scheduler started with {summary_interval}s interval"
            )

        # Twitch event sub setup
        self.event_ws = None
        self.twitch_event_task = asyncio.create_task(self._event_loop())
        self._is_healthy = True

        logger.info("Twitch Context Monitor started successfully!")

    async def stop(self) -> None:
        """Gracefully stop the Twitch Context Monitor."""
        logger.info("Stopping Twitch Context Monitor...")

        # Cancel event task
        if hasattr(self, "twitch_event_task") and self.twitch_event_task:
            self.twitch_event_task.cancel()
            try:
                await self.twitch_event_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket
        if self.event_ws:
            await self.event_ws.close()
            self.event_ws = None

        # Stop scheduler
        if hasattr(self, "scheduler") and self.scheduler:
            self.scheduler.shutdown()

        self.connection_state = ConnectionState.DISCONNECTED
        self._is_healthy = False
        logger.info("Twitch Context Monitor stopped")

    def _load_tokens(self) -> bool:
        """
        Load OAuth tokens from file if it exists.

        Returns:
            True if tokens were loaded successfully, False otherwise.
        """
        try:
            if not os.path.isfile(self.TOKEN_FILE):
                logger.warning(
                    f"Token file {self.TOKEN_FILE} not found. "
                    f"Please authenticate at {self.OAUTH_AUTHORIZE_URL}"
                )
                return False

            with open(self.TOKEN_FILE, "r") as f:
                token_o = json.load(f)
                self.access_token = token_o.get("access_token")
                self.refresh_token = token_o.get("refresh_token")

            if not self.access_token or not self.refresh_token:
                logger.error("Token file is missing required fields")
                return False

            logger.debug("OAuth tokens loaded successfully")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Token file is malformed: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Failed to load tokens from {self.TOKEN_FILE}: {e}. "
                f"Please reauthenticate at {self.OAUTH_AUTHORIZE_URL}"
            )
            return False

    def _refresh_tokens(self) -> bool:
        """
        Use refresh token to obtain new access/refresh token pair.

        Returns:
            True if tokens were refreshed successfully, False otherwise.
        """
        try:
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                params={
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            self.set_tokens(token_data["access_token"], token_data["refresh_token"])
            logger.debug("OAuth tokens refreshed successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to refresh tokens: {e}")
            return False
        except KeyError as e:
            logger.error(f"Invalid token response format: {e}")
            return False

    def set_tokens_from_code(self, code: str) -> bool:
        """
        Use authorization code to obtain access/refresh token pair.

        Args:
            code: OAuth authorization code from Twitch redirect

        Returns:
            True if tokens were set successfully, False otherwise.
        """
        try:
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                params={
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.OAUTH_REDIRECT_TOKENS,
                },
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            self.set_tokens(token_data["access_token"], token_data["refresh_token"])
            logger.info("OAuth tokens obtained from authorization code")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to get tokens from code: {e}")
            return False
        except KeyError as e:
            logger.error(f"Invalid token response format: {e}")
            return False

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """
        Save access/refresh token pair to file and reload.

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
        """
        os.makedirs(os.path.dirname(self.TOKEN_FILE), exist_ok=True)
        with open(self.TOKEN_FILE, "w") as f:
            json.dump(
                {"access_token": access_token, "refresh_token": refresh_token},
                f,
                indent=4,
            )
        self._load_tokens()

    # Attempts subscription using Twitch Events Sub API
    # For reference: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/
    def _subscribe(self):
        if self.access_token is None:
            logger.warning(
                "Can't subscribe to events until authenticated. Please authenticate at {}".format(
                    self.OAUTH_AUTHORIZE_URL
                )
            )
            raise Exception("Can't complete subscription")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.CLIENT_ID,
            "Content-Type": "application/json",
        }
        for data in self.event_sub_data:
            response = requests.post(
                "https://api.twitch.tv/helix/eventsub/subscriptions",
                headers=headers,
                json=data,
            )
            if (
                response.status_code == 401
            ):  # In case forbidden, refresh tokens and retry once
                logger.debug("Forbidden subscription request. Refreshing tokens")
                self._refresh_tokens()
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Client-Id": self.CLIENT_ID,
                    "Content-Type": "application/json",
                }
                response = requests.post(
                    "https://api.twitch.tv/helix/eventsub/subscriptions",
                    headers=headers,
                    json=data,
                )

            if response.status_code != 202:  # If not successful, signal failure
                logger.warning(f"Failing to subscribe to event: {response.json()}")
                raise Exception("Can't complete subscription")

    # Connect a new socket and resubscribe to events on its new session
    async def _setup_socket(self, reconnect_url: str = None):
        try:
            new_ws = await websockets.connect(
                reconnect_url
                or "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=10"
            )
            welcome_msg = json.loads(await new_ws.recv())
            if self.event_ws:
                await self.event_ws.close()
            self.event_ws = new_ws
            logger.debug(f"Connected new subscription events websocket: {welcome_msg}")
            self.session_id = welcome_msg["payload"]["session"]["id"]

            # List of subscriptables: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#subscription-types
            self.event_sub_data = [
                {
                    "type": "channel.chat.message",  # scope: user:read:chat
                    "version": "1",
                    "condition": {
                        "broadcaster_user_id": self.broadcaster_id,
                        "user_id": self.user_id,
                    },
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.follow",  # scope: moderator:read:followers
                    "version": "2",
                    "condition": {
                        "broadcaster_user_id": self.broadcaster_id,
                        "moderator_user_id": self.broadcaster_id,
                    },
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.subscribe",  # scope: channel:read:subscriptions
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.subscription.gift",  # scope: channel:read:subscriptions
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.subscription.message",  # scope: None
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.raid",  # scope: None
                    "version": "1",
                    "condition": {"to_broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.charity_campaign.donate",  # scope: channel:read:charity
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                # hype train
                {
                    "type": "channel.hype_train.begin",  # scope: channel:read:hype_train
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.hype_train.end",  # scope: channel:read:hype_train
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.bits.use",  # scope: bits:read
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
                {
                    "type": "channel.channel_points_automatic_reward_redemption.add",  # scope: channel:read:redemptions
                    "version": "1",
                    "condition": {"broadcaster_user_id": self.broadcaster_id},
                    "transport": {"method": "websocket", "session_id": self.session_id},
                },
            ]

            self._subscribe()
            return True
        except Exception as err:
            logger.error(
                "Failed to setup Twitch subscribed events websocket: {}".format(err)
            )
            return False

    # Wrapper for self._setup_socket to reattempt until success, retrying after delay on failure
    async def setup_socket(self, reconnect_url: str = None):
        while True:
            logger.debug("Attempting to setup Twitch subscribed events websocket...")
            if await self._setup_socket(reconnect_url=reconnect_url):
                break
            time.sleep(5)

    def _register_chat_context(self):
        logger.critical("Registering context")
        response = requests.put(
            self.jaison_api_endpoint + "/api/context/custom",
            headers={"Content-type": "application/json"},
            json={
                "context_id": self.context_id,
                "context_name": self.context_name,
                "context_description": self.context_description,
            },
        )

        logger.critical(response.json())

        if response.status_code != 200:
            raise Exception(
                f"Failed to register chat context: {response.status_code} {response.reason}"
            )

    def _generate_summary_input(self):
        content = ""
        for msg_o in self.chat_history:
            content += "{}: {}\n".format(msg_o["name"], msg_o["message"])

        result = "### Previous summary ###\n\n{prev_summary}\n### New messages ###\n\n{new_messages}".format(
            prev_summary=self.chat_summary, new_messages=content
        )
        logger.debug(f"Generated summary input: {result}")
        return result

    async def _interval_chat_context_updater(self):
        try:
            if len(self.chat_history) == 0:
                return

            # generate new summary
            summary = ""

            async with websockets.connect(self.jaison_ws_endpoint) as ws:
                job_request_response = requests.post(
                    self.jaison_api_endpoint + "/api/operations/use",
                    headers={"Content-type": "application/json"},
                    json={
                        "role": "mcp",
                        "payload": {
                            "instruction_prompt": self.SUMMARIZATION_PROMPT,
                            "messages": [
                                {
                                    "type": "raw",
                                    "message": self._generate_summary_input(),
                                }
                            ],
                        },
                    },
                )
                if job_request_response.status_code != 200:
                    raise Exception(
                        f"Failed to register chat context: {job_request_response.status_code} {job_request_response.reason}"
                    )

                parsed_job_request = job_request_response.json()
                job_id = parsed_job_request["response"]["job_id"]

                while True:
                    data = json.loads(await ws.recv())
                    event, status = data[0], data[1]
                    if event.get("response", {}).get("job_id") == job_id:
                        if not event.get("response", {}).get("finished", False):
                            summary += (
                                event["response"].get("result", {}).get("content", "")
                            )
                        elif event.get("response", {}).get(
                            "finished", False
                        ) and not event.get("response", {}).get("success", False):
                            raise Exception(
                                f"Failed to summarize chat: {job_request_response.status_code} {job_request_response.reason}"
                            )
                        else:
                            break

            # save new summary
            logger.debug(f"Got new twitch chat summary: {summary}")
            self.chat_summary = summary

            # chat history
            self.chat_history.clear()

            # send new summary
            if summary:
                async with websockets.connect(self.jaison_ws_endpoint) as ws:
                    response = requests.post(
                        self.jaison_api_endpoint + "/api/context/custom",
                        headers={"Content-type": "application/json"},
                        json={
                            "context_id": self.context_id,
                            "context_contents": summary,
                            "timestamp": datetime.now().timestamp(),
                        },
                    )

                    if response.status_code != 200:
                        raise Exception(f"{response.status_code} {response.reason}")

                    parsed_response = response.json()
                    job_id = parsed_response["response"]["job_id"]
                    while True:
                        data = json.loads(await ws.recv())
                        event, status = data[0], data[1]
                        if event.get("response", {}).get("job_id") == job_id:
                            payload = event.get("response", {})
                            if "success" in payload:
                                if not payload["success"]:
                                    self._register_chat_context()
                                    break
                                else:
                                    break
        except Exception as err:
            logger.error(f"Failed to update Twitch chat context", exc_info=True)

    def request_jaison(self, request_msg):
        response = requests.post(
            self.jaison_api_endpoint + "/api/context/request",
            headers={"Content-type": "application/json"},
            json={"content": request_msg},
        ).json()

        if response["status"] == 500:
            logger.error(f"Failed to send a request: {response['message']}")
            raise Exception(response["message"])

    def converse_jaison(self, user, message):
        response = requests.post(
            self.jaison_api_endpoint + "/api/context/conversation/text",
            headers={"Content-type": "application/json"},
            json={
                "user": user,
                "timestamp": datetime.now().timestamp(),
                "content": message,
            },
        )
        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")

    # Main event loop for handling incoming events from Twitch
    async def _event_loop(self):
        logger.debug("Started event loop!")
        await self.setup_socket()
        logger.info("Twitch Monitor Ready")
        while True:
            try:
                event = json.loads(await self.event_ws.recv())
                logger.debug("Event loop received event: {}".format(event))
                if (
                    "metadata" not in event or "payload" not in event
                ):  # Expect message to have a specific structure
                    logger.warning("Unexpected event: {}".format(event))
                if (
                    event["metadata"]["message_type"] == "notification"
                ):  # Handling subscribed events
                    event = event["payload"]
                    if "subscription" in event:
                        try:
                            if event["subscription"]["type"] == "channel.chat.message":
                                name = event["event"]["chatter_user_name"]
                                message = event["event"]["message"]["text"]
                                self.chat_history.append(
                                    {"name": name, "message": message}
                                )
                                self.chat_history = self.chat_history[
                                    -(self.MAX_CHAT_LENGTH) :
                                ]

                                if self.chatting_method <= ChatModeEnum.ALL:
                                    self.converse_jaison(name, message)
                                elif self.chatting_method <= ChatModeEnum.KEYWORD:
                                    for keyword in self.keywords:
                                        if keyword in message:
                                            self.converse_jaison(name, message)
                                            break
                            elif event["subscription"]["type"] == "channel.follow":
                                self.request_jaison(
                                    "Say thank you to {} for the follow.".format(
                                        event["event"]["user_name"]
                                    )
                                )
                            elif event["subscription"]["type"] == "channel.subscribe":
                                if not event["event"]["is_gift"]:
                                    self.request_jaison(
                                        "Say thank you to {} for the tier {} sub.".format(
                                            event["event"]["user_name"],
                                            get_twitch_sub_tier(event["event"]["tier"]),
                                        )
                                    )
                            elif (
                                event["subscription"]["type"]
                                == "channel.subscription.gift"
                            ):
                                message = (
                                    "Say thank you"
                                    if event["event"]["is_anonymous"]
                                    else "Say thank you to {}".format(
                                        event["event"]["user_name"]
                                    )
                                )
                                message += " for the {} tier {} gifted subs.".format(
                                    event["event"]["cumulative_total"],
                                    get_twitch_sub_tier(event["event"]["tier"]),
                                )
                                self.request_jaison(message)
                            elif (
                                event["subscription"]["type"]
                                == "channel.subscription.message"
                            ):
                                self.request_jaison(
                                    "{} says {}. Thank them for their tier {} sub.".format(
                                        event["event"]["user_name"],
                                        event["event"]["message"]["text"],
                                        get_twitch_sub_tier(event["event"]["tier"]),
                                    )
                                )
                            elif event["subscription"]["type"] == "channel.raid":
                                self.request_jaison(
                                    "Thank {} for raiding you with {} viewers.".format(
                                        event["event"]["from_broadcaster_user_name"],
                                        event["event"]["viewers"],
                                    )
                                )
                            elif (
                                event["subscription"]["type"]
                                == "channel.charity_campaign.donate"
                            ):
                                self.request_jaison(
                                    "Thank {} for donating {} {} to {}.".format(
                                        event["event"]["user_name"],
                                        event["event"]["amount"]["value"],
                                        event["event"]["amount"]["currency"],
                                        event["event"]["charity_name"],
                                    )
                                )
                            elif (
                                event["subscription"]["type"]
                                == "channel.hype_train.begin"
                            ):
                                self.request_jaison(
                                    "A Twitch hype train started. Hype up the hype train."
                                )
                            elif (
                                event["subscription"]["type"]
                                == "channel.hype_train.end"
                            ):
                                self.request_jaison(
                                    "The Twitch hype train has finished  at level {}. Thank the viewers for all their effort.".format(
                                        event["event"]["level"]
                                    )
                                )
                            elif (
                                self.chatting_method <= ChatModeEnum.HIGHLIGHT
                                and event["subscription"]["type"]
                                == "channel.channel_points_automatic_reward_redemption.add"
                            ):
                                if (
                                    event["event"]["reward"]["type"]
                                    == "send_highlighted_message"
                                ):
                                    user = event["event"]["user_name"]
                                    message = event["event"]["message"]["text"]
                                    self.converse_jaison(user, message)
                            elif event["subscription"]["type"] == "channel.bits.use":
                                user = event["event"]["user_name"]
                                bits_spent = event["event"]["bits"]
                                byte_redemption_type = event["event"][
                                    "type"
                                ]  # cheer for message or powerup for whatever
                                if (
                                    self.chatting_method <= ChatModeEnum.HIGHLIGHT
                                    and byte_redemption_type == "cheer"
                                    and bits_spent >= self.bits_threshold
                                ):
                                    message = event["event"]["message"]["text"]
                                    self.converse_jaison(
                                        user, f"(spent {bits_spent} bits) {message}"
                                    )
                                else:
                                    message = (
                                        "Say thank you to {} for the {} bits.".format(
                                            event["event"]["user_name"],
                                            event["event"]["bits"],
                                        )
                                    )
                                    self.request_jaison(message)
                            else:
                                logger.warning(
                                    "Unhandled event subscription: {}".format(event)
                                )
                        except Exception as err:
                            logger.error(
                                "Request failed for event: {}".format(event),
                                exc_info=True,
                            )
                    else:
                        logger.warning("Unknown event response: {}".format(event))
                elif (
                    event["metadata"]["message_type"] == "session_reconnect"
                ):  # Handling reconnect request
                    self.setup_socket(event["payload"]["session"]["reconnect_url"])
                elif (
                    event["metadata"]["message_type"] == "revocation"
                ):  # Notified of a subscription being removed by Twitch
                    logger.warning(
                        "A Twitch event subscrption has been revoked: {}".format(
                            event["payload"]["subscription"]["type"]
                        )
                    )
            except Exception as err:
                # Event must continue to run even in event of error
                logger.error(f"Event loop ran into an error: {err}")
