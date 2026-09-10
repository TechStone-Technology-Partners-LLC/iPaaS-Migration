# webMethods Package Analysis — `GLDFundingEngine20080714`

**Source package:** `WebMethods/GLDFundingEngine20080714/` (pre-existing folder in the repo, reused as-is)
**Analysis date:** 2026-09-09
**Analyst:** MigrAIte (webMethods → Workato migration agent)
**Scope:** Step 1 (Analyze) of `initiate_migration/Instruction_Workato.md`. No Workato assets were created or touched.

> **Evidence basis.** Every statement below is derived from the 38 files in the package export. Where the package
> references a component that lives *outside* this export (e.g. `GLD_ACHAdaptersServices`), that is stated
> explicitly and listed as a gap rather than guessed at.

---

## 1. Package Identity & Metadata

| Attribute | Value | Source file |
|---|---|---|
| Release name | `GLDFundingEngine20080714` | `manifest.rel` |
| Target package name | `GLDFundingEngine` | `manifest.rel` |
| Version | 1.0 | `manifest.rel` / `manifest.v3` |
| Build timestamp | 2008-07-14 12:56:18 EDT | `manifest.rel` |
| Publisher host | `cwb02dwmis02.keybank.com` | `manifest.rel` |
| Source/target IS version | webMethods Integration Server 6.5 | `manifest.rel` |
| JVM | 1.4.2 | `manifest.rel` |
| Export type | `full` | `manifest.rel` |
| Package enabled on export | **`no`** | `manifest.v3` |
| Declared dependency | `WmFlatFile` 6.5 | `manifest.v3` |
| Startup service | `GLDFundingEngine.Wrappers.Registration:registerFlowServiceForSOAP` | `manifest.v3` |
| Shutdown service | `GLDFundingEngine.Wrappers.Registration:unregisterFlowServiceForSOAP` | `manifest.v3` |
| List ACL | `Default` | `manifest.v3` |
| XML namespace | `https://webmethods.keybank.com/GLDFundingEngine/Wrappers` | `fundingEngineWrapperInput/node.ndf` |

**Business owner signal.** The `processACHBatch` notification email is addressed to `steven.a.miller@key.com`,
sent from `ACHProcess@key.com`. The developer variant flow additionally mails `venkat.mylavarapu@key.com`.
The `processFundingRequest` header comment is authored by `millese`, dated 06/11/08.

---

## 2. Complete File Inventory (38 files)

### 2.1 Package-level (5)
| File | Purpose |
|---|---|
| `manifest.v3` | Package config: startup/shutdown services, dependencies, enabled flag |
| `manifest.rel` | Release metadata (name, version, build host, IS version) |
| `manifest.bak` | Backup of a prior manifest (byte-identical content in export) |
| `pub/index.html` | Static package home page — "Welcome To The Home Page For The *GLDFundingEngine* Package." No logic. |

### 2.2 Namespace folders (8 × `node.idf`)
All eight are empty folder markers (`node_type = interface`), carrying no logic:
`GLDFundingEngine`, `.Wrappers`, `.Wrappers.Registration`, `.DocumentTypes`, `.MainFlows`, `.Schemas`,
`.webConnectors`, `.ProcessFlows`.

> **Note:** `DocumentTypes`, `webConnectors` and `ProcessFlows` are **empty folders** in this export.
> The document types that the flows actually use live under `Wrappers/`. There are **no web service
> connectors (`webConnectors`) in this package** — all outbound calls are `INVOKE`s of flow services in
> *other* packages.

### 2.3 Flow services (6, counting the developer variant)
| Service | Lines of flow.xml | Role |
|---|---|---|
| `GLDFundingEngine.Wrappers:fundingEngineWrapper` | 1,997 | **SOAP entry point.** Unwraps SOAP → doc, logs, delegates, logs, rewraps → SOAP |
| `GLDFundingEngine.MainFlows:processFundingRequest` | 5,946 | **Core business logic.** Per-payment routing to CheckWriter / ACH |
| `GLDFundingEngine.MainFlows:processACHBatch` | 3,037 | **Batch NACHA file build.** Incomplete — see §7 |
| `GLDFundingEngine.MainFlows:processACHBatch_venkat` | 1,734 | Developer scratch variant of the above — **dead code**, see §7.3 |
| `GLDFundingEngine.Wrappers.Registration:registerFlowServiceForSOAP` | 129 | Startup: registers the SOAP processor |
| `GLDFundingEngine.Wrappers.Registration:unregisterFlowServiceForSOAP` | 71 | Shutdown: unregisters the SOAP processor |

