# Workato Thinking — Core Mental Models

Read this file before building any recipe. These mental models are the foundation that the rest of the skill references build on. If you skip this file, you will make structural mistakes that are invisible until the recipe fails silently in the GUI.

---

## Mental Model 1 — Recipe as a Pipeline

A Workato recipe is a linear pipeline with a single entry point:

```
trigger → [step, step, step, ...] → (optional) send_reply
```

The trigger fires once per event. Everything flows forward — there is no back-edge, no loop that spans the trigger boundary. Control constructs (each, if, try) are **nested blocks**, not separate threads.

Every recipe has two top-level structures in the API:
- `code` — the recipe's step tree (JSON, sent as a string in the API payload)
- `config` — the connection registry (JSON, sent as a string in the API payload)

The trigger is the **root node** of `code`. Steps live in its `block` array.

### Anatomy of a complete recipe node

```python
{
    "number": 0,                        # trigger is always 0; steps increment
    "keyword": "trigger",               # or "action", "if", "each", "try", etc.
    "provider": "workato_service",      # connector provider slug
    "name": "receive_request",          # action/trigger name within provider
    "as": "trigger",                    # alias — used in datapill references
    "uuid": "550e8400-...",             # UUID4, unique per step — REQUIRED
    "dynamicPickListSelection": {},     # REQUIRED — even if empty
    "toggleCfg": {},                    # REQUIRED on all non-trigger steps — even if empty
    "parameters_schema": "",            # REQUIRED on workato_service trigger only
    "input": {                          # provider-specific configuration
        "request_schema_json": "...",   # JSON string (not dict) for callable triggers
        "response_schema_json": "...",
        "response_type": "json"
    },
    "extended_output_schema": [...],    # datapill definitions for GUI (triggers only)
    "block": [                          # child steps — present on triggers + control flow
        # ... step dicts
    ]
}
```

Every field matters. Omitting `uuid`, `toggleCfg`, or `dynamicPickListSelection` causes silent failures — the platform accepts the push but the step renders broken in the GUI.

---

## Mental Model 2 — Step Anatomy in Detail

A non-trigger action step has this structure:

```python
{
    "keyword": "action",
    "provider": "oracle",
    "name": "execute_stored_procedure",
    "as": "log_check_request",          # unique alias across the recipe
    "uuid": str(uuid.uuid4()),           # unique UUID4
    "dynamicPickListSelection": {        # required; pre-selections for pick-list fields
        "stored_procedure": "GLD_ACH.INSERTPAYMENT"
    },
    "toggleCfg": {                       # required; toggle overrides (usually empty)
        "batch_mode": False
    },
    "input": {                           # all step parameters go here
        "stored_procedure": "GLD_ACH.INSERTPAYMENT",
        "input": [                       # for Oracle: array of param bindings
            {
                "name": "APP_ID",
                "type": "string",
                "value": "#{_dp('...')}"  # datapill or literal
            }
        ]
    }
    # No "block" key on leaf action steps
}
```

**Alias (`as`) rules:**
- Must be unique within the recipe — two steps with the same alias cause unpredictable pill resolution
- Used verbatim in datapill `line` field — keep it short and descriptive
- Conventional pattern: `snake_case` matching the step's purpose

**`number` field:** Optional on steps (only required on trigger as `0`). If included, it must be sequential. Safest to omit on non-trigger steps and let the platform assign.

---

## Mental Model 3 — Datapill as a Reference

A datapill is a runtime reference to a value produced by an earlier step. In the recipe JSON it is encoded as a template string:

```
"#{_dp('JSON_ENCODED_PILL_OBJECT')}"
```

The pill object has this shape:

```python
{
    "pill_type": "output",          # always "output"
    "provider": "workato_service",  # provider of the step that produces this value
    "line": "trigger",              # the "as" alias of the producing step
    "path": [                       # navigation path through the output schema
        {"path_element_type": "key", "key": "payments"}
    ]
}
```

**Path element types:**

