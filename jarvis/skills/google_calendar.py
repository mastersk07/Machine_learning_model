"""Google Calendar (read-only), scoped to what was actually requested.

Setup (do this on your own machine, not in this sandbox):
1. https://console.cloud.google.com/ -> new project -> enable "Google Calendar API".
2. OAuth consent screen -> External -> add yourself as a test user.
3. Credentials -> Create OAuth client ID -> Desktop app -> download JSON,
   save it as `credentials.json` in the repo root (gitignored already).
4. Set GOOGLE_CALENDAR_ENABLED=true in .env.
5. First call opens a browser for you to grant calendar.readonly consent;
   a token.json is cached afterward (also gitignored).
"""
import os

from jarvis import config

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"


def _get_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"{CREDENTIALS_PATH} not found. See setup instructions in "
                    "jarvis/skills/google_calendar.py."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def upcoming_events(max_results: int = 10) -> str:
    if not config.GOOGLE_CALENDAR_ENABLED:
        return "Google Calendar isn't enabled. Set GOOGLE_CALENDAR_ENABLED=true in .env after completing setup."

    import datetime

    try:
        service = _get_service()
    except Exception as exc:  # noqa: BLE001
        return f"Couldn't connect to Google Calendar: {exc}"

    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    if not events:
        return "No upcoming events."

    lines = ["Upcoming events:"]
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        lines.append(f"- {start}: {event.get('summary', '(no title)')}")
    return "\n".join(lines)