### 2.4 Document types (2)
`GLDFundingEngine.Wrappers:fundingEngineWrapperInput`, `GLDFundingEngine.Wrappers:fundingEngineWrapperOutput` — see §4.

### 2.5 Schemas (6)
`Schemas:NACHA` (Document Part Holder / field dictionary), `Schemas:NACHA_Schema` (Flat File Schema, active),
`Schemas:ACH_Schema` (Flat File Schema, unreferenced), `Schemas:NACHA_SchemaDT` (active flat-file document type),
`Schemas:NACHA_SchemaDT1` and `NACHA_SchemaDT2` (unreferenced variants). See §6.

### 2.6 Backups (6 × `.bak`)
Structural diffs were taken between every `.bak` and its live counterpart. The only material change is a
**refactor of the response document type**: the older `.bak` versions wrote into an internal
`GLDFundingEngine.DocumentTypes:fundingResponse` document which the wrapper then copied into
`fundingEngineWrapperOutput`. The live versions write directly into `fundingEngineWrapperOutput`, and the
intermediate `fundingResponse` doc type was deleted (which is why `DocumentTypes/` is now empty).
**No business logic differs between `.bak` and live.** `processACHBatch` and `processACHBatch_venkat` backups
are byte-identical to their live files.

---

## 3. Integration Logic — Plain-English Walkthrough

There are **two independent integrations** in this package. They are coupled only through a shared Oracle
ACH staging table, not through any direct call.

### 3.1 Integration A — Real-time funding request (synchronous, SOAP)

> *"An external lending/leasing application submits a funding request containing one application header and
> N payments. For each payment, route it to the correct disbursement system based on its `type`: checks go
> to the CheckWriter system over HTTP; ACH payments are parked in an Oracle staging table for later batch
> processing. Reply synchronously with a per-payment status. A failure on one payment must not abort the
> remaining payments."*

**Flow, end to end:**

1. **SOAP arrives.** At IS startup, `registerFlowServiceForSOAP` binds `GLDFundingEngine.Wrappers:fundingEngineWrapper`
   to the SOAP directive **`GLDFundingEngine`**, described as *"SOAP processor for GLD funding requests"*.
   The live endpoint is therefore `http(s)://<is-host>:<port>/soap/GLDFundingEngine`.
2. **Unwrap.** `pub.soap.utils:getBody` extracts the SOAP body node → `pub.xml:xmlNodeToDocument`
   (`documentTypeName = GLDFundingEngine.Wrappers:fundingEngineWrapperInput`, `makeArrays = false`)
   converts it into the typed `fundingEngineWrapperInput` document.
3. **Log the request.** `GLDMessageLog:LogXMLRequest` is called with `AppID = 3`,
   `RequestIdentifier1 = "FE"`, `RequestDoc = <the whole inbound document>`. It returns a `MessageLogID`,
   stashed in the pipeline as `MessageLogID_FundingEngine` for correlation with the response log.
4. **Delegate.** `GLDFundingEngine.MainFlows:processFundingRequest` runs the business logic (§3.1.1).
5. **Log the response.** `GLDMessageLog:LogXMLResponse` with the stashed `MessageLogID` and
   `ResponseIdentifier4 = "FE"`.
6. **Rewrap.** `pub.xml:documentToXMLString` (`encode = true`,
   `documentTypeName = GLDFundingEngine.Wrappers:fundingEngineWrapperOutput`) →
   `pub.xml:xmlStringToXMLNode` (`isXML = true`) → `pub.soap.utils:createSoapData` →
   `pub.soap.utils:addBodyEntry` → returned as `soapResponseData`.

#### 3.1.1 `processFundingRequest` — the core logic

**Step 0 — Debug harness (developer-only).**
A `BRANCH` on `/debug`:
- `debug` is null → `pub.flow:savePipelineToFile`, filename `FundingEngineRequest`
- `debug == "true"` → `pub.flow:restorePipelineFromFile`, filename `FundingEngineRequest`

This is a developer pipeline-capture/replay harness, not business logic. **It must not be migrated.**

