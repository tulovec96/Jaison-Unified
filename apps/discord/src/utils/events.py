"""
Enhanced event handlers for Discord bot with monitoring and logging
"""

import discord
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class EventTracker:
    """Tracks Discord events and metrics"""

    def __init__(self):
        self.message_count = 0
        self.voice_connections = 0
        self.reaction_count = 0
        self.member_join_count = 0
        self.error_count = 0
        self.event_history = []

    def log_event(self, event_type: str, details: dict):
        """Log an event with timestamp"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
        }
        self.event_history.append(entry)
        # Keep only last 1000 events in memory
        if len(self.event_history) > 1000:
            self.event_history.pop(0)

    def get_stats(self) -> dict:
        """Get current event statistics"""
        return {
            "message_count": self.message_count,
            "voice_connections": self.voice_connections,
            "reaction_count": self.reaction_count,
            "member_joins": self.member_join_count,
            "errors": self.error_count,
            "total_events": len(self.event_history),
        }


# Global event tracker instance
event_tracker = EventTracker()


async def on_message_event(message: discord.Message):
    """Handle incoming messages"""
    try:
        event_tracker.message_count += 1
        event_tracker.log_event(
            "message",
            {
                "author": str(message.author),
                "channel": str(message.channel),
                "content_length": len(message.content),
                "has_attachments": len(message.attachments) > 0,
            },
        )
        logger.info(
            f"Message from {message.author} in {message.channel}: {len(message.content)} chars"
        )
    except Exception as e:
        event_tracker.error_count += 1
        logger.error(f"Error in message handler: {str(e)}")


async def on_voice_state_update_event(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    """Handle voice state changes"""
    try:
        if before.channel is None and after.channel is not None:
            # User joined voice
            event_tracker.voice_connections += 1
            event_tracker.log_event(
                "voice_join", {"member": str(member), "channel": str(after.channel)}
            )
            logger.info(f"{member} joined voice channel {after.channel}")

        elif before.channel is not None and after.channel is None:
            # User left voice
            event_tracker.voice_connections = max(
                0, event_tracker.voice_connections - 1
            )
            event_tracker.log_event(
                "voice_leave", {"member": str(member), "channel": str(before.channel)}
            )
            logger.info(f"{member} left voice channel {before.channel}")
    except Exception as e:
        event_tracker.error_count += 1
        logger.error(f"Error in voice state handler: {str(e)}")


async def on_member_join_event(member: discord.Member):
    """Handle new member joins"""
    try:
        event_tracker.member_join_count += 1
        event_tracker.log_event(
            "member_join",
            {
                "member": str(member),
                "guild": str(member.guild),
                "account_created": member.created_at.isoformat(),
            },
        )
        logger.info(f"New member joined: {member} to {member.guild}")
    except Exception as e:
        event_tracker.error_count += 1
        logger.error(f"Error in member join handler: {str(e)}")


async def on_reaction_add_event(reaction: discord.Reaction, user: discord.User):
    """Handle reaction additions"""
    try:
        if user.bot:
            return

        event_tracker.reaction_count += 1
        event_tracker.log_event(
            "reaction_add",
            {
                "emoji": str(reaction.emoji),
                "user": str(user),
                "message_id": reaction.message.id,
                "channel": str(reaction.message.channel),
            },
        )
        logger.info(f"{user} reacted with {reaction.emoji}")
    except Exception as e:
        event_tracker.error_count += 1
        logger.error(f"Error in reaction handler: {str(e)}")


async def on_ready_event(client: discord.Client):
    """Handle bot ready"""
    try:
        event_tracker.log_event(
            "bot_ready",
            {
                "bot_name": str(client.user),
                "guild_count": len(client.guilds),
                "startup_time": datetime.now().isoformat(),
            },
        )
        logger.info(f"Bot ready as {client.user} in {len(client.guilds)} guilds")
    except Exception as e:
        event_tracker.error_count += 1
        logger.error(f"Error in ready handler: {str(e)}")


def get_event_tracker() -> EventTracker:
    """Get the global event tracker"""
    return event_tracker
