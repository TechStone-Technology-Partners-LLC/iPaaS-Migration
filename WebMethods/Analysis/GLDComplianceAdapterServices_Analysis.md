# GLDComplianceAdapterServices — Component Analysis

**Package:** GLDComplianceAdapterServices  
**Platform:** webMethods Integration Server 6.5  
**Publisher:** cwb02dwmis02.keybank.com  
**Build Date:** 2008-06-26  
**Version:** 1.0  
**Adapter Type:** JDBC Adapter (JDBCAdapter)  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`  
**Database:** Oracle — `GLD_SCHEMA` (CSC06DSHORA1S:1522/ILMSUM)

---

## Package Overview

`GLDComplianceAdapterServices` is a webMethods JDBC Adapter Service package that provides all Oracle database interaction for the GLD Compliance workflow. It contains **6 adapter services**, each mapping directly to either a stored procedure call or a SELECT query against the Oracle GLD schema. These services are called by the `GLDComplianceCheck` flow services to log requests, log replies, select customer data, update reference numbers, and purge old data.

---

## Service Inventory

| # | Service Name | DB Operation | SQL Object |
|---|---|---|---|
| 1 | `logCheckRequest` | INSERT via Stored Procedure | `GLD_SCHEMA.ACCLOGCHECKREQUEST` |
| 2 | `logCheckRequestXML` | INSERT via Stored Procedure | `GLD_SCHEMA.LOGXMLREQUEST` |
| 3 | `logCheckReply` | SELECT via Stored Procedure | `GLD_SCHEMA.ACCLOGCHECKREPLY` |
| 4 | `logCheckReplyError` | INSERT via Stored Procedure | `GLD_SCHEMA.ACCLOGCHECKREPLYERROR` |
| 5 | `selectCustomerAndRequest` | SELECT (JOIN query) | `GLD_SCHEMA.ACCCUSTOMER` JOIN `GLD_SCHEMA.ACCCHECKREQUEST` |
| 6 | `updateCIURefNbr` | UPDATE via Stored Procedure | `GLD_SCHEMA.ACCUPDATECIUREFNBR` |
| 7 | `purgeData` | DELETE via Stored Procedure | `GLD_SCHEMA.ACCPURGEDATA` |

> Note: The package folder has 6 node.ndf files (logCheckReply, logCheckReplyError, logCheckRequest, logCheckRequestXML, purgeData, selectCustomerAndRequest, updateCIURefNbr = 7 services total).

---

## Detailed Service Definitions

### 1. `logCheckRequest`
**Purpose:** Logs a new compliance check request to the Oracle database. Returns the generated request ID.  
**DB Object:** Stored Procedure `ACCLOGCHECKREQUEST`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In (Input Fields):**
| Field | Java Type | DB Type | Notes |
|---|---|---|---|
| CustomerNbr | String | VARCHAR2(18) | Customer number |
| CustomerType | String | VARCHAR2(3) | Customer type code |
| PartyType | String | VARCHAR2(20) | Party type |
| Businessname | String | VARCHAR2(40) | Business name |
| ApplicationNbr | String | VARCHAR2(18) | Application number |
| Channel | String | VARCHAR2(10) | Originating channel |
| LOB | String | VARCHAR2(10) | Line of business |
| ProductCode | String | VARCHAR2(10) | Product code |
| SubProductCode | String | VARCHAR2(10) | Sub-product code |
| PostBack | String | VARCHAR2(200) | Post-back URL/value |
| ComplianceReplyEmail | String | VARCHAR2(75) | Email for compliance reply |
| FirstName | String | VARCHAR2(20) | Customer first name |
| MiddleName | String | VARCHAR2(20) | Customer middle name |
| LastName | String | VARCHAR2(20) | Customer last name |
| AddressLine1 | String | VARCHAR2(40) | Address line 1 |
| AddressLine2 | String | VARCHAR2(40) | Address line 2 |
| AddressLine3 | String | VARCHAR2(40) | Address line 3 |
| AddressLine4 | String | VARCHAR2(40) | Address line 4 |
| City | String | VARCHAR2(20) | City |
| State | String | VARCHAR2(2) | State code |
| Zip | String | VARCHAR2(10) | ZIP code |
| CountryCode | String | VARCHAR2(3) | Country code |
| SSNTIN | String | VARCHAR2(9) | SSN or Tax ID |
| DOB | String | DATE | Date of birth |
| RequestorSystemRequestID | Long | BIGINT | Requestor system request ID |

**Pipeline Out (Output Fields):**
| Field | Java Type | Notes |
|---|---|---|
| accCheckRequestID | Long | Auto-generated request ID from Oracle |

---

### 2. `logCheckRequestXML`
**Purpose:** Logs the raw XML representation of a compliance check request for audit/archival.  
**DB Object:** Stored Procedure `LOGXMLREQUEST`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In (Input Fields):**
| Field | Java Type | DB Type | Notes |
|---|---|---|---|
| ApplicationID | Long | BIGINT | Application identifier |
| Request | Object | LONGVARCHAR | Raw XML of the request |
| RequestIdentifier1 | String | VARCHAR2 | Identifier 1 |
| RequestIdentifier2 | String | VARCHAR2 | Identifier 2 |
| RequestIdentifier3 | String | VARCHAR2 | Identifier 3 |

**Pipeline Out:** No output fields (void procedure).

---

### 3. `logCheckReply`
**Purpose:** Retrieves/logs a compliance check reply from the database based on `CIURefNbr`, `CheckType`, and `Result`.  
**DB Object:** Stored Procedure `ACCLOGCHECKREPLY`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In (Input Fields):**
| Field | Java Type | DB Type | Notes |
|---|---|---|---|
| CIURefNbr | String | VARCHAR2 | CIU reference number (compliance check reference) |
| CheckType | String | VARCHAR2 | Type of compliance check |
| Result | Boolean | VARCHAR2 | Result of the check (true/false) |

**Pipeline Out:** No output fields (the procedure logs the reply internally).

---

### 4. `logCheckReplyError`
**Purpose:** Logs an error that occurred during a compliance check reply.  
**DB Object:** Stored Procedure `ACCLOGCHECKREPLYERROR`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In (Input Fields):**
| Field | Java Type | DB Type | Notes |
|---|---|---|---|
| ErrorType | String | VARCHAR2 | Category of error |
| ErrorCode | String | VARCHAR2 | Error code |
| ErrorDesc | String | VARCHAR2 | Error description |
| CIURefNbr | String | VARCHAR2 | CIU reference number associated with the error |

**Pipeline Out:** No output fields (void procedure).

---

### 5. `selectCustomerAndRequest`
**Purpose:** Retrieves combined customer and compliance check request data from Oracle. Used to look up all request context when a CIU reference number is received back from the compliance system.  
**DB Object:** SELECT JOIN query — `GLD_SCHEMA.ACCCUSTOMER` t1 JOIN `GLD_SCHEMA.ACCCHECKREQUEST` t2  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**SQL (reconstructed from IRTNODE_PROPERTY metadata):**
```sql
SELECT DISTINCT
  t1.CUSTOMERNBR, t1.CUSTOMERTYPE, t1.BUSINESSNAME,
  t1.FIRSTNAME, t1.MIDDLENAME, t1.LASTNAME,
  t1.ADDRESSLINE1, t1.ADDRESSLINE2, t1.ADDRESSLINE3, t1.ADDRESSLINE4,
  t1.CITY, t1.STATE, t1.ZIP, t1.COUNTRYCODE, t1.SSNTIN,
  t1.PARTYTYPE, t1.DOB,
  t2.ACCCHECKREQUESTID, t2.APPLICATIONNBR, t2.CHANNEL, t2.LOB,
  t2.PRODUCTCODE, t2.SUBPRODUCTCODE, t2.POSTBACK,
  t2.COMPLIANCEREPLYEMAIL, t2.CIUREFNBR, t2.REQUESTTIMESTAMP,
  t1.ACCCUSTOMERID
