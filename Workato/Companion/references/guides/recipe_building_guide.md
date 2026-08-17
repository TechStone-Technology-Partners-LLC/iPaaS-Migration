# Recipe Building Guide

End-to-end walkthrough for building and pushing a Workato recipe via the REST API.

---

## Step 1 — Determine the Trigger Type

| Scenario | Trigger |
|----------|---------|
| Called from another recipe or external HTTP | `workato_service / receive_request` (callable) |
| Runs on a schedule | `scheduled_event / timer` |
| Fires on a Salesforce record event | `salesforce / new_sobject` or similar |
| Fires on an SFTP file arrival | `sftp / new_file` |

For most migration recipes, use **callable** — it lets you test from Postman and wire
later to whatever event source the business uses.

---

## Step 2 — Design a Flat Trigger Schema

The flatten rule: **never nest objects inside `request_schema_json`**.
Nested objects cause steps to be invisible in the Workato GUI even though the recipe
technically runs. Always flatten to a list of scalar fields.

For arrays (e.g. a list of payments), accept the array as a **JSON string** field and
parse it inside the `each` step with `.parse_json`.

```python
# Good — flat scalars + one JSON-string array
request_schema = [
    {"name": "customerId",    "type": "string",  "optional": False, "control_type": "text",   "label": "Customer ID"},
    {"name": "customerName",  "type": "string",  "optional": False, "control_type": "text",   "label": "Customer Name"},
    {"name": "amount",        "type": "number",  "optional": True,  "control_type": "number", "label": "Amount"},
    {"name": "payments",      "type": "string",  "optional": True,  "control_type": "text",   "label": "Payments JSON"},
]

# Bad — nested object causes GUI invisibility
request_schema = [
    {"name": "applicationInfo", "type": "object", "properties": [...]}  # DO NOT DO THIS
]
```

---

## Step 3 — Sketch the Step Tree

Before writing code, draw the block hierarchy:

```
trigger (block=[
  try (block=[
    each payments (block=[
      if type==Check (block=[...])
      elsif type==ACH (block=[...])
      else (block=[...])
      rescue (block=[log_error])   # MUST be last in each.block
    ])
    send_reply
    catch (block=[log_error])      # MUST be last in try.block
  ])
])
```

Number steps sequentially starting from 1 (trigger is 0).
Assign a unique `as` alias to every step — datapills reference this alias.

---

## Step 4 — Write the Push Script

### Skeleton

```python
import json, requests
from uuid import uuid4

WORKATO_TOKEN = "your-api-token"
WORKATO_EMAIL = "you@example.com"
FOLDER_ID = 12345678   # get from workato-folder-list.py

HEADERS = {
    "x-user-token": WORKATO_TOKEN,
    "x-user-email": WORKATO_EMAIL,
    "Content-Type": "application/json"
}

def dp(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    pill = json.dumps({"pill_type": "output", "provider": provider, "line": line,
                       "path": path}).replace('"', '\\"')
    return "#{_dp('" + pill + "')}"

TRIG = "receive_payment_request"   # trigger alias — all datapills start here

# --- Build steps (bottom-up: deepest nesting first) ---

step_log_error = {
    "number": 5,
    "keyword": "action",
    "provider": "logger",
    "name": "create_message",
    "as": "log_error",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {"message": "Error occurred", "level": "error"}
}

step_rescue = {
    "number": 4,
    "keyword": "rescue",
    "uuid": str(uuid4()),
    "block": [step_log_error]
}

step_each = {
    "number": 3,
    "keyword": "each",
    "as": "payment_loop",
    "uuid": str(uuid4()),
    "input": {"source": dp("workato_service", TRIG, "payments") + ".parse_json"},
    "block": [step_rescue]
}

step_reply = {
    "number": 2,
    "keyword": "action",
    "provider": "workato_service",
    "name": "send_reply",
    "as": "send_reply_step",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {"reply.status": True},
    "input": {"reply_type": "success", "reply": {"status": "COMPLETED"}},
    "extended_input_schema": [{"label": "Reply", "name": "reply", "type": "object",
        "properties": [{"control_type": "text", "label": "Status",
                        "name": "status", "type": "string", "optional": False}]}]
}

step_catch = {
    "number": 6,
    "keyword": "catch",
    "uuid": str(uuid4()),
    "input": {"max_retry_count": "0", "retry_interval": "2"},
    "block": [step_log_error]
}

step_try = {
    "number": 1,
    "keyword": "try",
    "uuid": str(uuid4()),
    "input": {},
    "block": [step_each, step_reply, step_catch]   # catch LAST
}

trigger = {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    "as": TRIG,
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "parameters_schema": "",
    "input": {
        "service_name": "PaymentService",
        "request_schema_json": json.dumps([
            {"name": "customerId", "type": "string", "optional": False,
             "control_type": "text", "label": "Customer ID"},
            {"name": "payments", "type": "string", "optional": True,
             "control_type": "text", "label": "Payments JSON"}
        ]),
        "reply_schema_json": json.dumps([
            {"name": "status", "type": "string", "optional": False,
             "control_type": "text", "label": "Status"}
        ])
    },
    "block": [step_try]
}

config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None, "skip_validation": False},
    {"keyword": "application", "provider": "logger",
     "account_id": None, "skip_validation": False},
]

payload = {
    "recipe": {
        "name": "My Payment Recipe",
        "folder_id": str(FOLDER_ID),
        "code": json.dumps(trigger),
        "config": json.dumps(config)
    }
}

# POST to create
resp = requests.post(
    "https://www.workato.com/api/recipes",
    headers=HEADERS,
    json=payload
)
print(resp.status_code, resp.json())
recipe_id = resp.json()["id"]
print(f"Recipe ID: {recipe_id}")
```

---

## Step 5 — Run and Verify

```bash
python scripts/push_my_recipe.py
```

Expected output:
```
201 {'id': 73XXXXXX, 'name': 'My Payment Recipe', ...}
Recipe ID: 73XXXXXX
```

Open the Workato GUI: the recipe appears in the target folder with all steps visible.
Check the step tree in the canvas matches the sketch from Step 3.

---

## Step 6 — Update an Existing Recipe

Read the current state first (required — otherwise PUT returns 400):

```python
GET_RESP = requests.get(f"https://www.workato.com/api/recipes/{RECIPE_ID}", headers=HEADERS)
current = GET_RESP.json()

# Modify payload
payload = {
    "recipe": {
        "name": current["name"],
        "code": json.dumps(new_trigger),
        "config": json.dumps(new_config)
    }
}

requests.put(f"https://www.workato.com/api/recipes/{RECIPE_ID}", headers=HEADERS, json=payload)
```

---

## POST Payload Format

```json
{
  "recipe": {
    "name": "Recipe display name",
    "folder_id": "12345678",
    "code": "<trigger JSON string>",
    "config": "<config array JSON string>"
  }
}
```

- `code` is the entire trigger (with all steps nested in its `block`) serialised as a JSON string.
- `config` is the config array serialised as a JSON string.
- `folder_id` must be a **string**, not an integer.
