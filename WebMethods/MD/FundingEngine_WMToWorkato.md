# WMToWorkato: GLDFundingEngine20080714 → "FundingEngine" Recipe Build Prompts

**Source analysis:** `WebMethods/Analysis/MD/PackageAnalysis.md` (sections 5–10)  
**Target recipe name:** FundingEngine  
**Target folder:** migrAIte_Training/webMethodsMigration (folderId: 32050036)  
**Reference components:** `Workato/RecipeComponents/`  
**Generated:** 2026-07-30

---

## Overview

These prompts build two Workato recipes from GLDFundingEngine20080714 (webMethods IS 6.5):

- **Recipe 1 — FundingEngine** (processFundingRequest): callable recipe with flat trigger, each loop, 3-way payment type branching, per-payment rescue, outer catch
- **Recipe 2 — processACHBatch**: scheduled recipe with Oracle queries, NACHA generation (⚠️ gap), email notification

Execute prompts sequentially. Each is self-contained and builds on prior steps.

---

## Connections Required

| Connection Name | App | Type | Notes |
|---|---|---|---|
| `GLDFundingEngine_CheckWriter_Connection` | rest (HTTP) | HTTP REST | Base URL from SME — GLDExpressGateway CheckWriter |
| `GLDFundingEngine_ACH_Connection` | rest (HTTP) | HTTP REST | Base URL from SME — GLD_ACHAdaptersServices |
| `GLDFundingEngine_MessageLog_Connection` | rest (HTTP) | HTTP REST | Base URL from SME — GLDMessageLog |
| `GLDFundingEngine_Oracle_Connection` | oracle | Oracle JDBC | For processACHBatch Oracle queries |
| `GLDFundingEngine_Email_Connection` | gmail or smtp | Email | For processACHBatch email notification |

---

## SME Inputs Required Before Building

| # | Input Needed | Used In |
|---|---|---|
| S1 | GLDExpressGateway CheckWriter base URL + auth | Recipe 1 steps 3, 5, 6 |
| S2 | GLD_ACHAdaptersServices base URL + auth (HTTP gateway or direct Oracle) | Recipe 1 step 8 |
| S3 | GLDMessageLog base URL + auth | Recipe 1 rescue, Recipe 2 catch |
| S4 | Oracle host, port, SID, schema credentials | Recipe 2 steps 1–3 |
| S5 | processACHBatch schedule (frequency + time) | Recipe 2 trigger |
| S6 | ACH batch email recipients | Recipe 2 step 6 |
| S7 | NACHA file header fields (Company Name, Company ID, Entry Description, Effective Date) | Recipe 2 step 5 gap |
| S8 | FTP/SFTP server details (if NACHA file delivery activation needed) | Recipe 2 optional |

---

## Recipe 1 Build Prompts — FundingEngine (processFundingRequest)

---

### Prompt 0: Create the recipe skeleton

Create a new Workato recipe named **"FundingEngine"** in folder **migrAIte_Training/webMethodsMigration** (folderId `32050036`).

- Recipe type: callable recipe
- Trigger: `workato_service/receive_request`
- `service_name`: `"FundingEngine"`
- Leave trigger schema and recipe body empty for now

Reference: `Workato/RecipeComponents/WorkatoServiceTrigger.json`

---

### Prompt 1: Define the callable trigger input schema (flat — no nested objects)

Workato silently wipes nested `type:"object"` fields in `request_schema_json`. Use **flat fields** for all applicationInfo fields and pass the payments array as a **JSON string**.

Set the trigger `input.request_schema_json` to:

```json
[
  {"name":"id","type":"string","optional":false,"control_type":"text","label":"Application ID"},
  {"name":"customerName","type":"string","optional":false,"control_type":"text","label":"Customer Name"},
  {"name":"customerID","type":"string","optional":false,"control_type":"text","label":"Customer ID"},
  {"name":"sourceName","type":"string","optional":true,"control_type":"text","label":"Source Name"},
  {"name":"sourceSubCategory","type":"string","optional":true,"control_type":"text","label":"Source Sub Category"},
  {"name":"salesRepName","type":"string","optional":true,"control_type":"text","label":"Sales Rep Name"},
  {"name":"payments","type":"string","optional":false,"control_type":"text","label":"Payments JSON Array"}
]
```

Set the trigger `input.reply_schema_json` to:

