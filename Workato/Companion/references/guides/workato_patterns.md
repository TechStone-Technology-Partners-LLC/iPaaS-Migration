# Common Workato Recipe Patterns

Complete Python code for the most frequent recipe patterns. All examples use the `dp()`
helper defined in datapill_guide.md.

---

## Pattern 1 — Callable Recipe with Flat Trigger Schema

```python
trigger = {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_service",
    "name": "receive_request",
    "as": "trig",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "parameters_schema": "",
    "input": {
        "service_name": "MyService",
        "request_schema_json": json.dumps([
            {"name": "id",           "type": "string",  "optional": False, "control_type": "text",   "label": "ID"},
            {"name": "customerName", "type": "string",  "optional": False, "control_type": "text",   "label": "Customer Name"},
            {"name": "amount",       "type": "number",  "optional": True,  "control_type": "number", "label": "Amount"},
            {"name": "payments",     "type": "string",  "optional": True,  "control_type": "text",   "label": "Payments JSON"},
        ]),
        "reply_schema_json": json.dumps([
            {"name": "status", "type": "string", "optional": False, "control_type": "text", "label": "Status"}
        ])
    },
    "block": [...]
}
```

---

## Pattern 2 — Payment Routing (if / elsif / else Branching)

```python
step_if_check = {
    "number": 4, "keyword": "if", "uuid": str(uuid4()),
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "equals",
                              "lhs": dp("workato_service", "payment_loop", "*", "type"),
                              "rhs": "Check", "uuid": str(uuid4())}]},
    "block": [create_check_request_step]
}

step_elsif_ach = {
    "number": 5, "keyword": "elsif", "uuid": str(uuid4()),
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "equals",
                              "lhs": dp("workato_service", "payment_loop", "*", "type"),
                              "rhs": "ACH", "uuid": str(uuid4())}]},
    "block": [insert_payment_step]
}

step_else_default = {
    "number": 6, "keyword": "else", "uuid": str(uuid4()),
    "block": [log_default_step]
}

# NOTE: elsif is a SIBLING of if inside the parent block — not nested inside else
each_block = [step_if_check, step_elsif_ach, step_else_default, rescue_step]
```

---

## Pattern 3 — Retry Pattern with try / catch

```python
step_try = {
    "number": 1, "keyword": "try", "uuid": str(uuid4()),
    "input": {},
    "block": [
        main_work_step,
        send_reply_step,
        # catch MUST be last
        {
            "number": 99, "keyword": "catch", "uuid": str(uuid4()),
            "input": {"max_retry_count": "3", "retry_interval": "5"},
            "block": [log_error_step]
        }
    ]
}
```

---

## Pattern 4 — Per-Item Error Handling with rescue

```python
each_step = {
    "number": 3, "keyword": "each",
    "as": "payment_loop", "uuid": str(uuid4()),
    "input": {"source": dp("workato_service", "trig", "payments") + ".parse_json"},
    "block": [
        if_step,
        elsif_step,
        else_step,
        # rescue MUST be last in each.block
        {
            "number": 9, "keyword": "rescue", "uuid": str(uuid4()),
            "block": [{
                "number": 10, "keyword": "action",
                "provider": "logger", "name": "create_message",
                "as": "log_item_error", "uuid": str(uuid4()),
                "dynamicPickListSelection": {}, "toggleCfg": {},
                "input": {"message": "Item error — check Workato job logs", "level": "error"}
            }]
        }
    ]
}
```

---

## Pattern 5 — Lookup Before Create (Check Then Create)

```python
# Step A: look up existing record
step_lookup = {
    "number": 5, "keyword": "action",
    "provider": "oracle", "name": "select_rows",
    "as": "lookup_payee", "uuid": str(uuid4()),
    "dynamicPickListSelection": {}, "toggleCfg": {},
    "input": {
        "sql": "SELECT PAYEE_KEY FROM SCHEMA.PAYEES WHERE PAYEE_NAME = :name",
        "parameters": {"name": dp("workato_service", "payment_loop", "*", "payeeName")}
    }
}

# Step B: if lookup returned nothing, create
step_if_empty = {
    "number": 6, "keyword": "if", "uuid": str(uuid4()),
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "is_empty",
                              "lhs": dp("oracle", "lookup_payee", "rows"),
                              "uuid": str(uuid4())}]},
    "block": [create_payee_step]
}
```

---

## Pattern 6 — Oracle SP Call

```python
step_sp = {
    "number": 7, "keyword": "action",
    "provider": "oracle", "name": "execute_stored_procedure",
    "as": "insert_payment", "uuid": str(uuid4()),
    "dynamicPickListSelection": {"procedure_name": "GLD_ACH.INSERTPAYMENT"},
    "toggleCfg": {},
    "input": {
        "procedure_name": "GLD_ACH.INSERTPAYMENT",
        "APP_ID":         dp("workato_service", "trig", "appId"),
        "CUSTOMER_NAME":  dp("workato_service", "trig", "customerName"),
        "AMOUNT":         dp("workato_service", "payment_loop", "*", "amount"),
        "REQUESTOR_ID":   "1"   # static value
    }
}
```

---

## Pattern 7 — HTTP POST with JSON Payload

```python
step_http = {
    "number": 8, "keyword": "action",
    "provider": "http", "name": "post",
    "as": "call_gateway", "uuid": str(uuid4()),
    "dynamicPickListSelection": {}, "toggleCfg": {},
    "input": {
        "url": "https://api.gateway.internal/process",
        "content_type": "application/json",
        "payload": json.dumps({
            "appId":        dp("workato_service", "trig", "appId"),
            "payeeName":    dp("workato_service", "payment_loop", "*", "payeeName"),
            "amount":       dp("workato_service", "payment_loop", "*", "amount")
        })
    }
}
```

---

## Pattern 8 — Logger Usage

```python
step_log_info = {
    "number": 2, "keyword": "action",
    "provider": "logger", "name": "create_message",
    "as": "log_request", "uuid": str(uuid4()),
    "dynamicPickListSelection": {}, "toggleCfg": {},
    "input": {
        "message": "Processing request for customer: "
                   + dp("workato_service", "trig", "customerName"),
        "level": "info"
    }
}

step_log_error = {
    "number": 15, "keyword": "action",
    "provider": "logger", "name": "create_message",
    "as": "log_system_error", "uuid": str(uuid4()),
    "dynamicPickListSelection": {}, "toggleCfg": {},
    "input": {
        "message": "System error — see job logs for error.message pill",
        "level": "error"
    }
}
# Note: error.message pill must be wired manually in the Workato GUI;
# it cannot be serialised programmatically via the push script.
```
