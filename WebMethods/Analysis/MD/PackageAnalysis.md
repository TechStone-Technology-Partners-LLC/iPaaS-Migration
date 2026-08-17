# Package Analysis: GLDFundingEngine20080714

**Source:** webMethods IS 6.5, keybank.com  
**Target:** Workato  
**Analyzed:** 2026-07-30  
**Flows:** processFundingRequest (primary), processACHBatch (batch)

---

## 1. Package Overview

`GLDFundingEngine` is a **payment routing engine** for KeyBank that processes multi-payment funding requests. It routes payments to the correct downstream processor based on payment type, then returns per-payment status responses.

**Systems involved:**
- **GLDExpressGateway CheckWriter** — HTTP/SOAP service for check payments (payee lookup, payee registration, check request creation)
- **GLD_ACHAdaptersServices** — Oracle JDBC service for ACH payments (insertPayment SP) and batch query operations
- **GLDMessageLog** — Oracle logging service (HTTP or SP), logs XML requests for audit
- **WSRCommon Email** — Internal SMTP email service for batch notifications

**Two primary flows:**

| Flow | Trigger | Purpose |
|---|---|---|
| `processFundingRequest` | Callable (SOAP/HTTP) | Accepts a funding request with N payments; routes each to Check, ACH, or Default path; returns per-payment statuses |
| `processACHBatch` | Scheduled (batch) | Queries Oracle for pending ACH records, builds NACHA flat file, emails notification (FTP step disabled in source) |

Additional artefacts (not migrated): `fundingEngineWrapper` (SOAP registration wrapper), `registerFlowServiceForSOAP`, `unregisterFlowServiceForSOAP` — infrastructure-only.

---

## 2. Shapes & Logic Breakdown

### 2.1 processFundingRequest

| # | webMethods Shape | Description | Workato Equivalent |
|---|---|---|---|
| 1 | FLOW entry | Service trigger | `workato_service/receive_request` callable recipe trigger |
| 2 | BRANCH on `/debug` | Dev-mode pipeline save/restore — not production logic | Not migrated (dev artifact only) |
| 3 | SEQUENCE EXIT-ON="SUCCESS" | Outer wrapper sequence | Implicit recipe body |
| 4 | SEQUENCE EXIT-ON="FAILURE" | Main TRY block | Outer `try` block |
| 5 | MAP (init) | Initialize `fundingEngineWrapperOutput`, set REQUESTOR="1" | Set variables / formula initialization |
| 6 | LOOP over `payments/payment[]` | Iterate each payment in the request | `each` (repeat for each) — source: `payments_json.parse_json` |
| 7 | Per-payment SEQUENCE EXIT-ON="FAILURE" | Per-payment TRY — error here skips to catch but continues loop | Steps inside `each` before `rescue` |
| 8 | BRANCH on `payment/type` | Route: "Check" / "ACH" / "$default" | `if` / `elsif` / `else` block |
| 9 | Check: INVOKE `invokeGetUniquePayee` | HTTP POST — search for existing payee by address/name | HTTP action: POST to CheckWriter getUniquePayee endpoint |
| 10 | Check: BRANCH on `/payeeKey` == $null | If no payeeKey returned, payee doesn't exist | `if` condition: `payeeKey.presence` is nil |
| 11 | Check: INVOKE `invokeAddNewPayee` | HTTP POST — register new payee if not found | HTTP action: POST to CheckWriter addNewPayee endpoint |
| 12 | Check: INVOKE `invokeCreateCheckRequest` | HTTP POST — create check with payee key and payment details | HTTP action: POST to CheckWriter createCheckRequest endpoint |
| 13 | Check: MAP set status="Paid" | Set paymentResponse.id + status="Paid" | Formula / set variable |
| 14 | ACH: INVOKE `insertPayment` | Oracle SP call via JDBC — insert ACH payment record (11 params) | HTTP action: POST to GLD_ACHAdaptersServices insertPayment |
| 15 | ACH: MAP set status="Paid" | Set paymentResponse.id + status="Paid" | Formula / set variable |
| 16 | Default: MAP set status="Default" | Wire/Other — no external call, mark as Default | `else` block, set status="Default" |
| 17 | Per-payment SEQUENCE EXIT-ON="DONE" | **CATCH** — runs on payment failure, continues to next payment | `rescue` block (last sibling in `each`) |
| 18 | CATCH: INVOKE `pub.flow:getLastError` | Get last error details (service_name, error message) | `error.message` datapill (available in `rescue`) |
| 19 | CATCH: MAP error details | Extract service_name + system_message into errorDoc | Set variable from `error.message` |
| 20 | CATCH: INVOKE `GLDMessageLog:LogXMLRequest` | Log error to Oracle MessageLog (wrapped in its own try to not fail on log failure) | HTTP action: POST to GLDMessageLog, AppID=3 |
| 21 | Outer SEQUENCE EXIT-ON="DONE" | **OUTER CATCH** — catches anything outside the loop | `catch` block at recipe level |
| 22 | Outer CATCH: INVOKE `GLDMessageLog:LogXMLRequest` | Log outer error to MessageLog | HTTP action: POST to GLDMessageLog |
| 23 | Outer CATCH: INVOKE `publishErrorDoc` | Publish to internal WSR stats system | Not migrated — internal monitoring only |

