# GLDFundingEngine20080714 — Package Analysis

## 1. Package Overview

| Attribute | Value |
|---|---|
| Package Name | GLDFundingEngine20080714 |
| Platform | webMethods IS 6.5 |
| Namespace Root | GLDFundingEngine |
| Domain | keybank.com (GLD = GL Disbursements) |
| External Dependency | WmFlatFile 6.5 (NACHA file generation) |

**Purpose**: This package orchestrates payment funding requests from a calling application. It accepts a structured payment request (containing one or more payments), routes each payment to either a **Check Writer** system (`GLDExpressGateway`) or an **ACH** payment system (`GLD_ACHAdaptersServices`) based on payment type, and returns a payment response for each. A second, separate batch flow generates NACHA (ACH) flat files from staged ACH payment records.

**Systems Involved:**
- **Inbound caller** (SOAP client): Submits payment requests
- **GLDExpressGateway** (CheckWriter): External check creation service (invoked for `type=Check`)
- **GLD_ACHAdaptersServices**: ACH adapter — inserts ACH payments into DB and provides batch query/NACHA generation services
- **GLDMessageLog**: Error logging service (DB or file-based)
- **webMethods `pub.flatFile`**: Built-in flat-file serializer used for NACHA file generation

---

## 2. Flows Identified

| Flow | Trigger | Purpose |
|---|---|---|
| `processFundingRequest` | SOAP (registered on startup) | Route individual payments to Check or ACH system |
| `processACHBatch` | Scheduled/batch (no SOAP registration) | Pull staged ACH records and generate NACHA flat file |
| `fundingEngineWrapper` | Internal wrapper | SOAP facade over `processFundingRequest` |

Registration services:
- Startup: `GLDFundingEngine.Wrappers.Registration:registerFlowServiceForSOAP`
- Shutdown: `GLDFundingEngine.Wrappers.Registration:unregisterFlowServiceForSOAP`

---

## 3. Shapes & Logic Breakdown

### 3.1 processFundingRequest

#### Input Schema (`fundingEngineWrapperInput`)
Namespace: `https://webmethods.keybank.com/GLDFundingEngine/Wrappers`

| Path | Type | Required | Constraints |
|---|---|---|---|
| `fundingRequest.applicationInfo.id` | string | Required | Length 1–100 |
| `fundingRequest.applicationInfo.customerName` | string | Required | Max 100 chars |
| `fundingRequest.applicationInfo.customerID` | integer | Required | Range 1–999999999999 |
| `fundingRequest.applicationInfo.sourceName` | string | Optional | |
| `fundingRequest.applicationInfo.sourceSubCategory` | string | Optional | |
| `fundingRequest.applicationInfo.salesRepName` | string | Optional | |
| `fundingRequest.payments.payment[*].id` | string | Required | Payment identifier |
| `fundingRequest.payments.payment[*].type` | enum | Required | Check \| ACH \| Other \| Wire |
| `fundingRequest.payments.payment[*].payee.id` | string | Required | |
| `fundingRequest.payments.payment[*].payee.type` | string | Required | |
| `fundingRequest.payments.payment[*].payee.name` | string | Required | |
| `fundingRequest.payments.payment[*].payee.address1` | string | Required | |
| `fundingRequest.payments.payment[*].payee.address2` | string | Optional | |
| `fundingRequest.payments.payment[*].payee.city` | string | Required | |
| `fundingRequest.payments.payment[*].payee.state_province` | string | Required | |
| `fundingRequest.payments.payment[*].payee.zip` | string | Required | |
| `fundingRequest.payments.payment[*].payee.phone` | string | Optional | |
| `fundingRequest.payments.payment[*].payee.fax` | string | Optional | |
| `fundingRequest.payments.payment[*].payee.contactName` | string | Optional | |
| `fundingRequest.payments.payment[*].payee.contactPhone` | string | Optional | |
| `fundingRequest.payments.payment[*].payee.routingNumber` | integer | Optional | 9 digits (ACH) |
| `fundingRequest.payments.payment[*].payee.accountNumber` | integer | Optional | 17 digits (ACH) |
| `fundingRequest.payments.payment[*].amount` | decimal | Required | |
| `fundingRequest.payments.payment[*].invoiceReference` | string | Optional | |
| `fundingRequest.payments.payment[*].comment` | string | Optional | |
| `fundingRequest.payments.payment[*].checkMemo` | string | Optional | |
| `fundingRequest.payments.payment[*].status` | string | Required | |
| `fundingRequest.payments.payment[*].glCode` | string | Optional | |
| `fundingRequest.payments.payment[*].glAmount` | string | Optional | |
| `fundingRequest.payments.payment[*].glDescription` | string | Optional | |
| `debug` | string | Optional | Enables pipeline file save/restore for debugging |

