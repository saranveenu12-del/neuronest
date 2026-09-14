"""
NeuroNest — Ollama Client
Handles communication with the local Ollama API.
"""
import requests

class OllamaClient:
    def __init__(self, model_name='llama3', base_url='http://localhost:11434'):
        self.model_name = model_name
        self.base_url = base_url
        self.session_context = None
        self.ready = True
        self.error_message = None

    def generate(self, prompt, system_prompt="", use_context=True):
        url = f"{self.base_url}/api/generate"
        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'system': system_prompt,
            'stream': False
        }
        if use_context and self.session_context is not None:
            payload['context'] = self.session_context

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            if use_context:
                self.session_context = data.get('context', [])
            return data.get('response', '').strip()
        except requests.exceptions.RequestException as e:
            self.ready = False
            self.error_message = str(e)
            print(f'Ollama API error: {e}')
            return f"I'm having trouble connecting to my AI brain (Ollama). Please make sure Ollama is running and the '{self.model_name}' model is pulled."

    def get_status(self):
        return {
            "provider": "ollama",
            "model_name": self.model_name,
            "ready": self.ready,
            "error": self.error_message,
        }

    def clear_context(self):
        self.session_context = None
