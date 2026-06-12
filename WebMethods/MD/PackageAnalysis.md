# PackageAnalysis — GLDComplianceAdapterServices → Boomi Migration Reference

> **Purpose:** This document is the authoritative reference for creating every Boomi component that corresponds to the `GLDComplianceAdapterServices` webMethods package. Every connection, operation, process shape, field mapping, and data type required to reproduce this package's behaviour in Boomi is captured here.

---

## 1. Source Package Summary

| Property | Value |
|---|---|
| Package Name | GLDComplianceAdapterServices |
| Platform | webMethods Integration Server 6.5 |
| Publisher | cwb02dwmis02.keybank.com |
| Build Date | 2008-06-26 |
| Component Type | JDBC Adapter Service package (7 adapter services) |
| DB Adapter | JDBCAdapter → Oracle 10g |
| DB Host | CSC06DSHORA1S:1522/ILMSUM |
| DB Schema | GLD_SCHEMA |
| Connection Alias | GLDComplianceAdapterEnv:ExpressOS |

---

## 2. Boomi Component Plan

### 2.1 Components to Create

| # | Boomi Component | Type | Notes |
|---|---|---|---|
| 1 | MIG_WM_GLD_DB_Connection | connector-settings (DatabaseV2) | One shared connection for all 7 services |
| 2 | MIG_WM_GLD_LogCheckRequest_Operation | connector-action (DatabaseV2) | Maps logCheckRequest SP |
| 3 | MIG_WM_GLD_LogCheckRequestXML_Operation | connector-action (DatabaseV2) | Maps logCheckRequestXML SP |
| 4 | MIG_WM_GLD_LogCheckReply_Operation | connector-action (DatabaseV2) | Maps logCheckReply SP |
| 5 | MIG_WM_GLD_LogCheckReplyError_Operation | connector-action (DatabaseV2) | Maps logCheckReplyError SP |
| 6 | MIG_WM_GLD_SelectCustomerAndRequest_Operation | connector-action (DatabaseV2) | Maps selectCustomerAndRequest SELECT JOIN |
| 7 | MIG_WM_GLD_UpdateCIURefNbr_Operation | connector-action (DatabaseV2) | Maps updateCIURefNbr SP |
| 8 | MIG_WM_GLD_PurgeData_Operation | connector-action (DatabaseV2) | Maps purgeData SP |
| 9 | MIG_WM_GLDComplianceAdapterServices_Process | process | Orchestrates the full compliance check flow |

---

## 3. Boomi Connection Component

**Component Name:** `MIG_WM_GLD_DB_Connection`  
**Connector Type:** `officialboomi-X3979C-dbv2da-prod` (DatabaseV2)

```xml
<GenericConnectionConfig>
  <field id="url"        type="string"  value="jdbc:oracle:thin:@CSC06DSHORA1S:1522:ILMSUM"/>
  <field id="className"  type="string"  value="oracle.jdbc.OracleDriver"/>
  <field id="username"   type="string"  value="GLD_SCHEMA"/>
  <field id="password"   type="password" value=""/>
  <field id="schemaName" type="string"  value="GLD_SCHEMA"/>
  <field id="enablePooling"       type="boolean" value="true"/>
  <field id="maximumConnections"  type="integer" value="10"/>
  <field id="minimumConnections"  type="integer" value="1"/>
  <field id="validationQuery"     type="string"  value="SELECT 1 FROM DUAL"/>
</GenericConnectionConfig>
```

> **Security:** Set `GLD_SCHEMA` password via Boomi Environment Extensions — never hardcode in XML.

---

## 4. Boomi Operation Components

