# Action: Oracle Database

Two Oracle actions are used in Workato: `execute_stored_procedure` for SP calls and
`select_rows` for SELECT queries. Both require a stored Oracle connection.

---

## execute_stored_procedure

```python
step_sp = {
    "number": N,
    "keyword": "action",
    "provider": "oracle",
    "name": "execute_stored_procedure",
    "as": "insert_payment",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {
        "procedure_name": "GLD_ACH.INSERTPAYMENT"   # SCHEMA.PROC_NAME — uppercase
    },
    "toggleCfg": {},
    "input": {
        "procedure_name": "GLD_ACH.INSERTPAYMENT",   # must match dynamicPickListSelection
        "APP_ID":         dp("workato_service", "trig", "appId"),
        "CUSTOMER_NAME":  dp("workato_service", "trig", "customerName"),
        "CUSTOMER_ID":    dp("workato_service", "trig", "customerId"),
        "PAYEE_NAME":     dp("workato_service", "payment_loop", "*", "payeeName"),
        "AMOUNT":         dp("workato_service", "payment_loop", "*", "amount"),
        "REFERENCE":      dp("workato_service", "payment_loop", "*", "reference"),
        "ROUTING_NUMBER": dp("workato_service", "payment_loop", "*", "routingNumber"),
        "ACCOUNT_NUMBER": dp("workato_service", "payment_loop", "*", "accountNumber"),
        "REQUESTOR_ID":   "1"   # static value mixed with datapills
    }
}
```

### Procedure Name Format

- Always `SCHEMA.PROC_NAME` — both parts uppercase.
- Must appear identically in both `dynamicPickListSelection.procedure_name` and
  `input.procedure_name`.
- Confirm exact name with the DBA — case mismatch causes runtime "procedure not found".

### IN vs OUT Parameters

- IN parameters: listed in `input` as key-value pairs.
- OUT parameters: accessible as datapills after the step runs, using the SP step's alias.

```python
# Access OUT param ACCCHECKREQUESTID from SP step "log_check_request"
dp("oracle", "log_check_request", "ACCCHECKREQUESTID")
```

---

## select_rows

```python
step_select = {
    "number": N,
    "keyword": "action",
    "provider": "oracle",
    "name": "select_rows",
    "as": "get_customer",
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "sql": "SELECT CUSTOMER_KEY, CUSTOMER_NAME, STATUS FROM GLD_SCHEMA.CUSTOMERS WHERE CUSTOMER_ID = :cust_id",
        "parameters": {
            "cust_id": dp("workato_service", "trig", "customerId")
        }
    }
}
```

### SQL Binding

- Named bind parameters use `:param_name` syntax in the SQL.
- Bind values go in `input.parameters` as a dict of `{param_name: value_or_datapill}`.
- Do not use positional `?` — Oracle requires named binds.

### Accessing Select Results

`select_rows` returns an array of rows. Access individual fields:

```python
# First row, first field (Workato auto-flattens single-row results in some contexts)
dp("oracle", "get_customer", "rows", "0", "CUSTOMER_KEY")

# In an each loop over the rows result
# (wire in GUI — programmatic row iteration requires an each step over the result)
```

For single-row lookups, use the result directly in conditions:

```python
{
    "keyword": "if",
    "input": {"type": "compound", "operand": "and",
              "conditions": [{"operand": "is_empty",
                              "lhs": dp("oracle", "get_customer", "rows"),
                              "uuid": str(uuid4())}]}
}
```

---

## Config Entry

```python
{"keyword": "application", "provider": "oracle", "account_id": 19657520, "skip_validation": False}
```

- `account_id` is the integer ID from `workato-connection-list.py`.
- The Oracle connection must be authorised in Workato GUI (credentials provided by DBA).
- One config entry covers all oracle actions in the recipe.

---

## Multiple Oracle Connections

If a recipe needs two different Oracle databases (e.g. different schemas), add two config
entries with different `account_id` values — but Workato does not natively support two
connections for the same provider in one recipe via push script. In practice, use one
Oracle connection that has access to both schemas, or split into two recipes.

---

## Notes

- `dynamicPickListSelection` on `select_rows` is empty `{}` — the table/view name is
  embedded in the SQL string directly.
- `dynamicPickListSelection` on `execute_stored_procedure` contains the procedure name —
  this is how Workato resolves the parameter list at design time.
- Oracle procedure parameters are case-sensitive in the Workato input — use the exact
  parameter names as defined in the SP signature (typically uppercase for Oracle).