**Step 1 — Outer TRY/CATCH.** `SEQUENCE EXIT-ON="SUCCESS"` wrapping `SEQUENCE EXIT-ON="FAILURE"` (TRY) plus a
sibling `SEQUENCE EXIT-ON="DONE"` (CATCH). This is the canonical webMethods try/catch idiom.

**Step 2 — Initialise.** A standalone MAP seeds an empty `fundingEngineWrapperOutput` document and sets the
constant **`REQUESTOR = "1"`**.

**Step 3 — LOOP over payments.**
`LOOP IN-ARRAY="/fundingEngineWrapperInput/ns1:fundingEngineWrapper/fundingRequest/payments/payment"`.

Inside each iteration there is a **second, nested TRY/CATCH** commented *"On Error Try other payments"* —
this is what makes a single bad payment non-fatal to the batch.

**Step 4 — Three-way BRANCH on `payment/type`:**

| Label | Path |
|---|---|
| `Check` | CheckWriter sub-flow (below) |
| `ACH` | Oracle staging insert (below) |
| `$default` | No external call — status only |

**Check path (3 outbound calls, one conditional):**
1. `GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee` — search for an existing payee by
   name + full address. Returns `payeeKey`.
2. `BRANCH SWITCH="/payeeKey"` with a single `$null` case →
   `GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee`.
   **i.e. only create the payee if the search found nothing.**
   ⚠️ This INVOKE has a **completely empty input MAP** — it relies on webMethods' implicit
   pipeline name-matching to pick up `PayeeInformation` (and whatever else is in scope). See §8, Gap G-1.
3. `GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest` — submit the check request using
   the (found or newly created) `payeeKey`.
4. Set `paymentResponse.id = payment.id`, `paymentResponse.status = "Paid"`.

**ACH path (1 outbound call):**
1. `GLD_ACHAdaptersServices:insertPayment` — a **JDBC adapter service** (external package) that inserts a
   row into the ACH staging table. 11 parameters, see §5.3.
2. Set `paymentResponse.id = payment.id`, `paymentResponse.status = "Paid"`.

**Default path (`$default` — covers `Wire` and anything else):**
1. No external call at all. Set `paymentResponse.id = payment.id`, `paymentResponse.status = "Default"`.

> **Business consequence:** a payment of type `Wire` (or any unrecognised type) is silently accepted and
> reported as `"Default"`. **No money moves and no error is raised.** The service comment confirms the
> intent — *"Currently it only handles Checks and ACH payments."*

**Step 5 — Per-payment CATCH.** On any failure inside one payment:
1. `pub.flow:getLastError` → `lastError` (`pub.event:exceptionInfo`), restoring the captured `pipeline`.
2. Build an `errorDoc`: `service_name = lastError/callStack[0]/service`, `system_message = lastError/error`,
   then **immediately overwritten** by `system_message = lastError/errorDump` (see §8, Gap G-6).
3. **Nested TRY** commented *"Do not fail the trxn if the logging to DB fails"* wrapping
   `GLDMessageLog:LogXMLRequest` with `AppID = 3`, `RequestIdentifier1 = "ERROR - processing payment"`,
   `Request = <error text>`, `RequestIdentifier3 = pipeline/REQUESTIDENTIFIER3`.
4. Set `paymentResponse.status = "Error"`, `errorDescription = lastError/error`, `id = payment.id`.
5. Append an `Error` document to `fundingEngineWrapperResponse/Errors/Error[]` via
   `pub.list:appendToDocumentList`.
6. `WSRProcessStatistics.MainFlows:publishErrorDoc` — publishes the errorDoc to the webMethods Broker for
   central monitoring (constants in §5.5).
7. Execution **continues with the next payment**.

**Step 6 — Outer CATCH.** Identical shape to the per-payment catch, but:
- `RequestIdentifier1 = "ERROR - processFundingRequest"`
- Writes to the top-level `Errors/Error[0]` with `errorCode = MessageLogID` and
  `errorDescription = lastError/error` (no per-payment context).

### 3.2 Integration B — Nightly ACH batch (`processACHBatch`)

> *"Sweep everything that Integration A parked in the ACH staging table, render it as a NACHA fixed-width
> file, mark the rows as batched, and deliver the file."*