### Operation 1: MIG_WM_GLD_LogCheckRequest_Operation
**Source Service:** `logCheckRequest`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.ACCLOGCHECKREQUEST`  
**Boomi Operation Type:** `EXECUTE` (Stored Procedure)

**Input Parameters (IN):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| CUSTOMERNBR | VARCHAR2(18) | String | CustomerNbr |
| CUSTOMERTYPE | VARCHAR2(3) | String | CustomerType |
| PARTYTYPE | VARCHAR2(20) | String | PartyType |
| BUSINESSNAME | VARCHAR2(40) | String | Businessname |
| APPLICATIONNBR | VARCHAR2(18) | String | ApplicationNbr |
| CHANNEL | VARCHAR2(10) | String | Channel |
| LOB | VARCHAR2(10) | String | LOB |
| PRODUCTCODE | VARCHAR2(10) | String | ProductCode |
| SUBPRODUCTCODE | VARCHAR2(10) | String | SubProductCode |
| POSTBACK | VARCHAR2(200) | String | PostBack |
| COMPLIANCEREPLYEMAIL | VARCHAR2(75) | String | ComplianceReplyEmail |
| FIRSTNAME | VARCHAR2(20) | String | FirstName |
| MIDDLENAME | VARCHAR2(20) | String | MiddleName |
| LASTNAME | VARCHAR2(20) | String | LastName |
| ADDRESSLINE1 | VARCHAR2(40) | String | AddressLine1 |
| ADDRESSLINE2 | VARCHAR2(40) | String | AddressLine2 |
| ADDRESSLINE3 | VARCHAR2(40) | String | AddressLine3 |
| ADDRESSLINE4 | VARCHAR2(40) | String | AddressLine4 |
| CITY | VARCHAR2(20) | String | City |
| STATE | VARCHAR2(2) | String | State |
| ZIP | VARCHAR2(10) | String | Zip |
| COUNTRYCODE | VARCHAR2(3) | String | CountryCode |
| SSNTIN | VARCHAR2(9) | String | SSNTIN |
| DOB | DATE | String | DOB |
| REQUESTORSYSTEMREQUESTID | BIGINT | Long | RequestorSystemRequestID |

**Output Parameters (OUT):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| ACCCHECKREQUESTID | BIGINT | Long | accCheckRequestID |

---

### Operation 2: MIG_WM_GLD_LogCheckRequestXML_Operation
**Source Service:** `logCheckRequestXML`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.LOGXMLREQUEST`  
**Boomi Operation Type:** `EXECUTE`

**Input Parameters (IN):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| APPLICATIONID | BIGINT | Long | ApplicationID |
| REQUEST | LONGVARCHAR (CLOB) | Object | Request (raw XML string) |
| REQUESTIDENTIFIER1 | VARCHAR2 | String | RequestIdentifier1 |
| REQUESTIDENTIFIER2 | VARCHAR2 | String | RequestIdentifier2 |
| REQUESTIDENTIFIER3 | VARCHAR2 | String | RequestIdentifier3 |

**Output:** None (void stored procedure).

---

### Operation 3: MIG_WM_GLD_LogCheckReply_Operation
**Source Service:** `logCheckReply`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.ACCLOGCHECKREPLY`  
**Boomi Operation Type:** `EXECUTE`

**Input Parameters (IN):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| CIUREFNBR | VARCHAR2 | String | CIURefNbr |
| CHECKTYPE | VARCHAR2 | String | CheckType |
| RESULT | VARCHAR2 | Boolean (mapped to 'TRUE'/'FALSE') | Result |

**Output:** None.

---

### Operation 4: MIG_WM_GLD_LogCheckReplyError_Operation
**Source Service:** `logCheckReplyError`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.ACCLOGCHECKREPLYERROR`  
**Boomi Operation Type:** `EXECUTE`

**Input Parameters (IN):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| ERRORTYPE | VARCHAR2 | String | ErrorType |
| ERRORCODE | VARCHAR2 | String | ErrorCode |
| ERRORDESC | VARCHAR2 | String | ErrorDesc |
| CIUREFNBR | VARCHAR2 | String | CIURefNbr |

**Output:** None.

---

### Operation 5: MIG_WM_GLD_SelectCustomerAndRequest_Operation
**Source Service:** `selectCustomerAndRequest`  
**DB Action:** SELECT JOIN  
**Boomi Operation Type:** `GET` (SELECT)

**SQL:**
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

**Input Parameter:**
| Param | Type | Source |
|---|---|---|
| ? (CIUREFNBR) | VARCHAR2 | Dynamic Document Property: DPP_CIU_REF_NBR |

**Output Profile (JSON):**
```json
{
  "results": [
    {
      "ACCCUSTOMERID": "BigDecimal",
      "CUSTOMERNBR": "String",
      "CUSTOMERTYPE": "String",
      "BUSINESSNAME": "String",
      "FIRSTNAME": "String",
      "MIDDLENAME": "String",
      "LASTNAME": "String",
      "ADDRESSLINE1": "String",
      "ADDRESSLINE2": "String",
      "ADDRESSLINE3": "String",
      "ADDRESSLINE4": "String",
      "CITY": "String",
      "STATE": "String",
      "ZIP": "String",
      "COUNTRYCODE": "String",
      "SSNTIN": "String",
      "PARTYTYPE": "String",
      "DOB": "Timestamp",
      "ACCCHECKREQUESTID": "BigDecimal",
      "APPLICATIONNBR": "String",
      "CHANNEL": "String",
      "LOB": "String",
      "PRODUCTCODE": "String",
      "SUBPRODUCTCODE": "String",
      "POSTBACK": "String",
      "COMPLIANCEREPLYEMAIL": "String",
      "CIUREFNBR": "String",
      "REQUESTTIMESTAMP": "Timestamp"
    }
  ]
}
```

