import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from pathlib import Path
from memory.memory_manager import MemoryManager
from emotional.emotion_model import EmotionModel
from emotional.sentiment_analyzer import SentimentAnalyzer
from core.evolution_engine import EvolutionEngine
from core.safety_controller import SafetyController
from core.personality import Personality
from learning.curiosity_engine import CuriosityEngine
from learning.pattern_learner import PatternLearner
from learning.feedback_processor import FeedbackProcessor
from core.intelligence_engine import IntelligenceEngine

config_dir = Path('config')
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

memory = MemoryManager(data_dir, 10)
emotions = EmotionModel(data_dir / 'emotional_state')
evolution = EvolutionEngine(config_dir, data_dir)
safety = SafetyController(config_dir)
personality = Personality(config_dir)
learning = {
    'curiosity': CuriosityEngine(),
    'patterns': PatternLearner(data_dir),
    'feedback': FeedbackProcessor(data_dir),
}
engine = IntelligenceEngine(memory, emotions, evolution, personality, safety, learning, config_dir=config_dir)

print("Starting tests...\n")

r = engine.process_input('Hello!')
print(f"[TEST 1 - Greeting] Intent: {r['intent']}, Response: {r['response'][:80]}...")

r = engine.process_input('My name is Alex')
print(f"[TEST 2 - Name] Intent: {r['intent']}, Response: {r['response'][:80]}...")

r = engine.process_input('Did you know that the sun is a star?')
print(f"[TEST 3 - Teaching] Intent: {r['intent']}, Response: {r['response'][:80]}...")

r = engine.process_input('Who are you?')
print(f"[TEST 4 - Self] Intent: {r['intent']}, Response: {r['response'][:80]}...")

r = engine.process_input('I am excited about this!')
print(f"[TEST 5 - Emotion] Intent: {r['intent']}, Response: {r['response'][:80]}...")

status = evolution.get_status()
print(f"[TEST 6 - Status] Stage: {status['stage_name']}, XP: {status['total_xp']}, Interactions: {status['total_interactions']}")

stats = memory.get_stats()
print(f"[TEST 7 - Memory] Facts: {stats['total_facts']}, User: {stats['user_name']}")

sa = SentimentAnalyzer()
s = sa.analyze('I am so happy and excited!')
print(f"[TEST 8 - Sentiment] Score: {s['score']}, Label: {s['label']}, Emotions: {s['detected_emotions']}")

print("\nALL TESTS PASSED!")
