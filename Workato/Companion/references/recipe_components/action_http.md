# Action: HTTP / REST

Two providers handle generic HTTP calls: `http` (simple, no stored connection) and
`rest` via `rest/make_request_v2` (uses a stored HTTP connection with a base URL).

---

## Provider: http/post (No Stored Connection)

Use `http` when the full URL is hardcoded in the recipe. No connection setup required.

```python
step_http_post = {
    "number": N,
    "keyword": "action",
    "provider": "http",
    "name": "post",
    "as": "call_gateway",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "url": "https://api.gateway.internal/process",
        "content_type": "application/json",
        "payload": json.dumps({
            "appId":     dp("workato_service", "trig", "appId"),
            "amount":    dp("workato_service", "payment_loop", "*", "amount"),
            "reference": dp("workato_service", "payment_loop", "*", "reference")
        }),
        "headers": [
            {"key": "Authorization", "value": "Bearer my-api-key"}
        ]
    }
}
```

### Common input fields for http/post

| Field | Description |
|-------|-------------|
| `url` | Full endpoint URL (string or datapill) |
| `content_type` | `"application/json"`, `"application/x-www-form-urlencoded"`, `"text/xml"` |
| `payload` | Request body — JSON-encoded string for JSON payloads |
| `headers` | Array of `{"key": "...", "value": "..."}` objects |

### Config Entry for http

```python
{"keyword": "application", "provider": "http", "account_id": None, "skip_validation": False}
```

`http` always uses `account_id: None`.

---

## Provider: http/get

```python
step_http_get = {
    "number": N,
    "keyword": "action",
    "provider": "http",
    "name": "get",
    "as": "get_payee",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "url": "https://api.internal/payees/" + dp("workato_service", "trig", "payeeId"),
        "headers": []
    }
}
```

---

## Provider: rest/make_request_v2 (Stored Connection)

Use `rest` when the connection has a base URL stored in Workato (configured in GUI).
This allows path-relative URLs and centralised credential management.

```python
step_rest = {
    "number": N,
    "keyword": "action",
    "provider": "rest",
    "name": "make_request_v2",
    "as": "call_ciu",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "method": "POST",
        "path": "/compliance-check",        # relative to connection base URL
        "content_type": "json",
        "request_body": json.dumps({
            "requestId":   dp("workato_service", "trig", "requestId"),
            "customerId":  dp("workato_service", "trig", "customerId")
        }),
        "response_type": "json"
    }
}
```

### Config Entry for rest

```python
{"keyword": "application", "provider": "rest", "account_id": 19657520, "skip_validation": False}
```

Replace `19657520` with the actual connection ID from `workato-connection-list.py`.

---

## Accessing HTTP Response

After the HTTP call, access response fields via datapills:

```python
# For http/post — response body fields
dp("http", "call_gateway", "body", "result")
dp("http", "call_gateway", "body", "checkResult")

# For rest/make_request_v2
dp("rest", "call_ciu", "body", "checkResult")
```

### Note on Response Parsing

The response body is available as-is. If the API returns JSON, Workato auto-parses it
and makes fields available as datapills. If it returns XML or plain text, use a
subsequent logger or data step to process.

---

## Error Handling for HTTP Steps

Wrap HTTP calls in a `try/catch` if the endpoint may be unavailable:

```python
step_try = {
    "keyword": "try",
    "block": [
        step_http_post,
        step_catch
    ]
}
```

HTTP 4xx/5xx responses do not automatically throw an error in Workato — you must check
the response status code manually using an `if` step on the response body.
