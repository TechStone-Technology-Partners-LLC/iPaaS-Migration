# Package Analysis — `GLDFundingEngine20080714` → Workato

**Workato-oriented migration blueprint.**
Source analysis: [`WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md`](../Analysis/GLDFundingEngine20080714_Analysis.md) (analysis codename **AVOCADO**).
Construct mapping reference: `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx` (22 mappings).
Status: **awaiting approval — no Workato assets created yet.**

---

## 1. Package Overview

### What the integration does

`GLDFundingEngine` is KeyBank's **payment disbursement router** for the GLD / Blue Ocean lease-origination platform. A front-end system submits a *funding request* — one loan/lease application plus a list of payments to disburse — and the engine routes **each payment** to the correct downstream payment system based on its `type`.

Two independent runtime paths exist in the package:

| Path | Trigger | Purpose |
|---|---|---|
| **A. Synchronous funding request** (primary) | SOAP request | Route each payment: Check → CheckWriter; ACH → staging DB; other → no-op |
| **B. Nightly ACH batch** (secondary) | IS scheduled task (defined outside the package) | Drain the ACH staging table into a NACHA fixed-width file, FTP + email it |

### Systems involved

| System | Role | Access method in webMethods |
|---|---|---|
| GLD / Blue Ocean front end | Caller | SOAP over HTTP into IS directive `GLDFundingEngine` |
| **CheckWriter** (via `GLDExpressGateway`) | Check issuance | webMethods flow services in a sibling package |
| **ACH staging database** (Oracle, via `GLD_ACHAdaptersServices`) | ACH payment queue | webMethods **JDBC adapter services** |
| **GLDMessageLog** | XML request/response audit log | Flow service backed by a DB |
| **WSRProcessStatistics** | Enterprise error/statistics publisher | Flow service publishing to the broker |
| **Bank ACH FTP host** | NACHA file delivery | `pub.client:ftp` |
| **SMTP / email** | ACH file notification | `WSRCommon.Utilities.FlowServices:sendEmail` |

### Data flow (Path A)

```
GLD front end
   │  SOAP: fundingEngineWrapper (applicationInfo + payments[])
   ▼
fundingEngineWrapper ── log request ──► GLDMessageLog (AppID=3, id="FE")
   │
   ▼
processFundingRequest
   │  for each payment:
   │     type == "Check" ──► CheckWriter: getUniquePayee → [addNewPayee] → createCheckRequest  → status "Paid"
   │     type == "ACH"   ──► ACH DB: insertPayment (11 cols)                                    → status "Paid"
   │     else            ──► (no external call)                                                 → status "Default"
   │     on error        ──► GLDMessageLog + publishErrorDoc, status "Error", CONTINUE loop
   ▼
fundingEngineWrapper ── log response ──► GLDMessageLog
   │
   ▼  SOAP response: paymentResponses[] + Errors[]
GLD front end
```

### Scope decision

| Source service | Migrate? | Rationale |
|---|---|---|
| `Wrappers:fundingEngineWrapper` | **Merged into the recipe** | Its SOAP wrap/unwrap is transport plumbing that Workato's trigger handles natively; its two audit-log calls are preserved as recipe steps |
| `MainFlows:processFundingRequest` | **YES — this is the recipe** | Core business logic |
| `MainFlows:processACHBatch` | **NO — Phase 2** | NACHA generation is a HIGH gap (see §9); belongs in a separate scheduled recipe |
| `MainFlows:processACHBatch_venkat` | **NO** | Dead developer duplicate |
| `Wrappers.Registration:register/unregisterFlowServiceForSOAP` | **NO** | webMethods SOAP-processor lifecycle; no Workato equivalent needed — the callable-recipe endpoint replaces it |

---

## 2. Shapes & Logic Breakdown

Every shape in `processFundingRequest` (+ the wrapper), with its Workato equivalent. Mapping-file row numbers refer to the Agent Bridge workbook.

