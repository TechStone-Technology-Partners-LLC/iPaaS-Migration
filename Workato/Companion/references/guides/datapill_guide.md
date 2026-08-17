# Datapill Guide

Datapills are Workato's way of referencing output from a previous step or trigger inside
the `input` field of a later step. They appear as `#{_dp('...')}` tokens inside string
values. The inner payload is a JSON object serialised and then backslash-escaped.

---

## 1. JSON Structure

```json
{
  "pill_type": "output",
  "provider": "<provider>",
  "line": "<step_alias>",
  "path": [<path_element>, ...]
}
```

| Field | Description |
|-------|-------------|
| `pill_type` | Always `"output"` for step-output pills |
| `provider` | Provider name of the step being referenced (e.g. `"workato_service"`, `"oracle"`) |
| `line` | The `as` alias of the step being referenced |
| `path` | Array of path elements (strings or `{"path_element_type": "current_item"}`) |

---

## 2. Python Helper Function

```python
import json

def dp(provider, line, *path_parts):
    """Build a Workato datapill reference string."""
    path = [
        {"path_element_type": "current_item"} if p == "*" else p
        for p in path_parts
    ]
    pill = json.dumps({
        "pill_type": "output",
        "provider": provider,
        "line": line,
        "path": path
    }).replace('"', '\\"')
    return "#{_dp('" + pill + "')}"
```

Call as: `dp("workato_service", "trigger_alias", "field_name")`

---

## 3. Accessing Trigger Fields

The trigger `as` alias is declared in the trigger step. For a callable trigger with alias
`"receive_funding_request"`:

```python
# Access a top-level trigger field
dp("workato_service", "receive_funding_request", "applicationInfo_customerName")

# Access a nested field (if not flattened)
dp("workato_service", "receive_funding_request", "applicationInfo", "customerName")
```

**Flatten rule:** Nested trigger schemas cause recipe steps to be invisible in the GUI.
Always use a flat list of `name` fields (no nested objects in `request_schema_json`).
If the source has nested data, flatten at trigger level and accept a JSON string for
array fields — use `.parse_json` in each steps.

---

## 4. Accessing Step Output Fields

Given an Oracle SP step with alias `"log_check_request"`:

```python
# Access output field ACCCHECKREQUESTID
dp("oracle", "log_check_request", "ACCCHECKREQUESTID")
```

Given a SELECT step with alias `"get_customer"` that returns an array:

```python
# Access a field on the first row (Workato returns array; GUI handles iteration)
dp("oracle", "get_customer", "rows", "0", "CUSTOMER_NAME")
```

---

## 5. The `current_item` Pattern

When iterating with `each`, each iteration's current item is referenced with the
`path_element_type: "current_item"` sentinel — represented as `"*"` in the helper:

```python
# Inside an each loop with alias "payment_loop" iterating a payments array
# Reference the "type" field of the current payment item
dp("workato_service", "receive_funding_request", "payments", "*", "type")

# If payments is a parsed JSON string alias:
# Use the each step's own alias as the datapill "line"
dp("each_step_provider", "payment_loop", "*", "type")
```

In practice for the callable trigger pattern where payments is a JSON string parsed
inside the `each` input, the current item path resolves against the parsed structure:

```python
each_step = {
    "keyword": "each",
    "as": "payment_loop",
    "input": {
        "source": dp("workato_service", "trigger_alias", "payments") + ".parse_json"
    },
    "block": [...]
}

# Inside block — current item field "amount":
dp("workato_service", "payment_loop", "*", "amount")
```

---

## 6. `.parse_json` for String→Array

When a trigger field carries a JSON array as a string (e.g. `payments`), append
`.parse_json` directly to the datapill string:

```python
source_value = dp("workato_service", "trigger_alias", "payments") + ".parse_json"
```

The `each` step's `input.source` accepts this combined string. Workato evaluates
`.parse_json` at runtime and iterates the resulting array.

---

## 7. `presence ||` for OR / Fallback

To provide a fallback when a field may be blank:

```python
# Returns field1 if present, otherwise "default_value"
value = dp("workato_service", "trigger_alias", "field1") + ".presence || 'default_value'"
```

This is Workato formula syntax embedded directly in the input string.

---

## 8. Worked Examples

### Example A — Trigger field in an action input

```python
{
    "input": {
        "CUSTOMER_NAME": dp("workato_service", "trig", "customerName"),
        "AMOUNT": dp("workato_service", "trig", "amount"),
        "SOURCE": "SYSTEM_A"   # static string mixed with pills
    }
}
```

### Example B — Loop item field in a condition

```python
{
    "keyword": "if",
    "input": {
        "type": "compound",
        "operand": "and",
        "conditions": [{
            "operand": "equals",
            "lhs": dp("workato_service", "payment_loop", "*", "type"),
            "rhs": "Check",
            "uuid": str(uuid4())
        }]
    }
}
```

### Example C — Oracle SP output referenced later

```python
# SP step alias: "insert_payment"
# After the SP, reference its OUT param in a logger:
{
    "input": {
        "message": "Inserted payment ID: " + dp("oracle", "insert_payment", "PAYMENT_ID")
    }
}
```

### Example D — Nested path for HTTP response field

```python
# HTTP POST step alias: "call_ciu"
# Response JSON: {"result": {"checkResult": "TRUE"}}
dp("http", "call_ciu", "result", "checkResult")
```

---

## 9. Key Rules

- The `pill_type` is always `"output"`.
- The `line` field must exactly match the `as` alias of the referenced step.
- Path elements are plain strings; use `"*"` only for `current_item` (loop iteration).
- The entire JSON is double-quote-escaped because it is embedded inside a single-quoted
  JS string inside the `#{_dp('...')}` wrapper.
- Do not URL-encode or otherwise transform the pill string — the helper handles escaping.
