# Setting Up a Google Chat Bot Backed by an Agent (internal)

Step by step: provision the Google side (project, service account, IAM,
Pub/Sub, Chat app), connect it to a backend service, and drive a Claude
Agent SDK session from it. Part A is generic — it ends with a minimal bot
that simply chats with Claude, and the same skeleton can front any harness
or LLM call. Part B adds what MigrAIte specifically needs (Drive delivery,
the Workato AIRO login, its environment variables).

Related: [how the MigrAIte bot works](migraite-gchat-bot.md) · [workflow](migraite-workflow.md) · [client onboarding](migraite-client-onboarding.md)

---

# Part A — Google Chat → your service → Claude

## A0. Prerequisites

- A **Google Workspace** organization. Chat apps cannot be created from
  consumer Gmail accounts. Making the app visible to a named list of users
  needs no admin; publishing domain-wide does.
- A machine to run the service (laptop is fine to start) with Python 3.10+.
- Claude access: for a **deployed service**, an **Anthropic API key**; for
  **local runs** on your own machine, just the `claude` CLI logged in to
  your Claude account (see A5).

> **Do the steps in order.** A2 (service account) must exist before A3
> (Pub/Sub permissions), and A4.8 (topic Publisher) can only be done after
> the Chat app is configured. Where the console's button labels vary by
> version, both names are given.

## A1. Google Cloud project

1. Open console.cloud.google.com, signed in with your Workspace account.
2. In the **top-left**, next to the Google Cloud logo, there is a project
   selector (it shows the current project name, or "Select a project").
   Click it → a dialog opens → click **NEW PROJECT** (top right of the
   dialog).
3. Name it whatever you like (e.g. `ipaas-migraite-demo`). Leave
   Organization/Location as the Workspace organization it defaults to.
   Click **CREATE**.
4. **Check that the console switched to the new project**: the top-left
   selector should now show your new project's name. If it still shows the
   old one, click the selector again and pick the new project from the list.
5. Open **APIs & Services** from the left navigation menu. If you don't see
   the menu, click the **three horizontal lines** (☰) in the top-left to
   open it — or type "APIs & Services" in the search bar at the top.
6. **APIs & Services → Library**: search for and **Enable** each of:
   - **Google Chat API** — pick the one literally named "Google Chat API"
     (not anything with "MCP" in the name).
   - **Cloud Pub/Sub API**.
   - (MigrAIte only) **Google Drive API** — see Part B.

## A2. Service account and key

The service authenticates to Google as a service account. Create this
*before* Pub/Sub, because the Pub/Sub permissions in A3 refer to it.

1. Left menu → **IAM & Admin → Service Accounts** → **+ CREATE SERVICE
   ACCOUNT**.
2. Service account name: `gchat-migration-bot`. The ID auto-fills. Click
   **CREATE AND CONTINUE**.
3. The next two panels — *Grant this service account access to project*
   (permissions/roles) and *Grant users access to this service account*
   (principals with access) — can both be **skipped**: click **CONTINUE**,
   then **DONE**. No project-level roles are needed; access is granted on
   the specific Pub/Sub resources in A3.
4. Back in the list, click the new account → **KEYS** tab → **ADD KEY →
   Create new key → JSON → CREATE**. A file downloads. Move it outside any
   repository (e.g. `~/keys/gchat-bot.json`) and `chmod 600` it.
5. Note the account's email — `gchat-migration-bot@<project>.iam.gserviceaccount.com`
   — you'll paste it in A3 and B2.

## A3. Pub/Sub topic and subscription

How to get there: left menu → **Pub/Sub** (under "Analytics"; if it's not
pinned, use the top search bar and type "Pub/Sub") → **Topics**.

1. Click **+ CREATE TOPIC**. Topic ID: `gchat-events`.
2. In the create form, tick only **Add a default subscription** and leave
   everything else at its default: don't add a schema, don't enable
   ingestion, don't add a transform, keep encryption as *Google-managed*,
   no tags, default retention. Click **CREATE**.
   The default subscription is created for you, named `gchat-events-sub`,
   delivery type Pull — exactly what the service needs. (If you did *not*
   tick the box, create it now: inside the topic → *Create subscription* →
   ID `gchat-events-sub`, delivery type **Pull**, defaults, Create.)
