"""AgentSession — Claude Agent SDK wrapper for one migration conversation.

One session per Chat thread. Persistent streaming client; each user turn is
query() + receive_response(). Emits a small event stream the caller (bot or
CLI harness) renders: Text (post to chat), Tool (heartbeat material),
TurnDone (cost + session id for resume/budget).
"""

import asyncio
from dataclasses import dataclass, field

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

from .env import REPO_ROOT, get_float, get_int

DEFAULT_MAX_COST_USD = 5.00
DEFAULT_MAX_TURNS = 100
DEFAULT_TURN_TIMEOUT_S = 20 * 60


@dataclass
class Text:
    text: str


@dataclass
class Tool:
    name: str
    hint: str


@dataclass
class TurnDone:
    session_id: str
    cost_total: float
    cost_turn: float
    is_error: bool
    timed_out: bool = False


@dataclass
class Budget:
    max_cost_usd: float = field(default_factory=lambda: get_float("GCHAT_MAX_COST_USD", DEFAULT_MAX_COST_USD))
    max_turns: int = field(default_factory=lambda: get_int("GCHAT_MAX_TURNS", DEFAULT_MAX_TURNS))
    turn_timeout_s: int = field(default_factory=lambda: get_int("GCHAT_TURN_TIMEOUT_S", DEFAULT_TURN_TIMEOUT_S))
    spent_usd: float = 0.0
    turns: int = 0

    @property
    def exceeded(self) -> str | None:
        if self.spent_usd >= self.max_cost_usd:
            return f"cost limit reached (${self.spent_usd:.2f} of ${self.max_cost_usd:.2f})"
        if self.turns >= self.max_turns:
            return f"turn limit reached ({self.turns} of {self.max_turns})"
        return None

    def extend(self) -> None:
        """/continue: allow one more block of the same size."""
        self.max_cost_usd += get_float("GCHAT_MAX_COST_USD", DEFAULT_MAX_COST_USD)
        self.max_turns += get_int("GCHAT_MAX_TURNS", DEFAULT_MAX_TURNS)


def _tool_hint(block: ToolUseBlock) -> str:
    inp = block.input or {}
    for key in ("file_path", "path", "command", "pattern", "query"):
        if key in inp:
            val = str(inp[key])
            return val if len(val) <= 80 else val[:77] + "..."
    return ""


class AgentSession:
    def __init__(self, pkg_name: str, resume_session_id: str | None = None):
        self.pkg_name = pkg_name
        self.session_id: str | None = resume_session_id
        self.budget = Budget()
        self._client: ClaudeSDKClient | None = None

    async def connect(self) -> None:
        options = ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            permission_mode="bypassPermissions",
            setting_sources=["project"],  # load repo CLAUDE.md + skills
            max_turns=self.budget.max_turns,
            resume=self.session_id,
            # Workato AIRO recipe-builder MCP — auth comes from Claude Code's
            # shared OAuth store (verified working headless 2026-08-31)
            mcp_servers={
                "workato-airo-mcp-server": {
                    "type": "http",
                    "url": "https://app.workato.com/airo_mcp",
                }
            },
        )
        self._client = ClaudeSDKClient(options=options)
        await self._client.connect()

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None

    async def run_turn(self, prompt: str):
        """Send one user message; yield Text/Tool events, then a final TurnDone."""
        if not self._client:
            await self.connect()
        client = self._client
        assert client is not None

        cost_before = self.budget.spent_usd
        timed_out = False
        done: TurnDone | None = None

        await client.query(prompt)
        try:
            async with asyncio.timeout(self.budget.turn_timeout_s):
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock) and block.text.strip():
                                yield Text(block.text)
                            elif isinstance(block, ToolUseBlock):
                                yield Tool(block.name, _tool_hint(block))
                    elif isinstance(message, ResultMessage):
                        self.session_id = message.session_id
                        total = message.total_cost_usd or cost_before
                        self.budget.spent_usd = max(total, cost_before)
                        self.budget.turns += 1
                        done = TurnDone(
                            session_id=message.session_id,
                            cost_total=self.budget.spent_usd,
                            cost_turn=self.budget.spent_usd - cost_before,
                            is_error=bool(message.is_error),
                        )
        except TimeoutError:
            timed_out = True
            try:
                await client.interrupt()
            except Exception:
                pass

        if done is None:
            done = TurnDone(
                session_id=self.session_id or "",
                cost_total=self.budget.spent_usd,
                cost_turn=0.0,
                is_error=not timed_out,
                timed_out=timed_out,
            )
        yield done