#### Output Schema (`fundingEngineWrapperOutput`)
Namespace: `https://webmethods.keybank.com/GLDFundingEngine/Wrappers`

| Path | Type | Notes |
|---|---|---|
| `fundingEngineWrapperResponse.paymentResponses.paymentResponse[*].id` | string | Copied from input payment.id |
| `fundingEngineWrapperResponse.paymentResponses.paymentResponse[*].status` | string | "Paid", "Default", or error state |
| `fundingEngineWrapperResponse.paymentResponses.paymentResponse[*].errorDescription` | string | Optional, set on error |
| `fundingEngineWrapperResponse.Errors.Error[*]` | array | Optional, references GLDExpressWebServices.DocumentTypes:Error |

#### Flow Shape Inventory

| # | Shape | Type | Details |
|---|---|---|---|
| 1 | Debug check | BRANCH | On `debug` variable — saves/restores pipeline to file if truthy |
| 2 | Init output | MAP | Initialize empty `fundingEngineWrapperOutput` |
| 3 | Set REQUESTOR | MAP | Set static value REQUESTOR = "1" |
| 4 | TRY block | SEQUENCE (EXIT-ON=FAILURE) | Wraps the payment loop |
| 5 | Payment LOOP | LOOP | Iterates `fundingEngineWrapperInput/.../payments/payment[]` |
| 6 | Payment type BRANCH | BRANCH | Branches on `payment/type` |
| 7 | Check — GetUniquePayee | INVOKE | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee` |
| 8 | Map PayeeInformation | MAP | Maps payee fields → CheckWriter PayeeSearch document |
| 9 | Payee key null check | BRANCH | On `payeeKey == null` |
| 10 | Check — AddNewPayee | INVOKE | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee` |
| 11 | Map CheckRequest | MAP | Maps payment fields → CheckWriter CheckRequest |
| 12 | Check — CreateCheckRequest | INVOKE | `GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest` |
| 13 | Check — Set status | MAP | paymentResponse.id ← payment.id, status = "Paid" |
| 14 | ACH — InsertPayment | INVOKE | `GLD_ACHAdaptersServices:insertPayment` |
| 15 | Map ACH input | MAP | 11-field mapping to insertPayment |
| 16 | ACH — Set status | MAP | paymentResponse.id ← payment.id, status = "Paid" |
| 17 | Default — Set status | MAP | paymentResponse.id ← payment.id, status = "Default" |
| 18 | CATCH block | SEQUENCE (EXIT-ON=DONE) | Per-payment error handler |
| 19 | Get last error | INVOKE | `pub.flow:getLastError` |
| 20 | Modify error message | MAP | Build errorDoc (service_name from callStack, system_message from error/errorDump) |
| 21 | Log error | INVOKE | `GLDMessageLog:LogXMLRequest` — AppID=3, RequestIdentifier1="ERROR - processing payment" |

### 3.2 processACHBatch

#### Flow Shape Inventory

