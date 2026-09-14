"""
NeuroNest — Long-Term Memory Module

Persistent storage for facts, user information, learned knowledge,
and important experiences. Survives across sessions.
"""

import json
import os
import time
from pathlib import Path


class LongTermMemory:
    """
    Long-term memory stores persistent knowledge that carries
    across sessions. Data is saved to JSON files on disk.
    """

    def __init__(self, data_dir):
        """
        Initialize long-term memory with a storage directory.

        Args:
            data_dir: Path to the directory for storing memory files.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Memory categories
        self.facts_file = self.data_dir / "facts.json"
        self.user_profile_file = self.data_dir / "user_profile.json"
        self.experiences_file = self.data_dir / "experiences.json"
        self.learned_knowledge_file = self.data_dir / "learned_knowledge.json"

        # Load existing data
        self.facts = self._load_json(self.facts_file, default=[])
        self.user_profile = self._load_json(self.user_profile_file, default={
            "name": None,
            "preferences": {},
            "interests": [],
            "interaction_style": None,
            "known_facts_about_user": [],
        })
        self.experiences = self._load_json(self.experiences_file, default=[])
        self.learned_knowledge = self._load_json(
            self.learned_knowledge_file, default={}
        )

    def _load_json(self, filepath, default=None):
        """Load data from a JSON file, returning default if not found."""
        try:
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return default if default is not None else {}

    def _save_json(self, filepath, data):
        """Save data to a JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---- Fact Storage ----

    def store_fact(self, fact, source="conversation", category="general"):
        """
        Store a new fact in long-term memory.

        Args:
            fact: The fact string to remember.
            source: Where this fact came from.
            category: Category of the fact (general, science, user, etc.)

        Returns:
            bool: True if stored (new fact), False if already known.
        """
        # Check for duplicates
        for existing in self.facts:
            if existing["fact"].lower() == fact.lower():
                return False

        entry = {
            "fact": fact,
            "source": source,
            "category": category,
            "timestamp": time.time(),
            "recall_count": 0,
            "confidence": 0.8,
        }
        self.facts.append(entry)
        self._save_json(self.facts_file, self.facts)
        return True

    def recall_facts(self, query=None, category=None, limit=10):
        """
        Recall facts from memory, optionally filtered.

        Args:
            query: Search string to match against facts.
            category: Filter by category.
            limit: Maximum number of facts to return.

        Returns:
            List of matching fact entries.
        """
        results = self.facts

        if category:
            results = [f for f in results if f.get("category") == category]

        if query:
            query_lower = query.lower()
            query_words = query_lower.split()
            scored = []
            for fact_entry in results:
                fact_lower = fact_entry["fact"].lower()
                # Score based on word overlap
                score = sum(1 for w in query_words if w in fact_lower)
                if score > 0:
                    scored.append((score, fact_entry))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [f for _, f in scored]

        # Update recall count for returned facts
        for fact_entry in results[:limit]:
            fact_entry["recall_count"] = fact_entry.get("recall_count", 0) + 1

        self._save_json(self.facts_file, self.facts)
        return results[:limit]

    def get_fact_count(self):
        """Return total number of stored facts."""
        return len(self.facts)

    # ---- User Profile ----

    def update_user_profile(self, key, value):
        """
        Update a field in the user profile.

        Args:
            key: Profile field name.
            value: New value for the field.
        """
        self.user_profile[key] = value
        self._save_json(self.user_profile_file, self.user_profile)

    def add_user_fact(self, fact):
        """Add a fact about the user."""
        known = self.user_profile.get("known_facts_about_user", [])
        if fact not in known:
            known.append(fact)
            self.user_profile["known_facts_about_user"] = known
            self._save_json(self.user_profile_file, self.user_profile)
            return True
        return False

    def add_user_interest(self, interest):
        """Add a user interest."""
        interests = self.user_profile.get("interests", [])
        if interest.lower() not in [i.lower() for i in interests]:
            interests.append(interest)
            self.user_profile["interests"] = interests
            self._save_json(self.user_profile_file, self.user_profile)

    def get_user_profile(self):
        """Return the full user profile."""
        return self.user_profile.copy()

    def set_user_name(self, name):
        """Set the user's name."""
        self.user_profile["name"] = name
        self._save_json(self.user_profile_file, self.user_profile)

    def get_user_name(self):
        """Get the user's name, or None."""
        return self.user_profile.get("name")

    # ---- Experiences ----

    def store_experience(self, event_type, description, significance=0.5):
        """
        Store a notable experience/event.

        Args:
            event_type: Type of event (learning, mistake, achievement, etc.)
            description: What happened.
            significance: How important (0.0 to 1.0).
        """
        entry = {
            "event_type": event_type,
            "description": description,
            "significance": significance,
            "timestamp": time.time(),
        }
        self.experiences.append(entry)

        # Keep only the most significant experiences if too many
        if len(self.experiences) > 500:
            self.experiences.sort(
                key=lambda x: x["significance"], reverse=True
            )
            self.experiences = self.experiences[:400]

        self._save_json(self.experiences_file, self.experiences)

    def get_recent_experiences(self, n=10, event_type=None):
        """Get the N most recent experiences."""
        results = self.experiences
        if event_type:
            results = [e for e in results if e["event_type"] == event_type]
        return results[-n:]

    # ---- Learned Knowledge ----

    def store_knowledge(self, topic, content):
        """
        Store structured knowledge about a topic.

        Args:
            topic: The topic key.
            content: Knowledge content (string or dict).
        """
        if topic not in self.learned_knowledge:
            self.learned_knowledge[topic] = {
                "content": [],
                "first_learned": time.time(),
                "last_updated": time.time(),
                "access_count": 0,
            }

        if isinstance(content, str):
            if content not in self.learned_knowledge[topic]["content"]:
                self.learned_knowledge[topic]["content"].append(content)
        else:
            self.learned_knowledge[topic]["content"].append(content)

        self.learned_knowledge[topic]["last_updated"] = time.time()
        self._save_json(self.learned_knowledge_file, self.learned_knowledge)

    def recall_knowledge(self, topic):
        """
        Recall knowledge about a topic.

        Args:
            topic: The topic to look up.

        Returns:
            Knowledge dict or None.
        """
        # Exact match
        if topic in self.learned_knowledge:
            self.learned_knowledge[topic]["access_count"] += 1
            self._save_json(
                self.learned_knowledge_file, self.learned_knowledge
            )
            return self.learned_knowledge[topic]

        # Fuzzy match
        topic_lower = topic.lower()
        for key, value in self.learned_knowledge.items():
            if topic_lower in key.lower() or key.lower() in topic_lower:
                value["access_count"] += 1
                self._save_json(
                    self.learned_knowledge_file, self.learned_knowledge
                )
                return value

        return None

    def get_all_topics(self):
        """Return list of all known knowledge topics."""
        return list(self.learned_knowledge.keys())

    # ---- Stats ----

    def get_memory_stats(self):
        """Return overall memory statistics."""
        return {
            "total_facts": len(self.facts),
            "total_experiences": len(self.experiences),
            "total_knowledge_topics": len(self.learned_knowledge),
            "user_name": self.user_profile.get("name"),
            "user_interests_count": len(
                self.user_profile.get("interests", [])
            ),
            "user_facts_count": len(
                self.user_profile.get("known_facts_about_user", [])
            ),
        }

    def reset(self):
        """Reset all long-term memory (dangerous!)."""
        self.facts = []
        self.user_profile = {
            "name": None,
            "preferences": {},
            "interests": [],
            "interaction_style": None,
            "known_facts_about_user": [],
        }
        self.experiences = []
        self.learned_knowledge = {}
        self._save_json(self.facts_file, self.facts)
        self._save_json(self.user_profile_file, self.user_profile)
        self._save_json(self.experiences_file, self.experiences)
        self._save_json(self.learned_knowledge_file, self.learned_knowledge)