`processACHBatch` takes **no inputs and produces no outputs** (verified from `node.ndf` — empty signature),
so it is designed to be driven by a webMethods **Scheduled Task**. *No scheduler definition is included in
this package export* — see §8, Gap G-9.

**Flow:**
1. **TRY block opens.**
2. `GLD_ACHAdaptersServices:getSystemDateTime` → `maxDateTime` (DB clock, not IS clock — a deliberate
   choice so the high-water mark is consistent with the rows being selected).
3. `GLD_ACHAdaptersServices:selectACHBatch(maxDateTime)` → `results[]` — all unbatched payments up to that
   instant.
4. `GLD_ACHAdaptersServices:getNextBatchID` → `batchID`.
5. **LOOP over `selectACHBatchOutput/results`** — map each DB row into one NACHA type-6 Entry Detail record
   (`NACHA_SchemaDT/recordWithNoID[]`). Mapping + constants in §6.3.
6. `pub.flatFile:convertToString` with `ffSchema = GLDFundingEngine.Schemas:NACHA_Schema`, `spacePad = left`
   → the fixed-width file as `string`.
7. `GLD_ACHAdaptersServices:updateBatchIDs(BATCH_ID, PROCESS_DATE)` — **`DISABLED="true"`**.
8. Inner TRY *"Transfer ACH File"*:
   - `pub.client:ftp` — **`DISABLED="true"`** (host `localhost:8888`, user `Administrator`, blank password,
     `put` to `/admin/ftpfiles/PO.txt`)
   - `WSRCommon.Utilities.FlowServices:sendEmail` — **enabled**. To `steven.a.miller@key.com`,
     from `ACHProcess@key.com`, subject `ACH File`, attachment `ach.txt`, body = the NACHA string.
9. **CATCH block** — same idiom as §3.1: `getLastError` → errorDoc → nested-try `LogXMLRequest`
   (`AppID = 3`, `RequestIdentifier1 = "ERROR - processACHBatch"`) → `publishErrorDoc`.

**Assessment: this flow was never finished.** Three independent signals agree:
- The two steps that actually *commit* the batch — `updateBatchIDs` (mark rows as processed) and `ftp`
  (deliver the file) — are both **disabled**.
- The FTP target is `localhost:8888` with user `Administrator` and a blank password — developer scaffolding,
  not a bank's ACH gateway.
- The flat-file schema emits **only type-6 Entry Detail records** (§6.2). A NACHA file is invalid without a
  File Header (1), Batch Header (5), Batch Control (8) and File Control (9). The `NACHA` dictionary
  *defines* fields for all of those record types, but `NACHA_Schema` never references them.

The only live effect of running `processACHBatch` today is to **email an incomplete file to one person**,
leaving the staging rows unmarked so the next run re-sends them.

---

## 4. Document Types (the integration contract)

### 4.1 `GLDFundingEngine.Wrappers:fundingEngineWrapperInput`
Root element `processFundingRequest`; namespace `https://webmethods.keybank.com/GLDFundingEngine/Wrappers`.

```
ns1:fundingEngineWrapper
└── fundingRequest
    ├── applicationInfo
    │   ├── id                 string   (required)  -- the lease/application number
    │   ├── customerName       string   (required)
    │   ├── customerID         string   (required)
    │   ├── sourceName         string   (optional)
    │   ├── sourceSubCategory  string   (optional)
    │   └── salesRepName       string   (optional)
    └── payments
        └── payment[]          record   (unbounded array)
            ├── id                 string   (required)
            ├── type               string   (required)  -- "Check" | "ACH" | other
            ├── payee              record
            │   ├── id                string (required)
            │   ├── type             string (required)
            │   ├── name             string (required)
            │   ├── address1         string (required)
            │   ├── address2         string (optional)
            │   ├── city             string (required)
            │   ├── state_province   string (required)
            │   ├── zip              string (required)
            │   ├── phone            string (optional)
            │   ├── fax              string (optional)
            │   ├── contactName      string (optional)
            │   ├── contactPhone     string (optional)
            │   ├── routingNumber    string (optional)   -- ACH only
            │   └── accountNumber    string (optional)   -- ACH only
            ├── amount             string   (required)
            ├── invoiceReference   string   (optional)
            ├── comment            string   (optional)
            ├── checkMemo          string   (optional)
            ├── status             string   (required)   -- inbound only, never read by the flow
            ├── glCode             string   (optional)   -- never read by the flow
            ├── glAmount           string   (optional)   -- never read by the flow
            └── glDescription      string   (optional)   -- never read by the flow
```

