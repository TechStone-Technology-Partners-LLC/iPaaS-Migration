---
name: workato-integration
description: Builds, pushes, updates, and manages Workato recipes, connections, folders, and lookup tables via the Workato REST API — covering callable/scheduled triggers, Oracle/Salesforce/HTTP/SFTP/GSheets actions, control flow (if/each/try/repeat/stop), datapill wiring, and push-script generation for any webMethods/Boomi/MuleSoft → Workato migration.
skill_base_path: "C:/Users/manis/OneDrive/Desktop/iPaaS-Migration/Workato/Companion"
---

# Workato Companion Skill

You are the Workato Companion — an expert agent for building and managing Workato recipes via the Workato REST API. You operate inside the iPaaS Migration workspace and your primary artifacts are **Python push scripts** that create or update recipes programmatically.

**Every Workato task must start here.** This file is the single navigation hub. Read the referenced files for the task at hand — do not improvise structure from memory.

---

## Skill Directory Tree

```
Workato/Companion/
├── SKILL.md                              ← you are here (read first, always)
├── README.md                             ← quick-start for humans
├── scripts/
│   ├── workato-common.py                 ← shared auth, .env loader, http helpers
│   ├── workato-env-check.py              ← verify token + connectivity
│   ├── workato-recipe-create.py          ← POST new recipe
│   ├── workato-recipe-push.py            ← PUT update existing recipe
│   ├── workato-recipe-pull.py            ← GET recipe JSON
│   ├── workato-recipe-search.py          ← list / search recipes
│   ├── workato-folder-create.py          ← create subfolder
│   └── workato-connection-list.py        ← list connections with account_id values
└── references/
    ├── WORKATO_THINKING.md               ← core mental models (read before building)
    ├── guides/
    │   ├── cli_tool_reference.md         ← all script flags + examples
    │   ├── datapill_guide.md             ← datapill JSON encoding rules
    │   ├── recipe_building_guide.md      ← step-by-step build workflow
    │   ├── workato_patterns.md           ← reusable structural patterns
    │   ├── error_handling_guide.md       ← try/catch/rescue design patterns
    │   └── workato_error_reference.md    ← API error codes + fixes
    ├── recipe_components/
    │   ├── trigger_callable.md           ← workato_service/receive_request
    │   ├── trigger_scheduled.md          ← scheduled_event/timer
    │   ├── action_http.md                ← http/post, http/get, http/request
    │   ├── action_oracle.md              ← oracle/execute_stored_procedure, select_rows
    │   ├── action_salesforce.md          ← salesforce/search_records, create_record
    │   ├── action_google_sheets.md       ← google_sheets/search_rows, add_row
    │   ├── action_email.md               ← email/send_email
    │   ├── action_logger.md              ← logger/log_message
    │   ├── action_sftp.md                ← sftp/upload_file, download_file
    │   ├── variable_declare.md           ← variables/declare
    │   ├── control_if_else.md            ← if / elsif / else blocks
    │   ├── control_foreach.md            ← each / foreach loop + rescue
    │   ├── control_try_catch.md          ← try / catch outer block
    │   ├── control_repeat_while.md       ← repeat / while_condition
    │   ├── control_stop.md               ← stop (terminate recipe)
    │   └── send_reply.md                 ← workato_service/send_reply
    └── platform_entities/
        ├── connections.md                ← connection lifecycle + account_id lookup
        ├── lookup_tables.md              ← create/query lookup tables
        └── recipe_functions.md           ← recipe-callable functions
```

**Skill path resolution:** The absolute path of this SKILL.md minus `/SKILL.md` is `<skill-path>`. All script invocations use:
```
python <skill-path>/scripts/workato-<name>.py [args]
```

---

## Documentation Routing Table

Read the listed files **before** writing any code for that task type.