### 2.2 processACHBatch

| # | webMethods Shape | Description | Workato Equivalent |
|---|---|---|---|
| 1 | FLOW entry | Scheduled trigger | `scheduled_event/timer` (daily or cron) |
| 2 | SEQUENCE EXIT-ON="FAILURE" | TRY block | `try` block |
| 3 | INVOKE `getSystemDateTime` | Oracle `SELECT SYSDATE FROM DUAL` → `maxDateTime` | Oracle `select_rows` on DUAL |
| 4 | INVOKE `selectACHBatch` | Oracle SELECT pending ACH rows WHERE create_date <= maxDateTime | Oracle `select_rows` |
| 5 | INVOKE `getNextBatchID` | Oracle SELECT next batch ID sequence → `batchID` | Oracle `select_rows` |
| 6 | LOOP over `selectACHBatchOutput/results` | Iterate each ACH record, build NACHA document | `each` loop over Oracle results |
| 7 | Per-row MAP → NACHA fields | Map Oracle columns to NACHA flat-file record fields | Build output object per row with static values |
| 8 | INVOKE `pub.flatFile:convertToString` | Convert NACHA doc to fixed-width NACHA format string | ⚠️ GAP: no native Workato equivalent — custom Ruby formula required |
| 9 | INVOKE `updateBatchIDs` (**DISABLED**) | Oracle UPDATE to mark batch as processed | Not migrated — disabled in source |
| 10 | INVOKE `pub.client:ftp` (**DISABLED**) | FTP upload of NACHA file | Not migrated — disabled in source; SME input required if activation needed |
| 11 | INVOKE `sendEmail` | Email notification — batch complete | Email action (`gmail/send_email` or SMTP) |
| 12 | SEQUENCE EXIT-ON="DONE" | CATCH block | `catch` block |
| 13 | CATCH: INVOKE `GLDMessageLog:LogXMLRequest` | Log batch error | HTTP action: POST to GLDMessageLog |

---

## 3. Connections

| webMethods Service Group | System | Protocol | Workato Connection | Notes |
|---|---|---|---|---|
| GLDExpressGateway.ProcessFlows.CheckWriter | GLDExpressGateway | HTTP/SOAP | HTTP connection — `GLDFundingEngine_CheckWriter_Connection` | Base URL from SME; 3 endpoints: getUniquePayee, addNewPayee, createCheckRequest |
| GLD_ACHAdaptersServices | Oracle DB | JDBC (Oracle SP + SELECT) | HTTP connection — `GLDFundingEngine_ACH_Connection` (if via HTTP gateway) OR Oracle connection | If SP exposed via HTTP gateway, use HTTP; if direct DB, use Oracle |
| GLDMessageLog | Oracle logging service | HTTP/SOAP or Oracle SP | HTTP connection — `GLDFundingEngine_MessageLog_Connection` | Single endpoint: LogXMLRequest |
| WSRCommon.Utilities.FlowServices:sendEmail | SMTP/Email | Email | Gmail or SMTP connection | For processACHBatch notification email only |

