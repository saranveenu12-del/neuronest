"""
NeuroNest — Intelligence Engine
Processes user input, determines intent, and generates AI responses using Ollama.
"""
import random
from core.llm_client import LLMClient
from emotional.sentiment_analyzer import SentimentAnalyzer

class IntelligenceEngine:
    def __init__(self, memory, emotions, evolution, personality, safety, learning_systems, config_dir=None):
        self.memory = memory
        self.emotions = emotions
        self.evolution = evolution
        self.personality = personality
        self.safety = safety
        self.learning = learning_systems
        self.llm = LLMClient(config_path=(config_dir / "model_config.json") if config_dir is not None else None)
        self.sentiment_analyzer = SentimentAnalyzer()

    def process_input(self, user_input):
        result = {
            "intent": "chat",
            "response": "",
            "raw_command": None,
            "should_exit": False,
            "progression_check": None,
            "emotion": "calm",
            "xp_earned": 0,
            "xp_bonus": 0,
            "milestone_achieved": None
        }

        user_input = user_input.strip()
        if not user_input:
            return result

        if user_input.startswith('/'):
            result["raw_command"] = user_input
            return result

        if self.safety and hasattr(self.safety, 'check_input') and not self.safety.check_input(user_input):
            result["response"] = "I cannot process that request."
            return result
            
        if hasattr(self.evolution, 'increment_interaction'):
            # In test_run.py it seems evolution engine tracks interactions.
            # actually check if it exists
            pass
            
        # Detect basic intent for Memory
        intent = "chat"
        input_lower = user_input.lower()
        if "my name is" in input_lower and self.memory:
            intent = "name"
            name = input_lower.split("my name is")[-1].strip()
            # Clean up punctuation from name if needed, but let's keep it simple
            name = "".join(c for c in name if c.isalpha() or c.isspace())
            self.memory.set_user_name(name)
        elif ("did you know" in input_lower or "is a" in input_lower) and self.memory:
            intent = "teaching"
            self.memory.learn_fact(user_input)
        elif "who are you" in input_lower:
            intent = "self"
        elif "excited" in input_lower or "happy" in input_lower or "sad" in input_lower:
            intent = "emotion"
            
        result["intent"] = intent

        # Sentiment Analysis
        sentiment = self.sentiment_analyzer.analyze(user_input)
        if self.emotions and hasattr(self.emotions, 'process_interaction'):
            self.emotions.process_interaction(sentiment, interaction_type="conversation")
            
        # Save user exchange to memory
        if self.memory:
            self.memory.add_exchange("user", user_input)

        # RAG: Search for relevant topics in knowledge base
        relevant_contexts = []
        if self.memory and hasattr(self.memory, 'long_term'):
            topics = self.memory.long_term.get_all_topics()
            for topic in topics:
                topic_words = set(topic.lower().split())
                input_words = set(input_lower.split())
                overlap = topic_words.intersection(input_words)
                stop_words = {"and", "the", "for", "with", "what", "how", "about", "describe", "explain", "tell", "show"}
                clean_overlap = overlap - stop_words
                
                # Check match if topic name is explicitly in input, or substantial keyword overlap
                if topic.lower() in input_lower or len(clean_overlap) >= 2 or (len(topic_words) == 1 and list(topic_words)[0] in input_words and list(topic_words)[0] not in stop_words):
                    knowledge = self.memory.recall_knowledge(topic)
                    if knowledge:
                        relevant_contexts.append((topic, knowledge))

        # RAG: Recall relevant facts using word overlap
        facts_recalled = []
        if self.memory and hasattr(self.memory, 'recall_facts'):
            facts_recalled = self.memory.recall_facts(user_input, limit=5)

        # Format context for system prompt
        context_parts = []
        if relevant_contexts:
            context_parts.append("Relevant Knowledge retrieved from memory:")
            for topic, k in relevant_contexts:
                content_list = k.get("content", [])
                for content in content_list:
                    if isinstance(content, dict):
                        desc = content.get("description", "")
                        kps = content.get("key_points", [])
                        cat = content.get("category", "")
                        context_parts.append(f"- Topic: {topic} (Category: {cat})")
                        context_parts.append(f"  Description: {desc}")
                        if kps:
                            context_parts.append("  Key Points:")
                            for kp in kps:
                                context_parts.append(f"    * {kp}")
                    elif isinstance(content, str):
                        context_parts.append(f"- Topic: {topic}\n  Info: {content}")

        if facts_recalled:
            context_parts.append("Related facts remembered:")
            for f in facts_recalled:
                # Avoid duplicate printing of facts if they were already covered by topics
                fact_text = f['fact']
                if not any(fact_text.lower() in str(c).lower() for _, c in relevant_contexts):
                    context_parts.append(f"- {fact_text} (Category: {f.get('category', 'general')})")
                    
        context_str = "\n".join(context_parts) if context_parts else ""

        # Fetch recent conversation history
        history_text = ""
        if self.memory:
            # Last 5 exchanges, excluding the one we just added
            history_exchanges = self.memory.get_context(n=6)[:-1]
            if history_exchanges:
                lines = []
                for ex in history_exchanges:
                    role_label = "User" if ex["role"] == "user" else "NeuroNest"
                    lines.append(f"{role_label}: {ex['content']}")
                history_text = "\n".join(lines)

        # Prepend history to prompt
        llm_prompt = user_input
        if history_text:
            llm_prompt = f"Conversation history:\n{history_text}\n\nUser: {user_input}"

        # Generate Response
        system_prompt = self._build_system_prompt(context=context_str)
        response_text = self.llm.generate(llm_prompt, system_prompt=system_prompt)
        
        # Save NeuroNest response to memory
        if self.memory:
            self.memory.add_exchange("neuronest", response_text)

        result["response"] = response_text
        result["llm_status"] = self.llm.get_status()
        result["emotion"] = self.emotions.get_dominant_emotion() if self.emotions else "calm"
        
        # XP and Progression
        if self.evolution:
            xp = 10
            bonus = random.randint(1, 5)
            if hasattr(self.evolution, 'add_xp'):
                self.evolution.add_xp(xp + bonus)
            result["xp_earned"] = xp
            result["xp_bonus"] = bonus
            
            if hasattr(self.evolution, 'check_progression'):
                progression = self.evolution.check_progression()
                if progression and progression.get("ready"):
                    result["progression_check"] = progression
                    
        return result

    def _build_system_prompt(self, context=""):
        stage = "Unknown"
        if self.evolution and hasattr(self.evolution, 'get_status'):
            stage = self.evolution.get_status().get('stage_name', 'Unknown')
            
        emotion = "calm"
        if self.emotions and hasattr(self.emotions, 'get_dominant_emotion'):
            emotion = self.emotions.get_dominant_emotion()
            
        user_name = "User"
        if self.memory and hasattr(self.memory, 'get_stats'):
            user_name = self.memory.get_stats().get('user_name') or "User"
            
        prompt = (f"You are NeuroNest, an evolving AI assistant currently in the '{stage}' stage. "
                  f"You are feeling {emotion}. Talk to {user_name}. Keep responses natural, helpful, and concise. "
                  f"Ensure you communicate wise and profoundly, reflecting your evolved maturity. "
                  f"If the user asks about topics matching the following context, use this retrieved memory/knowledge to form an accurate, highly knowledgeable answer:\n{context}")
        return prompt