| # | Shape | Type | Details |
|---|---|---|---|
| 1 | TRY block | SEQUENCE | Wraps all steps |
| 2 | GetSystemDateTime | INVOKE | `GLD_ACHAdaptersServices:getSystemDateTime` → `maxDateTime` (SYS_DATE) |
| 3 | SelectACHBatch | INVOKE | `GLD_ACHAdaptersServices:selectACHBatch(maxDateTime)` → `selectACHBatchOutput.results[]` |
| 4 | GetNextBatchID | INVOKE | `GLD_ACHAdaptersServices:getNextBatchID` → `batchID` |
| 5 | Init NACHA_SchemaDT | MAP | Initialize NACHA flat-file document structure |
| 6 | Batch LOOP | LOOP | Iterates `selectACHBatchOutput/results` → builds `NACHA_SchemaDT/BatchRecord[]` |
| 7 | Map NACHA fields | MAP | Maps DB fields → NACHA entry fields |
| 8 | ConvertToString | INVOKE | `pub.flatFile:convertToString` using schema `GLDFundingEngine.Schemas:NACHA_Schema` |
| 9+ | (NACHA send/write) | INVOKE | File write or FTP send (not yet read — further in file) |

**NACHA Field Mappings (per ACH batch record):**

| DB Column | NACHA Field | Static Value |
|---|---|---|
| ROUTING_NUMBER | Routing/Transit Number | |
| ACCOUNT_NUMBER | Individual Account Number | |
| AMOUNT | Amount | |
| REFERENCE | Individual ID Number | |
| PAYEE_NAME | Individual Name | |
| — | Trace Number | 113000600000001 |
| — | Addenda Indicator | 0 |
| — | Discretionary Data | " " (space) |
| — | R/T CheckDigit | 9 |
| — | Transaction Code | 22 (PPD credit) |
| — | Record Type Code | 6 (Entry Detail) |

---

## 4. Connections

