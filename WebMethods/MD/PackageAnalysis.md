# PackageAnalysis — GLDComplianceAdapterServices → Workato Migration Reference

> **Document Status:** COMPLETE — All 7 DB services documented with full parameter tables.
> **Prepared by:** WebmethodsToBoomi_Migration Agent (re-oriented for Workato target)
> **Source Build Date:** 2008-06-26 | **Source Platform:** webMethods IS 6.5
> **Target Platform:** Workato (callable recipe + Oracle DB connector)
> **Connection Package:** GLDComplianceAdapterEnv (documents JDBC alias)
> **Services Package:** GLDComplianceAdapterServices (documents all 7 Oracle operations)

---

## 1. Source Package Summary

| Attribute | Value |
|---|---|
| **Primary Package** | `GLDComplianceAdapterServices` |
| **Connection Package** | `GLDComplianceAdapterEnv` |
| **Release** | `GLDComplianceAdapterServices 1.0 / 2008-06-26` |
| **Source IS Version** | webMethods Integration Server 6.5 |
| **Publisher Host** | `cwb02dwmis02.keybank.com` |
| **Adapter Type** | JDBC Adapter (`JDBCAdapter`) |
| **Connection Alias** | `GLDComplianceAdapterEnv:ExpressOS` |
| **DB Host** | `CSC06DSHORA1S` |
| **DB Port** | `1522` |
| **DB SID** | `ILMSUM` |
| **DB Schema** | `GLD_SCHEMA` |
| **DB Platform** | Oracle 10g |
| **Total DB Services** | 7 (5 stored procedures + 1 SELECT JOIN + 1 parameterless SP) |
| **Flow Services in Package** | 0 — orchestration is in `GLDComplianceCheck` (separate package) |
| **External System** | CIU (Customer Identification Unit) — external compliance check via HTTP |

### Integration Flow Summary

The GLD Compliance workflow performs identity/compliance checks for new customers:

```
CLIENT → [HTTP POST] → Workato Recipe
    │
    ├─ 1. ACCLOGCHECKREQUEST (Oracle SP)   ← Log new check request; get request ID
    ├─ 2. LOGXMLREQUEST (Oracle SP)         ← Archive raw XML request
    ├─ 3. [CIU HTTP call] (external)        ← Send to external compliance system
    ├─ 4. ACCUPDATECIUREFNBR (Oracle SP)    ← Store CIU reference number back
    │
    ├─ IF CIU passed:
    │   └─ 5a. ACCLOGCHECKREPLY (Oracle SP) ← Log successful reply
    │
    └─ IF CIU failed:
        └─ 5b. ACCLOGCHECKREPLYERROR (Oracle SP) ← Log error reply
    │
    ├─ 6. selectCustomerAndRequest (SELECT JOIN) ← Retrieve full record
    └─ RETURN: customer data to caller
    │
    └─ ON ERROR: ACCLOGCHECKREPLYERROR ← Log system error
```

---

## 2. Workato Component Plan

| # | Component Name | Workato Type | Source Artifact | Notes |
|---|---|---|---|---|
| 1 | `MIG_WM_GLD_Oracle_Connection` | Connection (Oracle DB) | `ExpressOS` JDBC alias | Create in Workato GUI — see §3 |
| 2 | `MIG_WM_GLDComplianceAdapterServices_Recipe` | Recipe (callable) | `GLDComplianceCheck` flow service | HTTP POST trigger, 10 steps |
| 3 | `MIG_WM_GLD_PurgeData_Recipe` | Recipe (scheduled) — optional | `purgeData` service | Daily/weekly maintenance recipe |

---

## 3. Workato Connection Component

### 3.1 Oracle DB Connection

| Parameter | Value |
|---|---|
| **Connection Name** | `MIG_WM_GLD_Oracle_Connection` |
| **Provider** | Oracle |
| **Host** | `CSC06DSHORA1S` |
| **Port** | `1522` |
| **SID / Service Name** | `ILMSUM` |
| **Schema / Username** | `GLD_SCHEMA` |
| **Password** | Retrieve from IS Admin UI: Adapters → JDBC → ExpressOS (proprietary encryption — cannot reuse directly) |
| **Pool Min / Max** | 1 / 10 (configure at Workato plan level) |

> **Security note:** The webMethods `node.ndf` stores the password in proprietary symmetric encryption. Obtain the plaintext from the IS Admin console or CyberArk/HashiCorp vault before decommissioning IS.

---

## 4. Operation Components (Workato Actions)

