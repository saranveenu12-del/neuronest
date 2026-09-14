"""
NeuroNest — Knowledge Graph Module
Tracks entities and relationships forming a web of connected knowledge.
"""
import json, time
from pathlib import Path


class KnowledgeGraph:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.graph_file = self.data_dir / "knowledge_graph.json"
        data = self._load()
        self.entities = data.get("entities", {})
        self.relationships = data.get("relationships", [])

    def _load(self):
        try:
            if self.graph_file.exists():
                with open(self.graph_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {"entities": {}, "relationships": []}

    def _save(self):
        data = {"entities": self.entities, "relationships": self.relationships}
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_entity(self, name, entity_type="concept", properties=None):
        key = name.lower().strip()
        if key not in self.entities:
            self.entities[key] = {
                "name": name, "type": entity_type,
                "properties": properties or {},
                "first_seen": time.time(),
                "last_referenced": time.time(),
                "reference_count": 1,
            }
        else:
            self.entities[key]["last_referenced"] = time.time()
            self.entities[key]["reference_count"] += 1
            if properties:
                self.entities[key]["properties"].update(properties)
        self._save()

    def add_relationship(self, entity1, relation, entity2):
        self.add_entity(entity1)
        self.add_entity(entity2)
        rel = {
            "source": entity1.lower().strip(),
            "relation": relation,
            "target": entity2.lower().strip(),
            "timestamp": time.time(),
        }
        for existing in self.relationships:
            if (existing["source"] == rel["source"]
                    and existing["relation"] == rel["relation"]
                    and existing["target"] == rel["target"]):
                return
        self.relationships.append(rel)
        self._save()

    def get_entity(self, name):
        return self.entities.get(name.lower().strip())

    def get_relationships_for(self, entity_name):
        key = entity_name.lower().strip()
        return [r for r in self.relationships
                if r["source"] == key or r["target"] == key]

    def get_related_entities(self, entity_name):
        key = entity_name.lower().strip()
        related = set()
        for rel in self.relationships:
            if rel["source"] == key:
                related.add(rel["target"])
            elif rel["target"] == key:
                related.add(rel["source"])
        return list(related)

    def search_entities(self, query, limit=10):
        q = query.lower()
        return [e for k, e in self.entities.items() if q in k][:limit]

    def get_stats(self):
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
        }
