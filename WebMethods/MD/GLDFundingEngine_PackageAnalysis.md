# GLDFundingEngine20080714 — Consolidated Package Analysis
**Source:** webMethods IS 6.5 · `GLDFundingEngine` namespace · keybank.com  
**Target:** Workato  
**Analysis path:** `WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md`  
**Component mapping reference:** `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx`

---

## 1. Package Overview

| Attribute | Value |
|---|---|
| Package Name | GLDFundingEngine20080714 |
| Platform | webMethods IS 6.5 |
| Namespace Root | `GLDFundingEngine` |
| Domain | keybank.com (GLD = GL Disbursements) |
| SOAP Namespace | `https://webmethods.keybank.com/GLDFundingEngine/Wrappers` |
| External Dependency | WmFlatFile 6.5 (NACHA file generation) |

**Purpose:** This package orchestrates payment funding requests from a calling application. It accepts a structured payment request containing one or more payments, routes each payment to either a **Check Writer** system (`GLDExpressGateway`) or an **ACH payment adapter** (`GLD_ACHAdaptersServices`) based on payment type, and returns a per-payment status response. A second, separate batch flow generates NACHA (ACH) flat files from staged ACH payment records.

**Systems Involved:**
| System | Role |
|---|---|
| Inbound caller | SOAP client — submits `processFundingRequest` |
| `GLDExpressGateway` (CheckWriter) | External check creation service (Check path) |
| `GLD_ACHAdaptersServices` | ACH DB adapter — stages ACH payments, provides batch/NACHA data |
| `GLDMessageLog` | Error and audit logging service (DB/file) |
| webMethods `pub.flatFile` | Built-in flat-file serializer (NACHA generation — batch flow only) |

---

## 2. Integration / Workflow Logic

### 2.1 processFundingRequest — End-to-End Flow (Plain Language)

A calling application sends a SOAP request to the funding engine's web service endpoint. The wrapper flow unwraps the SOAP envelope, logs the raw request to the message log, and hands the structured document to the main flow.

The main flow initializes a response structure (empty payment results and errors arrays) and sets a static constant `REQUESTOR = "1"`. It then loops over every payment in the request one at a time.

For each payment, it inspects the `type` field:
- **Check** — The flow first searches the CheckWriter system for an existing payee record matching the payment's payee details (name, address, contact info). If no payee is found, it registers a new one. It then creates a check disbursement request in the CheckWriter system, passing the payee key, amount, memo, invoice reference, and lease number. The payment's status is recorded as "Paid".
- **ACH** — The flow calls the ACH adapter's `insertPayment` service, passing all required bank details (routing number, account number, amount, customer and payee identifiers). The payment's status is recorded as "Paid".
- **Other / Wire / anything else** — No external system is called. The payment's status is recorded as "Default", meaning it must be handled manually downstream.

If any step in a payment's processing throws an error, the flow catches it individually, retrieves the error details using `pub.flow:getLastError`, logs them to the message log, and moves on to the next payment. A single failed payment never aborts the rest of the batch.

After all payments are processed, the wrapper flow logs the response, wraps the result back into a SOAP envelope, and returns it to the caller.

### 2.2 processACHBatch — End-to-End Flow (Plain Language)

This flow runs as a scheduled batch job (no SOAP exposure). It:
1. Retrieves the current database system date/time (used as a cutoff)
2. Queries the ACH staging table for all unprocessed ACH payments up to that cutoff time
3. Retrieves a new batch ID for the NACHA file
4. Loops over each queued payment, maps the DB fields to the NACHA fixed-width format
5. Calls the webMethods flat-file serializer to generate the NACHA file using the defined schema
6. Sends or writes the NACHA file (endpoint not confirmed — beyond the scope of the scanned flow)

---

## 3. Shapes & Logic Breakdown

### 3.1 processFundingRequest

