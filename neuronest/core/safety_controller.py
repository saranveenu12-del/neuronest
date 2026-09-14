"""
NeuroNest — Safety Controller
Enforces stage-appropriate restrictions, permissions, and oversight.
"""
import json, time, logging
from pathlib import Path

logger = logging.getLogger("neuronest.safety")


class SafetyController:
    """Enforces safety rules based on the current evolutionary stage."""

    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.rules = self._load_rules()
        self.safety_log = []

    def _load_rules(self):
        rules_file = self.config_dir / "safety_rules.json"
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load safety rules: {e}")
            return {"global_rules": {}, "stage_rules": {}, "admin_commands": {}}

    def check_action(self, action, current_stage_id):
        """
        Check if an action is allowed at the current stage.

        Returns:
            (allowed: bool, reason: str)
        """
        stage_key = str(current_stage_id)
        stage_rules = self.rules.get("stage_rules", {}).get(stage_key, {})

        allowed_actions = stage_rules.get("allowed_actions", [])
        blocked_actions = stage_rules.get("blocked_actions", [])

        if action in blocked_actions:
            reason = f"Action '{action}' is blocked at Stage {current_stage_id} ({stage_rules.get('stage_name', 'Unknown')})"
            self._log_event("BLOCKED", action, reason)
            return False, reason

        if "all" in allowed_actions or action in allowed_actions:
            return True, "Allowed"

        reason = f"Action '{action}' is not in the allowed list for Stage {current_stage_id}"
        self._log_event("DENIED", action, reason)
        return False, reason

    def needs_confirmation(self, action, current_stage_id):
        """Check if an action requires human confirmation."""
        stage_key = str(current_stage_id)
        stage_rules = self.rules.get("stage_rules", {}).get(stage_key, {})
        confirm_list = stage_rules.get("confirmation_required_for", [])
        return action in confirm_list

    def get_autonomy_level(self, current_stage_id):
        """Get the autonomy level for the current stage."""
        stage_key = str(current_stage_id)
        stage_rules = self.rules.get("stage_rules", {}).get(stage_key, {})
        return stage_rules.get("autonomy_level", 0.2)

    def get_content_restrictions(self, current_stage_id):
        """Get content restrictions for the current stage."""
        stage_key = str(current_stage_id)
        stage_rules = self.rules.get("stage_rules", {}).get(stage_key, {})
        return stage_rules.get("content_restrictions", {})

    def check_content(self, text, current_stage_id):
        """
        Basic content safety check.

        Returns:
            (safe: bool, issues: list)
        """
        issues = []
        restrictions = self.get_content_restrictions(current_stage_id)

        if not restrictions.get("allow_controversial_topics", False):
            # Very basic check - in production this would be more sophisticated
            controversial_patterns = [
                "politics", "religion", "violence", "weapon",
            ]
            text_lower = text.lower()
            for pattern in controversial_patterns:
                if pattern in text_lower:
                    issues.append(f"Controversial topic detected: {pattern}")

        return len(issues) == 0, issues

    def _log_event(self, event_type, action, details):
        """Log a safety event."""
        entry = {
            "type": event_type,
            "action": action,
            "details": details,
            "timestamp": time.time(),
        }
        self.safety_log.append(entry)
        logger.info(f"Safety [{event_type}]: {action} — {details}")

    def get_recent_logs(self, n=20):
        """Get recent safety log entries."""
        return self.safety_log[-n:]
