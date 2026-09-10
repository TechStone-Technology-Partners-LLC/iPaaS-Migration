# Package Analysis — `GLDFundingEngine20080714` → Workato

**Purpose:** the approved blueprint for building the Workato recipe. Section 8 (*Equivalent Recipe Structure*) is the build spec. **Source detail:** `WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md` **Construct mapping reference:** `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx` (22 rows, sheet *wM to Workato Mapping*) **Status:** awaiting review & approval. No Workato assets created.

---

## 1. Package Overview

### 1.1 What the integration does

`GLDFundingEngine` is KeyBank's **payment disbursement router** for the GLD (leasing/lending) platform, built on webMethods Integration Server 6.5 and released 2008-07-14.

An upstream origination system submits a **funding request** — one application header plus N payments — as a SOAP message. The engine walks the payment list and routes each payment to the correct disbursement channel based on its `type`:

- **`Check`** → three HTTP calls into the **CheckWriter** system: find the payee, create the payee if it doesn't exist, then submit the check request.  
- **`ACH`** → one **Oracle** insert into an ACH staging table. Nothing moves yet; a nightly batch drains the table.  
- **anything else** (incl. `Wire`) → accepted, no action, reported as `"Default"`.

It replies **synchronously** with a per-payment status. A failure on one payment is caught, logged, and recorded against that payment — the remaining payments still process.

A second, independent service (`processACHBatch`) sweeps the ACH staging table nightly and renders a **NACHA fixed-width file**. It is unfinished — see §9 Gap G-4.

### 1.2 Systems involved

| Role | System | Protocol | In this export? |
| --- | --- | --- | --- |
| Caller | GLD origination platform | SOAP over HTTP | No (external caller) |
| Router | **GLDFundingEngine** (this package) | webMethods IS 6.5 | ✅ Yes |
| Check disbursement | `GLDExpressGateway` — CheckWriter | webMethods flow services (HTTP) | ❌ No |
| ACH staging + batch | `GLD_ACHAdaptersServices` — Oracle JDBC adapter | JDBC / Oracle | ❌ No |
| Audit log | `GLDMessageLog` | webMethods flow services | ❌ No |
| Error monitoring | `WSRProcessStatistics` | webMethods Broker publish | ❌ No |
| Email | `WSRCommon.Utilities.FlowServices` | SMTP | ❌ No |

### 1.3 Data flow

```
  Caller (SOAP)
      │  fundingEngineWrapperInput  { applicationInfo, payments[] }
      ▼
  fundingEngineWrapper ──► GLDMessageLog:LogXMLRequest  (AppID=3, ID1="FE")
      │
      ▼
  processFundingRequest
      │  REQUESTOR := "1"
      │
      └─ for each payment ──── switch(payment.type)
             │
             ├─ "Check" ─► CheckWriter: getUniquePayee ──► payeeKey
             │              └─ if payeeKey empty ─► CheckWriter: addNewPayee
             │              └─ CheckWriter: createCheckRequest      status := "Paid"
             │
             ├─ "ACH"   ─► Oracle: insertPayment (11 cols)          status := "Paid"
             │
             └─ default ─► (no call)                                status := "Default"
             │
             └─ on error ─► LogXMLRequest("ERROR - processing payment")
                            append Errors[]  ·  publishErrorDoc     status := "Error"
      ▼
  fundingEngineWrapper ──► GLDMessageLog:LogXMLResponse (ID4="FE")
      │  fundingEngineWrapperResponse { paymentResponses[], Errors[] }
      ▼
  Caller (SOAP)
  ── separate, scheduled ──
  processACHBatch ─► Oracle getSystemDateTime ─► selectACHBatch ─► getNextBatchID
                  ─► build NACHA type-6 records ─► flatFile:convertToString
                  ─► [updateBatchIDs DISABLED] ─► [ftp DISABLED] ─► sendEmail
```

### 1.4 Migration scope decision

| Service | Decision |
| --- | --- |
| `fundingEngineWrapper` + `processFundingRequest` | **Merge into ONE Workato recipe.** Recipe 1. |
| `processACHBatch` | **Defer to phase 2** as a separate scheduled recipe. See §9 G-4/G-7/G-8. |
| `processACHBatch_venkat` | Do not migrate — dead developer copy. |
| `register`/`unregisterFlowServiceForSOAP` | Do not migrate — replaced by Workato API Platform. |
| `/debug` pipeline harness | Do not migrate — developer tooling. |

**Why merge the wrapper into the core recipe?** The wrapper's SOAP/XML marshalling steps (`getBody`, `xmlNodeToDocument`, `documentToXMLString`, `xmlStringToXMLNode`, `createSoapData`, `addBodyEntry`) have **no Workato equivalent and no business meaning** — Workato's callable-recipe trigger handles request/response serialisation natively. What *is* meaningful in the wrapper is the `LogXMLRequest` / `LogXMLResponse` audit pair, which belongs in the same recipe as the logic it brackets. Two recipes would force an artificial callable-recipe hop for zero benefit.

---