3. Give the service account the right to pull: **Pub/Sub → Subscriptions →
   gchat-events-sub** → **PERMISSIONS** tab (in some console versions this
   is a side panel — tick the subscription's checkbox and the panel opens
   on the right) → **ADD PRINCIPAL** (older label: *Grant access*).
   - *New principals*: paste the service account email from A2.5 in full —
     `gchat-migration-bot@<project>.iam.gserviceaccount.com`. It may not
     autocomplete; pasting the full address works.
   - *Role*: search **Pub/Sub Subscriber** → select → **SAVE**.
4. The **topic** also needs a Publisher — but the principal that publishes
   is Google's own, and its address is only revealed on the Chat app
   configuration page. Come back for it in A4.7–A4.8.

## A4. Chat app

How to get there: left menu → **APIs & Services → Enabled APIs & services**
→ click **Google Chat API** in the list → **CONFIGURATION** tab (next to
Metrics/Quotas/Credentials).

Fill the page top to bottom and **save before** trying to grant the topic
Publisher — the principal you need only appears after the first save.

1. **App name** (e.g. `migrAIte`), **avatar URL**, **description**.
2. **Interactive features: ON**. Tick *Receive 1:1 messages* and *Join
   spaces and group conversations*.
3. **Connection settings → Cloud Pub/Sub** → topic name
   `projects/<project>/topics/gchat-events`. Nothing else appears here yet;
   that is expected.
4. **Visibility** → tick *Make this Chat app available to specific people
   and groups in <domain>* → add yourself and anyone else who should be
   able to use the app (emails or groups). Domain-wide availability instead
   needs a Workspace admin.
5. **Log errors to Cloud Logging: ON**. It is the only visibility into
   delivery failures.
6. **SAVE**.
7. Now look under **Connection settings** again: a **Service account email**
   has appeared — format
   `service-<PROJECT_NUMBER>@gcp-sa-gsuiteaddons.iam.gserviceaccount.com`.
   This is Google's per-app service agent, the principal that publishes
   Chat events to your topic. Copy it.
   (If it does not appear, construct it: the project number — a 10–12 digit
   number, not the project ID — is on **Cloud overview → Dashboard → Project
   info**; e.g. project number `2985430398` →
   `service-2985430398@gcp-sa-gsuiteaddons.iam.gserviceaccount.com`.)
8. Grant it Publisher: **Pub/Sub → Topics → gchat-events → PERMISSIONS →
   ADD PRINCIPAL** (older label: *Grant access*) → paste the address → role
   **Pub/Sub Publisher** → SAVE.
   > Not `chat-api-push@system.gserviceaccount.com` — that is the legacy
   > principal from older docs. With it, every publish fails with
   > `PERMISSION_DENIED` and the app looks dead.
9. In Google Chat: **New chat → search the app name → open a DM with it**,
   or create a space and add the app. The app can only act in spaces it
   belongs to.

## A5. Install the SDK

```bash
pip3 install claude-agent-sdk google-cloud-pubsub google-api-python-client google-auth
```

`claude-agent-sdk` bundles the Claude Code engine — no separate install.

Claude authentication depends on where this runs:

- **Local run / development on your own machine**: no API key needed.
  Open a terminal and run:

  ```bash
  claude
  ```

  Inside the Claude session that opens, type `/login` and complete the
  browser sign-in with your Claude account, then `/exit`. The engine reuses
  that login for every session on this machine (it lives in `~/.claude`).
- **Deployed service**: set `ANTHROPIC_API_KEY` in the service's
  environment so usage bills to the service, not to a person, and nothing
  depends on an interactive login on the server.

## A6. Minimal bot: relay Chat ↔ a Claude session