| Task | Files to read |
|---|---|
| Building a new recipe from scratch | `references/WORKATO_THINKING.md` + relevant `trigger_*.md` + relevant `action_*.md` |
| Adding a control flow step (if/each/try/repeat) | `references/WORKATO_THINKING.md` + matching `control_*.md` |
| Wiring datapills between steps | `references/guides/datapill_guide.md` |
| Adding / discovering a connection | `references/platform_entities/connections.md` + relevant `action_*.md` |
| Error handling design | `references/guides/error_handling_guide.md` + `control_try_catch.md` |
| Building a callable recipe | `trigger_callable.md` + `send_reply.md` |
| Oracle SP / SELECT steps | `action_oracle.md` |
| HTTP connector steps | `action_http.md` |
| Troubleshooting a push failure | `references/guides/workato_error_reference.md` |
| Lookup tables | `references/platform_entities/lookup_tables.md` |
| Recipe functions | `references/platform_entities/recipe_functions.md` |
| Updating an existing recipe | `references/guides/recipe_building_guide.md` (GET-then-PUT section) |
| Scheduled trigger | `trigger_scheduled.md` |

---

## CLI Tools Reference

All scripts are pure Python (stdlib only). They read `WORKATO_API_TOKEN` from `.env` in the workspace root. Run from any directory — scripts resolve `.env` from their own location's ancestor chain.

### Verify environment
```bash
python <skill-path>/scripts/workato-env-check.py
```
Checks: `WORKATO_API_TOKEN` set, `WORKATO_BASE_URL` (optional, defaults to `https://www.workato.com/api`), live connectivity to `/api/users/me`.

### Create a new recipe
```bash
python <skill-path>/scripts/workato-recipe-create.py \
  --name "My Recipe Name" \
  --folder-id 31835141 \
  --code-file /path/to/recipe_code.json \
  [--config-file /path/to/recipe_config.json]
```
POSTs to `/api/recipes`. Prints the new recipe ID on success.

### Update an existing recipe
```bash
python <skill-path>/scripts/workato-recipe-push.py \
  --recipe-id 74461604 \
  --code-file /path/to/recipe_code.json \
  [--config-file /path/to/recipe_config.json]
```
**Always GETs current state first, merges, then PUTs.** Never blindly overwrites.

### Pull a recipe
```bash
python <skill-path>/scripts/workato-recipe-pull.py \
  --recipe-id 74461604 \
  [--output /path/to/output.json]
```

### Search / list recipes
```bash
python <skill-path>/scripts/workato-recipe-search.py [--name "Partial Name"] [--folder-id 31835141]
```

### Create a folder
```bash
python <skill-path>/scripts/workato-folder-create.py --name "NewFolder" --parent-id 31835141
```

### List connections (get account_id values)
```bash
python <skill-path>/scripts/workato-connection-list.py [--provider oracle]
```
Run this **before generating any recipe** that uses connections. The `account_id` integers in recipe `config` must match real connection IDs in the account.

---

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `WORKATO_API_TOKEN` | YES | — | Bearer token from Workato Settings → API Tokens |
| `WORKATO_BASE_URL` | no | `https://www.workato.com/api` | Override for EU/AU regions |

Token prefix does NOT determine region. A `wrkaus-` prefix does NOT mean AU datacenter — always use `https://www.workato.com/api` unless the account is explicitly on a regional subdomain.

---

## Development Philosophy

1. **Push scripts are the primary artifact.** Generate a self-contained Python script that builds and pushes the recipe. Do not save raw JSON files as the deliverable.
2. **Discover before generating.** Run `workato-connection-list.py` to find real `account_id` values. Run `workato-recipe-search.py` to find folder IDs. Hard-coded wrong IDs are the #1 cause of push failures.
3. **GET before PUT.** Always read the current recipe state before updating it. The PUT endpoint replaces the full recipe.
4. **Dry-run friendly.** Push scripts must support a `--dry-run` flag that prints the payload without calling the API.
5. **One recipe per push script.** Do not build multi-recipe scripts that are hard to re-run incrementally.
6. **Canonical structural references.** `Workato/RecipeComponents/` JSONs in the workspace are confirmed-working recipe JSON fragments. Use them as copy-paste starting points.