## 2. Shapes & Logic Breakdown

Every construct found in `fundingEngineWrapper` + `processFundingRequest`, with its Workato equivalent. The **Map row** column cites the row number in *Agent Bridge Web Methods to Workato Component Mapping.xlsx*; **—** means the construct has no row in that file and the equivalent was chosen by judgement (all such choices are itemised in §9).

| # | webMethods shape | Source location | Workato equivalent | Map row |
| --- | --- | --- | --- | --- |
| S-1 | SOAP processor registration (`pub.soap.processor:registerProcessor`, directive `GLDFundingEngine`) | Registration | **API Platform endpoint** on a callable recipe. No step — configuration. | — |
| S-2 | `pub.soap.utils:getBody` | wrapper | *Dropped* — trigger deserialises natively | — |
| S-3 | `pub.xml:xmlNodeToDocument` | wrapper | *Dropped* — trigger schema replaces it | — |
| S-4 | `INVOKE GLDMessageLog:LogXMLRequest` | wrapper | **HTTP action** (`http/post`) | 22 |
| S-5 | `INVOKE processFundingRequest` | wrapper | *Dropped* — inlined into the same recipe | — |
| S-6 | `INVOKE GLDMessageLog:LogXMLResponse` | wrapper | **HTTP action** (`http/post`) | 22 |
| S-7 | `pub.xml:documentToXMLString` → `xmlStringToXMLNode` → `createSoapData` → `addBodyEntry` | wrapper | *Dropped* — `send_reply` serialises natively | — |
| S-8 | `BRANCH SWITCH="/debug"` + save/restorePipelineToFile | processFundingRequest | *Dropped* — developer harness | — |
| S-9 | Outer `SEQUENCE EXIT-ON="SUCCESS"` / `EXIT-ON="FAILURE"` (TRY) | processFundingRequest | **Error monitor / `try` block** | 2 |
| S-10 | Outer `SEQUENCE EXIT-ON="DONE"` (CATCH) | processFundingRequest | **`catch` / on-error block** | 3 |
| S-11 | `MAP MODE="STANDALONE"` seeding `REQUESTOR = "1"` | processFundingRequest | **Static value in the consuming action's input** (no separate step) | 21 |
| S-12 | `LOOP IN-ARRAY=".../payments/payment"` | processFundingRequest | **Repeat for each** (`foreach`), list alias `payment_loop` | 12 |
| S-13 | Inner `SEQUENCE EXIT-ON="FAILURE"` *"On Error Try other payments"* | inside loop | **`try` block nested inside the foreach** | 2 |
| S-14 | Inner `SEQUENCE EXIT-ON="DONE"` (per-payment CATCH) | inside loop | **`rescue` block inside the foreach** | 3 |
| S-15 | `BRANCH SWITCH=".../payment/type"` (3 labelled paths) | inside loop | **`if` / `elsif` / `else`** chain | 6, 10 |
| S-16 | `SEQUENCE NAME="Check"` | branch | `if` clause, condition `type == "Check"` | 5 |
| S-17 | `INVOKE CheckWriter:invokeGetUniquePayee` | Check path | **HTTP action** (`http/post`) | 22 |
| S-18 | `BRANCH SWITCH="/payeeKey"` with `$null` case | Check path | **`if` block**, condition `payeeKey is blank` | 5 |
| S-19 | `INVOKE CheckWriter:invokeAddNewPayee` (**empty input MAP**) | Check path | **HTTP action** — inputs must be named explicitly. See §9 G-1 | 22 |
| S-20 | `INVOKE CheckWriter:invokeCreateCheckRequest` | Check path | **HTTP action** (`http/post`) | 22 |
| S-21 | `SEQUENCE NAME="ACH"` | branch | `elsif` clause, condition `type == "ACH"` | 6, 8 |
| S-22 | `INVOKE GLD_ACHAdaptersServices:insertPayment` (JDBC adapter) | ACH path | **Oracle connector action** — `insert_row` / `execute_stored_procedure` | 20 |
| S-23 | `SEQUENCE NAME="$default"` | branch | `else` clause | 7 |
| S-24 | `MAP MODE="STANDALONE"` writing `paymentResponse` | all 3 paths + catch | **Variable / list-append action.** See §9 G-2 | 21 |
| S-25 | `INVOKE pub.flow:getLastError` | both catches | *Dropped* — Workato exposes `error.message` natively in the rescue block | — |
| S-26 | `SEQUENCE EXIT-ON="DONE"` *"Do not fail the trxn if the logging to DB fails"* | both catches | **Nested `try`/`rescue` around the log action** | 2, 3 |
| S-27 | `INVOKE pub.list:appendToDocumentList` | per-payment catch | **List-append action** (accumulate `Errors[]`) | — |
| S-28 | `INVOKE WSRProcessStatistics.MainFlows:publishErrorDoc` (Broker publish) | all catches | **HTTP action** or Workato **Event Topic** publish. See §9 G-12 | 22 (approx.) |

---

## 3. Connections

