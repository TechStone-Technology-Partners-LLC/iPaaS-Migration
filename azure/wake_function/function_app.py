"""MigrAIte wake function (Azure Functions, Python v2 model).

Pub/Sub push subscription `gchat-wake-sub` POSTs every Chat event to
/api/wake?code=<function key>. If the bot's VM is off, start it and post a
"waking up" notice in the thread. The bot itself reads the message from its
own pull subscription once the VM is up.

App settings:
  AZ_SUBSCRIPTION_ID, AZ_RESOURCE_GROUP, AZ_VM_NAME   which VM to start
  GCHAT_SA_JSON        optional: Chat service account key (JSON) for the notice
  GCHAT_ALLOWED_USERS  optional: same allowlist as the bot

The app's system-assigned identity needs Virtual Machine Contributor on the VM.
"""

import json
import os

import azure.functions as func
import requests

import wake_logic

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

ARM = "https://management.azure.com"
API_VERSION = "2024-07-01"
CHAT_SCOPES = ["https://www.googleapis.com/auth/chat.bot"]


class AzureVM:
    def __init__(self) -> None:
        self.base = (f"{ARM}/subscriptions/{os.environ['AZ_SUBSCRIPTION_ID']}"
                     f"/resourceGroups/{os.environ['AZ_RESOURCE_GROUP']}"
                     f"/providers/Microsoft.Compute/virtualMachines/{os.environ['AZ_VM_NAME']}")
        self.headers = {"Authorization": f"Bearer {_arm_token()}"}

    def power_state(self) -> str:
        r = requests.get(f"{self.base}/instanceView", params={"api-version": API_VERSION},
                         headers=self.headers, timeout=10)
        r.raise_for_status()
        codes = [s["code"] for s in r.json().get("statuses", [])]
        return next((c.split("/", 1)[1] for c in codes if c.startswith("PowerState/")), "unknown")

    def start(self) -> None:
        r = requests.post(f"{self.base}/start", params={"api-version": API_VERSION},
                          headers=self.headers, timeout=15)
        if r.status_code not in (200, 202):
            raise RuntimeError(f"start refused: HTTP {r.status_code} {r.text[:300]}")


def _arm_token() -> str:
    """Managed identity token from the Functions host's identity endpoint."""
    r = requests.get(os.environ["IDENTITY_ENDPOINT"],
                     params={"resource": f"{ARM}/", "api-version": "2019-08-01"},
                     headers={"X-IDENTITY-HEADER": os.environ["IDENTITY_HEADER"]}, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def _chat_notifier():
    raw = os.environ.get("GCHAT_SA_JSON")
    if not raw:
        return None
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account
    session = AuthorizedSession(service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=CHAT_SCOPES))

    def notify(space: str, thread: str | None, text: str) -> None:
        body: dict = {"text": text}
        params = {}
        if thread:
            body["thread"] = {"name": thread}
            params["messageReplyOption"] = "REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
        r = session.post(f"https://chat.googleapis.com/v1/{space}/messages",
                         params=params, json=body, timeout=10)
        r.raise_for_status()
    return notify


def _allowed() -> list[str]:
    raw = os.environ.get("GCHAT_ALLOWED_USERS", "")
    return [u.strip().lower() for u in raw.split(",") if u.strip()]


@app.route(route="wake", methods=["POST"])
def wake(req: func.HttpRequest) -> func.HttpResponse:
    try:
        vm = AzureVM()
    except Exception:
        wake_logic.log.exception("identity/config error")
        return func.HttpResponse(status_code=wake_logic.RETRY)
    status = wake_logic.handle(req.get_body(), vm, _chat_notifier(), _allowed())
    return func.HttpResponse(status_code=status)
