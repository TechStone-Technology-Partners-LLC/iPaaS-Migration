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
# Workato folder the built recipe is created in (default: AIRO Testing Rithwik)
GCHAT_WORKATO_FOLDER_ID=33882168
```

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
the thread to answer; say "approved" to finish (v1 stops at approved
analysis — no recipe is built). `/abort` stops a run; `/continue` extends
the budget after a limit pause.

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
