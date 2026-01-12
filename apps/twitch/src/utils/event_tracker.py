"""
Twitch event tracking and analytics
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

logger = logging.getLogger(__name__)


class TwitchEventType:
    """Twitch EventSub event types"""

    STREAM_ONLINE = "stream.online"
    STREAM_OFFLINE = "stream.offline"
    CHANNEL_UPDATE = "channel.update"
    CHANNEL_FOLLOW = "channel.follow"
    CHANNEL_SUBSCRIBE = "channel.subscribe"
    CHANNEL_CHEER = "channel.cheer"
    CHANNEL_RAID = "channel.raid"
    CHANNEL_HYPE_TRAIN_BEGIN = "channel.hype_train.begin"
    CHANNEL_HYPE_TRAIN_END = "channel.hype_train.end"
    CHANNEL_CHARITY_DONATE = "channel.charity_donate"
    CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION = (
        "channel.channel_points_custom_reward_redemption.add"
    )


class TwitchEvent:
    """Represents a Twitch event"""

    def __init__(
        self,
        event_type: str,
        timestamp: datetime,
        user: Optional[str] = None,
        data: Optional[Dict] = None,
    ):
        self.event_type = event_type
        self.timestamp = timestamp
        self.user = user
        self.data = data or {}

    def __repr__(self):
        return f"TwitchEvent({self.event_type}, user={self.user}, {self.timestamp.isoformat()})"


class TwitchEventTracker:
    """Track and analyze Twitch events"""

    def __init__(self, max_history: int = 1000):
        self.event_history: deque = deque(maxlen=max_history)
        self.stats = {
            "followers": 0,
            "subscribers": 0,
            "raids": 0,
            "cheers": 0,
            "hype_trains": 0,
            "custom_rewards": 0,
            "charity_donations": 0,
        }
        self.event_counts = {}
        self.user_contributions: Dict[str, Dict] = {}
        self.ongoing_hype_train = False

    def track_event(self, event: TwitchEvent):
        """Track a new event"""
        self.event_history.append(event)

        # Update event counts
        if event.event_type not in self.event_counts:
            self.event_counts[event.event_type] = 0
        self.event_counts[event.event_type] += 1

        # Update stats
        self._update_stats(event)

        # Track user contributions
        if event.user:
            self._track_user_contribution(event)

        logger.info(f"Event tracked: {event}")

    def _update_stats(self, event: TwitchEvent):
        """Update statistics based on event type"""
        if event.event_type == TwitchEventType.CHANNEL_FOLLOW:
            self.stats["followers"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_SUBSCRIBE:
            self.stats["subscribers"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_RAID:
            self.stats["raids"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_CHEER:
            bits = event.data.get("bits", 0)
            self.stats["cheers"] += bits
        elif event.event_type == TwitchEventType.CHANNEL_HYPE_TRAIN_BEGIN:
            self.ongoing_hype_train = True
            self.stats["hype_trains"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_HYPE_TRAIN_END:
            self.ongoing_hype_train = False
        elif (
            event.event_type == TwitchEventType.CHANNEL_POINTS_CUSTOM_REWARD_REDEMPTION
        ):
            self.stats["custom_rewards"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_CHARITY_DONATE:
            self.stats["charity_donations"] += 1

    def _track_user_contribution(self, event: TwitchEvent):
        """Track individual user contributions"""
        if event.user not in self.user_contributions:
            self.user_contributions[event.user] = {
                "follows": 0,
                "subs": 0,
                "raids": 0,
                "bits": 0,
                "last_event": None,
            }

        user_data = self.user_contributions[event.user]
        user_data["last_event"] = event.timestamp

        if event.event_type == TwitchEventType.CHANNEL_FOLLOW:
            user_data["follows"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_SUBSCRIBE:
            user_data["subs"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_RAID:
            user_data["raids"] += 1
        elif event.event_type == TwitchEventType.CHANNEL_CHEER:
            user_data["bits"] += event.data.get("bits", 0)

    def get_top_contributors(self, limit: int = 10) -> List[tuple]:
        """Get top contributing users"""
        contributors = []
        for user, data in self.user_contributions.items():
            score = (
                data["follows"] * 1
                + data["subs"] * 10
                + data["raids"] * 20
                + (data["bits"] / 100)  # Normalize bits
            )
            contributors.append((user, score, data))

        return sorted(contributors, key=lambda x: x[1], reverse=True)[:limit]

    def get_top_raiders(self, limit: int = 5) -> List[tuple]:
        """Get users who have raided the most"""
        raiders = [
            (user, data["raids"])
            for user, data in self.user_contributions.items()
            if data["raids"] > 0
        ]
        return sorted(raiders, key=lambda x: x[1], reverse=True)[:limit]

    def get_top_subscribers(self, limit: int = 5) -> List[tuple]:
        """Get users with most subscriptions"""
        subs = [
            (user, data["subs"])
            for user, data in self.user_contributions.items()
            if data["subs"] > 0
        ]
        return sorted(subs, key=lambda x: x[1], reverse=True)[:limit]

    def get_top_cheerers(self, limit: int = 5) -> List[tuple]:
        """Get users who have donated most bits"""
        cheerers = [
            (user, data["bits"])
            for user, data in self.user_contributions.items()
            if data["bits"] > 0
        ]
        return sorted(cheerers, key=lambda x: x[1], reverse=True)[:limit]

    def get_stream_stats(self) -> Dict:
        """Get overall stream statistics"""
        recent_events = list(self.event_history)

        return {
            "total_followers": self.stats["followers"],
            "total_subscribers": self.stats["subscribers"],
            "total_raids": self.stats["raids"],
            "total_bits_cheered": self.stats["cheers"],
            "hype_trains_triggered": self.stats["hype_trains"],
            "custom_rewards_redeemed": self.stats["custom_rewards"],
            "charity_donations": self.stats["charity_donations"],
            "ongoing_hype_train": self.ongoing_hype_train,
            "top_event": (
                max(self.event_counts, key=self.event_counts.get)
                if self.event_counts
                else None
            ),
            "total_events": len(self.event_history),
            "unique_contributors": len(self.user_contributions),
        }

    def get_recent_events(self, limit: int = 20) -> List[TwitchEvent]:
        """Get recent events"""
        return list(reversed(list(self.event_history)[-limit:]))

    def get_events_by_type(self, event_type: str) -> List[TwitchEvent]:
        """Get events of specific type"""
        return [e for e in self.event_history if e.event_type == event_type]


class StreamSessionTracker:
    """Track individual stream sessions"""

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def start_session(self, stream_id: str):
        """Start a new stream session"""
        self.sessions[stream_id] = {
            "start_time": datetime.now(),
            "end_time": None,
            "events": [],
            "status": "online",
        }
        logger.info(f"Stream session started: {stream_id}")

    def end_session(self, stream_id: str):
        """End a stream session"""
        if stream_id in self.sessions:
            self.sessions[stream_id]["end_time"] = datetime.now()
            self.sessions[stream_id]["status"] = "offline"
            logger.info(f"Stream session ended: {stream_id}")

    def add_event_to_session(self, stream_id: str, event: TwitchEvent):
        """Add event to stream session"""
        if stream_id in self.sessions:
            self.sessions[stream_id]["events"].append(event)

    def get_session_duration(self, stream_id: str) -> Optional[float]:
        """Get session duration in seconds"""
        if stream_id not in self.sessions:
            return None

        session = self.sessions[stream_id]
        end_time = session["end_time"] or datetime.now()
        return (end_time - session["start_time"]).total_seconds()

    def get_session_summary(self, stream_id: str) -> Optional[Dict]:
        """Get summary of a stream session"""
        if stream_id not in self.sessions:
            return None

        session = self.sessions[stream_id]
        return {
            "stream_id": stream_id,
            "start_time": session["start_time"].isoformat(),
            "end_time": (
                session["end_time"].isoformat() if session["end_time"] else None
            ),
            "duration_seconds": self.get_session_duration(stream_id),
            "status": session["status"],
            "total_events": len(session["events"]),
            "event_types": len(set(e.event_type for e in session["events"])),
        }


logger.info("Twitch event tracking initialized")
