"""
NeuroNest — Emotion Model
Simulates NeuroNest's internal emotional state with 6 base emotions,
decay over time, and trigger-based transitions.
"""
import json, time
from pathlib import Path


class EmotionModel:
    """
    Models NeuroNest's emotional state as a blend of base emotions
    that shift based on interactions and decay toward baseline.
    """

    # Base emotions and their defaults
    EMOTIONS = {
        "joy": 0.3,
        "curiosity": 0.7,
        "confusion": 0.0,
        "concern": 0.0,
        "excitement": 0.3,
        "calm": 0.5,
    }

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "emotional_state.json"
        self._load_state()

    def _load_state(self):
        """Load emotional state from disk or initialize defaults."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.emotions = data.get("emotions", dict(self.EMOTIONS))
                self.last_update = data.get("last_update", time.time())
                self.emotion_history = data.get("history", [])
            else:
                self._reset()
        except (json.JSONDecodeError, IOError):
            self._reset()

    def _reset(self):
        self.emotions = dict(self.EMOTIONS)
        self.last_update = time.time()
        self.emotion_history = []

    def _save_state(self):
        data = {
            "emotions": self.emotions,
            "last_update": self.last_update,
            "history": self.emotion_history[-100:],  # Keep last 100 entries
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _apply_decay(self):
        """Decay emotions toward baseline over time."""
        now = time.time()
        elapsed = now - self.last_update
        decay_rate = 0.01  # Per second

        for emotion, baseline in self.EMOTIONS.items():
            current = self.emotions.get(emotion, baseline)
            diff = current - baseline
            if abs(diff) > 0.01:
                decay = min(abs(diff), decay_rate * elapsed)
                if diff > 0:
                    self.emotions[emotion] = current - decay
                else:
                    self.emotions[emotion] = current + decay

        self.last_update = now

    def process_interaction(self, sentiment_result, interaction_type="conversation"):
        """
        Update emotional state based on a sentiment analysis result.

        Args:
            sentiment_result: Dict from SentimentAnalyzer.analyze()
            interaction_type: Type of interaction
        """
        self._apply_decay()

        score = sentiment_result.get("score", 0)
        detected = sentiment_result.get("detected_emotions", [])

        # Map detected emotions to internal state changes
        for emotion in detected:
            if emotion == "joy" or emotion == "gratitude":
                self._shift("joy", 0.15)
                self._shift("excitement", 0.1)
            elif emotion == "curiosity":
                self._shift("curiosity", 0.15)
                self._shift("excitement", 0.08)
            elif emotion == "frustration":
                self._shift("concern", 0.2)
                self._shift("joy", -0.1)
                self._shift("calm", -0.1)
            elif emotion == "sadness":
                self._shift("concern", 0.15)
                self._shift("joy", -0.15)
                self._shift("calm", -0.05)
            elif emotion == "confusion":
                self._shift("confusion", 0.2)
                self._shift("curiosity", 0.1)
            elif emotion == "concern":
                self._shift("concern", 0.15)
                self._shift("calm", -0.1)
            elif emotion == "positive":
                self._shift("joy", 0.1)
                self._shift("calm", 0.05)
            elif emotion == "negative":
                self._shift("concern", 0.1)
                self._shift("joy", -0.05)

        # General sentiment influence
        if score > 0.3:
            self._shift("joy", 0.05)
            self._shift("calm", 0.05)
        elif score < -0.3:
            self._shift("concern", 0.05)
            self._shift("calm", -0.05)

        # Learning events boost curiosity and excitement
        if interaction_type == "learning":
            self._shift("curiosity", 0.1)
            self._shift("excitement", 0.15)
            self._shift("joy", 0.08)

        # Record to history
        self.emotion_history.append({
            "timestamp": time.time(),
            "trigger": interaction_type,
            "dominant": self.get_dominant_emotion(),
            "emotions": dict(self.emotions),
        })

        self._save_state()

    def _shift(self, emotion, amount):
        """Shift an emotion value, clamping to [0, 1]."""
        current = self.emotions.get(emotion, 0)
        self.emotions[emotion] = max(0.0, min(1.0, current + amount))

    def get_dominant_emotion(self):
        """Return the emotion with the highest current value."""
        return max(self.emotions, key=self.emotions.get)

    def get_emotional_state(self):
        """Return the full emotional state."""
        self._apply_decay()
        return {
            "emotions": dict(self.emotions),
            "dominant": self.get_dominant_emotion(),
            "timestamp": time.time(),
        }

    def get_response_modifier(self):
        """
        Return modifiers that should influence response generation.

        Returns:
            Dict with tone suggestions based on emotional state.
        """
        dominant = self.get_dominant_emotion()
        modifiers = {
            "joy": {"tone": "warm and happy", "emoji": "😊", "energy": "high"},
            "curiosity": {"tone": "eager and inquisitive", "emoji": "🤔", "energy": "high"},
            "confusion": {"tone": "uncertain but trying", "emoji": "😅", "energy": "medium"},
            "concern": {"tone": "gentle and caring", "emoji": "😟", "energy": "low"},
            "excitement": {"tone": "enthusiastic and energetic", "emoji": "✨", "energy": "high"},
            "calm": {"tone": "peaceful and steady", "emoji": "😌", "energy": "medium"},
        }
        return modifiers.get(dominant, modifiers["calm"])

    def get_emotion_bar(self, width=20):
        """Get a visual representation of emotions for the console."""
        bars = {}
        for emotion, value in sorted(self.emotions.items()):
            filled = int(value * width)
            bar = "█" * filled + "░" * (width - filled)
            bars[emotion] = f"{bar} {value:.0%}"
        return bars

    def reset(self):
        """Reset emotional state to defaults."""
        self._reset()
        self._save_state()