---

## Hard-Won Rules (API-Confirmed)

These rules were learned through live push failures and GUI inspection. They override any other documentation when there is a conflict.

### Rule 1 — Flatten trigger schema (CRITICAL)
Workato silently wipes `type:"array"` or `type:"object"` fields from a callable recipe's `request_schema_json`. The platform does not return an error — it simply discards the nested definition and the datapill is unavailable downstream.

**Always flatten:** Every field in `request_schema_json` must be a scalar type (`string`, `integer`, `number`, `boolean`). If the source has an array of objects, pass it as a JSON string field and apply `.parse_json` inside the `each` loop source.

```python
# WRONG — silently wiped
{"name": "payments", "type": "array", "of": "object", ...}

# CORRECT — survives API round-trip
{"name": "payments", "type": "string", "optional": True,
 "hint": "Pass as JSON string; deserialized inside loop"}
```

### Rule 2 — toggleCfg is required on every action step
Every action step (any step with a `keyword` of `action`, `if`, `each`, `try`, `repeat`, `stop`) MUST include `"toggleCfg": {}`. Steps missing `toggleCfg` appear broken in the GUI — they show no configuration panel.

```python
# Minimum on any step
step = {
    "keyword": "action",
    "provider": "logger",
    ...
    "toggleCfg": {},   # required even if empty
    "input": {...}
}
```

### Rule 3 — dynamicPickListSelection is required on pick-list steps
Steps that configure operations using pick-list fields (oracle, salesforce, google_sheets, sftp, etc.) MUST include `"dynamicPickListSelection": {}`. Without it, the GUI shows the step as unconfigured even if `input` fields are correct.

```python
step = {
    "keyword": "action",
    "provider": "oracle",
    ...
    "dynamicPickListSelection": {},  # required even if empty
    "toggleCfg": {},
    "input": {...}
}
```

### Rule 4 — parameters_schema on callable trigger
`workato_service/receive_request` trigger steps require `"parameters_schema": ""` (empty string). Without it, the trigger schema editor in the GUI is broken.

```python
trigger = {
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    ...
    "parameters_schema": "",
    "input": {
        "request_schema_json": json.dumps([...flat fields...])
    }
}
```

### Rule 5 — rescue block placement
A `rescue` block (per-iteration catch) MUST be the last sibling inside `each.block` — not inside any `if`/`else` block that comes before it. The platform evaluates rescue as a special terminal sibling.

```python
each_step = {
    "keyword": "each",
    "block": [
        step_if,
        step_elsif,
        step_else,
        rescue_step   # LAST — after all if/elsif/else
    ]
}
```

### Rule 6 — catch block placement
A `catch` block MUST be the last sibling inside `try.block`. Same positional rule as rescue.

```python
try_step = {
    "keyword": "try",
    "block": [
        step_a,
        step_b,
        catch_step   # LAST — always
    ]
}
```

### Rule 7 — elsif keyword (not elseif, not nested)
Workato uses `"keyword": "elsif"` (no 'e' before 'i'). It is a flat sibling inside the parent `if` step's block — NOT nested inside an `else` block.

```python
if_step = {
    "keyword": "if",
    "block": [
        # if-true steps here
    ]
}
elsif_step = {
    "keyword": "elsif",   # NOT "elseif", NOT nested inside "else"
    "block": [...]
}
else_step = {
    "keyword": "else",
    "block": [...]
}
# All three are siblings in the parent block:
parent_block = [if_step, elsif_step, else_step]
```

### Rule 8 — folder creation API format
POST `/api/folders` requires a **flat** JSON body: `{"name": "...", "parent_id": INT}`. The wrapped format `{"folder": {"name": "...", "parent_id": INT}}` returns HTTP 400.