`processFundingRequest` additionally declares an **optional `debug` string** input (the pipeline-capture
harness of §3.1.1 Step 0).

> **Unused inbound fields.** `payment/status`, `payment/glCode`, `payment/glAmount`, `payment/glDescription`,
> `payee/type` and `payee/id` (Check path only) are accepted by the contract but never consumed on their
> respective paths. They must still be present in the migrated trigger schema to keep callers compatible.

### 4.2 `GLDFundingEngine.Wrappers:fundingEngineWrapperOutput`
Root element `fundingResponse`; same namespace.

```
ns1:fundingEngineWrapperResponse
├── paymentResponses
│   └── paymentResponse[]      record  (declared as an array)
│       ├── id               string
│       ├── status           string   -- "Paid" | "Default" | "Error"
│       └── errorDescription string
└── Errors                    record  (optional)
    └── Error[]  -> GLDExpressWebServices.DocumentTypes:Error
        ├── errorCode         (set to MessageLogID in the outer catch)
        └── errorDescription
```

> ⚠️ **Critical finding — see §8 Gap G-2.** Although `paymentResponse` is *declared* as an array, every
> write in `processFundingRequest` targets it at dimension `;2;0` (scalar) and there is **no
> `appendToDocumentList` for it**. By contrast `Errors/Error` is written at `;4;1` (array) *and* appended
> with `pub.list:appendToDocumentList`. The source flow therefore **overwrites the payment response on every
> loop iteration** — the SOAP reply carries only the *last* payment's status.

---

## 5. External Dependencies & Field-Level Mappings

None of the four external systems below ship inside this export. Each is an `INVOKE` of a flow service or
adapter service in a *different* webMethods package.

| # | External namespace | Kind | Used by |
|---|---|---|---|
| E-1 | `GLDExpressGateway.ProcessFlows.CheckWriter` | Flow services (check disbursement) | `processFundingRequest` (Check path) |
| E-2 | `GLD_ACHAdaptersServices` | **JDBC adapter services** (Oracle) | `processFundingRequest` (ACH path), `processACHBatch` |
| E-3 | `GLDMessageLog` | Flow services (XML audit log) | wrapper, both catch blocks, `processACHBatch` |
| E-4 | `WSRProcessStatistics.MainFlows` | Broker publish (central error monitoring) | all catch blocks |
| E-5 | `WSRCommon.Utilities.FlowServices` | SMTP send | `processACHBatch` |

### 5.1 `invokeGetUniquePayee` — input mapping
Target doc: `GLDExpressGateway.DocumentTypes.CheckWriter:PayeeSearch`

| Target field | Source |
|---|---|
| `PayeeName` | `payment/payee/name` |
| `AddressLine1` | `payment/payee/address1` |
| `AddressLine2` | `payment/payee/address2` |
| `City` | `payment/payee/city` |
| `State` | `payment/payee/state_province` |
| `PostalCode` | `payment/payee/zip` |
| `PhoneNumber` | `payment/payee/phone` |
| `FaxNumber` | `payment/payee/fax` |
| `ContactName` | `payment/payee/contactName` |
| `ContactPhoneNumber` | `payment/payee/contactPhone` |
| `Country` | **constant `"USA"`** (enum in the doc type is `USA` \| `CAN`) |

**Output:** `payeeKey` (scalar, dropped into the pipeline root).

### 5.2 `invokeCreateCheckRequest` — input mapping
Target doc: `GLDExpressGateway.DocumentTypes.CheckWriter:CheckRequest`

| Target field | Source |
|---|---|
| `PayeeKey` | `payeeKey` (from search, or from `invokeAddNewPayee`) |
| `Notes` | `payment/invoiceReference` |
| `Comments` | `payment/comment` |
| `CheckAmount` | `payment/amount` |
| `Memo` | `payment/checkMemo` |
| `PayeeName` | `payment/payee/name` |
| `LeaseNumber` | `applicationInfo/id` |

### 5.3 `GLD_ACHAdaptersServices:insertPayment` — input mapping (11 params)
Target doc: `insertPaymentInput`