```json
[
  {"name":"paymentResponses","type":"string","optional":false,"control_type":"text","label":"Payment Responses JSON"}
]
```

Reference: `Workato/RecipeComponents/WorkatoServiceTrigger.json`

---

### Prompt 2: Add the outer try block

Inside the trigger's `block` array, add a `try` block as step 1:

- `keyword`: `"try"`
- `provider`: `"workato"`
- `name`: `"try"`
- Leave `try.block` empty for now — subsequent prompts fill it
- Add a `catch` placeholder as the last sibling in `try.block`

---

### Prompt 3: Add the each loop over payments (inside try)

Inside `try.block`, add a `repeat_for_each` (`each`) step:

**Configuration:**
- `keyword`: `"each"`
- `provider`: `"workato"`
- `name`: `"each"`
- `as`: `"payment_loop"`
- Input source (the `each` input that feeds the loop):  
  `"#{_dp('workato_service', '[TRIGGER_AS]', 'request', 'payments').parse_json}"`  
  where `[TRIGGER_AS]` is the trigger's `as` identifier (e.g., `"10aff7cc"` or the alias set in Prompt 0)
- Inside `each.block`, a `rescue` placeholder must be the **last sibling** — add it now

Each current item is accessed via datapills with path segment `'*'` (current_item):  
`_dp('workato', 'payment_loop', '*', 'fieldName')`

Reference: `Workato/RecipeComponents/forEach.json`, `Workato/RecipeComponents/For Each.json`

---

### Prompt 4: Add payment type if/elsif/else branching

Inside `each.block` (before the `rescue` placeholder), add an `if` step:

**Check condition (if):**
- `keyword`: `"if"`
- `provider`: `"workato"`
- `name`: `"if"`
- `as`: `"payment_type_branch"`
- `input.operand_1`: datapill for current payment `type` field  
  Pill: `_dp('workato', 'payment_loop', '*', 'type')`
- `input.operand_2`: `"Check"`
- `input.operator`: `"equals"`
- `input.type`: `"compound"`

After the `if` block, add an `elsif` sibling (for ACH) and an `else` sibling (for Default):

**elsif condition:**
- `operand_1`: same `type` datapill
- `operand_2`: `"ACH"`
- `operator`: `"equals"`

**else:** no condition — covers Other, Wire, and any unmapped type.

Reference: `Workato/RecipeComponents/IF-ELSE.json`

---

### Prompt 5: Check path — Connection + invokeGetUniquePayee (HTTP POST)

**First, create the CheckWriter HTTP connection:**
- App: `rest`
- Name: `GLDFundingEngine_CheckWriter_Connection`
- Base URL: `https://expressgateway.keybank.internal/checkwriter` *(placeholder — replace with SME URL)*
- Auth method: confirm with SME (Bearer token or Basic)

Inside the `if` (Check) block, add HTTP POST action:

- `keyword`: `"action"`
- `provider`: `"rest"`
- `name`: `"make_request_v2"`
- `as`: `"get_unique_payee"`
- Connection: `GLDFundingEngine_CheckWriter_Connection`
- `input.request_name`: `"invokeGetUniquePayee"`
- HTTP method: `POST`
- URL path: `/invokeGetUniquePayee` *(confirm endpoint with SME)*
- Request body (set as `extended_input_schema` and `input`):

| Request Field | Workato Source |
|---|---|
| PayeeName | `payment_loop['payee']['name']` |
| AddressLine1 | `payment_loop['payee']['address1']` |
| AddressLine2 | `payment_loop['payee']['address2']` |
| City | `payment_loop['payee']['city']` |
| State | `payment_loop['payee']['state_province']` |
| PostalCode | `payment_loop['payee']['zip']` |
| PhoneNumber | `payment_loop['payee']['phone']` |
| FaxNumber | `payment_loop['payee']['fax']` |
| ContactName | `payment_loop['payee']['contactName']` |
| ContactPhoneNumber | `payment_loop['payee']['contactPhone']` |
| Country | `"USA"` (static) |

**Expected response output:** `payeeKey` field in response body.

Reference: `Workato/RecipeComponents/HTTP.json`

---

### Prompt 6: Check path — Conditional invokeAddNewPayee (if payeeKey empty)

After `get_unique_payee`, add a nested `if` inside the Check block:

**Condition:**
- `operand_1`: `get_unique_payee` response → `payeeKey`  
  Pill: `_dp('rest', 'get_unique_payee', 'response', 'payeeKey')`