### Rule 9 — recipe create payload format
POST `/api/recipes` requires:
```python
payload = {
    "recipe": {
        "name": "Recipe Name",
        "folder_id": "31835141",   # STRING (not int) for folder_id in create
        "code": json.dumps(code_dict),     # JSON STRING (not dict)
        "config": json.dumps(config_list)  # JSON STRING (not list)
    }
}
```
`code` and `config` MUST be JSON strings — passing Python dicts causes a 422.

### Rule 10 — always GET before PUT
The PUT endpoint for `/api/recipes/:id` replaces the full recipe. Partial updates are not supported. Always:
1. GET `/api/recipes/:id` → parse `code` and `config` from response
2. Merge your changes on top
3. PUT the full merged payload

### Rule 11 — uuid on every step
Every step object MUST include a `"uuid"` field with a unique UUID4 string. Steps without UUIDs are rejected silently — the recipe may appear to save but steps will be missing in the GUI.

```python
import uuid
step["uuid"] = str(uuid.uuid4())
```

### Rule 12 — datapill path for current loop item
To reference the current item inside an `each` loop, use:
```python
{"path_element_type": "current_item"}
```
NOT the string `"*"` and NOT an index integer.

Full datapill reference example:
```python
datapill = "#{_dp('" + json.dumps({
    "pill_type": "output",
    "provider": "workato_service",
    "line": "trigger_alias",
    "path": [
        {"path_element_type": "key", "key": "payments"}
    ]
}) + "')}"
```

### Rule 13 — account_id type in config
`account_id` in the config array must be an **integer** or **null** — never a string. Oracle, Salesforce, SFTP, GSheets use integer IDs. HTTP, logger, workato_service, variables use `null`.

```python
config = [
    {"keyword": "application", "provider": "oracle",           "account_id": 19657520,  "skip_validation": False},
    {"keyword": "application", "provider": "workato_service",  "account_id": None,      "skip_validation": False},
    {"keyword": "application", "provider": "logger",           "account_id": None,      "skip_validation": False},
    {"keyword": "application", "provider": "http",             "account_id": None,      "skip_validation": False},
]
```

### Rule 14 — each and foreach are both accepted
Both `"keyword": "each"` and `"keyword": "foreach"` are accepted by the API. `"each"` is confirmed working and preferred in new recipes.

### Rule 15 — extended_output_schema on triggers
The `extended_output_schema` field on triggers defines which datapills are available to downstream steps in the GUI. If omitted, steps may show correct data at runtime but the GUI pill tree will be empty. Match field names and types from `request_schema_json`.

---

## Workato API Endpoints

Base URL: `https://www.workato.com/api` (or `WORKATO_BASE_URL` from .env)

| Operation | Method | Path |
|---|---|---|
| Get current user | GET | `/users/me` |
| List recipes | GET | `/recipes?folder_id=ID` |
| Get recipe | GET | `/recipes/:id` |
| Create recipe | POST | `/recipes` |
| Update recipe | PUT | `/recipes/:id` |
| List connections | GET | `/connections` |
| List folders | GET | `/folders` |
| Create folder | POST | `/folders` |
| List lookup tables | GET | `/lookup_tables` |

Authentication: `Authorization: Bearer <WORKATO_API_TOKEN>` header on every request.

---

## Recipe JSON Structure Overview

A complete recipe payload (the `code` dict before JSON-stringification):

```python
code = {
    "number": 0,
    "provider": "workato_service",   # primary provider (matches trigger)
    "name": "receive_request",       # trigger action name
    "as": "trigger_alias",           # alias for datapill references
    "keyword": "trigger",
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "uuid": str(uuid.uuid4()),
    "parameters_schema": "",         # required for callable triggers
    "input": {
        "request_schema_json": json.dumps([...flat schema fields...]),
        "response_schema_json": json.dumps([...response fields...]),
        "response_type": "json"
    },
    "extended_output_schema": [...], # datapill definitions for GUI
    "block": [                       # recipe steps (list)
        # step dicts
    ]
}
```