| # | webMethods shape | Detail | Workato equivalent | Bridge row |
|---|---|---|---|---|
| 1 | SOAP processor registration + `pub.soap.utils:getBody` + `pub.xml:xmlNodeToDocument` | Receive & parse request | **Trigger:** `workato_service/receive_request` (callable recipe) with a typed input schema | — (deviation, §9 G-1) |
| 2 | `INVOKE GLDMessageLog:LogXMLRequest` | Audit inbound XML, AppID=3, id="FE" | **HTTP action** `POST` to GLDMessageLog | row 22 (INVOKE HTTP) |
| 3 | `SEQUENCE EXIT-ON=SUCCESS` + `SEQUENCE EXIT-ON=FAILURE` | Outer TRY | **`handle_error` (try) block** | rows 2, 11 |
| 4 | `MAP STANDALONE` — init response, `REQUESTOR="1"` | Constant init | Inline static value in the ACH action input (`REQUESTOR_ID = 1`) | row 21 (MAP) |
| 5 | `LOOP IN-ARRAY=.../payment` | Iterate payments | **`repeat_for_each`** over `payments`, list alias `payment_loop` | row 12 (LOOP) |
| 6 | `SEQUENCE EXIT-ON=SUCCESS/FAILURE` inside LOOP | Per-payment TRY | **`rescue` block inside the loop** — keeps the loop going | rows 2, 3 |
| 7 | `BRANCH SWITCH=payment/type` | 3-way router | **`if` / `elsif` / `else`** chain (value equality) | rows 6, 10 (CASE/SWITCH) |
| 8 | `SEQUENCE NAME="Check"` | Check path | `if` clause: `payment.type == "Check"` | row 5 |
| 9 | `INVOKE CheckWriter:invokeGetUniquePayee` | Payee search, 11 fields | **HTTP action** `POST /invokeGetUniquePayee` | row 22 |
| 10 | `BRANCH SWITCH=/payeeKey`, label `$null` | Payee not found? | **Nested `if`**: `payeeKey is_blank` | row 5 |
| 11 | `INVOKE CheckWriter:invokeAddNewPayee` | Create payee | **HTTP action** `POST /invokeAddNewPayee` | row 22 |
| 12 | `INVOKE CheckWriter:invokeCreateCheckRequest` | Create check, 7 fields | **HTTP action** `POST /invokeCreateCheckRequest` | row 22 |
| 13 | `MAP` → status `"Paid"` | Response row | Logger / response accumulator step | row 21 |
| 14 | `SEQUENCE NAME="ACH"` | ACH path | **`elsif`** clause: `payment.type == "ACH"` | row 8 (ELSEIF) |
| 15 | `INVOKE GLD_ACHAdaptersServices:insertPayment` | JDBC adapter insert, 11 params | **Oracle connector — `execute_stored_procedure`** (`GLD_ACH.INSERTPAYMENT`) | row 20 (INVOKE DB) |
| 16 | `MAP` → status `"Paid"` | Response row | Logger / response accumulator step | row 21 |
| 17 | `SEQUENCE NAME="$default"` | Fallback path | **`else`** clause | row 7 (ELSE) |
| 18 | `MAP` → status `"Default"` | Response row, no external call | Logger step | rows 7, 21 |
| 19 | `SEQUENCE EXIT-ON=DONE` (per-payment) | Per-payment CATCH | **`rescue` clause of the loop's error block** | row 3 |
| 20 | `INVOKE pub.flow:getLastError` | Fetch error | Workato `error` datapill — **no step needed** | — (deviation, §9 G-5) |
| 21 | `INVOKE GLDMessageLog:LogXMLRequest` (`ERROR - processing payment`) | Log payment error | **HTTP action** inside `rescue` | row 22 |
| 22 | `MAPINVOKE pub.list:appendToDocumentList` | Append to `Errors[]` | Implicit — collect within the loop | row 21 |
| 23 | `INVOKE WSRProcessStatistics:publishErrorDoc` | Publish error doc | **HTTP action** (see §9 G-4) | row 22 |
| 24 | `SEQUENCE EXIT-ON=DONE` (outer) | Request-level CATCH | **`catch` clause of the outer error block** | row 3 |
| 25 | `INVOKE GLDMessageLog:LogXMLRequest` (`ERROR - processFundingRequest`) | Log system error | **HTTP action** inside `catch` | row 22 |
| 26 | `INVOKE GLDMessageLog:LogXMLResponse` | Audit response | **HTTP action** | row 22 |
| 27 | `pub.xml:documentToXMLString` + `xmlStringToXMLNode` + `createSoapData` + `addBodyEntry` | Build SOAP response | **`workato_service/send_reply`** | — (deviation, §9 G-1) |
| 28 | `BRANCH SWITCH=/debug` + `savePipelineToFile` / `restorePipelineFromFile` | Debug harness | **NOT MIGRATED** (§9 G-8) | — |
| 29 | 50+ `MAPDELETE` pipeline drops | Pipeline hygiene | **No equivalent needed** — Workato has no shared pipeline | — |

---