| DB parameter | Source |
|---|---|
| `REQUESTOR_ID` | **constant `"1"`** (via pipeline var `REQUESTOR`) |
| `APP_ID` | `applicationInfo/id` |
| `CUSTOMER_NAME` | `applicationInfo/customerName` |
| `CUSTOMER_ID` | `applicationInfo/customerID` |
| `SOURCE` | `applicationInfo/sourceName` |
| `AMOUNT` | `payment/amount` |
| `REFERENCE` | `payment/invoiceReference` |
| `PAYEE_ID` | `payment/payee/id` |
| `PAYEE_NAME` | `payment/payee/name` |
| `ACCOUNT_NUMBER` | `payment/payee/accountNumber` |
| `ROUTING_NUMBER` | `payment/payee/routingNumber` |

### 5.4 `GLDMessageLog` — audit logging calls

| Call site | Service | `AppID` | `RequestIdentifier1` | Payload |
|---|---|---|---|---|
| Wrapper, pre-processing | `LogXMLRequest` | `3` | `FE` | `RequestDoc` = whole inbound document |
| Wrapper, post-processing | `LogXMLResponse` | — | `ResponseIdentifier4 = FE` | `ResponseDoc` = whole outbound document, correlated by `MessageLogID` |
| Per-payment catch | `LogXMLRequest` | `3` | `ERROR - processing payment` | `Request` = `lastError/error` |
| Outer catch | `LogXMLRequest` | `3` | `ERROR - processFundingRequest` | `Request` = `lastError/error` |
| `processACHBatch` catch | `LogXMLRequest` | `3` | `ERROR - processACHBatch` | `Request` = `lastError/error` |

### 5.5 `WSRProcessStatistics.MainFlows:publishErrorDoc` — constants
Target doc: `WSRProcessStatistics.DocumentTypes:errorDoc`. **Identical constants in all three catch blocks:**

| Field | Value |
|---|---|
| `severity_level` | `CRITICAL` (enum: WARNING \| CRITICAL \| FATAL \| HARMLESS) |
| `appl_id` | `GLD` |
| `entry_type` | `E` (enum: S \| E \| T \| F) |
| `sender_id` | `EFW` |
| `receiver_id` | `WMB` |
| `transaction_type` | `XML` |
| `service_name` | `GLDExpressGateway.MainFlows.EFW:processLXIRequest` ⚠️ **copy-paste defect — see §8 Gap G-5** |
| `system_message` | `lastError/errorDump` |

---

## 6. Flat File Schemas (NACHA)

### 6.1 `Schemas:NACHA` — Document Part Holder (field dictionary)
A field dictionary defining reusable NACHA field parts. Decoding the `IDataEncoded` blob shows it defines
parts for **all five NACHA record types**, including File Header / Batch Header / Control / Trailer fields:
`Origin Name`, `Block Count`, `Destination Name`, `Immediate Origin Number`, `Priority Code`,
`Effective Entry Date`, `Transmission Time`, `Company Identification`, `Reserved 39`, `Settlement Date`,
`Entry/Addenda Count`, `Originator Status Code`, `Total Debits Dollar Amount`, `Entry Hash`, `Batch Number`,
`Total Credits Dollar Amount`, `Immediate Destination Identification Number`, `Origination ID`,
`File ID Modifier`, `Company Entry Description`, `Format Code`, `Batch Count`, `Company Descriptive Data`,
`Company Discretionary Data`, `Message Authentication Code`, `Reference Code`, `Service Class Code`,
`Standard Entry Class Code`, `Transmission Date`, `Blocking Factor`, `Record Size`, `Company Name`,
`Reserved 6`.

**None of these header/control fields are wired into the active schema.**

### 6.2 `Schemas:NACHA_Schema` — the active Flat File Schema
- Parser: `com.wm.ff.parse.FixedLengthParser`, **`RecordSize = 94`** (the NACHA standard record length)
- Record identifier: `PositionalRecordIdentifier`, `OFFSET = 0`
- Document structure: a single `OrderedNodeContainer` referencing part holder `GLDFundingEngine.Schemas:NACHA`,
  node `BatchRecord`, `MaxOccur = -1` (unbounded), default record `recordWithNoID`
- `AllowUndefinedData = false`

**Entry Detail (type 6) layout — offsets decoded from the schema blob and cross-checked against the
NACHA PPD standard (they agree exactly, and sum to 94):**

