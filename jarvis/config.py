"""Loads configuration from environment variables (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


TENSORX_API_KEY = os.environ.get("TENSORX_API_KEY", "")
TENSORX_BASE_URL = os.environ.get("TENSORX_BASE_URL", "https://api.tensorx.ai/v1")
TENSORX_MODEL = os.environ.get("TENSORX_MODEL", "default")

GOOGLE_CALENDAR_ENABLED = _bool("GOOGLE_CALENDAR_ENABLED")
GMAIL_ENABLED = _bool("GMAIL_ENABLED")

X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")
X_API_KEY = os.environ.get("X_API_KEY", "")
X_API_SECRET = os.environ.get("X_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "")

META_PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN", "")
META_IG_USER_ID = os.environ.get("META_IG_USER_ID", "")
META_FB_PAGE_ID = os.environ.get("META_FB_PAGE_ID", "")

WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jarvis", "workspace")
