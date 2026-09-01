# webMethods Package Analysis — `GLDFundingEngine20080714`

**Analysis codename: AVOCADO**
_(Per the migration request, this analysis run is tagged **AVOCADO**. Use this tag when referring back to this specific analysis pass.)_

| Attribute | Value |
|---|---|
| Package name (release) | `GLDFundingEngine20080714` |
| Target package name | `GLDFundingEngine` |
| Package version | 1.0 |
| Source / target IS version | webMethods Integration Server **6.5** |
| JVM version | 1.4.2 |
| Publisher | `cwb02dwmis02.keybank.com` |
| Published (release time) | 2008-07-14 12:56:18 EDT |
| Release type | full |
| Package `enabled` | **no** (package shipped disabled) |
| Declared dependency | `WmFlatFile` 6.5 |
| Startup service | `GLDFundingEngine.Wrappers.Registration:registerFlowServiceForSOAP` |
| Shutdown service | `GLDFundingEngine.Wrappers.Registration:unregisterFlowServiceForSOAP` |
| List ACL | Default |
| Source folder analysed | `WebMethods/GLDFundingEngine20080714/` (pre-existing folder in the repo, reused as-is) |

---

## 1. Package Inventory

38 files. Namespace root is `GLDFundingEngine`.

### 1.1 Namespace folders (`node.idf`)

| Folder | Contents |
|---|---|
| `GLDFundingEngine` | root interface node |
| `GLDFundingEngine.MainFlows` | `processFundingRequest`, `processACHBatch`, `processACHBatch_venkat` |
| `GLDFundingEngine.Wrappers` | `fundingEngineWrapper`, `fundingEngineWrapperInput`, `fundingEngineWrapperOutput` |
| `GLDFundingEngine.Wrappers.Registration` | `registerFlowServiceForSOAP`, `unregisterFlowServiceForSOAP` |
| `GLDFundingEngine.Schemas` | `ACH_Schema`, `NACHA`, `NACHA_Schema`, `NACHA_SchemaDT`, `NACHA_SchemaDT1`, `NACHA_SchemaDT2` |
| `GLDFundingEngine.DocumentTypes` | **empty** (folder node only — see §9 note on `fundingResponse`) |
| `GLDFundingEngine.ProcessFlows` | **empty** (folder node only) |
| `GLDFundingEngine.webConnectors` | **empty** (folder node only) |

### 1.2 Services (flow services)

| # | Service | Type | Role |
|---|---|---|---|
| 1 | `GLDFundingEngine.Wrappers:fundingEngineWrapper` | flow | SOAP entry point — unwraps SOAP, logs, delegates, re-wraps |
| 2 | `GLDFundingEngine.MainFlows:processFundingRequest` | flow | **Core business logic** — per-payment routing (Check / ACH / default) |
| 3 | `GLDFundingEngine.MainFlows:processACHBatch` | flow | Nightly ACH batch — builds NACHA flat file, FTPs it, emails it |
| 4 | `GLDFundingEngine.MainFlows:processACHBatch_venkat` | flow | Developer variant of #3 (not wired to anything) |
| 5 | `...Wrappers.Registration:registerFlowServiceForSOAP` | flow | Startup: registers SOAP directive |
| 6 | `...Wrappers.Registration:unregisterFlowServiceForSOAP` | flow | Shutdown: unregisters SOAP directive |

### 1.3 Document types & schemas

| Node | Type | Purpose |
|---|---|---|
| `Wrappers:fundingEngineWrapperInput` | record (IS doc type) | Inbound funding request contract |
| `Wrappers:fundingEngineWrapperOutput` | record (IS doc type) | Outbound funding response contract |
| `Schemas:NACHA_Schema` | Flat File Schema | NACHA fixed-width record layout used by `pub.flatFile:convertToString` |
| `Schemas:ACH_Schema` | Flat File Schema | Secondary/unused flat file schema |
| `Schemas:NACHA` | Document Part Holder | Flat-file doc part holder |
| `Schemas:NACHA_SchemaDT` | record | NACHA document type — `recordWithNoID` with 11 fields |
| `Schemas:NACHA_SchemaDT1` / `DT2` | record | Alternate NACHA doc-type revisions (`BatchBody` / `BatchRecord` variants) |

### 1.4 Other files