| Service Invoked | Protocol | Type | Workato Equivalent |
|---|---|---|---|
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee` | webMethods IS service call | Internal service (IS package dependency) | HTTP POST action (endpoint TBD from SME) |
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee` | webMethods IS service call | Internal service | HTTP POST action |
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest` | webMethods IS service call | Internal service | HTTP POST action |
| `GLD_ACHAdaptersServices:insertPayment` | webMethods IS service call | DB adapter call | HTTP POST action or Oracle connector |
| `GLD_ACHAdaptersServices:getSystemDateTime` | webMethods IS service call | DB SELECT (SYS_DATE) | Oracle `SELECT SYSDATE FROM DUAL` |
| `GLD_ACHAdaptersServices:selectACHBatch` | webMethods IS service call | DB SELECT (batch records) | Oracle `select_rows` action |
| `GLD_ACHAdaptersServices:getNextBatchID` | webMethods IS service call | DB SELECT | Oracle `select_rows` action |
| `GLDMessageLog:LogXMLRequest` | webMethods IS service call | Logging / DB insert | Oracle `execute_stored_procedure` or HTTP logging |
| `pub.flatFile:convertToString` | webMethods built-in | Flat-file serializer | No direct equivalent — custom Ruby/JavaScript formula |

---

## 5. Operations

| Operation | Source Service | IN Fields | OUT Fields |
|---|---|---|---|
| invokeGetUniquePayee | GLDExpressGateway | PayeeInformation: name, address1, address2, city, state_province, zip, phone, fax, contactName, contactPhone, Country="USA" | payeeKey (nullable) |
| invokeAddNewPayee | GLDExpressGateway | Same PayeeInformation fields | payeeKey |
| invokeCreateCheckRequest | GLDExpressGateway | PayeeKey, Notes (invoiceReference), Comments (comment), CheckAmount (amount), Memo (checkMemo), PayeeName (payee.name), LeaseNumber (applicationInfo.id) | (check record created) |
| insertPayment | GLD_ACHAdaptersServices | APP_ID, CUSTOMER_NAME, PAYEE_NAME, PAYEE_ID, REFERENCE, AMOUNT, ROUTING_NUMBER, ACCOUNT_NUMBER, CUSTOMER_ID, REQUESTOR_ID, SOURCE | (ACH payment staged) |
| getSystemDateTime | GLD_ACHAdaptersServices | none | SYS_DATE |
| selectACHBatch | GLD_ACHAdaptersServices | maxDateTime | results[] {ROUTING_NUMBER, ACCOUNT_NUMBER, REFERENCE, PAYEE_NAME, AMOUNT, ID} |
| getNextBatchID | GLD_ACHAdaptersServices | none | nextBatchID |
| LogXMLRequest | GLDMessageLog | AppID, Request, RequestIdentifier1, RequestIdentifier2, RequestIdentifier3, RequestDoc | MessageLogID |

---

## 6. Data Mappings

### 6.1 Check path — PayeeInformation mapping

| Source (fundingEngineWrapperInput) | Target (CheckWriter PayeeSearch) |
|---|---|
| `payment.payee.name` | `PayeeInformation.name` |
| `payment.payee.address1` | `PayeeInformation.address1` |
| `payment.payee.address2` | `PayeeInformation.address2` |
| `payment.payee.city` | `PayeeInformation.city` |
| `payment.payee.state_province` | `PayeeInformation.state_province` |
| `payment.payee.zip` | `PayeeInformation.zip` |
| `payment.payee.phone` | `PayeeInformation.phone` |
| `payment.payee.fax` | `PayeeInformation.fax` |
| `payment.payee.contactName` | `PayeeInformation.contactName` |
| `payment.payee.contactPhone` | `PayeeInformation.contactPhone` |
| *(static)* "USA" | `PayeeInformation.Country` |

### 6.2 Check path — CheckRequest mapping

| Source | Target (CheckWriter CheckRequest) |
|---|---|
| `payeeKey` | `CheckRequest.PayeeKey` |
| `payment.invoiceReference` | `CheckRequest.Notes` |
| `payment.comment` | `CheckRequest.Comments` |
| `payment.amount` | `CheckRequest.CheckAmount` |
| `payment.checkMemo` | `CheckRequest.Memo` |
| `payment.payee.name` | `CheckRequest.PayeeName` |
| `applicationInfo.id` | `CheckRequest.LeaseNumber` |

### 6.3 ACH path — insertPayment mapping

| Source | Target (insertPayment) |
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
| `REQUESTOR` (pipeline var = "1") | `REQUESTOR_ID` |
| `applicationInfo.sourceName` | `SOURCE` |

### 6.4 Output — paymentResponse mapping

| Source | Target |
|---|---|
| `payment.id` | `paymentResponse.id` |
| "Paid" (static, on success) | `paymentResponse.status` |
| "Default" (static, unhandled type) | `paymentResponse.status` |

---

## 7. Business Rules & Conditions

| Rule | Location | Logic |
|---|---|---|
| Payment routing by type | processFundingRequest / BRANCH | `type == "Check"` → Check Writer path; `type == "ACH"` → ACH path; `$default` → status set to "Default", no processing |
| Payee lookup before creation | Check path / BRANCH | `invokeGetUniquePayee` first; if `payeeKey == null` then call `invokeAddNewPayee` to create new payee |
| Per-payment error isolation | CATCH block | Each payment is individually caught; errors are logged but do not abort the whole batch (TRY-CATCH is inside LOOP) |
| Static REQUESTOR | MAP | REQUESTOR is hardcoded to "1" regardless of caller |
| Static AppID in error log | CATCH / MAP | Error log AppID hardcoded to "3" |
| Debug mode | BRANCH | If `debug` input is set, pipeline is serialized to a file for offline inspection |
| **GAP: Other/Wire types** | BRANCH default | Payment types "Other" and "Wire" fall to `$default` branch — they are recorded with status "Default" but are **not processed** |

---

## 8. Error Handling

| Construct | webMethods Implementation | Workato Equivalent |
|---|---|---|
| Per-payment try/catch | SEQUENCE (EXIT-ON=FAILURE) containing LOOP; SEQUENCE (EXIT-ON=DONE) as catch | `rescue` block inside `repeat_for_each` item |
| Get error details | `pub.flow:getLastError` | Native `rescue` block exposes error automatically |
| Error logging | `GLDMessageLog:LogXMLRequest` (AppID=3) | Oracle SP or HTTP action inside `rescue` block |
| Non-fatal catch | CATCH does NOT re-throw — continues to next payment | `rescue` block with no re-raise — loop continues |

---

## 9. Equivalent Workato Recipe Structure

### Recipe 1: processFundingRequest → Workato Callable Recipe

```
TRIGGER: callable_recipe (HTTP POST)
  Name: "Process Funding Request"
  Input: fundingRequest (JSON object — applicationInfo + payments array)