Four Workato connections are needed. **None of the target systems ship inside this package export**, so every base URL below is a placeholder that must be confirmed with an SME before the recipe can run.

| # | Connection name | Type | Serves | Auth | Status |
| --- | --- | --- | --- | --- | --- |
| C-1 | `GLDFundingEngine_CheckWriter_Connection` | **HTTP** | S-17, S-19, S-20 | TBD (likely network-internal / basic) | **Create in GUI** |
| C-2 | `GLDFundingEngine_ACH_Oracle_Connection` | **Oracle** | S-22 | DB user + password | **Create with generic placeholder values — user configures in GUI later** |
| C-3 | `GLDFundingEngine_MessageLog_Connection` | **HTTP** | S-4, S-6, and the log action in every catch | TBD | **Create in GUI** |
| C-4 | `GLDFundingEngine_ProcessStats_Connection` | **HTTP** (or Event Topic) | S-28 | TBD | **Create in GUI** |

**Connector selection rationale (mapping-file rule: "find the best connector"):**

- **C-2 uses the Oracle connector, not generic HTTP.** `GLD_ACHAdaptersServices:insertPayment` is a **JDBC adapter service**, not a web service. Mapping row 20 (`INVOKE (DB)` → *oracle connector action*) applies directly. **Per reviewer direction (2026-09-09): create a *new* Oracle connection using generic placeholder connection values — the reviewer will configure the real host, SID, schema and credentials in the Workato GUI after the build.** Do not reuse or point at any previously registered Oracle connection.  
- **C-1, C-3, C-4 use the generic HTTP connector** because the targets are bespoke internal webMethods flow services (`GLDExpressGateway`, `GLDMessageLog`, `WSRProcessStatistics`). There is no purpose-built Workato connector for a private webMethods service; HTTP is the correct choice, per mapping row 22, not a fallback.

**Placeholder connection values** (realistic-looking, to be replaced in the GUI after the build):

| Connection | Placeholder value |
| --- | --- |
| C-1 CheckWriter | `https://gldexpressgateway.keybank.internal/invoke/GLDExpressGateway.ProcessFlows.CheckWriter` |
| C-2 ACH Oracle | JDBC URL `jdbc:oracle:thin:@oracle.keybank.internal:1521:GLDACH` · user `gld_ach_user` · schema `GLD_ACH` |
| C-3 MessageLog | `https://gldmessagelog.keybank.internal/invoke/GLDMessageLog` |
| C-4 ProcessStats | `https://wsrprocessstats.keybank.internal/invoke/WSRProcessStatistics.MainFlows` |

---

## 4. Operations

| Op | Source invocation | Workato connector | Action | Inputs | Output used |
| --- | --- | --- | --- | --- | --- |
| O-1 | `GLDMessageLog:LogXMLRequest` (wrapper) | HTTP (C-3) | `POST /LogXMLRequest` | `AppID="3"`, `RequestIdentifier1="FE"`, `RequestDoc`=whole request | `MessageLogID` → correlate with O-2 |
| O-2 | `GLDMessageLog:LogXMLResponse` (wrapper) | HTTP (C-3) | `POST /LogXMLResponse` | `MessageLogID` (from O-1), `ResponseIdentifier4="FE"`, `ResponseDoc`=whole response | — |
| O-3 | `CheckWriter:invokeGetUniquePayee` | HTTP (C-1) | `POST /invokeGetUniquePayee` | `PayeeInformation` (11 fields, §5.1) | `payeeKey` |
| O-4 | `CheckWriter:invokeAddNewPayee` | HTTP (C-1) | `POST /invokeAddNewPayee` | ⚠️ **unspecified in source** — see §9 G-1 | `payeeKey` |
| O-5 | `CheckWriter:invokeCreateCheckRequest` | HTTP (C-1) | `POST /invokeCreateCheckRequest` | `CheckRequest` (7 fields, §5.2) | — (fire and forget) |
| O-6 | `GLD_ACHAdaptersServices:insertPayment` | **Oracle (C-2)** | `insert_row` on the ACH staging table, **or** `execute_stored_procedure` | 11 params (§5.3) | — |
| O-7 | `GLDMessageLog:LogXMLRequest` (error) | HTTP (C-3) | `POST /LogXMLRequest` | `AppID="3"`, `RequestIdentifier1`=context string, `Request`=error text | — |
| O-8 | `WSRProcessStatistics:publishErrorDoc` | HTTP (C-4) | `POST /publishErrorDoc` | `errorDoc` (8 fields, §5.5) | — |

> **O-6 note.** The source is a webMethods JDBC *adapter service*, whose underlying SQL is defined in the `GLD_ACHAdaptersServices` package — **not in this export**. Whether it is a plain `INSERT` or a stored procedure cannot be determined from these files. §9 G-13 tracks this; the SME must supply the table name (or procedure name) and column list before O-6 can be finalised.

### Deferred to phase 2 (`processACHBatch`)