| File | Notes |
|---|---|
| `manifest.v3`, `manifest.rel`, `manifest.bak` | Package descriptors |
| `pub/index.html` | Static package home page (“Welcome To The Home Page For The GLDFundingEngine Package.”) |
| `*/flow.xml.bak` | Prior revisions of each flow — see §9 |

---

## 2. Service #1 — `Wrappers:fundingEngineWrapper` (SOAP entry point)

**Registered as a SOAP processor** at startup with directive `GLDFundingEngine`, descriptive name *“SOAP processor for GLD funding requests”*, bound to service `GLDFundingEngine.Wrappers:fundingEngineWrapper`.

Effective endpoint (webMethods SOAP-RPC/MSG processor convention):
`http://<is-host>:<port>/soap/GLDFundingEngine`

XML namespace for the payload: `https://webmethods.keybank.com/GLDFundingEngine/Wrappers` (prefix `ns1`).

### 2.1 Step sequence

| # | Step | Service | Detail |
|---|---|---|---|
| 1 | INVOKE | `pub.soap.utils:getBody` | `soapRequestData` → `soapData`; returns `body` (XML node) |
| 2 | INVOKE | `pub.xml:xmlNodeToDocument` | `node`=`body`; `documentTypeName` = `GLDFundingEngine.Wrappers:fundingEngineWrapperInput`; `makeArrays`=`false`; `nsDecls` = `https://webmethods.keybank.com/GLDFundingEngine/Wrappers`. Result → `fundingEngineWrapperInput` |
| 3 | INVOKE | `GLDMessageLog:LogXMLRequest` | Audit-log the inbound request. `RequestDoc`=input doc, `RequestIdentifier1`=**`FE`**, `AppID`=**`3`**. Captures `MessageLogID` → `MessageLogID_FundingEngine` |
| 4 | INVOKE | `GLDFundingEngine.MainFlows:processFundingRequest` | Core processing. Returns `fundingEngineWrapperOutput` |
| 5 | INVOKE | `GLDMessageLog:LogXMLResponse` | Audit-log the response. `MessageLogID`=saved id, `ResponseDoc`=output doc, `ResponseIdentifier4`=**`FE`** |
| 6 | INVOKE | `pub.xml:documentToXMLString` | `document`=output doc; `documentTypeName`=`...:fundingEngineWrapperOutput`; `encode`=`true`; `nsDecls` incl. prefix `ns1` |
| 7 | INVOKE | `pub.xml:xmlStringToXMLNode` | `isXML`=`true` → `node` |
| 8 | INVOKE | `pub.soap.utils:createSoapData` | New empty SOAP envelope |
| 9 | INVOKE | `pub.soap.utils:addBodyEntry` | `bodyEntry`=`node`, `soapData`→`soapResponseData` |

**Observation (dead code):** step 6's OUTPUT map drops `/responseData;4;0;ESHEquifax.Wrappers:equifaxWrapperOutput` — a copy/paste leftover from the unrelated **ESHEquifax** package. Harmless but confirms this wrapper was cloned from that package.

---

## 3. Service #2 — `MainFlows:processFundingRequest` (core logic)

### 3.1 Signature

**Input:**
- `fundingEngineWrapperInput` — recref → `GLDFundingEngine.Wrappers:fundingEngineWrapperInput`
- `debug` — string, **optional**

**Output:**
- `fundingEngineWrapperOutput` — recref → `GLDFundingEngine.Wrappers:fundingEngineWrapperOutput`

**Settings:** stateless=no, caching=no, audit_level=off, retry_max=0, retry_interval=0, input validation = `default`, output validation = `none`, audit on error = true.

### 3.2 Developer comment embedded in `node.ndf` (verbatim, authoritative)

> SNo. Date  Author  Description
> 1. 06/11/08 **millese** — This service is invoked from fundingEngineWrapper. This service takes a list of payments and associated application data and sends each payment request to the appropriate system. Currently it only handles Checks and ACH payments. Check requests are sent to check writer calling the appropriate functions (search for payee, create payee, create check request) as needed. ACH has an associated DB that the request information is stored in until day processing occurs.
>
> NOTE: for sample data, data dictionary, etc please look in the `eftest$\Blue Ocean Pipeline BPU\Design And Documentation\Funding Research` folder.

### 3.3 Flow structure