FROM GLD_SCHEMA.ACCCUSTOMER t1
JOIN GLD_SCHEMA.ACCCHECKREQUEST t2
  ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID
WHERE t2.CIUREFNBR = ?
```

**Pipeline In (Input Fields):**
| Field | Java Type | Notes |
|---|---|---|
| CIURefNbr | String | Compliance reference number to look up |

**Pipeline Out (Output Fields) — `results[]` array:**
| Field | Java Type | DB Column | Notes |
|---|---|---|---|
| ACCCUSTOMERID | BigDecimal | t1.ACCCUSTOMERID | Internal customer ID |
| CUSTOMERNBR | String | t1.CUSTOMERNBR | Customer number |
| CUSTOMERTYPE | String | t1.CUSTOMERTYPE | Customer type |
| BUSINESSNAME | String | t1.BUSINESSNAME | Business name |
| FIRSTNAME | String | t1.FIRSTNAME | First name |
| MIDDLENAME | String | t1.MIDDLENAME | Middle name |
| LASTNAME | String | t1.LASTNAME | Last name |
| ADDRESSLINE1 | String | t1.ADDRESSLINE1 | Address line 1 |
| ADDRESSLINE2 | String | t1.ADDRESSLINE2 | Address line 2 |
| ADDRESSLINE3 | String | t1.ADDRESSLINE3 | Address line 3 |
| ADDRESSLINE4 | String | t1.ADDRESSLINE4 | Address line 4 |
| CITY | String | t1.CITY | City |
| STATE | String | t1.STATE | State |
| ZIP | String | t1.ZIP | ZIP code |
| COUNTRYCODE | String | t1.COUNTRYCODE | Country code |
| SSNTIN | String | t1.SSNTIN | SSN or TIN |
| PARTYTYPE | String | t1.PARTYTYPE | Party type |
| DOB | Timestamp | t1.DOB | Date of birth |
| ACCCHECKREQUESTID | BigDecimal | t2.ACCCHECKREQUESTID | Request ID |
| APPLICATIONNBR | String | t2.APPLICATIONNBR | Application number |
| CHANNEL | String | t2.CHANNEL | Channel |
| LOB | String | t2.LOB | Line of business |
| PRODUCTCODE | String | t2.PRODUCTCODE | Product code |
| SUBPRODUCTCODE | String | t2.SUBPRODUCTCODE | Sub-product code |
| POSTBACK | String | t2.POSTBACK | Post-back value |
| COMPLIANCEREPLYEMAIL | String | t2.COMPLIANCEREPLYEMAIL | Reply email |
| CIUREFNBR | String | t2.CIUREFNBR | CIU reference number |
| REQUESTTIMESTAMP | Timestamp | t2.REQUESTTIMESTAMP | Request timestamp |

---

### 6. `updateCIURefNbr`
**Purpose:** Updates the CIU (Compliance/Identity Unit) reference number on an existing compliance check request record. Called after the external compliance system returns a reference number.  
**DB Object:** Stored Procedure `ACCUPDATECIUREFNBR`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In (Input Fields):**
| Field | Java Type | DB Type | Notes |
|---|---|---|---|
| accCheckRequestID | Long | BIGINT | The internal request ID to update |
| CIURefNbr | String | VARCHAR2 | The CIU reference number to store |

**Pipeline Out:** No output fields (void update).

---

### 7. `purgeData`
**Purpose:** Purges old/expired compliance check records. No input parameters — the stored procedure likely uses an internal date threshold.  
**DB Object:** Stored Procedure `ACCPURGEDATA`  
**Connection:** `GLDComplianceAdapterEnv:ExpressOS`

**Pipeline In:** No input fields.  
**Pipeline Out:** No output fields.

---

## Connection Details

All 7 services share a single connection alias:

| Property | Value |
|---|---|
| Connection Name | `GLDComplianceAdapterEnv:ExpressOS` |
| Adapter Type | `JDBCAdapter` |
| Factory Class | `com.wm.adapter.wmjdbc.connection.JDBCConnectionFactory` |
| JDBC URL | `jdbc:oracle:thin:@CSC06DSHORA1S:1522:ILMSUM` (or `/ILMSUM`) |
| Schema | `GLD_SCHEMA` |
| Database | Oracle 10g |
| Pool Min/Max | 1 / 10 |

---

## Integration Flow Context

The services in `GLDComplianceAdapterServices` support the following execution sequence (called by `GLDComplianceCheck`):

```
1. logCheckRequest       ← INSERT new request; get accCheckRequestID
2. logCheckRequestXML    ← INSERT raw XML of request for audit
3. [External CIU call]   ← webMethods sends to external compliance system
4. updateCIURefNbr       ← UPDATE request with CIURefNbr returned by CIU
5. logCheckReply         ← LOG the reply (pass/fail) from compliance system
6. logCheckReplyError    ← LOG any error in the reply (error path only)
7. selectCustomerAndRequest ← SELECT combined record (used on reply callback)
8. purgeData             ← PURGE old records (scheduled/maintenance operation)
```

---

## Missing / Gap Components

The following elements are required but not present in this package alone:

| Gap | Description |
|---|---|
| Flow Services | No flow.xml files exist in this package — logic is in `GLDComplianceCheck` |
| External CIU Connector | The external compliance service endpoint is not defined here |
| Trigger/Scheduler | No trigger or scheduler is defined in this package |
| Error handling flow | Error routing is delegated to `GLDComplianceCheck` flow services |