| Op | Source | Workato equivalent |
| --- | --- | --- |
| O-9 | `GLD_ACHAdaptersServices:getSystemDateTime` | Oracle `select` (`SELECT SYSDATE FROM DUAL`) |
| O-10 | `GLD_ACHAdaptersServices:selectACHBatch(maxDateTime)` | Oracle `select_rows` |
| O-11 | `GLD_ACHAdaptersServices:getNextBatchID` | Oracle `select` (sequence `NEXTVAL`) |
| O-12 | `pub.flatFile:convertToString` (NACHA, 94-byte fixed width) | **No Workato equivalent** — custom Ruby/formula. §9 G-11 |
| O-13 | `GLD_ACHAdaptersServices:updateBatchIDs` | Oracle `update_rows` (**disabled in source**) |
| O-14 | `pub.client:ftp` | Workato **FTP/SFTP connector** (**disabled in source**) |
| O-15 | `WSRCommon.Utilities.FlowServices:sendEmail` | Workato **Email connector** — `send_email` with attachment |

---

## 5. Data Mappings

### 5.1 O-3 `invokeGetUniquePayee` ← payment

| Target (`PayeeSearch`) | Source | Transform |
| --- | --- | --- |
| `PayeeName` | `payment.payee.name` | direct |
| `AddressLine1` | `payment.payee.address1` | direct |
| `AddressLine2` | `payment.payee.address2` | direct (optional) |
| `City` | `payment.payee.city` | direct |
| `State` | `payment.payee.state_province` | direct |
| `PostalCode` | `payment.payee.zip` | direct |
| `PhoneNumber` | `payment.payee.phone` | direct (optional) |
| `FaxNumber` | `payment.payee.fax` | direct (optional) |
| `ContactName` | `payment.payee.contactName` | direct (optional) |
| `ContactPhoneNumber` | `payment.payee.contactPhone` | direct (optional) |
| `Country` | — | **constant `"USA"`** |

### 5.2 O-5 `invokeCreateCheckRequest` ← payment + payee lookup

| Target (`CheckRequest`) | Source | Transform |
| --- | --- | --- |
| `PayeeKey` | `payeeKey` from O-3, or from O-4 if O-3 returned blank | conditional |
| `Notes` | `payment.invoiceReference` | direct |
| `Comments` | `payment.comment` | direct |
| `CheckAmount` | `payment.amount` | direct |
| `Memo` | `payment.checkMemo` | direct |
| `PayeeName` | `payment.payee.name` | direct |
| `LeaseNumber` | `applicationInfo.id` | direct — **from the header, not the payment** |

### 5.3 O-6 `insertPayment` ← application header + payment (11 columns)

| Column | Source | Transform |
| --- | --- | --- |
| `REQUESTOR_ID` | — | **constant `"1"`** |
| `APP_ID` | `applicationInfo.id` | direct |
| `CUSTOMER_NAME` | `applicationInfo.customerName` | direct |
| `CUSTOMER_ID` | `applicationInfo.customerID` | direct |
| `SOURCE` | `applicationInfo.sourceName` | direct |
| `AMOUNT` | `payment.amount` | direct |
| `REFERENCE` | `payment.invoiceReference` | direct |
| `PAYEE_ID` | `payment.payee.id` | direct |
| `PAYEE_NAME` | `payment.payee.name` | direct |
| `ACCOUNT_NUMBER` | `payment.payee.accountNumber` | direct |
| `ROUTING_NUMBER` | `payment.payee.routingNumber` | direct |

### 5.4 Response mapping (per payment)

| Target (`paymentResponse`) | Check path | ACH path | Default path | Error path |
| --- | --- | --- | --- | --- |
| `id` | `payment.id` | `payment.id` | `payment.id` | `payment.id` |
| `status` | `"Paid"` | `"Paid"` | `"Default"` | `"Error"` |
| `errorDescription` | — | — | — | `error.message` |

### 5.5 O-8 `publishErrorDoc` — all constant except `system_message`

| Field | Value |
| --- | --- |
| `severity_level` | `"CRITICAL"` |
| `appl_id` | `"GLD"` |
| `entry_type` | `"E"` |
| `sender_id` | `"EFW"` |
| `receiver_id` | `"WMB"` |
| `transaction_type` | `"XML"` |
| `service_name` | `"GLDExpressGateway.MainFlows.EFW:processLXIRequest"` ⚠️ **wrong in source — §9 G-5** |
| `system_message` | `error.message` (source uses `lastError/errorDump`) |

### 5.6 Trigger schema (from `fundingEngineWrapperInput`)

```
applicationInfo : object
  id                  string   required
  customerName        string   required
  customerID          string   required
  sourceName          string   optional
  sourceSubCategory   string   optional
  salesRepName        string   optional
payments : array of object
  id                  string   required
  type                string   required     -- "Check" | "ACH" | other
  payee : object
    id                string   required
    type              string   required
    name              string   required
    address1          string   required
    address2          string   optional
    city              string   required
    state_province    string   required
    zip               string   required
    phone             string   optional
    fax               string   optional
    contactName       string   optional
    contactPhone      string   optional
    routingNumber     string   optional     -- ACH only
    accountNumber     string   optional     -- ACH only
  amount              string   required
  invoiceReference    string   optional
  comment             string   optional
  checkMemo           string   optional
  status              string   required     -- accepted, never read
  glCode              string   optional     -- accepted, never read
  glAmount            string   optional     -- accepted, never read
  glDescription       string   optional     -- accepted, never read
```