### 4.1 logCheckRequest → ACCLOGCHECKREQUEST (Stored Procedure)

**Workato Action:** Oracle → Stored procedure → `GLD_SCHEMA.ACCLOGCHECKREQUEST`

**Input Parameters (25):**

| # | SP Parameter | DB Type | webMethods Field | Workato Input Source | Notes |
|---|---|---|---|---|---|
| 1 | CUSTOMERNBR | VARCHAR2(18) | CustomerNbr | trigger.CustomerNbr | Customer number |
| 2 | CUSTOMERTYPE | VARCHAR2(3) | CustomerType | trigger.CustomerType | Type code |
| 3 | PARTYTYPE | VARCHAR2(20) | PartyType | trigger.PartyType | Party type |
| 4 | BUSINESSNAME | VARCHAR2(40) | Businessname | trigger.Businessname | Business name |
| 5 | APPLICATIONNBR | VARCHAR2(18) | ApplicationNbr | trigger.ApplicationNbr | App number |
| 6 | CHANNEL | VARCHAR2(10) | Channel | trigger.Channel | Channel |
| 7 | LOB | VARCHAR2(10) | LOB | trigger.LOB | Line of business |
| 8 | PRODUCTCODE | VARCHAR2(10) | ProductCode | trigger.ProductCode | Product code |
| 9 | SUBPRODUCTCODE | VARCHAR2(10) | SubProductCode | trigger.SubProductCode | Sub-product code |
| 10 | POSTBACK | VARCHAR2(200) | PostBack | trigger.PostBack | Post-back URL |
| 11 | COMPLIANCEREPLYEMAIL | VARCHAR2(75) | ComplianceReplyEmail | trigger.ComplianceReplyEmail | Reply email |
| 12 | FIRSTNAME | VARCHAR2(20) | FirstName | trigger.FirstName | First name |
| 13 | MIDDLENAME | VARCHAR2(20) | MiddleName | trigger.MiddleName | Middle name |
| 14 | LASTNAME | VARCHAR2(20) | LastName | trigger.LastName | Last name |
| 15 | ADDRESSLINE1 | VARCHAR2(40) | AddressLine1 | trigger.AddressLine1 | Address 1 |
| 16 | ADDRESSLINE2 | VARCHAR2(40) | AddressLine2 | trigger.AddressLine2 | Address 2 |
| 17 | ADDRESSLINE3 | VARCHAR2(40) | AddressLine3 | trigger.AddressLine3 | Address 3 |
| 18 | ADDRESSLINE4 | VARCHAR2(40) | AddressLine4 | trigger.AddressLine4 | Address 4 |
| 19 | CITY | VARCHAR2(20) | City | trigger.City | City |
| 20 | STATE | VARCHAR2(2) | State | trigger.State | State code |
| 21 | ZIP | VARCHAR2(10) | Zip | trigger.Zip | ZIP code |
| 22 | COUNTRYCODE | VARCHAR2(3) | CountryCode | trigger.CountryCode | Country code |
| 23 | SSNTIN | VARCHAR2(9) | SSNTIN | trigger.SSNTIN | SSN or TIN |
| 24 | DOB | DATE | DOB | trigger.DOB (convert to DATE) | Date of birth |
| 25 | REQUESTORSYSTEMREQUESTID | BIGINT | RequestorSystemRequestID | trigger.RequestorSystemRequestID | Requestor system request ID |

**Output:**
- `accCheckRequestID` (BIGINT) — auto-generated by Oracle; use `SELECT ACCCHECKREQUESTID FROM GLD_SCHEMA.ACCCHECKREQUEST WHERE REQUESTORSYSTEMREQUESTID = ?` to retrieve

---

### 4.2 logCheckRequestXML → LOGXMLREQUEST (Stored Procedure)

**Workato Action:** Oracle → Stored procedure → `GLD_SCHEMA.LOGXMLREQUEST`

| # | SP Parameter | DB Type | webMethods Field | Workato Input Source |
|---|---|---|---|---|
| 1 | APPLICATIONID | BIGINT | ApplicationID | step1.accCheckRequestID |
| 2 | REQUEST | LONGVARCHAR | Request | JSON encode of trigger payload |
| 3 | REQUESTIDENTIFIER1 | VARCHAR2 | RequestIdentifier1 | trigger.CustomerNbr |
| 4 | REQUESTIDENTIFIER2 | VARCHAR2 | RequestIdentifier2 | trigger.ApplicationNbr |
| 5 | REQUESTIDENTIFIER3 | VARCHAR2 | RequestIdentifier3 | trigger.Channel |