---

## 4. Operations

| # | Operation | Connection | Type | Input Fields | Output Fields |
|---|---|---|---|---|---|
| 1 | `invokeGetUniquePayee` | CheckWriter | HTTP POST | PayeeName, AddressLine1-2, City, State, PostalCode, PhoneNumber, FaxNumber, ContactName, ContactPhoneNumber, Country="USA" | `payeeKey` |
| 2 | `invokeAddNewPayee` | CheckWriter | HTTP POST | Same PayeeInformation fields as above | `payeeKey` |
| 3 | `invokeCreateCheckRequest` | CheckWriter | HTTP POST | PayeeKey, Notes, Comments, CheckAmount, Memo, PayeeName, LeaseNumber | Check confirmation |
| 4 | `insertPayment` | ACH | HTTP POST or Oracle | APP_ID, CUSTOMER_NAME, PAYEE_NAME, PAYEE_ID, REFERENCE, AMOUNT, ROUTING_NUMBER, ACCOUNT_NUMBER, CUSTOMER_ID, REQUESTOR_ID="1", SOURCE | Insert confirmation |
| 5 | `getSystemDateTime` | Oracle | SELECT DUAL | (none) | `SYS_DATE` |
| 6 | `selectACHBatch` | Oracle | SELECT | `maxDateTime` | results[]: ROUTING_NUMBER, ACCOUNT_NUMBER, AMOUNT, REFERENCE, PAYEE_NAME |
| 7 | `getNextBatchID` | Oracle | SELECT | (none) | `nextBatchID` |
| 8 | `LogXMLRequest` | MessageLog | HTTP POST | AppID, Request, RequestIdentifier1, RequestIdentifier2, RequestIdentifier3, RequestDoc | (log confirmation) |
| 9 | `sendEmail` | Email | Email | (subject, body, recipients) | (sent) |

---

## 5. Data Mappings

### 5.1 Trigger Input Schema — processFundingRequest

Workato callables do not support nested objects in `request_schema_json` without silent schema wiping. Use **flat fields** for `applicationInfo.*` and pass `payments` as a JSON string.

**applicationInfo fields (flat at trigger level):**

| Field Name | Type | Required | Constraint | Notes |
|---|---|---|---|---|
| `id` | string | yes | 1–100 chars | Application ID / Lease Number |
| `customerName` | string | yes | max 100 chars | |
| `customerID` | string | yes | integer 1–999999999999 | |
| `sourceName` | string | no | — | Source system name |
| `sourceSubCategory` | string | no | — | Optional subcategory |
| `salesRepName` | string | no | — | Sales rep name |
| `payments` | string | yes | JSON string | Array of payment objects serialized as JSON |

**payment object fields (each element in `payments.parse_json`):**

| Field Name | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Payment identifier |
| `type` | string | yes | Enum: `Check` \| `ACH` \| `Other` \| `Wire` |
| `amount` | string | yes | Payment amount |
| `invoiceReference` | string | no | Mapped to Notes (Check) or REFERENCE (ACH) |
| `comment` | string | no | Mapped to Comments (Check) |
| `checkMemo` | string | no | Mapped to Memo (Check) |
| `status` | string | yes | Set by flow: "Paid" / "Default" / error |
| `glCode` | string | no | GL code |
| `glAmount` | string | no | GL amount |
| `glDescription` | string | no | GL description |
| `payee.id` | string | yes | Payee identifier (mapped to PAYEE_ID) |
| `payee.type` | string | yes | Payee type |
| `payee.name` | string | yes | Payee full name |
| `payee.address1` | string | yes | Street address line 1 |
| `payee.address2` | string | no | Address line 2 |
| `payee.city` | string | yes | City |
| `payee.state_province` | string | yes | State/province |
| `payee.zip` | string | yes | Postal code |
| `payee.phone` | string | no | Phone number |
| `payee.fax` | string | no | Fax number |
| `payee.contactName` | string | no | Contact name |
| `payee.contactPhone` | string | no | Contact phone |
| `payee.routingNumber` | string | no | 9-digit ABA routing number (ACH only) |
| `payee.accountNumber` | string | no | Up to 17-digit account number (ACH only) |