| # | Shape | webMethods Construct | Workato Equivalent | Details |
|---|---|---|---|---|
| 1 | Debug check | BRANCH | *Omit* — IS-specific diagnostic | On `debug` pipeline variable: saves/restores pipeline to file. No Workato equivalent. |
| 2 | Init output | MAP (STANDALONE) | Variables / formula pill | Initializes empty `fundingEngineWrapperOutput` (paymentResponses[], Errors[]) |
| 3 | Set REQUESTOR | MAP (MAPSET) | Set variable `REQUESTOR = "1"` | Static constant used in ACH call |
| 4 | TRY block | SEQUENCE (EXIT-ON=FAILURE) | `try` block (Handle Errors) | Wraps the payment loop — caught by outer catch only if loop itself fails |
| 5 | Payment LOOP | LOOP (IN-ARRAY, OUT-ARRAY) | `repeat_for_each` (each) | Iterates `fundingRequest.payments.payment[]` |
| 6 | Per-payment TRY | SEQUENCE (EXIT-ON=FAILURE) | `try` block (inner, inside each) | Per-payment error isolation |
| 7 | Payment type branch | BRANCH (SWITCH) | IF / ELSE IF / ELSE | On `payment.type` |
| 8 | GetUniquePayee | INVOKE | HTTP action: POST to CheckWriter | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee` |
| 9 | Map PayeeSearch | MAP (MAPCOPY, MAPSET) | Datapill mapping + set Country="USA" | Maps 10 payee fields to `PayeeInformation` document |
| 10 | payeeKey null check | BRANCH | IF condition: `payeeKey` is nil? | If payee not found, create new |
| 11 | AddNewPayee | INVOKE | HTTP action: POST to CheckWriter | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee` |
| 12 | Map CheckRequest | MAP (MAPCOPY) | Datapill mapping | Maps payeeKey, amount, memo, invoice ref, lease number |
| 13 | CreateCheckRequest | INVOKE | HTTP action: POST to CheckWriter | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest` |
| 14 | Set Check status | MAP (MAPSET, MAPCOPY) | Set `paymentResponse.id` + `status = "Paid"` | Check path exit |
| 15 | InsertPayment (ACH) | INVOKE | HTTP action: POST to ACH adapter | `GLD_ACHAdaptersServices:insertPayment` (11 params) |
| 16 | Map ACH input | MAP (MAPCOPY, MAPSET) | Datapill mapping | Maps 11 fields: APP_ID, CUSTOMER_NAME, PAYEE_NAME, PAYEE_ID, REFERENCE, AMOUNT, ROUTING_NUMBER, ACCOUNT_NUMBER, CUSTOMER_ID, REQUESTOR_ID, SOURCE |
| 17 | Set ACH status | MAP (MAPSET, MAPCOPY) | Set `paymentResponse.id` + `status = "Paid"` | ACH path exit |
| 18 | Set Default status | MAP (MAPSET, MAPCOPY) | Set `paymentResponse.id` + `status = "Default"` | Wire/Other path |
| 19 | Per-payment CATCH | SEQUENCE (EXIT-ON=DONE) | `catch` block (inside each) | Catches per-payment failure; does not re-raise |
| 20 | GetLastError | INVOKE `pub.flow:getLastError` | Native error object in `catch` | `error.message`, `error.error_type` auto-available |
| 21 | Modify error doc | MAP | Formula pill: build error record | Extracts service_name (from callStack), system_message (from errorDump) |
| 22 | Log error | INVOKE `GLDMessageLog:LogXMLRequest` | HTTP / Oracle SP (logging) | AppID=3, RequestIdentifier1="ERROR - processing payment" |

### 3.2 fundingEngineWrapper (SOAP Facade)

| # | Shape | webMethods Construct | Workato Equivalent | Details |
|---|---|---|---|---|
| 1 | Extract SOAP body | INVOKE `pub.soap.utils:getBody` | *Handled by trigger* | Gets body element from incoming SOAP envelope |
| 2 | Parse XML to doc | INVOKE `pub.xml:xmlNodeToDocument` | *Handled by trigger* | Parses XML to `fundingEngineWrapperInput` document |
| 3 | Log request | INVOKE `GLDMessageLog:LogXMLRequest` | HTTP / Oracle: log entry | AppID=3, RequestIdentifier1="FE", logs full request doc |
| 4 | Invoke main flow | INVOKE `processFundingRequest` | *Recipe sub-call or inline* | Passes `fundingEngineWrapperInput`, receives `fundingEngineWrapperOutput` |
| 5 | Log response | INVOKE `GLDMessageLog:LogXMLResponse` | HTTP / Oracle: log entry | Logs response with same MessageLogID, ResponseIdentifier4="FE" |
| 6 | Convert to XML | INVOKE `pub.xml:documentToXMLString` | *Handled by trigger send_reply* | Serializes output document to XML string |
| 7 | Wrap in SOAP | INVOKE `pub.soap.utils:createSoapData` + `addBodyEntry` | *Handled by trigger send_reply* | Wraps response XML in SOAP envelope |

> **Workato note:** Steps 1-2 and 6-7 (SOAP envelope wrap/unwrap) are handled automatically by Workato's callable recipe trigger — they do not need to be explicit steps. Steps 3 and 5 (logging) should be translated to a Workato log action or Oracle SP call.

### 3.3 processACHBatch

| # | Shape | webMethods Construct | Workato Equivalent | Details |
|---|---|---|---|---|
| 1 | TRY block | SEQUENCE (EXIT-ON=FAILURE) | `try` block | Wraps all steps |
| 2 | GetSystemDateTime | INVOKE | Oracle: `SELECT SYSDATE FROM DUAL` → `maxDateTime` | Gets current DB time as batch cutoff |
| 3 | SelectACHBatch | INVOKE | Oracle `select_rows` | Query ACH staging table with `maxDateTime` filter; returns results[] |
| 4 | GetNextBatchID | INVOKE | Oracle `select_rows` | Returns `nextBatchID` |
| 5 | Init NACHA doc | MAP | Variables / formula | Initialize empty NACHA document structure |
| 6 | Batch LOOP | LOOP | `repeat_for_each` | Iterates `selectACHBatchOutput.results[]` → builds NACHA entry per row |
| 7 | Map NACHA fields | MAP (MAPCOPY, MAPSET) | Datapill mapping + static values | 5 DB fields → NACHA fields; 5 static values |
| 8 | ConvertToString | INVOKE `pub.flatFile:convertToString` | **Custom JavaScript formula** — GAP | No native NACHA generator in Workato |
| 9 | (File send / FTP) | INVOKE (beyond scan range) | SFTP upload or file action | Destination not confirmed |

---

## 4. Connections

| Connection | Protocol / Type | Workato App & Connector | Configuration Needed |
|---|---|---|---|
| GLDExpressGateway (CheckWriter) | HTTP/SOAP call via webMethods IS | **HTTP connector** | Base URL (from SME), auth type (Basic/token), endpoint paths for each operation |
| GLD_ACHAdaptersServices | webMethods IS adapter → Oracle DB | **HTTP connector** (if service) or **Oracle connector** (if direct SQL) | Confirm with SME whether `insertPayment` is a callable REST service or a direct DB SP |
| GLDMessageLog | webMethods IS service → Oracle DB | **Oracle connector** — `execute_stored_procedure` or `select_rows` | Oracle host, port, SID, schema, credentials |
| Oracle DB (batch) | JDBC via webMethods IS | **Oracle connector** | Same Oracle connection as GLDMessageLog if same DB |

---

## 5. Operations

| Operation | Source Service | Input Fields | Output Fields | Workato Action |
|---|---|---|---|---|
| `invokeGetUniquePayee` | GLDExpressGateway CheckWriter | name, address1, address2, city, state_province, zip, phone, fax, contactName, contactPhone, Country="USA" | `payeeKey` (nullable string) | HTTP POST |
| `invokeAddNewPayee` | GLDExpressGateway CheckWriter | Same PayeeInformation fields | `payeeKey` | HTTP POST |
| `invokeCreateCheckRequest` | GLDExpressGateway CheckWriter | PayeeKey, Notes (invoiceRef), Comments (comment), CheckAmount (amount), Memo (checkMemo), PayeeName (payee.name), LeaseNumber (appInfo.id) | (check record created) | HTTP POST |
| `insertPayment` | GLD_ACHAdaptersServices | APP_ID, CUSTOMER_NAME, PAYEE_NAME, PAYEE_ID, REFERENCE, AMOUNT, ROUTING_NUMBER, ACCOUNT_NUMBER, CUSTOMER_ID, REQUESTOR_ID, SOURCE | (payment staged) | Oracle SP or HTTP POST |
| `getSystemDateTime` | GLD_ACHAdaptersServices | none | `SYS_DATE` | Oracle: `SELECT SYSDATE FROM DUAL` |
| `selectACHBatch` | GLD_ACHAdaptersServices | `maxDateTime` | results[]: {ROUTING_NUMBER, ACCOUNT_NUMBER, REFERENCE, PAYEE_NAME, AMOUNT, ID} | Oracle `select_rows` |
| `getNextBatchID` | GLD_ACHAdaptersServices | none | `nextBatchID` | Oracle `select_rows` |
| `LogXMLRequest` | GLDMessageLog | AppID, Request, RequestIdentifier1/2/3, RequestDoc | MessageLogID | Oracle SP or HTTP |
| `LogXMLResponse` | GLDMessageLog | MessageLogID, Response, ResponseIdentifier4/5/6, ResponseDoc | (void) | Oracle SP or HTTP |

---

## 6. Data Mappings

### 6.1 Trigger Input Schema — `fundingEngineWrapperInput`

| Field Path | Type | Required | Constraints |
|---|---|---|---|
| `applicationInfo.id` | string | Required | Length 1–100 |
| `applicationInfo.customerName` | string | Required | Max 100 chars |
| `applicationInfo.customerID` | integer | Required | Range 1–999999999999 |
| `applicationInfo.sourceName` | string | Optional | |
| `applicationInfo.sourceSubCategory` | string | Optional | |
| `applicationInfo.salesRepName` | string | Optional | |
| `payments.payment[*].id` | string | Required | Payment identifier |
| `payments.payment[*].type` | enum | Required | `Check` \| `ACH` \| `Other` \| `Wire` |
| `payments.payment[*].payee.id` | string | Required | |
| `payments.payment[*].payee.type` | string | Required | |
| `payments.payment[*].payee.name` | string | Required | |
| `payments.payment[*].payee.address1` | string | Required | |
| `payments.payment[*].payee.address2` | string | Optional | |
| `payments.payment[*].payee.city` | string | Required | |
| `payments.payment[*].payee.state_province` | string | Required | |
| `payments.payment[*].payee.zip` | string | Required | |
| `payments.payment[*].payee.phone` | string | Optional | |
| `payments.payment[*].payee.fax` | string | Optional | |
| `payments.payment[*].payee.contactName` | string | Optional | |
| `payments.payment[*].payee.contactPhone` | string | Optional | |
| `payments.payment[*].payee.routingNumber` | integer (9 digits) | Optional (ACH) | |
| `payments.payment[*].payee.accountNumber` | integer (17 digits) | Optional (ACH) | |
| `payments.payment[*].amount` | decimal | Required | |
| `payments.payment[*].invoiceReference` | string | Optional | |
| `payments.payment[*].comment` | string | Optional | |
| `payments.payment[*].checkMemo` | string | Optional | |
| `payments.payment[*].status` | string | Required | |
| `payments.payment[*].glCode` | string | Optional | |
| `payments.payment[*].glAmount` | string | Optional | |
| `payments.payment[*].glDescription` | string | Optional | |

### 6.2 Trigger Output Schema — `fundingEngineWrapperOutput`

| Field Path | Type | Notes |
|---|---|---|
| `paymentResponses.paymentResponse[*].id` | string | Echo of input `payment.id` |
| `paymentResponses.paymentResponse[*].status` | string | "Paid" or "Default" |
| `paymentResponses.paymentResponse[*].errorDescription` | string | Optional, on error |
| `Errors.Error[*]` | array | Full error objects from per-payment CATCH block |

### 6.3 Check path — PayeeSearch mapping

| Source (trigger input) | Target (CheckWriter `PayeeInformation`) |
|---|---|
| `payment.payee.name` | `name` |
| `payment.payee.address1` | `address1` |
| `payment.payee.address2` | `address2` |
| `payment.payee.city` | `city` |
| `payment.payee.state_province` | `state_province` |
| `payment.payee.zip` | `zip` |
| `payment.payee.phone` | `phone` |
| `payment.payee.fax` | `fax` |
| `payment.payee.contactName` | `contactName` |
| `payment.payee.contactPhone` | `contactPhone` |
| *(static)* `"USA"` | `Country` |

### 6.4 Check path — CheckRequest mapping

| Source | Target (CheckWriter `CheckRequest`) |
|---|---|
| `payeeKey` (from GetUniquePayee/AddNewPayee response) | `PayeeKey` |
| `payment.invoiceReference` | `Notes` |
| `payment.comment` | `Comments` |
| `payment.amount` | `CheckAmount` |
| `payment.checkMemo` | `Memo` |
| `payment.payee.name` | `PayeeName` |
| `applicationInfo.id` | `LeaseNumber` |

### 6.5 ACH path — insertPayment mapping

| Source | Target (`insertPayment`) |
|---|---|
| `applicationInfo.id` | `APP_ID` |
| `applicationInfo.customerName` | `CUSTOMER_NAME` |
| `payment.payee.name` | `PAYEE_NAME` |
| `payment.payee.id` | `PAYEE_ID` |
| `payment.invoiceReference` | `REFERENCE` |
| `payment.amount` | `AMOUNT` |
| `payment.payee.routingNumber` | `ROUTING_NUMBER` |
| `payment.payee.accountNumber` | `ACCOUNT_NUMBER` |
| `applicationInfo.customerID` | `CUSTOMER_ID` |
| *(static)* `"1"` (REQUESTOR pipeline var) | `REQUESTOR_ID` |
| `applicationInfo.sourceName` | `SOURCE` |

### 6.6 NACHA batch record mapping (processACHBatch LOOP)

| DB Column | NACHA Fixed-Width Field | Value / Note |
|---|---|---|
| `ROUTING_NUMBER` | Routing/Transit Number | From DB |
| `ACCOUNT_NUMBER` | Individual Account Number | From DB |
| `AMOUNT` | Amount | From DB |
| `REFERENCE` | Individual ID Number | From DB |
| `PAYEE_NAME` | Individual Name | From DB |
| *(static)* | Record Type Code | `6` (Entry Detail) |
| *(static)* | Transaction Code | `22` (PPD credit) |
| *(static)* | R/T Check Digit | `9` |
| *(static)* | Trace Number | `113000600000001` |
| *(static)* | Addenda Indicator | `0` |
| *(static)* | Discretionary Data | `" "` (space) |

---

## 7. Business Rules & Conditions

| Rule | Location | Logic |
|---|---|---|
| Payment routing by type | `processFundingRequest` / BRANCH | `type == "Check"` → CheckWriter path; `type == "ACH"` → ACH path; `$default` (Other/Wire/unknown) → status="Default", no processing |
| Payee lookup before creation | Check path / BRANCH | `invokeGetUniquePayee` first; if `payeeKey == null` (not found) → call `invokeAddNewPayee` |
| Per-payment error isolation | CATCH block inside LOOP | Each payment has its own TRY-CATCH; errors captured to `Errors[]` but do not abort the batch |
| Static REQUESTOR_ID | MAP | `REQUESTOR` hardcoded to `"1"` regardless of caller — used in ACH `insertPayment` |
| Static AppID in logs | CATCH + wrapper | AppID `"3"` hardcoded in all `LogXMLRequest` calls; `"FE"` as identifier |
| Debug mode (omit in migration) | BRANCH | If `debug` input set, serializes/restores IS pipeline to file — IS-specific, no Workato equivalent |
| **GAP: Other/Wire not processed** | BRANCH $default | `type=Other` and `type=Wire` are recorded with status "Default" but receive no external processing — this is intentional existing behavior |

---

## 8. Error Handling

| Construct | webMethods Implementation | Workato Equivalent |
|---|---|---|
| Per-payment TRY | `SEQUENCE EXIT-ON="FAILURE"` inside LOOP | `try` block inside `repeat_for_each` (each) |
| Per-payment CATCH | `SEQUENCE EXIT-ON="DONE"` (sibling) | `catch` block (rescue) inside `each` |
| Error retrieval | `pub.flow:getLastError` → service_name, system_message, errorDump | Native: `error.message`, `error.error_type` auto-exposed in rescue block |
| Error logging | `GLDMessageLog:LogXMLRequest` (AppID=3) | Oracle SP call or HTTP logging action inside rescue block |
| Non-fatal catch | CATCH does NOT re-throw — LOOP continues to next payment | `rescue` block with no re-raise — `each` continues naturally |
| Wrapper request/response logging | `GLDMessageLog:LogXMLRequest` + `LogXMLResponse` (AppID=3, ID="FE") | Oracle SP / HTTP at recipe start and end |

---

## 9. Triggers & Scripting

### 9.1 processFundingRequest — SOAP Trigger

- **webMethods registration:** Service `GLDFundingEngine.Wrappers.Registration:registerFlowServiceForSOAP` runs on IS startup and registers `fundingEngineWrapper` as a SOAP endpoint.
- **SOAP namespace:** `https://webmethods.keybank.com/GLDFundingEngine/Wrappers`
- **Unregistration:** `unregisterFlowServiceForSOAP` runs on IS shutdown.
- **Workato trigger:** `workato_service / receive_request` (callable recipe — HTTP POST). No SOAP translation is needed; Workato accepts JSON. The SOAP envelope handling (wrap/unwrap) is transparent — only the business payload is modeled.

