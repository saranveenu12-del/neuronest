"""
NeuroNest — Short-Term Memory Module

Maintains the current conversation context (session-level).
Acts like a working memory buffer that holds recent exchanges
for contextual understanding.
"""

import time
from collections import deque


class ShortTermMemory:
    """
    Short-term memory holds the current conversation context.
    It functions like a sliding window of recent interactions.
    """

    def __init__(self, max_context_window=10):
        """
        Initialize short-term memory.

        Args:
            max_context_window: Maximum number of exchanges to remember
                               in the current conversation context.
        """
        self.max_context_window = max_context_window
        self.conversation_buffer = deque(maxlen=max_context_window)
        self.session_start_time = time.time()
        self.session_metadata = {
            "topics_discussed": [],
            "entities_mentioned": [],
            "user_mood_trajectory": [],
            "questions_asked_this_session": 0,
            "facts_learned_this_session": 0,
        }

    def add_exchange(self, role, content, metadata=None):
        """
        Add a conversational exchange to the buffer.

        Args:
            role: 'user' or 'neuronest'
            content: The text content of the message
            metadata: Optional dict with extra info (intent, emotion, etc.)
        """
        exchange = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self.conversation_buffer.append(exchange)

    def get_context(self, n=None):
        """
        Get the last N exchanges for context building.

        Args:
            n: Number of recent exchanges to return. None = all.

        Returns:
            List of exchange dicts.
        """
        if n is None:
            return list(self.conversation_buffer)
        return list(self.conversation_buffer)[-n:]

    def get_last_exchange(self, role=None):
        """
        Get the most recent exchange, optionally filtered by role.

        Args:
            role: If provided, get the last exchange from this role.

        Returns:
            Exchange dict or None.
        """
        if not self.conversation_buffer:
            return None

        if role is None:
            return self.conversation_buffer[-1]

        for exchange in reversed(self.conversation_buffer):
            if exchange["role"] == role:
                return exchange
        return None

    def add_topic(self, topic):
        """Track a topic discussed in this session."""
        if topic not in self.session_metadata["topics_discussed"]:
            self.session_metadata["topics_discussed"].append(topic)

    def add_entity(self, entity):
        """Track an entity mentioned in this session."""
        if entity not in self.session_metadata["entities_mentioned"]:
            self.session_metadata["entities_mentioned"].append(entity)

    def track_mood(self, mood):
        """Track user mood changes during the session."""
        self.session_metadata["user_mood_trajectory"].append({
            "mood": mood,
            "timestamp": time.time(),
        })

    def increment_questions(self):
        """Increment the session question counter."""
        self.session_metadata["questions_asked_this_session"] += 1

    def increment_facts(self):
        """Increment the session fact counter."""
        self.session_metadata["facts_learned_this_session"] += 1

    def get_session_summary(self):
        """
        Generate a summary of the current session.

        Returns:
            Dict with session statistics and metadata.
        """
        return {
            "duration_seconds": time.time() - self.session_start_time,
            "total_exchanges": len(self.conversation_buffer),
            "topics": self.session_metadata["topics_discussed"],
            "entities": self.session_metadata["entities_mentioned"],
            "questions_asked": self.session_metadata["questions_asked_this_session"],
            "facts_learned": self.session_metadata["facts_learned_this_session"],
            "mood_trajectory": self.session_metadata["user_mood_trajectory"],
        }

    def clear(self):
        """Clear all short-term memory (new session)."""
        self.conversation_buffer.clear()
        self.session_start_time = time.time()
        self.session_metadata = {
            "topics_discussed": [],
            "entities_mentioned": [],
            "user_mood_trajectory": [],
            "questions_asked_this_session": 0,
            "facts_learned_this_session": 0,
        }

    def get_conversation_text(self, n=None):
        """
        Get conversation as formatted text for context injection.

        Args:
            n: Number of recent exchanges.

        Returns:
            Formatted string of the conversation.
        """
        exchanges = self.get_context(n)
        lines = []
        for ex in exchanges:
            role_label = "User" if ex["role"] == "user" else "NeuroNest"
            lines.append(f"{role_label}: {ex['content']}")
        return "\n".join(lines)
