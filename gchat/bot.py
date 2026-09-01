"""MigrAIte Google Chat bot — Pub/Sub pull loop + thread routing.

Run:  python -m gchat.bot

Google never calls this machine: events arrive by pulling the subscription,
replies go out as HTTPS calls to the Chat API. One active migration globally
(demo constraint); each Chat thread maps to one AgentSession.
"""

import asyncio
import json
import logging
import time
from collections import OrderedDict
from pathlib import Path

from google.cloud import pubsub_v1

from . import env, intake, prompts
from .chat_api import ChatAPI
from .session import AgentSession, Text, Tool, TurnDone

log = logging.getLogger("gchat")

STATE_PATH = Path(__file__).parent / "state.json"
HEARTBEAT_S = 60

# thread states
IDLE, AGENT_RUNNING, WAITING_FOR_USER, BUDGET_PAUSED, DONE = (
    "IDLE", "AGENT_RUNNING", "WAITING_FOR_USER", "BUDGET_PAUSED", "DONE",
)


class Thread:
    """One conversation: a thread in a space, or a whole DM (reply_thread None)."""

    def __init__(self, space: str, name: str, reply_thread: str | None = None):
        self.space = space
        self.name = name              # routing key: thread name, or space name for DMs
        self.reply_thread = reply_thread  # thread to post into; None = flat (DM)
        self.state = IDLE
        self.pkg: str | None = None
        self.session: AgentSession | None = None
        self.buffered: str | None = None  # latest mid-turn user message
        self.task: asyncio.Task | None = None  # in-flight agent turn


