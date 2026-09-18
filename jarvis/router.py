"""Lightweight keyword-based intent router.

TensorX's support for OpenAI-style function/tool calling is unverified
from this sandbox, so rather than depend on that, simple commands are
matched by keyword before falling back to general LLM chat. This is
deliberately basic - good enough for clear commands, not a full NLU
system.
"""
import re

from jarvis.skills import files, system_actions, time_skill, web_search
from jarvis.skills import google_calendar, gmail, x_social, meta_social


def route(text: str) -> str | None:
    """Returns a skill's output if `text` matches a known command,
    else None (caller should fall back to the LLM)."""
    t = text.strip().lower()

    if re.search(r"\b(what.?s the time|current time|what time is it)\b", t):
        return time_skill.current_time()

    m = re.search(r"\bsearch(?: the web)? for (.+)", t)
    if m:
        return web_search.search(m.group(1).strip())

    if re.search(r"\b(list|show) (my )?files\b", t):
        return files.list_files()

    m = re.search(r"\bopen (https?://\S+|\S+\.\S+)\b", t)
    if m:
        return system_actions.open_url(m.group(1))

    if re.search(r"\b(system info|about this system)\b", t):
        return system_actions.system_info()

    if re.search(r"\b(my calendar|upcoming events|what.?s on my calendar)\b", t):
        return google_calendar.upcoming_events()

    if re.search(r"\b(check|read) (my )?(email|gmail|inbox)\b", t):
        return gmail.read_recent()

    m = re.search(r"\bpost (.+) to (x|twitter)\b", t)
    if m:
        return x_social.post_tweet(m.group(1).strip())

    m = re.search(r"\bpost (.+) to facebook\b", t)
    if m:
        return meta_social.post_to_facebook(m.group(1).strip())

    return None