```
FLOW
├── BRANCH on /debug                                   ← DEBUG HARNESS (dev only)
│   ├── label "$null"  → INVOKE pub.flow:savePipelineToFile   (fileName="FundingEngineRequest")
│   └── label "true"   → INVOKE pub.flow:restorePipelineFromFile (fileName="FundingEngineRequest")
│
└── SEQUENCE (EXIT-ON=SUCCESS)                          ← TRY/CATCH wrapper
    ├── SEQUENCE (EXIT-ON=FAILURE)   // "TRY Block"
    │   ├── MAP (STANDALONE)
    │   │   ├── SET fundingEngineWrapperOutput = (initialise empty response doc)
    │   │   └── SET REQUESTOR = "1"
    │   │
    │   └── LOOP  IN-ARRAY  = .../fundingRequest/payments/payment
    │             OUT-ARRAY = .../fundingEngineWrapperResponse/paymentResponses/paymentResponse
    │       └── SEQUENCE (EXIT-ON=SUCCESS)              ← per-payment TRY/CATCH
    │           ├── SEQUENCE (EXIT-ON=FAILURE) // "On Error Try other payments"
    │           │   └── BRANCH on .../payment/type
    │           │       ├── "Check"    → SEQUENCE (EXIT-ON=FAILURE)
    │           │       │   ├── INVOKE CheckWriter:invokeGetUniquePayee
    │           │       │   ├── BRANCH on /payeeKey
    │           │       │   │   └── "$null" → INVOKE CheckWriter:invokeAddNewPayee
    │           │       │   ├── INVOKE CheckWriter:invokeCreateCheckRequest
    │           │       │   └── MAP → paymentResponse.id, status = "Paid"
    │           │       ├── "ACH"      → SEQUENCE (EXIT-ON=FAILURE)
    │           │       │   ├── INVOKE GLD_ACHAdaptersServices:insertPayment
    │           │       │   └── MAP → paymentResponse.id, status = "Paid"
    │           │       └── "$default" → SEQUENCE (EXIT-ON=FAILURE)
    │           │           └── MAP → paymentResponse.id, status = "Default"   (no external call)
    │           │
    │           └── SEQUENCE (EXIT-ON=DONE) // "Catch Block for individual payments"
    │               ├── INVOKE pub.flow:getLastError
    │               ├── MAP "Modify error message"
    │               ├── SEQUENCE (EXIT-ON=DONE) // "Do not fail the trxn if the logging to DB fails"
    │               │   └── INVOKE GLDMessageLog:LogXMLRequest  (AppID=3, RequestIdentifier1="ERROR - processing payment")
    │               ├── MAP → paymentResponse.errorDescription, id, status = "Error"
    │               ├── MAP + MAPINVOKE pub.list:appendToDocumentList → append Error to Errors[]
    │               └── INVOKE WSRProcessStatistics.MainFlows:publishErrorDoc
    │
    └── SEQUENCE (EXIT-ON=DONE)   // "CATCH Block" (whole-request)
        ├── INVOKE pub.flow:getLastError
        ├── MAP "Modify error message"
        ├── SEQUENCE (EXIT-ON=DONE) // "Do not fail the trxn if the logging to DB fails"
        │   └── INVOKE GLDMessageLog:LogXMLRequest (AppID=3, RequestIdentifier1="ERROR - processFundingRequest")
        ├── MAP → Errors[].errorDescription = lastError.error, Errors[].errorCode = MessageLogID
        └── INVOKE WSRProcessStatistics.MainFlows:publishErrorDoc
```

**webMethods TRY/CATCH idiom:** `SEQUENCE EXIT-ON=SUCCESS` wrapping `SEQUENCE EXIT-ON=FAILURE` (try) + `SEQUENCE EXIT-ON=DONE` (catch). This appears **twice** — once at request level, once per payment inside the LOOP.

### 3.4 Branch semantics

All three `BRANCH` shapes are **value switches** (no `evaluateLabels`), i.e. exact string equality on the switch path.

| BRANCH | Switch path | Labels |
|---|---|---|
| Debug harness | `/debug` | `$null` → savePipelineToFile · `true` → restorePipelineFromFile |
| Payment router | `.../payments/payment/type` | `Check` · `ACH` · `$default` |
| Payee existence | `/payeeKey` | `$null` → invokeAddNewPayee (no other labels — non-null falls through) |

**Important:** the payee branch has a single `$null` label. If `payeeKey` came back **null** from the search, a new payee is created. If it is non-null, the branch is a no-op and the existing key is reused.

