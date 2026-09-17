"""Gmail (read + send), scoped to what was actually requested.

Setup: same Google Cloud project as google_calendar.py - additionally
enable the "Gmail API", and note the scopes below are broader (read +
send). Same credentials.json / token.json flow.
"""
import base64
import os
from email.mime.text import MIMEText

from jarvis import config

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "gmail_token.json"


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
                    "jarvis/skills/gmail.py."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def read_recent(max_results: int = 5) -> str:
    if not config.GMAIL_ENABLED:
        return "Gmail isn't enabled. Set GMAIL_ENABLED=true in .env after completing setup."

    try:
        service = _get_service()
    except Exception as exc:  # noqa: BLE001
        return f"Couldn't connect to Gmail: {exc}"

    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])
    if not messages:
        return "No messages found."

    lines = ["Recent messages:"]
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="metadata",
                                              metadataHeaders=["From", "Subject"]).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        lines.append(f"- From: {headers.get('From', '?')} | Subject: {headers.get('Subject', '(no subject)')}")
    return "\n".join(lines)


def send_email(to: str, subject: str, body: str) -> str:
    if not config.GMAIL_ENABLED:
        return "Gmail isn't enabled. Set GMAIL_ENABLED=true in .env after completing setup."

    try:
        service = _get_service()
    except Exception as exc:  # noqa: BLE001
        return f"Couldn't connect to Gmail: {exc}"

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"Email sent to {to}."
