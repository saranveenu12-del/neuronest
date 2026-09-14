"""
NeuroNest — Main Entry Point
Initializes all subsystems and starts the console interface.

Usage:
    py main.py           # Start NeuroNest in console mode
    py main.py --voice   # Start with voice output enabled
"""
import sys
import os
from pathlib import Path

# Fix terminal encoding for emojis on Windows
if (sys.stdout.encoding or '').lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Initialize NeuroNest and start the interactive session."""

    # --- Parse arguments ---
    voice_mode = "--voice" in sys.argv

    # --- Paths ---
    config_dir = PROJECT_ROOT / "config"
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("🧠 Initializing NeuroNest...")

    # --- Initialize Memory ---
    from memory.memory_manager import MemoryManager
    memory = MemoryManager(data_dir, max_context_window=10)
    print("  ✓ Memory Framework loaded")

    # --- Initialize Emotional System ---
    from emotional.emotion_model import EmotionModel
    emotions = EmotionModel(data_dir / "emotional_state")
    print("  ✓ Emotional Simulation loaded")

    # --- Initialize Evolution Engine ---
    from core.evolution_engine import EvolutionEngine
    evolution = EvolutionEngine(config_dir, data_dir)
    print("  ✓ Evolution Engine loaded")

    # --- Initialize Safety Controller ---
    from core.safety_controller import SafetyController
    safety = SafetyController(config_dir)
    print("  ✓ Safety Controller loaded")

    # --- Initialize Personality ---
    from core.personality import Personality
    personality = Personality(config_dir)
    print("  ✓ Personality Module loaded")

    # --- Initialize Learning Systems ---
    from learning.curiosity_engine import CuriosityEngine
    from learning.pattern_learner import PatternLearner
    from learning.feedback_processor import FeedbackProcessor

    learning_systems = {
        "curiosity": CuriosityEngine(),
        "patterns": PatternLearner(data_dir),
        "feedback": FeedbackProcessor(data_dir),
    }
    print("  ✓ Learning Systems loaded")

    # --- Initialize Intelligence Engine ---
    from core.intelligence_engine import IntelligenceEngine
    engine = IntelligenceEngine(
        memory=memory,
        emotions=emotions,
        evolution=evolution,
        personality=personality,
        safety=safety,
        learning_systems=learning_systems,
        config_dir=config_dir,
    )
    print("  ✓ Intelligence Engine loaded")

    # --- Initialize Voice (optional) ---
    voice = None
    try:
        from interface.voice import VoiceInterface
        voice = VoiceInterface()
        if voice.tts_available:
            print("  ✓ Voice Interface loaded (TTS ready)")
        else:
            print("  ⚠ Voice Interface loaded (TTS unavailable — install pyttsx3)")
    except Exception as e:
        print(f"  ⚠ Voice Interface skipped: {e}")

    print("  ✓ All systems online!\n")

    # --- Start Console Interface ---
    from interface.console import ConsoleInterface
    console = ConsoleInterface(
        engine=engine,
        evolution=evolution,
        emotions=emotions,
        memory=memory,
        personality=personality,
        voice=voice,
    )

    if voice_mode and voice and voice.tts_available:
        console.voice_enabled = True
        print("  🔊 Voice output enabled\n")

    try:
        console.start()
    except KeyboardInterrupt:
        print("\n\n🧠 NeuroNest shutting down... Saving state...")
        memory.consolidate_session()
        print("   State saved. Goodbye! ✨\n")


if __name__ == "__main__":
    main()
