# Platform Entities: Connections

A connection (also called an "application" or "account") stores credentials for a
specific external system. Each connection has a unique integer ID within the Workato
account. Connections are referenced in the recipe's `config` array.

---

## Config Array Format

The `config` array declares which connections the recipe uses. One entry per provider.

```python
config = [
    {
        "keyword": "application",
        "provider": "workato_service",    # provider name (matches step "provider" field)
        "account_id": None,               # None = no stored connection needed
        "skip_validation": False          # always False
    },
    {
        "keyword": "application",
        "provider": "oracle",
        "account_id": 19657520,           # integer ID from workato-connection-list.py
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "http",
        "account_id": None,
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "salesforce",
        "account_id": 647483,
        "skip_validation": False
    },
    {
        "keyword": "application",
        "provider": "logger",
        "account_id": None,
        "skip_validation": False
    },
]
```

---

## account_id: None vs Integer

| account_id | When to use |
|-----------|-------------|
| `None` | Provider does not require stored credentials |
| `<integer>` | Provider requires a pre-authorised connection in Workato |

### Providers that always use None

- `workato_service` (callable/reply)
- `http` (generic HTTP — URL is in the step)
- `logger` (built-in log)
- `scheduled_event` (timer trigger)
- `workato_variable` (variables)
- `workato_recipe_function` (recipe functions)

### Providers that require an integer account_id

- `oracle`, `salesforce`, `netsuite`, `jira`, `box`
- `google_sheets`, `gmail`, `google_drive`
- `sftp`, `ftp`
- Any named app connector with OAuth2 or API key credentials

---

## Discovering Connection IDs

Run the connection list script to find IDs for the current account:

```bash
python scripts/workato-connection-list.py
# Filter by provider:
python scripts/workato-connection-list.py --provider oracle
python scripts/workato-connection-list.py --provider salesforce
```

Example output:
```
ID          Name                              Provider     Authorised
19657520    MIG_WM_GLD_Oracle_Connection      oracle       Yes
647483      Salesforce Connection (Manish A)  salesforce   Yes
88421       SFTP Production                   sftp         Yes
```

Use the ID integer directly in the config array.

---

## One Entry Per Provider

If a recipe uses two different Oracle connections (e.g., two databases), Workato
supports only one config entry per provider. Work around this by:
- Using a single Oracle user with cross-schema access, or
- Splitting into two recipes (each with its own Oracle connection), or
- Using a gateway/proxy that presents a single connection.

---

## Connection Not Authorised

If a connection exists but is not authorised (password not yet set, OAuth not completed):
- The recipe will push successfully.
- At runtime the step using that connection will fail with "Connection not found" or
  "Invalid credentials".
- Fix: open the connection in Workato GUI → enter credentials → click "Connect".

Set `skip_validation: False` always. Setting it to `True` bypasses the validation check
but does not fix missing credentials — it just delays the failure to runtime.

---

## Multiple Accounts for the Same Provider

If your Workato account has two Salesforce connections (e.g., sandbox and production),
each has a different `account_id`. Use the correct ID for the target environment.

```python
# Sandbox
{"keyword": "application", "provider": "salesforce", "account_id": 112233, ...}

# Production
{"keyword": "application", "provider": "salesforce", "account_id": 445566, ...}
```

---

## config is JSON-serialised in the POST payload

```python
payload = {
    "recipe": {
        "name": "My Recipe",
        "folder_id": "12345678",
        "code": json.dumps(trigger),
        "config": json.dumps(config)   # config is a JSON string in the API payload
    }
}
```
