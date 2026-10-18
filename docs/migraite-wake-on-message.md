# MigrAIte bot — wake-on-message hosting (Azure VM)

Status: design, not built. 2026-10-17.

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

Azure VM `migraite-bot` (B2als_v2, 2 vCPU / 4 GB)
   systemd runs `python -m gchat.bot` at boot
   bot idle watcher: 60 min with no activity → deallocate self
```

| Piece | New? | Runs | Cost/mo |
|---|---|---|---|
| Pub/Sub topic + pull sub | exists | Google, always | ~$0 |
| Push sub `gchat-wake-sub` | new | Google, always | ~$0 |
| Function `migraite-wake` | new | only when a message arrives | ~$0 (free grant) |
| VM compute | exists in plan | only while awake | ~$0.04/hr awake |
| VM disk + public IP | exists in plan | always | ~$9 |

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
  - `now - last_activity >= GCHAT_IDLE_SHUTDOWN_S` (default 3600; `0` disables).
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
1. VM `migraite-bot`: B2als_v2, Ubuntu LTS, Standard SSD OS disk, Standard
   public IP. Turn on **system-assigned managed identity**.
2. Give the VM's identity **Virtual Machine Contributor** scoped to the VM itself
   (so it can deallocate itself and nothing else).
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

1. VM + systemd + managed identity (bot runs always-on first — proves the host).
2. Bot idle watcher + self-deallocate (`GCHAT_IDLE_SHUTDOWN_S`).
3. ~~Persist `pending_delivery` and budget state~~ — done (§6).
4. Wake function + push subscription.
5. End-to-end: let it sleep, send a message, confirm reply and notice.
