"""Google Chat REST client: post threaded messages, download attachments.

Auth: the app's own service account with scope chat.bot — the app can only act
in spaces it has been added to. No domain-wide delegation.
"""

import io
import logging
import os
import socket
import ssl

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from . import env

log = logging.getLogger("gchat.chat_api")

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
        self._creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
        self._svc = self._build()

    def _build(self):
        return build("chat", "v1", credentials=self._creds, cache_discovery=False)

    def _execute(self, make_request):
        """Run make_request(service).execute() with reconnect-and-retry.

        The discovery client keeps a persistent HTTPS socket; after idle
        periods the far end drops it and the next write raises SSLEOFError /
        ConnectionError. Rebuild the client once and retry.
        """
        try:
            return make_request(self._svc).execute(num_retries=2)
        except (ssl.SSLError, ConnectionError, socket.error, OSError) as exc:
            log.warning("chat api transport error (%s) — rebuilding client and retrying", exc)
            self._svc = self._build()
            return make_request(self._svc).execute(num_retries=2)

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
            self._execute(lambda svc: svc.spaces().messages().create(**kwargs))

    # ── attachments ──────────────────────────────────────────────────────────
    def download_attachment(self, attachment: dict) -> bytes:
        """Download an UPLOADED_CONTENT attachment via the Chat media API."""
        resource = attachment.get("attachmentDataRef", {}).get("resourceName")
        if not resource:
            raise RuntimeError("Attachment has no attachmentDataRef.resourceName")
        def _download(svc):
            request = svc.media().download_media(resourceName=resource)
            buf = io.BytesIO()
            downloader = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = downloader.next_chunk(num_retries=2)
            return buf.getvalue()

        try:
            return _download(self._svc)
        except (ssl.SSLError, ConnectionError, socket.error, OSError) as exc:
            log.warning("chat media transport error (%s) — rebuilding client and retrying", exc)
            self._svc = self._build()
            return _download(self._svc)


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