---

### Operation 6: MIG_WM_GLD_UpdateCIURefNbr_Operation
**Source Service:** `updateCIURefNbr`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.ACCUPDATECIUREFNBR`  
**Boomi Operation Type:** `EXECUTE`

**Input Parameters (IN):**
| Parameter | DB Type | Java Mapping | wM Field |
|---|---|---|---|
| ACCCHECKREQUESTID | BIGINT | Long | accCheckRequestID |
| CIUREFNBR | VARCHAR2 | String | CIURefNbr |

**Output:** None.

---

### Operation 7: MIG_WM_GLD_PurgeData_Operation
**Source Service:** `purgeData`  
**DB Action:** Stored Procedure — `GLD_SCHEMA.ACCPURGEDATA`  
**Boomi Operation Type:** `EXECUTE`

**Input Parameters:** None.  
**Output:** None.

---

## 5. Process Design — MIG_WM_GLDComplianceAdapterServices_Process

### Flow Logic

The compliance adapter services follow this sequence when a compliance check is initiated:

```
START (WSS listener or scheduled trigger)
  │
  ├─ shape: Set Properties → extract incoming request fields into DDPs
  │         DPP_CUSTOMER_NBR, DPP_CUSTOMER_TYPE, DPP_FIRST_NAME, ...
  │
  ├─ shape: DB EXECUTE → logCheckRequest
  │         IN:  all customer fields from DDPs
  │         OUT: DPP_ACC_CHECK_REQUEST_ID
  │
  ├─ shape: DB EXECUTE → logCheckRequestXML
  │         IN:  DPP_APPLICATION_ID, raw XML document, identifiers
  │         OUT: (void)
  │
  ├─ shape: [HTTP/REST Connector] → External CIU Compliance System
  │         Sends compliance check request; receives CIU reference number
  │         OUT: DPP_CIU_REF_NBR
  │
  ├─ shape: DB EXECUTE → updateCIURefNbr
  │         IN:  DPP_ACC_CHECK_REQUEST_ID, DPP_CIU_REF_NBR
  │
  ├─ [Wait / callback — CIU sends reply asynchronously]
  │
  ├─ shape: DB GET → selectCustomerAndRequest
  │         IN:  DPP_CIU_REF_NBR
  │         OUT: results[] array with full customer + request context
  │
  ├─ shape: Decision → "Did check pass?"
  │   ├─ TRUE path:
  │   │    shape: DB EXECUTE → logCheckReply
  │   │           IN:  DPP_CIU_REF_NBR, CheckType, Result=TRUE
  │   │    shape: Stop (success)
  │   │
  │   └─ FALSE / ERROR path:
  │        shape: DB EXECUTE → logCheckReplyError
  │               IN:  ErrorType, ErrorCode, ErrorDesc, DPP_CIU_REF_NBR
  │        shape: Stop (continue=false)
  │
  └─ [Maintenance / scheduled path]
       shape: DB EXECUTE → purgeData  (no inputs)
       shape: Stop
