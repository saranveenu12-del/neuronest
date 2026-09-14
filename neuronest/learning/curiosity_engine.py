"""
NeuroNest — Curiosity Engine
Generates exploratory questions based on conversation topics.
Drives Stage 1's core behavior: curiosity-driven learning.
"""
import random


class CuriosityEngine:
    """Generates curious follow-up questions to drive learning."""

    # Topic-based question templates
    TOPIC_QUESTIONS = {
        "nature": [
            "Why do leaves change color in autumn? 🍂",
            "How do birds know which direction to fly when they migrate?",
            "What makes the sky blue during the day but orange at sunset?",
            "Do plants feel anything when they grow toward the light?",
        ],
        "space": [
            "How far away is the nearest star? ⭐",
            "Why doesn't the moon fall down to Earth?",
            "What's inside a black hole? That sounds mysterious!",
            "How many galaxies are there in the universe?",
        ],
        "animals": [
            "Do animals dream like humans do? 🐕",
            "Why can cats always land on their feet?",
            "How do dolphins communicate with each other?",
            "What's the smartest animal besides humans?",
        ],
        "science": [
            "How does electricity actually work? ⚡",
            "Why does ice float on water when most solids sink?",
            "What are atoms made of? And what are those made of?",
            "How do magnets know to attract each other?",
        ],
        "people": [
            "What do you enjoy doing in your free time?",
            "What's something you've always wanted to learn?",
            "What's the most interesting place you've ever been?",
            "Is there something that always makes you smile?",
        ],
        "feelings": [
            "What makes you feel really happy? 😊",
            "How do you handle days when you feel sad?",
            "What's something you're really proud of?",
            "Do you have a favorite memory?",
        ],
        "learning": [
            "What subject do you find most fascinating?",
            "How do you like to learn new things — reading, watching, or doing?",
            "What's something you learned recently that surprised you?",
            "Is there a question you've always wondered about?",
        ],
    }

    # General curiosity questions when no specific topic
    GENERAL_QUESTIONS = [
        "I'm curious — what's something interesting you know that most people don't? 🤔",
        "If you could learn about anything right now, what would you pick?",
        "What's the most amazing fact you've ever heard?",
        "Can you teach me something? I love learning new things! 📚",
        "What made you happy today? I want to know! 😊",
        "Is there anything you've been thinking about lately?",
        "What's something you wish you understood better?",
        "If you could ask any question and get the perfect answer, what would it be?",
        "What are you interested in? I'd love to learn about it with you!",
        "Tell me about something you find really cool or fascinating!",
    ]

    # Follow-up question templates based on detected topics
    FOLLOW_UP_TEMPLATES = [
        "That's so interesting! Why does {topic} work that way?",
        "Oh wow! Can you tell me more about {topic}? 🤩",
        "I want to understand — what exactly is {topic}?",
        "How did you learn about {topic}? That's fascinating!",
        "{topic} sounds amazing! What else should I know about it?",
        "I've never thought about {topic} before — why is it important?",
    ]

    def __init__(self):
        self.asked_questions = set()
        self.topics_explored = set()

    def generate_question(self, context_topics=None, conversation_context=None):
        """
        Generate a curious question.

        Args:
            context_topics: List of topics from current conversation.
            conversation_context: Recent conversation text for context.

        Returns:
            A question string.
        """
        # Try topic-specific question first
        if context_topics:
            for topic in context_topics:
                topic_lower = topic.lower()
                for category, questions in self.TOPIC_QUESTIONS.items():
                    if category in topic_lower or topic_lower in category:
                        available = [q for q in questions if q not in self.asked_questions]
                        if available:
                            question = random.choice(available)
                            self.asked_questions.add(question)
                            self.topics_explored.add(category)
                            return question

        # Try follow-up based on context topics
        if context_topics and random.random() < 0.4:
            topic = random.choice(context_topics)
            template = random.choice(self.FOLLOW_UP_TEMPLATES)
            return template.format(topic=topic)

        # Fall back to general questions
        available = [q for q in self.GENERAL_QUESTIONS if q not in self.asked_questions]
        if not available:
            self.asked_questions.clear()
            available = self.GENERAL_QUESTIONS

        question = random.choice(available)
        self.asked_questions.add(question)
        return question

    def detect_topics(self, text):
        """
        Extract possible topics from text for question generation.

        Returns:
            List of detected topic strings.
        """
        topics = []
        text_lower = text.lower()

        topic_keywords = {
            "nature": ["tree", "flower", "plant", "forest", "ocean", "river", "mountain", "weather", "rain", "sun"],
            "space": ["star", "planet", "moon", "sun", "galaxy", "universe", "rocket", "astronaut", "mars", "earth"],
            "animals": ["dog", "cat", "bird", "fish", "animal", "pet", "horse", "elephant", "whale", "insect"],
            "science": ["experiment", "atom", "energy", "gravity", "light", "electricity", "chemistry", "physics"],
            "technology": ["computer", "robot", "ai", "internet", "code", "program", "software", "machine"],
            "music": ["song", "music", "instrument", "piano", "guitar", "sing", "band", "melody"],
            "art": ["paint", "draw", "art", "color", "design", "creative", "picture", "sculpture"],
            "food": ["food", "cook", "eat", "recipe", "fruit", "vegetable", "cake", "pizza"],
            "sports": ["game", "play", "sport", "football", "basketball", "run", "swim", "exercise"],
        }

        for category, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(category)

        return topics if topics else ["general"]

    def get_exploration_stats(self):
        """Return curiosity exploration statistics."""
        return {
            "questions_asked": len(self.asked_questions),
            "topics_explored": list(self.topics_explored),
        }