### 3.5 Static values set (`MAPSET`)

| Field | Value | Where |
|---|---|---|
| `REQUESTOR` | `1` | Try block init — flows into `insertPaymentInput/REQUESTOR_ID` |
| `PayeeInformation/Country` | `USA` | invokeGetUniquePayee input |
| `paymentResponse/status` | `Paid` | Check success path |
| `paymentResponse/status` | `Paid` | ACH success path |
| `paymentResponse/status` | `Default` | `$default` path |
| `paymentResponse/status` | `Error` | per-payment catch |
| `AppID` | `3` | both GLDMessageLog error calls |
| `RequestIdentifier1` | `ERROR - processing payment` | per-payment catch |
| `RequestIdentifier1` | `ERROR - processFundingRequest` | outer catch |
| `errorDoc/severity_level` | `CRITICAL` | both catches |
| `errorDoc/appl_id` | `GLD` | both catches |
| `errorDoc/entry_type` | `E` | both catches |
| `errorDoc/sender_id` | `EFW` | both catches |
| `errorDoc/receiver_id` | `WMB` | both catches |
| `errorDoc/transaction_type` | `XML` | both catches |
| `errorDoc/service_name` | `GLDExpressGateway.MainFlows.EFW:processLXIRequest` | both catches — **copy/paste leftover**, wrong service name |
| `fileName` | `FundingEngineRequest` | debug pipeline save/restore |

---

## 4. Field-level Data Mappings

### 4.1 `invokeGetUniquePayee` — payee search (Check path)

Source root: `fundingEngineWrapperInput/ns1:fundingEngineWrapper/fundingRequest/payments/payment/payee/`
Target root: `PayeeInformation` (`GLDExpressGateway.DocumentTypes.CheckWriter:PayeeSearch`)

| Source (payee.*) | Target (PayeeSearch.*) |
|---|---|
| `name` | `PayeeName` |
| `address1` | `AddressLine1` |
| `address2` | `AddressLine2` |
| `city` | `City` |
| `state_province` | `State` |
| `zip` | `PostalCode` |
| `phone` | `PhoneNumber` |
| `fax` | `FaxNumber` |
| `contactName` | `ContactName` |
| `contactPhone` | `ContactPhoneNumber` |
| _(static)_ `"USA"` | `Country` |

**Output:** `payeeKey`.

### 4.2 `invokeAddNewPayee` — create payee (Check path, conditional)

Input/output maps are **empty** — the flow relies on webMethods *implicit pipeline matching*: `PayeeInformation` is already in the pipeline from step 4.1 and is picked up by name, and `payeeKey` is returned into the pipeline by name.

### 4.3 `invokeCreateCheckRequest` — create check request (Check path)

Target root: `CheckRequest` (`GLDExpressGateway.DocumentTypes.CheckWriter:CheckRequest`)

| Source | Target (CheckRequest.*) |
|---|---|
| `/payeeKey` (pipeline) | `PayeeKey` |
| `payment/invoiceReference` | `Notes` |
| `payment/comment` | `Comments` |
| `payment/amount` | `CheckAmount` |
| `payment/checkMemo` | `Memo` |
| `payment/payee/name` | `PayeeName` |
| `applicationInfo/id` | `LeaseNumber` |

### 4.4 `GLD_ACHAdaptersServices:insertPayment` — ACH path

Target root: `insertPaymentInput`

| Source | Target |
|---|---|
| `/REQUESTOR` (static `"1"`) | `REQUESTOR_ID` |
| `applicationInfo/id` | `APP_ID` |
| `applicationInfo/customerName` | `CUSTOMER_NAME` |
| `applicationInfo/customerID` | `CUSTOMER_ID` |
| `applicationInfo/sourceName` | `SOURCE` |
| `payment/amount` | `AMOUNT` |
| `payment/invoiceReference` | `REFERENCE` |
| `payment/payee/id` | `PAYEE_ID` |
| `payment/payee/name` | `PAYEE_NAME` |
| `payment/payee/accountNumber` | `ACCOUNT_NUMBER` |
| `payment/payee/routingNumber` | `ROUTING_NUMBER` |

**11 parameters.** Note `applicationInfo/sourceSubCategory` and `salesRepName` are **never used** anywhere in the flow.

### 4.5 Response mapping (all paths)

