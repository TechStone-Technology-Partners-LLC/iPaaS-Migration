# Action: workato_service / send_reply

Returns a response to the caller of a callable recipe. Must only appear when the trigger
is `workato_service/receive_request`. Place it after the main logic, before the `catch`.

---

## Success Variant

```python
step_reply_success = {
    "number": N,
    "keyword": "action",
    "provider": "workato_service",
    "name": "send_reply",
    "as": "send_reply_step",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {
        "reply.status": True    # REQUIRED — enables the reply.status field in GUI
    },
    "input": {
        "reply_type": "success",
        "reply": {
            "status": "PAYMENTS_PROCESSED"
        }
    },
    "extended_input_schema": [
        {
            "label": "Reply",
            "name": "reply",
            "type": "object",
            "properties": [
                {
                    "control_type": "text",
                    "label": "Status",
                    "name": "status",
                    "type": "string",
                    "optional": False
                }
            ]
        }
    ]
}
```

---

## Multi-Field Reply

To return multiple fields, extend `reply` and `extended_input_schema`:

```python
"input": {
    "reply_type": "success",
    "reply": {
        "status":    "COMPLETED",
        "recordId":  dp("oracle", "insert_record", "RECORD_ID"),
        "message":   "All payments processed successfully"
    }
},
"extended_input_schema": [
    {
        "label": "Reply",
        "name": "reply",
        "type": "object",
        "properties": [
            {"control_type": "text",    "label": "Status",    "name": "status",    "type": "string",  "optional": False},
            {"control_type": "text",    "label": "Record ID", "name": "recordId",  "type": "string",  "optional": True},
            {"control_type": "text",    "label": "Message",   "name": "message",   "type": "string",  "optional": True},
        ]
    }
]
```

---

## Error Variant

Use when you want to signal a structured error response to the caller:

```python
step_reply_error = {
    "number": N,
    "keyword": "action",
    "provider": "workato_service",
    "name": "send_reply",
    "as": "send_error_reply",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {"reply.message": True, "reply.code": True},
    "input": {
        "reply_type": "error",
        "reply": {
            "message": "Payment processing failed",
            "code":    "PAYMENT_ERROR"
        }
    },
    "extended_input_schema": [
        {
            "label": "Reply",
            "name": "reply",
            "type": "object",
            "properties": [
                {"control_type": "text", "label": "Message", "name": "message", "type": "string", "optional": False},
                {"control_type": "text", "label": "Code",    "name": "code",    "type": "string", "optional": False}
            ]
        }
    ]
}
```

---

## reply_type Values

| Value | Caller Experience |
|-------|------------------|
| `"success"` | Caller receives HTTP 200 with the reply body |
| `"error"` | Caller receives an error response (Workato marks as failed) |

---

## toggleCfg Requirement

`toggleCfg` must include an entry for each reply field name, set to `True`. Without this,
the reply field is not visible or editable in the Workato GUI canvas.

```python
"toggleCfg": {
    "reply.status": True,
    "reply.recordId": True,
    "reply.message": True
}
```

---

## Placement in Recipe

`send_reply` should appear after the main processing logic, but before `catch`:

```
try.block = [
    step_each,         # main logic
    send_reply_step,   # reply to caller (inside try so catch handles its errors too)
    catch_step         # must be last
]
```

If `send_reply` is inside the `try` block and an error occurs before it is reached, the
caller will not receive a reply. For resilient reply patterns, place `send_reply` inside
the catch block as well (error reply).

---

## Config Entry

```python
{"keyword": "application", "provider": "workato_service",
 "account_id": None, "skip_validation": False}
```

`workato_service` always uses `account_id: None`.

---

## Notes

- `send_reply` without `extended_input_schema` will push successfully, but the reply
  body field will not be visible in the GUI. Always include it.
- The `reply_schema_json` in the trigger determines what the caller sees in its output
  schema. Ensure the field names match between the trigger's `reply_schema_json` and the
  `send_reply` step's `reply` object.
- A callable recipe without `send_reply` will leave the caller hanging indefinitely
  (timeout). Always include it.
