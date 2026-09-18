"""Instagram / Facebook via Meta Graph API - read/post.

Setup: https://developers.facebook.com -> create an app -> add
Instagram Graph API / Pages API products -> generate a long-lived Page
Access Token with the relevant permissions (instagram_content_publish,
pages_read_engagement, etc.) -> fill META_* values in .env. Nothing here
works until you provide those; Meta's review process is also required for
some permissions before they work on anything but your own test accounts.
"""
import requests

from jarvis import config

GRAPH_BASE = "https://graph.facebook.com/v20.0"


def facebook_recent_posts(max_results: int = 5) -> str:
    if not (config.META_PAGE_ACCESS_TOKEN and config.META_FB_PAGE_ID):
        return "Facebook isn't configured. Set META_PAGE_ACCESS_TOKEN and META_FB_PAGE_ID in .env."

    resp = requests.get(
        f"{GRAPH_BASE}/{config.META_FB_PAGE_ID}/posts",
        params={"access_token": config.META_PAGE_ACCESS_TOKEN, "limit": max_results},
        timeout=15,
    )
    if resp.status_code != 200:
        return f"Facebook fetch failed: HTTP {resp.status_code} - {resp.text[:300]}"

    data = resp.json().get("data", [])
    if not data:
        return "No recent posts."
    lines = ["Recent Facebook posts:"]
    for p in data:
        lines.append(f"- {p.get('message', '(no text)')[:120]}")
    return "\n".join(lines)


def post_to_facebook(message: str) -> str:
    if not (config.META_PAGE_ACCESS_TOKEN and config.META_FB_PAGE_ID):
        return "Facebook isn't configured. Set META_PAGE_ACCESS_TOKEN and META_FB_PAGE_ID in .env."

    resp = requests.post(
        f"{GRAPH_BASE}/{config.META_FB_PAGE_ID}/feed",
        data={"message": message, "access_token": config.META_PAGE_ACCESS_TOKEN},
        timeout=15,
    )
    if resp.status_code not in (200, 201):
        return f"Posting to Facebook failed: HTTP {resp.status_code} - {resp.text[:300]}"
    return "Posted to Facebook."


def post_to_instagram(image_url: str, caption: str) -> str:
    """Instagram posting is a two-step publish flow: create a media
    container, then publish it. Requires a publicly reachable image_url."""
    if not (config.META_PAGE_ACCESS_TOKEN and config.META_IG_USER_ID):
        return "Instagram isn't configured. Set META_PAGE_ACCESS_TOKEN and META_IG_USER_ID in .env."

    create = requests.post(
        f"{GRAPH_BASE}/{config.META_IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": config.META_PAGE_ACCESS_TOKEN,
        },
        timeout=15,
    )
    if create.status_code != 200:
        return f"Instagram container creation failed: HTTP {create.status_code} - {create.text[:300]}"
    container_id = create.json().get("id")

    publish = requests.post(
        f"{GRAPH_BASE}/{config.META_IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": config.META_PAGE_ACCESS_TOKEN},
        timeout=15,
    )
    if publish.status_code != 200:
        return f"Instagram publish failed: HTTP {publish.status_code} - {publish.text[:300]}"
    return "Posted to Instagram."
