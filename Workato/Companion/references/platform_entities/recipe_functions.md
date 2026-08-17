# Platform Entities: Recipe Functions

A recipe function is a reusable recipe that can be called synchronously from another
recipe, similar to a subroutine or function call. The function recipe uses a special
trigger and a return action; the calling recipe uses a call action.

---

## Function Recipe — Trigger

```python
FUNC_TRIG = "receive_func_call"

func_trigger = {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_recipe_function",
    "name": "execute",
    "as": FUNC_TRIG,
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "parameters_schema": "",
    "input": {
        "input_schema_json": json.dumps([
            {"name": "payeeName", "type": "string",  "optional": False,
             "control_type": "text", "label": "Payee Name"},
            {"name": "amount",    "type": "number",  "optional": True,
             "control_type": "number", "label": "Amount"}
        ])
    },
    "block": [...]   # function body steps
}
```

### Accessing Function Input Fields

```python
dp("workato_recipe_function", FUNC_TRIG, "payeeName")
dp("workato_recipe_function", FUNC_TRIG, "amount")
```

---

## Function Recipe — Return Result

```python
step_return = {
    "number": N,
    "keyword": "action",
    "provider": "workato_recipe_function",
    "name": "return_result",
    "as": "return_payee_key",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {"output.payeeKey": True},
    "input": {
        "output": {
            "payeeKey": dp("http", "get_payee_response", "body", "payeeKey"),
            "status":   "FOUND"
        }
    },
    "extended_input_schema": [
        {
            "label": "Output",
            "name": "output",
            "type": "object",
            "properties": [
                {"control_type": "text", "label": "Payee Key", "name": "payeeKey",
                 "type": "string", "optional": True},
                {"control_type": "text", "label": "Status",    "name": "status",
                 "type": "string", "optional": False}
            ]
        }
    ]
}
```

---

## Calling a Function — call_recipe Action

```python
step_call_func = {
    "number": N,
    "keyword": "action",
    "provider": "workato_recipe_function",
    "name": "call_recipe",
    "as": "call_get_payee",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "zip_name": "GetPayeeFunction"    # display name of the function recipe
    },
    "toggleCfg": {},
    "input": {
        "zip_name": "GetPayeeFunction",
        "flow_id": "73963480",            # recipe ID of the function recipe (as string)
        "input": {
            "payeeName": dp("workato_service", "trig", "payeeName"),
            "amount":    dp("workato_service", "trig", "amount")
        }
    }
}
```

### Accessing the Function's Return Value

```python
# After the call_recipe step:
dp("workato_recipe_function", "call_get_payee", "output", "payeeKey")
dp("workato_recipe_function", "call_get_payee", "output", "status")
```

---

## Config Entry

```python
{"keyword": "application", "provider": "workato_recipe_function",
 "account_id": None, "skip_validation": False}
```

`workato_recipe_function` uses `account_id: None`.

---

## Input / Output Schema Pattern

Both the function trigger and the call action must agree on the schema:

| Function trigger `input_schema_json` | Call action `input` keys |
|--------------------------------------|--------------------------|
| Field names defined in the schema | Same field names in the input dict |

| Function `return_result` output fields | Call action expected output |
|---------------------------------------|----------------------------|
| Keys in `output` dict | Accessed via datapill `output.<field>` |

---

## zip_name vs flow_id

- `zip_name` is the display name of the function recipe (used in `dynamicPickListSelection`).
- `flow_id` is the numeric recipe ID as a string (e.g., `"73963480"`).
- Both must be set. `flow_id` is the authoritative reference at runtime.

---

## When to Use Recipe Functions

| Use recipe functions when... | Use callable recipes when... |
|-----------------------------|------------------------------|
| Called only from other Workato recipes | Called from external systems (HTTP) |
| Reusable logic within the same account | Exposed as an API endpoint |
| Needs typed input/output schema | Simpler trigger/reply pattern |
| Synchronous call with return value expected | Asynchronous or fire-and-forget |

---

## Notes

- The function recipe must be active (running) for it to be callable.
- `flow_id` must be discovered by running the function recipe and reading its ID from the
  Workato GUI URL or the recipe list API.
- Recipe functions cannot be tested independently via Postman — use a test caller recipe.