| Source | Target |
|---|---|
| `payment/id` | `paymentResponse/id` |
| _(static)_ | `paymentResponse/status` — `Paid` / `Default` / `Error` |
| `lastError.error` | `paymentResponse/errorDescription` (error path only) |

### 4.6 Error document mapping (both catch blocks)

| Source | Target |
|---|---|
| `lastError/callStack[0]/service` | `errorDoc/service_name` (then **overwritten** by static MAPSET) |
| `lastError/error` | `errorDoc/system_message` |
| `lastError/errorDump` | `errorDoc/system_message` (**second write — overwrites the previous line**) |
| `lastError/error` | `GLDMessageLog:LogXMLRequest → Request` |
| `pipeline/REQUESTIDENTIFIER3` | `LogXMLRequest → RequestIdentifier3` |

---

## 5. Input / Output Document Contracts

### 5.1 `fundingEngineWrapperInput`

```
ns1:fundingEngineWrapper (record)
└── fundingRequest (record)
    ├── applicationInfo (record)
    │   ├── id                (string)
    │   ├── customerName      (string)
    │   ├── customerID        (string)
    │   ├── sourceName        (string)
    │   ├── sourceSubCategory (string)   ← unused in flow
    │   └── salesRepName      (string)   ← unused in flow
    └── payments (record)
        └── payment (record[])           ← ARRAY, loop source
            ├── id               (string)
            ├── type             (string)   ← branch key: "Check" | "ACH" | other
            ├── payee (record)
            │   ├── id             (string)
            │   ├── type           (string)   ← unused in flow
            │   ├── name           (string)
            │   ├── address1       (string)
            │   ├── address2       (string)
            │   ├── city           (string)
            │   ├── state_province (string)
            │   ├── zip            (string)
            │   ├── phone          (string)
            │   ├── fax            (string)
            │   ├── contactName    (string)
            │   ├── contactPhone   (string)
            │   ├── routingNumber  (string)
            │   └── accountNumber  (string)
            ├── amount           (string)
            ├── invoiceReference (string)
            ├── comment          (string)
            ├── checkMemo        (string)
            ├── status           (string)   ← unused inbound
            ├── glCode           (string)   ← unused in flow
            ├── glAmount         (string)   ← unused in flow
            └── glDescription    (string)   ← unused in flow
```

**6 applicationInfo fields + 14 payment fields (incl. 14-field nested payee).**

### 5.2 `fundingEngineWrapperOutput`

```
ns1:fundingEngineWrapperResponse (record)
├── paymentResponses (record)
│   └── paymentResponse (record[])
│       ├── id               (string)
│       ├── status           (string)   "Paid" | "Default" | "Error"
│       └── errorDescription (string)
└── Errors (record)
    └── Error (recref[] → GLDExpressWebServices.DocumentTypes:Error)
```

---

## 6. Service #3 — `MainFlows:processACHBatch` (nightly NACHA batch)

No declared signature (`svc_sigtype: java 3.5`, no `svc_sig`) — takes no input, produces no output. Not wired to any trigger or scheduler inside this package; would be driven by an IS scheduled task defined **outside** the package.

### 6.1 Flow structure

```
FLOW
└── SEQUENCE (EXIT-ON=SUCCESS)                        ← TRY/CATCH
    ├── SEQUENCE (EXIT-ON=FAILURE) // "TRY Block"
    │   ├── INVOKE GLD_ACHAdaptersServices:getSystemDateTime  → maxDateTime (SYS_DATE)
    │   ├── INVOKE GLD_ACHAdaptersServices:selectACHBatch     (in: maxDateTime) → results[]
    │   ├── INVOKE GLD_ACHAdaptersServices:getNextBatchID     → batchID (nextBatchID)
    │   ├── LOOP IN-ARRAY=/selectACHBatchOutput/results
    │   │        OUT-ARRAY=/NACHA_SchemaDT/BatchRecord
    │   │   └── MAP → NACHA detail record (see 6.2)
    │   ├── INVOKE pub.flatFile:convertToString
    │   │        ffSchema="GLDFundingEngine.Schemas:NACHA_Schema", spacePad="left", delimiters.record="\r\n"
    │   │        → string
    │   ├── INVOKE GLD_ACHAdaptersServices:updateBatchIDs (BATCH_ID=batchID, PROCESS_DATE=maxDateTime)
    │   └── SEQUENCE (EXIT-ON=FAILURE) // "Transfer ACH File"
    │       ├── INVOKE pub.client:ftp  (see 6.3)
    │       └── INVOKE WSRCommon.Utilities.FlowServices:sendEmail (see 6.4)
    │
    └── SEQUENCE (EXIT-ON=DONE) // "CATCH Block"
        ├── INVOKE pub.flow:getLastError
        ├── MAP "Modify error message"
        ├── SEQUENCE (EXIT-ON=DONE) → INVOKE GLDMessageLog:LogXMLRequest
        │        (AppID=3, RequestIdentifier1="ERROR - processACHBatch")
        └── INVOKE WSRProcessStatistics.MainFlows:publishErrorDoc
```