### 9.2 processACHBatch — Scheduled Trigger

- **webMethods trigger:** No SOAP registration. Run via scheduler or manually from IS Admin console.
- **Workato trigger:** Scheduled (cron-based or time-interval). No input schema required.
- **Schedule frequency:** Not defined in package source — must be confirmed with operations team.

### 9.3 Custom Scripting

- No Groovy or Java scripting in this package — all logic uses standard webMethods flow steps.
- The only scriptable concern is NACHA file generation (`pub.flatFile:convertToString`) which uses a schema-driven fixed-width formatter. This has no Workato native equivalent and requires a custom JavaScript formula pill.

---

## 10. Equivalent Recipe Structure

### Recipe 1 — processFundingRequest (Callable Recipe)

```
TRIGGER: workato_service / receive_request
  Name: "Process Funding Request"
  Input schema:
    - applicationInfo (object): id, customerName, customerID, sourceName, sourceSubCategory, salesRepName
    - payments (array of objects):
        id, type (Check|ACH|Other|Wire),
        payee (object): id, type, name, address1, address2, city, state_province, zip,
                        phone, fax, contactName, contactPhone, routingNumber, accountNumber
        amount, invoiceReference, comment, checkMemo, status, glCode, glAmount, glDescription
  Reply schema:
    - paymentResponses (array): paymentResponse[]: { id, status, errorDescription }
    - Errors (array): Error[]: { ... error details ... }

STEP 1 — Handle Errors (try block)
│
├── STEP 2 — HTTP POST: Log request (GLDMessageLog LogXMLRequest)
│     App: HTTP · AppID=3, RequestIdentifier1="FE", request body = trigger input JSON
│
├── STEP 3 — Repeat for each payment in trigger.payments
│     (each step — line alias: payment_loop)
│     │
│     ├── STEP 3.1 — try block (per-payment error isolation)
│     │     │
│     │     ├── STEP 3.2 — IF payment.type == "Check"
│     │     │     │
│     │     │     ├── STEP 3.2.1 — HTTP POST: invokeGetUniquePayee
│     │     │     │     Input: PayeeInformation (11 fields from payment.payee + Country="USA")
│     │     │     │     Output: payeeKey
│     │     │     │
│     │     │     ├── STEP 3.2.2 — IF payeeKey is nil?
│     │     │     │     │
│     │     │     │     └── STEP 3.2.2a — HTTP POST: invokeAddNewPayee
│     │     │     │           Input: PayeeInformation (same 11 fields)
│     │     │     │           Output: payeeKey
│     │     │     │
│     │     │     ├── STEP 3.2.3 — HTTP POST: invokeCreateCheckRequest
│     │     │     │     Input: PayeeKey, Notes (invoiceRef), Comments (comment),
│     │     │     │            CheckAmount (amount), Memo (checkMemo),
│     │     │     │            PayeeName (payee.name), LeaseNumber (appInfo.id)
│     │     │     │
│     │     │     └── STEP 3.2.4 — Set paymentResponse:
│     │     │           paymentResponse.id = payment.id
│     │     │           paymentResponse.status = "Paid"
│     │     │
│     │     ├── STEP 3.3 — ELSE IF payment.type == "ACH"
│     │     │     │
│     │     │     ├── STEP 3.3.1 — HTTP POST (or Oracle SP): insertPayment
│     │     │     │     Input (11 params):
│     │     │     │       APP_ID = appInfo.id
│     │     │     │       CUSTOMER_NAME = appInfo.customerName
│     │     │     │       PAYEE_NAME = payment.payee.name
│     │     │     │       PAYEE_ID = payment.payee.id
│     │     │     │       REFERENCE = payment.invoiceReference
│     │     │     │       AMOUNT = payment.amount
│     │     │     │       ROUTING_NUMBER = payment.payee.routingNumber
│     │     │     │       ACCOUNT_NUMBER = payment.payee.accountNumber
│     │     │     │       CUSTOMER_ID = appInfo.customerID
│     │     │     │       REQUESTOR_ID = "1" (static)
│     │     │     │       SOURCE = appInfo.sourceName
│     │     │     │
│     │     │     └── STEP 3.3.2 — Set paymentResponse:
│     │     │           paymentResponse.id = payment.id
│     │     │           paymentResponse.status = "Paid"
│     │     │
│     │     └── STEP 3.4 — ELSE (Other / Wire / default)
│     │           └── Set paymentResponse:
│     │                 paymentResponse.id = payment.id
│     │                 paymentResponse.status = "Default"
│     │
│     └── CATCH (rescue — per payment):
│           STEP 3.5 — HTTP POST (or Oracle SP): LogXMLRequest
│                 AppID=3, error.message, error.error_type
│           (no re-raise — each iteration continues)
│
├── STEP 4 — HTTP POST: Log response (GLDMessageLog LogXMLResponse)
│     AppID=3, ResponseIdentifier4="FE", response body = paymentResponses
│
└── STEP 5 — send_reply
      paymentResponses = accumulated paymentResponse array
      Errors = accumulated errors from rescue blocks

CATCH (outer — unexpected recipe-level failure):
  STEP 6 — Log critical error
```