- `operator`: `"is_empty"` (or `"equals"` with `""`)

Inside this nested `if.block`, add HTTP POST action:

- `as`: `"add_new_payee"`
- Connection: `GLDFundingEngine_CheckWriter_Connection`
- URL path: `/invokeAddNewPayee` *(confirm with SME)*
- Request body: identical PayeeInformation fields as Prompt 5

**Combined payeeKey formula** (to use in next step):  
`"#{_dp('rest','get_unique_payee','response','payeeKey').presence || _dp('rest','add_new_payee','response','payeeKey')}"`

---

### Prompt 7: Check path — invokeCreateCheckRequest (HTTP POST)

After the nested payeeKey if/action, add HTTP POST action to create the check:

- `as`: `"create_check_request"`
- Connection: `GLDFundingEngine_CheckWriter_Connection`
- URL path: `/invokeCreateCheckRequest` *(confirm with SME)*
- Request body:

| Request Field | Workato Source |
|---|---|
| PayeeKey | Combined formula from Prompt 6 |
| Notes | `payment_loop['invoiceReference']` |
| Comments | `payment_loop['comment']` |
| CheckAmount | `payment_loop['amount']` |
| Memo | `payment_loop['checkMemo']` |
| PayeeName | `payment_loop['payee']['name']` |
| LeaseNumber | Trigger `id` field: `_dp('workato_service', '[TRIGGER_AS]', 'request', 'id')` |

---

### Prompt 8: ACH path — invokeInsertPayment (HTTP POST, elsif block)

**First, create the ACH HTTP connection** (if not already):
- App: `rest`
- Name: `GLDFundingEngine_ACH_Connection`
- Base URL: `https://gld-ach.keybank.internal` *(placeholder — replace with SME URL)*

Inside the `elsif` (ACH) block, add HTTP POST action:

- `as`: `"insert_payment"`
- Connection: `GLDFundingEngine_ACH_Connection`
- URL path: `/insertPayment` *(confirm with SME)*
- Request body:

| Request Field | Value / Workato Source |
|---|---|
| APP_ID | Trigger `id` |
| CUSTOMER_NAME | Trigger `customerName` |
| CUSTOMER_ID | Trigger `customerID` |
| SOURCE | Trigger `sourceName` |
| PAYEE_NAME | `payment_loop['payee']['name']` |
| PAYEE_ID | `payment_loop['payee']['id']` |
| AMOUNT | `payment_loop['amount']` |
| REFERENCE | `payment_loop['invoiceReference']` |
| ROUTING_NUMBER | `payment_loop['payee']['routingNumber']` |
| ACCOUNT_NUMBER | `payment_loop['payee']['accountNumber']` |
| REQUESTOR_ID | `"1"` (static — hardcoded in webMethods source) |

Reference: `Workato/RecipeComponents/HTTP.json`

---

### Prompt 9: Default path — Log step (else block)

Inside the `else` block (covers Other, Wire, and any unrecognized type):

Add a Log step:

- `keyword`: `"action"`
- `provider`: `"logger"`
- `name`: `"create_message"`
- `input.message`: `"Payment #{payment_loop['id']} type #{payment_loop['type']} — Default path (no external processor called)"`

Reference: `Workato/RecipeComponents/Log.json`

---

### Prompt 10: Add the rescue block (per-payment error handler)

**Create GLDMessageLog HTTP connection** (if not already):
- App: `rest`
- Name: `GLDFundingEngine_MessageLog_Connection`
- Base URL: `https://gld-messagelog.keybank.internal` *(placeholder — replace with SME URL)*

Add `rescue` block as the **last sibling** inside `each.block`:

- `keyword`: `"rescue"`
- `provider`: `"workato"`
- Inside `rescue.block`, add HTTP POST action:

- `as`: `"log_payment_error"`
- Connection: `GLDFundingEngine_MessageLog_Connection`
- URL path: `/LogXMLRequest`
- Request body:

| Field | Value |
|---|---|
| AppID | `"3"` (static) |
| Request | `error['message']` (error datapill available in rescue scope) |
| RequestIdentifier1 | `payment_loop['id']` |
| RequestIdentifier2 | `payment_loop['type']` |
| RequestIdentifier3 | Trigger `id` |
| RequestDoc | JSON-serialized current payment |

Reference: `Workato/RecipeComponents/HTTP.json`

---