## 3. Connections

| # | Connection name (proposed) | Workato connector | Purpose | Steps served | Status |
|---|---|---|---|---|---|
| C-1 | `GLDFundingEngine_CheckWriter_Connection` | **HTTP** (custom action) | CheckWriter gateway — payee search, payee create, check request | 9, 11, 12 | ❗ Must be created in the Workato GUI. Base URL unknown — SME input required. Placeholder: `https://gldexpressgateway.keybank.internal` |
| C-2 | `MIG_WM_GLD_Oracle_Connection` | **Oracle** | ACH staging database (`insertPayment`) | 15 | ✅ Candidate exists in the workspace (ID `19657520`, created for the GLD Compliance migration). Must be confirmed to point at the **ACH** schema and authorized. |
| C-3 | `GLDFundingEngine_MessageLog_Connection` | **HTTP** | GLDMessageLog XML request/response audit log | 2, 21, 25, 26 | ❗ Must be created in the GUI. Placeholder: `https://gldmessagelog.keybank.internal` |
| C-4 | `GLDFundingEngine_ProcessStats_Connection` | **HTTP** | WSRProcessStatistics `publishErrorDoc` | 23 | ❗ Optional — see §9 G-4 |
| C-5 | *(none)* | **Workato callable-recipe service** | Recipe trigger + reply — built in, no connection required | trigger, reply | ✅ No action |

**Connector-selection rationale (per Instruction_Workato.md “find the best connector”):**
- `insertPayment` is a **webMethods JDBC adapter service**, not an HTTP call. The purpose-built Workato equivalent is the **Oracle connector**, not generic HTTP. Bridge row 20 confirms: *INVOKE (DB) → oracle connector action*.
- CheckWriter / GLDMessageLog / WSRProcessStatistics are **webMethods flow services in sibling packages**. There is no Workato connector for "a webMethods flow service". Since these were exposed over HTTP within the IS estate, the **HTTP connector** is the accurate choice. Flagged in §9 (G-2).

---

## 4. Operations

| # | webMethods operation | Kind | Workato action | Connection | Key inputs |
|---|---|---|---|---|---|
| O-1 | `GLDMessageLog:LogXMLRequest` (inbound) | flow service | `http/post` | C-3 | `RequestDoc` = full request, `RequestIdentifier1` = `"FE"`, `AppID` = `3` → returns `MessageLogID` |
| O-2 | `CheckWriter:invokeGetUniquePayee` | flow service | `http/post` | C-1 | `PayeeInformation` (11 fields, §5.1) → returns `payeeKey` |
| O-3 | `CheckWriter:invokeAddNewPayee` | flow service | `http/post` | C-1 | Same `PayeeInformation` payload → returns `payeeKey` |
| O-4 | `CheckWriter:invokeCreateCheckRequest` | flow service | `http/post` | C-1 | `CheckRequest` (7 fields, §5.3) |
| O-5 | `GLD_ACHAdaptersServices:insertPayment` | **JDBC adapter (insert)** | **`oracle/execute_stored_procedure`** — `GLD_ACH.INSERTPAYMENT` | C-2 | 11 params (§5.4) |
| O-6 | `GLDMessageLog:LogXMLRequest` (payment error) | flow service | `http/post` | C-3 | `Request` = error message, `RequestIdentifier1` = `"ERROR - processing payment"`, `AppID` = `3` |
| O-7 | `GLDMessageLog:LogXMLRequest` (system error) | flow service | `http/post` | C-3 | `Request` = error message, `RequestIdentifier1` = `"ERROR - processFundingRequest"`, `AppID` = `3` |
| O-8 | `GLDMessageLog:LogXMLResponse` | flow service | `http/post` | C-3 | `MessageLogID` = O-1 result, `ResponseDoc`, `ResponseIdentifier4` = `"FE"` |
| O-9 | `WSRProcessStatistics:publishErrorDoc` | flow service (broker publish) | `http/post` (optional) | C-4 | `errorDoc` (7 static fields, §5.6) |
| O-10 | `pub.soap.utils:*` / `pub.xml:*` | built-in | **replaced by trigger/reply** | — | — |
| O-11 | `pub.flow:getLastError` | built-in | **replaced by `error` datapill** | — | — |

### Phase-2 operations (ACH batch — not built now)