| Type | Usage | JSON |
|---|---|---|
| `key` | Navigate to a named field | `{"path_element_type": "key", "key": "fieldName"}` |
| `current_item` | Current iteration item inside `each` loop | `{"path_element_type": "current_item"}` |
| `index` | Numeric array index (rarely used) | `{"path_element_type": "index", "index": 0}` |

**Building a datapill in Python:**

```python
import json

def datapill(provider, alias, *path_keys, loop_item=False):
    """Build a #{_dp('...')} datapill string."""
    path = []
    for k in path_keys:
        path.append({"path_element_type": "key", "key": k})
    if loop_item:
        path.append({"path_element_type": "current_item"})
    pill = {
        "pill_type": "output",
        "provider": provider,
        "line": alias,
        "path": path
    }
    return "#{_dp('" + json.dumps(pill, separators=(',', ':')) + "')}"

# Examples:
# Field from trigger:
trigger_payments = datapill("workato_service", "trigger", "payments")

# Current loop item inside an each loop (alias "payment_loop"):
current_payment = datapill("workato_service", "payment_loop", loop_item=True)

# Nested field on current item:
payment_type = datapill("workato_service", "payment_loop", "type")
# (path: [{key: "type"}] — the current_item context is implicit inside the loop)
```

**String concatenation in inputs:**
```python
"value": f"Hello #{_dp('...')} World"
# Multiple pills can appear in a single string value
```

---

## Mental Model 4 — Config Array

The `config` array is the connection registry for the recipe. One entry per unique provider used anywhere in the recipe (trigger or steps). Missing a provider causes a 422 on push.

```python
config = [
    {
        "keyword": "application",
        "provider": "workato_service",  # callable trigger provider
        "account_id": None,             # null for system providers
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "oracle",
        "account_id": 19657520,         # integer ID from Workato GUI
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "logger",
        "account_id": None,
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "http",
        "account_id": None,             # HTTP uses null (connection configured per-step)
        "skip_validation": False
    }
]
```

**account_id rules:**
- Must be an integer or `None` (null) — never a string
- `None`: workato_service, logger, http, variables (no user-owned connection needed)
- Integer: oracle, salesforce, google_sheets, sftp, email, and all user-managed connectors
- Get real IDs by running: `python Workato/Companion/scripts/workato-connection-list.py`

The `config` is sent to the API as `json.dumps(config)` — a string, not a list.

---

## Mental Model 5 — Control Flow Constructs

### if / elsif / else

`if`, `elsif`, and `else` are **flat siblings** inside their parent block. They are NOT nested inside each other.

```
parent_block = [
    { keyword: "if",     condition: ..., block: [...true_steps...] },
    { keyword: "elsif",  condition: ..., block: [...elsif_steps...] },
    { keyword: "else",   block: [...else_steps...] }
]
```

The `condition` field structure:
```python
"condition": {
    "operand_1": datapill("workato_service", "payment_loop", "type"),
    "operator":  "==",
    "operand_2": "Check"
}
```

Operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `contains`, `starts_with`, `ends_with`, `is_present`, `is_not_present`

### try / catch

`try` wraps steps that may fail. `catch` is the LAST sibling inside `try.block`.

```python
try_step = {
    "keyword": "try",
    "block": [
        step_a,
        step_b,
        {
            "keyword": "catch",
            "block": [...error_handling_steps...]
        }
    ]
}
```

### each / foreach (loop)

`each` iterates over an array. `rescue` (per-iteration catch) is the LAST sibling inside `each.block`.

```python
each_step = {
    "keyword": "each",
    "input": {
        "source": datapill_to_array,  # the array to iterate
        "type": "array"
    },
    "as": "payment_loop",             # alias for current item
    "block": [
        step_if,
        step_elsif,
        step_else,
        {
            "keyword": "rescue",      # LAST — per-iteration error handler
            "block": [...error_steps...]
        }
    ]
}
```

When the array is passed as a JSON string (Rule 1 — flatten), apply `.parse_json` in the source:
```python
"input": {
    "source": f"{datapill_to_string}.parse_json",
    "type": "array"
}
```

### repeat / while_condition

Repeat-until loop: executes block, then checks condition. Stops when condition is true.

