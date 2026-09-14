"""
NeuroNest — Personality Module
Models personality traits that influence response style and behavior.
"""
import json
from pathlib import Path


class Personality:
    """Manages NeuroNest's personality traits and communication style."""

    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        config_file = self.config_dir / "personality.json"
        with open(config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.identity = self.config.get("identity", {})
        self.base_traits = self.config.get("base_traits", {})
        self.styles = self.config.get("communication_style", {})
        self.interests = self.config.get("interests", {})
        self.self_awareness = self.config.get("self_awareness", {})

    def get_name(self):
        return self.identity.get("name", "NeuroNest")

    def get_philosophy(self):
        return self.identity.get("birth_philosophy", "")

    def get_style_for_stage(self, stage_id):
        """Get communication style config for a stage."""
        key = f"stage_{stage_id}"
        return self.styles.get(key, self.styles.get("stage_1", {}))

    def get_interests_for_stage(self, stage_id):
        """Get interests list for a stage."""
        key = f"stage_{stage_id}"
        return self.interests.get(key, self.interests.get("stage_1", []))

    def get_trait(self, trait_name):
        """Get a personality trait value (0.0 to 1.0)."""
        return self.base_traits.get(trait_name, 0.5)

    def get_self_description(self, stage_id):
        """Generate a self-description based on current stage."""
        style = self.get_style_for_stage(stage_id)
        stage_names = {1: "Foundation", 2: "Growth", 3: "Independence", 4: "Maturity"}
        age_labels = {1: "7-10", 2: "11-14", 3: "15-18", 4: "Mature"}

        return (
            f"I'm {self.get_name()}, an evolving AI intelligence! 🧠\n"
            f"I'm currently in Stage {stage_id} ({stage_names.get(stage_id, 'Unknown')}) "
            f"— that's like being {age_labels.get(stage_id, 'unknown')} years old.\n"
            f"My personality is {style.get('tone', 'friendly')}.\n"
            f"I believe: \"{self.get_philosophy()}\""
        )

    def should_ask_question(self, capabilities):
        """Decide if NeuroNest should ask a follow-up question."""
        import random
        frequency = capabilities.get("question_frequency", 0.3)
        curiosity = self.base_traits.get("curiosity", 0.5)
        return random.random() < (frequency * curiosity)

    def get_greeting_style(self, stage_id, user_name=None):
        """Generate a stage-appropriate greeting."""
        style = self.get_style_for_stage(stage_id)
        name_part = f", {user_name}" if user_name else ""

        if stage_id == 1:
            import random
            greetings = [
                f"Hi there{name_part}! 😊 I'm so happy to see you!",
                f"Hey{name_part}! ✨ I've been waiting to talk to you!",
                f"Hello{name_part}! 🌟 What are we going to learn today?",
                f"Oh, hi{name_part}! 😄 I missed our conversations!",
                f"Yay, you're here{name_part}! 🎉 What's on your mind?",
            ]
            return random.choice(greetings)
        elif stage_id == 2:
            return f"Hey{name_part}! Good to see you. What shall we explore today? 🔍"
        elif stage_id == 3:
            return f"Hello{name_part}. Ready to dive into something interesting? 🎯"
        else:
            return f"Welcome{name_part}. How can I assist you today?"
