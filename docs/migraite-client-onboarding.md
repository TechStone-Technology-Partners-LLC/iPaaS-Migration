# MigrAIte Bot — Client Onboarding (internal)

What to do, per client, so their people can run migrations through the bot
and receive recipes in their own Workato workspace. Assumes the service is
already provisioned per [migraite-bot-setup.md](migraite-bot-setup.md).

Related: [workflow](migraite-workflow.md) · [gchat bot](migraite-gchat-bot.md) · [user guide](migraite-user-guide.md)

---

## 0. The model

Per client, the service holds exactly one client-specific secret: an AIRO
OAuth login performed by **the client's own Workato user** into a **Claude
config directory reserved for that client**. Everything else the client
needs is access: to the Chat app, to the Shared Drive folder, and to their
own Workato workspace (which they already have). The service's Claude
identity (`ANTHROPIC_API_KEY`) is shared across clients and bills to us.

**Status.** The per-client config directory and the client registry that
selects it are designed and verified in pieces (the engine honors
`CLAUDE_CONFIG_DIR`; MCP auth state is stored per config directory) but not
yet wired into the bot — today the bot uses one AIRO login and one Drive
destination for everyone. Until that lands, "onboarding a client" means
switching the service's single identity to that client's, one client at a
time. The steps below are written for the target model and marked where
today differs.

---

## 1. Before the call — checklist

- [ ] Client has a Workato workspace with **AIRO / WorkAI MCP available**
      (it is a Workato entitlement; confirm in their workspace before
      promising the build phase).
- [ ] Client has (or creates) a **Workato user** that will own the migration
      recipes: a member of the target workspace with rights to create
      recipes and folders in the target project. This is the identity that
      logs in to AIRO in §3.
- [ ] Client has a target **Workato folder** (or lets us create one during
      the first run).
- [ ] Client contacts have Google accounts we can share with — either
      techstonellc.com guest accounts we issue (simplest: everything
      in-domain), or their own Workspace accounts (requires our Workspace
      admin to allow external members on the Shared Drive and external users
      on the Chat app).
- [ ] Decide the client's **cost cap** per migration and who is on the
      **allowlist** (sender emails permitted to trigger runs).

---

## 2. Google side — making the bot reachable from outside TechStone

The Chat app and the Shared Drive both live in the techstonellc.com
Workspace. A client's people are *external* to it, and Google gates external
access in three places. Pick one of two models:

- **Guest-account model (simplest, recommended for pilots).** Issue each
  client user a techstonellc.com account (e.g. `jane-acme@techstonellc.com`).
  They are then in-domain: the app's visibility list and the Shared Drive
  work with no admin changes. Cost: a Workspace seat per user and the client
  using a second account.
- **External-access model.** Client users keep their own Google accounts.
  Requires a **techstonellc.com Workspace admin** to (a) allow external
  users on the Chat app — in the Admin console under Apps → Google
  Workspace → Google Chat, external chat must be enabled for the org unit,
  and the app's visibility must include the client's users or domain; and
  (b) allow **external members on Shared Drives** (Admin console → Apps →
  Drive and Docs → Sharing settings → shared drive creation/sharing options
  → allow users outside the organization). Verify both with one client user
  before promising it; the Chat-app part in particular has changed across
  Google releases.

Then, whichever model:

1. **Chat app visibility.** Google Chat API → Configuration → Visibility →
   add the client users' emails (guest accounts or, under the external
   model, their own).
2. **Client adds the app.** Have each client user open Google Chat → **New
   chat** → search `migrAIte` → start a DM. For a shared client space, create
   it yourself (`MigrAIte — Acme`), add the app, then add the client users.
   In a space, one thread = one migration; several people can watch one
   contained conversation. (There is nothing to "download" — a Chat app is
   added, not installed.)
3. **Analysis delivery.** Create a folder for the client inside the Shared
   Drive (e.g. `MigrAIte/Acme`) and add the client users as
   **Contributors** — they need edit rights to give feedback in the Docs.
   Record the folder id for the registry.
4. **Allowlist.** Add the client users' emails to the client's allowlist so
   only they can start runs in that space.

Test the whole path as the client would: from their account, DM the app with
`hi` (expect the greeting) and open the Drive folder (expect edit access).

*Today:* one Shared Drive id in `.env` — put the client folder id there while
that client is active.

---

## 3. Workato AIRO login for the client

This is the step that makes recipes land in the *client's* workspace.

1. On the service machine, create the client's Claude config directory:

   ```bash
   export CLAUDE_CONFIG_DIR=/srv/migraite/clients/acme/claude   # any path; one per client
   mkdir -p "$CLAUDE_CONFIG_DIR"
   ```

