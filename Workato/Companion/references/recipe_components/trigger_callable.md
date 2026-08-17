# Trigger: workato_service / receive_request (Callable Recipe)

A callable recipe trigger exposes the recipe as an HTTP endpoint. Other recipes or
external callers (HTTP POST) can invoke it synchronously and receive a reply.

---

## Complete Python Code

```python
import json
from uuid import uuid4

TRIG = "receive_my_request"  # alias — referenced in all datapills

request_schema = [
    {"name": "id",           "type": "string",  "optional": False, "control_type": "text",   "label": "ID"},
    {"name": "customerName", "type": "string",  "optional": False, "control_type": "text",   "label": "Customer Name"},
    {"name": "customerId",   "type": "string",  "optional": False, "control_type": "text",   "label": "Customer ID"},
    {"name": "amount",       "type": "number",  "optional": True,  "control_type": "number", "label": "Amount"},
    {"name": "active",       "type": "boolean", "optional": True,  "control_type": "checkbox","label": "Active"},
    {"name": "payments",     "type": "string",  "optional": True,  "control_type": "text",   "label": "Payments JSON"},
]

reply_schema = [
    {"name": "status",  "type": "string", "optional": False, "control_type": "text", "label": "Status"},
    {"name": "message", "type": "string", "optional": True,  "control_type": "text", "label": "Message"},
]

trigger = {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    "as": TRIG,
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "parameters_schema": "",      # REQUIRED — must be empty string, not omitted
    "input": {
        "service_name": "MyService",
        "request_schema_json": json.dumps(request_schema),
        "reply_schema_json": json.dumps(reply_schema)
    },
    "block": [...]   # all recipe steps go here
}
```

---

## Schema Field Types

| `type` value | `control_type` value | Used for |
|-------------|---------------------|----------|
| `"string"`  | `"text"`            | Text fields, IDs, names, JSON strings |
| `"integer"` | `"integer"`         | Whole numbers |
| `"number"`  | `"number"`          | Decimal / float values |
| `"boolean"` | `"checkbox"`        | True/False flags |
| `"string"`  | `"text"`            | Array passed as JSON string |

**Important:** Do not use `"type": "object"` or `"type": "array"` in `request_schema_json`.
These cause the recipe steps to be invisible in the Workato GUI (flatten rule).

---

## The Flatten Rule

If the source system has a nested structure like:
```json
{"applicationInfo": {"customerId": "123", "customerName": "Acme"}, "payments": [...]}
```

Flatten it to scalar fields at the trigger level:
```json
{"applicationInfo_customerId": "123", "applicationInfo_customerName": "Acme", "payments": "...json string..."}
```

Arrays are passed as a JSON-encoded string and parsed inside the `each` step:
```python
{"name": "payments", "type": "string", "optional": True, "control_type": "text", "label": "Payments JSON"}
```

---

## parameters_schema Requirement

The `parameters_schema` key must be present and set to an empty string `""`.
If omitted, Workato may reject the recipe or fail to render the trigger schema in the GUI.

---

## Accessing Trigger Fields (Datapills)

```python
def dp(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    pill = json.dumps({"pill_type": "output", "provider": provider, "line": line,
                       "path": path}).replace('"', '\\"')
    return "#{_dp('" + pill + "')}"

# Access trigger fields:
dp("workato_service", TRIG, "customerName")
dp("workato_service", TRIG, "amount")
dp("workato_service", TRIG, "payments")   # raw JSON string — use .parse_json in each
```

---

## Config Entry

```python
config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None, "skip_validation": False},
    # ... other providers ...
]
```

`workato_service` always uses `account_id: None` — no stored connection required.

---

## extended_output_schema

If downstream recipe components need to read the trigger's output schema, add:

```python
"extended_output_schema": [
    {"name": f["name"], "type": f["type"],
     "control_type": f["control_type"], "label": f["label"]}
    for f in request_schema
]
```

This is usually not needed for push-script-built recipes, but may be required for
recipe functions that call this callable recipe.