### Recipe 2 — processACHBatch (Scheduled Recipe)

**NOTE: This recipe has a HIGH-severity gap — NACHA flat-file generation requires custom implementation. Recommend phased approach or dedicated NACHA library.**

```
TRIGGER: Scheduled (cron — daily, time TBD with operations team)

STEP 1 — Oracle: SELECT SYSDATE FROM DUAL
  → store as maxDateTime

STEP 2 — Oracle select_rows: selectACHBatch
  Filter: WHERE datetime <= maxDateTime
  Returns: results[] { ROUTING_NUMBER, ACCOUNT_NUMBER, REFERENCE, PAYEE_NAME, AMOUNT, ID }

STEP 3 — Oracle select_rows: getNextBatchID
  Returns: nextBatchID

STEP 4 — Repeat for each record in results[]
  Build NACHA entry:
    Routing/Transit Number = ROUTING_NUMBER
    Individual Account Number = ACCOUNT_NUMBER
    Amount = AMOUNT
    Individual ID Number = REFERENCE
    Individual Name = PAYEE_NAME
    Record Type Code = "6" (static)
    Transaction Code = "22" (static — PPD credit)
    R/T Check Digit = "9" (static)
    Trace Number = "113000600000001" (static)
    Addenda Indicator = "0" (static)
    Discretionary Data = " " (static)

STEP 5 — Custom JavaScript formula: Generate NACHA flat-file string
  (No native Workato NACHA generator — requires custom implementation)

STEP 6 — SFTP upload OR File write: Send NACHA file
  (Destination endpoint not confirmed — SME input required)
```

