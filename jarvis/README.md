# Jarvis

A personal AI assistant scaffold: text/voice chat over the TensorX API, plus
skills for web search, local files/code, Google Calendar, Gmail, and posting
to X/Facebook/Instagram.

## What this is, honestly

This was built and tested inside a sandboxed cloud container with **no
microphone, no speaker, and no network access to `api.tensorx.ai`,
`graph.facebook.com`, or `api.twitter.com`** (blocked by the sandbox's
egress policy). So:

- The code is structurally complete and each module has been reasoned
  through carefully, but the TensorX integration, voice I/O, and all social
  integrations have **not been run end-to-end**. You'll be the first one to
  actually exercise them.
- If something doesn't work first try (especially the TensorX request/response
  shape in `jarvis/llm.py`, which was written assuming an OpenAI-compatible
  API because the real contract couldn't be fetched from this sandbox),
  that's expected - treat this as a strong first draft, not a finished
  product.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # if starting fresh; your .env already has your TensorX key
```

### 1. Verify TensorX connectivity

```bash
python -m jarvis.llm
```

This hits `/models` and prints the result (or the actual error). If it
fails, paste the real error / API docs back so `jarvis/llm.py` can be
corrected to match TensorX's actual contract.

### 2. Run Jarvis (text mode CLI - always works)

```bash
python -m jarvis.main
```

### 2b. Run the holographic HUD web interface

```bash
python -m jarvis.web.app
```

Then open http://127.0.0.1:5000. This is a local Flask dev server - not
deployed anywhere, just runs on your machine. It's a dark sci-fi HUD with a
reactive animated core (Three.js/WebGL) that changes state as you talk to
Jarvis: idle (slow cyan pulse), listening (green), thinking (amber spin),
speaking (fast cyan pulse). Voice in/out here uses the **browser's** Web
Speech API (Chrome/Edge only) instead of PyAudio, so it works without any
extra system audio setup - click the 🎙 button and allow microphone access
when the browser prompts you. This was verified working in this sandbox
for page load, static assets, and the chat API (including the clean
TensorX-unreachable error path); the LLM call itself is still unverified
for the same reason as the CLI, see below.

This is a real 3D-animated interface, but it is not a "metaverse" (no
VR, no persistent 3D world, no avatar) - see the note under "What's
deliberately NOT built".

### 3. Voice mode in the CLI (needs your own machine, mic, and speakers)

This needs an extra install - `requirements.txt` deliberately does NOT
include PyAudio, since it fails to build without a system library first
(and isn't needed at all for the web HUD):

- macOS: `brew install portaudio`
- Debian/Ubuntu: `sudo apt install portaudio19-dev python3-pyaudio`
- Windows: PyAudio wheels install directly via pip

Then:

```bash
pip install -r requirements-cli-voice.txt
python -m jarvis.main --voice
```

It falls back to text automatically if no mic is detected.

### 4. Google Calendar / Gmail (optional)

1. https://console.cloud.google.com/ -> new project.
2. Enable "Google Calendar API" and/or "Gmail API".
3. OAuth consent screen -> External -> add yourself as a test user.
4. Credentials -> Create OAuth client ID -> **Desktop app** -> download the
   JSON -> save as `credentials.json` in the repo root.
5. In `.env`, set `GOOGLE_CALENDAR_ENABLED=true` and/or `GMAIL_ENABLED=true`.
6. First relevant command opens a browser for consent; a token is cached
   locally afterward (`token.json` / `gmail_token.json`, both gitignored).

Ask things like *"what's on my calendar"* or *"check my email"*.

### 5. X (Twitter) (optional)

1. https://developer.twitter.com -> create a project/app with read+write access.
2. Generate a Bearer Token (search/read) and OAuth 1.0a User Context keys
   (API key/secret + access token/secret) for posting.
3. Fill `X_BEARER_TOKEN`, `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`,
   `X_ACCESS_SECRET` in `.env`.

Say *"post \<text\> to x"* to post, or *"search for \<query\>"* falls back to
web search, not X search (X search isn't wired into the router yet - use
`jarvis.skills.x_social.recent_search()` directly if you need it).

### 6. Instagram / Facebook (optional)

1. https://developers.facebook.com -> create an app -> add the Instagram
   Graph API and/or Pages API products.
2. Generate a long-lived Page Access Token with the permissions you need.
   Some permissions require Meta's app review before they work on anything
   but your own test accounts.
3. Fill `META_PAGE_ACCESS_TOKEN`, `META_IG_USER_ID`, `META_FB_PAGE_ID` in `.env`.

Say *"post \<text\> to facebook"*. Instagram posting
(`jarvis.skills.meta_social.post_to_instagram`) needs a publicly reachable
image URL and isn't wired into the text router yet - call it directly.

## What's deliberately NOT built

- **No arbitrary shell command execution.** `jarvis/skills/files.py` runs
  Python snippets in a sandboxed subprocess with a timeout, confined to
  `jarvis/workspace/`. A voice/text-driven assistant that can run *any*
  shell command anywhere on your disk is a real security risk (misheard
  speech, a malicious instruction slipped into some text it reads). If you
  want to widen this, do it deliberately with your own risk assessment.
- **No blanket "full access" to your Google/social accounts.** Every
  integration uses the narrowest scope for what you asked for (calendar
  read, Gmail read+send, specific social posting), each gated behind
  credentials only you can generate.
- **No physical-world capability.** This is software running on a computer
  - no cameras, no sensors, no robotics. If the "Jarvis" framing implied
  otherwise, that's fiction, not something this code can do.
- **No actual "metaverse" / VR interface.** The web HUD is a real animated
  3D scene rendered with WebGL (Three.js) in a normal browser tab - it
  looks like a sci-fi holographic display, but it is not a persistent 3D
  world, has no avatar, and doesn't need or support a VR headset. A true
  metaverse-style environment is a multi-month game-engine project
  (Unreal/Unity, 3D asset pipelines, VR SDKs), well beyond what a personal
  assistant interface needs.

## Project layout

```
jarvis/
  main.py            CLI entry point (text/voice loop)
  router.py           keyword router: skill match, else fall back to LLM
  llm.py               TensorX chat client
  personality.py       Jarvis system prompt
  voice.py             CLI-side STT/TTS wrapper (PyAudio) with fallback
  config.py            env var loading
  web/
    app.py              Flask app (HUD web interface)
    templates/index.html
    static/style.css     dark sci-fi HUD theme
    static/hud.js         Three.js reactive animated core
    static/app.js          chat wiring + browser Web Speech API voice
  skills/
    time_skill.py
    web_search.py       DuckDuckGo, no API key needed
    files.py             sandboxed file read/write + python exec
    system_actions.py    open URL, system info
    google_calendar.py
    gmail.py
    x_social.py
    meta_social.py       Instagram + Facebook
```
