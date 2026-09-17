"""Safe, whitelisted system actions.

No arbitrary command execution here (see files.py docstring for why) -
just a small set of explicitly whitelisted, low-risk actions.
"""
import platform
import webbrowser


def open_url(url: str) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    opened = webbrowser.open(url)
    return f"Opened {url}." if opened else f"Could not open a browser for {url} (no display available)."


def system_info() -> str:
    return (
        f"{platform.system()} {platform.release()} "
        f"({platform.machine()}), Python {platform.python_version()}"
    )
