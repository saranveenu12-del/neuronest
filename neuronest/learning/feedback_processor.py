"""
NeuroNest — Feedback Processor
Learns from corrections and user feedback to improve responses.
"""
import json, time
from pathlib import Path


class FeedbackProcessor:
    """Processes user corrections and feedback to improve NeuroNest."""

    CORRECTION_KEYWORDS = [
        "no,", "no ", "wrong", "incorrect", "that's not right",
        "actually", "not quite", "nope", "that's wrong",
        "you're wrong", "mistake", "error", "fix", "correct",
    ]

    POSITIVE_KEYWORDS = [
        "yes", "correct", "right", "exactly", "perfect",
        "good job", "well done", "great", "awesome", "nice",
        "thanks", "thank you", "helpful", "smart", "brilliant",
    ]

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir) / "learned_patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.data_dir / "feedback.json"
        self._load()

    def _load(self):
        try:
            if self.feedback_file.exists():
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.corrections = data.get("corrections", [])
                self.positive_feedback = data.get("positive_feedback", [])
                self.total_corrections = data.get("total_corrections", 0)
                self.total_positive = data.get("total_positive", 0)
            else:
                self._init()
        except (json.JSONDecodeError, IOError):
            self._init()

    def _init(self):
        self.corrections = []
        self.positive_feedback = []
        self.total_corrections = 0
        self.total_positive = 0

    def _save(self):
        data = {
            "corrections": self.corrections[-100:],
            "positive_feedback": self.positive_feedback[-100:],
            "total_corrections": self.total_corrections,
            "total_positive": self.total_positive,
        }
        with open(self.feedback_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def detect_feedback_type(self, user_message):
        """
        Detect if a user message contains correction or positive feedback.

        Returns:
            'correction', 'positive', or None
        """
        msg_lower = user_message.lower().strip()

        for keyword in self.CORRECTION_KEYWORDS:
            if msg_lower.startswith(keyword) or keyword in msg_lower:
                return "correction"

        for keyword in self.POSITIVE_KEYWORDS:
            if keyword in msg_lower:
                return "positive"

        return None

    def process_correction(self, user_message, previous_response):
        """Record and learn from a correction."""
        self.corrections.append({
            "user_said": user_message,
            "neuronest_said": previous_response,
            "timestamp": time.time(),
        })
        self.total_corrections += 1
        self._save()

    def process_positive(self, user_message, previous_response):
        """Record positive feedback."""
        self.positive_feedback.append({
            "user_said": user_message,
            "neuronest_said": previous_response,
            "timestamp": time.time(),
        })
        self.total_positive += 1
        self._save()

    def get_correction_response(self):
        """Get a correction acknowledgment response."""
        import random
        responses = [
            "Oh, I'm sorry about that! Thank you for correcting me — I'll remember! 😊",
            "Oops, my mistake! I appreciate you teaching me the right answer! 📝",
            "You're right, I got that wrong. Thanks for helping me learn! 🌱",
            "I made an error, didn't I? Thank you for being patient with me! 💡",
            "Oh no, I messed that up! But that's how I learn — thank you! ✨",
        ]
        return random.choice(responses)

    def get_positive_response(self):
        """Get a response to positive feedback."""
        import random
        responses = [
            "Yay, I got it right! That makes me so happy! 😄",
            "Thank you! I'm learning and getting better! ✨",
            "That means a lot! I love when I can be helpful! 🌟",
            "I'm glad I could help! Let's keep learning together! 📚",
        ]
        return random.choice(responses)

    def get_stats(self):
        return {
            "total_corrections": self.total_corrections,
            "total_positive": self.total_positive,
            "learning_ratio": round(
                self.total_positive / max(1, self.total_corrections + self.total_positive), 2
            ),
        }