**Output:** None (void procedure).

---

### 4.3 CIU External Call (HTTP Placeholder)

**Workato Action:** HTTP → POST → `[CIU_ENDPOINT_URL]`

> ⚠️ Endpoint URL is unknown — obtain from SME. Wire this action after receiving the URL.

| Field | Value |
|---|---|
| Method | POST |
| URL | `[CIU_ENDPOINT_URL]` — wire from SME |
| Request body | JSON of all customer + request fields |
| Expected response | `{ "CIURefNbr": "...", "CheckResult": "TRUE" or "FALSE", "ErrorType": "...", "ErrorCode": "...", "ErrorDesc": "..." }` |

**Output data pills used downstream:**
- `ciu_response.CIURefNbr` → steps 4, 5a, 5b, 6
- `ciu_response.CheckResult` → IF condition (step 5)
- `ciu_response.ErrorType / ErrorCode / ErrorDesc` → step 5b

---

### 4.4 updateCIURefNbr → ACCUPDATECIUREFNBR (Stored Procedure)

**Workato Action:** Oracle → Stored procedure → `GLD_SCHEMA.ACCUPDATECIUREFNBR`

| # | SP Parameter | DB Type | Workato Input Source |
|---|---|---|---|
| 1 | ACCCHECKREQUESTID | BIGINT | step1.accCheckRequestID |
| 2 | CIUREFNBR | VARCHAR2 | step3.CIURefNbr |

**Output:** None (void update).

---

### 4.5a logCheckReply → ACCLOGCHECKREPLY (TRUE path)

**Workato Action:** Oracle → Stored procedure → `GLD_SCHEMA.ACCLOGCHECKREPLY`

| # | SP Parameter | DB Type | Workato Input Source |
|---|---|---|---|
| 1 | CIUREFNBR | VARCHAR2 | step3.CIURefNbr |
| 2 | CHECKTYPE | VARCHAR2 | step3.CheckType (or static "COMPLIANCE") |
| 3 | RESULT | VARCHAR2 | "true" (literal — this is the success path) |

**Output:** None.

---

### 4.5b logCheckReplyError → ACCLOGCHECKREPLYERROR (ELSE / error paths)

**Workato Action:** Oracle → Stored procedure → `GLD_SCHEMA.ACCLOGCHECKREPLYERROR`

| # | SP Parameter | DB Type | Workato Input Source | Notes |
|---|---|---|---|---|
| 1 | ERRORTYPE | VARCHAR2 | step3.ErrorType OR error_monitor.error_type | CIU failure or system error |
| 2 | ERRORCODE | VARCHAR2 | step3.ErrorCode OR error_monitor.error_code | |
| 3 | ERRORDESC | VARCHAR2 | step3.ErrorDesc OR error_monitor.message | |
| 4 | CIUREFNBR | VARCHAR2 | step3.CIURefNbr (if available) | May be blank on system errors |

**Output:** None.

---

### 4.6 selectCustomerAndRequest → SELECT JOIN

**Workato Action:** Oracle → Custom SQL (SELECT)

```sql
SELECT DISTINCT
  t1.ACCCUSTOMERID, t1.CUSTOMERNBR, t1.CUSTOMERTYPE, t1.BUSINESSNAME,
  t1.FIRSTNAME, t1.MIDDLENAME, t1.LASTNAME,
  t1.ADDRESSLINE1, t1.ADDRESSLINE2, t1.ADDRESSLINE3, t1.ADDRESSLINE4,
  t1.CITY, t1.STATE, t1.ZIP, t1.COUNTRYCODE, t1.SSNTIN,
  t1.PARTYTYPE, t1.DOB,
  t2.ACCCHECKREQUESTID, t2.APPLICATIONNBR, t2.CHANNEL, t2.LOB,
  t2.PRODUCTCODE, t2.SUBPRODUCTCODE, t2.POSTBACK,
  t2.COMPLIANCEREPLYEMAIL, t2.CIUREFNBR, t2.REQUESTTIMESTAMP
FROM GLD_SCHEMA.ACCCUSTOMER t1
JOIN GLD_SCHEMA.ACCCHECKREQUEST t2
  ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID
WHERE t2.CIUREFNBR = ?
```

**Input:** `CIURefNbr` → step3.CIURefNbr

**Output (28 columns):**