### 5.2 Check Payment Field Mappings

| Source (Workato datapill) | → | CheckWriter Request Field |
|---|---|---|
| `payment.payee.name` | → | PayeeName |
| `payment.payee.address1` | → | AddressLine1 |
| `payment.payee.address2` | → | AddressLine2 |
| `payment.payee.city` | → | City |
| `payment.payee.state_province` | → | State |
| `payment.payee.zip` | → | PostalCode |
| `payment.payee.phone` | → | PhoneNumber |
| `payment.payee.fax` | → | FaxNumber |
| `payment.payee.contactName` | → | ContactName |
| `payment.payee.contactPhone` | → | ContactPhoneNumber |
| `"USA"` (static) | → | Country |
| `getUniquePayee_response.payeeKey` OR `addNewPayee_response.payeeKey` | → | PayeeKey |
| `payment.invoiceReference` | → | Notes |
| `payment.comment` | → | Comments |
| `payment.amount` | → | CheckAmount |
| `payment.checkMemo` | → | Memo |
| `applicationInfo.id` | → | LeaseNumber |

### 5.3 ACH Payment Field Mappings

| Source (Workato datapill) | → | insertPayment Param |
|---|---|---|
| `"1"` (static — REQUESTOR constant) | → | REQUESTOR_ID |
| `applicationInfo.id` | → | APP_ID |
| `applicationInfo.customerName` | → | CUSTOMER_NAME |
| `applicationInfo.customerID` | → | CUSTOMER_ID |
| `applicationInfo.sourceName` | → | SOURCE |
| `payment.amount` | → | AMOUNT |
| `payment.invoiceReference` | → | REFERENCE |
| `payment.payee.id` | → | PAYEE_ID |
| `payment.payee.name` | → | PAYEE_NAME |
| `payment.payee.accountNumber` | → | ACCOUNT_NUMBER |
| `payment.payee.routingNumber` | → | ROUTING_NUMBER |

### 5.4 NACHA Batch Mappings (processACHBatch)

| Oracle Column | → | NACHA Detail Record Field |
|---|---|---|
| `ROUTING_NUMBER` | → | Routing/Transit Number |
| `ACCOUNT_NUMBER` | → | Individual Account Number |
| `AMOUNT` | → | Amount |
| `REFERENCE` | → | Individual ID Number |
| `PAYEE_NAME` | → | Individual Name |
| `batchID` (from getNextBatchID) | → | Trace Number |
| `"0"` (static) | → | Addenda Indicator |
| `""` (static) | → | Discretionary Data |
| Computed check digit | → | R/T CheckDigit |
| `"22"` (static — checking credit) | → | Transaction Code |
| `"6"` (static — detail record) | → | Record Type Code |

---

## 6. Business Rules & Conditions

1. **Payment type routing:** Branch on `payment.type`. Enum: `Check` (CheckWriter path), `ACH` (insertPayment path), `Other`/`Wire` → Default (status="Default", no external call).
2. **Payee lookup:** For Check payments, always call `invokeGetUniquePayee` first. Only if `payeeKey` is null/empty, call `invokeAddNewPayee`. Then always call `invokeCreateCheckRequest`.
3. **Error isolation:** Each payment iteration has its own try/catch (SEQUENCE EXIT-ON="DONE"). Failure in one payment logs the error but does NOT stop the loop — remaining payments continue.
4. **REQUESTOR constant:** `REQUESTOR_ID="1"` is hardcoded in the original source for all ACH insertPayment calls.
5. **Country constant:** `Country="USA"` is hardcoded for all payee lookup/registration calls.
6. **Error log nesting:** The `GLDMessageLog:LogXMLRequest` call inside the per-payment catch is itself wrapped in an EXIT-ON="DONE" guard — if logging fails, the loop still continues.
7. **ACH Batch datetime filter:** `maxDateTime` = `SYSDATE` from Oracle — selects all ACH records created up to the current moment.
8. **NACHA batch static fields:** Transaction Code="22" (checking account credit), Record Type Code="6" (PPD detail record), Addenda Indicator="0" (no addenda).

---

## 7. Error Handling