| # | Operation | Workato equivalent |
|---|---|---|
| O-12 | `getSystemDateTime` | `oracle/select` — `SELECT SYSDATE FROM DUAL` |
| O-13 | `selectACHBatch` | `oracle/select_rows` with `maxDateTime` bind |
| O-14 | `getNextBatchID` | `oracle/select` on the batch-id sequence |
| O-15 | `pub.flatFile:convertToString` (NACHA) | **No native equivalent** — see §9 G-3 |
| O-16 | `updateBatchIDs` | `oracle/update_rows` |
| O-17 | `pub.client:ftp` | **FTP/SFTP connector** — `upload_file` |
| O-18 | `sendEmail` | **Email connector** — `send_email` with attachment |

---

## 5. Data Mappings

### 5.1 Trigger input schema (from `fundingEngineWrapperInput`)

Workato callable-recipe triggers work best with a flat top level plus one JSON payload for the repeating group.

| Trigger field | Type | Source path | Required |
|---|---|---|---|
| `id` | string | `applicationInfo/id` | yes |
| `customerName` | string | `applicationInfo/customerName` | yes |
| `customerID` | string | `applicationInfo/customerID` | yes |
| `sourceName` | string | `applicationInfo/sourceName` | yes |
| `sourceSubCategory` | string | `applicationInfo/sourceSubCategory` | no (unused downstream — carried for fidelity) |
| `salesRepName` | string | `applicationInfo/salesRepName` | no (unused downstream — carried for fidelity) |
| `payments` | string (JSON array) | `payments/payment[]` | yes |

`payments` is parsed in the loop with `.parse_json`. Each element:

```
{ "id", "type", "amount", "invoiceReference", "comment", "checkMemo",
  "status", "glCode", "glAmount", "glDescription",
  "payee": { "id","type","name","address1","address2","city","state_province",
             "zip","phone","fax","contactName","contactPhone",
             "routingNumber","accountNumber" } }
```

### 5.2 O-2 / O-3 — `PayeeInformation` (CheckWriter payee search & create)

| Workato source pill | Target field | Transformation |
|---|---|---|
| `payment_loop.payee.name` | `PayeeName` | direct |
| `payment_loop.payee.address1` | `AddressLine1` | direct |
| `payment_loop.payee.address2` | `AddressLine2` | direct |
| `payment_loop.payee.city` | `City` | direct |
| `payment_loop.payee.state_province` | `State` | direct |
| `payment_loop.payee.zip` | `PostalCode` | direct |
| `payment_loop.payee.phone` | `PhoneNumber` | direct |
| `payment_loop.payee.fax` | `FaxNumber` | direct |
| `payment_loop.payee.contactName` | `ContactName` | direct |
| `payment_loop.payee.contactPhone` | `ContactPhoneNumber` | direct |
| — | `Country` | **static `"USA"`** |

### 5.3 O-4 — `CheckRequest`

| Workato source pill | Target field | Transformation |
|---|---|---|
| `payeeKey` (from O-2, or O-3 if created) | `PayeeKey` | direct |
| `payment_loop.invoiceReference` | `Notes` | direct |
| `payment_loop.comment` | `Comments` | direct |
| `payment_loop.amount` | `CheckAmount` | direct |
| `payment_loop.checkMemo` | `Memo` | direct |
| `payment_loop.payee.name` | `PayeeName` | direct |
| `id` (trigger, `applicationInfo/id`) | `LeaseNumber` | direct |

### 5.4 O-5 — `GLD_ACH.INSERTPAYMENT` stored-procedure parameters

| # | Parameter | Workato source pill | Transformation |
|---|---|---|---|
| 1 | `APP_ID` | trigger `id` | direct |
| 2 | `CUSTOMER_NAME` | trigger `customerName` | direct |
| 3 | `CUSTOMER_ID` | trigger `customerID` | direct |
| 4 | `SOURCE` | trigger `sourceName` | direct |
| 5 | `PAYEE_ID` | `payment_loop.payee.id` | direct |
| 6 | `PAYEE_NAME` | `payment_loop.payee.name` | direct |
| 7 | `AMOUNT` | `payment_loop.amount` | direct |
| 8 | `REFERENCE` | `payment_loop.invoiceReference` | direct |
| 9 | `ROUTING_NUMBER` | `payment_loop.payee.routingNumber` | direct |
| 10 | `ACCOUNT_NUMBER` | `payment_loop.payee.accountNumber` | direct |
| 11 | `REQUESTOR_ID` | — | **static `"1"`** (was pipeline var `REQUESTOR`) |

### 5.5 Response mapping (`fundingEngineWrapperOutput`)

