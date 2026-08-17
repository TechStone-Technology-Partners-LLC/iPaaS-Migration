# Control: each (Foreach Loop)

The `each` keyword iterates over an array. Each item is accessible inside the block
via the `current_item` datapill pattern.

---

## Complete Python Code

```python
step_each = {
    "number": N,
    "keyword": "each",
    "as": "payment_loop",           # alias — referenced in datapills inside the block
    "uuid": str(uuid4()),
    "input": {
        "source": dp("workato_service", "trig", "payments") + ".parse_json"
        # OR: just a datapill if the source is already an array (not a JSON string)
        # "source": dp("salesforce", "search_accounts", "sobjects")
    },
    "block": [
        step_if,        # process each item
        step_elsif,
        step_else,
        step_rescue     # MUST be last in each.block
    ]
}
```

---

## input.source Variants

### JSON string from trigger (most common)

The trigger carries a JSON-encoded array as a string field. Parse it at iteration time:

```python
"source": dp("workato_service", "trig", "payments") + ".parse_json"
```

### Already-an-array output from a previous step

When a prior step (e.g., Salesforce search, select_rows) returns an array directly:

```python
"source": dp("salesforce", "search_accounts", "sobjects")
"source": dp("oracle", "get_rows", "rows")
```

No `.parse_json` needed — the array is already structured.

---

## Accessing the Current Item (Datapills Inside the Block)

Inside the `each.block`, reference fields of the current iteration item using `"*"` as
a path element, which becomes `{"path_element_type": "current_item"}`:

```python
def dp(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    pill = json.dumps({"pill_type": "output", "provider": provider, "line": line,
                       "path": path}).replace('"', '\\"')
    return "#{_dp('" + pill + "')}"

# Inside the each block — current payment's "type" field
dp("workato_service", "payment_loop", "*", "type")

# Current item's nested field
dp("workato_service", "payment_loop", "*", "payee", "name")
```

**Note:** The `provider` and `line` in the datapill refer to the **source** of the data,
not the `each` step itself. Use the trigger alias with `"*"` for the current item when
iterating over trigger data.

---

## rescue Placement Rule

`rescue` must be the **last element** in `each.block`. Placing any step after `rescue`
inside the block causes a Workato parse error or mis-rendering.

```python
"block": [
    if_step,
    elsif_step,
    else_step,
    rescue_step    # ALWAYS LAST
]
```

---

## Nested each Loops

For iterating over a nested array (e.g., line items within orders), nest `each` steps:

```python
step_each_orders = {
    "keyword": "each",
    "as": "order_loop",
    "input": {"source": dp("workato_service", "trig", "orders") + ".parse_json"},
    "block": [
        {
            "keyword": "each",
            "as": "line_loop",
            "input": {"source": dp("workato_service", "order_loop", "*", "lineItems") + ".parse_json"},
            "block": [
                process_line_step,
                # inner rescue
            ]
        },
        # outer rescue
    ]
}
```

---

## No alias on each

The `each` step does not require a provider name in the `config` array — it is a
built-in control flow keyword, not an app connector.

---

## Notes

- `"keyword": "each"` is the correct keyword — not `"foreach"`.
- The `as` alias is mandatory; it is used in the datapill `line` field for current-item
  references inside the block.
- An `each` loop with an empty array source is a no-op — the block simply does not
  execute. This is safe and expected.
- Step numbers must be globally sequential. Steps inside `each.block` get their own
  unique `number` values that continue from the outer step sequence.
