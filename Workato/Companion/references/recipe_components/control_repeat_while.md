# Control: repeat / while_condition (Repeat While Loop)

A `repeat` loop runs its block repeatedly until a `while_condition` step inside it
evaluates to false (or until a configured limit is hit). Use when the number of
iterations is unknown at the start — e.g., polling until a record appears, or
processing pages until the result set is exhausted.

**Prefer `each` when the array to iterate is already known.** Use `repeat` only when
you need a condition-controlled loop.

---

## Complete Python Code

```python
# Step: check the exit condition (placed inside repeat.block)
step_while_condition = {
    "number": N + 1,
    "keyword": "while_condition",
    "uuid": str(uuid4()),
    "input": {
        "type": "compound",
        "operand": "and",
        "conditions": [
            {
                "operand": "not_equals",
                "lhs": dp("workato_variable", "poll_status", "variable"),
                "rhs": "DONE",
                "uuid": str(uuid4())
            }
        ]
    }
}

# Step: do the work inside the loop
step_poll_action = {
    "number": N + 2,
    "keyword": "action",
    "provider": "http",
    "name": "get",
    "as": "poll_endpoint",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {"url": "https://api.internal/status/" + dp("workato_service", "trig", "jobId")}
}

# Step: update variable based on response
step_update_status = {
    "number": N + 3,
    "keyword": "action",
    "provider": "workato_variable",
    "name": "update_variable",
    "as": "set_done",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "variable_name": "poll_status",
        "new_value": dp("http", "poll_endpoint", "body", "status")
    }
}

# The repeat step
step_repeat = {
    "number": N,
    "keyword": "repeat",
    "uuid": str(uuid4()),
    "input": {
        "max_iterations": "100"   # safety cap — prevents infinite loops
    },
    "block": [
        step_poll_action,
        step_update_status,
        step_while_condition    # while_condition evaluates after each iteration
    ]
}
```

---

## while_condition Placement

`while_condition` is typically placed **last** in `repeat.block`. Workato evaluates it
at the **end** of each iteration:
- If the condition is **true** → loop continues (runs block again).
- If the condition is **false** → loop exits.

This is a "do-while" behaviour: the block always runs at least once.

---

## max_iterations

Always set `max_iterations` to prevent runaway loops. The value is a string.

```python
"input": {"max_iterations": "50"}
```

If the loop reaches `max_iterations` without the condition becoming false, Workato
stops the loop and continues to the next step (it does not raise an error by default).

---

## Condition Operand Reference

Same operands as `if` conditions:
`"equals"`, `"not_equals"`, `"is_empty"`, `"is_not_empty"`, `"greater_than"`, `"less_than"`

---

## each vs repeat — Decision Guide

| Use `each` when... | Use `repeat` when... |
|--------------------|----------------------|
| Iterating over a known array | Exit condition depends on runtime data |
| Array comes from trigger or prior step | Polling for a status change |
| Fixed number of items | Paginating through an API with unknown page count |

---

## Notes

- `while_condition` is a control keyword — it has no `provider`, `name`, or `as`.
- If the condition is true on the first evaluation, the loop has already run the block
  once (do-while semantics).
- Combine with a `workato_variable` to track loop state across iterations.
- For simple counted loops, use `each` with a generated array rather than `repeat`.
