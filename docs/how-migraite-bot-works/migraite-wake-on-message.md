# MigrAIte bot — wake-on-message hosting (Azure VM)

Status: design, not built. 2026-10-17.

**v1 scope:** run the current bot flow unchanged on the VM, plus sleep/wake.
The current flow allows **one migration at a time** across all users
(`active_thread` guard, one shared checkout). Concurrent users need the
per-session worktree change (§6a) — later, not v1.

The bot runs on one small Azure VM that **deallocates itself after 60 minutes
idle** and is **started again by the next Chat message**. Nothing we run is on
24/7; Google Pub/Sub holds messages while the VM is off.

## 1. Pieces

```
Google Chat ──► Pub/Sub topic `gchat-events`
                   │
                   ├─► gchat-events-sub   (PULL, exists today)
                   │      read by the bot on the VM — messages wait here while VM is off
                   │
                   └─► gchat-wake-sub     (PUSH, new)
                          POST each message to the wake function
                                 │
                                 ▼
                    Azure Function `migraite-wake`  (new, runs only per request)
                      VM off?  → start it, post "starting up" in the thread
                      VM on?   → do nothing

Azure VM `migraite-bot` (B2s, 2 vCPU / 4 GB)
   systemd runs `python -m gchat.bot` at boot
   bot idle watcher: 60 min with no activity → deallocate self
```

| Piece | New? | Runs | Cost/mo |
|---|---|---|---|
| Pub/Sub topic + pull sub | exists (GCP) | Google, always | ~$0 |
| Push sub `gchat-wake-sub` | new (GCP) | Google, always | ~$0 |
| Function `migraite-wake` | new (Azure) | only when a message arrives | ~$0 (free grant) |
| VM compute | new (Azure) | only while awake | ~$0.04/hr awake |
| VM disk + public IP | new (Azure) — part of the VM | always, even while VM is off | ~$9 |

## 1a. Azure placement

Checked 2026-10-17 with `az` (read-only). The signed-in account sees one
subscription, **Techstone-iGlass**. It holds only iGlass resources (resource
group `iGlass`: 3 Linux web apps on B1/B2 App Service plans, Function App
`iglasslogs` on a Y1 consumption plan, Key Vault `iglass-dev-kv`, SQL, Service
Bus, Azure OpenAI). **No VMs, disks or public IPs exist.**

Decision: MigrAIte goes in **its own new resource group `rg-migraite`** in
Techstone-iGlass, region **East US** (prices above are East US). Everything
MigrAIte needs is created there; nothing of iGlass is reused:

| Resource | Name | Why not reuse iGlass's |
|---|---|---|
| VM + OS disk + public IP | `migraite-bot` | none exist |
| Function App + its storage account | `migraite-wake` | `iglasslogs` is iGlass code; keep deploys and permissions separate |
| Key Vault (Chat key for "waking up" notice) | `kv-migraite` | `iglass-dev-kv` is iGlass dev secrets; a separate vault keeps access separate (cost ~$0) |

One resource group means MigrAIte's cost shows up as a single line in Cost
Management, and deleting the group removes all of it.

**Created 2026-10-18** (VM only; sleep/wake not built yet):

| Item | Value |
|---|---|
| Resource group | `rg-migraite` (East US, tag `app=migraite`) |
| VM | `migraite-bot`, **Standard_B2s** (2 vCPU / 4 GB), Ubuntu 24.04 LTS, admin `azureuser`, SSH key `~/.ssh/id_ed25519_techstone` |
| Disk | 64 GB Standard SSD |
| Public IP | `20.115.25.138` (Standard, static) |
| NSG | `migraite-botNSG`, one inbound rule `AllowSSH-Rithwik`: TCP 22 from `73.189.70.138/32` only |
| System identity | principal ID `269ab3e9-e9e3-49db-b031-e2e84c74c9f0` (no roles yet) |
| Providers registered | `Microsoft.Compute`, `Microsoft.Network` (were unregistered; free) |