### 6.2 NACHA detail-record mapping (per DB row)

| Source (`selectACHBatchOutput/results/*`) | Target (`NACHA_SchemaDT/recordWithNoID/*`) |
|---|---|
| `ROUTING_NUMBER` | `Routing/Transit Number` |
| `ACCOUNT_NUMBER` | `Individual Account Number` |
| `AMOUNT` | `Amount` |
| `REFERENCE` | `Individual ID Number` |
| `PAYEE_NAME` | `Individual Name` |

Static NACHA fields:

| Field | Value | NACHA meaning |
|---|---|---|
| `Record Type Code` | `6` | Entry Detail Record |
| `Transaction Code` | `22` | Checking account credit |
| `R/T CheckDigit` | `9` | **hardcoded** — should be computed from the routing number |
| `Addenda Indicator` | `0` | No addenda |
| `Discretionary Data` | _(empty)_ | |
| `Trace Number` | `113000600000001` | **hardcoded constant** — should increment per record |

### 6.3 FTP transfer (`pub.client:ftp`)

| Parameter | Value |
|---|---|
| `serverhost` | `localhost` |
| `serverport` | `8888` |
| `username` | `Administrator` |
| `password` | _(base64-wrapped `Values` blob, IS-encrypted)_ |
| `command` | `put` |
| `dirpath` | `/admin/ftpfiles` |
| `remotefile` | `PO.txt` |
| `content` | `string` (the NACHA flat file) |

**These are unmistakably developer/test values** — `localhost:8888` with `Administrator`, and a remote filename of `PO.txt` for an ACH file. The real bank FTP target is not in this package.

### 6.4 Email notification (`WSRCommon.Utilities.FlowServices:sendEmail`)

| Field | Value |
|---|---|
| `to` | `steven.a.miller@key.com` |
| `from` | `ACHProcess@key.com` |
| `subject` | `ACH File` |
| `attachmentFlag` | `true` |
| `attachementFileName` | `ach.txt` _(sic — misspelled in source)_ |
| `contents` | the NACHA flat-file string |

---

## 7. Service #4 — `MainFlows:processACHBatch_venkat` (developer variant)

A near-duplicate of `processACHBatch` attributed to a second developer. Differences observed:

- Uses `NACHA_Schema` / `BatchRecord` / `@composite` doc-type shape rather than `NACHA_SchemaDT/recordWithNoID`
- Sets `@composite = 1`; omits the `R/T CheckDigit` static
- Email `to` = `venkat.mylavarapu@key.com, steven.a.miller@key.com`
- Same FTP settings (`localhost:8888`, `Administrator`, `/admin/ftpfiles`, `PO.txt`)

**Not referenced by any other service.** Treat as dead developer scratch code — **out of scope for migration**.

---

## 8. External Dependencies (NOT contained in this package)

Every one of these is an unresolved reference — the package cannot run standalone.