> **Fidelity note.** `sourceSubCategory`, `salesRepName`, `payment.status`, `glCode`, `glAmount`, `glDescription` and `payee.type` are never consumed by the flow. They stay in the trigger schema so the contract remains backward-compatible for existing callers. The `debug` input is **deliberately dropped** (§9 G-10).  
>   
> **Fallback if nested arrays are not supported** by the chosen trigger type: flatten `applicationInfo` to six scalar fields and accept `payments` as a **JSON string**, then apply `.parse_json` before the `foreach`. Prefer the true nested schema.

### 5.7 Reply schema (from `fundingEngineWrapperOutput`)

```
paymentResponses : array of object
  id                string
  status            string     -- "Paid" | "Default" | "Error"
  errorDescription  string
Errors : array of object        -- only populated on failure
  errorCode         string
  errorDescription  string
```

---

## 6. Business Rules & Conditions

| # | Rule | Source | Workato implementation |
| --- | --- | --- | --- |
| BR-1 | Iterate every payment in the request independently | `LOOP IN-ARRAY` | `foreach` over `payments`, alias `payment_loop` |
| BR-2 | `type == "Check"` → CheckWriter path (3 calls) | `SEQUENCE NAME="Check"` | `if payment.type equals "Check"` |
| BR-3 | `type == "ACH"` → Oracle staging insert | `SEQUENCE NAME="ACH"` | `elsif payment.type equals "ACH"` |
| BR-4 | Any other type → no action, status `"Default"` | `SEQUENCE NAME="$default"` | `else` |
| BR-5 | **Create the payee only if the search returned nothing** | `BRANCH SWITCH="/payeeKey"`, `$null` case | `if payeeKey is blank` → call O-4 |
| BR-6 | Country is always `USA` on payee search | constant setter | static input value |
| BR-7 | Requestor is always `1` on ACH insert | `REQUESTOR = "1"` | static input value |
| BR-8 | A failure on one payment must not abort the others | per-payment TRY/CATCH inside the loop | `try`/`rescue` **inside** the `foreach` — placement is what makes this work |
| BR-9 | A failure while logging an error must not abort the payment | nested `SEQUENCE EXIT-ON="DONE"` | nested `try`/`rescue` around the log action |
| BR-10 | Errors accumulate into a list across iterations | `pub.list:appendToDocumentList` | list-append action |
| BR-11 | Every request and response is audit-logged under `AppID = 3` | wrapper O-1 / O-2 | HTTP actions at the top and bottom of the recipe |
| BR-12 | Batch-level failures are reported separately from payment-level failures | outer catch, different `RequestIdentifier1` | outer `catch` with `"ERROR - processFundingRequest"` |

**Branch evaluation order matters.** webMethods `BRANCH` on a switch value evaluates labelled children in document order and takes the first match, with `$default` last. The Workato `if`/`elsif`/`else` chain reproduces this exactly (mapping rows 5–7, 10) — as long as `Check` is the `if`, `ACH` the `elsif`, and the default the `else`, in that order.

---

## 7. Error Handling

### 7.1 Source model — three nested levels

```
outer TRY  ────────────────────────────────────── level 1: whole request
  └─ foreach payment
       └─ inner TRY ──────────────────────────── level 2: one payment
            └─ business logic
       └─ inner CATCH
            └─ nested TRY around the log call ── level 3: logging must never fail
outer CATCH
     └─ nested TRY around the log call ───────── level 3
```

### 7.2 Level 2 — per-payment catch (`"ERROR - processing payment"`)

1. Nested try → `LogXMLRequest` (`AppID="3"`, `RequestIdentifier1="ERROR - processing payment"`, `Request` = error text, `RequestIdentifier3` = pipeline correlation id)  
2. `paymentResponse` ← `{ id: payment.id, status: "Error", errorDescription: error.message }`  
3. Append to `Errors[]`  
4. `publishErrorDoc` (constants per §5.5)  
5. **Continue with the next payment** — the loop is not broken

### 7.3 Level 1 — outer catch (`"ERROR - processFundingRequest"`)

1. Nested try → `LogXMLRequest` (`AppID="3"`, `RequestIdentifier1="ERROR - processFundingRequest"`)  
2. `Errors[0]` ← `{ errorCode: MessageLogID, errorDescription: error.message }`  
3. `publishErrorDoc`

### 7.4 Workato construction rules

