# Workato Error Reference

Common errors encountered during recipe development, their root causes, and fixes.
All confirmed from real push attempts.

---

## HTTP 400 — Missing Parameter Name

**Error message:**
```
{"message": "Missing parameter name"}
```

**Cause:** The recipe POST payload was missing the `"recipe"` wrapper key, or the
`folder_id` was passed as an integer instead of a string.

**Fix:**
```python
# Wrong
payload = {"name": "My Recipe", "code": "...", "folder_id": 12345678}

# Correct
payload = {
    "recipe": {
        "name": "My Recipe",
        "folder_id": "12345678",  # string!
        "code": json.dumps(trigger),
        "config": json.dumps(config)
    }
}
```

---

## HTTP 404 on Recipe Push (PUT)

**Error message:**
```
{"message": "Not found"}
```

**Cause:** The recipe ID in the PUT URL does not exist in the account. This happens when
the push script hardcodes an ID from a previous session or different account.

**Fix:** Use POST (create) for new recipes, PUT (update) only for existing ones.
Verify the ID exists:
```bash
python scripts/workato-recipe-list.py --folder-id FOLDER_ID
```
If the ID is not listed, delete the hardcoded ID from the script and use POST.

---

## Recipe Visible but Steps Empty / Invisible in GUI

**Symptom:** The recipe appears in the folder. The canvas shows the trigger but no steps
inside, or the step count is wrong.

**Cause:** The trigger schema uses nested objects (`"type": "object"` with `"properties"`).
Workato GUI cannot render steps when the trigger schema has nested objects.

**Fix:** Apply the flatten rule — replace nested objects with flat scalar fields, and
accept arrays as a JSON-string field:

```python
# Bad — causes invisible steps
{"name": "applicationInfo", "type": "object", "properties": [...]}

# Good — flat scalars
{"name": "applicationInfo_customerId", "type": "string", ...}
{"name": "applicationInfo_customerName", "type": "string", ...}
{"name": "payments", "type": "string", ...}  # JSON array as string
```

---

## Connection Not Found at Runtime

**Symptom:** Recipe runs but fails with "Connection not found" or "Invalid connection".

**Cause:** The `account_id` in the `config` array is wrong — either null when it should
be an integer, or an integer from the wrong Workato account.

**Fix:**
1. Run `python scripts/workato-connection-list.py` to get current account connection IDs.
2. Update the config array with the correct integer ID for each provider.
3. Use `null` (Python `None`) only for providers that do not require a stored connection
   (http, logger, workato_service, scheduled_event).

```python
config = [
    {"keyword": "application", "provider": "workato_service", "account_id": None, "skip_validation": False},
    {"keyword": "application", "provider": "oracle",           "account_id": 19657520, "skip_validation": False},
    {"keyword": "application", "provider": "http",             "account_id": None, "skip_validation": False},
    {"keyword": "application", "provider": "logger",           "account_id": None, "skip_validation": False},
]
```

---

## UUID Collision

**Symptom:** Recipe push returns 200 but recipe behaves unexpectedly; steps appear merged
or duplicated in the canvas.

**Cause:** Push script reuses UUID constants (e.g., copy-pasted from a previous recipe)
instead of generating fresh ones.

**Fix:** Always call `str(uuid4())` for every step in every push run. Never hardcode
or reuse UUID strings across steps.

```python
from uuid import uuid4
# Every step gets its own fresh UUID
step = {"uuid": str(uuid4()), ...}
```

---

## "Recipe Already Running" Error on Update

**Symptom:** PUT to update a recipe returns 422 or 400 with "recipe already running".

**Cause:** Workato will not accept updates to a recipe that is currently active (started).

**Fix:**
1. Stop the recipe in the GUI before running the update script.
2. Or add a stop step to your script:
```python
requests.put(f"https://www.workato.com/api/recipes/{RECIPE_ID}/stop", headers=HEADERS)
# wait a moment, then push the update
```

---

## Step Numbers Out of Sequence

**Symptom:** Recipe appears correct but GUI shows steps in wrong order, or some steps
are missing from the canvas.

**Cause:** Step `number` fields are not sequential across the entire recipe tree. Workato
uses `number` for ordering; gaps or duplicates cause rendering issues.

**Fix:** Number steps sequentially starting from 1 (trigger = 0). The numbering must be
globally unique across the entire recipe, not just within each block.

```python
# Simple counter approach
_counter = [1]
def next_num():
    n = _counter[0]
    _counter[0] += 1
    return n
```

---

## send_reply Not Triggering in Caller

**Symptom:** The calling recipe (or HTTP client) never receives a response after the
callable recipe runs.

**Cause:** `send_reply` is missing `extended_input_schema`, or `toggleCfg` is missing
`"reply.status": True`.

**Fix:**
```python
step_reply = {
    "keyword": "action",
    "provider": "workato_service",
    "name": "send_reply",
    "toggleCfg": {"reply.status": True},  # REQUIRED
    "input": {"reply_type": "success", "reply": {"status": "COMPLETED"}},
    "extended_input_schema": [{"label": "Reply", "name": "reply", "type": "object",
        "properties": [{"control_type": "text", "label": "Status",
                        "name": "status", "type": "string", "optional": False}]}]
}
```

---

## Oracle SP Not Executing — "Procedure Not Found"

**Symptom:** Oracle SP step fails at runtime with procedure not found.

**Cause:** `dynamicPickListSelection.procedure_name` does not match the actual schema and
procedure name in the database, or the Oracle connection points to the wrong schema.

**Fix:** Confirm exact schema and procedure name with the DBA. Format is `SCHEMA.PROC_NAME`
(uppercase). Update both `dynamicPickListSelection` and `input.procedure_name`:

```python
"dynamicPickListSelection": {"procedure_name": "GLD_ACH.INSERTPAYMENT"},
"input": {"procedure_name": "GLD_ACH.INSERTPAYMENT", ...}
```
