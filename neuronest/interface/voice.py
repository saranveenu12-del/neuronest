"""
NeuroNest — Voice Interface
Text-to-speech and speech-to-text integration (offline TTS via pyttsx3).
"""
import re


class VoiceInterface:
    """Handles voice output (TTS) and optional voice input (STT)."""

    def __init__(self):
        self.tts_engine = None
        self.stt_available = False
        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        """Initialize text-to-speech engine."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            # Configure voice
            self.tts_engine.setProperty("rate", 160)  # Speed
            self.tts_engine.setProperty("volume", 0.9)
            # Try to use a friendly voice
            voices = self.tts_engine.getProperty("voices")
            if voices and len(voices) > 1:
                # Usually index 1 is a female voice on Windows
                self.tts_engine.setProperty("voice", voices[1].id)
        except Exception:
            self.tts_engine = None

    def _init_stt(self):
        """Initialize speech-to-text (optional)."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.stt_available = True
        except (ImportError, OSError):
            self.stt_available = False

    def speak(self, text):
        """Speak text aloud using TTS."""
        if not self.tts_engine:
            return False
        try:
            # Clean text for speech (remove emojis and special chars)
            clean = self._clean_for_speech(text)
            if clean.strip():
                self.tts_engine.say(clean)
                self.tts_engine.runAndWait()
            return True
        except Exception:
            return False

    def listen(self, timeout=5):
        """
        Listen for voice input using microphone.

        Returns:
            Recognized text string, or None if failed.
        """
        if not self.stt_available:
            return None
        try:
            import speech_recognition as sr
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
            text = self.recognizer.recognize_google(audio)
            return text
        except Exception:
            return None

    def _clean_for_speech(self, text):
        """Remove emojis and special characters for cleaner speech."""
        # Remove emoji unicode ranges
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & pictographs
            "\U0001F680-\U0001F6FF"  # Transport & map
            "\U0001F1E0-\U0001F1FF"  # Flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub("", text)
        # Remove special symbols
        text = text.replace("✧", "").replace("─", "")
        text = re.sub(r"[★☆●◆▸▹►▻➤➜→]", "", text)
        return text.strip()

    @property
    def tts_available(self):
        return self.tts_engine is not None