| Rule | Why |
| --- | --- |
| The per-payment `try`/`rescue` must sit **inside** the `foreach`, not around it | Putting it outside would abort the whole batch on the first bad payment — the exact behaviour BR-8 exists to prevent. This is the single most important structural detail in the migration. |
| Log actions in a rescue get their **own** nested `try`/`rescue` | Reproduces the source's *"Do not fail the trxn if the logging to DB fails"* sequences (BR-9) |
| Use Workato's native `error.message` | Replaces `pub.flow:getLastError`; no separate step needed |
| No retry logic to migrate | All six services have `retry_max = 0`, `retry_interval = 0` (verified in every `node.ndf`) |
| Reply is sent even when payments failed | The source always returns a `fundingEngineWrapperResponse`; failures surface as `status = "Error"` plus `Errors[]`, **not** as a SOAP fault |

---

## 8. Equivalent Recipe Structure — BUILD SPEC

**Recipe name:** `GLD Funding Engine — processFundingRequest` **Type:** callable / API-callable recipe (`workato_service/receive_request` + `send_reply`)

```
TRIGGER  workato_service/receive_request  — "GLD Funding Engine"
         input schema per §5.6
 1  TRY                                                  [S-9 · outer error monitor]
 2  │  HTTP POST  MessageLog/LogXMLRequest               [O-1 · C-3]
    │     AppID="3" · RequestIdentifier1="FE" · RequestDoc = whole request
    │     → capture MessageLogID
    │
 3  │  FOREACH payments  as payment_loop                 [S-12 · BR-1]
 4  │  │  TRY                                            [S-13 · BR-8 — INSIDE the loop]
 5  │  │  │  IF payment.type == "Check"                  [BR-2]
 6  │  │  │  │  HTTP POST CheckWriter/invokeGetUniquePayee   [O-3 · C-3→C-1 · map §5.1]
    │  │  │  │     → payeeKey
 7  │  │  │  │  IF payeeKey is blank                     [BR-5]
 8  │  │  │  │  │  HTTP POST CheckWriter/invokeAddNewPayee   [O-4 · C-1 · ⚠️ G-1]
    │  │  │  │  │     → payeeKey
 9  │  │  │  │  HTTP POST CheckWriter/invokeCreateCheckRequest [O-5 · C-1 · map §5.2]
10  │  │  │  │  paymentResponse ← { id, status:"Paid" }
    │  │  │  │
11  │  │  │  ELSIF payment.type == "ACH"                 [BR-3]
12  │  │  │  │  ORACLE insert  ACH staging table         [O-6 · C-2 · map §5.3]
13  │  │  │  │  paymentResponse ← { id, status:"Paid" }
    │  │  │  │
14  │  │  │  ELSE                                        [BR-4]
15  │  │  │  │  paymentResponse ← { id, status:"Default" }   (no external call)
    │  │  │
16  │  │  RESCUE                                         [S-14 · per-payment]
17  │  │  │  TRY                                         [BR-9]
18  │  │  │  │  HTTP POST MessageLog/LogXMLRequest       [O-7 · C-3]
    │  │  │  │     AppID="3" · RequestIdentifier1="ERROR - processing payment"
    │  │  │  │     Request = error.message
19  │  │  │  RESCUE → (swallow)
20  │  │  │  paymentResponse ← { id, status:"Error", errorDescription: error.message }
21  │  │  │  append to Errors[]                          [BR-10]
22  │  │  │  HTTP POST ProcessStats/publishErrorDoc      [O-8 · C-4 · map §5.5]
    │
23  │  HTTP POST  MessageLog/LogXMLResponse              [O-2 · C-3]
    │     MessageLogID (step 2) · ResponseIdentifier4="FE" · ResponseDoc = reply
    │
24  │  send_reply  { paymentResponses[], Errors[] }      [§5.7]
    │
25  CATCH                                                [S-10 · outer]
26  │  TRY                                               [BR-9]
27  │  │  HTTP POST MessageLog/LogXMLRequest             [O-7 · C-3]
    │  │     AppID="3" · RequestIdentifier1="ERROR - processFundingRequest"
28  │  RESCUE → (swallow)
29  │  Errors[0] ← { errorCode: MessageLogID, errorDescription: error.message }
30  │  HTTP POST ProcessStats/publishErrorDoc            [O-8 · C-4]
```

### 8.1 Build rules

| # | Rule |
| --- | --- |
| B-1 | **Never hand-author datapill paths.** Use `recipe_builder_get_datapills` for every input binding. |
| B-2 | The per-payment `try`/`rescue` (steps 4/16) goes **inside** the `foreach` (step 3). Non-negotiable — BR-8. |
| B-3 | `Check` is the `if`, `ACH` the `elsif`, default the `else`, in that order — preserves BR-2/3/4 evaluation order. |
| B-4 | Constants `"USA"` (§5.1), `"1"` (§5.3), `"3"`, `"FE"` and the §5.5 error constants are **static input values**, not steps. |
| B-5 | Configure each connector action **fully — every field — before moving to the next**, per Instruction_Workato.md Step 3. |
| B-6 | Where a connection cannot be created (C-1, C-3, C-4 need SME URLs; **C-2 Oracle uses generic placeholder values by reviewer direction**), still configure the action completely with the §3 placeholder value and record the wiring as a manual GUI step. |
| B-7 | Use `error.message` in rescue blocks; do not attempt to recreate `pub.flow:getLastError`. |
| B-8 | Do **not** carry over the `debug` input or the pipeline save/restore steps. |

