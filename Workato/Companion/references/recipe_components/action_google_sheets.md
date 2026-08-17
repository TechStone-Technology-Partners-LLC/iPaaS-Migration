# Action: Google Sheets

Google Sheets actions use `dynamicPickListSelection` to declare the spreadsheet and
sheet, and `toggleCfg` to set header row behaviour.

---

## add_spreadsheet_row_v4 (Append a Row)

```python
step_gsheets = {
    "number": N,
    "keyword": "action",
    "provider": "google_sheets",
    "name": "add_spreadsheet_row_v4",
    "as": "append_row",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",  # spreadsheet ID from URL
        "sheet_id": "Sheet1"
    },
    "toggleCfg": {
        "is_top_left": True    # REQUIRED: tells Workato the first row is headers
    },
    "input": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
        "sheet_id": "Sheet1",
        "data": {
            "Customer_ID":   dp("workato_service", "trig", "customerId"),
            "Customer_Name": dp("workato_service", "trig", "customerName"),
            "Amount":        dp("workato_service", "trig", "amount"),
            "Status":        "Processed",
            "Timestamp":     dp("scheduled_event", "clock", "scheduled_at")
        }
    },
    "extended_input_schema": [
        {"name": "data", "type": "object", "label": "Row data", "properties": [
            {"name": "Customer_ID",   "type": "string", "label": "Customer ID",   "optional": True},
            {"name": "Customer_Name", "type": "string", "label": "Customer Name", "optional": True},
            {"name": "Amount",        "type": "string", "label": "Amount",        "optional": True},
            {"name": "Status",        "type": "string", "label": "Status",        "optional": True},
            {"name": "Timestamp",     "type": "string", "label": "Timestamp",     "optional": True},
        ]}
    ]
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `spreadsheet_id` | The long alphanumeric ID from the Google Sheets URL |
| `sheet_id` | Sheet tab name (e.g., `"Sheet1"`, `"Data"`) |
| `is_top_left` | `True` = row 1 is the header row; Workato uses column names from headers |

### Column Names in data

The keys in `input.data` must match the header row column names exactly (case-sensitive,
spaces allowed). Workato maps each key to the corresponding column.

---

## get_spreadsheet_rows (Read Rows)

```python
step_get_rows = {
    "number": N,
    "keyword": "action",
    "provider": "google_sheets",
    "name": "get_spreadsheet_rows",
    "as": "read_config",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
        "sheet_id": "Config"
    },
    "toggleCfg": {"is_top_left": True},
    "input": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
        "sheet_id": "Config"
    }
}
```

---

## Accessing Google Sheets Output

```python
# After add_spreadsheet_row_v4 — the new row data
dp("google_sheets", "append_row", "data", "Customer_ID")

# After get_spreadsheet_rows — rows array
dp("google_sheets", "read_config", "rows", "0", "Config_Key")
```

---

## Config Entry

```python
{"keyword": "application", "provider": "google_sheets", "account_id": 98765, "skip_validation": False}
```

Replace `98765` with the actual Google Sheets connection ID from `workato-connection-list.py`.
The connection requires Google OAuth2 authorisation in the Workato GUI.

---

## Notes

- `toggleCfg: {"is_top_left": True}` is required. Without it, Workato treats all rows
  as data rows and column names are A, B, C... instead of header values.
- The `extended_input_schema` defines which columns are visible as datapill inputs.
  Columns not listed here will not appear in the GUI step editor.
- Spreadsheet ID is found in the Google Sheets URL:
  `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit`
