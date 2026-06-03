# webMethods GLD Integration Suite — Full Analysis
## Migration Reference Document for Boomi

> **Scope**: All 15 webMethods packages extracted from the GLD project archive.
> **Purpose**: Complete reverse-engineering of connections, flow services, triggers, document types, schemas, and Java custom code for migration to Boomi.
> **Source server**: webMethods Integration Server 6.5 — KeyBank (`cwb02dwmis02.keybank.com` / `csc06dwmis01.keybank.com`)

---

## Table of Contents

1. [Package Inventory](#1-package-inventory)
2. [Database Connections (All)](#2-database-connections)
3. [Triggers (Event Entry Points)](#3-triggers)
4. [Package: GLDComplianceCheck](#4-gldcompliancecheck)
5. [Package: GLDExpressGateway](#5-gldexpressgateway)
6. [Package: GLDExpressWebServices](#6-gldexpresswebservices)
7. [Package: GLDFundingEngine](#7-gldfundingengine)
8. [Package: GLDMessageLog](#8-gldmessagelog)
9. [Package: GLDSoap](#9-gldsoap)
10. [Adapter/Environment Packages](#10-adapterenvironment-packages)
11. [Java Custom Services](#11-java-custom-services)
12. [Document Types and Schemas](#12-document-types-and-schemas)
13. [Boomi Migration Mapping Summary](#13-boomi-migration-mapping-summary)
14. [Open Items & Migration Checklist](#14-open-items--migration-checklist)

---

## 1. Package Inventory

| Package | Role | Flow Services | Connections | Triggers | Java Files |
|---|---|---|---|---|---|
| `GLDComplianceCheck` | **Core compliance engine** — receives check requests, calls CIU, returns results | 14 | 0 (uses AdapterEnv) | 1 | 1 |
| `GLDExpressGateway` | **Central orchestrator** — routes EFW/VMR/Customer/CheckWriter requests to XOS/XLink | 149 | 0 | 1 | 4 |
| `GLDExpressWebServices` | **SOAP web service wrappers** — exposes flows as external web services | 27 | 0 | 0 | 1 |
| `GLDFundingEngine` | **ACH/NACHA funding processor** — parses flat files, processes ACH batches | 6 | 0 | 0 | 0 |
| `GLDMessageLog` | **Audit/logging utility** — logs XML request/response pairs to DB | 3 | 0 | 0 | 0 |
| `GLDSoap` | **Generic SOAP invoker** — low-level HTTP/SOAP call utility | 3 | 0 | 0 | 1 |
| `GLDSoap20` | Clone of GLDSoap (updated version) | 1 | 0 | 0 | 1 |
| `GLDComplianceAdapterEnv` | Env: Oracle DB connection for compliance (ORASHR4T) | 0 | 1 | 0 | 0 |
| `GLDComplianceAdapterServices` | IS Record types for DB adapter service signatures | 0 | 0 | 0 | 0 |
| `GLDExpressAdapterEnv` | Env: 4 DB connections (EDW, ODS, FundingACH, LeasePak) | 0 | 4 | 0 | 0 |
| `GLDExpressAdapterServices` | IS Record types for Express adapter service signatures | 0 | 0 | 0 | 0 |
| `GLDMessageLogAdapterEnv` | Env: Oracle DB connection for message log (ORASHR4T) | 0 | 1 | 0 | 0 |
| `GLDMessageLogAdapterServices` | IS Record types for message log adapter signatures | 0 | 0 | 0 | 0 |
| `GLDExpressGateway_old` | **Archived prior version** of GLDExpressGateway — do not migrate | — | — | — | 1 |
| `GLDFundingEngine20080714` | **Archived snapshot** of GLDFundingEngine (2008-07-14) — do not migrate | — | — | — | 0 |

> **Active packages to migrate**: GLDComplianceCheck, GLDExpressGateway, GLDExpressWebServices, GLDFundingEngine, GLDMessageLog, GLDSoap + all Env/AdapterServices packages for connections.

---

## 2. Database Connections

All connections are **JDBC Adapter** (`JDBCAdapter`) using Oracle or Sybase databases. Passwords are webMethods-proprietary encrypted — all must be reset in Boomi.

### 2.1 GLDComplianceAdapterEnv:ExpressOS

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_ComplianceDB_Connection` |
| **Adapter** | JDBCAdapter → Oracle (`oracle.jdbc.pool.OracleDataSource`) |
| **Driver** | Oracle Thin JDBC |
| **Host** | `CSC06DSHORA1S` |
| **Port** | `1522` |
| **Database / SID** | `ORASHR4T` |
| **Username** | `GLD_SCHEMA` |
| **Password** | Encrypted — must be reset |
| **Transaction** | NO_TRANSACTION |
| **Pool Min/Max** | 1 / 10 |
| **Blocking Timeout** | 10,000 ms |
| **JDBC URL** | `jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHR4T` |
| **Used by** | `GLDComplianceAdapterServices` (logCheckRequest, logCheckReply, selectCustomerAndRequest, updateCIURefNbr, purgeData) |

### 2.2 GLDMessageLogAdapterEnv:MessageLog

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_MessageLogDB_Connection` |
| **Adapter** | JDBCAdapter → Oracle (`oracle.jdbc.pool.OracleDataSource`) |
| **Host** | `CSC06DSHORA1S` |
| **Port** | `1522` |
| **Database / SID** | `ORASHR4T` |
| **Username** | `GLD_SCHEMA` |
| **Password** | Encrypted — must be reset |
| **Transaction** | NO_TRANSACTION |
| **Pool Min/Max** | 1 / 10 |
| **Blocking Timeout** | 10,000 ms |
| **JDBC URL** | `jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHR4T` |
| **Note** | Same host/SID as ExpressOS — possibly same Oracle instance, different schema or identical schema |
| **Used by** | `GLDMessageLog` (LogRequestAndResponse, LogXMLRequest, LogXMLResponse) |

### 2.3 GLDExpressAdapterEnv.EDW:DataWareHouseEDW

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_EDW_Connection` |
| **Adapter** | JDBCAdapter → Oracle (`oracle.jdbc.pool.OracleDataSource`) |
| **Host** | `CSC06DORASA` |
| **Port** | `1521` (default) |
| **Database / SID** | `KEF1` |
| **Username** | `KEF_GLD_WEBMETHOD` |
| **Password** | Encrypted — must be reset |
| **Transaction** | NO_TRANSACTION |
| **JDBC URL** | `jdbc:oracle:thin:@CSC06DORASA:1521:KEF1` |
| **Used by** | `GLDExpressGateway` EDW-related adapter services |

### 2.4 GLDExpressAdapterEnv.ODS:DataWareHouseODS

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_ODS_Connection` |
| **Adapter** | JDBCAdapter → Oracle (`oracle.jdbc.pool.OracleDataSource`) |
| **Host** | `CSC06DORASA` |
| **Port** | `1521` (default) |
| **Database / SID** | `KEF1` |
| **Username** | `KEF_GLD_WEBMETHOD` |
| **Password** | Encrypted (different from EDW) — must be reset |
| **Note** | Same host/SID as EDW; different password suggests a distinct schema/role |
| **JDBC URL** | `jdbc:oracle:thin:@CSC06DORASA:1521:KEF1` |
| **Used by** | `GLDExpressGateway` ODS adapter services |

### 2.5 GLDExpressAdapterEnv.Funding:FundingEngineACH

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_FundingACH_Connection` |
| **Adapter** | JDBCAdapter → Oracle (`oracle.jdbc.pool.OracleDataSource`) |
| **Host** | `CSC06DORASA` |
| **Port** | `1521` (default) |
| **Database / SID** | `ORA01` |
| **Username** | `GLD_ACHD_SCHEMA` |
| **Password** | Encrypted — must be reset |
| **Blocking Timeout** | 10,000 ms |
| **JDBC URL** | `jdbc:oracle:thin:@CSC06DORASA:1521:ORA01` |
| **Used by** | `GLDFundingEngine` ACH processing flows |

### 2.6 GLDExpressAdapterEnv.LeasePak:LeasePakDatabase

| Property | Value |
|---|---|
| **Boomi Component Name** | `MIG_WM_LeasePak_Connection` |
| **Adapter** | JDBCAdapter → **Sybase** (`com.sybase.jdbc2.jdbc.SybDataSource`) |
| **Driver** | Sybase jConnect 2 |
| **Host** | `csc06dsyb01` |
| **Port** | `2048` (default Sybase) |
| **Database** | `ksc_cartman` |
| **Username** | `webmthd` |
| **Password** | Encrypted — must be reset |
| **Other Props** | `sybase.jdbc.J2EE13Compliant=true` |
| **JDBC URL** | `jdbc:sybase:Tds:csc06dsyb01:2048/ksc_cartman` |
| **Note** | **Different DB vendor** — Sybase, not Oracle. Boomi's DatabaseV2 connector supports Sybase via `com.sybase.jdbc4.jdbc.SybDriver`. JAR `jconn4.jar` needed on Atom. |
| **Used by** | `GLDExpressGateway.MainFlows.Customer` (LeasePak → ExpressLink customer sync) |

---

## 3. Triggers

webMethods triggers are publish-subscribe event listeners — equivalent to Boomi's **JMS/message queue listener** or a scheduled process with a filter.

### 3.1 GLDComplianceCheck.MainFlows:triggerForCheckRequest

| Property | Value | Boomi Equivalent |
|---|---|---|
| **Document Type** | `GLDComplianceCheck.DocumentTypes:ComplianceCheckRequest` | JMS message type / queue name |
| **Fires Service** | `GLDComplianceCheck.MainFlows:performComplianceCheck` | Process to trigger |
| **Condition Name** | `ComplianceCheck` | Filter/subscription name |
| **Concurrent** | `false` | Single-threaded processing |
| **Serial Suspend on Error** | `false` | |
| **Audit on Error** | `true` | Error logging enabled |
| **Boomi Pattern** | JMS Listen Start Shape → `MIG_WM_performComplianceCheck_Process` | |

### 3.2 GLDExpressGateway.ProcessFlows:triggerForSumbitToCredit

| Property | Value | Boomi Equivalent |
|---|---|---|
| **Document Type** | `GLDExpressGateway.DocumentTypes:SubmitToCredit` | JMS message type |
| **Fires Service** | `GLDExpressGateway.ProcessFlows:invokeSubmitToCredit` | Process to trigger |
| **Condition Name** | `subscribeToSubmitToCredit` | |
| **Concurrent** | `false` | Single-threaded |
| **Audit on Error** | `true` | |
| **Boomi Pattern** | JMS Listen Start Shape → `MIG_WM_invokeSubmitToCredit_Process` | |

---

## 4. GLDComplianceCheck

**Purpose**: Core compliance screening engine. Receives a `ComplianceCheckRequest`, validates it, determines the check type (CIU/OFAC/etc.), calls the external compliance system via DB adapter, and returns a `ComplianceCheckReply`.

**Entry Point**: Triggered by `triggerForCheckRequest` (pub-sub on `ComplianceCheckRequest` document).

### 4.1 Main Flows (Entry Points)

#### `MainFlows/complianceCheckRequest`
- **Role**: Public-facing service — the receiver of compliance check requests published to the trigger
- **Boomi Equivalent**: Start shape of the main process (triggered by JMS)

#### `MainFlows/performComplianceCheck`
- **Role**: Master orchestrator — calls validation, type determination, field mapping, external check, and reply
- **Contains**: 1 LOOP (iterates over multiple check records or applicants)
- **Calls** (in order):
  1. `validateRequiredFields`
  2. `validateFieldsFormat`
  3. `determineCheckRequestType`
  4. `mapRequestFieldsBasedOnCheckType`
  5. DB adapter services (select/insert/update via `GLDComplianceAdapterServices`)
  6. `sendReply`
- **Boomi Equivalent**: Main process with Decision/Map/Database shapes in sequence

### 4.2 Process Flows (Sub-Services)

| Service | Logic | Boomi Shape |
|---|---|---|
| `determineCheckRequestType` | Branch on check type field — routes to CIU, OFAC, or other path | **Decision** shape |
| `mapRequestFieldsBasedOnCheckType` | Map input fields to the specific format required by the check type | **Map** shape (multiple mappings) |
| `validateRequiredFields` | Loop over required field list; set error flag if any are null/blank; calls `isNullOrBlank` | **Loop** + **Decision** + **Map** |
| `validateFieldsFormat` | Validate numeric/positive constraints on fields; calls `isNumericOrEmpty`, `isPositiveNumber` | **Decision** + Java service calls |
| `sendReply` | Build and publish `ComplianceCheckReply` document back to the caller | **Message** shape + **Return** |

### 4.3 Utility Services

| Service | Logic | Boomi Equivalent |
|---|---|---|
| `addressValidation` | Validates address fields, likely calls an external address service | Custom scripting / HTTP call |
| `getProfileData` | Retrieves a customer profile; contains a LOOP (iterates result rows) | DB query + loop |
| `isNullOrBlank` | Checks if a string is null or empty — returns `"true"/"false"` | Groovy script or Decision |
| `isNumericOrEmpty` | Checks if string is numeric or empty | Groovy script |
| `isPositiveNumber` | Checks if value is a positive number | Groovy script |

### 4.4 Document Types (Data Structures)

| Document Type | Fields (Partial) | Boomi Profile |
|---|---|---|
| `ComplianceCheckRequest` | Check type, customer identifiers, name, address, SSN, DOB, amount | XML/JSON Profile — input |
| `ComplianceCheckReply` | Status, match result, CIU response fields, error codes | XML/JSON Profile — output |
| `ComplianceCheckRequestStatus` | Status fields for a pending request | XML Profile |
| `ComplianceCheckReplyStatus` | Reply status indicators | XML Profile |
| `CIUReply` | Raw CIU system response fields | XML Profile |
| `Identification` | Customer ID, SSN, passport, government ID fields | XML Profile (nested) |
| `Error` | errorCode, errorMessage, errorType | XML Profile |
| `CommonRecord` | Shared base fields across documents | XML Profile (referenced) |

### 4.5 DB Adapter Services (GLDComplianceAdapterServices)

These are IS Record types that define the signatures for JDBC adapter-invoked database operations against `ExpressOS` (Oracle `GLD_SCHEMA` on `ORASHR4T`).

| Service | Operation | Boomi Equivalent |
|---|---|---|
| `logCheckRequest` | INSERT — log incoming request to DB | Database (Insert) shape |
| `logCheckRequestXML` | INSERT — log raw XML of the request | Database (Insert) shape |
| `logCheckReply` | INSERT — log the compliance reply | Database (Insert) shape |
| `logCheckReplyError` | INSERT — log error replies | Database (Insert) shape |
| `selectCustomerAndRequest` | SELECT — look up customer + existing request | Database (Query) shape |
| `updateCIURefNbr` | UPDATE — store CIU reference number after check | Database (Update) shape |
| `purgeData` | DELETE — purge old compliance records | Database (Delete) shape |

---

## 5. GLDExpressGateway

**Purpose**: Central integration hub routing between the internal EFW (Express Financing Web) front-end system, XOS (eXpress Origination System), XLink (CRM/Customer master), VMR (Vendor Management Repository), and external credit bureaus (D&B). Also syncs LeasePak customer data to ExpressLink.

**Entry Points**:
- `triggerForSumbitToCredit` — async pub-sub trigger for credit submission
- `MainFlows/*` — synchronous HTTP/SOAP entry points for EFW, VM, CheckWriter, Customer sync

### 5.1 Main Flows

#### `MainFlows/EFW/processLXIRequest` *(Primary EFW Gateway)*
- **Role**: Master router for all EFW (Express Financing Web) requests — determines which XOS service to call based on request type
- **Pattern**: Receives XML request → Calls `getEfwServiceNameToInvoke` (lookup table) → Branches to appropriate Process Flow → Calls XOS via SOAP → Returns response
- **Backup versions**: `processLXIRequest_9_25_08_bu`, `processLXIRequest_ryan_bu` — archived; do not migrate

#### `MainFlows/VMSMT/processVMRequest` *(Vendor Management Router)*
- **Role**: Routes Vendor Management Repository (VMR) requests to the correct XLink service
- **Pattern**: Parse incoming VM request → Branch on request type → Call VMR/XLink service → Return

#### `MainFlows/CheckWriter/processCWRequest` *(Check Writer Router)*
- **Role**: Routes check write requests — creates payees, creates check requests
- **Calls**: `invokeGetUniquePayee`, `invokeAddNewPayee`, `invokeCreateCheckRequest`

#### `MainFlows/Customer/updateELCustomersFromLeasePk` *(LeasePak → ExpressLink Customer Sync)*
- **Role**: Batch sync — reads customers from LeasePak (Sybase), transforms, writes to ExpressLink (XOS)
- **Contains**: 1 LOOP (iterates over all customers)
- **Sub-flows called**: `runLpk2ELCustomerUpdate` → `elCustomerUpdateTask` → `invokeProcessLpkCustomer`

### 5.2 EFW Process Flows (XOS Integration — 30+ services)

These are the bulk of the integration — each `invoke*` flow calls one XOS service via HTTP/SOAP.

| Flow | Calls | Description |
|---|---|---|
| `invokeLoginRequest` | XOS SOAP | Authenticate user to XOS |
| `invokeAppHomeRequest` | XOS SOAP | Get application home/dashboard |
| `invokeAppSearchRequest` | XOS SOAP + 5 LOOPs | Search applications with filters |
| `invokeGetAppRequest` | XOS SOAP | Get full application details |
| `invokeAppSubmitRequest` | XOS SOAP | Submit application for processing |
| `invokeNewAppDataRequest` | XOS SOAP | Create new application |
| `invokeRefDataRequest` | XOS SOAP + 2 LOOPs | Get reference/lookup data |
| `invokeEquipmentStructureRequest` | XOS SOAP | Get equipment structure |
| `invokeGetLeaseStructureRequest` | XOS SOAP | Get lease structure |
| `invokeGetDecisionRequest` | XOS SOAP + 2 LOOPs | Get credit decision |
| `invokeStatusHistoryRequest` | XOS SOAP + 1 LOOP | Get status history |
| `invokeChargeListRequest` | XOS SOAP + 6 LOOPs | Get list of charges |
| `invokeCommentListRequest` | XOS SOAP + 2 LOOPs | Get comments list |
| `invokeCommentTypeListRequest` | XOS SOAP | Get comment type reference |
| `invokeAddCommentRequest` | XOS SOAP | Add a comment to application |
| `invokeDocumentListRequest` | XOS SOAP | Get document list |
| `invokeImageListRequest` | XOS SOAP | Get image list |
| `invokeUserPermissionInfoRequest` | XOS SOAP | Get user permission profile |
| `invokeUserSourcePermissionCheckRequest` | XOS SOAP | Check user permission for source |
| `invokeDefaultRequest` | XOS SOAP | Fallback default handler |

### 5.3 Applicant Process Flows

| Flow | Contains | Description |
|---|---|---|
| `invokeGetTransactionApplicants` | — | Get all applicants on a transaction |
| `invokeApplicantMatch` | 7 LOOPs | Match applicant against XLink records |
| `invokeDandBMatch` | — | Match business applicant vs D&B bureau |
| `getXLinkApplicantId` | 2 LOOPs | Retrieve XLink applicant ID |
| `invokeXLinkMatch` | — | Match customer in XLink CRM |
| `invokeXOSGetApplicant` | — | Get applicant from XOS |
| `invokeXOSGenericSaveApplicant` | — | Save applicant to XOS |
| `invokeSaveEFWApplicant` | — | Save EFW-specific applicant data |
| `invokeSaveEFWPrincipal` | — | Save principal/guarantor data |
| `invokeAddApplicantAddresses` | 2 LOOPs | Add addresses for applicant |

### 5.4 Customer Sync Process Flows

| Flow | Contains | Description |
|---|---|---|
| `invokeProcessLpkCustomer` | — | Process one LeasePak customer record |
| `invokeCustomerLesseeDataUpdateProcess` | 3 LOOPs | Update lessee data in ExpressLink |
| `createSaveApplicantFromLpk2XosData` | 4 LOOPs | Transform LeasePak → XOS applicant format |
| `prepareSaveApplicantMessage` | 4 LOOPs | Build SOAP payload for save |
| `invokeSaveUpdatedCustomer` | — | Persist updated customer |
| `assignCustomFieldIds` | 2 LOOPs | Assign GLD custom field IDs |
| `getCustomerLesseeData` | — | Retrieve lessee data |

### 5.5 VMR Process Flows

| Flow | Description |
|---|---|
| `invokeGetVendorContacts` | Retrieve vendor contact list from XLink |
| `invokeGetVendorDetailsByGldId` | Get vendor details by GLD ID |
| `invokeGetVendorConstructs` | Get vendor business constructs |
| `invokeUpdateVendorRequest` | Update vendor record |
| `invokeUpdateVendorContactRequest` | Update vendor contact |
| `invokeDeleteVendorContactRequest` | Delete vendor contact |
| `invokeUpdateVendorApprovals` | Update vendor approval status |
| `invokeUpdateVendorServicingRequest` | Update vendor servicing info |
| `invokeUpdateVendorCreditDataRequest` | Update vendor credit data |
| `invokeMapVmrContactsToGld` | Map VMR contact IDs to GLD IDs (1 LOOP) |
| `invokeUpdateContactGldIDsRequest` | Sync GLD IDs back to contacts (1 LOOP) |
| `invokeGetContact` | Retrieve single contact |
| `invokeChangeStatusRequest` | Change vendor status |
| `invokeUpdateVendorInXLink` | Push vendor changes to XLink CRM |
| `invokeGetRgrpGldIdsRequest` | Get RGRP GLD IDs |
| `invokeGetExcludeInterimRent` | Get exclude interim rent flag |
| `invokeGetIsProrataAppliedValue` | Get prorata applied value |

### 5.6 Compliance Process Flow

| Flow | Description |
|---|---|
| `invokeComplianceCheckBatch` | Invoke GLDComplianceCheck for a batch of applicants |

### 5.7 XOS Generic Transaction Flows

| Flow | Contains | Description |
|---|---|---|
| `invokeXosGenericXmlTransactionSave` | 4 LOOPs | Generic XML transaction save to XOS |
| `invokeXosGenericXmlTransactionAssetsSave` | 3 LOOPs | Save transaction assets |
| `invokeXosGenericXmlTransactionNotesSave` | 1 LOOP | Save transaction notes |
| `invokeXosGenericRelatedPartySave` | — | Save related party |
| `invokeXosGenericXmlTransactionSave_1` | — | Alternate version |
| `invokeGetTransactionDetails` | — | Get full transaction detail |
| `invokeGetTransactionAssets` | — | Get transaction assets |
| `invokeGetCreditDecision` | — | Get credit bureau decision |
| `invokeRelatedPartyRequest` | 1 LOOP | Get/save related parties |
| `invokeTransactionAssetCustomFieldSave` | 2 LOOPs | Save custom fields on assets |
| `invokeTransactionContactInformationSave` | — | Save contact info |
| `invokeXLinkCustomFieldSave` | — | Save custom field in XLink |
| `invokeXOSDataLoader` | — | Load data to XOS |
| `invokeXOSDataLoaderOriginators` | 1 LOOP | Load originator data |
| `invokeXOSDataLoaderSuppliers` | — | Load supplier data |

### 5.8 Utility Services

| Service | Contains | Description |
|---|---|---|
| `getEfwServiceNameToInvoke` | — | Lookup table: map EFW action code → XOS service name |
| `getXLinkConstants` | — | Return XLink system constants (URLs, credentials) |
| `getVMSMTConstants` | — | Return VMR system constants |
| `getVMSMTUserConstants` | — | Return user-context VMR constants |
| `getDandBConstants` | — | Return D&B bureau endpoint constants |
| `getGldStatusIdList` | — | Return list of GLD status IDs |
| `getGldTranStatusCategory` | — | Map transaction status to category |
| `getNextSequenceValue` | — | Get next DB sequence value |
| `getRelatedPartyType` | — | Look up related party type code |
| `getELBusinessType` | — | Look up business type code |
| `getWmForXLinkUserId` | — | Map webMethods user to XLink user ID |
| `getTNProfile` | 1 LOOP | Get TN (Tenant) profile data |
| `getServiceName` | — | Get current running service name |
| `getDocument` | — | Retrieve a named document from the pipeline |
| `getDateDiff` | — | Calculate date difference |
| `clenseXLinkDate` | — | Clean/normalize XLink date format |
| `lookupCountryFromProvince` | — | Map province code to country |
| `lookupCustomFieldIdBasedOnName` | — | Reverse lookup: name → custom field ID |
| `invokeFindMatchInList` | 2 LOOPs | Search a list for a matching value |
| `invokeMatchVMR_ID_to_XLink_ID` | — | Cross-reference VMR and XLink IDs |
| `invokeXML_HTTP` | — | Generic HTTP POST with XML |
| `invokeXML_SOAP` | — | Generic SOAP call |
| `isNullOrBlank` | — | Null/blank check utility |
| `isUserAssignedGLDgroups` | — | Authorization check |
| `logRequestResponse` | — | Log request/response (calls GLDMessageLog) |
| `processScreenButtonPerms` | 6 LOOPs | Process screen button permission matrix |
| `setGroups` | — | Set group membership on pipeline |
| `setAppSubmitAssets` | 1 LOOP | Set assets for app submission |
| `publishSubmitToCredit` | — | **Publish** SubmitToCredit document to trigger |
| `AddExternalSystemID` | — | Add an external system ID to document |
| `insertAssetInformation` | 2 LOOPs | Insert asset records |
| `insertLegalBusinessTypes` | — | Insert legal business type lookups |

### 5.9 D&B Web Connector Flows

These are auto-generated stubs from the D&B WSDL. All call the D&B credit bureau SOAP service.

| Flow | Description |
|---|---|
| `GetReport` | Get full credit report for a business |
| `GetPacket` | Get a specific data packet |
| `GetPacketsFromArf` | Get packets from ARF (Automated Report Feed) |
| `GetListOfSimilars` | Get list of similar businesses for matching |
| `GetListOfSimilarsHtml` | HTML-formatted similar list |
| `GetListOfSimilarsXml` | XML-formatted similar list |
| `GetEM09LookupResponse` | Get EM09 lookup result |

**Boomi equivalent**: These become HTTP Client connector calls with SOAP action headers targeting the D&B endpoint.

### 5.10 Supplemental Flows

| Flow | Description |
|---|---|
| `getFixedCommentTypeList` | Return hardcoded comment type list |
| `lookUpCommentTypeDescription` | Look up description for a comment type code (1 LOOP) |

---

## 6. GLDExpressWebServices

**Purpose**: Exposes selected GLDExpressGateway and utility flows as external SOAP web services. Uses webMethods SOAP wrappers with `registerFlowServiceForSOAP` / `unregisterFlowServiceForSOAP` lifecycle services.

**Boomi equivalent**: These become **API Service Components** (REST/SOAP endpoint) in Boomi's API Management.

### 6.1 Exposed Web Services

| SOAP Operation | Underlying Flow | Description |
|---|---|---|
| `normalizeAddress` | `GLDExpressWebServices.MainFlows:NormalizeAddress` | Normalize a mailing address (calls external address service) |
| `getCustomerHistory` | `GLDExpressWebServices.MainFlows:processCustomerHistoryRequest` | Retrieve customer history from LeasePak/XOS |
| `getLesseeIDFromLPK` | `GLDExpressWebServices.MainFlows:getLesseeIDFromLPK` | Look up lessee ID from LeasePak by customer data |
| `approvedStatusChangeNotification` | `GLDExpressWebServices.MainFlows:approvedStatusChangeNotification` | Notify downstream of approved status change |
| `genericStatusChangeNotification` | `GLDExpressWebServices.MainFlows:genericStatusChangeNotification` | Notify downstream of any status change (5 LOOPs) |
| `Example` | `GLDExpressWebServices.MainFlows:Example` | Example/test endpoint |

### 6.2 Wrapper Pattern

Each exposed service has:
- **Wrapper flow**: receives SOAP input, transforms to IS format, calls underlying service, wraps response back to SOAP
- **Registration flows**: `registerFlowServiceForSOAP` / `unregisterFlowServiceForSOAP` — called at package startup/shutdown to bind the service to the IS SOAP listener

**Boomi migration pattern**:
- Create an **API Component** with a SOAP or REST definition
- The wrapper logic becomes a Map shape at the start (SOAP envelope → internal format) and end (internal → SOAP response) of the process

### 6.3 Sub-Flows

| Flow | Description |
|---|---|
| `ProcessFlows/GetLesseeIDFromLPK/checkDocument` | Validates the input document format before calling LeasePak |
| `Utilities/getStateCode` | Look up state code from name or abbreviation |
| `MainFlows/setTempCustomerHistoryOutput` | Temp output staging for customer history |

### 6.4 Address Normalization WSDL Wrapper

- `Wrappers/AddressNormalization/GLDExpressGatewayServices_AddressNormalizationPortType/normalizeAddress`  
  → Auto-generated from WSDL; delegates to `addressNormalizationWrapper`  
  → **Boomi**: HTTP Client shape calling address normalization service (USPS or similar)

---

## 7. GLDFundingEngine

**Purpose**: ACH (Automated Clearing House) funding processor. Receives a funding request, parses a NACHA flat-file structure, processes ACH batch records, and writes results to the Oracle funding database.

### 7.1 Main Flows

#### `MainFlows/processFundingRequest`
- **Role**: Entry point — receives a funding request, validates, calls `processACHBatch`
- **Contains**: 2 LOOPs
- **Boomi Equivalent**: Main process — Start shape → Map → Loop → Database

#### `MainFlows/processACHBatch`
- **Role**: Process each ACH batch entry in the NACHA file
- **Contains**: 1 LOOP (iterates ACH batch records)
- **Uses**: `GLDFundingEngine.Schemas:NACHA_Schema` (flat file parser), `FundingEngineACH` DB connection
- **Boomi Equivalent**: Map shape with Flat File Profile → Loop → Database (Insert)

### 7.2 SOAP Wrapper

#### `Wrappers/fundingEngineWrapper`
- Exposes `processFundingRequest` as a SOAP web service (1 LOOP)
- Registration flows: `registerFlowServiceForSOAP` / `unregisterFlowServiceForSOAP`

### 7.3 Schemas (Flat File)

| Schema | Type | Description |
|---|---|---|
| `GLDFundingEngine.Schemas:NACHA_Schema` | Flat File Schema | NACHA ACH file format — delimiter-based, with `DelimiterExtractorContainer` |
| `GLDFundingEngine.Schemas:ACH_Schema` | Flat File Schema | ACH fixed-length record format — `FixedLengthParser`, record size defined |
| `GLDFundingEngine.Schemas:NACHA` | Document Part Holder | NACHA dictionary defining `BatchRecord` type |

**Boomi equivalent**: These become **Flat File Profiles** in Boomi — NACHA uses fixed-length records with the record type code in position 1 (standard NACHA format).

### 7.4 Utility

| Flow | Description |
|---|---|
| `ProcessFlows/formatRoutingNumber` | Format/pad a 9-digit ABA routing number to NACHA spec |

---

## 8. GLDMessageLog

**Purpose**: Audit logging utility. Stores raw XML request/response pairs in the Oracle message log database (`GLD_SCHEMA` on `ORASHR4T`). Called by `GLDExpressGateway.Utilities.FlowServices:logRequestResponse`.

### 8.1 Flow Services

| Service | Description | Boomi Equivalent |
|---|---|---|
| `LogRequestAndResponse` | Log both request and response XML to DB in one call | Database (Insert) — 2 records |
| `LogXMLRequest` | Log the XML request document only | Database (Insert) |
| `LogXMLResponse` | Log the XML response document only | Database (Insert) |

**Connection used**: `GLDMessageLogAdapterEnv:MessageLog` → Oracle `GLD_SCHEMA@CSC06DSHORA1S:1522/ORASHR4T`

**Boomi migration**: A reusable subprocess with a Database connector (Insert) using `MIG_WM_MessageLogDB_Connection`. Called from any process that needs audit logging.

---

## 9. GLDSoap

**Purpose**: Low-level generic SOAP/HTTP invocation utility. Provides reusable services for making SOAP calls with namespace injection capabilities. Used by GLDExpressGateway flows that call XOS and XLink SOAP APIs.

### 9.1 Flow Services

| Service | Description | Boomi Equivalent |
|---|---|---|
| `ProcessFlows/invokeSOAPService` | Generic SOAP call — builds HTTP request, sets headers, invokes endpoint | HTTP Client connector |
| `ProcessFlows/invokeSOAPService_1` | Alternate SOAP invoker (variant) | HTTP Client connector |
| `ProcessFlows/invokeSOAPService_BeforeXmlHeader` | SOAP call variant — inserts XML header before SOAP envelope | HTTP Client with custom header shape |

**GLDSoap20**: Identical copy of GLDSoap — same logic, newer version. **Migrate from GLDSoap20 only.**

### 9.2 Java Service: `addNameSpace`

```
Inputs:  nodeName (String), nameSpace (String), prefix (String, optional), document (IData)
Output:  document (IData) — with namespace attribute added to the specified node
Logic:   Walks the IS document cursor, finds the target node, injects
         xmlns:prefix="namespace" attribute into the XML element
```

**Boomi equivalent**: A Groovy scripting shape that performs `element.setAttribute("xmlns:prefix", "namespace")` on a DOM element.

### 9.3 Java Service: `getNodeName`

```
Inputs:  (pipeline, reads 'nodeName')
Output:  Extracted or normalized node name
Logic:   Parses and returns the local name portion of a qualified XML node name
```

**Boomi equivalent**: Groovy script or a Set Properties shape with a substring expression.

---

## 10. Adapter/Environment Packages

### 10.1 GLDComplianceAdapterServices — Record Types

These are IS `record` node types — they define the input/output signatures of JDBC adapter services. In the migration, they become the **request/response profiles** for Boomi Database connector operations.

| Record | Operation | Table/Procedure (inferred) |
|---|---|---|
| `logCheckRequest` | INSERT | Compliance check request log table |
| `logCheckRequestXML` | INSERT | Raw XML log table |
| `logCheckReply` | INSERT | Compliance reply log table |
| `logCheckReplyError` | INSERT | Error log table |
| `selectCustomerAndRequest` | SELECT | Customer + request lookup |
| `updateCIURefNbr` | UPDATE | Set CIU reference number |
| `purgeData` | DELETE | Data purge operation |

### 10.2 GLDExpressAdapterServices — Record Types

Similar pattern for Express adapter. Record signatures match tables in the EDW, ODS, and Funding databases used by `GLDExpressGateway` flows.

### 10.3 GLDMessageLogAdapterServices — Record Types

Record signatures for the message log INSERT operations.

---

## 11. Java Custom Services

All Java services use the webMethods `IData` pipeline pattern. Each reads from `pipeline.getCursor()` and writes results back into the same cursor.

### 11.1 GLDComplianceCheck.Utilities.JavaServices

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `isNullOrBlank` | `inString` | `result` ("true"/"false") | Null check + `.trim().equals("")` |
| `isNumericOrEmpty` | `inString` | `result` | Regex or `Long.parseLong()` check |
| `isPositiveNumber` | `inString` | `result` | Parse as double, check > 0 |

**Boomi equivalent**: All three become a **Groovy Data Process** shape or Decision shape.

### 11.2 GLDExpressGateway.ProcessFlows.Applicant.JavaServices

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `invokeXOS_EFWApplicantMatch` | `EFWCustomer` (IData), `XLinkCustomer` (IData) | `Reason`, `MatchCode` | Uses KeyBank proprietary `com.keybank.kef.bop` library to match ExpressFinancing and ExpressLink customer records by name, TIN, address |

**Dependency**: `com.keybank.kef.bop.*` — KeyBank internal library. **Must be provided as a JAR on the Boomi Atom.**

**Boomi equivalent**: Groovy script that implements the matching logic inline (preferred if JAR is unavailable) or Java SDK custom library.

### 11.3 GLDExpressGateway.ProcessFlows.Customer.JavaServices

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `determineXLinkCustomerUpdate` | LeasePak customer IData | Action code | Compares LPK customer fields against XLink to decide create/update/skip |
| `groupLpkCustomerData` | LPK data list | Grouped IData | Groups multiple LPK records by customer ID |
| `versionCheck` | `initialLoad` flag | — | Checks version for initial vs delta load logic |

**Dependency**: `com.keybank.kef.lpk2xoscu.*` — LeasePak-to-XOS Customer Update library.

### 11.4 GLDExpressGateway.Utilities.JavaServices

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `addDateTime` | `inDateTime`, `pattern`, `datePart`, `addValue`, `subtractDay` | `outDateTime` | Date arithmetic using `SimpleDateFormat` + `Calendar.add()` |
| `calculateDateDifference` | two date strings | difference in days/hours | `Calendar` subtraction |
| `compareDates` | two date strings | comparison result | `Date.before()` / `after()` |
| `invokeServiceThrowExceptions` | `serviceName`, input IData | service output | Dynamically invokes an IS service by name, propagates exceptions |
| `serviceExists` | `serviceName` | boolean | Checks if a named IS service exists in the namespace |
| `sortDocumentList` | IData list | sorted IData list | Java `Collections.sort()` with custom Comparator |
| `sortDocumentList_1` | IData list | sorted list | Variant of sortDocumentList |

**Boomi equivalents**:
- `addDateTime` / `calculateDateDifference` / `compareDates` → Groovy script with Java `LocalDate`/`Calendar`
- `invokeServiceThrowExceptions` → Boomi's **Execute Process** shape (dynamic subprocess invocation)
- `serviceExists` → Not directly needed; simplify by using direct process references
- `sortDocumentList` → Groovy script sorting a list

### 11.5 GLDExpressWebServices.Utilities.JavaServices

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `doesLesseeMatch` | `expressLinkCustomerData` (IData), `leasePakLesseeData` (IData) | `matched` | Uses `com.keybank.kef.bop.model` to compare ExpressLink and LeasePak lessee records for identity matching |

**Dependency**: `com.keybank.kef.bop.*`

### 11.6 GLDSoap.Utilities.JavaServices (used in GLDSoap20 too)

| Method | Inputs | Outputs | Logic |
|---|---|---|---|
| `addNameSpace` | `nodeName`, `nameSpace`, `prefix`, `document` (IData) | `document` (IData) | Walks IS document tree, injects XML namespace declaration onto the specified element |
| `getNodeName` | `document` cursor | `nodeName` | Extracts local name from a qualified XML node |

---

## 12. Document Types and Schemas

### 12.1 Compliance Document Types (GLDComplianceCheck)

| Type | Purpose |
|---|---|
| `ComplianceCheckRequest` | Input to the compliance engine — customer data for screening |
| `ComplianceCheckReply` | Output — screening result, match codes, CIU response |
| `ComplianceCheckRequestStatus` | Status tracker for async requests |
| `ComplianceCheckReplyStatus` | Reply status for async patterns |
| `CIUReply` | Raw response from CIU (Compliance Intelligence Unit) system |
| `Identification` | Customer identification sub-document (SSN, passport, etc.) |
| `Error` | Error payload structure |
| `CommonRecord` | Base record — shared fields across all document types |

### 12.2 Express Gateway Document Types (GLDExpressGateway)

- `GLDExpressGateway.DocumentTypes:SubmitToCredit` — published to trigger `triggerForSumbitToCredit`
- Hundreds of IS Records for XOS/XLink request and response structures (163 total in GLDExpressGateway, 113 in old version)

### 12.3 Web Services Document Types (GLDExpressWebServices)

- `normalizeAddressRequest` — XSD schema for address normalization SOAP input

### 12.4 Funding Engine Schemas (GLDFundingEngine)

| Schema | Format | Use |
|---|---|---|
| `NACHA_Schema` | Flat File (delimited, `DelimiterExtractorContainer`) | Parse NACHA ACH file format |
| `ACH_Schema` | Flat File (fixed-length, `FixedLengthParser`) | Parse individual ACH records |
| `NACHA` | Document Part Holder — `BatchRecord` type | NACHA record type dictionary |

---

## 13. Boomi Migration Mapping Summary

### 13.1 Connections → Boomi Connection Components

| webMethods Connection | Boomi Component | Type | Notes |
|---|---|---|---|
| `GLDComplianceAdapterEnv:ExpressOS` | `MIG_WM_ComplianceDB_Connection` | Database (Oracle) | Reset password |
| `GLDMessageLogAdapterEnv:MessageLog` | `MIG_WM_MessageLogDB_Connection` | Database (Oracle) | Reset password; may share with above |
| `GLDExpressAdapterEnv.EDW:DataWareHouseEDW` | `MIG_WM_EDW_Connection` | Database (Oracle) | Reset password |
| `GLDExpressAdapterEnv.ODS:DataWareHouseODS` | `MIG_WM_ODS_Connection` | Database (Oracle) | Reset password |
| `GLDExpressAdapterEnv.Funding:FundingEngineACH` | `MIG_WM_FundingACH_Connection` | Database (Oracle) | Reset password |
| `GLDExpressAdapterEnv.LeasePak:LeasePakDatabase` | `MIG_WM_LeasePak_Connection` | Database (Sybase) | Sybase JAR needed; reset password |
| XOS SOAP API (via `invokeSOAPService`) | `MIG_WM_XOS_HTTP_Connection` | HTTP Client | URL in `getXLinkConstants` utility |
| XLink CRM API (via `invokeSOAPService`) | `MIG_WM_XLink_HTTP_Connection` | HTTP Client | URL in `getXLinkConstants` utility |
| D&B SOAP API (via WebConnectors) | `MIG_WM_DandB_HTTP_Connection` | HTTP Client | D&B endpoint URL from WSDL |

### 13.2 Triggers → Boomi Process Starts

| webMethods Trigger | Boomi Start Shape |
|---|---|
| `triggerForCheckRequest` (subscribe to `ComplianceCheckRequest`) | JMS Listen — `ComplianceCheckRequest` queue |
| `triggerForSumbitToCredit` (subscribe to `SubmitToCredit`) | JMS Listen — `SubmitToCredit` queue |

### 13.3 Flow Services → Boomi Processes

| webMethods Pattern | Boomi Equivalent |
|---|---|
| Main orchestrator flow | Single Boomi process with sequential shapes |
| `BRANCH` on a field value | **Decision** shape |
| `LOOP` over a document list | **Loop** shape (or Data Process → iterate) |
| `INVOKE` another IS service | **Execute Process** subprocess shape |
| `MAP` step (field mapping) | **Map** shape |
| `EXIT` with success/failure signal | **Stop** shape (success) / **Stop** shape (failure/exception) |
| SOAP invocation via `invokeSOAPService` | **HTTP Client** connector with SOAP action |
| DB adapter service (SELECT/INSERT/UPDATE) | **Database** connector (Query/Execute) |
| Publish a document to trigger | **JMS** connector Send |

### 13.4 Java Services → Boomi Groovy Scripts

| Java Service Method | Boomi Implementation |
|---|---|
| `isNullOrBlank`, `isNumericOrEmpty`, `isPositiveNumber` | Groovy script in **Data Process** shape |
| `addDateTime`, `calculateDateDifference`, `compareDates` | Groovy script using `java.time.LocalDate` |
| `addNameSpace`, `getNodeName` | Groovy script manipulating XML DOM |
| `invokeServiceThrowExceptions` | **Execute Process** shape (dynamic) |
| `sortDocumentList` | Groovy script with `Collections.sort()` |
| `invokeXOS_EFWApplicantMatch` | Groovy script implementing matching logic (KeyBank JAR may be needed) |
| `determineXLinkCustomerUpdate`, `groupLpkCustomerData` | Groovy scripts (require LPK2XOS JAR or reimplementation) |

### 13.5 SOAP Web Services → Boomi API Endpoints

| webMethods SOAP Service | Boomi API Pattern |
|---|---|
| `normalizeAddress` | REST/SOAP API Component → Process |
| `getCustomerHistory` | REST/SOAP API Component → Process |
| `getLesseeIDFromLPK` | REST/SOAP API Component → Process |
| `approvedStatusChangeNotification` | REST/SOAP API Component → Process |
| `genericStatusChangeNotification` | REST/SOAP API Component → Process |
| `fundingEngineWrapper` | REST/SOAP API Component → Process |

### 13.6 Flat File Schemas → Boomi Flat File Profiles

| webMethods Schema | Boomi Profile | Format |
|---|---|---|
| `NACHA_Schema` | `MIG_WM_NACHA_FlatFile_Profile` | NACHA ACH — delimiter-based |
| `ACH_Schema` | `MIG_WM_ACH_FlatFile_Profile` | ACH — fixed-length records |

---

## 14. Open Items & Migration Checklist

### Database Credentials (All must be reset)
- [ ] Oracle `GLD_SCHEMA` password for `CSC06DSHORA1S:1522/ORASHR4T` (Compliance + MessageLog)
- [ ] Oracle `KEF_GLD_WEBMETHOD` password for `CSC06DORASA:1521/KEF1` (EDW connection)
- [ ] Oracle `KEF_GLD_WEBMETHOD` password for `CSC06DORASA:1521/KEF1` (ODS connection — verify if same as EDW)
- [ ] Oracle `GLD_ACHD_SCHEMA` password for `CSC06DORASA:1521/ORA01` (Funding)
- [ ] Sybase `webmthd` password for `csc06dsyb01/ksc_cartman` (LeasePak)

### System Endpoint URLs (Not stored in packages — must be sourced)
- [ ] XOS SOAP endpoint URL (used in all `invokeXOS*` flows via `getXLinkConstants`)
- [ ] XLink CRM SOAP endpoint URL
- [ ] D&B credit bureau WSDL / endpoint URL
- [ ] Address normalization service endpoint (used in `NormalizeAddress`)
- [ ] CIU (Compliance Intelligence Unit) endpoint details

### JDBC Drivers for Boomi Atom
- [ ] Oracle JDBC JAR (`ojdbc8.jar` or `ojdbc11.jar`) — for all Oracle connections
- [ ] Sybase jConnect JAR (`jconn4.jar`) — for LeasePak connection

### Proprietary Java Libraries
- [ ] `com.keybank.kef.bop.*` — needed for `invokeXOS_EFWApplicantMatch` and `doesLesseeMatch`
- [ ] `com.keybank.kef.lpk2xoscu.*` — needed for Customer sync Java services
- [ ] Decision needed: **Reimplement logic in Groovy** vs **deploy JARs to Boomi Atom custom lib**

### Architecture Decisions
- [ ] JMS broker for pub-sub triggers: Use Boomi's built-in **JMS** or replace with a direct process invocation (simpler if async not required)
- [ ] NACHA flat file: Confirm exact record layout against NACHA spec (94-character fixed-length is standard)
- [ ] LeasePak Sybase: Confirm Sybase version (the JAR is `jconn2` = Sybase ASE ≤ 15; update to `jconn4` for ASE 16+)
- [ ] `GLDExpressGateway` has 149 flow services — prioritize which are in active use vs legacy/backup flows
- [ ] `*_bu`, `*_OLD`, `*_old` naming indicates backup/archived versions — confirm none are in active use before skipping

### Not Migrating (Archived)
- `GLDExpressGateway_old` — superseded by `GLDExpressGateway`
- `GLDFundingEngine20080714` — superseded by `GLDFundingEngine`
- All flows named `*_OLD`, `*_bu`, `*_Ryan_*` within active packages — backup copies

---

*Analysis generated: 2026-06-02 | Packages: 15 | Flow services: 202 active (272 total including archives) | Java methods: 20 | DB connections: 6 | Triggers: 2*