### 8.2 Phase 2 — `processACHBatch` (separate recipe, not built now)

```
TRIGGER  scheduler (frequency unknown — §9 G-9)
 1  TRY
 2  │  ORACLE  SELECT SYSDATE FROM DUAL              → maxDateTime      [O-9]
 3  │  ORACLE  selectACHBatch(maxDateTime)           → results[]        [O-10]
 4  │  ORACLE  getNextBatchID                        → batchID          [O-11]
 5  │  FOREACH results → build one 94-byte NACHA type-6 record          [§6.3 of the source analysis]
 6  │  custom formula/Ruby → fixed-width string                         [O-12 · G-11]
 7  │  ORACLE  updateBatchIDs(batchID, maxDateTime)                     [O-13 · disabled in source]
 8  │  SFTP    put ach file                                             [O-14 · disabled in source]
 9  │  EMAIL   to steven.a.miller@key.com, attachment ach.txt           [O-15]
10  CATCH → LogXMLRequest("ERROR - processACHBatch") → publishErrorDoc
```

**Do not build phase 2 until G-4, G-7, G-8 and G-11 are resolved** — the source produces an invalid NACHA file and never commits the batch.

---

## 9. Mapping Gaps / Deviations

### 9.1 Decisions needed before the build

| ID | Sev | Gap | Recommendation |
| --- | --- | --- | --- |
| **G-1** | **HIGH** | **`invokeAddNewPayee` has an empty input MAP.** The source relies on webMethods implicit pipeline name-matching; Workato has no ambient pipeline, so inputs must be named. The service's real signature lives in `GLDExpressGateway`, which is **not in this export**. | Send the same `PayeeInformation` payload built for O-3 (§5.1) — it is still in scope at that point in the source pipeline. **Confirm with SME** before go-live. |
| **G-2** | **HIGH** | **The source overwrites `paymentResponse` on every iteration.** It is declared `record[]` but every write targets dim `;2;0` with no append, while `Errors/Error` is written at `;4;1` *with* `appendToDocumentList`. The 2008 SOAP reply therefore returns **only the last payment's status**. | Almost certainly a latent bug. **Recommend fixing**: accumulate one `paymentResponse` per payment. Flagged as a deliberate, documented deviation from source behaviour. **Needs your call.** |
| **G-3** | **HIGH** | **`Wire` payments silently succeed.** The `$default` branch makes no call and returns `"Default"`, not an error. Any unrecognised `type` lands here. | Replicate faithfully (it is the documented 2008 behaviour), but surface it to the business. If `Wire` should now be handled or rejected, that is new scope. |
| **G-13** | **HIGH** | **The ACH insert's SQL is unknown.** `GLD_ACHAdaptersServices:insertPayment` is a JDBC adapter service defined outside this export — table name vs. stored-procedure name cannot be determined from these files. | Configure the Oracle action against the 11 columns in §5.3 and obtain the exact target from the SME. |

### 9.2 Constructs with no row in the mapping spreadsheet

The mapping file covers 22 control-flow and invoke constructs. These appear in the package and have **no row**; the equivalent below is a judgement call, per the mapping file's own "not a strict rulebook" guidance.

| ID | Sev | Construct | Chosen equivalent | Rationale |
| --- | --- | --- | --- | --- |
| G-14 | LOW | `pub.soap.utils:getBody` / `createSoapData` / `addBodyEntry`, `pub.xml:xmlNodeToDocument` / `documentToXMLString` / `xmlStringToXMLNode` | **Dropped entirely** | Pure SOAP/XML marshalling. The Workato callable-recipe trigger and `send_reply` handle serialisation natively. No business logic is lost. |
| G-15 | **MED** | **SOAP protocol itself** (`registerProcessor`, directive `GLDFundingEngine`) | **REST/JSON callable recipe** on Workato API Platform | ⚠️ **Protocol change.** Existing SOAP callers **will not work unmodified**. Either callers migrate to REST, or a SOAP→REST façade is needed. This is the largest behavioural deviation in the migration. |
| G-16 | LOW | `pub.flow:getLastError` | Native `error.message` in the rescue block | Direct semantic equivalent |
| G-17 | LOW | `pub.list:appendToDocumentList` | List-append action / list variable | Row 21 (MAP) is the closest but does not cover list accumulation |
| G-12 | **MED** | `WSRProcessStatistics:publishErrorDoc` — a **webMethods Broker publish** (async pub/sub), not a request/reply call | **HTTP POST**, or a Workato **Event Topic** if one exists | Row 22 (`INVOKE (HTTP)`) is the pragmatic choice, but it converts an **async publish into a sync call**. Failure semantics change: a monitoring outage could now slow the funding path. Recommend fire-and-forget with its own try/rescue. |
| G-18 | LOW | Nested TRY *"Do not fail the trxn if the logging to DB fails"* | Nested `try`/`rescue` (rows 2 + 3, applied recursively) | The mapping file does not discuss nesting; Workato supports it |
| G-11 | **HIGH** | `pub.flatFile:convertToString` — 94-byte fixed-width NACHA generation | **No Workato equivalent.** Custom Ruby/formula, or an external service | Phase 2 blocker. Rows 1–22 contain nothing for flat-file handling. |
| G-19 | LOW | `pub.client:ftp` | Workato **SFTP/FTP connector** | Phase 2 (disabled in source anyway) |
| G-20 | LOW | `WSRCommon.Utilities.FlowServices:sendEmail` | Workato **Email connector** (`send_email` with attachment) | Phase 2 |
| G-21 | LOW | `pub.flow:savePipelineToFile` / `restorePipelineFromFile` | **Not migrated** | Developer harness, and `restorePipelineFromFile` is a security concern (G-10) |
| **G-22** | **MED** | **Implicit pipeline as a data model.** webMethods carries an ambient, mutable pipeline; every step reads and writes it by field name, and MAPDELETE "droppers" clean it up. Workato has explicit datapills only. | Every input binding must be resolved explicitly via `recipe_builder_get_datapills`. **This is the root cause of G-1 and the general reason field-level fidelity must be verified per step.** The mapping spreadsheet has no row for this, because it is a paradigm difference rather than a construct. |  |

