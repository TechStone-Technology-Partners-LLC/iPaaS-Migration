# Platform Entities: Lookup Tables

Lookup tables are key-value stores inside Workato. They function like in-memory
dictionaries: a recipe can add entries, retrieve entries by key, and list all entries.
Common uses: configuration values, reference data, simple caches.

---

## Table Structure

A lookup table has:
- A **name** (display name in the Workato console)
- **Columns** — each column has a name and type
- A maximum entry count (`max_allowed_entries_count`)

Tables are created in the Workato GUI: Tools → Lookup Tables → New Table.

---

## lookup_table/add_entry (Write an Entry)

```python
step_add_entry = {
    "number": N,
    "keyword": "action",
    "provider": "lookup_table",
    "name": "add_entry",
    "as": "save_payee_key",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "zip_name": "PayeeDirectory"    # lookup table name (zip_name is the internal term)
    },
    "toggleCfg": {},
    "input": {
        "zip_name": "PayeeDirectory",
        "parameters": {
            "payee_name": dp("workato_service", "payment_loop", "*", "payeeName"),
            "payee_key":  dp("http", "get_payee", "body", "payeeKey"),
            "created_at": dp("scheduled_event", "clock", "scheduled_at")
        }
    }
}
```

### parameters Keys

The keys in `parameters` must match the column names defined in the lookup table exactly
(case-sensitive).

---

## lookup_table/lookup (Find an Entry)

```python
step_lookup = {
    "number": N,
    "keyword": "action",
    "provider": "lookup_table",
    "name": "lookup",
    "as": "find_payee",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "zip_name": "PayeeDirectory"
    },
    "toggleCfg": {},
    "input": {
        "zip_name": "PayeeDirectory",
        "search_column": "payee_name",
        "search_value": dp("workato_service", "payment_loop", "*", "payeeName")
    }
}
```

### Accessing Lookup Result

```python
# Single matching entry
dp("lookup_table", "find_payee", "payee_key")
dp("lookup_table", "find_payee", "created_at")

# Check if entry was found (Workato returns null fields if no match)
{
    "keyword": "if",
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "is_not_empty",
                              "lhs": dp("lookup_table", "find_payee", "payee_key"),
                              "uuid": str(uuid4())}]}
}
```

---

## lookup_table/search_entries (Find Multiple Entries)

```python
step_search = {
    "number": N,
    "keyword": "action",
    "provider": "lookup_table",
    "name": "search_entries",
    "as": "search_config",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {"zip_name": "AppConfig"},
    "toggleCfg": {},
    "input": {
        "zip_name": "AppConfig",
        "search_column": "environment",
        "search_value": "production"
    }
}

# Results as array
dp("lookup_table", "search_config", "entries", "0", "config_value")
```

---

## lookup_table/delete_entry (Remove an Entry)

```python
step_delete = {
    "number": N,
    "keyword": "action",
    "provider": "lookup_table",
    "name": "delete_entry",
    "as": "remove_payee",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {"zip_name": "PayeeDirectory"},
    "toggleCfg": {},
    "input": {
        "zip_name": "PayeeDirectory",
        "entry_id": dp("lookup_table", "find_payee", "id")
    }
}
```

---

## Config Entry

```python
{"keyword": "application", "provider": "lookup_table",
 "account_id": None, "skip_validation": False}
```

`lookup_table` uses `account_id: None` — it is a built-in Workato feature.

---

## Notes

- `zip_name` is the internal Workato term for the lookup table name. Always set both
  `dynamicPickListSelection.zip_name` and `input.zip_name` to the same value.
- Column names are case-sensitive and must match the table definition exactly.
- Lookup tables are shared across all recipes in the account — treat them as global state.
- Maximum entry count is configured per table in the GUI (default 5,000).
- For high-volume key-value storage, consider an external database instead.