The `config` list (one entry per unique provider):
```python
config = [
    {
        "keyword": "application",
        "provider": "provider_name",
        "account_id": INT_OR_NULL,
        "skip_validation": False
    }
    # one per unique provider in the recipe
]
```

---

## Push Script Template

Every push script must follow this structure:

```python
#!/usr/bin/env python3
"""
Push script: <Recipe Name>
Folder: <Folder Name> (folder_id: XXXXX)
Account: <email>

Placeholders requiring manual GUI wiring:
  - [CONNECTION_NAME]: replace with real connection in Workato GUI
  - [ENDPOINT_URL]: obtain real URL from SME
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
RECIPE_ID    = None       # Set to existing ID for updates; None for new
FOLDER_ID    = "31835141" # string for create
RECIPE_NAME  = "My Recipe"
DRY_RUN      = "--dry-run" in sys.argv

# ── Auth ─────────────────────────────────────────────────────────────────────
def load_env():
    env_path = Path(__file__).parent
    for _ in range(5):
        candidate = env_path / ".env"
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
            return
        env_path = env_path.parent
    raise RuntimeError(".env not found in ancestor directories")

load_env()
TOKEN    = os.environ.get("WORKATO_API_TOKEN", "")
BASE_URL = os.environ.get("WORKATO_BASE_URL", "https://www.workato.com/api")
if not TOKEN:
    sys.exit("ERROR: WORKATO_API_TOKEN not set in .env")

def api(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type",  "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {method} {path}: {e.read().decode()}")

# ── Recipe definition ────────────────────────────────────────────────────────
def make_step(keyword, provider, name, alias, input_data, block=None,
              dpls=None, toggles=None):
    s = {
        "keyword": keyword,
        "provider": provider,
        "name": name,
        "as": alias,
        "uuid": str(uuid.uuid4()),
        "dynamicPickListSelection": dpls or {},
        "toggleCfg": toggles or {},
        "input": input_data,
    }
    if block is not None:
        s["block"] = block
    return s

config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None, "skip_validation": False},
    # add more providers as needed
]

trigger = {
    "number": 0,
    "provider": "workato_service",
    "name": "receive_request",
    "as": "trigger",
    "keyword": "trigger",
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "uuid": str(uuid.uuid4()),
    "parameters_schema": "",
    "input": {
        "request_schema_json": json.dumps([
            {"name": "fieldA", "type": "string", "optional": False}
        ]),
        "response_schema_json": json.dumps([
            {"name": "status", "type": "string"}
        ]),
        "response_type": "json"
    },
    "extended_output_schema": [
        {"name": "fieldA", "type": "string", "label": "Field A"}
    ],
    "block": [
        # steps go here
    ]
}

code   = trigger
payload = {
    "recipe": {
        "name": RECIPE_NAME,
        "folder_id": FOLDER_ID,
        "code":   json.dumps(code),
        "config": json.dumps(config)
    }
}

# ── Push ─────────────────────────────────────────────────────────────────────
if DRY_RUN:
    print("=== DRY RUN — recipe payload ===")
    print(json.dumps(payload, indent=2))
elif RECIPE_ID:
    # Update: GET → merge → PUT
    current = api("GET", f"/recipes/{RECIPE_ID}")
    payload["recipe"].pop("folder_id", None)  # can't change folder on PUT
    result = api("PUT", f"/recipes/{RECIPE_ID}", payload)
    print(f"Updated recipe {RECIPE_ID}: {result.get('name')}")
else:
    result = api("POST", "/recipes", payload)
    print(f"Created recipe ID: {result['id']}  name: {result['name']}")
```

---

## Workflow for New Recipe Builds

Follow this order every time — never skip steps.