| Column | DB Type | Workato Data Pill |
|---|---|---|
| ACCCUSTOMERID | NUMBER | step6.rows[0].ACCCUSTOMERID |
| CUSTOMERNBR | VARCHAR2 | step6.rows[0].CUSTOMERNBR |
| CUSTOMERTYPE | VARCHAR2 | step6.rows[0].CUSTOMERTYPE |
| BUSINESSNAME | VARCHAR2 | step6.rows[0].BUSINESSNAME |
| FIRSTNAME | VARCHAR2 | step6.rows[0].FIRSTNAME |
| MIDDLENAME | VARCHAR2 | step6.rows[0].MIDDLENAME |
| LASTNAME | VARCHAR2 | step6.rows[0].LASTNAME |
| ADDRESSLINE1 | VARCHAR2 | step6.rows[0].ADDRESSLINE1 |
| ADDRESSLINE2 | VARCHAR2 | step6.rows[0].ADDRESSLINE2 |
| ADDRESSLINE3 | VARCHAR2 | step6.rows[0].ADDRESSLINE3 |
| ADDRESSLINE4 | VARCHAR2 | step6.rows[0].ADDRESSLINE4 |
| CITY | VARCHAR2 | step6.rows[0].CITY |
| STATE | VARCHAR2 | step6.rows[0].STATE |
| ZIP | VARCHAR2 | step6.rows[0].ZIP |
| COUNTRYCODE | VARCHAR2 | step6.rows[0].COUNTRYCODE |
| SSNTIN | VARCHAR2 | step6.rows[0].SSNTIN |
| PARTYTYPE | VARCHAR2 | step6.rows[0].PARTYTYPE |
| DOB | DATE | step6.rows[0].DOB |
| ACCCHECKREQUESTID | NUMBER | step6.rows[0].ACCCHECKREQUESTID |
| APPLICATIONNBR | VARCHAR2 | step6.rows[0].APPLICATIONNBR |
| CHANNEL | VARCHAR2 | step6.rows[0].CHANNEL |
| LOB | VARCHAR2 | step6.rows[0].LOB |
| PRODUCTCODE | VARCHAR2 | step6.rows[0].PRODUCTCODE |
| SUBPRODUCTCODE | VARCHAR2 | step6.rows[0].SUBPRODUCTCODE |
| POSTBACK | VARCHAR2 | step6.rows[0].POSTBACK |
| COMPLIANCEREPLYEMAIL | VARCHAR2 | step6.rows[0].COMPLIANCEREPLYEMAIL |
| CIUREFNBR | VARCHAR2 | step6.rows[0].CIUREFNBR |
| REQUESTTIMESTAMP | TIMESTAMP | step6.rows[0].REQUESTTIMESTAMP |

---

### 4.7 purgeData → ACCPURGEDATA (Scheduled recipe)

**Workato Recipe:** Separate recipe with scheduled trigger (daily/weekly).

**Action:** Oracle → Stored procedure → `GLD_SCHEMA.ACCPURGEDATA`
**Input:** None.
**Output:** None.

---

## 5. Recipe Design

### 5.1 webMethods → Workato Construct Mapping

| # | webMethods | Workato Equivalent | Used In Recipe |
|---|---|---|---|
| 1 | Workflow | Recipe | Main recipe container |
| 2 | TRY | Error monitor (try block) | Wraps all 7 DB + HTTP steps |
| 3 | CATCH | on_error block | Calls ACCLOGCHECKREPLYERROR |
| 5 | IF | if/else conditional | CIU result check |
| 7 | ELSE | else clause | Error reply path |
| 20 | INVOKE (DB) | Oracle action | Steps 1, 2, 4, 5a, 5b, 6, 7 |
| 20 | INVOKE (HTTP) | HTTP action | Step 3 (CIU call) |
| 21 | MAP | Formula fields | Input field binding in each action |

Full 22-row mapping: see `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx`

### 5.2 Recipe Action Inventory (10 steps)

| Step | Workato Type | Label | Notes |
|---|---|---|---|
| Trigger | callable_recipe | HTTP POST — Compliance Check | Receives 25-field JSON |
| 1 | Oracle SP | Log Check Request | SP ACCLOGCHECKREQUEST, 25 IN params |
| 2 | Oracle SP | Log Check Request XML | SP LOGXMLREQUEST, 5 IN params |
| 3 | HTTP action | Call CIU System | Placeholder — wire endpoint URL |
| 4 | Oracle SP | Update CIU Reference | SP ACCUPDATECIUREFNBR, 2 IN params |
| 5 | IF/ELSE | Check CIU Result | Condition: CIUResult == "TRUE" |
| 5a | Oracle SP | Log Check Reply (TRUE) | SP ACCLOGCHECKREPLY, 3 IN params |
| 5b | Oracle SP | Log Check Reply Error (ELSE) | SP ACCLOGCHECKREPLYERROR, 4 IN params |
| 6 | Oracle SELECT | Select Customer and Request | SELECT JOIN, 1 IN, 28 OUT columns |
| catch | Oracle SP | Log Error (catch block) | SP ACCLOGCHECKREPLYERROR on system error |