| Target | Value |
|---|---|
| `paymentResponse[].id` | `payment_loop.id` |
| `paymentResponse[].status` | `"Paid"` (Check) · `"Paid"` (ACH) · `"Default"` (else) · `"Error"` (rescue) |
| `paymentResponse[].errorDescription` | `error.message` (rescue only) |
| `Errors[].errorDescription` | `error.message` (outer catch) |
| `Errors[].errorCode` | `MessageLogID` from O-7 |

Final `send_reply` returns `status = "PAYMENTS_PROCESSED"` plus the accumulated payment responses.

### 5.6 Error-document static fields (O-9)

| Field | Value |
|---|---|
| `severity_level` | `CRITICAL` |
| `appl_id` | `GLD` |
| `entry_type` | `E` |
| `sender_id` | `EFW` |
| `receiver_id` | `WMB` |
| `transaction_type` | `XML` |
| `service_name` | `GLDExpressGateway.MainFlows.EFW:processLXIRequest` ⚠ *source defect — see §9 G-9* |
| `system_message` | `error.message` |

---

## 6. Business Rules & Conditions

| # | Rule | Source shape | Workato implementation |
|---|---|---|---|
| BR-1 | **Each payment is routed independently by `payment.type`.** | `BRANCH SWITCH=payment/type` | `if` / `elsif` / `else` inside `repeat_for_each` |
| BR-2 | `type == "Check"` → CheckWriter path. **Exact, case-sensitive string match.** | label `Check` | `payment_loop.type` **equals** `Check` |
| BR-3 | `type == "ACH"` → ACH staging insert. **Exact, case-sensitive.** | label `ACH` | `payment_loop.type` **equals** `ACH` |
| BR-4 | Any other type (incl. **Wire**) → **no external call**, status `Default`. | label `$default` | `else` clause — logger only |
| BR-5 | **Create the payee only if the search returned nothing.** | `BRANCH SWITCH=/payeeKey` label `$null` | nested `if`: `payeeKey` **is blank** → `invokeAddNewPayee` |
| BR-6 | If a payee already exists, **reuse the returned key** — do not create a duplicate. | non-null falls through the branch | the nested `if` has no `else` |
| BR-7 | **A failing payment must not stop the other payments.** (source comment: *"On Error Try other payments"*) | per-payment TRY/CATCH inside LOOP | `rescue` block **inside** the `repeat_for_each` |
| BR-8 | **Audit logging must never fail the transaction.** (source comment: *"Do not fail the trxn if the logging to DB fails"*) | `SEQUENCE EXIT-ON=DONE` around each log call | wrap each MessageLog HTTP action in its own error handler / set to continue on error |
| BR-9 | `Country` on a payee search is always `USA`. | `MAPSET` | static field value |
| BR-10 | `REQUESTOR_ID` on every ACH insert is always `1`. | `MAPSET REQUESTOR="1"` | static parameter value |
| BR-11 | Both audit-log calls tag `AppID = 3` (GLD Funding Engine's application id). | `MAPSET AppID="3"` | static field value |
| BR-12 | Request/response audit-log correlation uses identifier `FE`. | `MAPSET` | static field value |
| BR-13 | ACH payments are **not** sent to the bank synchronously — they are staged for the nightly batch. | ACH path ends at `insertPayment` | recipe ends the ACH branch at the Oracle SP; no downstream call |

---

## 7. Error Handling

### Source model (two nested levels)

| Level | webMethods construct | Behaviour |
|---|---|---|
| **Per-payment** | `SEQUENCE EXIT-ON=SUCCESS` → try `EXIT-ON=FAILURE` / catch `EXIT-ON=DONE`, **inside** the LOOP | Catch, log, record `status="Error"` + `errorDescription` on that payment, append to `Errors[]`, publish error doc, **continue to the next payment** |
| **Whole request** | Same idiom at flow top level | Catch, log, put message into `Errors[]` with `errorCode = MessageLogID`, publish error doc, still return a well-formed response |
| **Logging sub-level** | `SEQUENCE EXIT-ON=DONE` wrapping each `LogXMLRequest` | Swallow logging failures entirely |

**Retry:** `retry_max = 0`, `retry_interval = 0` on `processFundingRequest`. **No retry logic exists in the source.** Do not invent one.

### Workato target model

```
try (outer error handler)
└── repeat_for_each  payments
    ├── if / elsif / else   ← business routing
    └── rescue              ← per-payment (BR-7): log error, status "Error", continue loop
catch (outer)               ← log system error, populate Errors[]
send_reply                  ← always returns a response
```

| Source behaviour | Workato mechanism | Bridge row |
|---|---|---|
| Outer TRY | `handle_error` try block | 2 |
| Outer CATCH | `on_error` / `catch` clause | 3 |
| Per-payment TRY/CATCH inside loop | `rescue` block nested inside `repeat_for_each` | 2, 3 |
| Continue loop after a payment error | Native — `rescue` inside the loop resumes the next iteration | 17 (CONTINUE) |
| `pub.flow:getLastError` | `error.message` / `error.type` datapills | — |
| "Do not fail the trxn if logging fails" | Per-step error handling on each MessageLog action | 2, 3 |
| No retry | Leave retry settings at default/off | — |

---

## 8. Equivalent Recipe Structure

**Recipe name:** `GLDFundingEngine — processFundingRequest`
**Type:** Callable recipe (`workato_service/receive_request` → `send_reply`)

```
TRIGGER  workato_service/receive_request   name: "FundingEngine"
         input: id, customerName, customerID, sourceName,
                sourceSubCategory, salesRepName, payments (JSON string)

 1  try  ────────────────────────────────────────────── outer error handler
 2  │  HTTP POST  GLDMessageLog:LogXMLRequest            [C-3]
 3  │     RequestDoc = full request · RequestIdentifier1 = "FE" · AppID = 3
 4  │     → capture MessageLogID
 5  │
 6  │  repeat_for_each  source = payments.parse_json     alias: payment_loop
 7  │  │
 8  │  │  IF  payment_loop.type == "Check"  ───────────── BR-2
 9  │  │  │   HTTP POST CheckWriter:invokeGetUniquePayee [C-1]
10  │  │  │      PayeeName, AddressLine1/2, City, State, PostalCode,
11  │  │  │      PhoneNumber, FaxNumber, ContactName, ContactPhoneNumber,
12  │  │  │      Country = "USA"                          → payeeKey
13  │  │  │
14  │  │  │   IF  payeeKey is blank  ──────────────────── BR-5
15  │  │  │   │   HTTP POST CheckWriter:invokeAddNewPayee [C-1]  → payeeKey
16  │  │  │   (no else — existing key reused)             ── BR-6
17  │  │  │
18  │  │  │   HTTP POST CheckWriter:invokeCreateCheckRequest [C-1]
19  │  │  │      PayeeKey, Notes, Comments, CheckAmount, Memo,
20  │  │  │      PayeeName, LeaseNumber
21  │  │  │   Logger: payment id + status "Paid"
22  │  │  │
23  │  │  ELSIF  payment_loop.type == "ACH"  ──────────── BR-3
24  │  │  │   Oracle execute_stored_procedure  GLD_ACH.INSERTPAYMENT  [C-2]
25  │  │  │      APP_ID, CUSTOMER_NAME, CUSTOMER_ID, SOURCE,
26  │  │  │      PAYEE_ID, PAYEE_NAME, AMOUNT, REFERENCE,
27  │  │  │      ROUTING_NUMBER, ACCOUNT_NUMBER, REQUESTOR_ID = "1"
28  │  │  │   Logger: payment id + status "Paid"
29  │  │  │
30  │  │  ELSE  ──────────────────────────────────────── BR-4
31  │  │  │   Logger: payment id + status "Default"   (no external call)
32  │  │
33  │  │  RESCUE  (per-payment, last in loop block)  ──── BR-7
34  │  │      HTTP POST GLDMessageLog:LogXMLRequest      [C-3]
35  │  │         Request = error.message
36  │  │         RequestIdentifier1 = "ERROR - processing payment" · AppID = 3
37  │  │      Logger: payment id + status "Error" + errorDescription
38  │  │      → loop continues with the next payment
39  │
40  │  HTTP POST  GLDMessageLog:LogXMLResponse            [C-3]
41  │     MessageLogID (from step 4) · ResponseDoc · ResponseIdentifier4 = "FE"
42  │
43  CATCH  (outer, last in try block)  ──────────────────
44      HTTP POST GLDMessageLog:LogXMLRequest             [C-3]
45         Request = error.message
46         RequestIdentifier1 = "ERROR - processFundingRequest" · AppID = 3
47
48  workato_service/send_reply
49     status = "PAYMENTS_PROCESSED" · paymentResponses[] · Errors[]
```

### Structural rules to honour when building

1. `rescue` must be the **last** block inside `repeat_for_each` — this is what makes a failed payment continue the loop (BR-7).
2. `catch` must be the **last** block inside the outer `try`.
3. `send_reply` sits **outside** the try block so a response is returned on every path.
4. The `if` / `elsif` / `else` chain must be one construct, not three sibling `if`s — otherwise a `Check` payment would also fall into the `else`.
5. Use `recipe_builder_get_datapills` for every pill path. Do **not** hand-author them.
6. Loop source is `payments` with `.parse_json` applied; the list alias is `payment_loop`.

---

## 9. Mapping Gaps / Deviations

Items where the Agent Bridge mapping is absent, ambiguous, or where a deliberate deviation was made. **Each needs review before or during the build.**

| ID | Severity | Gap / Deviation | Detail & proposed handling |
|---|---|---|---|
| **G-1** | MEDIUM | **SOAP transport has no row in the mapping file.** | Rows 1–22 cover control flow and INVOKE, but nothing maps `pub.soap.utils:*` / SOAP processor registration. **Deviation:** the entire SOAP wrap/unwrap chain (9 wrapper steps) collapses into Workato's `workato_service/receive_request` trigger + `send_reply`. Callers move from SOAP/XML to the Workato callable-recipe HTTP endpoint (JSON). **This changes the client contract** and needs consumer sign-off. |
| **G-2** | MEDIUM | **No Workato connector exists for "a webMethods flow service in a sibling package."** | CheckWriter, GLDMessageLog and WSRProcessStatistics are all IS flow services, not a product with a Workato connector. Bridge row 22 maps HTTP INVOKEs to the HTTP connector, so **HTTP connector** is the closest accurate fit. **Risk:** if these services are only reachable via IS-internal RPC and were never HTTP-exposed, the HTTP approach will not work and each will need its own migration. **SME confirmation required.** |
| **G-3** | **HIGH** | **NACHA flat-file generation has no mapping and no Workato equivalent.** | `pub.flatFile:convertToString` + the `NACHA_Schema` fixed-width schema have no counterpart in the mapping file or in Workato's connector library. The whole `processACHBatch` service is therefore **deferred to Phase 2** and will need a custom implementation (Workato custom action / SDK connector, or an external service). Compounded by source defects: hardcoded `Trace Number`, hardcoded `R/T CheckDigit`, and **no file/batch header or control records** — the current output is not a valid NACHA file. Recommend re-specifying NACHA generation with the SME rather than porting it. |
| **G-4** | MEDIUM | **`WSRProcessStatistics:publishErrorDoc` publishes to the webMethods Broker.** | No row in the mapping file; no Workato equivalent for a Broker publish. Options: (a) HTTP POST if the service is exposed, (b) drop it and rely on Workato's native job error reporting, (c) Workato Event Streams topic. **Proposal: omit from v1** and rely on the GLDMessageLog HTTP call plus Workato job history. Flagged for decision. |
| **G-5** | LOW | `pub.flow:getLastError` has no mapping row. | **Deviation:** no equivalent step is created — Workato exposes `error.message` / `error.type` datapills directly inside `rescue` / `catch`. Behaviourally equivalent. |
| **G-6** | LOW | `MAPDELETE` (50+ pipeline drops) has no mapping row. | **Deviation:** intentionally not migrated. webMethods uses one shared mutable pipeline requiring manual hygiene; Workato passes explicit step outputs. No functional loss. |
| **G-7** | LOW | `MAPINVOKE pub.list:appendToDocumentList` has no mapping row. | **Deviation:** list accumulation is implicit in a Workato loop. No dedicated step. |
| **G-8** | LOW | **Debug harness not migrated.** | `BRANCH /debug` → `savePipelineToFile` / `restorePipelineFromFile` is dev tooling. **Deviation: omitted.** Note it currently writes full pipelines — including payee routing and account numbers — to disk on every request; dropping it is also a security improvement. |
| **G-9** | LOW | **Source defect carried or corrected?** | `errorDoc/service_name` is hardcoded to `GLDExpressGateway.MainFlows.EFW:processLXIRequest` — the wrong service (copy/paste leftover). **Moot if G-4 is omitted from v1.** If `publishErrorDoc` is built, recommend correcting to `GLDFundingEngine.MainFlows:processFundingRequest`. |
| **G-10** | LOW | **Source defect: duplicated `system_message` write.** | `errorDoc/system_message` is mapped twice (`lastError/error`, then `lastError/errorDump`); the second wins. **Proposal:** map once, from `error.message`. |
| **G-11** | MEDIUM | **`$default` path silently swallows Wire and unknown payment types.** | BR-4 faithfully reproduces the source: no external call, status `Default`, no error raised. **This is preserved for fidelity**, but is arguably a bug — a Wire payment is accepted and never disbursed. Flagged for business review. |
| **G-12** | LOW | **Unused inbound fields.** | `sourceSubCategory`, `salesRepName`, `payee/type`, `payment/status`, `glCode`, `glAmount`, `glDescription` are in the contract but never read. Carried into the trigger schema for contract fidelity; not mapped to any action. |
| **G-13** | MEDIUM | **`payeeKey` response field name unverified.** | The Check path branches on `/payeeKey` returned by `invokeGetUniquePayee`. The actual HTTP/JSON response field name from CheckWriter is unknown. The pill path must be corrected once the real response is observed. |
| **G-14** | MEDIUM | **ACH stored-procedure name unverified.** | The source is a webMethods JDBC **adapter service** named `insertPayment`; the underlying schema/procedure name is defined in `GLD_ACHAdaptersServices`, which is **not in this package**. `GLD_ACH.INSERTPAYMENT` is a working assumption. **SME confirmation required.** |
| **G-15** | LOW | **Endpoint URLs and credentials unavailable.** | All base URLs (CheckWriter, GLDMessageLog, ProcessStats) are unknown. Realistic placeholders will be used per Instruction_Workato.md; real values from SME before go-live. |
| **G-16** | LOW | **Bridge row 9 (BRANCH → parallel) not applicable.** | The mapping file's row 9 warns Workato has no native parallelism. This package has **no parallel branches** — all `BRANCH` shapes are value switches (rows 6/10). No gap in practice. |

### Open questions for the SME (do not block the build)

1. Are CheckWriter / GLDMessageLog / WSRProcessStatistics reachable over HTTP, and at what base URLs? *(G-2, G-15)*
2. What is the exact schema-qualified name of the ACH insert procedure? *(G-14)*
3. What field name does `invokeGetUniquePayee` return the payee key in? *(G-13)*
4. Should `publishErrorDoc` be reproduced, or replaced by Workato job monitoring? *(G-4)*
5. Should Wire / unknown payment types continue to be silently accepted? *(G-11)*
6. Is NACHA batch generation in scope for Phase 2, and should it be re-specified rather than ported? *(G-3)*

---

## 10. Construct Coverage vs the Agent Bridge Mapping File

| Bridge row | Construct | Present in package? | Used in recipe |
|---|---|---|---|
| 1 | Workflow → Recipe | ✅ | Recipe |
| 2 | TRY → handle_error | ✅ ×3 | try + rescue blocks |
| 3 | CATCH → on_error | ✅ ×3 | catch + rescue clauses |
| 4 | FINALLY | ❌ not used | — |
| 5 | IF → conditional | ✅ | `if payeeKey is blank` |
| 6 | CASE → elsif | ✅ | payment type router |
| 7 | ELSE → else | ✅ | `$default` path |
| 8 | ELSEIF → elsif | ✅ | ACH clause |
| 9 | BRANCH (parallel) | ❌ none parallel | — (G-16) |
| 10 | SWITCH → if/elsif chain | ✅ ×3 | payment type, payeeKey, debug |
| 11 | SEQUENCE → sequential actions | ✅ | default ordering |
| 12 | LOOP → repeat for each | ✅ ×2 | `repeat_for_each` payments |
| 13–16 | DO / WHILE / REPEAT / UNTIL | ❌ not used | — |
| 17 | CONTINUE | ✅ implicit (BR-7) | native via `rescue` in loop |
| 18 | BREAK | ❌ not used | — |
| 19 | EXIT | ❌ not used | — |
| 20 | INVOKE (DB) → oracle | ✅ ×5 | `execute_stored_procedure` (1 in v1, 4 in Phase 2) |
| 21 | MAP → formula fields | ✅ ×9 | inline action input mapping |
| 22 | INVOKE (HTTP) → http | ✅ | CheckWriter ×3, MessageLog ×4 |
| **—** | **SOAP transport** | ✅ | **NO ROW — gap G-1** |
| **—** | **Flat file / NACHA** | ✅ | **NO ROW — gap G-3** |
| **—** | **Broker publish** | ✅ | **NO ROW — gap G-4** |
| **—** | **MAPDELETE / MAPINVOKE / getLastError** | ✅ | **NO ROW — gaps G-5/6/7** |

---

_Blueprint derived from analysis **AVOCADO**. Awaiting approval before any Workato asset is created._
