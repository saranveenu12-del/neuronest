"""
NeuroNest — Knowledge Base Import Script
Imports topics, facts, and key points from knowledge_base.json into NeuroNest's long-term memory and knowledge graph.
"""
import json
import sys
from pathlib import Path

# Fix terminal encoding for emojis on Windows
if (sys.stdout.encoding or '').lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from memory.memory_manager import MemoryManager

def main():
    print("🧠 Initializing Memory Manager...")
    data_dir = PROJECT_ROOT / "data"
    memory = MemoryManager(data_dir)

    kb_path = PROJECT_ROOT / "neuronest-showcase" / "client" / "public" / "knowledge_base.json"
    if not kb_path.exists():
        print(f"❌ Error: knowledge_base.json not found at: {kb_path}")
        sys.exit(1)

    print(f"📖 Reading knowledge base from {kb_path}...")
    with open(kb_path, "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    print(f"🚀 Importing {len(kb_data)} topics into memory...")
    imported_topics = 0
    imported_facts = 0

    for topic, entry in kb_data.items():
        # 1. Store structured knowledge
        memory.store_knowledge(topic, entry)
        imported_topics += 1

        # 2. Store key points as individual recallable facts
        category = entry.get("category", "general")
        for kp in entry.get("key_points", []):
            stored = memory.learn_fact(kp, source="showcase_import", category=category)
            if stored:
                imported_facts += 1

    # Force immediate save/consolidation by updating experiences
    memory.store_experience(
        event_type="knowledge_import",
        description=f"Successfully imported {imported_topics} topics and {imported_facts} new facts from showcase database.",
        significance=0.8
    )

    print(f"✅ Import complete! Imported {imported_topics} topics and {imported_facts} facts.")
    print("Memory statistics after import:")
    stats = memory.get_stats()
    print(f"  - Total Facts: {stats.get('total_facts')}")
    print(f"  - Total Entities: {stats.get('total_entities')}")
    print(f"  - Total Topics: {stats.get('total_knowledge_topics')}")

if __name__ == "__main__":
    main()
