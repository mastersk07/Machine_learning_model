"""Voice I/O for Jarvis, with graceful fallback to text.

This sandbox has no microphone/speaker hardware, so none of this can be
exercised here - only imported and structurally checked. Run it on your own
machine (with a mic and speakers, and PyAudio's system dependencies
installed - see README) to actually use voice mode.
"""
import sys


class VoiceUnavailable(RuntimeError):
    pass


def _load_backends():
    import speech_recognition as sr
    import pyttsx3

    return sr, pyttsx3


class VoiceIO:
    def __init__(self):
        try:
            sr, pyttsx3 = _load_backends()
            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone()  # raises OSError if no input device
            self._tts = pyttsx3.init()
            self.available = True
        except Exception as exc:  # noqa: BLE001
            self.available = False
            self._error = exc

    def listen(self) -> str:
        if not self.available:
            raise VoiceUnavailable(f"Voice input unavailable: {self._error}")
        import speech_recognition as sr

        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source)
            print("Listening...", file=sys.stderr)
            audio = self._recognizer.listen(source)
        try:
            return self._recognizer.recognize_google(audio)
        except sr.UnknownValueError as exc:
            raise VoiceUnavailable("Could not understand audio") from exc
        except sr.RequestError as exc:
            raise VoiceUnavailable(f"Speech recognition service error: {exc}") from exc

    def speak(self, text: str) -> None:
        if not self.available:
            raise VoiceUnavailable(f"Voice output unavailable: {self._error}")
        self._tts.say(text)
        self._tts.runAndWait()