```python
repeat_step = {
    "keyword": "repeat",
    "as": "repeat_loop",
    "block": [
        ...body_steps...,
        {
            "keyword": "while_condition",
            "condition": {...}  # stop when this is true
        }
    ]
}
```

### stop

Terminates recipe execution immediately. No `block`.

```python
stop_step = {
    "keyword": "stop",
    "uuid": str(uuid.uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "stop_type": "success"  # or "error"
    }
}
```

---

## Mental Model 6 — Trigger Types

### Callable recipe (workato_service/receive_request)

Invoked by another recipe or via HTTP POST. Input schema defined in `request_schema_json`. Response schema in `response_schema_json`. Always ends with a `workato_service/send_reply` step.

```python
{
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    "as": "trigger",
    "parameters_schema": "",           # REQUIRED — empty string
    "input": {
        "request_schema_json":  json.dumps([...flat_input_fields...]),
        "response_schema_json": json.dumps([...flat_output_fields...]),
        "response_type": "json"
    },
    "extended_output_schema": [...]    # datapill definitions matching request_schema_json
}
```

### Scheduled trigger (scheduled_event/timer)

```python
{
    "keyword": "trigger",
    "provider": "scheduled_event",
    "name": "timer",
    "as": "trigger",
    "input": {
        "interval":  "1",
        "time_unit": "days",          # "minutes", "hours", "days"
        "start_time": "2026-01-01T00:00:00.000-05:00"
    },
    "extended_output_schema": []
}
```

### Event trigger (provider-specific)

Each connector defines its own event trigger (e.g., salesforce/new_updated_object, sftp/new_file). Consult the relevant `trigger_*.md` in `recipe_components/`.

---

## Mental Model 7 — The Flatten Rule (Critical)

Workato's callable recipe trigger schema editor silently discards any field with `"type": "array"` or `"type": "object"`. The platform:
- Does NOT return an error
- Does NOT warn in the GUI
- Simply omits the field from the stored schema
- Makes the datapill unavailable to downstream steps

**The fix: always flatten.**

| Source shape | Do this instead |
|---|---|
| Array of objects (e.g., `payments[]`) | Pass as `"type": "string"`, add hint "Pass as JSON string". Apply `.parse_json` as the `each` loop source. |
| Nested object (e.g., `applicationInfo.customerId`) | Flatten to top-level `"applicationInfo_customerId": "string"` |
| Complex typed fields | Use string and document the expected format in `hint` |

**Example:**
```python
# WRONG — payments field will be silently wiped:
request_schema = [
    {"name": "payments", "type": "array", "of": "object", "properties": [...]}
]

# CORRECT — survives round-trip:
request_schema = [
    {"name": "applicationInfo_customerName", "type": "string", "optional": False},
    {"name": "applicationInfo_customerId",   "type": "string", "optional": False},
    {"name": "payments", "type": "string", "optional": False,
     "hint": "JSON string: array of payment objects. Deserialized inside loop."}
]
```

Inside the recipe, the `each` loop source applies `.parse_json`:
```python
"input": {
    "source": datapill("workato_service", "trigger", "payments") + ".parse_json",
    "type": "array"
}
```

---

## Mental Model 8 — The Connection Rule

Every non-null `account_id` in the `config` array must be the integer ID of an existing, authorized Workato connection in the account. Using a wrong ID causes the recipe to appear saved but all steps using that connection will fail at runtime.

**Before generating any recipe code:**
1. Run `workato-connection-list.py` and record the `id` column
2. Match each provider in your recipe to the correct connection ID
3. Hard-code the integer IDs in the push script

If the connection doesn't exist yet, document it in the push script's header comment as "manual GUI step: create connection, then update RECIPE_ID and re-run."

---

## Mental Model 9 — Build Order

Never free-form build. Always follow this sequence:

