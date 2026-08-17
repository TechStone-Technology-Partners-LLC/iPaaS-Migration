# Control: stop

The `stop` keyword immediately terminates the current recipe run. Execution halts at the
stop step; no subsequent steps are executed.

---

## Complete Python Code

```python
# Stop and mark the job as failed
step_stop_error = {
    "number": N,
    "keyword": "stop",
    "uuid": str(uuid4()),
    "input": {
        "stop_with_error": "true",
        "stop_reason": "Invalid payment type — no matching branch found"
    }
}

# Stop and mark the job as successful (graceful early exit)
step_stop_success = {
    "number": N,
    "keyword": "stop",
    "uuid": str(uuid4()),
    "input": {
        "stop_with_error": "false",
        "stop_reason": "No records to process — exiting early"
    }
}
```

---

## stop_with_error

| Value | Job Status | Use Case |
|-------|-----------|----------|
| `"true"` | Error (red) | Unexpected situation that should alert the team |
| `"false"` | Success (green) | Intentional early exit (nothing to do) |

---

## stop_reason

A plain-text description of why the recipe was stopped. Appears in:
- The Workato job history detail view.
- Alert emails (if error alerts are configured).

Keep it descriptive:
```python
"stop_reason": "No payment type matched — expected Check, ACH, or Wire but got: "
               + dp("workato_service", "payment_loop", "*", "type")
```

Datapills can be embedded in `stop_reason`.

---

## Common Uses

### Guard clause — validate required input

```python
step_check_required = {
    "keyword": "if",
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "is_empty",
                              "lhs": dp("workato_service", "trig", "customerId"),
                              "uuid": str(uuid4())}]},
    "block": [
        {
            "keyword": "stop",
            "uuid": str(uuid4()),
            "input": {
                "stop_with_error": "true",
                "stop_reason": "customerId is required but was not provided"
            }
        }
    ]
}
```

### Early exit when no records found

```python
step_exit_if_empty = {
    "keyword": "if",
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "is_empty",
                              "lhs": dp("oracle", "query_pending", "rows"),
                              "uuid": str(uuid4())}]},
    "block": [
        {
            "keyword": "stop",
            "uuid": str(uuid4()),
            "input": {
                "stop_with_error": "false",
                "stop_reason": "No pending records found — nothing to process"
            }
        }
    ]
}
```

---

## Notes

- `stop` has no `provider`, `name`, or `as` — it is a control keyword.
- `stop` does not appear in the config array.
- After a `stop` step, all subsequent steps in the same block (and parent blocks) are
  skipped. Use with care inside loops — stopping inside an `each` loop halts the entire
  recipe, not just the current iteration. For per-item halts, use `rescue` instead.
- `stop_with_error: "true"` triggers any error monitoring / alerting configured in the
  Workato account settings.
