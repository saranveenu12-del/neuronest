"""
NeuroNest — Evolution Engine
Manages developmental stage progression, XP, milestones, and behavioral scaling.
"""
import json, time
from pathlib import Path


class EvolutionEngine:
    """
    Tracks NeuroNest's growth through developmental stages.
    Manages XP, milestone achievements, and stage transitions.
    """

    def __init__(self, config_dir, data_dir):
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir) / "evolution_state"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "evolution_state.json"

        self.stages = self._load_stages()
        self._load_state()

    def _load_stages(self):
        stages_file = self.config_dir / "stages.json"
        with open(stages_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {s["id"]: s for s in data["stages"]}

    def _load_state(self):
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.current_stage_id = state.get("current_stage_id", 1)
                self.total_xp = state.get("total_xp", 0)
                self.milestone_progress = state.get("milestone_progress", {})
                self.stage_history = state.get("stage_history", [])
                self.total_interactions = state.get("total_interactions", 0)
                self.birth_time = state.get("birth_time", time.time())
            else:
                self._init_state()
        except (json.JSONDecodeError, IOError):
            self._init_state()

    def _init_state(self):
        self.current_stage_id = 1
        self.total_xp = 0
        self.milestone_progress = {}
        self.stage_history = [{
            "stage_id": 1, "entered_at": time.time(), "xp_at_entry": 0
        }]
        self.total_interactions = 0
        self.birth_time = time.time()
        self._save_state()

    def _save_state(self):
        state = {
            "current_stage_id": self.current_stage_id,
            "total_xp": self.total_xp,
            "milestone_progress": self.milestone_progress,
            "stage_history": self.stage_history,
            "total_interactions": self.total_interactions,
            "birth_time": self.birth_time,
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    # ---- XP System ----

    def award_xp(self, amount, reason="interaction"):
        """Award XP and check for stage progression."""
        self.total_xp += amount
        self.total_interactions += 1
        self._save_state()
        return self._check_progression()

    def get_xp_for_action(self, action_type):
        """Get XP reward amount for different action types."""
        xp_table = {
            "conversation": 2,
            "question_asked": 5,
            "fact_learned": 8,
            "pattern_recognized": 10,
            "correction_accepted": 12,
            "emotion_detected": 3,
            "memory_recalled": 4,
            "teaching_received": 15,
            "milestone_achieved": 50,
        }
        return xp_table.get(action_type, 1)

    # ---- Milestones ----

    def increment_milestone(self, milestone_key, amount=1):
        """Increment progress toward a milestone."""
        if milestone_key not in self.milestone_progress:
            self.milestone_progress[milestone_key] = 0
        self.milestone_progress[milestone_key] += amount

        # Check if milestone just completed
        stage = self.stages.get(self.current_stage_id, {})
        milestones = stage.get("milestones", {})
        if milestone_key in milestones:
            target = milestones[milestone_key]["target"]
            current = self.milestone_progress[milestone_key]
            if current == target:
                self.award_xp(self.get_xp_for_action("milestone_achieved"), "milestone")
                self._save_state()
                return milestones[milestone_key]["label"]

        self._save_state()
        return None

    def get_milestone_status(self):
        """Get progress on all milestones for the current stage."""
        stage = self.stages.get(self.current_stage_id, {})
        milestones = stage.get("milestones", {})
        status = {}
        for key, info in milestones.items():
            current = self.milestone_progress.get(key, 0)
            target = info["target"]
            status[key] = {
                "label": info["label"],
                "current": current,
                "target": target,
                "completed": current >= target,
                "percentage": min(100, int((current / target) * 100)),
            }
        return status

    # ---- Stage Progression ----

    def _check_progression(self):
        """Check if ready to progress to next stage."""
        stage = self.stages.get(self.current_stage_id)
        if not stage:
            return None

        xp_to_next = stage.get("xp_to_next")
        if xp_to_next is None:
            return None  # Already at max stage

        if self.total_xp >= xp_to_next:
            # Check if enough milestones are completed
            milestones = self.get_milestone_status()
            completed = sum(1 for m in milestones.values() if m["completed"])
            total = len(milestones)

            if total == 0 or completed >= total * 0.6:
                return {
                    "ready": True,
                    "next_stage": self.current_stage_id + 1,
                    "message": f"Ready to evolve to Stage {self.current_stage_id + 1}!",
                }
            else:
                return {
                    "ready": False,
                    "milestones_needed": int(total * 0.6) - completed,
                    "message": f"Need {int(total * 0.6) - completed} more milestones to evolve.",
                }
        return None

    def evolve(self):
        """
        Attempt to evolve to the next stage.

        Returns:
            (success: bool, message: str)
        """
        check = self._check_progression()
        if not check or not check.get("ready"):
            return False, "Not ready to evolve yet."

        next_id = check["next_stage"]
        if next_id not in self.stages:
            return False, "Already at maximum stage."

        self.current_stage_id = next_id
        self.stage_history.append({
            "stage_id": next_id,
            "entered_at": time.time(),
            "xp_at_entry": self.total_xp,
        })
        self._save_state()
        next_stage = self.stages[next_id]
        return True, f"🎉 Evolved to Stage {next_id}: {next_stage['name']} ({next_stage['age_label']})!"

    # ---- Queries ----

    def get_current_stage(self):
        """Return the current stage data."""
        return self.stages.get(self.current_stage_id, {})

    def get_capabilities(self):
        """Return current stage capabilities."""
        return self.get_current_stage().get("capabilities", {})

    def get_status(self):
        """Return comprehensive evolution status."""
        stage = self.get_current_stage()
        xp_to_next = stage.get("xp_to_next")
        xp_progress = 0
        if xp_to_next:
            stage_start_xp = stage.get("xp_required", 0)
            xp_in_stage = self.total_xp - stage_start_xp
            xp_needed = xp_to_next - stage_start_xp
            xp_progress = min(100, int((xp_in_stage / max(1, xp_needed)) * 100))

        age_days = (time.time() - self.birth_time) / 86400

        return {
            "stage_id": self.current_stage_id,
            "stage_name": stage.get("name", "Unknown"),
            "age_label": stage.get("age_label", "Unknown"),
            "total_xp": self.total_xp,
            "xp_to_next": xp_to_next,
            "xp_progress_percent": xp_progress,
            "total_interactions": self.total_interactions,
            "milestones": self.get_milestone_status(),
            "age_days": round(age_days, 1),
            "unlocked_features": stage.get("unlocked_features", []),
        }

    def get_xp_bar(self, width=30):
        """Visual XP progress bar for console display."""
        stage = self.get_current_stage()
        xp_to_next = stage.get("xp_to_next")
        if not xp_to_next:
            return "████████████████████████████████ MAX"
        stage_start = stage.get("xp_required", 0)
        progress = (self.total_xp - stage_start) / max(1, xp_to_next - stage_start)
        progress = min(1.0, max(0.0, progress))
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {self.total_xp}/{xp_to_next} XP"
