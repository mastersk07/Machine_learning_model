"""Jarvis holographic HUD web interface.

A local Flask app - not deployed anywhere, runs on your own machine. Voice
in/out here uses the *browser's* Web Speech API (no PyAudio needed), which
only Chrome/Edge support well; the CLI's jarvis/voice.py (Python-side
speech_recognition/pyttsx3) is a separate path for --voice mode in the
terminal.

Run with:
    python -m jarvis.web.app
then open http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

from jarvis import llm, router
from jarvis.personality import SYSTEM_PROMPT

app = Flask(__name__)

# In-memory, single-user session history. Fine for a local personal
# assistant; not meant to serve multiple concurrent users.
_history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_text = (data.get("message") or "").strip()
    if not user_text:
        return jsonify({"error": "empty message"}), 400

    skill_reply = router.route(user_text)
    if skill_reply is not None:
        return jsonify({"reply": skill_reply, "source": "skill"})

    _history.append({"role": "user", "content": user_text})
    try:
        reply = llm.chat(_history)
    except llm.TensorXError as exc:
        return jsonify({"reply": f"Jarvis couldn't reach TensorX: {exc}", "source": "error"}), 502

    _history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply, "source": "llm"})


@app.route("/api/reset", methods=["POST"])
def reset():
    global _history
    _history = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"ok": True})


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