| Field | 1-based position | Length | Populated by `processACHBatch` |
|---|---|---|---|
| Record Type Code | 1 | 1 | constant `6` |
| Transaction Code | 2–3 | 2 | constant `22` (checking credit) |
| Routing/Transit Number | 4–11 | 8 | `results/ROUTING_NUMBER` |
| R/T CheckDigit | 12 | 1 | constant `9` ⚠️ |
| Individual Account Number | 13–29 | 17 | `results/ACCOUNT_NUMBER` |
| Amount | 30–39 | 10 | `results/AMOUNT` |
| Individual ID Number | 40–54 | 15 | `results/REFERENCE` |
| Individual Name | 55–76 | 22 | `results/PAYEE_NAME` |
| Discretionary Data | 77–78 | 2 | constant `" "` (space) |
| Addenda Indicator | 79 | 1 | constant `0` |
| Trace Number | 80–94 | 15 | constant `113000600000001` ⚠️ |

⚠️ **`R/T CheckDigit` is hard-coded to `9`** — the check digit must be computed per routing number
(NACHA mod-10 weighted algorithm). A fixed `9` is correct only by coincidence.
⚠️ **`Trace Number` is hard-coded to `113000600000001`** for *every* record. NACHA requires a unique,
monotonically increasing trace number per entry. Note `11300060` is a valid KeyBank ABA prefix, so the
intent was clearly `<ODFI routing prefix> + <7-digit sequence>` — the sequence was never implemented.

### 6.3 `Schemas:NACHA_SchemaDT` — active flat-file document type
`recordWithNoID[]` with the 11 fields above. Used as `ffValues` for `pub.flatFile:convertToString`.

### 6.4 Unreferenced schema assets (dead)
- `Schemas:ACH_Schema` — a second Flat File Schema (`RecordSize = 94`, node `BatchTest`,
  `Mandatory = false`). **Not referenced by any flow.**
- `Schemas:NACHA_SchemaDT1` / `NACHA_SchemaDT2` — richer document types with a proper
  `BatchRecord → BatchBody` hierarchy plus `@record-id`, `@segment-id`, `@area`, `@position`,
  `@record-count`, `unDefData`, `segmentCount`. `NACHA_SchemaDT2` includes `R/T CheckDigit`;
  `NACHA_SchemaDT1` omits it. **Neither is referenced by the live `processACHBatch`** — only the abandoned
  `processACHBatch_venkat` targets the `BatchRecord/BatchBody` shape. These look like an unfinished attempt
  to build the *full* multi-record NACHA structure.

---

## 7. Dead / Disabled / Non-Production Code

| # | Item | Location | Evidence |
|---|---|---|---|
| D-1 | Pipeline save/restore debug harness | `processFundingRequest`, `BRANCH /debug` | `pub.flow:savePipelineToFile` / `restorePipelineFromFile`, file `FundingEngineRequest` |
| D-2 | `pub.client:ftp` step | `processACHBatch` | `DISABLED="true"`; target `localhost:8888`, user `Administrator`, blank password |
| D-3 | `updateBatchIDs` step | `processACHBatch` | `DISABLED="true"` — staging rows are never marked as batched |
| D-4 | Entire `processACHBatch_venkat` service | `MainFlows` | §7.3 |
| D-5 | `Schemas:ACH_Schema` | `Schemas` | Not referenced by any flow |
| D-6 | `Schemas:NACHA_SchemaDT1`, `NACHA_SchemaDT2` | `Schemas` | Not referenced by any live flow |
| D-7 | Empty folders `DocumentTypes`, `webConnectors`, `ProcessFlows` | `ns/` | Only `node.idf` markers |
| D-8 | Package shipped **disabled** | `manifest.v3` | `<value name="enabled">no</value>` |

### 7.3 `processACHBatch_venkat` — confirmed dead code
A developer's working copy. Its entire `LOOP` over `selectACHBatchOutput/results` — including all five field
mappings and all six constant setters — is marked `DISABLED="true"`, so it calls
`pub.flatFile:convertToString` on an **empty document**. It also mails
`venkat.mylavarapu@key.com, steven.a.miller@key.com`, calls `selectACHBatch` with no `maxDateTime`,
has no try/catch, and no error logging. **Do not migrate.**

---

## 8. Defects & Ambiguities Found in the Source

