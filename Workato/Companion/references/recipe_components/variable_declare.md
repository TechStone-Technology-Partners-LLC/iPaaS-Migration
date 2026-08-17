# Control: Variables (workato_variable)

Workato variables hold a scalar value or a list that persists across steps within a
recipe run. Useful for accumulators, counters, and values built up across loop iterations.

---

## declare_variable (Scalar Variable)

```python
step_declare_var = {
    "number": N,
    "keyword": "action",
    "provider": "workato_variable",
    "name": "declare_variable",
    "as": "init_status",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "variable_name": "processingStatus",
        "variable_type": "string",
        "initial_value": "PENDING"
    },
    "extended_input_schema": [
        {"name": "variable_name",  "type": "string", "label": "Variable name",  "optional": False},
        {"name": "variable_type",  "type": "string", "label": "Variable type",  "optional": False},
        {"name": "initial_value",  "type": "string", "label": "Initial value",  "optional": True}
    ],
    "extended_output_schema": [
        {"name": "variable", "type": "string", "label": "processingStatus"}
    ]
}
```

### variable_type Options

| Value | Description |
|-------|-------------|
| `"string"` | Text value |
| `"integer"` | Whole number |
| `"number"` | Decimal |
| `"boolean"` | True/False |
| `"date_time"` | Timestamp |

---

## declare_list (List Variable)

```python
step_declare_list = {
    "number": N,
    "keyword": "action",
    "provider": "workato_variable",
    "name": "declare_list",
    "as": "init_errors",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "variable_name": "errorList",
        "initial_value": "[]"   # empty JSON array as string
    },
    "extended_input_schema": [
        {"name": "variable_name", "type": "string", "label": "Variable name", "optional": False},
        {"name": "initial_value", "type": "string", "label": "Initial value",  "optional": True}
    ],
    "extended_output_schema": [
        {"name": "variable", "type": "array", "label": "errorList"}
    ]
}
```

---

## update_variable (Set a New Value)

```python
step_update_var = {
    "number": N,
    "keyword": "action",
    "provider": "workato_variable",
    "name": "update_variable",
    "as": "set_status_complete",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "variable_name": "processingStatus",
        "new_value": "COMPLETED"
    }
}
```

---

## Referencing a Variable in Later Steps

After declaring a variable with alias `"init_status"`, reference its current value:

```python
dp("workato_variable", "init_status", "variable")

# Example: in a condition
{
    "keyword": "if",
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "equals",
                              "lhs": dp("workato_variable", "init_status", "variable"),
                              "rhs": "COMPLETED",
                              "uuid": str(uuid4())}]}
}

# Example: in a logger
{
    "input": {"message": "Status is: " + dp("workato_variable", "init_status", "variable")}
}
```

**Important:** The datapill `line` is the alias of the **declare** step, not the update
step. The variable always reads the current value regardless of which update step ran last.

---

## Config Entry

```python
{"keyword": "application", "provider": "workato_variable",
 "account_id": None, "skip_validation": False}
```

`workato_variable` always uses `account_id: None`.

---

## Notes

- Variables are scoped to the current recipe run — they reset on each job execution.
- Variables are not shared across parallel recipe runs.
- For counters that need to persist across runs (e.g., sequence numbers), use a
  lookup table or database instead.
- `extended_output_schema` is required so that the variable value is available as a
  datapill in downstream steps.