| Dependency | Kind | Used by |
|---|---|---|
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeGetUniquePayee` | flow service | processFundingRequest (Check) |
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeAddNewPayee` | flow service | processFundingRequest (Check) |
| `GLDExpressGateway.ProcessFlows.CheckWriter:invokeCreateCheckRequest` | flow service | processFundingRequest (Check) |
| `GLDExpressGateway.DocumentTypes.CheckWriter:PayeeSearch` | doc type | Check path input |
| `GLDExpressGateway.DocumentTypes.CheckWriter:CheckRequest` | doc type | Check path input |
| `GLD_ACHAdaptersServices:insertPayment` | **JDBC adapter service** | processFundingRequest (ACH) |
| `GLD_ACHAdaptersServices:getSystemDateTime` | JDBC adapter service | processACHBatch |
| `GLD_ACHAdaptersServices:selectACHBatch` | JDBC adapter service | processACHBatch |
| `GLD_ACHAdaptersServices:getNextBatchID` | JDBC adapter service | processACHBatch |
| `GLD_ACHAdaptersServices:updateBatchIDs` | JDBC adapter service | processACHBatch |
| `GLDMessageLog:LogXMLRequest` | flow service (DB-backed audit log) | wrapper, both catches, ACH batch |
| `GLDMessageLog:LogXMLResponse` | flow service | wrapper |
| `WSRProcessStatistics.MainFlows:publishErrorDoc` | flow service (publishes to broker) | all catch blocks |
| `WSRProcessStatistics.DocumentTypes:errorDoc` | doc type | all catch blocks |
| `WSRCommon.Utilities.FlowServices:sendEmail` | flow service | processACHBatch |
| `GLDExpressWebServices.DocumentTypes:Error` | doc type | response `Errors[]` |
| `pub.soap.utils:*`, `pub.xml:*`, `pub.flow:*`, `pub.list:*`, `pub.client:ftp`, `pub.flatFile:*` | WmPublic / WmFlatFile built-ins | all |

**Architectural read:** `GLDFundingEngine` is a thin orchestration layer. All actual system access lives in sibling packages — `GLDExpressGateway` (CheckWriter SOAP/HTTP gateway), `GLD_ACHAdaptersServices` (Oracle JDBC adapter), `GLDMessageLog` (audit DB), `WSRProcessStatistics` (error broker).

---

## 9. `.bak` revision comparison

| Flow | `.bak` differs? | Nature of the difference |
|---|---|---|
| `processFundingRequest` | Yes | The `.bak` wrote responses into an intermediate doc `GLDFundingEngine.DocumentTypes:fundingResponse`; the live flow writes straight into `fundingEngineWrapperOutput`. Also one MAPSET reordering. **Business logic identical.** |
| `fundingEngineWrapper` | Yes | The `.bak` copied `fundingResponse.paymentResponse[]` and `fundingResponse.Errors` into the wrapper output; the live flow receives `fundingEngineWrapperOutput` directly. **Same behaviour.** |
| `registerFlowServiceForSOAP` / `unregister` | Yes | Cosmetic only |
| `processACHBatch`, `processACHBatch_venkat` | No | Byte-identical |

This explains why `GLDFundingEngine.DocumentTypes` is an empty folder: the `fundingResponse` doc type was removed during that refactor. **The live `flow.xml` files are authoritative** — no contradiction requiring a decision.

---

## 10. Observations, Defects & Risks in the Source

| # | Severity | Finding |
|---|---|---|
| 1 | HIGH | `processACHBatch` FTP target is `localhost:8888` / `Administrator` / `PO.txt` — dev placeholders. Real destination unknown. |
| 2 | HIGH | NACHA `Trace Number` is the hardcoded constant `113000600000001` for **every** record. NACHA requires a unique, sequential trace number per entry. |
| 3 | HIGH | NACHA `R/T CheckDigit` hardcoded to `9`; it must be derived from the routing number. |
| 4 | HIGH | The generated NACHA file contains **only Entry Detail (type 6) records** — no File Header (1), Batch Header (5), Batch Control (8) or File Control (9). This is not a valid NACHA file as-is. |
| 5 | MEDIUM | `errorDoc/service_name` is hardcoded to `GLDExpressGateway.MainFlows.EFW:processLXIRequest` in **both** catch blocks of `processFundingRequest` and in `processACHBatch` — wrong service name, copy/paste leftover. It also overwrites the correctly-mapped `lastError/callStack[0]/service`. |
| 6 | MEDIUM | `errorDoc/system_message` is written twice (from `lastError/error`, then `lastError/errorDump`) — the second wins; the first mapping is dead. |
| 7 | MEDIUM | Package ships with `enabled = no`. |
| 8 | MEDIUM | The `$default` payment-type path silently marks the payment `Default` and performs **no** external call. Wire and other payment types are effectively dropped without error. |
| 9 | LOW | Debug harness (`savePipelineToFile` / `restorePipelineFromFile`) is live in the main flow — in normal operation (`debug` unset → `$null`) it **writes the full pipeline to disk on every request**, including payee bank routing/account numbers. Data-at-rest concern. |
| 10 | LOW | `processACHBatch_venkat` is dead duplicate code. |
| 11 | LOW | Unused inbound fields: `sourceSubCategory`, `salesRepName`, `payee/type`, `payment/status`, `glCode`, `glAmount`, `glDescription`. |
| 12 | LOW | ESHEquifax leftover reference in the wrapper's output map. |
| 13 | LOW | Misspelled field `attachementFileName` (source-side, in the sendEmail doc). |

