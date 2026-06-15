# Boomi.md — GLDComplianceAdapterServices Build Reference

> **Purpose:** Authoritative specification for building all 18 Boomi components in the
> `MIG_gld_compliance` folder (folderId `Rjo4NjIxNDk3`).
> Generated from: `PackageAnalysis.md` + `Agent Bridge Web Methods to Boomi Component Mapping.xlsx` +
> `Boomi Map To Test Skill.xlsx`.

---

## 1. Component Inventory

| # | Component Name | Boomi Type | Priority | Notes |
|---|---|---|---|---|
| 1 | MIG_WM_GLD_DB_Connection | connector-settings | EXISTING — reuse ID `370bf544-60a9-4048-8197-0c442243571d` | |
| 2 | MIG_WM_GLD_MapTest_Source_Profile | profile.json | STEP 8 — create first | A1-A5 test fields |
| 3 | MIG_WM_GLD_MapTest_Target_Profile | profile.json | STEP 8 — create second | B1-B5 test fields |
| 4 | MIG_WM_GLD_MapTestSkill_Map | transform.map | STEP 8 — after profiles | Needs profile IDs from above |
| 5 | MIG_WM_GLD_LogCheckRequest_Operation | connector-action | STEP 13 | SP: ACCLOGCHECKREQUEST, 25 IN + 1 OUT |
| 6 | MIG_WM_GLD_LogCheckRequestXML_Operation | connector-action | STEP 13 | SP: LOGXMLREQUEST, 5 IN |
| 7 | MIG_WM_GLD_LogCheckReply_Operation | connector-action | STEP 13 | SP: ACCLOGCHECKREPLY, 3 IN |
| 8 | MIG_WM_GLD_LogCheckReplyError_Operation | connector-action | STEP 13 | SP: ACCLOGCHECKREPLYERROR, 4 IN |
| 9 | MIG_WM_GLD_SelectCustomerRequest_Operation | connector-action | STEP 13 | SELECT JOIN, 1 IN, 28 OUT fields |
| 10 | MIG_WM_GLD_UpdateCIURefNbr_Operation | connector-action | STEP 13 | SP: ACCUPDATECIUREFNBR, 2 IN |
| 11 | MIG_WM_GLD_PurgeData_Operation | connector-action | STEP 13 | SP: ACCPURGEDATA, no params |
| 12 | MIG_WM_GLDComplianceAdapterServices_Process | process | STEP 13 — last | Needs all operation IDs above |

---

## 2. Step 8 — Map Test (Boomi Map To Test Skill.xlsx)

### Source Profile: MIG_WM_GLD_MapTest_Source_Profile

Fields from column A of the Excel:

| Key | Field Name | Type | Mappable |
|---|---|---|---|
| 1 | root (JSONRootValue) | — | false |
| 2 | payload (JSONObjectValue) | — | false |
| 3 | A1 | character | true |
| 4 | A2 | character | true |
| 5 | A3 | character | true |
| 6 | A4 | character | true |
| 7 | A5 | character | true |

### Target Profile: MIG_WM_GLD_MapTest_Target_Profile

Fields from column B of the Excel:

| Key | Field Name | Type | Mappable |
|---|---|---|---|
| 1 | root (JSONRootValue) | — | false |
| 2 | payload (JSONObjectValue) | — | false |
| 3 | B1 | character | true |
| 4 | B2 | character | true |
| 5 | B3 | character | true |
| 6 | B4 | character | true |
| 7 | B5 | character | true |

### Map: MIG_WM_GLD_MapTestSkill_Map

| Excel Instruction | Source Key | Transformation | Target Key |
|---|---|---|---|
| A1 → Default to 2000 → B1 | — | Default value `2000` | 3 (B1) |
| A2 → If A2="Config" → "Yes" Else "False" | 4 (A2) | Groovy function `fn1` | 4 (B2) |
| A3 → Direct Mapping | 5 (A3) | Direct copy | 5 (B3) |
| A4 → Convert String to Integer | 6 (A4) | Groovy function `fn2` | 6 (B4) |
| A5 → No Mapping | 7 (A5) | None (unmapped) | — |

**Groovy function fn1 (A2 conditional):**
```groovy
if (inputs[0] == "Config") return "Yes"
return "False"
```

**Groovy function fn2 (A4 String→Integer):**
```groovy
def s = inputs[0] ?: "0"
return Integer.parseInt(s.trim()).toString()
```

---

## 3. Step 13 — DB Operations

### Connection Reference
- **Name:** MIG_WM_GLD_DB_Connection
- **ID:** `370bf544-60a9-4048-8197-0c442243571d`
- **JDBC URL:** `jdbc:oracle:thin:@CSC06DSHORA1S:1522:ILMSUM`
- **Driver:** `oracle.jdbc.OracleDriver`
- **Schema:** `GLD_SCHEMA`

