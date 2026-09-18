"""X (Twitter) API v2 - read/post.

Setup: https://developer.twitter.com -> create a project + app with
read/write access -> generate a Bearer Token (for reads) and, for posting,
OAuth 1.0a User Context keys (API key/secret + access token/secret).
Fill X_* values in .env. Nothing here works until you provide those.
"""
import requests

from jarvis import config

API_BASE = "https://api.twitter.com/2"


def recent_search(query: str, max_results: int = 5) -> str:
    if not config.X_BEARER_TOKEN:
        return "X isn't configured. Set X_BEARER_TOKEN in .env (see jarvis/skills/x_social.py)."

    headers = {"Authorization": f"Bearer {config.X_BEARER_TOKEN}"}
    params = {"query": query, "max_results": max(10, max_results)}
    resp = requests.get(f"{API_BASE}/tweets/search/recent", headers=headers, params=params, timeout=15)
    if resp.status_code != 200:
        return f"X search failed: HTTP {resp.status_code} - {resp.text[:300]}"

    data = resp.json().get("data", [])
    if not data:
        return f"No recent tweets found for '{query}'."
    lines = [f"Recent tweets for '{query}':"]
    for t in data[:max_results]:
        lines.append(f"- {t.get('text', '')}")
    return "\n".join(lines)


def post_tweet(text: str) -> str:
    if not all([config.X_API_KEY, config.X_API_SECRET, config.X_ACCESS_TOKEN, config.X_ACCESS_SECRET]):
        return "X posting isn't configured. Set X_API_KEY/X_API_SECRET/X_ACCESS_TOKEN/X_ACCESS_SECRET in .env."

    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        return "Posting to X requires `requests_oauthlib`: pip install requests-oauthlib"

    auth = OAuth1(
        config.X_API_KEY, config.X_API_SECRET,
        config.X_ACCESS_TOKEN, config.X_ACCESS_SECRET,
    )
    resp = requests.post(f"{API_BASE}/tweets", auth=auth, json={"text": text}, timeout=15)
    if resp.status_code not in (200, 201):
        return f"Posting to X failed: HTTP {resp.status_code} - {resp.text[:300]}"
    return "Posted to X."
