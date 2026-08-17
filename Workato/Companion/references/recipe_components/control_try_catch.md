# Control: try / catch and rescue

Three error-handling constructs with distinct scopes and placement rules.

---

## try / catch

Wraps a sequence of steps. If any step inside the `try` block raises an error, execution
jumps to the `catch` block. The recipe continues after the try/catch pair.

### Complete Python Code

```python
step_log_system_error = {
    "number": 20,
    "keyword": "action",
    "provider": "logger",
    "name": "create_message",
    "as": "log_system_error",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "message": "System error — wire error.message pill in GUI",
        "level": "error"
    }
}

step_catch = {
    "number": 15,
    "keyword": "catch",
    "uuid": str(uuid4()),
    "input": {
        "max_retry_count": "0",   # "0" = no retry; "3" = retry try block 3 times
        "retry_interval": "2"     # seconds between retries (as string)
    },
    "block": [step_log_system_error]
}

step_try = {
    "number": 1,
    "keyword": "try",
    "uuid": str(uuid4()),
    "input": {},            # always empty dict
    "block": [
        step_each,
        step_send_reply,
        step_catch          # catch MUST be last in try.block
    ]
}
```

### Placement Rule — catch

`catch` must be the **last element** in the `try` step's `block` array.
Steps appearing after `catch` in the same `block` will be silently ignored or cause
a recipe parse error.

### max_retry_count

| Value | Behaviour |
|-------|-----------|
| `"0"` | No retry. Catch block runs immediately on first failure. |
| `"1"` | Retry once (2 total attempts) before running catch. |
| `"3"` | Retry 3 times (4 total attempts) before running catch. |

`retry_interval` is in seconds (string format). Minimum `"1"`, safe default `"2"`.

---

## rescue

Attached to an `each` loop to catch per-item errors without stopping the loop.
If an item raises an error, `rescue` runs for that item; the loop continues to the
next item.

### rescue Placement Rule

`rescue` must be the **last element** in the `each` step's `block` array.

```python
each_step = {
    "keyword": "each",
    "as": "payment_loop",
    "block": [
        if_step,
        elsif_step,
        else_step,
        {
            "number": 9,
            "keyword": "rescue",
            "uuid": str(uuid4()),
            "block": [
                {
                    "number": 10,
                    "keyword": "action",
                    "provider": "logger",
                    "name": "create_message",
                    "as": "log_item_error",
                    "uuid": str(uuid4()),
                    "dynamicPickListSelection": {},
                    "toggleCfg": {},
                    "input": {
                        "message": "Item error — wire error.message pill in GUI",
                        "level": "error"
                    }
                }
            ]
        }   # rescue ALWAYS LAST
    ]
}
```

---

## rescue vs catch — When to Use Each

| Construct | Location | Scope | Behaviour |
|-----------|----------|-------|-----------|
| `rescue` | Last in `each.block` | Per loop item | Catches item error, continues loop |
| `catch` | Last in `try.block` | Entire try block | Catches any error, ends try block |

Use both together for the most robust pattern:

```
try
  each payments       ← inner rescue catches per-item errors
    if / elsif / else
    rescue → log_item_error
  send_reply
  catch → log_system_error  ← outer catch catches errors in send_reply or unhandled
```

---

## error.message Pill (Manual GUI Step)

Both `catch` and `rescue` blocks have access to the `error.message` datapill — the
exception message from Workato. This pill **cannot be written in the push script**.

After pushing:
1. Open the recipe in the Workato GUI.
2. Click the logger step inside catch/rescue.
3. In the message field, select the `error.message` datapill from the Error section of
   the datapill tree.

Leave a comment in the push script:
```python
"message": "System error — wire error.message pill in GUI"
```

---

## Notes

- `try` has `"input": {}` — always an empty dict, never `None` or omitted.
- `catch` and `rescue` have no `provider`, `name`, or `as` — they are control keywords.
- Neither `catch` nor `rescue` appears in the config array.
- A `try` without a `catch` is valid but not recommended — unhandled errors will
  terminate the recipe run and mark the job as failed.
