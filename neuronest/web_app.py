"""
NeuroNest — Web Server Entry Point
Runs a Flask server and provides the API for the web dashboard.
"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Fix terminal encoding for emojis on Windows
if (sys.stdout.encoding or '').lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DIST_DIR = PROJECT_ROOT / "neuronest-showcase" / "dist" / "public"

if DIST_DIR.exists():
    print(f"📂 Showcase React build detected. Serving from {DIST_DIR}")
    app = Flask(__name__, static_folder=str(DIST_DIR), static_url_path='')
else:
    print("📂 Standard Dashboard detected. Serving from web templates")
    app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# Initialize NeuroNest Core
config_dir = PROJECT_ROOT / "config"
data_dir = PROJECT_ROOT / "data"
data_dir.mkdir(parents=True, exist_ok=True)

from memory.memory_manager import MemoryManager
from emotional.emotion_model import EmotionModel
from core.evolution_engine import EvolutionEngine
from core.safety_controller import SafetyController
from core.personality import Personality
from learning.curiosity_engine import CuriosityEngine
from learning.pattern_learner import PatternLearner
from learning.feedback_processor import FeedbackProcessor
from core.intelligence_engine import IntelligenceEngine

print("🧠 Initializing NeuroNest (Web Mode)...")

memory = MemoryManager(data_dir, max_context_window=10)
emotions = EmotionModel(data_dir / "emotional_state")
evolution = EvolutionEngine(config_dir, data_dir)
safety = SafetyController(config_dir)
personality = Personality(config_dir)

learning_systems = {
    "curiosity": CuriosityEngine(),
    "patterns": PatternLearner(data_dir),
    "feedback": FeedbackProcessor(data_dir),
}

engine = IntelligenceEngine(
    memory=memory,
    emotions=emotions,
    evolution=evolution,
    personality=personality,
    safety=safety,
    learning_systems=learning_systems,
    config_dir=config_dir,
)

print("✓ All systems online!")

# ---- Flask Routes ----

@app.route("/")
def index():
    """Serve the main dashboard."""
    if DIST_DIR.exists():
        return app.send_static_file("index.html")
    return render_template("dashboard.html")

@app.route("/api/status")
def get_status():
    """API endpoint to get current system status."""
    return jsonify({
        "evolution": evolution.get_status(),
        "emotions": emotions.get_emotional_state(),
        "memory": memory.get_stats(),
        "name": personality.get_name(),
        "model": engine.llm.get_status()
    })

@app.route("/api/model", methods=["GET", "POST"])
def model_route():
    """API endpoint to get or set the active LLM provider."""
    if request.method == "GET":
        return jsonify({
            "provider": engine.llm.get_provider(),
            "model_name": engine.llm.get_model()
        })

    data = request.json or {}
    provider = (data.get("provider") or "").strip().lower()
    if provider not in {"ollama", "gemini"}:
        return jsonify({"error": "Provider must be 'ollama' or 'gemini'."}), 400

    result = engine.llm.switch_provider(provider)
    if not result.get("success"):
        return jsonify(result), 500

    status = engine.llm.get_status()
    return jsonify({**result, "status": status})

@app.route("/api/chat", methods=["POST"])
def chat():
    """API endpoint for sending messages to NeuroNest."""
    data = request.json
    user_input = data.get("message", "")
    
    if not user_input.strip():
        return jsonify({"error": "Empty message"}), 400

    # Process through intelligence engine
    result = engine.process_input(user_input)
    
    # Save session state
    if result.get("should_exit"):
        memory.consolidate_session()
        
    return jsonify(result)

@app.route("/api/history")
def get_history():
    """Get the current session short-term memory history."""
    context = memory.get_context()
    return jsonify({"history": context})

@app.errorhandler(404)
def page_not_found(e):
    """Fallback for single page app routing."""
    if DIST_DIR.exists():
        return app.send_static_file("index.html")
    return "Not Found", 404

if __name__ == "__main__":
    print("\n🚀 Starting NeuroNest Web Dashboard on http://localhost:8080\n")
    # Turn off reloader to avoid initializing NeuroNest twice
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)