### processFundingRequest
| Scope | Pattern | webMethods | Workato |
|---|---|---|---|
| Per-payment | SEQUENCE EXIT-ON="DONE" | Catches payment-level errors; logs via LogXMLRequest; continues loop | `rescue` block as last sibling inside `each` |
| Per-payment log guard | SEQUENCE EXIT-ON="DONE" (nested) | Protects against log failures | Inner error handling omitted — Workato `rescue` handles this |
| Outer | SEQUENCE EXIT-ON="DONE" | Catches anything outside the loop | `catch` block at recipe level |

### processACHBatch
| Scope | Pattern | webMethods | Workato |
|---|---|---|---|
| Entire flow | SEQUENCE EXIT-ON="FAILURE"/"DONE" | Single try/catch wrapping all steps | `try`/`catch` at recipe level |

---

## 8. Equivalent Recipe Structure

### Recipe 1: FundingEngine (processFundingRequest → Workato callable)

```
TRIGGER: workato_service/receive_request — "FundingEngine"
  Input schema (flat trigger fields):
    id, customerName, customerID, sourceName, sourceSubCategory, salesRepName, payments (JSON string)
  Output schema:
    paymentResponses (array: [{id, status}])

[1] try:
  [2] each payment in trigger.payments.parse_json as payment_item:
    [3] if payment_item.type == "Check":
      [4] HTTP POST → invokeGetUniquePayee
            PayeeName: payment_item.payee.name
            AddressLine1: payment_item.payee.address1
            ... (10 payee fields)
            Country: "USA"
          → payeeKey (from response)
      [5] if payeeKey is empty:
        [6] HTTP POST → invokeAddNewPayee (same fields)
              → payeeKey
      [7] HTTP POST → invokeCreateCheckRequest
            PayeeKey: payeeKey
            Notes: payment_item.invoiceReference
            Comments: payment_item.comment
            CheckAmount: payment_item.amount
            Memo: payment_item.checkMemo
            PayeeName: payment_item.payee.name
            LeaseNumber: trigger.id
      [8] set paymentResponse.status = "Paid"
    
    [9] elsif payment_item.type == "ACH":
      [10] HTTP POST → insertPayment
            APP_ID: trigger.id
            CUSTOMER_NAME: trigger.customerName
            CUSTOMER_ID: trigger.customerID
            SOURCE: trigger.sourceName
            PAYEE_NAME: payment_item.payee.name
            PAYEE_ID: payment_item.payee.id
            AMOUNT: payment_item.amount
            REFERENCE: payment_item.invoiceReference
            ROUTING_NUMBER: payment_item.payee.routingNumber
            ACCOUNT_NUMBER: payment_item.payee.accountNumber
            REQUESTOR_ID: "1"
      [11] set paymentResponse.status = "Paid"
    
    [12] else (Other / Wire):
      [13] set paymentResponse.status = "Default"
    
    [rescue] ← last sibling in each block:
      [14] HTTP POST → GLDMessageLog:LogXMLRequest
            AppID: "3"
            Request: error.message
            RequestIdentifier1: payment_item.id
            RequestDoc: payment_item (serialized)

[catch] ← last sibling in try block:
  [15] HTTP POST → GLDMessageLog:LogXMLRequest
        AppID: "3"
        Request: error.message

[send_reply]:
  paymentResponses: (collected from each iteration)
```

### Recipe 2: processACHBatch (Workato scheduled recipe — ⚠️ NACHA gap)

