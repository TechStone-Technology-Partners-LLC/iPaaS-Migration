"""Decide what to do with one Pub/Sub push of a Chat event.

Kept free of Azure/Google SDK imports so it can be tested anywhere; the
VM and Chat calls are passed in. See docs/how-migraite-bot-works/migraite-wake-on-message.md §2.

Return value is the HTTP status for Pub/Sub: 2xx = delivered (done),
503 = retry later (Pub/Sub backs off 10 s -> 600 s).
"""

import base64
import json
import logging

log = logging.getLogger("migraite-wake")

OK, RETRY = 200, 503

NOTICE = ("⏰ MigrAIte was asleep — starting up now (about 2 minutes). "
          "Your message is queued and will be answered.")


def chat_event(body: bytes) -> dict | None:
    """Pub/Sub push body {"message": {"data": base64(event)}} -> Chat event."""
    try:
        data = json.loads(body)["message"]["data"]
        return json.loads(base64.b64decode(data))
    except Exception:
        return None


def classify(event: dict | None, allowed: list[str]) -> tuple[bool, tuple[str, str | None] | None]:
    """(wake?, where to post the notice). Mirrors gchat.bot._parse_event.

    Unknown payloads wake the VM (fail open): the bot decides what to ignore.
    Known non-message events, bot senders and non-allowlisted users don't.
    """
    if event is None:
        return True, None
    if "chat" in event:
        payload = event["chat"].get("messagePayload")
        if not payload:
            return False, None  # added-to-space, app command, ...
        msg = payload.get("message", {})
        space = payload.get("space") or msg.get("space") or {}
        sender = msg.get("sender") or event["chat"].get("user", {})
    elif event.get("type") == "MESSAGE":
        msg = event.get("message", {})
        space = event.get("space") or msg.get("space") or {}
        sender = msg.get("sender") or event.get("user", {})
    elif "type" in event:
        return False, None  # classic non-message event
    else:
        return True, None
    if sender.get("type") == "BOT":
        return False, None
    if allowed and (sender.get("email") or "").lower() not in allowed:
        return False, None
    is_dm = space.get("spaceType") == "DIRECT_MESSAGE" or space.get("type") == "DM"
    thread = None if is_dm else (msg.get("thread") or {}).get("name")
    target = (space["name"], thread) if space.get("name") else None
    return True, target


def handle(body: bytes, vm, notify, allowed: list[str]) -> int:
    """vm: .power_state() -> str, .start(); notify(space, thread, text) or None."""
    wake, target = classify(chat_event(body), allowed)
    if not wake:
        return OK
    try:
        state = vm.power_state()
    except Exception:
        log.exception("power state lookup failed")
        return RETRY
    if state in ("running", "starting"):
        return OK
    if state in ("deallocating", "stopping"):
        return RETRY  # can't start mid-shutdown; Pub/Sub will redeliver
    try:
        vm.start()
    except Exception:
        log.exception("start failed (state was %s)", state)
        return RETRY
    log.info("VM was %s — start requested", state)
    if notify and target:
        try:
            notify(target[0], target[1], NOTICE)
        except Exception:
            log.exception("wake notice failed (VM still starting)")
    return OK