```
1. Determine trigger type
   └── callable → read trigger_callable.md + send_reply.md
   └── scheduled → read trigger_scheduled.md

2. Design flat schema (apply Rule 1 — flatten everything)
   └── List all input fields as scalars
   └── List all output fields for send_reply

3. Sketch step tree top-down (on paper or as comments)
   trigger
   └── try (outer)
       ├── each over payments
       │   ├── if type=="Check" → ...
       │   ├── elsif type=="ACH" → ...
       │   ├── else → ...
       │   └── rescue → log_error
       └── catch → log_system_error
   send_reply

4. Read component refs for each node type
   └── control_foreach.md, control_if_else.md, control_try_catch.md, action_oracle.md

5. Write push script (Python, stdlib only, --dry-run flag)

6. Run --dry-run, inspect JSON structure

7. Push and open GUI to verify all steps are visible and wired

8. Document manual wiring steps (connections, pills, SPs that need GUI touch)
```

---

## Mental Model 10 — Recipe Update Discipline

The Workato PUT endpoint for `/api/recipes/:id` performs a **full replacement** — it is not a partial update or patch. If you PUT without including existing steps, those steps are deleted.

**Always:**
```python
# Step 1: Read current state
response = api("GET", f"/recipes/{RECIPE_ID}")
current_code   = json.loads(response["code"])
current_config = json.loads(response["config"])

# Step 2: Merge your changes onto current
# (add/replace steps by UUID, append new config entries, etc.)

# Step 3: PUT the full merged payload
api("PUT", f"/recipes/{RECIPE_ID}", {
    "recipe": {
        "code":   json.dumps(merged_code),
        "config": json.dumps(merged_config)
    }
})
```

Treat the GET response as a contract. If step UUIDs change between GET and PUT, the GUI will show duplicate or orphaned steps. Preserve UUIDs of unchanged steps.

---

## Quick Reference — Required Fields by Step Type

| Step type | Required beyond keyword/provider/name/as/uuid |
|---|---|
| Any action | `toggleCfg`, `dynamicPickListSelection`, `input` |
| Callable trigger | `parameters_schema: ""`, `toggleCfg`, `dynamicPickListSelection`, `input`, `extended_output_schema` |
| Scheduled trigger | `toggleCfg`, `dynamicPickListSelection`, `input`, `extended_output_schema` |
| `if` / `elsif` | `toggleCfg`, `dynamicPickListSelection`, `condition`, `block` |
| `else` | `toggleCfg`, `dynamicPickListSelection`, `block` (no condition) |
| `each` | `toggleCfg`, `dynamicPickListSelection`, `input` (source + type), `block` |
| `try` | `toggleCfg`, `dynamicPickListSelection`, `block` |
| `catch` | `toggleCfg`, `dynamicPickListSelection`, `block` (must be last in try.block) |
| `rescue` | `toggleCfg`, `dynamicPickListSelection`, `block` (must be last in each.block) |
| `stop` | `toggleCfg`, `dynamicPickListSelection`, `input` (stop_type) |
| `repeat` | `toggleCfg`, `dynamicPickListSelection`, `block` (ends with `while_condition`) |

---

## Worked Example — Minimal Callable Recipe

```python
import json, uuid

def uid(): return str(uuid.uuid4())

config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None, "skip_validation": False},
    {"keyword": "application", "provider": "logger",
     "account_id": None, "skip_validation": False},
]

log_step = {
    "keyword": "action",
    "provider": "logger",
    "name": "log_message",
    "as": "log_receipt",
    "uuid": uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "message": "Received: #{_dp('" + json.dumps({
            "pill_type": "output",
            "provider": "workato_service",
            "line": "trigger",
            "path": [{"path_element_type": "key", "key": "fieldA"}]
        }, separators=(',',':')) + "')}"
    }
}

send_reply = {
    "keyword": "action",
    "provider": "workato_service",
    "name": "send_reply",
    "as": "send_reply",
    "uuid": uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "reply_body_json": json.dumps({"status": "OK"})
    }
}

code = {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    "as": "trigger",
    "uuid": uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
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
    "block": [log_step, send_reply]
}

payload = {
    "recipe": {
        "name": "Minimal Callable Recipe",
        "folder_id": "31835141",
        "code": json.dumps(code),
        "config": json.dumps(config)
    }
}
```

This is a correct, pushable recipe. Every required field is present. Use it as the skeleton for any new callable recipe.
