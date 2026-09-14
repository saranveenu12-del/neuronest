"""
NeuroNest — Gemini Client
Handles communication with Google's Gemini API using the google-generativeai package.
"""
import os

class GeminiClient:
    def __init__(self, model_name="gemini-3.5-pro", api_key_env="GEMINI_API_KEY"):
        self.model_name = model_name
        self.api_key_env = api_key_env
        self.api_key = os.environ.get(self.api_key_env)
        self.model = None
        self.ready = False
        self.error_message = None

        if not self.api_key:
            self.error_message = f"Gemini API key not found in environment variable '{self.api_key_env}'."
            print(self.error_message)
            return

        try:
            from google import generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name=self.model_name)
            self.ready = True
        except Exception as exc:
            self.error_message = f"Gemini client initialization failed: {exc}"
            print(self.error_message)

    def generate(self, prompt, system_prompt="", use_context=True):
        if self.model is None or not self.ready:
            return (
                "I'm unable to access Gemini because the Gemini client failed to initialize. "
                "Please set the GEMINI_API_KEY environment variable and install google-generativeai."
            )

        request_text = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
        try:
            response = self.model.generate_content(request_text)
            return self._extract_response_text(response)
        except Exception as exc:
            print(f"Gemini API error: {exc}")
            return (
                "I'm having trouble connecting to my AI brain (Gemini). "
                "Please check the Gemini API key and your internet connection."
            )

    def get_status(self):
        return {
            "provider": "gemini",
            "model_name": self.model_name,
            "ready": self.ready,
            "error": self.error_message,
        }

    def _extract_response_text(self, response):
        if response is None:
            return ""
        if isinstance(response, str):
            return response.strip()
        if hasattr(response, "text"):
            return response.text.strip()
        if hasattr(response, "output"):
            return str(response.output).strip()
        if isinstance(response, dict):
            return response.get("text", "") or response.get("output", "")
        return str(response).strip()
