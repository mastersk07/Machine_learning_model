/* Chat wiring + browser-native voice (Web Speech API). No PyAudio needed
   here - this is separate from jarvis/voice.py, which is the CLI's
   Python-side voice path. Web Speech API is a Chrome/Edge feature; other
   browsers will just fall back to typing. */
(function () {
  const transcript = document.getElementById("transcript");
  const input = document.getElementById("text-input");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");

  function addMessage(text, cls) {
    const div = document.createElement("div");
    div.className = `msg ${cls}`;
    div.textContent = text;
    transcript.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    addMessage(text, "user");
    input.value = "";
    window.JarvisHUD.setState("thinking");

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await resp.json();

      if (!resp.ok) {
        addMessage(data.reply || "Something went wrong.", "error");
        window.JarvisHUD.setState("idle");
        return;
      }

      addMessage(data.reply, "jarvis");
      speak(data.reply);
    } catch (err) {
      addMessage(`Connection error: ${err.message}`, "error");
      window.JarvisHUD.setState("idle");
    }
  }

  function speak(text) {
    window.JarvisHUD.setState("speaking");
    if (!("speechSynthesis" in window)) {
      window.JarvisHUD.setState("idle");
      return;
    }
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;
    utter.pitch = 0.9;
    utter.onend = () => window.JarvisHUD.setState("idle");
    utter.onerror = () => window.JarvisHUD.setState("idle");
    window.speechSynthesis.speak(utter);
  }

  sendBtn.addEventListener("click", () => sendMessage(input.value));
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(input.value);
  });

  // Voice input via Web Speech API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    let listening = false;

    recognition.onstart = () => {
      listening = true;
      micBtn.classList.add("active");
      window.JarvisHUD.setState("listening");
    };
    recognition.onend = () => {
      listening = false;
      micBtn.classList.remove("active");
      if (window.JarvisHUD) window.JarvisHUD.setState("idle");
    };
    recognition.onerror = (e) => {
      addMessage(`Voice input error: ${e.error}`, "error");
    };
    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      sendMessage(text);
    };

    micBtn.addEventListener("click", () => {
      if (listening) {
        recognition.stop();
      } else {
        recognition.start();
      }
    });
  } else {
    micBtn.disabled = true;
    micBtn.title = "Voice input not supported in this browser (try Chrome/Edge)";
  }

  window.JarvisHUD && window.JarvisHUD.setState("idle");
  addMessage("Jarvis online. Standing by.", "jarvis");
})();