class Bot:
    def __init__(self) -> None:
        self.chat = ChatAPI()
        self.threads: dict[str, Thread] = {}
        self.active_thread: str | None = None  # one migration at a time
        self.seen: OrderedDict[str, None] = OrderedDict()  # message.name dedupe
        self.queue: asyncio.Queue = asyncio.Queue()
        self.loop: asyncio.AbstractEventLoop | None = None
        self._state = self._load_state()

    # ── persisted state (thread → session id) for restart resume ────────────
    def _load_state(self) -> dict:
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return {}

    def _save_state(self) -> None:
        data = {
            t.name: {"session_id": t.session.session_id if t.session else None,
                     "pkg": t.pkg, "state": t.state, "space": t.space}
            for t in self.threads.values()
        }
        STATE_PATH.write_text(json.dumps(data, indent=2))

    # ── pub/sub plumbing ─────────────────────────────────────────────────────
    def _callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        """Runs on a Pub/Sub gRPC thread: ack immediately, hand off to asyncio."""
        try:
            event = json.loads(message.data.decode("utf-8"))
        except Exception:
            message.ack()
            return
        message.ack()
        if self.loop:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, event)

    async def run(self) -> None:
        self.loop = asyncio.get_running_loop()
        project = env.get("GCP_PROJECT_ID")
        sub_name = env.get("GCHAT_SUBSCRIPTION", "gchat-events-sub")
        if not project:
            raise SystemExit("GCP_PROJECT_ID not set — see docs/gchat-setup.md")
        subscriber = pubsub_v1.SubscriberClient()
        sub_path = subscriber.subscription_path(project, sub_name)
        streaming = subscriber.subscribe(sub_path, callback=self._callback)
        log.info("listening on %s", sub_path)
        try:
            while True:
                event = await self.queue.get()
                try:
                    await self._handle(event)
                except Exception:
                    log.exception("error handling event")
        finally:
            streaming.cancel()

    # ── event handling ───────────────────────────────────────────────────────
    @staticmethod
    def _parse_event(event: dict) -> dict | None:
        """Normalize both Chat event formats to {msg, space, sender}.

        New (Workspace Add-ons infra): {"chat": {"user":…, "messagePayload":
        {"message":…, "space":…}}}. Classic: {"type":"MESSAGE", "message":…,
        "space":…}.
        """
        if "chat" in event:
            payload = event["chat"].get("messagePayload")
            if not payload:
                return None  # added-to-space, app command, etc.
            msg = payload.get("message", {})
            space_obj = payload.get("space") or msg.get("space") or {}
        elif event.get("type") == "MESSAGE":
            msg = event.get("message", {})
            space_obj = event.get("space") or msg.get("space") or {}
        else:
            return None
        return {
            "msg": msg,
            "space": space_obj.get("name", ""),
            "sender": msg.get("sender") or event.get("chat", {}).get("user", {}) or event.get("user", {}),
            "is_dm": space_obj.get("spaceType") == "DIRECT_MESSAGE" or space_obj.get("type") == "DM",
        }

    async def _handle(self, event: dict) -> None:
        parsed = self._parse_event(event)
        if parsed is None:
            log.info("ignoring non-message event (keys=%s)", list(event.keys()))
            return
        msg = parsed["msg"]
        name = msg.get("name", "")
        log.info("message space=%s sender=%s text=%r attachments=%d",
                 parsed["space"], parsed["sender"].get("email"),
                 (msg.get("text") or "")[:60],
                 len(msg.get("attachment") or msg.get("attachments") or []))
        if not name or name in self.seen:
            return  # Pub/Sub redelivery duplicate
        self.seen[name] = None
        while len(self.seen) > 500:
            self.seen.popitem(last=False)

        sender = parsed["sender"]
        if sender.get("type") == "BOT":
            return
        allow = env.allowed_users()
        sender_email = (sender.get("email") or "").lower()
        if allow and sender_email not in allow:
            return

        space = parsed["space"]
        # DMs are one flat conversation (route by space, post unthreaded);
        # spaces keep thread-per-migration.
        if parsed["is_dm"]:
            thread_name = space
            reply_thread = None
        else:
            thread_name = msg.get("thread", {}).get("name", "")
            reply_thread = thread_name
        text = (msg.get("argumentText") or msg.get("text") or "").strip()
        # in the add-ons format argumentText still includes the @mention — strip it
        if text.lower().startswith("@migraite"):
            text = text.split(None, 1)[1].strip() if len(text.split(None, 1)) > 1 else ""
        attachments = msg.get("attachment") or msg.get("attachments") or []

        thread = self.threads.get(thread_name)
        if thread is None:
            thread = Thread(space, thread_name, reply_thread)
            saved = self._state.get(thread_name)
            if saved and saved.get("session_id") and saved.get("state") not in (DONE, None):
                # bot restarted mid-migration: resume the session on next reply
                thread.pkg = saved.get("pkg")
                thread.session = AgentSession(thread.pkg or "", resume_session_id=saved["session_id"])
                thread.state = WAITING_FOR_USER
                self.active_thread = thread_name
            self.threads[thread_name] = thread

        if text.lower() in ("/new", "/reset"):
            if thread.task:
                thread.task.cancel()
            if thread.session:
                await thread.session.disconnect()
            fresh = Thread(space, thread_name, reply_thread)
            self.threads[thread_name] = fresh
            if self.active_thread == thread_name:
                self.active_thread = None
            self._save_state()
            self.chat.post(space, reply_thread,
                           "🔄 Conversation reset — upload a webMethods package zip to start a new migration.")
            return

        zips = [a for a in attachments if (a.get("contentName") or "").lower().endswith(".zip")]
        if zips and thread.state == IDLE:
            await self._start_migration(thread, zips[0], text)
        elif thread.state == WAITING_FOR_USER:
            await self._user_reply(thread, text)
        elif thread.state == BUDGET_PAUSED:
            await self._budget_reply(thread, text)
        elif thread.state == AGENT_RUNNING:
            if text.lower() == "/abort":
                if thread.task:
                    thread.task.cancel()
                await self._finish(thread, aborted=True)
            else:
                thread.buffered = text or thread.buffered
                self.chat.post(space, reply_thread,
                               "⏳ Still working on the previous step — I'll use your message as soon as I'm ready.")
        elif thread.state == IDLE:
            self.chat.post(space, reply_thread,
                           "👋 I'm MigrAIte. Upload a webMethods package zip in this thread to start a migration analysis.")
        elif thread.state == DONE:
            self.chat.post(space, reply_thread,
                           "✅ This migration analysis is complete. Start a new thread with a new zip to run another.")

    async def _start_migration(self, thread: Thread, attachment: dict, user_text: str = "") -> None:
        if self.active_thread and self.active_thread != thread.name:
            self.chat.post(thread.space, thread.reply_thread,
                           "🚧 A migration is already running in another thread — please try again when it finishes.")
            return
        try:
            data = self.chat.download_attachment(attachment)
            pkg, dest, reused = intake.extract_package(data, attachment.get("contentName", "package.zip"))
        except intake.IntakeError as exc:
            self.chat.post(thread.space, thread.reply_thread, f"⚠️ {exc}")
            return
        thread.pkg = pkg
        thread.session = AgentSession(pkg)
        self.active_thread = thread.name
        self.chat.post(thread.space, thread.reply_thread,
                       f"📦 Received *{pkg}*. Starting analysis — I'll post progress here and ask when I need input.")
        self._spawn_turn(thread, prompts.kickoff(pkg, reused, user_text))

    async def _user_reply(self, thread: Thread, text: str) -> None:
        if not text:
            return
        if text.lower() == "/abort":
            await self._finish(thread, aborted=True)
            return
        assert thread.pkg is not None
        self._spawn_turn(thread, prompts.reanchor(thread.pkg, "analysis", text))

    async def _budget_reply(self, thread: Thread, text: str) -> None:
        cmd = text.lower()
        if cmd == "/continue" and thread.session:
            thread.session.budget.extend()
            self.chat.post(thread.space, thread.reply_thread, "💰 Budget extended — continuing.")
            thread.state = WAITING_FOR_USER
            await self._user_reply(thread, "Continue where you left off.")
        elif cmd == "/abort":
            await self._finish(thread, aborted=True)
        else:
            self.chat.post(thread.space, thread.reply_thread,
                           "Budget limit is active — reply /continue to extend or /abort to stop.")

    def _spawn_turn(self, thread: Thread, prompt: str) -> None:
        """Run the agent turn as a background task so the event loop keeps
        consuming Pub/Sub events (mid-turn messages get the 'still working'
        ack instead of silently queueing behind a 10-minute turn)."""
        async def _run() -> None:
            try:
                await self._run_turn(thread, prompt)
            except Exception:
                log.exception("agent turn failed")
                thread.state = WAITING_FOR_USER
                self.chat.post(thread.space, thread.reply_thread,
                               "⚠️ Something went wrong during that step — send a message to retry.")
        thread.task = asyncio.create_task(_run())

    async def _run_turn(self, thread: Thread, prompt: str) -> None:
        assert thread.session is not None
        thread.state = AGENT_RUNNING
        last_beat = time.monotonic()
        last_tool = ""
        done: TurnDone | None = None
        async for event in thread.session.run_turn(prompt):
            if isinstance(event, Text):
                self.chat.post(thread.space, thread.reply_thread, event.text)
            elif isinstance(event, Tool):
                last_tool = f"{event.name} {event.hint}".strip()
                if time.monotonic() - last_beat >= HEARTBEAT_S:
                    self.chat.post(thread.space, thread.reply_thread,
                                   f"⏳ Still working — last step: {last_tool}")
                    last_beat = time.monotonic()
            elif isinstance(event, TurnDone):
                done = event
        assert done is not None
        self._save_state()

        footer = f"(turn: ${done.cost_turn:.2f} · total: ${done.cost_total:.2f})"
        if done.timed_out:
            self.chat.post(thread.space, thread.reply_thread,
                           f"⏱️ That step hit the time limit. Send a message to continue. {footer}")
        else:
            self.chat.post(thread.space, thread.reply_thread, footer)

        breach = thread.session.budget.exceeded
        if breach:
            thread.state = BUDGET_PAUSED
            self.chat.post(thread.space, thread.reply_thread,
                           f"💰 Budget limit: {breach}. Reply /continue to extend or /abort to stop.")
            return

        thread.state = WAITING_FOR_USER
        if thread.buffered:
            buffered, thread.buffered = thread.buffered, None
            await self._user_reply(thread, buffered)

    async def _finish(self, thread: Thread, aborted: bool = False) -> None:
        if thread.session:
            await thread.session.disconnect()
        thread.state = DONE
        if self.active_thread == thread.name:
            self.active_thread = None
        self._save_state()
        if aborted:
            self.chat.post(thread.space, thread.reply_thread, "🛑 Migration aborted.")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    env.load_env()
    asyncio.run(Bot().run())


if __name__ == "__main__":
    main()