### 9.3 Source defects carried into the analysis

| ID | Sev | Defect | Recommendation |
| --- | --- | --- | --- |
| G-5 | MED | `errorDoc/service_name` hard-coded to `GLDExpressGateway.MainFlows.EFW:processLXIRequest` in all three catch blocks — a copy-paste leftover. Central monitoring attributes every failure to the wrong service. | **Recommend fixing** to `GLDFundingEngine.MainFlows:processFundingRequest`. Deviation from source, flagged. |
| G-6 | LOW | `errorDoc/system_message` is mapped twice (`lastError/error`, then overwritten by `lastError/errorDump`) | Map once from `error.message` |
| G-7 | MED | NACHA `R/T CheckDigit` hard-coded to `9` instead of computed | Phase 2 — implement the NACHA mod-10 check digit |
| G-8 | HIGH | NACHA `Trace Number` hard-coded to `113000600000001` for every record; NACHA requires a unique sequential trace per entry | Phase 2 — blocker |
| G-4 | MED | `processACHBatch` never commits: `updateBatchIDs` and `ftp` are both `DISABLED="true"` | Phase 2 — clarify intended behaviour with the SME before building |
| G-9 | MED | No scheduled-task definition in the export; `processACHBatch` frequency is unknown | Obtain the schedule from the SME |
| G-10 | LOW | The `debug` input lets a caller trigger `restorePipelineFromFile` | **Dropped** from the trigger schema |
| G-11b | LOW | Blank FTP password stored in the flow | Not carried forward; use a Workato connection |

### 9.4 Open questions for the SME (do not block the analysis)

1. Base URLs for CheckWriter, GLDMessageLog and WSRProcessStatistics (§3 placeholders).  
2. Auth scheme for each of those three endpoints.  
3. `invokeAddNewPayee` request contract (G-1).  
4. ACH staging table or stored-procedure name and column list (G-13).  
5. ~~Oracle credentials/host for the ACH schema~~ — **resolved 2026-09-09:** reviewer will configure the Oracle connection in the GUI after the build. Build against a generic placeholder.  
6. Exact field name for `payeeKey` in the `invokeGetUniquePayee` response.  
7. `processACHBatch` schedule (G-9).  
8. Whether SOAP callers can move to REST, or whether a façade is required (G-15).

---

## 10. Summary Assessment

| Dimension | Verdict |
| --- | --- |
| Migratable now | `fundingEngineWrapper` + `processFundingRequest` → **one Workato recipe**, 30 steps |
| Deferred | `processACHBatch` → phase 2, blocked on G-4/G-7/G-8/G-11 |
| Not migrated | `processACHBatch_venkat`, SOAP registration services, `/debug` harness, 3 unreferenced schemas |
| Construct coverage by the mapping spreadsheet | 18 of 28 shapes map to a row; **10 required judgement** (§9.2) |
| Largest behavioural deviation | **SOAP → REST** (G-15) — existing callers are affected |
| Largest unknown | `invokeAddNewPayee` contract (G-1) — empty input MAP in the source |
| Recommended source-bug fixes | G-2 (accumulate payment responses), G-5 (correct `service_name`) |

---

## 11. Reviewer Notes

**2026-09-09 — reviewer comment:** *"Use an oracle connector with a generic url I will configure it later."*

**Applied.** The ACH staging insert (S-22 / O-6) is built with the **Oracle connector**, using a **new connection created with generic placeholder values** (`GLDFundingEngine_ACH_Oracle_Connection`, §3). No existing Oracle connection is reused and no real host, SID, schema or credential is assumed. The reviewer configures the connection in the Workato GUI after the recipe is pushed; this is carried into the post-build manual-steps list.