```
TRIGGER: scheduled_event/timer (daily, time TBD by SME)

[1] try:
  [2] Oracle select_rows → SELECT SYSDATE FROM DUAL
        → maxDateTime (SYS_DATE column)
  
  [3] Oracle select_rows → selectACHBatch
        WHERE create_date <= maxDateTime
        → results[] (ROUTING_NUMBER, ACCOUNT_NUMBER, AMOUNT, REFERENCE, PAYEE_NAME)
  
  [4] Oracle select_rows → getNextBatchID
        → batchID (nextBatchID column)
  
  [5] each row in results as batch_row:
    [5a] Collect NACHA record fields:
          routingTransit: batch_row.ROUTING_NUMBER
          accountNumber: batch_row.ACCOUNT_NUMBER
          amount: batch_row.AMOUNT
          individualID: batch_row.REFERENCE
          individualName: batch_row.PAYEE_NAME
          traceNumber: batchID
          transactionCode: "22"
          recordTypeCode: "6"
          addendaIndicator: "0"
  
  [6] ⚠️ NACHA GENERATION GAP:
      pub.flatFile:convertToString with NACHA_Schema has no Workato equivalent.
      Approach: Custom Ruby formula step to serialize the collected batch_rows
      into NACHA ACH fixed-width format (94-char records per NACHA spec).
      This requires SME input on exact NACHA header/footer fields and file company info.
  
  [7] Email action → sendEmail
        Subject: "ACH Batch Processed - [date]"
        Body: summary of records processed

[catch]:
  [8] HTTP POST → GLDMessageLog:LogXMLRequest
        AppID: "3"
        Request: error.message
```

---

## 9. Mapping Gaps / Deviations

| # | Gap | Severity | Source Behaviour | Workato Approach |
|---|---|---|---|---|
| G1 | `pub.flatFile:convertToString` with NACHA schema | **HIGH** | webMethods converts a structured document tree into a fixed-width NACHA ACH file | No native equivalent — implement as custom Ruby formula that serializes collected records per NACHA fixed-width specification (94 chars/record). SME must provide file header/footer fields. |
| G2 | `pub.client:ftp` (DISABLED in source) | **MEDIUM** | FTP delivery of NACHA file — never active | If re-activation is needed, use Workato SFTP connector. Confirm with SME whether this path should be restored. |
| G3 | `updateBatchIDs` (DISABLED in source) | **LOW** | Oracle UPDATE to mark batch records — never active | Use Oracle `run_sql` if reactivation is needed. Confirm with SME. |
| G4 | `WSRProcessStatistics.MainFlows:publishErrorDoc` | **LOW** | Posts error details to internal WSR monitoring platform | Not migrated — internal system unavailable. Substitute with `logger/create_message` (Log step) or email alert. |
| G5 | `pub.flow:getLastError` pipeline details | **LOW** | Returns full pipeline snapshot at time of error | Workato `error.message` datapill captures the error message only. Full pipeline snapshot not available. |
| G6 | payeeKey combined formula | **LOW** | `payeeKey` comes from either getUniquePayee OR addNewPayee response | Use Workato formula: `getUniquePayee_response.payeeKey.presence \|\| addNewPayee_response.payeeKey` |
| G7 | REQUESTOR constant | **INFO** | Hardcoded "1" | Set as static string "1" in recipe |
| G8 | Country constant | **INFO** | Hardcoded "USA" | Set as static string "USA" in recipe |
| G9 | debug BRANCH | **INFO** | Dev-only diagnostic branch (save/restore pipeline) | Not migrated — development tool with no production use |

---

## 10. SME Inputs Required

| # | Input Needed | Used By | Notes |
|---|---|---|---|
| S1 | GLDExpressGateway CheckWriter base URL | Recipes 1 (steps 4, 6, 7) | Base URL + endpoint paths for getUniquePayee, addNewPayee, createCheckRequest |
| S2 | GLDExpressGateway auth credentials | Recipe 1 (HTTP connection) | API key, OAuth, or Basic auth |
| S3 | GLD_ACHAdaptersServices base URL or Oracle DSN | Recipe 1 (step 10), Recipe 2 (steps 2-4) | If via HTTP gateway: URL + auth. If direct Oracle: host, port, SID, credentials |
| S4 | GLDMessageLog base URL | Recipes 1 & 2 (rescue/catch) | URL + auth for LogXMLRequest endpoint |
| S5 | NACHA file company info | Recipe 2 (step 6) | Company Name, Company ID, Company Entry Description, Effective Date format for NACHA file header |
| S6 | FTP/SFTP server details | Recipe 2 (step 6, if reactivated) | Host, credentials, target directory for NACHA file delivery |
| S7 | processACHBatch schedule | Recipe 2 trigger | Exact time and frequency for scheduled trigger |
| S8 | Email recipients for batch notification | Recipe 2 (step 7) | To/CC addresses for ACH batch completion email |