**Why B2s, not B2als_v2:** the subscription's B-series v2 quota in East US is
0 cores. B2s (older B-series, quota 10) has the same 2 vCPU / 4 GB at
$0.0416/hr vs $0.0376/hr (~$0.26/mo more at 66 awake hours). B2s is
zone-restricted for this subscription, so the VM is regional (no zone).
To move to B2als_v2 later: request 2 cores of `standardBasv2Family` quota,
then resize (one reboot).

## 2. Wake path

1. User sends a message. Chat publishes it to the topic.
2. Pub/Sub delivers one copy to each subscription. The pull copy waits.
3. Pub/Sub POSTs the push copy to the function.
4. Function reads the VM power state:

| Power state | Function does | Returns |
|---|---|---|
| `running`, `starting` | nothing | 200 |
| `deallocated`, `stopped` | `begin_start` (don't wait) + post "starting up" | 200 |
| `deallocating`, `stopping` | nothing | **503** |
| start call fails (capacity, API error) | nothing | **503** |

5. VM boots (~1–3 min), systemd starts the bot, the bot pulls the waiting
   message and handles it as normal.

**Why 503 matters:** a message that lands while the VM is shutting down can't
start it yet. Returning 503 makes Pub/Sub retry the push (backoff 10 s → 600 s)
until the VM is fully deallocated and the start succeeds. The same retry covers
a failed start. Without this, that message would sit in the pull sub with
nothing to wake the VM until someone sends another message.

"Starting up" is posted only on the call that actually issued the start, so a
burst of messages during boot gets one notice, not five.

## 3. Sleep path (inside the bot)

The bot already knows whether it's busy, so it decides when to sleep — no
external cron.

- `last_activity` is set on every handled event and at the end of every agent turn.
- A watcher task checks every 60 s. Idle means **all** of:
  - no thread has a running `task` (no agent turn in flight — long AIRO builds
    send no messages, so message time alone is not enough),
  - the event queue is empty,
  - `now - last_activity >= GCHAT_IDLE_SHUTDOWN_S` (default `0` = off, so dev
    machines never try; the VM's systemd unit sets `3600`).
- Shutdown order (closes the race with a message arriving at the last second):
  1. Cancel the streaming pull. New messages now stay unacked in the pull sub.
  2. Re-check the queue and running tasks. If anything appeared, resubscribe and abort.
  3. `_save_state()`.
  4. Disconnect agent sessions.
  5. Deallocate self via the VM's managed identity. The process dies with the VM.
- Steps 1–5 take a few seconds. A message landing in that window is never
  lost — it was not pulled, so it stays in the pull sub. But its wake can be
  missed: if the function checks the VM before step 5 starts, it sees
  `running`, returns 200, and nothing wakes the VM later. The message is then
  answered when the next message wakes the VM. Accepted for v1 (needs a
  message within seconds of an exact 60-min idle mark). Closing it fully: the
  bot sets a VM tag `migraite=sleeping` before step 1, and the function returns
  503 for `running` + `sleeping` (and the bot clears the tag after subscribing
  on boot).
- Without step 1 first, the same message would be pulled and acked
  (`bot.py:101` acks on receipt) and then die with the VM — gone for good.

The VM finds its own subscription / resource group / name from the instance
metadata endpoint (`169.254.169.254/metadata/instance`), so no config is needed.

## 4. Code sketches

**Wake function** (Python, Azure Functions Flex Consumption):

```python
import json, base64, logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from google.oauth2 import service_account
from googleapiclient.discovery import build

SUB_ID, RG, VM = env("AZ_SUB"), env("AZ_RG"), env("AZ_VM")
compute = ComputeManagementClient(DefaultAzureCredential(), SUB_ID)

def main(req: func.HttpRequest) -> func.HttpResponse:
    state = power_state()
    if state in ("running", "starting"):
        return ok()
    if state in ("deallocating", "stopping"):
        return retry()                        # Pub/Sub will redeliver
    try:
        compute.virtual_machines.begin_start(RG, VM)   # returns immediately
    except Exception:
        logging.exception("start failed")
        return retry()
    notify_starting(req)                      # best effort; never fails the request
    return ok()

def power_state() -> str:
    view = compute.virtual_machines.instance_view(RG, VM)
    return next(s.code.split("/")[1] for s in view.statuses if s.code.startswith("PowerState/"))

def notify_starting(req) -> None:
    # Pub/Sub push body: {"message": {"data": base64(chat event)}}
    # Parse space/thread the same way Bot._parse_event does (both event formats);
    # skip non-message events and BOT senders; post via Chat API with the
    # bot's service account (scope chat.bot):
    # "⏰ MigrAIte is waking up — about 2 minutes. Your message is queued."
    ...
```

**Self-deallocate** (new helper on the VM, called from the bot's watcher):

```python
from azure.identity import ManagedIdentityCredential
from azure.mgmt.compute import ComputeManagementClient
import requests

meta = requests.get("http://169.254.169.254/metadata/instance/compute?api-version=2021-02-01",
                    headers={"Metadata": "true"}, timeout=5).json()
compute = ComputeManagementClient(ManagedIdentityCredential(), meta["subscriptionId"])
compute.virtual_machines.begin_deallocate(meta["resourceGroupName"], meta["name"])
```

## 5. Setup (one time)

**Azure**
1. ~~VM `migraite-bot`~~ — done 2026-10-18 (§1a): B2s, Ubuntu LTS, Standard SSD OS disk, Standard
   public IP. Turn on **system-assigned managed identity**.
2. ~~Give the VM's identity **Virtual Machine Contributor** scoped to the VM itself~~
   — done 2026-10-18 (so it can deallocate itself and nothing else).
3. Function App `migraite-wake` (Python, Flex Consumption). Turn on
   system-assigned managed identity; give it **Virtual Machine Contributor**
   scoped to the VM.
4. Function app settings: `AZ_SUB`, `AZ_RG`, `AZ_VM`, and the Chat service
   account key (`gchat-bot.json` contents) as a Key Vault reference.

**VM**
5. systemd unit for the bot: `After=network-online.target`, `Restart=always`,
   `WantedBy=multi-user.target`, enabled.
6. Set `DISABLE_AUTOUPDATER=1` for the Claude Code CLI so a reboot never pulls
   a new CLI version mid-project; upgrade on purpose.
7. Keep repo, worktrees, `state.json` and `~/.claude` on the OS disk (they must
   survive deallocation; any temp disk is wiped).
   With per-session worktrees, save each thread's worktree path in
   `state.json` and resume with that same `cwd` — Claude Code files session
   transcripts by working directory, so a different `cwd` can't find them.

**GCP**
8. On topic `gchat-events`, create push subscription `gchat-wake-sub`:
   - endpoint: function URL with `?code=<function key>`
   - ack deadline: 60 s (covers function cold start)
   - retry policy: exponential backoff, min 10 s, max 600 s
   - leave `gchat-events-sub` (pull) unchanged

## 6. Second-order effects

Restarts go from rare to several per day, so the restart-resume path in
`bot.py` (lines 197–205) becomes the main path. What it drops today:

| On restart | Effect | Status |
|---|---|---|
| `BUDGET_PAUSED` state + budget spend | used to come back as `WAITING_FOR_USER` with a fresh budget | **fixed 2026-10-17** — state, spend, turns and `/continue` extensions saved in `state.json` |
| `pending_delivery` | a failed Drive upload used to be forgotten | **fixed 2026-10-17** — saved in `state.json` |
| `buffered` mid-turn message | n/a — can't sleep mid-turn | none needed |
| `seen` dedupe | messages are acked on receipt, so no redelivery after restart | none needed |

Old `state.json` files without the new keys still load (fresh budget, nothing pending).

Also: the first message after sleep takes 1–3 min to answer. The "starting up"
notice is what keeps users from thinking the bot is broken.

## 6a. Worktree cleanup

Applies once per-session worktrees land (one worktree per Chat thread).

**RAM vs disk.** RAM leaks come from Claude CLI processes; every deallocate
kills them, so RAM resets on each sleep. Worktrees are disk and survive sleep,
so they need their own cleanup. Growth is slow (~8 MB repo + package each).

**No "finished" signal.** A successful migration never reaches `DONE`: every
`_finish` call is `aborted=True`, and the prompt tells the agent to stay
available for recipe changes after the push. So cleanup keys off inactivity,
not completion.

| Trigger | When | Notes |
|---|---|---|
| `/abort` or `/new` | immediately | user explicitly ended the thread |
| **No message in the thread for N days** (default 7, `GCHAT_WORKTREE_TTL_DAYS`) | checked on boot and before each sleep | main trigger; post "archived — start a new thread", mark `DONE` |
| `/done` command (optional) | immediately | lets users close a thread early |
| Orphans on boot | every boot | delete worktree dirs no active thread in `state.json` points to (crash leftovers), then `git worktree prune` |

**Before deleting a worktree:**
1. *(Later, optional)* `migration-specs/<pkg>_progress.md` exists only in the
   worktree (only the two analysis docs go to Drive). Its content is mostly in
   the agent's final Chat message, so losing it is acceptable for now; adding
   it to the Drive deliveries is a later flow change.
2. Skip the delete if `pending_delivery` is non-empty; retry next check.
3. Mark the thread `DONE` and remove its transcript dir under
   `~/.claude/projects/` (keyed by the worktree path), so a later message never
   tries to resume a session whose `cwd` is gone.

## 7. Failure modes

| Failure | Result | Covered by |
|---|---|---|
| Message after deallocate begins | push retries until deallocated, then starts | 503 + Pub/Sub retry |
| Message in the seconds before deallocate begins | kept in pull sub; answered on next wake | cancel pull first; optional VM tag (§3) |
| Start fails (capacity) | push retries with backoff | 503 + Pub/Sub retry |
| Bot crashes while VM up | systemd restarts it; message waits in pull sub | `Restart=always` |
| Function down / misconfigured | VM never wakes; messages wait 7 days | alert on push-sub undelivered count |
| VM never sleeps (bug in watcher) | billed like always-on (~$36/mo) | Azure budget alert |

## 8. Decisions taken (change if needed)

- Idle timeout 60 min (`GCHAT_IDLE_SHUTDOWN_S`).
- Function hosted in Azure (managed identity → no Azure secret outside Azure).
- Push auth by function key in the URL. Leak impact is low (someone can start
  the VM). Harden later with Pub/Sub OIDC tokens if needed.
- "Starting up" notice on: requires the Chat key in Key Vault.

## 9. Known issues — accepted for v1

Reviewed 2026-10-17 and deliberately left for later.

1. **Missed wake at the shutdown instant.** A message landing in the few
   seconds between "stop pulling" and "deallocate" is kept, but nothing wakes
   the VM for it; it's answered when the next message arrives. Fix later: the
   VM-tag handshake in §3.
2. **Cold start.** First reply after sleep takes 1–3 min (no live test needed;
   accepted).
3. **Resume needs the same `cwd`.** Must be handled when per-session worktrees
   land (§5 step 7) — not a problem while the bot uses one checkout.

## 10. Build order

**Phase 1 — one migration at a time on the VM (current flow)**
1. VM + systemd + managed identity; bot runs always-on. Run one full
   migration from Chat end to end — proves the host before anything else.
   *2026-10-18:* VM, swap, venv, Claude login, AIRO login (tunnel on port
   8765, headless check OK), `migraite-bot.service` (enabled, survives reboot),
   Chat "hi" round trip — all done. **Full migration: done 2026-10-18**
   (STKErrorHandler → 2 recipes pushed to "migrAIte Bot Demo", folder
   35793543; 0 errors in the journal; ~0.8 GB RAM used, swap untouched).
2. Bot idle watcher + self-deallocate (`GCHAT_IDLE_SHUTDOWN_S`).
   *2026-10-18:* code in `gchat/bot.py` (`_idle_watch`) + `gchat/vm_power.py`
   (IMDS token + ARM deallocate, no new deps); VM role granted. **Live test
   passed 2026-10-18** with `GCHAT_IDLE_SHUTDOWN_S=300` (systemd drop-in
   `/etc/systemd/system/migraite-bot.service.d/idle.conf`): the VM's own
   identity deallocated it, ~19 s from request to deallocated. Kept at `0`
   (off) until the wake function (step 4) exists.
3. ~~Persist `pending_delivery` and budget state~~ — done (§6).
4. Wake function + push subscription.
   *2026-10-18:* code in `azure/wake_function/` (`wake_logic.py` = decisions,
   15 local cases pass; `function_app.py` = Azure/Chat calls). Created
   Function App `migraite-wake` (Flex Consumption, Python 3.12, 512 MB,
   East US) + storage `stmigraitewake1665` + App Insights `migraite-wake`;
   system identity has Virtual Machine Contributor on the VM; app settings
   `AZ_SUBSCRIPTION_ID` / `AZ_RESOURCE_GROUP` / `AZ_VM_NAME`. Registered
   `Microsoft.Storage`. Chat key app setting `GCHAT_SA_JSON` and the push
   subscription are set by Rithwik (secrets; local gcloud is a different org).
5. End-to-end: let it sleep, send a message, confirm reply and notice.
   *Passed 2026-10-18/19:* with a 300 s timeout the VM's identity deallocated
   it; a Chat DM then made the wake function's identity start it (activity
   log), and the bot replied. Push sub `gchat-wake-sub` created by Rithwik in
   the TechStone GCP project. Production timeout: 3600 s.

**Phase 2 — multiple migrations at once**
6. Per-session worktrees: package extracted into the thread's worktree, `cwd`
   per session, worktree path saved per thread in `state.json`.
7. Remove the `active_thread` one-migration guard.
8. Cleanup triggers and pre-delete steps (§6a).
9. Owed test: two builds at once under one AIRO login — confirm each gets its
   own recipe.

## 11. Productionize later

Shortcuts taken to get v1 running; revisit before wider use.

| # | Shortcut now | Production version | Why |
|---|---|---|---|
| 1 | VM uses Rithwik's own GitHub login to clone/pull | Read-only **fine-grained token** (Contents: read, this repo only) or a read-only **deploy key** | The agent runs with `bypassPermissions` and reads untrusted client packages; a personal login gives it push access to every repo the account can reach, and its actions show as Rithwik |
| 2 | SSH open only to Rithwik's current IP | Per-user IPs or Azure Bastion / `az ssh` | Breaks when connecting from another network |
| 3 | VM size B2s (B-series v2 quota is 0) | Request `standardBasv2Family` quota, resize to B2als_v2 | ~10% cheaper per hour |
| 4 | `<pkg>_progress.md` stays only on disk | Add to Drive deliveries | Lost on worktree cleanup (§6a) |
| 5 | Missed-wake race at shutdown accepted | VM-tag handshake (§3) | Rare delayed reply |
| 6 | VM uses Rithwik's personal Claude login (`/login`) | `ANTHROPIC_API_KEY` in the VM `.env` | A personal plan's usage limits and terms don't fit a shared service; with the key set the engine ignores the login |
| 7 | `requirements.txt` unpinned (VM got claude-agent-sdk 0.2.168, Mac 0.2.148) | Pin versions | VM and dev machines run different engine versions |
| 8 | Chat service account key stored as a plain Function App setting (`GCHAT_SA_JSON`) | Key Vault reference (`@Microsoft.KeyVault(...)`) with the function identity as Secrets User | App settings are readable by anyone with contributor on the app |
| 9 | Push subscription authenticates with the function key in the URL | Pub/Sub OIDC token, verified in the function | A leaked URL lets anyone start the VM (low impact) |

Token expiry note for #1: fine-grained tokens expire; when one does, pulls fail
but the running bot keeps working. Renew on a calendar reminder.