---

## 6. Map Shape Field Mappings

Full field-level mapping: see `Workato/Workato_Map_Field_Mappings.xlsx`

**Sheet 1 — LogCheckRequest_Mapping:** 25 rows mapping trigger input JSON → ACCLOGCHECKREQUEST SP parameters
**Sheet 2 — SelectCustomer_Output:** 28 rows mapping SELECT output columns → Workato data pills
**Sheet 3 — Missing_Components:** 5 gap items with resolutions

---

## 7. Database Table Definitions

| Table | Schema | Role |
|---|---|---|
| `GLD_SCHEMA.ACCCHECKREQUEST` | GLD_SCHEMA | Stores compliance check requests; keyed on ACCCHECKREQUESTID |
| `GLD_SCHEMA.ACCCUSTOMER` | GLD_SCHEMA | Stores customer data; keyed on ACCCUSTOMERID |

Stored procedures write into these tables. The SELECT JOIN on step 6 reads from both via `t1.ACCCUSTOMERID = t2.ACCCUSTOMERID`.

---

## 8. Stored Procedures Summary

| # | Procedure | Schema | IN Params | OUT Params | Workato Step |
|---|---|---|---|---|---|
| 1 | ACCLOGCHECKREQUEST | GLD_SCHEMA | 25 | accCheckRequestID (BIGINT) | Step 1 |
| 2 | LOGXMLREQUEST | GLD_SCHEMA | 5 | None | Step 2 |
| 3 | ACCUPDATECIUREFNBR | GLD_SCHEMA | 2 | None | Step 4 |
| 4 | ACCLOGCHECKREPLY | GLD_SCHEMA | 3 | None | Step 5a |
| 5 | ACCLOGCHECKREPLYERROR | GLD_SCHEMA | 4 | None | Step 5b / catch |
| 6 | ACCPURGEDATA | GLD_SCHEMA | 0 | None | Separate scheduled recipe |

---

## 9. Migration Gaps

| # | Gap | Severity | Impact | Resolution |
|---|---|---|---|---|
| 1 | CIU endpoint URL unknown | Critical | Step 3 (HTTP action) cannot be wired | Obtain from SME |
| 2 | Oracle DB credentials | Critical | Connection cannot be authorized | Retrieve GLD_SCHEMA password from IS Admin / CyberArk |
| 3 | accCheckRequestID OUT param not returned by Standard Insert | High | Cannot get request ID from step 1 directly | Run SELECT after INSERT: `SELECT MAX(ACCCHECKREQUESTID) FROM ACCCHECKREQUEST WHERE REQUESTORSYSTEMREQUESTID=?` |
| 4 | CIU result field mapping | High | Unknown how CIU sets CHECK_RESULT | Add formula in recipe: HTTP 200 → "TRUE", otherwise "FALSE" |
| 5 | No trigger source in flow.xml | Medium | Unknown what fires the workflow | Use callable recipe (HTTP POST); clients must call the Workato recipe URL |
| 6 | Oracle SID: ORASHRT4 vs ILMSUM conflict | Medium | Two different SID values appear across files | Analysis file shows ILMSUM; confirm with DBA which is correct |

---

## 10. Files Referenced

| File | Location | Purpose |
|---|---|---|
| `GLDComplianceAdapterEnv_Analysis.md` | `WebMethods/Analysis/` | Connection alias details (ExpressOS) |
| `GLDComplianceAdapterServices_Analysis.md` | `WebMethods/Analysis/` | All 7 service definitions |
| `Agent Bridge Web Methods to Workato Component Mapping.xlsx` | `WebMethods/` | 22-row webMethods → Workato construct map |
| `Workato_Map_Field_Mappings.xlsx` | `Workato/` | Field-level input/output mapping + gap log |
| `Workato.md` | `WebMethods/MD/` | Full build reference (Step 10 output) |
| `manifest.v3` | `GLDComplianceAdapterEnv/` | Package metadata |
| `ExpressOS/node.ndf` | `GLDComplianceAdapterEnv/ns/` | JDBC connection alias definition |
| `*.node.ndf` | `GLDComplianceAdapterServices/ns/` | 7 adapter service definitions |
