"""Local dry-run harness: the migration conversation over stdin/stdout.

Exercises intake + prompts + session exactly as the Chat bot does, with the
terminal standing in for Google Chat. Primary dev loop — run this before any
Google wiring.

Usage:
  python -m gchat.cli_harness --zip /path/to/package.zip
  python -m gchat.cli_harness --package GLDFundingEngine20080714   # already in WebMethods/
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from . import env, intake, prompts
from .session import AgentSession, Text, Tool, TurnDone

HEARTBEAT_S = 60


def _post(text: str) -> None:
    print(f"\n🤖 {text}\n{'-' * 60}")


async def _render_turn(session: AgentSession, prompt: str) -> TurnDone:
    last_beat = time.monotonic()
    last_tool = ""
    done: TurnDone | None = None
    async for event in session.run_turn(prompt):
        if isinstance(event, Text):
            _post(event.text)
        elif isinstance(event, Tool):
            last_tool = f"{event.name} {event.hint}".strip()
            if time.monotonic() - last_beat >= HEARTBEAT_S:
                print(f"   … still working — last tool: {last_tool}")
                last_beat = time.monotonic()
        elif isinstance(event, TurnDone):
            done = event
    assert done is not None
    print(f"   (turn: ${done.cost_turn:.2f} · total: ${done.cost_total:.2f} · session {done.session_id[:8]})")
    if done.timed_out:
        _post("⏱️ That step hit the turn time limit — send a message to continue.")
    return done


async def main() -> None:
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--zip", help="path to a webMethods package zip")
    group.add_argument("--package", help="package dir name already under WebMethods/")
    ap.add_argument("--resume", help="session id to resume", default=None)
    args = ap.parse_args()

    env.load_env()

    if args.zip:
        data = Path(args.zip).read_bytes()
        pkg, dest, reused = intake.extract_package(data, Path(args.zip).name)
        print(f"[intake] package={pkg} dir={dest} reused={reused}")
    else:
        pkg, reused = args.package, True
        if not (intake.WM_DIR / pkg).is_dir():
            sys.exit(f"WebMethods/{pkg}/ not found")

    session = AgentSession(pkg, resume_session_id=args.resume)
    await session.connect()
    try:
        turn_prompt = prompts.kickoff(pkg, reused) if not args.resume else prompts.reanchor(
            pkg, "analysis", "Resume where you left off — re-read the analysis files on disk if needed."
        )
        while True:
            done = await _render_turn(session, turn_prompt)
            breach = session.budget.exceeded
            if breach:
                _post(f"💰 Budget limit: {breach}. Type /continue to extend, /abort to stop.")
            try:
                reply = input("👤 you> ").strip()
            except EOFError:
                break
            if reply in ("/abort", "/quit", "exit"):
                break
            if reply == "/continue":
                session.budget.extend()
                reply = "Continue."
            if not reply:
                continue
            turn_prompt = prompts.reanchor(pkg, "analysis", reply)
    finally:
        await session.disconnect()
        print(f"[session] id={session.session_id} spent=${session.budget.spent_usd:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