### Prompt 11: Add outer catch block + send_reply

**Outer catch block** — last sibling inside `try.block`:

- `keyword`: `"catch"`
- `provider`: `"workato"`
- Inside `catch.block`, add HTTP POST to `GLDFundingEngine_MessageLog_Connection`:

| Field | Value |
|---|---|
| AppID | `"3"` |
| Request | `error['message']` |
| RequestIdentifier1 | `"FundingEngine outer error"` |
| RequestDoc | `"processFundingRequest"` |

**send_reply step** — add AFTER the `try`/`catch` pair (sibling of `try`, not inside it):

- `keyword`: `"action"`
- `provider`: `"workato_service"`
- `name`: `"send_reply"`
- `input.reply`: collected paymentResponses as JSON string  
  (Note: Workato `each` collects output per iteration — reference the `payment_loop` results)

Reference: `Workato/RecipeComponents/WorkatoServiceSendReply.json`

---

### Prompt 12: Wire the config array

Set the recipe's top-level `config` array:

```json
[
  {"keyword":"application","provider":"workato_service","skip_validation":false,"account_id":null},
  {"keyword":"application","provider":"rest","skip_validation":false,"account_id":"[CHECKWRITER_CONN_ID]"},
  {"keyword":"application","provider":"rest","skip_validation":false,"account_id":"[ACH_CONN_ID]"},
  {"keyword":"application","provider":"rest","skip_validation":false,"account_id":"[MESSAGELOG_CONN_ID]"}
]
```

Replace `[..._CONN_ID]` with the actual `account_id` values returned when the connections were created (GET `/api/connections`).

---

### Prompt 13: Verify Recipe 1 — FundingEngine

After pushing, verify this structure via GET `/api/recipes/[RECIPE_ID]`:

```
[0] trigger: workato_service/receive_request — "FundingEngine" (flat 7-field schema)
  [1] try:
    [2] each: payment_loop (source: trigger.payments.parse_json)
      [3] if: payment_loop.type == "Check"
        [4] HTTP POST → get_unique_payee (invokeGetUniquePayee)
        [5] if: payeeKey is empty
          [6] HTTP POST → add_new_payee (invokeAddNewPayee)
        [7] HTTP POST → create_check_request (invokeCreateCheckRequest)
      [8] elsif: payment_loop.type == "ACH"
        [9] HTTP POST → insert_payment (insertPayment, 11 params)
      [10] else: (Other/Wire)
        [11] Log → "Default path"
      [rescue]:  ← last in each.block
        [12] HTTP POST → log_payment_error (LogXMLRequest, AppID=3)
    [catch]:  ← last in try.block
      [13] HTTP POST → log_outer_error (LogXMLRequest, AppID=3)
  [14] send_reply: paymentResponses
config: [workato_service(null), CheckWriter(rest), ACH(rest), MessageLog(rest)]
```

---

## Recipe 2 Build Prompts — processACHBatch

---

### Prompt 14: Create Recipe 2 skeleton

Create a new Workato recipe named **"processACHBatch"** in folder **migrAIte_Training/webMethodsMigration** (folderId `32050036`).

- Trigger type: `scheduled_event/timer`
- Schedule: daily at `[SME_TIME]` (placeholder)
- Body: empty for now

---

### Prompt 15: Oracle connection + getSystemDateTime

**Create Oracle connection:**
- App: `oracle`
- Name: `GLDFundingEngine_Oracle_Connection`
- Host: `[SME_ORACLE_HOST]`
- Port: `[SME_ORACLE_PORT]`
- SID: `[SME_ORACLE_SID]`
- Credentials: from SME

Add Step 1 — Oracle `select_rows`:

- `as`: `"get_sysdate"`
- Connection: `GLDFundingEngine_Oracle_Connection`
- SQL: `SELECT SYSDATE AS SYS_DATE FROM DUAL`
- Output: `SYS_DATE` → used as `maxDateTime` in next step

Reference: `Workato/RecipeComponents/OracleSearchRows.json`

---

### Prompt 16: selectACHBatch Oracle query

Add Step 2 — Oracle `select_rows`:

- `as`: `"select_ach_batch"`
- Connection: `GLDFundingEngine_Oracle_Connection`
- SQL: `SELECT ROUTING_NUMBER, ACCOUNT_NUMBER, AMOUNT, REFERENCE, PAYEE_NAME FROM GLD_SCHEMA.ACH_PAYMENTS WHERE CREATE_DATE <= :maxDateTime`
  *(Confirm exact table name and column names with SME)*
