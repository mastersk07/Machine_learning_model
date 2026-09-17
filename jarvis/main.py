"""Jarvis entry point.

Usage:
    python -m jarvis.main          # text mode
    python -m jarvis.main --voice  # voice mode (needs mic/speaker + PyAudio)
"""
import argparse
import sys

from jarvis import llm, router
from jarvis.personality import SYSTEM_PROMPT


def run(voice: bool) -> None:
    voice_io = None
    if voice:
        from jarvis.voice import VoiceIO

        voice_io = VoiceIO()
        if not voice_io.available:
            print(
                f"Voice mode unavailable ({voice_io._error}); falling back to text.",
                file=sys.stderr,
            )
            voice_io = None

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Jarvis is online. Type 'exit' to quit.\n")

    while True:
        if voice_io:
            try:
                user_text = voice_io.listen()
                print(f"You: {user_text}")
            except Exception as exc:  # noqa: BLE001
                print(f"(voice error: {exc}, type instead)")
                user_text = input("You: ")
        else:
            user_text = input("You: ")

        if user_text.strip().lower() in ("exit", "quit"):
            print("Jarvis: Goodbye.")
            break

        skill_reply = router.route(user_text)
        if skill_reply is not None:
            reply = skill_reply
        else:
            history.append({"role": "user", "content": user_text})
            try:
                reply = llm.chat(history)
            except llm.TensorXError as exc:
                reply = f"(Jarvis couldn't reach TensorX: {exc})"
            history.append({"role": "assistant", "content": reply})

        print(f"Jarvis: {reply}\n")
        if voice_io:
            try:
                voice_io.speak(reply)
            except Exception as exc:  # noqa: BLE001
                print(f"(voice output error: {exc})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis personal AI assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice input/output")
    args = parser.parse_args()
    run(voice=args.voice)


if __name__ == "__main__":
    main()