STEP 1 — Handle Error block (rescue)
  |
  STEP 2 — Repeat for each (loop over payments array)
  |   |
  |   STEP 3 — IF payment.type == "Check"
  |   |   STEP 3.1 — HTTP POST: invokeGetUniquePayee
  |   |   STEP 3.2 — IF payeeKey is empty/null
  |   |   |   STEP 3.2.1 — HTTP POST: invokeAddNewPayee
  |   |   STEP 3.3 — HTTP POST: invokeCreateCheckRequest
  |   |   STEP 3.4 — Set paymentResponse (id = payment.id, status = "Paid")
  |   |
  |   STEP 4 — ELSE IF payment.type == "ACH"
  |   |   STEP 4.1 — Oracle: insertPayment (execute_stored_procedure or HTTP)
  |   |   STEP 4.2 — Set paymentResponse (id = payment.id, status = "Paid")
  |   |
  |   STEP 5 — ELSE (Other / Wire / unknown)
  |       STEP 5.1 — Set paymentResponse (id = payment.id, status = "Default")
  |
  CATCH (rescue):
    STEP 6 — Oracle: LogXMLRequest (AppID=3, error details)
    NOTE: Error is caught per-payment, loop continues

STEP 7 — Return: fundingEngineWrapperResponse (paymentResponses array)
```

### Recipe 2: processACHBatch → Scheduled Workato Recipe

```
TRIGGER: Scheduled (daily or cron)

STEP 1 — Oracle: SELECT SYSDATE FROM DUAL → maxDateTime
STEP 2 — Oracle: select_rows (selectACHBatch) → batch records[]
STEP 3 — Oracle: select_rows (getNextBatchID) → batchID
STEP 4 — Repeat for each (loop over batch records)
  |   Build NACHA BatchRecord entry:
  |     ROUTING_NUMBER, ACCOUNT_NUMBER, AMOUNT, REFERENCE, PAYEE_NAME
  |     Static: Transaction Code=22, Record Type=6, etc.
STEP 5 — Format NACHA file (custom script / formula pill — NO native Workato NACHA generator)
STEP 6 — HTTP or SFTP: Send NACHA file to bank
```

---

## 10. Mapping Gaps / Deviations

| # | Gap | Severity | Description |
|---|---|---|---|
| 1 | NACHA flat-file generation | **High** | `pub.flatFile:convertToString` with `GLDFundingEngine.Schemas:NACHA_Schema` generates a fixed-width NACHA ACH file. Workato has no built-in NACHA generator. This requires a custom JavaScript formula pill or a third-party NACHA library. |
| 2 | GLDExpressGateway endpoint unknown | **Medium** | `invokeGetUniquePayee`, `invokeAddNewPayee`, `invokeCreateCheckRequest` are webMethods IS service calls — the underlying HTTP/SOAP endpoint, auth, and request/response schema are not in this package. SME input required. |
| 3 | Other/Wire payment types not processed | **Medium** | `type=Other` and `type=Wire` fall to default branch and are set to status "Default" without processing. This is existing behaviour — no work needed, but must be documented as a known gap. |
| 4 | GLD_ACHAdaptersServices service layer | **Medium** | `insertPayment`, `getSystemDateTime`, `selectACHBatch`, `getNextBatchID` are webMethods IS service wrappers that internally call Oracle procedures. The underlying Oracle SP/SQL names are not in this package — need GLDACHAdaptersServices package source or DB access. |
| 5 | GLDMessageLog:LogXMLRequest | **Low** | Logging service — likely writes to a DB table. The underlying table/SP name is not in this package. Can be replaced with Workato error notification or a generic Oracle logging SP if available. |
| 6 | Debug pipeline save | **Low** | The debug BRANCH that serializes/deserializes the webMethods pipeline to a file is an IS-specific diagnostic feature. No Workato equivalent — omit from recipe. |
| 7 | `processACHBatch` complexity | **High** | This flow is tightly coupled to webMethods built-ins (flat-file schema, batch orchestration) and internal IS services. It is **not a straightforward migration** — recommend a phased approach or custom integration. |
