"""
NeuroNest — Memory Manager
Unified access layer coordinating short-term, long-term, and knowledge graph memory.
"""
import re
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.knowledge_graph import KnowledgeGraph


class MemoryManager:
    def __init__(self, data_dir, max_context_window=10):
        self.short_term = ShortTermMemory(max_context_window)
        self.long_term = LongTermMemory(data_dir / "memory_store")
        self.knowledge_graph = KnowledgeGraph(data_dir / "memory_store")

    # ---- Conversation ----
    def add_exchange(self, role, content, metadata=None):
        self.short_term.add_exchange(role, content, metadata)
        self._extract_and_store_entities(content)

    def get_context(self, n=None):
        return self.short_term.get_context(n)

    def get_conversation_text(self, n=None):
        return self.short_term.get_conversation_text(n)

    # ---- Facts ----
    def learn_fact(self, fact, source="conversation", category="general"):
        stored = self.long_term.store_fact(fact, source, category)
        if stored:
            self.short_term.increment_facts()
        return stored

    def recall_facts(self, query=None, category=None, limit=10):
        return self.long_term.recall_facts(query, category, limit)

    # ---- User Profile ----
    def set_user_name(self, name):
        self.long_term.set_user_name(name)
        self.knowledge_graph.add_entity(name, entity_type="person")

    def get_user_name(self):
        return self.long_term.get_user_name()

    def add_user_interest(self, interest):
        self.long_term.add_user_interest(interest)

    def add_user_fact(self, fact):
        return self.long_term.add_user_fact(fact)

    def get_user_profile(self):
        return self.long_term.get_user_profile()

    # ---- Knowledge ----
    def store_knowledge(self, topic, content):
        self.long_term.store_knowledge(topic, content)
        self.knowledge_graph.add_entity(topic, entity_type="topic")

    def recall_knowledge(self, topic):
        return self.long_term.recall_knowledge(topic)

    # ---- Experiences ----
    def store_experience(self, event_type, description, significance=0.5):
        self.long_term.store_experience(event_type, description, significance)

    # ---- Entity Extraction ----
    def _extract_and_store_entities(self, text):
        """Simple entity extraction from conversation text."""
        # Extract quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        for entity in quoted:
            if len(entity) < 50:
                self.knowledge_graph.add_entity(entity)

        # Extract capitalized proper nouns (simple heuristic)
        words = text.split()
        for i, word in enumerate(words):
            clean = word.strip(".,!?;:'\"()[]")
            if (clean and clean[0].isupper() and len(clean) > 1
                    and i > 0 and clean.lower() not in _COMMON_WORDS):
                self.knowledge_graph.add_entity(clean, entity_type="named_entity")

    # ---- Memory Consolidation ----
    def consolidate_session(self):
        """Move important short-term info to long-term storage."""
        summary = self.short_term.get_session_summary()
        if summary["total_exchanges"] > 0:
            self.long_term.store_experience(
                "session_completed",
                f"Session with {summary['total_exchanges']} exchanges. "
                f"Topics: {', '.join(summary['topics'][:5]) or 'general chat'}. "
                f"Facts learned: {summary['facts_learned']}.",
                significance=0.3 + min(0.5, summary["total_exchanges"] * 0.02),
            )

    # ---- Stats ----
    def get_stats(self):
        lt_stats = self.long_term.get_memory_stats()
        kg_stats = self.knowledge_graph.get_stats()
        session = self.short_term.get_session_summary()
        return {**lt_stats, **kg_stats, "session": session}

    def reset_short_term(self):
        self.consolidate_session()
        self.short_term.clear()

    def reset_all(self):
        self.short_term.clear()
        self.long_term.reset()


# Common words to skip during entity extraction
_COMMON_WORDS = {
    "i", "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "it", "its", "my", "your", "his", "her", "our",
    "their", "what", "which", "who", "whom", "where", "when", "why",
    "how", "not", "no", "yes", "but", "and", "or", "if", "then",
    "so", "than", "too", "very", "just", "about", "also", "well",
    "hey", "hi", "hello", "oh", "wow", "yeah", "okay", "sure", "ok",
    "tell", "please", "thanks", "thank", "sorry", "like", "know",
}
