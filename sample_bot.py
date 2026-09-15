# minimal_bot.py — run: python3 minimal_bot.py
import asyncio, json, os
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from googleapiclient.discovery import build
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

PROJECT = os.environ["GCP_PROJECT_ID"]
SUB = os.environ.get("GCHAT_SUBSCRIPTION", "gchat-events-sub")
KEY = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

creds = service_account.Credentials.from_service_account_file(KEY, scopes=["https://www.googleapis.com/auth/chat.bot"])
chat = build("chat", "v1", credentials=creds, cache_discovery=False)
sessions: dict[str, ClaudeSDKClient] = {}
queue: asyncio.Queue = asyncio.Queue()

def post(space: str, text: str) -> None:
    chat.spaces().messages().create(parent=space, body={"text": text[:4000]}).execute()

def parse(event: dict):
    """Chat delivers the Workspace Add-ons shape: chat.messagePayload.{message,space}."""
    payload = event.get("chat", {}).get("messagePayload")
    if not payload:
        return None, None
    msg = payload["message"]
    if msg.get("sender", {}).get("type") == "BOT":
        return None, None
    return payload["space"]["name"], (msg.get("argumentText") or msg.get("text") or "").strip()

async def reply(space: str, text: str) -> None:
    client = sessions.get(space)
    if client is None:
        client = ClaudeSDKClient(options=ClaudeAgentOptions(
            cwd=os.getcwd(), permission_mode="bypassPermissions", setting_sources=["project"]))
        await client.connect()
        sessions[space] = client
    await client.query(text)
    final = []
    async for m in client.receive_response():
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock):
                    final.append(b.text)
                elif isinstance(b, ToolUseBlock):
                    final.clear()          # text before a tool call is narration, not the answer
    post(space, "\n\n".join(final) or "(no reply)")

async def main() -> None:
    loop = asyncio.get_running_loop()
    sub = pubsub_v1.SubscriberClient()
    def on_event(message):                 # Pub/Sub thread: ack fast, hand off
        message.ack()
        loop.call_soon_threadsafe(queue.put_nowait, json.loads(message.data))
    sub.subscribe(sub.subscription_path(PROJECT, SUB), callback=on_event)
    print("listening")
    while True:
        space, text = parse(await queue.get())
        if space and text:
            asyncio.create_task(reply(space, text))   # don't block the loop on a long turn

asyncio.run(main())