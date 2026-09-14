"""
NeuroNest — LLM Client Abstraction
Routes text generation requests to the configured provider: Ollama or Gemini.
"""
import json
import os
from pathlib import Path

from core.gemini_client import GeminiClient
from core.ollama_client import OllamaClient

DEFAULT_CONFIG = {
    "provider": "ollama",
    "ollama": {
        "model_name": "llama3",
        "base_url": "http://localhost:11434"
    },
    "gemini": {
        "model_name": "gemini-3.5-pro",
        "api_key_env": "GEMINI_API_KEY"
    }
}


class LLMClient:
    def __init__(self, config_path=None):
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
        self.provider = os.environ.get(
            "NEURONEST_LLM_PROVIDER",
            self.config.get("provider", DEFAULT_CONFIG["provider"])
        ).lower()
        self.client = self._create_client()
        self.model_name = getattr(self.client, "model_name", None)

    def _resolve_config_path(self, config_path):
        if config_path:
            return Path(config_path)
        default_path = Path(__file__).resolve().parents[1] / "config" / "model_config.json"
        return default_path

    def _load_config(self):
        try:
            if self.config_path.exists():
                with self.config_path.open("r", encoding="utf-8") as handle:
                    return json.load(handle)
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()

    def _create_client(self):
        if self.provider == "gemini":
            gemini_config = self.config.get("gemini", {})
            model_name = os.environ.get(
                "NEURONEST_GEMINI_MODEL",
                gemini_config.get("model_name", DEFAULT_CONFIG["gemini"]["model_name"])
            )
            api_key_env = gemini_config.get("api_key_env", DEFAULT_CONFIG["gemini"]["api_key_env"])
            return GeminiClient(model_name=model_name, api_key_env=api_key_env)

        ollama_config = self.config.get("ollama", {})
        model_name = os.environ.get(
            "NEURONEST_OLLAMA_MODEL",
            ollama_config.get("model_name", DEFAULT_CONFIG["ollama"]["model_name"])
        )
        base_url = os.environ.get(
            "NEURONEST_OLLAMA_BASE_URL",
            ollama_config.get("base_url", DEFAULT_CONFIG["ollama"]["base_url"])
        )
        return OllamaClient(model_name=model_name, base_url=base_url)

    def generate(self, prompt, system_prompt="", use_context=True):
        return self.client.generate(prompt, system_prompt=system_prompt, use_context=use_context)

    def clear_context(self):
        if hasattr(self.client, "clear_context"):
            self.client.clear_context()

    def _save_config(self):
        try:
            if self.config_path:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with self.config_path.open("w", encoding="utf-8") as handle:
                    json.dump(self.config, handle, indent=2)
        except Exception:
            pass

    def switch_provider(self, provider):
        provider = provider.lower()
        if provider not in {"ollama", "gemini"}:
            return {"success": False, "error": f"Unsupported provider '{provider}'."}

        self.provider = provider
        self.config["provider"] = provider
        self._save_config()
        self.client = self._create_client()
        self.model_name = getattr(self.client, "model_name", None)

        return {
            "success": True,
            "provider": self.provider,
            "model_name": self.model_name,
        }

    def get_status(self):
        status = {
            "provider": self.provider,
            "model_name": self.model_name,
            "ready": True,
            "error": None,
        }
        if self.client is None:
            status["ready"] = False
            status["error"] = "No LLM client available."
            return status

        if hasattr(self.client, "get_status"):
            return self.client.get_status()

        return status

    def get_provider(self):
        return self.provider

    def get_model(self):
        return self.model_name