- Input parameter: `maxDateTime` = `get_sysdate.SYS_DATE`
- Output: `results` array — columns: ROUTING_NUMBER, ACCOUNT_NUMBER, AMOUNT, REFERENCE, PAYEE_NAME

---

### Prompt 17: getNextBatchID Oracle query

Add Step 3 — Oracle `select_rows`:

- `as`: `"get_next_batch_id"`
- Connection: `GLDFundingEngine_Oracle_Connection`
- SQL: `SELECT GLD_BATCH_SEQ.NEXTVAL AS NEXT_BATCH_ID FROM DUAL`
  *(Confirm Oracle sequence name with SME)*
- Output: `NEXT_BATCH_ID` → variable `batchID`

---

### Prompt 18: Add each loop over ACH batch rows

Add Step 4 — `each` loop:

- `as`: `"ach_batch_loop"`
- Source: `select_ach_batch.results[]`

Inside `ach_batch_loop.block`, collect the following NACHA fields per row:

| NACHA Field | Source | Value/Datapill |
|---|---|---|
| Routing/Transit Number | Oracle | `ach_batch_loop.ROUTING_NUMBER` |
| Individual Account Number | Oracle | `ach_batch_loop.ACCOUNT_NUMBER` |
| Amount | Oracle | `ach_batch_loop.AMOUNT` |
| Individual ID Number | Oracle | `ach_batch_loop.REFERENCE` |
| Individual Name | Oracle | `ach_batch_loop.PAYEE_NAME` |
| Trace Number | Step 3 output | `get_next_batch_id.NEXT_BATCH_ID` |
| Transaction Code | static | `"22"` (checking account credit) |
| Record Type Code | static | `"6"` (PPD detail record) |
| Addenda Indicator | static | `"0"` (no addenda) |
| Discretionary Data | static | `""` (blank) |

Add a Log step per row to capture the fields:
- `input.message`: `"NACHA_ROW: routing=#{ach_batch_loop.ROUTING_NUMBER} account=#{ach_batch_loop.ACCOUNT_NUMBER} amount=#{ach_batch_loop.AMOUNT}"`

---

### Prompt 19: ⚠️ NACHA Generation Gap — Custom Formula Step

**HIGH GAP — webMethods `pub.flatFile:convertToString` has no native Workato equivalent.**

webMethods converts a structured NACHA_SchemaDT document tree to a fixed-width NACHA ACH file (94 chars/record per NACHA specification). Workato has no built-in flat-file serializer.

**Stub implementation until SME provides NACHA file spec:**

Add a Log step:
- `input.message`: `"NACHA_STUB: Batch #{batchID} — #{select_ach_batch.results.size} records pending file generation. See NACHA implementation notes."`

**Full implementation requires:**

1. SME provides: Company Name, Company ID, Company Entry Description, Effective Entry Date
2. Implement NACHA PPD record format (94 char fixed-width) as a custom Ruby formula:
   - File Header Record (Type 1)
   - Batch Header Record (Type 5)  
   - Entry Detail Records (Type 6) — one per row from Step 4
   - Batch Control Record (Type 8)
   - File Control Record (Type 9)
3. If file delivery via FTP/SFTP is needed: use `Workato/RecipeComponents/SFTP.json` and wire to SFTP connector with SME credentials

**NACHA PPD Entry Detail Record layout (94 chars):**
```
Pos 01     : Record Type Code (1) = "6"
Pos 02-03  : Transaction Code (2) = "22"
Pos 04-12  : Routing Transit Number (9)
Pos 13-29  : Individual Account Number (17, space padded right)
Pos 30-39  : Amount in cents (10, zero padded)
Pos 40-54  : Individual ID Number (15, space padded right)
Pos 55-76  : Individual Name (22, space padded right)
Pos 77     : Discretionary Data (1)
Pos 78     : Addenda Indicator (1) = "0"
Pos 79-94  : Trace Number (15, zero padded)
```

Reference: `Workato/RecipeComponents/SFTP.json`

---

### Prompt 20: Email notification step

Add Step 6 — Email action:

**Create email connection** (if not already):
- App: `gmail` or SMTP
- Name: `GLDFundingEngine_Email_Connection`

