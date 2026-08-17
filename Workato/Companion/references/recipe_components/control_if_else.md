# Control: if / elsif / else

Conditional branching. Workato evaluates conditions in order: `if` → `elsif` → `else`.

---

## if Step

```python
step_if = {
    "number": N,
    "keyword": "if",
    "uuid": str(uuid4()),
    "input": {
        "type": "compound",
        "operand": "and",         # "and" or "or" — how to combine multiple conditions
        "conditions": [
            {
                "operand": "equals",
                "lhs": dp("workato_service", "payment_loop", "*", "type"),
                "rhs": "Check",
                "uuid": str(uuid4())
            }
        ]
    },
    "block": [create_check_request_step]
}
```

---

## elsif Step

`elsif` is a **sibling** of `if` in the parent block — it is NOT nested inside `else`.

```python
step_elsif = {
    "number": N,
    "keyword": "elsif",
    "uuid": str(uuid4()),
    "input": {
        "type": "compound",
        "operand": "and",
        "conditions": [
            {
                "operand": "equals",
                "lhs": dp("workato_service", "payment_loop", "*", "type"),
                "rhs": "ACH",
                "uuid": str(uuid4())
            }
        ]
    },
    "block": [insert_payment_step]
}
```

**Placement rule:** `if`, `elsif`, `else` must appear as sequential elements in the
same parent `block` array, in order. Do not nest `elsif` inside `else.block`.

---

## else Step

```python
step_else = {
    "number": N,
    "keyword": "else",
    "uuid": str(uuid4()),
    "block": [log_default_step]
}
```

`else` has no `input` field. Its `block` runs when no preceding `if`/`elsif` matched.

---

## Correct Placement Pattern

```python
# Inside parent block (e.g., an each loop block):
parent_block = [
    step_if,      # number 4 — if type == Check
    step_elsif,   # number 5 — elsif type == ACH
    step_else,    # number 6 — else (default)
    step_rescue   # number 7 — rescue (last)
]
```

---

## Condition Operand Values

| `operand` | Description | Notes |
|-----------|-------------|-------|
| `"equals"` | lhs == rhs | String comparison |
| `"not_equals"` | lhs != rhs | |
| `"is_empty"` | lhs is blank/null | No `rhs` needed |
| `"is_not_empty"` | lhs has a value | No `rhs` needed |
| `"contains"` | lhs contains rhs substring | String only |
| `"starts_with"` | lhs starts with rhs | String only |
| `"greater_than"` | lhs > rhs | Numeric comparison |
| `"less_than"` | lhs < rhs | Numeric comparison |

For `is_empty` and `is_not_empty`, omit the `rhs` key:

```python
{"operand": "is_empty", "lhs": dp("oracle", "lookup_payee", "rows"), "uuid": str(uuid4())}
```

---

## Compound Conditions (AND / OR)

```python
"input": {
    "type": "compound",
    "operand": "and",    # all conditions must be true
    "conditions": [
        {"operand": "equals", "lhs": dp(...), "rhs": "ACH", "uuid": str(uuid4())},
        {"operand": "is_not_empty", "lhs": dp(...), "uuid": str(uuid4())}
    ]
}
```

Use `"operand": "or"` if any one condition being true is sufficient.

---

## Simple (Non-Compound) Condition

For a single condition, the `"type": "compound"` wrapper with one entry in `"conditions"`
is still the correct format — Workato does not have a simpler single-condition format.

---

## Notes

- Every condition object requires its own `uuid` — use `str(uuid4())` for each.
- The `lhs` is almost always a datapill; `rhs` is usually a static string.
- `if` does not require a matching `else`. If `else` is omitted and no condition matches,
  the recipe skips the entire if/elsif block and continues to the next step.
- Step numbers must be globally sequential. Assign a unique `number` to every if, elsif,
  and else step, as well as to every step inside their blocks.
