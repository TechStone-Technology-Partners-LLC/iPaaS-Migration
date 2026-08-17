# Action: Salesforce

Salesforce actions in Workato use `dynamicPickListSelection` to declare the sObject type
and `extended_output_schema` to declare which fields are returned.

---

## search_sobjects (SOQL Query)

```python
step_sf_search = {
    "number": N,
    "keyword": "action",
    "provider": "salesforce",
    "name": "search_sobjects",
    "as": "search_accounts",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "sobject_name": "Account",
        "field_list": "Id\nName\nBillingCity\nBillingState\nPhone\nType\nIndustry"
    },
    "toggleCfg": {},
    "input": {
        "sobject_name": "Account",
        "field_list": "Id\nName\nBillingCity\nBillingState\nPhone\nType\nIndustry",
        "where": "Name = '" + dp("workato_service", "trig", "accountName") + "' LIMIT 1"
    },
    "extended_output_schema": [
        {"name": "sobjects", "type": "array", "of": "object", "properties": [
            {"name": "Id",          "type": "string", "label": "Account ID"},
            {"name": "Name",        "type": "string", "label": "Name"},
            {"name": "BillingCity", "type": "string", "label": "Billing City"},
            {"name": "Phone",       "type": "string", "label": "Phone"},
        ]}
    ]
}
```

### field_list Format

Fields are newline-delimited (`\n`) in a single string. This matches what Workato sends
when a user manually selects fields in the GUI.

```python
"field_list": "Id\nName\nEmail\nPhone\nAccountId"
```

### where Clause

The `where` clause is a SOQL WHERE fragment (without the `WHERE` keyword):

```python
"where": "Email = '" + dp("workato_service", "trig", "email") + "'"
"where": "LastModifiedDate > " + dp("scheduled_event", "clock", "scheduled_at")
"where": "Id = '" + dp("workato_service", "trig", "sfAccountId") + "' LIMIT 1"
```

---

## create_sobject

```python
step_sf_create = {
    "number": N,
    "keyword": "action",
    "provider": "salesforce",
    "name": "create_sobject",
    "as": "create_case",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {"sobject_name": "Case"},
    "toggleCfg": {},
    "input": {
        "sobject_name": "Case",
        "Subject":     dp("workato_service", "trig", "issueTitle"),
        "Description": dp("workato_service", "trig", "issueBody"),
        "AccountId":   dp("salesforce", "search_accounts", "sobjects", "0", "Id"),
        "Status":      "New",
        "Priority":    "Medium"
    }
}
```

---

## update_sobject

```python
step_sf_update = {
    "number": N,
    "keyword": "action",
    "provider": "salesforce",
    "name": "update_sobject",
    "as": "update_case",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {"sobject_name": "Case"},
    "toggleCfg": {},
    "input": {
        "sobject_name": "Case",
        "Id":      dp("salesforce", "search_cases", "sobjects", "0", "Id"),
        "Status":  "In Progress",
        "Subject": dp("workato_service", "trig", "issueTitle")
    }
}
```

---

## Accessing Salesforce Output

```python
# First result from a search
dp("salesforce", "search_accounts", "sobjects", "0", "Id")
dp("salesforce", "search_accounts", "sobjects", "0", "Name")

# Created record ID
dp("salesforce", "create_case", "id")

# Updated record ID
dp("salesforce", "update_case", "id")
```

---

## Config Entry

```python
{"keyword": "application", "provider": "salesforce", "account_id": 647483, "skip_validation": False}
```

Replace `647483` with the actual Salesforce connection ID from `workato-connection-list.py`.

---

## extended_output_schema

Always declare `extended_output_schema` on search steps so that downstream steps can
reference the returned fields as datapills:

```python
"extended_output_schema": [
    {"name": "sobjects", "type": "array", "of": "object", "properties": [
        {"name": "Id",    "type": "string", "label": "ID"},
        {"name": "Name",  "type": "string", "label": "Name"},
        {"name": "Email", "type": "string", "label": "Email"},
    ]}
]
```

Without this, datapills from the Salesforce step are not available in subsequent steps.