**Action configuration:**
- `provider`: `"gmail"`
- `name`: `"send_email"`
- `as`: `"send_batch_notification"`
- To: `[SME_RECIPIENT_EMAIL]`
- Subject: `"ACH Batch Processed — #{scheduled_at}"`
- Body: `"ACH batch completed. Records processed: #{select_ach_batch.results.size}. Batch ID: #{get_next_batch_id.NEXT_BATCH_ID}"`

Reference: `Workato/RecipeComponents/Email.json`

---

### Prompt 21: try/catch wrapper for Recipe 2

Wrap all Recipe 2 steps (15–20) in a `try` block. Add `catch` as last sibling:

**catch.block** — HTTP POST to `GLDFundingEngine_MessageLog_Connection`:

| Field | Value |
|---|---|
| AppID | `"3"` |
| Request | `"processACHBatch failed: #{error.message}"` |
| RequestIdentifier1 | `"processACHBatch"` |
| RequestDoc | `"ACH batch error"` |

---

### Prompt 22: Verify Recipe 2 structure

```
[0] trigger: scheduled_event/timer (daily)
  [1] try:
    [2] Oracle select_rows → get_sysdate (SYSDATE)
    [3] Oracle select_rows → select_ach_batch (WHERE <= maxDateTime)
    [4] Oracle select_rows → get_next_batch_id (NEXTVAL)
    [5] each → ach_batch_loop (source: select_ach_batch.results)
      [5a] Log: NACHA record fields per row
    [6] ⚠️ Log: NACHA_STUB (pending full implementation — SME input needed)
    [7] Gmail/Email → send_batch_notification
    [catch]:
      [8] HTTP POST → log_batch_error (LogXMLRequest)
config: [oracle, rest (MessageLog), gmail]
```

---

## Summary Table

| Prompt | Recipe | Component | App/Action | Connection | Notes |
|---|---|---|---|---|---|
| 0 | 1 | Recipe skeleton | workato_service | — | |
| 1 | 1 | Trigger schema (flat 7 fields) | workato_service/receive_request | — | No nested objects |
| 2 | 1 | Outer try block | workato/try | — | |
| 3 | 1 | each payment loop | workato/each | — | source: payments.parse_json |
| 4 | 1 | if/elsif/else payment type branch | workato/if | — | |
| 5 | 1 | HTTP: invokeGetUniquePayee | rest/make_request_v2 | CheckWriter | 10 payee fields + Country="USA" |
| 6 | 1 | if payeeKey empty → HTTP: invokeAddNewPayee | rest/make_request_v2 | CheckWriter | Combined `.presence \|\|` formula |
| 7 | 1 | HTTP: invokeCreateCheckRequest | rest/make_request_v2 | CheckWriter | PayeeKey + 6 check fields |
| 8 | 1 | HTTP: insertPayment (ACH) | rest/make_request_v2 | ACH | 11 params incl. REQUESTOR_ID="1" |
| 9 | 1 | Log: Default path | logger/create_message | — | |
| 10 | 1 | rescue: log_payment_error | rest/make_request_v2 | MessageLog | Per-payment error isolation |
| 11 | 1 | catch + send_reply | workato_service/send_reply | — | |
| 12 | 1 | Wire config array | — | 3 HTTP connections | |
| 13 | 1 | Verify structure | — | — | |
| 14 | 2 | Recipe skeleton | scheduled_event/timer | — | |
| 15 | 2 | Oracle: getSystemDateTime | oracle/select_rows | Oracle | SELECT SYSDATE |
| 16 | 2 | Oracle: selectACHBatch | oracle/select_rows | Oracle | WHERE create_date <= maxDateTime |
| 17 | 2 | Oracle: getNextBatchID | oracle/select_rows | Oracle | NEXTVAL sequence |
| 18 | 2 | each: ach_batch_loop | workato/each | — | NACHA field collection |
| 19 | 2 | ⚠️ NACHA generation | Custom formula | — | **GAP — SME input required** |
| 20 | 2 | Email: sendEmail | gmail/send_email | Email | |
| 21 | 2 | try/catch wrapper | workato | MessageLog | |
| 22 | 2 | Verify structure | — | — | |

**Connections to create: 5** (CheckWriter, ACH, MessageLog, Oracle, Email)  
**SME inputs needed: 8** (see table at top)  
**Critical gaps: 1 HIGH** (NACHA generation), **2 INFO** (updateBatchIDs + FTP both disabled in source)
