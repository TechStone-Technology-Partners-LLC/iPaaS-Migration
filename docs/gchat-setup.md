# MigrAIte Google Chat Bot — One-Time Setup

The bot runs locally (`python -m gchat.bot`) next to this repo and `.env`.
Google never calls this machine: events arrive by **pulling** a Pub/Sub
subscription; replies go out as HTTPS calls to the Chat API. No public
endpoint, no tunnel.

## 1. GCP project (techstonellc.com account)

1. console.cloud.google.com → create project, e.g. `ipaas-migraite-demo`.
2. **APIs & Services → Enable APIs**: enable **Google Chat API** and **Cloud Pub/Sub API**.

## 2. Service account + key

1. IAM & Admin → Service Accounts → Create: `gchat-migration-bot`.
2. Keys → Add key → JSON. Save it **outside the repo**, e.g. `~/keys/gchat-bot.json`.

## 3. Pub/Sub topic + subscription

1. Pub/Sub → Topics → Create: `gchat-events`.
2. On the topic, create a **pull** subscription: `gchat-events-sub`
   (defaults are fine; ack deadline 60s).
3. Grant publish rights to the Chat app's service agent — on topic `gchat-events`
   → Permissions → Grant access:
   - Principal: the **Service account email** shown on the Chat API
     **Configuration** page under **Connection settings** (format
     `service-<number>@gcp-sa-gsuiteaddons.iam.gserviceaccount.com`).
     Do NOT use `chat-api-push@system.gserviceaccount.com` — that is the
     legacy principal and publishes fail with PERMISSION_DENIED.
   - Role: **Pub/Sub Publisher**
4. On the **subscription** → Permissions → Grant access:
   - Principal: `gchat-migration-bot@<project>.iam.gserviceaccount.com`
   - Role: **Pub/Sub Subscriber**

## 4. Chat app configuration

Google Chat API → **Configuration** tab:

- App name: `migrAIte` · avatar URL + description as desired.
- Interactive features: **ON**. Enable *Receive 1:1 messages* and
  *Join spaces and group conversations*.
- Connection settings: **Cloud Pub/Sub**, topic
  `projects/<project>/topics/gchat-events`.
- Visibility: make the app available to specific people in techstonellc.com
  (a named list needs no admin; publishing domain-wide via Marketplace needs a
  Workspace admin to approve).
- Save. Then in Google Chat, create a test space and **add the migrAIte app**
  to it (the app can only act in spaces it's a member of).

## 5. `.env` additions

```
GOOGLE_APPLICATION_CREDENTIALS=/Users/<you>/keys/gchat-bot.json
GCP_PROJECT_ID=ipaas-migraite-demo
GCHAT_SUBSCRIPTION=gchat-events-sub
# optional allowlist of sender emails (comma-separated); empty = anyone in the space
GCHAT_ALLOWED_USERS=
# tunable safety limits (bot reads these each run)
# full analyze+build runs cost roughly $10-20 — set the cap accordingly
GCHAT_MAX_COST_USD=20.00
GCHAT_MAX_TURNS=100
GCHAT_TURN_TIMEOUT_S=1200
# "still working" heartbeat cadence during long agent turns (seconds)
GCHAT_HEARTBEAT_S=180
# Workato folder the built recipe is created in (default: AIRO Testing Rithwik)
GCHAT_WORKATO_FOLDER_ID=33882168
```

## 5b. Analysis delivery via Google Docs (optional but recommended)

Chat apps cannot attach files to messages (Google restricts uploads to user
auth), so the bot delivers the analysis as **Google Docs** in a shared Drive
folder and posts the links. Reviewers edit/comment in place; the bot pulls
the edited Doc back to disk before the agent's next turn.

1. Enable the **Google Drive API** on the project.
2. Create a Drive folder (e.g. "MigrAIte Analyses"). A folder inside a
   **Shared Drive** is most robust; a My Drive folder also works.
3. Share it with `gchat-migration-bot@<project>.iam.gserviceaccount.com`
   as **Editor**.
4. Add to `.env`: `GCHAT_DRIVE_FOLDER_ID=<folder id from the folder URL>`.

Without `GCHAT_DRIVE_FOLDER_ID` the bot runs normally and just skips delivery
(files stay on the bot machine's disk).

**Recipe build (phase 2):** after the user approves the analysis, the agent
builds the recipe through the **Workato AIRO MCP** (recipe_builder_* tools,
wired in `gchat/session.py`). AIRO auth rides on Claude Code's stored OAuth
for `https://app.workato.com/airo_mcp` — authorize it once by using the AIRO
MCP from an interactive Claude Code session in this repo. The final chat
message contains the recipe URL.

`ANTHROPIC_API_KEY` must also be present (it already is, for enrichment).

## 6. Install deps & run

```
pip3 install -r requirements.txt
python -m gchat.bot
```

Then in the test space: upload a webMethods package **zip** in a message.
The bot extracts it to `WebMethods/<PackageName>/`, runs the analysis,
posts progress + cost footers, and asks questions in the thread. Reply in
the thread to answer; say "approved" and it asks which Workato folder to
use, then builds the recipe via AIRO and posts the recipe URL. Commands:
`/new` resets the conversation, `/abort` stops a run immediately,
`/continue` extends the budget after a limit pause.

## Local dry-run (no Google needed)

```
python -m gchat.cli_harness --zip /path/to/package.zip
python -m gchat.cli_harness --package GLDFundingEngine20080714
```

## Notes / limits

- One migration at a time (demo constraint) — a second zip in another thread
  is politely rejected while one is active.
- Chat uploads cap at 200MB — ample for package zips.
- If the laptop is asleep, messages queue in the subscription and are
  processed when the bot starts (default message retention 7 days).
- Bot restart mid-migration: session ids are persisted in `gchat/state.json`;
  the session resumes with full context on the next message in the thread.

## Running the bot on another machine

The GCP project, Chat app, topic, and subscription are shared — do NOT
re-create them. A new machine needs:

1. **Repo + deps**: clone the branch, Python 3.10+, `pip3 install -r requirements.txt`
   (claude-agent-sdk bundles the Claude Code engine).
2. **`.env`** at the repo root with:
   ```
   ANTHROPIC_API_KEY=...                      # engine auth (or rely on a local `claude` login)
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/gchat-bot.json   # service-account key (get a copy, or mint a new key for the same SA)
   GCP_PROJECT_ID=ipaas-migraite-demo
   GCHAT_SUBSCRIPTION=gchat-events-sub
   GCHAT_MAX_COST_USD=20.00                   # optional, default 5.00
   GCHAT_MAX_TURNS=100                        # optional
   GCHAT_TURN_TIMEOUT_S=1200                  # optional
   GCHAT_WORKATO_FOLDER_ID=33882168           # optional, suggested default folder
   GCHAT_ALLOWED_USERS=                       # optional sender allowlist
   ```
3. **Workato AIRO OAuth** (needed for the build phase): the token lives in
   `~/.claude` per machine. Authorize once interactively:
   `claude mcp add --transport http workato-airo-mcp-server https://app.workato.com/airo_mcp`
   then in a `claude` session run `/mcp` and complete the login. The bot's
   headless sessions reuse that token.
4. **One runner at a time, globally.** The Pub/Sub subscription is shared:
   two machines running the bot will each receive half the messages. Stop the
   other instance first (or create a second Chat app + topic for a second runner).
