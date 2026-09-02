"""Google Chat REST client: post threaded messages, download attachments.

Auth: the app's own service account with scope chat.bot — the app can only act
in spaces it has been added to. No domain-wide delegation.
"""

import io
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from . import env

SCOPES = ["https://www.googleapis.com/auth/chat.bot"]

# Chat text messages cap at 4096 chars; chunk below that with headroom.
CHUNK = 3800


class ChatAPI:
    def __init__(self, credentials_path: str | None = None):
        path = credentials_path or env.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not path or not os.path.exists(path):
            raise RuntimeError(
                "GOOGLE_APPLICATION_CREDENTIALS is not set or the key file does not "
                "exist. See docs/gchat-setup.md."
            )
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
        self._svc = build("chat", "v1", credentials=creds, cache_discovery=False)

    # ── posting ──────────────────────────────────────────────────────────────
    def post(self, space_name: str, thread_name: str | None, text: str) -> None:
        """Post text into a space, threaded when thread_name is given.

        Long text is split into <=CHUNK-char messages on paragraph boundaries.
        """
        for part in _chunks(text):
            body: dict = {"text": part}
            kwargs: dict = {"parent": space_name, "body": body}
            if thread_name:
                body["thread"] = {"name": thread_name}
                kwargs["messageReplyOption"] = "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
            self._svc.spaces().messages().create(**kwargs).execute()

    # ── attachments ──────────────────────────────────────────────────────────
    def download_attachment(self, attachment: dict) -> bytes:
        """Download an UPLOADED_CONTENT attachment via the Chat media API."""
        resource = attachment.get("attachmentDataRef", {}).get("resourceName")
        if not resource:
            raise RuntimeError("Attachment has no attachmentDataRef.resourceName")
        request = self._svc.media().download_media(resourceName=resource)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buf.getvalue()


def _chunks(text: str) -> list[str]:
    text = text.strip()
    if len(text) <= CHUNK:
        return [text] if text else []
    parts: list[str] = []
    remaining = text
    while len(remaining) > CHUNK:
        window = remaining[:CHUNK]
        cut = max(window.rfind("\n\n"), window.rfind("\n"), window.rfind(". "))
        if cut < CHUNK // 2:
            cut = CHUNK
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        parts.append(remaining)
    return parts