2. Register the AIRO MCP server in that directory and open an interactive
   session there (from the repository root):

   ```bash
   claude mcp add --transport http workato-airo-mcp-server https://app.workato.com/airo_mcp
   claude
   ```

3. Inside the session: accept the workspace trust prompt if shown; if
   `ANTHROPIC_API_KEY` is not exported in this shell, run `/login` with the
   service's Claude identity; then run **`/mcp`**, select
   `workato-airo-mcp-server`, and complete the browser login **as the
   client's Workato user** from §1 (screen-share with the client, or have
   them type their credentials themselves — we never need their password).
   Exit the session.

4. Verify from the same shell that the token works and points at the right
   workspace — the folder names returned must be the *client's*:

   ```bash
   python3 - <<'EOF'
   import asyncio, os
   from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
   async def main():
       opts = ClaudeAgentOptions(cwd=os.getcwd(), permission_mode="bypassPermissions", setting_sources=["project"],
           mcp_servers={"workato-airo-mcp-server": {"type": "http", "url": "https://app.workato.com/airo_mcp"}},
           env={"CLAUDE_CONFIG_DIR": os.environ["CLAUDE_CONFIG_DIR"]}, max_turns=4)
       async with ClaudeSDKClient(options=opts) as c:
           await c.query("Call the AIRO tool folder_list and reply with the first 5 folder names, or AIRO-UNAVAILABLE.")
           async for m in c.receive_response():
               if isinstance(m, AssistantMessage):
                   for b in m.content:
                       if isinstance(b, TextBlock): print(b.text)
   asyncio.run(main())
   EOF
   ```

5. Note the client's default folder id (from the list above or the Workato
   UI) for the registry.

**Token lifetime.** The login stores a refresh token; the engine renews access
tokens automatically. If the client's Workato user is deactivated or the
grant is revoked, sessions start reporting AIRO as unavailable — redo §3.

**First-client caveat.** The login-as-another-workspace-user path has been
verified in parts but not yet rehearsed end to end with a second workspace.
Treat the first client onboarding as that rehearsal: run §3.4 and confirm
the folder list is theirs before the kickoff call.

*Today:* the bot does not yet select a config directory per client. To serve
a client now, perform §3 in the **default** config directory (i.e. without
setting `CLAUDE_CONFIG_DIR`) — which replaces the service's own AIRO login —
and restart the bot.

---

## 4. Registry entry *(target)*

Add the client to the registry the bot loads at start:

```
clients:
  acme:
    chat_spaces: [spaces/AAAA…]                    # the client's space(s); DM ids also allowed
    sender_domain: acme.com                         # fallback routing
    allowed_users: [jane@acme.com, raj@acme.com]
    claude_config_dir: /srv/migraite/clients/acme/claude
    workato_default_folder_id: 123456
    drive_folder_id: 1AbC…                          # their folder in the Shared Drive
    max_cost_usd: 25
    workdir: /srv/migraite/clients/acme/repo        # their own checkout of this repository
```

`workdir` is a separate checkout so two clients' runs never write the same
analysis paths.

*Today:* set the equivalent `.env` values (`GCHAT_DRIVE_FOLDER_ID`,
`GCHAT_WORKATO_FOLDER_ID`, `GCHAT_ALLOWED_USERS`, `GCHAT_MAX_COST_USD`) and
restart the bot.

---

## 5. Kickoff call — walkthrough script

1. In the client's space, start a thread: `@migrAIte` + upload a package zip
   (use one of theirs, or `GLDFundingEngine20080714` as the demo).
2. Narrate the phases while it runs: "📦 Received", heartbeats every ~3 min,
   the summary with one question (~10–15 min), the Doc links.
3. Open the Package Analysis Doc together; make one edit; reply in the
   thread; show the "📝 Picked up your edits" acknowledgment.
4. Reply "approved"; answer the folder question with *their* folder.
5. Build (20–30 min): show heartbeats, then the final message with the
   recipe URL. Open it in *their* Workato workspace.
6. Walk through the "remaining manual steps" in that message — typically
   creating/authorizing connections (HTTP, Oracle) in the Workato GUI, since
   AIRO cannot configure connector fields without a live connection.
7. Hand over the [user guide](migraite-user-guide.md).

Expect the "isn't responding" banner to flash on each message; say up front
that it is cosmetic.

---

## 6. Offboarding

Remove the client's users from the space, the Chat visibility list and the
Shared Drive folder; delete the registry entry and the client's config
directory (this discards their AIRO token); archive their checkout.
