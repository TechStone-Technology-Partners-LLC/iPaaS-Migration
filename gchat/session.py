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

from .env import REPO_ROOT, get, get_float, get_int

DEFAULT_MAX_COST_USD = 5.00
DEFAULT_MAX_TURNS = 100
DEFAULT_TURN_TIMEOUT_S = 20 * 60
DEFAULT_MODEL = "claude-sonnet-5-5"
DEFAULT_EFFORT = "medium"  # low | medium | high | xhigh | max

# $ per 1M tokens: (input, output, cache_read, cache_write) — published API rates.
# One cache-write rate is used regardless of the TTL the engine picks.
PRICES: dict[str, tuple[float, float, float, float]] = {
    "claude-sonnet-5-5": (2.0, 10.0, 0.20, 2.50),
    "claude-sonnet-5":   (2.0, 10.0, 0.20, 2.50),
    "claude-opus-5-5":   (4.0, 20.0, 0.20, 5.00),
    "claude-opus-5":     (5.0, 25.0, 0.50, 6.25),
    "claude-fable-5-1":  (10.0, 50.0, 0.25, 12.50),
    "claude-fable-5":    (10.0, 50.0, 1.00, 12.50),
    "claude-haiku-4-5":  (1.0, 5.0, 0.10, 1.25),
}


@dataclass
class Tokens:
    uncached_in: int = 0
    cache_write: int = 0
    cache_read: int = 0
    out: int = 0

    def add(self, other: "Tokens") -> None:
        self.uncached_in += other.uncached_in
        self.cache_write += other.cache_write
        self.cache_read += other.cache_read
        self.out += other.out


def tokens_from_usage(usage: dict | None) -> Tokens:
    u = usage or {}
    return Tokens(
        uncached_in=int(u.get("input_tokens") or 0),
        cache_write=int(u.get("cache_creation_input_tokens") or 0),
        cache_read=int(u.get("cache_read_input_tokens") or 0),
        out=int(u.get("output_tokens") or 0),
    )


def cost_usd(model: str, t: Tokens) -> float | None:
    """Cost from the token breakdown at published rates; None if model unknown."""
    p = PRICES.get(model)
    if not p:
        return None
    inp, out, read, write = p
    return (t.uncached_in * inp + t.out * out + t.cache_read * read
            + t.cache_write * write) / 1_000_000


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
    tokens_turn: Tokens = field(default_factory=Tokens)
    tokens_total: Tokens = field(default_factory=Tokens)
    cost_source: str = "engine"  # "table" when computed from PRICES


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
        self.model = get("GCHAT_MODEL", DEFAULT_MODEL)
        self.tokens = Tokens()  # cumulative for this conversation
        self._engine_cost_seen = 0.0  # engine's cumulative figure (fallback pricing)
        self._client: ClaudeSDKClient | None = None

    async def connect(self) -> None:
        options = ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            model=self.model,
            effort=get("GCHAT_EFFORT", DEFAULT_EFFORT),
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
                        turn_tokens = tokens_from_usage(message.usage)
                        self.tokens.add(turn_tokens)
                        exact = cost_usd(self.model, turn_tokens)
                        if exact is not None:
                            cost_turn, source = exact, "table"
                        else:  # unknown model: fall back to the engine's cumulative estimate
                            engine_total = message.total_cost_usd or self._engine_cost_seen
                            cost_turn = max(engine_total - self._engine_cost_seen, 0.0)
                            self._engine_cost_seen = max(engine_total, self._engine_cost_seen)
                            source = "engine"
                        self.budget.spent_usd = cost_before + cost_turn
                        self.budget.turns += 1
                        done = TurnDone(
                            session_id=message.session_id,
                            cost_total=self.budget.spent_usd,
                            cost_turn=cost_turn,
                            is_error=bool(message.is_error),
                            tokens_turn=turn_tokens,
                            tokens_total=Tokens(**vars(self.tokens)),
                            cost_source=source,
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
