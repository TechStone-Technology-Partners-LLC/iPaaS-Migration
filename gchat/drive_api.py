"""Google Drive delivery for analysis artifacts.

Chat apps cannot upload message attachments (user auth only), so artifacts
are delivered as Google Docs in a shared Drive folder: markdown is uploaded
with Docs conversion (reviewers edit/comment in place), and the Doc can be
re-exported as markdown so the agent picks up edits before continuing.
"""

import hashlib
import logging
import os
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import env

log = logging.getLogger("gchat.drive")

SCOPES = ["https://www.googleapis.com/auth/drive"]
DOC_MIME = "application/vnd.google-apps.document"


class DriveAPI:
    def __init__(self, credentials_path: str | None = None):
        path = credentials_path or env.get("GOOGLE_APPLICATION_CREDENTIALS")
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
        self._svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.folder_id = env.get("GCHAT_DRIVE_FOLDER_ID")

    @property
    def enabled(self) -> bool:
        return bool(self.folder_id)

    def create_folder(self, name: str, parent_id: str | None = None) -> dict:
        f = self._svc.files().create(
            body={"name": name, "mimeType": "application/vnd.google-apps.folder",
                  "parents": [parent_id or self.folder_id]},
            fields="id, webViewLink", supportsAllDrives=True,
        ).execute()
        return {"id": f["id"], "link": f.get("webViewLink", "")}

    def upload_markdown_as_doc(self, local_path: str, title: str,
                               existing_file_id: str | None = None,
                               parent_id: str | None = None) -> dict:
        """Upload/replace a markdown file as a Google Doc. Returns {id, link}."""
        media = MediaFileUpload(local_path, mimetype="text/markdown", resumable=False)
        if existing_file_id:
            f = self._svc.files().update(
                fileId=existing_file_id, media_body=media,
                fields="id, webViewLink", supportsAllDrives=True,
            ).execute()
        else:
            f = self._svc.files().create(
                body={"name": title, "mimeType": DOC_MIME, "parents": [parent_id or self.folder_id]},
                media_body=media, fields="id, webViewLink", supportsAllDrives=True,
            ).execute()
        return {"id": f["id"], "link": f.get("webViewLink", f"https://docs.google.com/document/d/{f['id']}")}

    def export_doc_markdown(self, file_id: str) -> str:
        data = self._svc.files().export(fileId=file_id, mimeType="text/markdown").execute()
        return data.decode("utf-8") if isinstance(data, bytes) else str(data)

    def export_fingerprint(self, file_id: str) -> str:
        """Hash of the Doc's current export — the baseline for edit detection."""
        return _fingerprint(self.export_doc_markdown(file_id))

    def sync_doc_to_local(self, file_id: str, local_path: str, baseline: str | None) -> tuple[bool, str]:
        """Pull reviewer edits to disk.

        Compares the Doc's export with the export taken at upload time
        (baseline fingerprint) — both come from Google's converter, so its
        cosmetic noise cancels out and only real user edits register.
        Returns (changed, new_fingerprint).
        """
        remote = self.export_doc_markdown(file_id)
        fp = _fingerprint(remote)
        if baseline and fp == baseline:
            return False, fp
        with open(local_path, "w", encoding="utf-8") as fh:
            fh.write(clean_export(remote))
        return True, fp


_ESCAPES = re.compile(r"\\([.=+_\-#*()\[\]!>|~`])")


def clean_export(md: str) -> str:
    """Undo Google's markdown export escapes and normalise table rules."""
    md = _ESCAPES.sub(r"\1", md)
    md = re.sub(r"^\|(\s*:?-+:?\s*\|)+\s*$",
                lambda m: re.sub(r":?-+:?", "---", m.group(0)), md, flags=re.M)
    return md


def _fingerprint(md: str) -> str:
    return hashlib.sha256(_norm(md).encode("utf-8")).hexdigest()


def _norm(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines())
