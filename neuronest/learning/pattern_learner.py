"""
NeuroNest — Pattern Learner
Learns from interaction patterns: user preferences, conversation patterns,
and response optimization.
"""
import json, time
from pathlib import Path


class PatternLearner:
    """Learns and stores patterns from interactions."""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir) / "learned_patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_file = self.data_dir / "patterns.json"
        self._load()

    def _load(self):
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.user_preferences = data.get("user_preferences", {})
                self.conversation_patterns = data.get("conversation_patterns", {})
                self.topic_frequency = data.get("topic_frequency", {})
                self.response_feedback = data.get("response_feedback", [])
                self.total_patterns = data.get("total_patterns", 0)
            else:
                self._init()
        except (json.JSONDecodeError, IOError):
            self._init()

    def _init(self):
        self.user_preferences = {}
        self.conversation_patterns = {
            "avg_message_length": 0, "total_messages": 0,
            "preferred_topics": {}, "active_hours": {},
        }
        self.topic_frequency = {}
        self.response_feedback = []
        self.total_patterns = 0

    def _save(self):
        data = {
            "user_preferences": self.user_preferences,
            "conversation_patterns": self.conversation_patterns,
            "topic_frequency": self.topic_frequency,
            "response_feedback": self.response_feedback[-200:],
            "total_patterns": self.total_patterns,
        }
        with open(self.patterns_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def learn_from_message(self, message, topics=None):
        """Learn patterns from a user message."""
        # Update message length average
        cp = self.conversation_patterns
        total = cp.get("total_messages", 0)
        avg = cp.get("avg_message_length", 0)
        new_avg = ((avg * total) + len(message)) / (total + 1)
        cp["avg_message_length"] = round(new_avg, 1)
        cp["total_messages"] = total + 1

        # Track active hours
        hour = str(time.localtime().tm_hour)
        hours = cp.get("active_hours", {})
        hours[hour] = hours.get(hour, 0) + 1
        cp["active_hours"] = hours

        # Track topics
        if topics:
            for topic in topics:
                self.topic_frequency[topic] = self.topic_frequency.get(topic, 0) + 1
                pref = cp.get("preferred_topics", {})
                pref[topic] = pref.get(topic, 0) + 1
                cp["preferred_topics"] = pref

        self.total_patterns += 1
        self._save()

    def learn_preference(self, key, value):
        """Store a learned user preference."""
        self.user_preferences[key] = {
            "value": value, "learned_at": time.time(),
            "confidence": 0.7,
        }
        self.total_patterns += 1
        self._save()

    def record_feedback(self, response_type, was_positive):
        """Record whether a response type got positive feedback."""
        self.response_feedback.append({
            "type": response_type, "positive": was_positive,
            "timestamp": time.time(),
        })
        self._save()

    def get_preferred_topics(self, n=5):
        """Return the user's most discussed topics."""
        sorted_topics = sorted(
            self.topic_frequency.items(),
            key=lambda x: x[1], reverse=True
        )
        return [t[0] for t in sorted_topics[:n]]

    def get_stats(self):
        return {
            "total_patterns": self.total_patterns,
            "known_preferences": len(self.user_preferences),
            "top_topics": self.get_preferred_topics(5),
            "total_messages_analyzed": self.conversation_patterns.get("total_messages", 0),
        }