---

## 11. Mapping Gaps / Deviations

| # | Gap | Severity | Description | Action Required |
|---|---|---|---|---|
| 1 | NACHA flat-file generation | **High** | `pub.flatFile:convertToString` with `GLDFundingEngine.Schemas:NACHA_Schema` generates fixed-width NACHA ACH file format. Workato has no built-in NACHA generator. | Custom JavaScript formula pill or third-party NACHA library. Recommend separate scoping session. |
| 2 | GLDExpressGateway endpoint schema unknown | **High** | `invokeGetUniquePayee`, `invokeAddNewPayee`, `invokeCreateCheckRequest` are internal webMethods IS service calls. The actual HTTP/SOAP endpoint URL, auth method, and request/response JSON/XML schema are not in this package. | SME input required before HTTP connector can be configured. |
| 3 | GLD_ACHAdaptersServices underlying SP/SQL unknown | **Medium** | `insertPayment`, `getSystemDateTime`, `selectACHBatch`, `getNextBatchID` are IS service wrappers over Oracle DB operations. The underlying SP names, table names, and SQL are not in this package. | Need GLDACHAdaptersServices package source or DBA access to confirm. |
| 4 | Other / Wire payment types not processed | **Medium** | `type=Other` and `type=Wire` fall to `$default` branch — status "Default", no external call. Intentional existing behavior. | Document as known gap; do not implement. Confirm with business that downstream handling is in place. |
| 5 | processACHBatch NACHA destination | **Medium** | The NACHA file send/write step at the end of `processACHBatch` is beyond the scanned section of the flow (file was read in part). The destination (FTP server, file path, or SFTP) is not confirmed. | Read remaining flow section or get SME confirmation. |
| 6 | GLDMessageLog service schema | **Low** | Logging service likely writes to a DB table. The underlying SP or table name is not in this package. | Can be replaced with Workato error monitor / Oracle SP if available, or omitted from MVP. |
| 7 | Debug pipeline save (omit) | **Low** | The debug BRANCH is an IS-specific diagnostic — no Workato equivalent. | Omit from recipe. |
| 8 | processACHBatch schedule frequency | **Low** | Scheduling details are not in the package source. | Confirm with operations team before configuring Workato scheduled trigger. |