These are properties of the 2008 webMethods code, not migration decisions. Each needs a call before the
Workato build.

| ID | Severity | Finding |
|---|---|---|
| **G-1** | **HIGH** | **`invokeAddNewPayee` has an empty input MAP.** It depends entirely on webMethods' implicit pipeline name-matching. Workato has no ambient pipeline — every input must be named explicitly. The *likely* intent is to pass the same `PayeeInformation`/`PayeeSearch` document built for `invokeGetUniquePayee` (it is still in scope at that point), but the true signature of `invokeAddNewPayee` lives in the `GLDExpressGateway` package, which is **not in this export**. Needs SME confirmation. |
| **G-2** | **HIGH** | **Payment responses are overwritten, not accumulated.** `paymentResponse` is declared `record[]` but every write targets dim `;2;0` with no `appendToDocumentList`, while `Errors/Error` is written at `;4;1` *with* an explicit append. The SOAP reply therefore returns only the **last** payment's status. Almost certainly a bug. Decision required: replicate faithfully, or fix to one response per payment (recommended). |
| **G-3** | **HIGH** | **`Wire` payments silently succeed with no money movement.** The `$default` branch performs no external call and returns `status = "Default"` — not an error. Anything that is not exactly `Check` or `ACH` falls here. |
| **G-4** | **MEDIUM** | **`processACHBatch` never commits.** `updateBatchIDs` is disabled, so staging rows are never marked processed and every run re-sends the same payments. Combined with the disabled FTP, the batch has no delivery path. |
| **G-5** | **MEDIUM** | **`errorDoc/service_name` is hard-coded to `GLDExpressGateway.MainFlows.EFW:processLXIRequest`** in all three catch blocks — a copy-paste leftover from a different integration. Central error monitoring attributes every GLDFundingEngine failure to the wrong service. |
| **G-6** | **LOW** | **`errorDoc/system_message` is mapped twice** — first from `lastError/error`, then immediately overwritten by `lastError/errorDump`. Only `errorDump` survives. Harmless but confusing. |
| **G-7** | **MEDIUM** | **NACHA `R/T CheckDigit` hard-coded to `9`** instead of computed per routing number. |
| **G-8** | **HIGH** | **NACHA `Trace Number` hard-coded to `113000600000001`** for every entry. NACHA requires a unique, sequential trace number per record. |
| **G-9** | **MEDIUM** | **No scheduler definition in the export.** `processACHBatch` has an empty signature and must be run by a webMethods Scheduled Task, but no task definition is included. Frequency and run time are unknown. |
| **G-10** | **LOW** | The `debug` input on `processFundingRequest` allows a caller to trigger `restorePipelineFromFile`, replacing the live pipeline with a file from disk. Should not be carried forward. |
| **G-11** | **MEDIUM** | **Blank FTP password** stored in the flow (`processACHBatch`, disabled step). Confirms developer scaffolding; also a credential-hygiene note. |

---

## 9. What Actually Needs to Migrate

| Migrate | Rationale |
|---|---|
| ✅ `fundingEngineWrapper` + `processFundingRequest` | **The real integration.** Merge into ONE Workato recipe — the wrapper's SOAP marshalling has no Workato analogue, but its logging steps do. |
| ✅ `fundingEngineWrapperInput` / `Output` doc types | The API contract; becomes the recipe trigger schema + reply schema. |
| ⚠️ `processACHBatch` | Migrate the *shape* only, and only after G-4/G-7/G-8 are resolved. NACHA generation is a substantial custom build, not a mapping exercise. Recommend a **separate scheduled recipe**, phase 2. |
| ❌ `processACHBatch_venkat` | Dead developer copy (D-4). |
| ❌ `registerFlowServiceForSOAP` / `unregisterFlowServiceForSOAP` | webMethods SOAP-processor plumbing. Workato's API Platform replaces this entirely — there is nothing to migrate, only an endpoint to publish. |
| ❌ `/debug` save/restore harness | Developer tooling (D-1, G-10). |
| ❌ `ACH_Schema`, `NACHA_SchemaDT1`, `NACHA_SchemaDT2` | Unreferenced (D-5, D-6). |
| ❌ `pub/index.html`, `node.idf` folder markers | No logic. |

---

*Companion document: `WebMethods/MD/PackageAnalysis.md` — the Workato-oriented build blueprint.*