### Operations SQL

#### logCheckRequest (Standard Insert)
```sql
{call GLD_SCHEMA.ACCLOGCHECKREQUEST(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}
```
Param order (25): CUSTOMERNBR, CUSTOMERTYPE, PARTYTYPE, BUSINESSNAME, APPLICATIONNBR, CHANNEL, LOB, PRODUCTCODE, SUBPRODUCTCODE, POSTBACK, COMPLIANCEREPLYEMAIL, FIRSTNAME, MIDDLENAME, LASTNAME, ADDRESSLINE1, ADDRESSLINE2, ADDRESSLINE3, ADDRESSLINE4, CITY, STATE, ZIP, COUNTRYCODE, SSNTIN, DOB, REQUESTORSYSTEMREQUESTID
> OUT param ACCCHECKREQUESTID — not capturable via Standard Insert; use subsequent SELECT for ID if needed.

#### logCheckRequestXML (Standard Insert)
```sql
{call GLD_SCHEMA.LOGXMLREQUEST(?,?,?,?,?)}
```
Param order (5): APPLICATIONID, REQUEST, REQUESTIDENTIFIER1, REQUESTIDENTIFIER2, REQUESTIDENTIFIER3

#### logCheckReply (Standard Insert)
```sql
{call GLD_SCHEMA.ACCLOGCHECKREPLY(?,?,?)}
```
Param order (3): CIUREFNBR, CHECKTYPE, RESULT

#### logCheckReplyError (Standard Insert)
```sql
{call GLD_SCHEMA.ACCLOGCHECKREPLYERROR(?,?,?,?)}
```
Param order (4): ERRORTYPE, ERRORCODE, ERRORDESC, CIUREFNBR

#### selectCustomerAndRequest (Standard Get)
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
Param: DPP_CIU_REF_NBR

#### updateCIURefNbr (Standard Insert)
```sql
{call GLD_SCHEMA.ACCUPDATECIUREFNBR(?,?)}
```
Param order (2): ACCCHECKREQUESTID, CIUREFNBR

#### purgeData (Standard Insert, no params)
```sql
{call GLD_SCHEMA.ACCPURGEDATA()}
```
No input parameters.

---

## 4. Step 13 — Process Design

### webMethods → Boomi Construct Mapping (from Agent Bridge Excel)

| # | webMethods | Boomi Shape | Used In Process |
|---|---|---|---|
| 1 | Workflow | Process Start shape | shape1 — Start (passthrough) |
| 2 | TRY | Try/Catch (try path) | shape3 — catcherrors (catchAll=true) |
| 3 | CATCH | Try/Catch (catch path) | shape3 catch dragpoint |
| 5 | IF | Decision | shape15 — Decision on DPP_CHECK_RESULT |
| 7 | ELSE | Decision false path | shape19 (logCheckReplyError path) |
| 20 | INVOKE | DB Connector step | shape5,8,11,13,17,20 |
| 21 | MAP | Map shape | shape4 (Set Properties), shape14 (Map result) |

### Shape Inventory (23 shapes)

| Shape | Type | Label | x | y | Notes |
|---|---|---|---|---|---|
| shape1 | Start | Start | 48 | 48 | Passthrough |
| shape2 | documentproperties | Extract Input DDPs | 208 | 48 | Set 21 DDPs from input JSON |
| shape3 | catcherrors | Try/Catch | 368 | 48 | catchAll=true |
| shape4 | message | Build logCheckRequest Input | 528 | 48 | JSON with 25 DDP values |
| shape5 | connectoraction | LogCheckRequest | 688 | 48 | logCheckRequest operation |
| shape6 | documentproperties | Capture Request ID | 848 | 48 | Note: OUT param not auto-captured |
| shape7 | message | Build logCheckRequestXML Input | 1008 | 48 | JSON with 5 values |
| shape8 | connectoraction | LogCheckRequestXML | 1168 | 48 | logCheckRequestXML operation |
| shape9 | documentproperties | Set CIU Placeholder | 1328 | 48 | Placeholder — wire CIU connector here |
| shape10 | message | Build UpdateCIURefNbr Input | 1488 | 48 | JSON with 2 values |
| shape11 | connectoraction | UpdateCIURefNbr | 1648 | 48 | updateCIURefNbr operation |
| shape12 | message | Build SelectCustomer Input | 1808 | 48 | JSON with DPP_CIU_REF_NBR |
| shape13 | connectoraction | SelectCustomerAndRequest | 1968 | 48 | selectCustomerAndRequest operation |
| shape14 | map | Map Result to DDPs | 2128 | 48 | Map component (from Map Test) |
| shape15 | decision | Check Passed? | 2288 | 48 | DPP_CHECK_RESULT == "TRUE" |
| shape16 | message | Build LogCheckReply Input | 2448 | 48 | TRUE path |
| shape17 | connectoraction | LogCheckReply | 2608 | 48 | logCheckReply operation |
| shape18 | stop | Success | 2768 | 48 | continue=true |
| shape19 | message | Build LogCheckReplyError Input | 2448 | 248 | FALSE path |
| shape20 | connectoraction | LogCheckReplyError | 2608 | 248 | logCheckReplyError operation |
| shape21 | stop | Fail | 2768 | 248 | continue=false |
| shape22 | notify | Log Error | 528 | 248 | CATCH path |
| shape23 | stop | Error | 688 | 248 | continue=false |