---

## 11. End-to-End Business Flow (plain English)

1. An external consumer (the GLD / Blue Ocean lease-origination front end) posts a **SOAP request** to the IS SOAP directive `GLDFundingEngine`, carrying one *funding request*: some `applicationInfo` (lease/app id, customer, source, sales rep) plus a **list of payments**.
2. `fundingEngineWrapper` extracts the SOAP body, converts it to the `fundingEngineWrapperInput` document, and **audit-logs the inbound XML** to the GLD message log (AppID `3`, identifier `FE`).
3. `processFundingRequest` initialises an empty response document and sets `REQUESTOR = "1"`, then **iterates over every payment**.
4. For each payment it switches on `payment/type`:
   - **`Check`** → search CheckWriter for a matching payee (name + full address + phone/fax + contact, Country forced to `USA`). If **no** payee key comes back, create the payee. Then create a check request (payee key, amount, invoice reference as Notes, comment as Comments, check memo as Memo, payee name, and the application id as `LeaseNumber`). Mark the payment **`Paid`**.
   - **`ACH`** → insert an 11-column row into the ACH staging database via the JDBC adapter (`insertPayment`). Nothing is sent to the bank yet — it waits for the nightly batch. Mark the payment **`Paid`**.
   - **anything else** (including Wire) → do nothing external; mark the payment **`Default`**.
5. If any single payment throws, the **per-payment catch** logs the error to the message log (`ERROR - processing payment`), publishes an error doc to WSRProcessStatistics, records `status = "Error"` plus the error text on that payment's response, appends to the response `Errors[]` list, **and the loop continues with the next payment** (comment in source: *"On Error Try other payments"*).
6. If the whole request throws, the **outer catch** logs `ERROR - processFundingRequest`, publishes the error doc, and puts the error into the response's `Errors[]` with the message-log id as `errorCode`.
7. `fundingEngineWrapper` audit-logs the response, serialises the response document back to XML, and returns it as a SOAP body.
8. **Separately and asynchronously**, `processACHBatch` runs (nightly, scheduled outside this package): it takes the DB system time as a cutoff, selects all pending ACH rows up to that time, gets the next batch id, maps each row into a NACHA type-6 entry detail record, converts the collection into a fixed-width flat file via the `NACHA_Schema` flat-file schema, marks the rows with the batch id and process date, then **FTPs the file** and **emails it as an attachment** to the ACH operations contact.

---

## 12. webMethods Construct Census (for mapping)

| Construct | Count | Where |
|---|---|---|
| `SEQUENCE` (try/catch pairs) | 5 pairs | 2 in processFundingRequest, 1 in processACHBatch, + inner "no-fail logging" sequences |
| `SEQUENCE` (plain grouping) | 4 | branch child sequences, "Transfer ACH File" |
| `BRANCH` (value switch) | 3 | debug, payment type, payeeKey |
| `LOOP` (over array) | 2 | payments[] , ACH results[] |
| `INVOKE` (external flow service) | 8 distinct | CheckWriter ×3, GLDMessageLog ×2, publishErrorDoc, sendEmail |
| `INVOKE` (JDBC adapter service) | 5 distinct | insertPayment, getSystemDateTime, selectACHBatch, getNextBatchID, updateBatchIDs |
| `INVOKE` (built-in) | 11 | SOAP ×3, XML ×3, flow ×3, flatFile ×1, ftp ×1 |
| `MAP` (STANDALONE) | 9 | response building, error doc shaping |
| `MAPINVOKE` | 1 | `pub.list:appendToDocumentList` |
| `MAPSET` (static value) | 28 | see §3.5, §6 |
| `MAPCOPY` (field link) | 60+ | see §4 |
| `MAPDELETE` (pipeline drop) | 50+ | pipeline hygiene — **no functional equivalent needed in Workato** |
| `EXIT` | 0 | none used |

---

_End of analysis **AVOCADO** — `GLDFundingEngine20080714`._