This is the whole idea in ~60 lines: pull events, keep one Claude session
per space, post the reply. Everything else in MigrAIte is elaboration of this
loop.

```python
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
```

The script reads three values from the environment. Set them in the same
terminal before running it (the minimal bot does not read a `.env` file;
MigrAIte's own bot does — see B5):

```bash
export GCP_PROJECT_ID=<your project id>            # the ID (see below), e.g. ipaas-migraite-demo
export GCHAT_SUBSCRIPTION=gchat-events-sub
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keys/gchat-bot.json
python3 minimal_bot.py
```

Where to get the **project ID**: click the project selector in the
top-left of the Cloud console — the dialog lists every project with two
columns, **Name** and **ID**; use the **ID** column (lowercase, hyphenated,
e.g. `ipaas-migraite-demo`). It is also on **Cloud overview → Dashboard →
Project info** as "Project ID". Do not confuse it with the *project number*
(all digits) — that one is only used to build the service-agent address in
A4.7.

Send `hello` to the app in Chat, and a Claude reply comes back. Points that
matter in this skeleton:

- **Ack first, process later.** A turn can take minutes; an un-acked message
  is redelivered.
- **One session per conversation**, kept alive — context without replaying
  history.
- **Run turns as tasks**, so the loop keeps receiving events during a long
  turn (that is what lets you acknowledge "still working").
- **Only the final text** after the last tool call is the reply; everything
  before it is the agent thinking out loud.
- **Exactly one instance** of this process per subscription.

To front something other than Claude, replace the body of `reply()` — a
different harness, a REST call, a pipeline — the Google side is unchanged.

## A7. Verify

- `hi` in the DM → reply within seconds. If the "app isn't responding"
  banner appears and nothing follows, check Cloud Logging → filter
  `resource.type="chat.googleapis.com/App"` — a `PERMISSION_DENIED` on
  publish means A4.8.
- `gcloud pubsub topics get-iam-policy gchat-events` (Cloud Shell) should
  list the `service-…@gcp-sa-gsuiteaddons` principal with
  `roles/pubsub.publisher`.

---

# Part B — MigrAIte specifics

## B1. Repository and dependencies

```bash
git clone <repo> && cd iPaaS-Migration
pip3 install -r requirements.txt
```

## B2. Google Drive for analysis delivery

Chat apps cannot attach files to messages, and service accounts have no My
Drive storage quota, so analyses are delivered as Google Docs in a **Shared
Drive**.

1. Enable **Google Drive API** on the project.
2. Google Drive → **Shared drives → New** → `MigrAIte`.
3. **Manage members** → add
   `gchat-migration-bot@<project>.iam.gserviceaccount.com` as **Content
   manager**.
4. Copy the drive id from its URL (`…/drive/folders/0A…`). Per-run
   subfolders are created inside it.

## B3. Claude identity

- **Local run**: use the `claude` login from A5 (run `claude` in a
  terminal → `/login`); nothing to set in `.env`.
- **Deployed service**: set `ANTHROPIC_API_KEY` in `.env`. Without it,
  sessions use whatever Claude login is stored in the config directory they
  run with — on a developer machine that is the developer's own, which is
  fine for demos and wrong for a service.

## B4. Workato AIRO login

AIRO (`https://app.workato.com/airo_mcp`) accepts only OAuth tokens from an
interactive login by a real Workato user; REST API tokens and
client-credentials grants are refused. The token is stored by Claude Code in
the **Claude config directory** and reused by headless sessions.

Service default login (used when no client-specific directory applies):

```bash
claude mcp add --transport http workato-airo-mcp-server https://app.workato.com/airo_mcp
claude          # inside: /mcp → authenticate workato-airo-mcp-server in the browser → /exit
```

Log in as the Workato user whose workspace recipes should land in. Verify
headlessly:

```bash
python3 - <<'EOF'
import asyncio, os
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
async def main():
    opts = ClaudeAgentOptions(cwd=os.getcwd(), permission_mode="bypassPermissions", setting_sources=["project"],
        mcp_servers={"workato-airo-mcp-server": {"type": "http", "url": "https://app.workato.com/airo_mcp"}}, max_turns=4)
    async with ClaudeSDKClient(options=opts) as c:
        await c.query("Call the AIRO tool folder_list and reply with only the first folder name, or AIRO-UNAVAILABLE.")
        async for m in c.receive_response():
            if isinstance(m, AssistantMessage):
                for b in m.content:
                    if isinstance(b, TextBlock): print(b.text)
asyncio.run(main())
EOF
```

Per-client logins go into per-client config directories — see
[client onboarding](migraite-client-onboarding.md).

## B5. Environment file

`.env` at the repository root (never committed):

```
ANTHROPIC_API_KEY=sk-ant-…            # deployed service only; omit for local runs (uses the claude login)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gchat-bot.json
GCP_PROJECT_ID=ipaas-migraite-demo
GCHAT_SUBSCRIPTION=gchat-events-sub
GCHAT_ALLOWED_USERS=                 # optional comma-separated sender emails; empty = anyone in the space
GCHAT_DRIVE_FOLDER_ID=0A…            # Shared Drive id; unset = no Doc delivery
GCHAT_WORKATO_FOLDER_ID=33882168     # suggested default folder in the folder question
GCHAT_MAX_COST_USD=20.00             # per conversation; analysis ≈ $5, analysis+build ≈ $10–20
GCHAT_MAX_TURNS=100
GCHAT_TURN_TIMEOUT_S=3600            # builds take 20–30 min
GCHAT_HEARTBEAT_S=180                # "still working" cadence
GCHAT_MODEL=claude-sonnet-5-5        # engine model for bot sessions (default)
GCHAT_EFFORT=medium                  # low | medium | high | xhigh | max (default medium)
```

## B6. Run and operate

```bash
python3 -m gchat.bot                 # from the repository root; exactly one instance
```

Startup logs `Drive delivery enabled (folder …)` and `listening on …`.
Smoke test with `hi`; then upload a package zip. Restart with
`pkill -f gchat.bot` and start again — conversations resume from
`gchat/state.json` (delete it for a clean slate). On a server run it under
systemd/launchd; today it dies with the terminal that started it.

Development without Google: `python3 -m gchat.cli_harness --package
GLDFundingEngine20080714`.

Another machine needs: the repo, requirements, the service-account key,
`.env`, the AIRO login(s), and the guarantee that no other instance runs —
the GCP project, Chat app, topic and subscription are shared and must not
be re-created.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "isn't responding", nothing arrives; Chat error log `Failed to publish … PERMISSION_DENIED` | Topic Publisher granted to the wrong principal | Grant Publisher to the per-app service agent from the Chat Configuration page (A4.7–A4.8) |
| Publishes succeed, service log shows nothing | Service not running, or message sent before the subscription existed | Start it; pre-subscription messages are not retained |
| Answers every other message | Two processes on one subscription | `pkill -f gchat.bot`, start one |
| `type=None space=None` in the log | Classic-format parser on an add-ons event | Parse `chat.messagePayload` (both shapes handled in `_parse_event`) |
| `400 The request does not specify which message to reply to` | `messageReplyOption` sent without a thread (DMs) | Only set it when a thread name is present |
| `SSL: UNEXPECTED_EOF_WHILE_READING` on a post after idle | Stale keep-alive socket | Rebuild the client and retry (already handled) |
| Agent says the AIRO MCP "failed to connect" | Network outage at session start; MCP is never retried in-session | Restore network; restart (resume) or `/new` |
| `storageQuotaExceeded` on Drive upload | Destination is My Drive | Use a Shared Drive (B2) |
| "time limit" message mid-build | `GCHAT_TURN_TIMEOUT_S` too short | Set ≥ 3600; `/continue` resumes |
| Another package's analysis appears in `PackageAnalysis.md` | Another user's run wrote the shared fixed path | One migration at a time today; per-client workdir in the target design |