### Process DDP Definitions (26 total)

| DDP | Source | Value Type |
|---|---|---|
| DPP_CUSTOMER_NBR | input JSON field CustomerNbr | profile |
| DPP_CUSTOMER_TYPE | input JSON field CustomerType | profile |
| DPP_PARTY_TYPE | input JSON field PartyType | profile |
| DPP_BUSINESS_NAME | input JSON field Businessname | profile |
| DPP_APPLICATION_NBR | input JSON field ApplicationNbr | profile |
| DPP_CHANNEL | input JSON field Channel | profile |
| DPP_LOB | input JSON field LOB | profile |
| DPP_PRODUCT_CODE | input JSON field ProductCode | profile |
| DPP_SUB_PRODUCT_CODE | input JSON field SubProductCode | profile |
| DPP_POSTBACK | input JSON field PostBack | profile |
| DPP_COMPLIANCE_REPLY_EMAIL | input JSON field ComplianceReplyEmail | profile |
| DPP_FIRST_NAME | input JSON field FirstName | profile |
| DPP_MIDDLE_NAME | input JSON field MiddleName | profile |
| DPP_LAST_NAME | input JSON field LastName | profile |
| DPP_ADDRESS_LINE1 | input JSON field AddressLine1 | profile |
| DPP_STATE | input JSON field State | profile |
| DPP_ZIP | input JSON field Zip | profile |
| DPP_COUNTRY_CODE | input JSON field CountryCode | profile |
| DPP_SSNTIN | input JSON field SSNTIN | profile |
| DPP_DOB | input JSON field DOB | profile |
| DPP_REQUESTOR_SYSTEM_REQUEST_ID | input JSON field RequestorSystemRequestID | profile |
| DPP_ACC_CHECK_REQUEST_ID | Static placeholder (wire after CIU step) | static |
| DPP_CIU_REF_NBR | Static placeholder (wire after CIU step) | static |
| DPP_CHECK_RESULT | Static placeholder (wire after CIU step) | static |
| DPP_ERROR_TYPE | Error path | static |
| DPP_ERROR_DESC | Error path | static |

### Process Flow Connections

| From | To | Dragpoint |
|---|---|---|
| shape1 | shape2 | — |
| shape2 | shape3 | — |
| shape3 | shape4 | default (TRY) |
| shape3 | shape22 | error (CATCH) |
| shape4 | shape5 | — |
| shape5 | shape6 | — |
| shape6 | shape7 | — |
| shape7 | shape8 | — |
| shape8 | shape9 | — |
| shape9 | shape10 | — |
| shape10 | shape11 | — |
| shape11 | shape12 | — |
| shape12 | shape13 | — |
| shape13 | shape14 | — |
| shape14 | shape15 | — |
| shape15 | shape16 | true |
| shape15 | shape19 | false |
| shape16 | shape17 | — |
| shape17 | shape18 | — |
| shape19 | shape20 | — |
| shape20 | shape21 | — |
| shape22 | shape23 | — |

---

## 5. Post-Build Manual Steps

| # | Step | Shape |
|---|---|---|
| 1 | Change shape1 Start from Passthrough to WSS Listener or scheduled trigger | shape1 |
| 2 | Replace shape9 Set Properties placeholder with actual CIU HTTP/REST connector call | shape9 |
| 3 | After CIU call, set DPP_ACC_CHECK_REQUEST_ID from logCheckRequest response | shape6 |
| 4 | After CIU call, set DPP_CIU_REF_NBR from CIU response | shape9 |
| 5 | Set DB password in Environment Extensions (GLD_SCHEMA user) | DB Connection |
| 6 | Verify `{call GLD_SCHEMA.PROCEDURE_NAME(?)}` syntax with DBA for Oracle version | All SP operations |
| 7 | Enable PII guard: set enableUserLog="false" on process | Process settings |
