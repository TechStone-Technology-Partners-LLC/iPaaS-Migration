# Action: Email / Gmail

Two email providers: `email` (Workato built-in SMTP relay, no stored connection) and
`gmail` (uses a Google OAuth2 connection).

---

## email/send_mail (Workato Built-In)

No stored connection required. Uses Workato's own mail relay. Suitable for notifications.

```python
step_email = {
    "number": N,
    "keyword": "action",
    "provider": "email",
    "name": "send_mail",
    "as": "send_notification",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "to": "team@company.com",
        "subject": "Payment Processing Complete — "
                   + dp("workato_service", "trig", "customerId"),
        "body": "All payments for customer "
                + dp("workato_service", "trig", "customerName")
                + " have been processed successfully.",
        "email_type": "text"
    }
}
```

### Config Entry for email

```python
{"keyword": "application", "provider": "email", "account_id": None, "skip_validation": False}
```

`email` always uses `account_id: None`.

---

## email/send_mail — HTML Body

```python
step_email_html = {
    "number": N,
    "keyword": "action",
    "provider": "email",
    "name": "send_mail",
    "as": "send_html_notification",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "to": "operations@company.com",
        "subject": "Error Alert: "
                   + dp("workato_service", "trig", "customerId"),
        "body": "<h2>Error Occurred</h2><p>Customer: "
                + dp("workato_service", "trig", "customerName")
                + "</p><p>Please review the job logs.</p>",
        "email_type": "html"
    }
}
```

### email_type Options

| Value | Description |
|-------|-------------|
| `"text"` | Plain text body |
| `"html"` | HTML-formatted body |

---

## Multiple Recipients

```python
"to": "alice@company.com, bob@company.com, carol@company.com"
```

Comma-separated email addresses in a single string.

---

## gmail/send_mail (Google OAuth2)

Sends via the authenticated Google account. Requires a Google connection.

```python
step_gmail = {
    "number": N,
    "keyword": "action",
    "provider": "gmail",
    "name": "send_mail",
    "as": "send_gmail",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "to": dp("workato_service", "trig", "recipientEmail"),
        "subject": "Confirmation: "
                   + dp("workato_service", "trig", "orderId"),
        "body": "Your order has been processed.",
        "email_type": "text",
        "from_name": "My Service"   # optional: display name for the From field
    }
}
```

### Config Entry for gmail

```python
{"keyword": "application", "provider": "gmail", "account_id": 55512, "skip_validation": False}
```

Replace `55512` with the Google/Gmail connection ID from `workato-connection-list.py`.

---

## Notes

- The `email` provider is preferred for internal notifications — it requires no
  connection setup and never needs re-authorisation.
- Use `gmail` when the email must appear to come from a specific Google account, or
  when you need Gmail-specific features (labels, threading).
- Neither provider supports attachments via the push script API. For attachments,
  configure the step manually in the GUI after pushing.
- Datapills can be used in `to`, `subject`, and `body` fields.
