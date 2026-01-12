"""
Advanced Twitch chat handler with filtering, sentiment analysis, and moderation
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class UserTier(Enum):
    """User tier classification"""

    STREAMER = "streamer"
    MODERATOR = "moderator"
    SUBSCRIBER_T3 = "tier3_subscriber"
    SUBSCRIBER_T2 = "tier2_subscriber"
    SUBSCRIBER_T1 = "tier1_subscriber"
    VIP = "vip"
    BITS_SUPPORTER = "bits_supporter"
    FOLLOWER = "follower"
    VIEWER = "viewer"


class MessageSentiment(Enum):
    """Message sentiment classification"""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class ChatMessage:
    """Represents a Twitch chat message with metadata"""

    def __init__(
        self,
        author: str,
        content: str,
        user_id: str,
        timestamp: datetime,
        badges: Dict[str, str] = None,
        bits: int = 0,
        channel_points: int = 0,
    ):
        self.author = author
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp
        self.badges = badges or {}
        self.bits = bits
        self.channel_points = channel_points
        self.sentiment: Optional[MessageSentiment] = None
        self.flags = []
        self.moderation_score = 0.0

    def get_user_tier(self) -> UserTier:
        """Determine user tier from badges"""
        if "broadcaster" in self.badges:
            return UserTier.STREAMER
        elif "moderator" in self.badges:
            return UserTier.MODERATOR
        elif "founder" in self.badges:
            return UserTier.SUBSCRIBER_T3
        elif "subscriber" in self.badges:
            tier = self.badges["subscriber"]
            if tier == "3":
                return UserTier.SUBSCRIBER_T3
            elif tier == "2":
                return UserTier.SUBSCRIBER_T2
            else:
                return UserTier.SUBSCRIBER_T1
        elif "vip" in self.badges:
            return UserTier.VIP
        elif self.bits > 0:
            return UserTier.BITS_SUPPORTER
        else:
            return UserTier.VIEWER

    def analyze_sentiment(self) -> MessageSentiment:
        """Analyze message sentiment (placeholder)"""
        content_lower = self.content.lower()

        # Simple sentiment analysis
        positive_words = [
            "love",
            "awesome",
            "great",
            "amazing",
            "nice",
            "good",
            "best",
            "!",
        ]
        negative_words = ["hate", "bad", "terrible", "awful", "worst", "sucks"]

        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count + 1:
            self.sentiment = MessageSentiment.POSITIVE
        elif negative_count > positive_count + 1:
            self.sentiment = MessageSentiment.NEGATIVE
        else:
            self.sentiment = MessageSentiment.NEUTRAL

        return self.sentiment


class ChatFilter:
    """Advanced chat filtering and moderation"""

    def __init__(self):
        self.blocked_words = set()
        self.spam_threshold = 5  # Messages per 10 seconds
        self.caps_threshold = 0.7  # 70% caps = warning
        self.user_message_history: Dict[str, List[ChatMessage]] = {}
        self.timeout_users: set = set()

    def add_blocked_word(self, word: str):
        """Add word to blocklist"""
        self.blocked_words.add(word.lower())

    def remove_blocked_word(self, word: str):
        """Remove word from blocklist"""
        self.blocked_words.discard(word.lower())

    def is_spam(self, user_id: str) -> bool:
        """Check if user is spamming"""
        if user_id not in self.user_message_history:
            return False

        messages = self.user_message_history[user_id]
        # Keep only messages from last 10 seconds
        now = datetime.now()
        recent = [m for m in messages if (now - m.timestamp).total_seconds() < 10]

        return len(recent) > self.spam_threshold

    def has_blocked_words(self, message: ChatMessage) -> bool:
        """Check if message contains blocked words"""
        content_lower = message.content.lower()
        return any(word in content_lower for word in self.blocked_words)

    def has_excessive_caps(self, message: ChatMessage) -> bool:
        """Check if message has excessive caps"""
        if len(message.content) < 3:
            return False

        caps_count = sum(1 for c in message.content if c.isupper())
        caps_ratio = caps_count / len(message.content)
        return caps_ratio > self.caps_threshold

    def calculate_moderation_score(self, message: ChatMessage) -> float:
        """Calculate how likely message needs moderation"""
        score = 0.0

        if self.has_blocked_words(message):
            score += 0.5

        if self.has_excessive_caps(message):
            score += 0.1

        if self.is_spam(message.user_id):
            score += 0.3

        # Lower score for high-tier users
        tier = message.get_user_tier()
        tier_trust = {
            UserTier.STREAMER: 1.0,
            UserTier.MODERATOR: 0.95,
            UserTier.SUBSCRIBER_T3: 0.90,
            UserTier.SUBSCRIBER_T2: 0.85,
            UserTier.SUBSCRIBER_T1: 0.80,
            UserTier.VIP: 0.85,
            UserTier.BITS_SUPPORTER: 0.80,
            UserTier.FOLLOWER: 0.7,
            UserTier.VIEWER: 0.5,
        }

        score *= 1.0 - tier_trust.get(tier, 0.5)

        message.moderation_score = min(1.0, max(0.0, score))
        return message.moderation_score

    def should_timeout_user(self, user_id: str, duration: int = 300) -> bool:
        """Check if user should be timed out"""
        if user_id in self.timeout_users:
            return True

        if user_id not in self.user_message_history:
            return False

        # Check for excessive violations
        messages = self.user_message_history[user_id]
        violations = sum(1 for m in messages if m.moderation_score > 0.7)

        return violations > 3

    def track_message(self, message: ChatMessage):
        """Track message for spam/moderation analysis"""
        if message.user_id not in self.user_message_history:
            self.user_message_history[message.user_id] = []

        self.user_message_history[message.user_id].append(message)

        # Keep only last 100 messages per user
        if len(self.user_message_history[message.user_id]) > 100:
            self.user_message_history[message.user_id].pop(0)


class ChatAnalytics:
    """Analyze chat trends and patterns"""

    def __init__(self, max_history: int = 500):
        self.message_history: List[ChatMessage] = []
        self.max_history = max_history
        self.top_chatters: Dict[str, int] = {}

    def add_message(self, message: ChatMessage):
        """Add message to analytics"""
        self.message_history.append(message)

        # Update top chatters
        if message.author not in self.top_chatters:
            self.top_chatters[message.author] = 0
        self.top_chatters[message.author] += 1

        # Trim history
        if len(self.message_history) > self.max_history:
            oldest = self.message_history.pop(0)
            self.top_chatters[oldest.author] = max(
                0, self.top_chatters[oldest.author] - 1
            )

    def get_top_chatters(self, limit: int = 10) -> List[tuple]:
        """Get top active chatters"""
        return sorted(self.top_chatters.items(), key=lambda x: x[1], reverse=True)[
            :limit
        ]

    def get_sentiment_distribution(self) -> Dict[str, int]:
        """Get sentiment distribution of recent messages"""
        distribution = {
            "very_positive": 0,
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "very_negative": 0,
        }

        for message in self.message_history:
            if message.sentiment:
                distribution[message.sentiment.value] += 1

        return distribution

    def get_average_response_time(self) -> float:
        """Calculate average time between messages"""
        if len(self.message_history) < 2:
            return 0.0

        times = []
        for i in range(1, len(self.message_history)):
            delta = (
                self.message_history[i].timestamp
                - self.message_history[i - 1].timestamp
            ).total_seconds()
            times.append(delta)

        return sum(times) / len(times) if times else 0.0


def create_chat_message_from_event(event_data: dict) -> ChatMessage:
    """Factory function to create ChatMessage from Twitch IRC event"""
    return ChatMessage(
        author=event_data.get("author", "Unknown"),
        content=event_data.get("message", ""),
        user_id=event_data.get("user_id", ""),
        timestamp=datetime.now(),
        badges=event_data.get("badges", {}),
        bits=event_data.get("bits", 0),
        channel_points=event_data.get("channel_points", 0),
    )


logger.info("Advanced Twitch chat handlers initialized")
