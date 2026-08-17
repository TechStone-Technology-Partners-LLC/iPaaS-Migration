# Error Handling Guide

Workato has three error-handling constructs: `try/catch`, `rescue`, and `stop`.
Each has a distinct purpose and strict placement rules.

---

## 1. try / catch — Outer Block Error Handling

Use `try/catch` to wrap a sequence of steps and catch any error that bubbles up from
within that sequence.

### Structure

```python
step_try = {
    "number": 1,
    "keyword": "try",
    "uuid": str(uuid4()),
    "input": {},
    "block": [
        step_a,
        step_b,
        step_c,
        step_catch   # MUST be the last element in try.block
    ]
}

step_catch = {
    "number": 10,
    "keyword": "catch",
    "uuid": str(uuid4()),
    "input": {
        "max_retry_count": "0",   # "0" = no retry, "3" = retry up to 3 times
        "retry_interval": "2"     # seconds between retries (string)
    },
    "block": [log_error_step]
}
```

### Placement Rule

`catch` must be the **last element** in the `try` step's `block` array. If any step
appears after `catch` in the same `block`, Workato will reject or mis-render the recipe.

### max_retry_count and retry_interval

| `max_retry_count` | Effect |
|------------------|--------|
| `"0"` | No retry; catch block runs immediately on first error |
| `"3"` | Retry the try block up to 3 times before running catch |

`retry_interval` is in seconds. Use `"2"` (2 seconds) as a safe default.

---

## 2. rescue — Per-Iteration Error Handling

Use `rescue` inside an `each` (foreach) block to catch errors on a per-item basis
without aborting the entire loop.

### Structure

```python
each_step = {
    "number": 3,
    "keyword": "each",
    "as": "payment_loop",
    "uuid": str(uuid4()),
    "input": {"source": "...datapill....parse_json"},
    "block": [
        if_step,
        elsif_step,
        else_step,
        rescue_step   # MUST be the last element in each.block
    ]
}

rescue_step = {
    "number": 8,
    "keyword": "rescue",
    "uuid": str(uuid4()),
    "block": [log_item_error_step]
}
```

### Placement Rule

`rescue` must be the **last element** in the `each` step's `block` array.

### rescue vs catch

| Construct | Where it sits | Scope | Use case |
|-----------|--------------|-------|----------|
| `rescue`  | Last in `each.block` | Per loop iteration | Catch item-level errors, continue to next item |
| `catch`   | Last in `try.block`  | Entire try block   | Catch recipe-level errors, execute recovery logic |

---

## 3. error.message Datapill

Inside a `catch` or `rescue` block, you can reference the error message using Workato's
built-in `error.message` pill. **This pill cannot be serialised via the push script.**

After pushing, open the recipe in the Workato GUI:
1. Open the catch/rescue step.
2. Inside the log or notification step, click the field and select the `error.message`
   datapill from the "Error" section of the datapill tree.

In push scripts, leave a placeholder comment:

```python
step_log_error = {
    "input": {
        "message": "Error occurred — wire error.message pill in GUI"
    }
}
```

---

## 4. stop — Unconditional Halt

Use `stop` when you want to deliberately terminate the recipe run with a clear reason.

```python
step_stop = {
    "number": N,
    "keyword": "stop",
    "uuid": str(uuid4()),
    "input": {
        "stop_with_error": "true",   # "true" marks the job as failed; "false" = success
        "stop_reason": "Invalid payment type — no matching branch"
    }
}
```

- `stop_with_error: "true"` → job status = Error (visible in job history).
- `stop_with_error: "false"` → job status = Success but recipe halted early.

---

## 5. Combined Pattern — Outer try + Inner rescue

The most robust pattern for payment-style recipes:

```
trigger
  try
    each payments
      if Check → ...
      elsif ACH → ...
      else → logger (default)
      rescue → logger (item error)   ← catches per-item errors
    send_reply
    catch → logger (system error)   ← catches anything not caught by rescue
```

```python
step_catch = {
    "number": 20, "keyword": "catch", "uuid": str(uuid4()),
    "input": {"max_retry_count": "0", "retry_interval": "2"},
    "block": [step_log_system_error]
}

step_try = {
    "number": 1, "keyword": "try", "uuid": str(uuid4()),
    "input": {},
    "block": [step_each, step_send_reply, step_catch]
}
```

Errors inside the loop are swallowed by `rescue`; errors outside (e.g. in `send_reply`)
are caught by `catch`. This ensures the recipe always terminates cleanly.