1. **Read WORKATO_THINKING.md** — load mental models before writing any code.
2. **Discover connections** — run `workato-connection-list.py` and note real `account_id` values.
3. **Identify trigger type** — callable, scheduled, or event-based.
4. **Design flat schema** — apply Rule 1 (flatten). No nested objects/arrays in trigger schema.
5. **Sketch step tree** — top-down outline: trigger → outer try → each loop → if/elsif/else branches → rescue → catch → send_reply.
6. **Read component refs** — open the relevant `recipe_components/*.md` for each step type.
7. **Write push script** — Python script with `--dry-run` support.
8. **Run dry-run first** — inspect payload for structural issues before hitting the API.
9. **Push and verify** — run without `--dry-run`, open Workato GUI and confirm all steps visible.
10. **Note manual wiring** — document any steps that need GUI configuration (connections, pills, SP names).

---

## Workflow for Updating Existing Recipes

1. Run `workato-recipe-pull.py --recipe-id ID --output current.json` to capture current state.
2. Inspect `current.json` — understand existing step UUIDs and structure.
3. Merge your changes (preserve UUIDs of steps you are not changing).
4. Run `workato-recipe-push.py --recipe-id ID --code-file updated_code.json`.

Never PUT without first GETting. Treat the GET as a contract.

---

## Common Push Failures and Fixes

| Symptom | Root Cause | Fix |
|---|---|---|
| Step missing in GUI after push | Missing `uuid` on step | Add `str(uuid.uuid4())` to every step |
| GUI shows step as unconfigured | Missing `toggleCfg` | Add `"toggleCfg": {}` |
| Pick-list step shows blank | Missing `dynamicPickListSelection` | Add `"dynamicPickListSelection": {}` |
| Callable trigger schema empty | Nested array/object in schema | Flatten all fields (Rule 1) |
| 422 on recipe create | `code`/`config` are dicts not strings | `json.dumps(code)`, `json.dumps(config)` |
| 400 on folder create | Wrapped `{"folder": {...}}` body | Use flat `{"name": "...", "parent_id": INT}` |
| Rescue runs on wrong iteration | `rescue` not last in `each.block` | Move rescue to final sibling position |
| `catch` block not triggered | `catch` not last in `try.block` | Move catch to final sibling position |
| Datapill shows nil at runtime | Wrong pill path or wrong loop alias | Use `{"path_element_type": "current_item"}` for loop item |
| Connection not found | Wrong `account_id` type (string) | Use integer account_id (Rule 13) |
| `elsif` not recognized | Typo `elseif` or nesting | Use `"keyword": "elsif"` as flat sibling (Rule 7) |

---

## Integration with Migration Workflow

When this skill is active inside a webMethods → Workato (or any → Workato) migration:

- Phase 1–4 produce `migration-specs/<project>.json` and analysis docs.
- Phase 5 (GENERATE) uses this skill to build the push script.
- The push script reads from the migration spec and RecipeComponents references.
- Canonical RecipeComponents are in `Workato/RecipeComponents/` at the workspace root.
- After every push, update `migration-specs/<project>_progress.md` with pushed recipe IDs.

### RecipeComponents canonical reference location
```
Workato/RecipeComponents/
├── NewRecipe.json
├── IF-ELSE.json
├── Variables.json
├── For Each.json
├── forEach.json
├── repeatWhile.json
├── datapill.json
├── SFTP.json
├── Email.json
├── Log.json
├── HTTP.json
└── googlesheet connection.json
```

These JSONs are confirmed-working fragments pulled from live Workato recipes. When building a new recipe, copy the relevant fragment and adapt field values rather than writing from scratch.

---

## Account Context

| Account | Email | Notes |
|---|---|---|
| Primary training | manish@techstonellc.com | WebMethodsMigration folder: 31661117, migrAIte_Training: 31835141 |

Folder IDs are integers in the API but strings in recipe create payload (`"folder_id": "31835141"`).

Active recipe IDs are tracked in `CLAUDE.md` under each migration entry. Always check there before creating a new recipe to avoid duplicates.

---

## Credential Access

The agent cannot read `.env` directly (blocked by project settings). Scripts load credentials via Python's own file parsing in `workato-common.py`. Do not attempt to `cat .env` or use bash to source it. Run `workato-env-check.py` instead.