```

### Dynamic Document Properties (DDPs)

| DDP Name | Type | Source Service | Purpose |
|---|---|---|---|
| DPP_CUSTOMER_NBR | String | Input | Customer number |
| DPP_CUSTOMER_TYPE | String | Input | Customer type |
| DPP_FIRST_NAME | String | Input | First name |
| DPP_LAST_NAME | String | Input | Last name |
| DPP_MIDDLE_NAME | String | Input | Middle name |
| DPP_BUSINESS_NAME | String | Input | Business name |
| DPP_APPLICATION_NBR | String | Input | Application number |
| DPP_CHANNEL | String | Input | Channel |
| DPP_LOB | String | Input | Line of business |
| DPP_PRODUCT_CODE | String | Input | Product code |
| DPP_SUB_PRODUCT_CODE | String | Input | Sub-product code |
| DPP_POSTBACK | String | Input | Post-back |
| DPP_COMPLIANCE_REPLY_EMAIL | String | Input | Reply email |
| DPP_ADDRESS_LINE1 | String | Input | Address line 1 |
| DPP_CITY | String | Input | City |
| DPP_STATE | String | Input | State |
| DPP_ZIP | String | Input | ZIP |
| DPP_COUNTRY_CODE | String | Input | Country code |
| DPP_SSNTIN | String | Input | SSN/TIN |
| DPP_DOB | String | Input | Date of birth |
| DPP_REQUESTOR_SYSTEM_REQUEST_ID | Long | Input | Requestor's request ID |
| DPP_ACC_CHECK_REQUEST_ID | Long | logCheckRequest OUT | Internal request ID |
| DPP_CIU_REF_NBR | String | CIU system response | CIU reference number |
| DPP_CHECK_RESULT | Boolean | CIU response | Pass/fail result |
| DPP_ERROR_TYPE | String | Error path | Error type |
| DPP_ERROR_CODE | String | Error path | Error code |
| DPP_ERROR_DESC | String | Error path | Error description |

---

## 6. Map Shape Field Mappings

The Map shape connecting the input document to `logCheckRequest` parameters:

| Source (Pipeline In) | Transformation | Target (Pipeline Out) | Data Type | Notes |
|---|---|---|---|---|
| request/CustomerNbr | Direct copy | DPP_CUSTOMER_NBR | String | |
| request/CustomerType | Direct copy | DPP_CUSTOMER_TYPE | String | |
| request/PartyType | Direct copy | DPP_PARTY_TYPE | String | |
| request/Businessname | Direct copy | DPP_BUSINESS_NAME | String | |
| request/ApplicationNbr | Direct copy | DPP_APPLICATION_NBR | String | |
| request/Channel | Direct copy | DPP_CHANNEL | String | |
| request/LOB | Direct copy | DPP_LOB | String | |
| request/ProductCode | Direct copy | DPP_PRODUCT_CODE | String | |
| request/SubProductCode | Direct copy | DPP_SUB_PRODUCT_CODE | String | |
| request/PostBack | Direct copy | DPP_POSTBACK | String | |
| request/ComplianceReplyEmail | Direct copy | DPP_COMPLIANCE_REPLY_EMAIL | String | |
| request/FirstName | Direct copy | DPP_FIRST_NAME | String | |
| request/MiddleName | Direct copy | DPP_MIDDLE_NAME | String | |
| request/LastName | Direct copy | DPP_LAST_NAME | String | |
| request/AddressLine1 | Direct copy | DPP_ADDRESS_LINE1 | String | |
| request/AddressLine2 | Direct copy | DPP_ADDRESS_LINE2 | String | |
| request/AddressLine3 | Direct copy | DPP_ADDRESS_LINE3 | String | |
| request/AddressLine4 | Direct copy | DPP_ADDRESS_LINE4 | String | |
| request/City | Direct copy | DPP_CITY | String | |
| request/State | Direct copy | DPP_STATE | String | 2-char |
| request/Zip | Direct copy | DPP_ZIP | String | |
| request/CountryCode | Direct copy | DPP_COUNTRY_CODE | String | 3-char |
| request/SSNTIN | Direct copy | DPP_SSNTIN | String | Sensitive PII |
| request/DOB | Date format: yyyy-MM-dd → Oracle DATE | DPP_DOB | String/DATE | |
| request/RequestorSystemRequestID | Convert String→Long | DPP_REQUESTOR_SYSTEM_REQUEST_ID | Long | |
| selectCustomerAndRequest/results[0]/ACCCHECKREQUESTID | Direct copy | DPP_ACC_CHECK_REQUEST_ID | Long | Output of logCheckRequest; also returned by SELECT |
| CIU response/CIURefNbr | Direct copy | DPP_CIU_REF_NBR | String | Set after external CIU call |

---

## 7. Database Table Definitions (Inferred from Adapter Metadata)

### GLD_SCHEMA.ACCCUSTOMER (t1)
| Column | Type | Constraints | Notes |
|---|---|---|---|
| ACCCUSTOMERID | NUMBER(12) | NOT NULL, PK | Internal customer ID |
| CUSTOMERNBR | VARCHAR2(18) | NOT NULL | Customer number |
| CUSTOMERTYPE | VARCHAR2(3) | NOT NULL | Customer type |
| BUSINESSNAME | VARCHAR2(40) | | Business name |
| FIRSTNAME | VARCHAR2(20) | | First name |
| MIDDLENAME | VARCHAR2(20) | | Middle name |
| LASTNAME | VARCHAR2(20) | | Last name |
| ADDRESSLINE1 | VARCHAR2(40) | | Address line 1 |
| ADDRESSLINE2 | VARCHAR2(40) | | Address line 2 |
| ADDRESSLINE3 | VARCHAR2(40) | | Address line 3 |
| ADDRESSLINE4 | VARCHAR2(40) | | Address line 4 |
| CITY | VARCHAR2(20) | | City |
| STATE | VARCHAR2(2) | | State |
| ZIP | VARCHAR2(10) | | ZIP |
| COUNTRYCODE | VARCHAR2(3) | | Country code |
| SSNTIN | VARCHAR2(9) | | SSN / TIN |
| PARTYTYPE | VARCHAR2(20) | NOT NULL | Party type |
| DOB | DATE | | Date of birth |

### GLD_SCHEMA.ACCCHECKREQUEST (t2)
| Column | Type | Constraints | Notes |
|---|---|---|---|
| ACCCHECKREQUESTID | NUMBER(12) | NOT NULL, PK | Request ID (auto-generated) |
| ACCCUSTOMERID | NUMBER(12) | NOT NULL, FK | FK → ACCCUSTOMER |
| APPLICATIONNBR | VARCHAR2(18) | NOT NULL | Application number |
| CHANNEL | VARCHAR2(10) | NOT NULL | Channel |
| LOB | VARCHAR2(10) | NOT NULL | Line of business |
| PRODUCTCODE | VARCHAR2(10) | NOT NULL | Product code |
| SUBPRODUCTCODE | VARCHAR2(10) | NOT NULL | Sub-product code |
| POSTBACK | VARCHAR2(200) | NOT NULL | Post-back value |
| COMPLIANCEREPLYEMAIL | VARCHAR2(75) | NOT NULL | Reply email |
| CIUREFNBR | VARCHAR2(20) | | CIU reference (set after external call) |
| REQUESTTIMESTAMP | TIMESTAMP(6) | NOT NULL | When request was created |

---

## 8. Stored Procedures Summary

| Procedure Name | Schema | Action | Key Parameters |
|---|---|---|---|
| ACCLOGCHECKREQUEST | GLD_SCHEMA | INSERT into ACCCHECKREQUEST + ACCCUSTOMER | All 25 customer/request fields IN; ACCCHECKREQUESTID OUT |
| LOGXMLREQUEST | GLD_SCHEMA | INSERT raw XML log | ApplicationID, Request (CLOB), 3 identifiers |
| ACCLOGCHECKREPLY | GLD_SCHEMA | INSERT/UPDATE reply log | CIURefNbr, CheckType, Result |
| ACCLOGCHECKREPLYERROR | GLD_SCHEMA | INSERT error log | ErrorType, ErrorCode, ErrorDesc, CIURefNbr |
| ACCUPDATECIUREFNBR | GLD_SCHEMA | UPDATE ACCCHECKREQUEST.CIUREFNBR | ACCCHECKREQUESTID, CIURefNbr |
| ACCPURGEDATA | GLD_SCHEMA | DELETE old records | No params (uses internal date threshold) |

---

## 9. Migration Gaps

| Gap | Impact | Resolution |
|---|---|---|
| Stored procedure bodies not available | Cannot fully replicate SP logic in Boomi | Use DatabaseV2 `EXECUTE` with procedure name — SP runs server-side on Oracle |
| External CIU system endpoint unknown | Cannot build HTTP/REST connector without endpoint URL | Ask for CIU service WSDL or REST URL |
| ACCCUSTOMER/ACCCHECKREQUEST schema not available as DDL | Table definitions inferred from adapter metadata | Use inferred definitions; verify with DBA before going live |
| purgeData has no input params | Date threshold is internal to SP | No change needed — just call with no inputs |
| Boolean `Result` field in logCheckReply | Oracle procedure expects VARCHAR2; Java sends Boolean | Map true→'TRUE' / false→'FALSE' in Boomi Set Properties before calling DB operation |
| DOB date format | Oracle expects DATE; source has String | Add date format function in Boomi Map: input mask `yyyy-MM-dd`, output mask Oracle DATE |
| SSNTIN is PII | Must be masked in logs | Set `enableUserLog="false"` on process; never log raw SSNTIN in Notify shapes |

---

## 10. Files Referenced

| File | Location | Purpose |
|---|---|---|
| Component analysis | WebMethods/Analysis/GLDComplianceAdapterServices_Analysis.md | Detailed field-level breakdown |
| Map field mappings | WebMethods/Analysis/map_field_mappings.xlsx | Excel map template with pipeline in/out/transform |
| Boomi mapping reference | WebMethods/Agent Bridge Web Methods to Boomi Component Mapping.xlsx | webMethods → Boomi construct mapping |
| Connection node | iPaas Migration/WebMethods/GLDProject/GLDComplianceAdapterEnv/ | Oracle JDBC connection definition |
