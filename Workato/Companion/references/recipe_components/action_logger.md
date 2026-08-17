# Action: Logger

The `logger` provider writes messages to the Workato job log. No stored connection
required. Indispensable for debugging and audit trails.

---

## create_message (Write a Log Entry)

```python
step_log = {
    "number": N,
    "keyword": "action",
    "provider": "logger",
    "name": "create_message",
    "as": "log_request",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "message": "Processing payment for customer: "
                   + dp("workato_service", "trig", "customerName"),
        "level": "info"
    }
}
```

---

## Level Options

| `level` | Use case |
|---------|----------|
| `"info"` | Normal flow milestones (request received, step completed) |
| `"warn"` | Unexpected but recoverable situations |
| `"error"` | Errors caught by rescue/catch blocks |
| `"debug"` | Verbose diagnostic data during development |

---

## Config Entry

```python
{"keyword": "application", "provider": "logger", "account_id": None, "skip_validation": False}
```

`logger` always uses `account_id: None`.

---

## Composing the Message

Mix static text with datapills:

```python
"message": "Request received — Customer: "
           + dp("workato_service", "trig", "customerName")
           + " | Amount: "
           + dp("workato_service", "trig", "amount")
           + " | ID: "
           + dp("workato_service", "trig", "customerId")
```

---

## Logging Error Details (in catch/rescue blocks)

The `error.message` datapill is available inside `catch` and `rescue` blocks, but it
**cannot be serialised in the push script**. After pushing, open the recipe in the GUI
and manually wire the `error.message` pill into the logger message field.

Leave a placeholder in the push script:

```python
step_log_error = {
    "number": N,
    "keyword": "action",
    "provider": "logger",
    "name": "create_message",
    "as": "log_item_error",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "message": "Item processing error — wire error.message pill in GUI",
        "level": "error"
    }
}
```

---

## Viewing Logs

Log entries written by the `logger` step appear in:
- **Workato GUI** → Jobs → select a job → Step log tab.
- Each step shows its input, output, and logger messages inline.

---

## Common Logger Patterns

### Log incoming request

```python
"message": "Received request — ID: " + dp("workato_service", "trig", "id")
           + " | Customer: " + dp("workato_service", "trig", "customerName")
```

### Log loop progress

```python
"message": "Processing payment type: "
           + dp("workato_service", "payment_loop", "*", "type")
```

### Log successful completion

```python
"message": "All payments processed — sending reply"
```

### Log default branch hit

```python
"message": "Default payment type — no action taken"
```

### Log system error placeholder

```python
"message": "System error — wire error.message pill in GUI"
```
