# WMToWorkato — Sequential Workato Recipe Build Prompts

**Source:** `PackageAnalysis.md` — Section 5 (Recipe Design) + Sections 3 & 4 (Connection & Operations)
**Recipe Name:** `MIG_WM_GLDComplianceAdapterServices_Recipe`
**Recipe Type:** Callable Recipe (HTTP POST trigger)

Execute the prompts below in order. Each prompt builds one piece of the recipe.

---

## PROMPT 0 — Create the Oracle Database Connection

Create an Oracle database connection in Workato with the following settings:

- **Connection Name:** `MIG_WM_GLD_Oracle_Connection`
- **App / Provider:** Oracle
- **Host:** `CSC06DSHORA1S`
- **Port:** `1522`
- **SID / Service Name:** `ILMSUM`
- **Schema / Username:** `GLD_SCHEMA`
- **Password:** Retrieve from webMethods IS Admin UI → Adapters → JDBC → ExpressOS. ⚠️ The password is stored in proprietary encryption — obtain the plaintext from the IS Admin console or CyberArk before proceeding.
- **Connection Pool Min:** 1
- **Connection Pool Max:** 10

Save this connection. It will be reused by all Oracle action steps in the recipe.

---

## PROMPT 1 — Create the Recipe and Configure the Callable Trigger

Create a new Workato recipe named `MIG_WM_GLDComplianceAdapterServices_Recipe` in the `WebMethodsMigration` folder.

Set the **Trigger** as follows:
- **App:** Recipe Function by Workato (callable recipe)
- **Trigger event:** Receive request (callable recipe — HTTP POST)
- **Service Name:** `Compliance Check`

Define the **Request Input Schema** with the following 25 fields (all type: string unless noted):

| Field Name | Type | Notes |
|---|---|---|
| CustomerNbr | string | Max 18 chars |
| CustomerType | string | Max 3 chars |
| PartyType | string | Max 20 chars |
| Businessname | string | Max 40 chars |
| ApplicationNbr | string | Max 18 chars |
| Channel | string | Max 10 chars |
| LOB | string | Max 10 chars |
| ProductCode | string | Max 10 chars |
| SubProductCode | string | Max 10 chars |
| PostBack | string | Max 200 chars |
| ComplianceReplyEmail | string | Max 75 chars |
| FirstName | string | Max 20 chars |
| MiddleName | string | Max 20 chars |
| LastName | string | Max 20 chars |
| AddressLine1 | string | Max 40 chars |
| AddressLine2 | string | Max 40 chars |
| AddressLine3 | string | Max 40 chars |
| AddressLine4 | string | Max 40 chars |
| City | string | Max 20 chars |
| State | string | Max 2 chars |
| Zip | string | Max 10 chars |
| CountryCode | string | Max 3 chars |
| SSNTIN | string | Max 9 chars |
| DOB | date | Date of birth — convert to Oracle DATE format |
| RequestorSystemRequestID | integer | Requestor system request ID (BIGINT) |

Define the **Reply Schema** with a single field:
- `status` (string) — success or error message returned to caller

---

## PROMPT 2 — Add Error Handling Block (Handle Errors / Try-Catch)

Add a **Handle Errors** block (error monitor) immediately after the trigger, wrapping all action steps.

- **Block type:** Handle Errors (Workato try-catch pattern)
- **Label:** `Handle Errors`
- This block will contain all Oracle and HTTP action steps (Steps 1–6).
- The **on_error** (catch) path will be configured in a later prompt (Prompt 12).

---

## PROMPT 3 — Add Step 1: Oracle SP — Log Check Request (ACCLOGCHECKREQUEST)

Inside the **Handle Errors** block, add the first action step:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.ACCLOGCHECKREQUEST`
- **Step Label:** `Log Check Request`

Configure the **25 input parameters** by mapping each from the trigger input:

| SP Parameter | Data Type | Map From (Trigger Datapill) |
|---|---|---|
| CUSTOMERNBR | VARCHAR2(18) | trigger.CustomerNbr |
| CUSTOMERTYPE | VARCHAR2(3) | trigger.CustomerType |
| PARTYTYPE | VARCHAR2(20) | trigger.PartyType |
| BUSINESSNAME | VARCHAR2(40) | trigger.Businessname |
| APPLICATIONNBR | VARCHAR2(18) | trigger.ApplicationNbr |
| CHANNEL | VARCHAR2(10) | trigger.Channel |
| LOB | VARCHAR2(10) | trigger.LOB |
| PRODUCTCODE | VARCHAR2(10) | trigger.ProductCode |
| SUBPRODUCTCODE | VARCHAR2(10) | trigger.SubProductCode |
| POSTBACK | VARCHAR2(200) | trigger.PostBack |
| COMPLIANCEREPLYEMAIL | VARCHAR2(75) | trigger.ComplianceReplyEmail |
| FIRSTNAME | VARCHAR2(20) | trigger.FirstName |
| MIDDLENAME | VARCHAR2(20) | trigger.MiddleName |
| LASTNAME | VARCHAR2(20) | trigger.LastName |
| ADDRESSLINE1 | VARCHAR2(40) | trigger.AddressLine1 |
| ADDRESSLINE2 | VARCHAR2(40) | trigger.AddressLine2 |
| ADDRESSLINE3 | VARCHAR2(40) | trigger.AddressLine3 |
| ADDRESSLINE4 | VARCHAR2(40) | trigger.AddressLine4 |
| CITY | VARCHAR2(20) | trigger.City |
| STATE | VARCHAR2(2) | trigger.State |
| ZIP | VARCHAR2(10) | trigger.Zip |
| COUNTRYCODE | VARCHAR2(3) | trigger.CountryCode |
| SSNTIN | VARCHAR2(9) | trigger.SSNTIN |
| DOB | DATE | trigger.DOB (apply date conversion formula) |
| REQUESTORSYSTEMREQUESTID | BIGINT | trigger.RequestorSystemRequestID |

**Output Note:** This stored procedure does not return the generated `ACCCHECKREQUESTID` directly. Proceed to Prompt 4 to retrieve it with a follow-up SELECT.

---

## PROMPT 4 — Add Step 1b: Oracle SELECT — Retrieve accCheckRequestID

Immediately after Step 1 (still inside Handle Errors), add a second Oracle action to retrieve the auto-generated request ID:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Run Custom SQL / Select Rows
- **Step Label:** `Get Check Request ID`

**SQL:**
```sql
SELECT ACCCHECKREQUESTID
FROM GLD_SCHEMA.ACCCHECKREQUEST
WHERE REQUESTORSYSTEMREQUESTID = ?
```

**Input parameter:** `REQUESTORSYSTEMREQUESTID` → map from trigger.RequestorSystemRequestID

**Output:** `rows[0].ACCCHECKREQUESTID` — this datapill will be used as `step1.accCheckRequestID` in Steps 2 and 4.

---

## PROMPT 5 — Add Step 2: Oracle SP — Log Check Request XML (LOGXMLREQUEST)

Inside the Handle Errors block, add the next action step:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.LOGXMLREQUEST`
- **Step Label:** `Log Check Request XML`

Configure the **5 input parameters**:

| SP Parameter | Data Type | Map From |
|---|---|---|
| APPLICATIONID | BIGINT | Step 1b output → rows[0].ACCCHECKREQUESTID |
| REQUEST | LONGVARCHAR | JSON-encode the full trigger input payload using a formula: `trigger.to_json` or build a JSON string of all 25 input fields |
| REQUESTIDENTIFIER1 | VARCHAR2 | trigger.CustomerNbr |
| REQUESTIDENTIFIER2 | VARCHAR2 | trigger.ApplicationNbr |
| REQUESTIDENTIFIER3 | VARCHAR2 | trigger.Channel |

**Output:** None (void procedure — no output datapills).

**JSON Profile Note:** For the REQUEST parameter, create a JSON formula that encodes the full trigger input as a JSON string. Use Workato's formula mode to build: `{"CustomerNbr": #{trigger.CustomerNbr}, "CustomerType": #{trigger.CustomerType}, ...}` — include all 25 trigger fields.

---

## PROMPT 6 — Add Step 3: HTTP Action — Call CIU External System

Inside the Handle Errors block, add an HTTP action step:

- **App:** HTTP
- **Connection:** Create a new HTTP connection named `MIG_WM_CIU_Connection`
  - **Base URL:** `[CIU_ENDPOINT_URL]` — ⚠️ URL is unknown; obtain from SME. Leave as placeholder for now.
  - **Authentication:** To be determined by SME
- **Action:** Send Request (HTTP POST)
- **Step Label:** `Call CIU System`

**Request configuration:**
- **Method:** POST
- **URL path:** `/` (or the specific CIU endpoint path — obtain from SME)
- **Request body type:** JSON
- **Request body:** Include all 25 customer fields from the trigger input as a JSON payload

**Define a JSON Request Profile** with these fields (all strings unless noted):
`CustomerNbr`, `CustomerType`, `PartyType`, `Businessname`, `ApplicationNbr`, `Channel`, `LOB`, `ProductCode`, `SubProductCode`, `PostBack`, `ComplianceReplyEmail`, `FirstName`, `MiddleName`, `LastName`, `AddressLine1`–`AddressLine4`, `City`, `State`, `Zip`, `CountryCode`, `SSNTIN`, `DOB`, `RequestorSystemRequestID`

**Define a JSON Response Profile** with these 5 fields:
| Field | Type | Description |
|---|---|---|
| CIURefNbr | string | CIU reference number — used in Steps 4, 5a, 5b, 6 |
| CheckResult | string | "TRUE" or "FALSE" — used in Step 5 IF condition |
| ErrorType | string | Error type if CIU failed — used in Step 5b |
| ErrorCode | string | Error code — used in Step 5b |
| ErrorDesc | string | Error description — used in Step 5b |

**Output datapills available after this step:**
- `step3.CIURefNbr`
- `step3.CheckResult`
- `step3.ErrorType`, `step3.ErrorCode`, `step3.ErrorDesc`

---

## PROMPT 7 — Add Step 4: Oracle SP — Update CIU Reference Number (ACCUPDATECIUREFNBR)

Inside the Handle Errors block, add the next action step:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.ACCUPDATECIUREFNBR`
- **Step Label:** `Update CIU Reference`

Configure the **2 input parameters**:

| SP Parameter | Data Type | Map From |
|---|---|---|
| ACCCHECKREQUESTID | BIGINT | Step 1b output → rows[0].ACCCHECKREQUESTID |
| CIUREFNBR | VARCHAR2 | Step 3 output → step3.CIURefNbr |

**Output:** None (void update — no output datapills).

---

## PROMPT 8 — Add Step 5: IF/ELSE Block — Check CIU Result

Inside the Handle Errors block, add a conditional IF/ELSE block:

- **Block type:** IF/ELSE (conditional)
- **Step Label:** `Check CIU Result`

**IF condition:**
- **Data field:** Step 3 output → `step3.CheckResult`
- **Operator:** equals
- **Value:** `TRUE`

The **IF (true) path** will contain Step 5a (Prompt 9).
The **ELSE (false) path** will contain Step 5b (Prompt 10).

---

## PROMPT 9 — Add Step 5a: Oracle SP — Log Check Reply, TRUE Path (ACCLOGCHECKREPLY)

Inside the **IF (true) branch** of the IF/ELSE block from Prompt 8, add:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.ACCLOGCHECKREPLY`
- **Step Label:** `Log Check Reply (Success)`

Configure the **3 input parameters**:

| SP Parameter | Data Type | Map From |
|---|---|---|
| CIUREFNBR | VARCHAR2 | Step 3 output → step3.CIURefNbr |
| CHECKTYPE | VARCHAR2 | Step 3 output → step3.CheckType, OR use static value `"COMPLIANCE"` if not returned |
| RESULT | VARCHAR2 | Static value → `"true"` (literal — this is the success path) |

**Output:** None.

---

## PROMPT 10 — Add Step 5b: Oracle SP — Log Check Reply Error, ELSE Path (ACCLOGCHECKREPLYERROR)

Inside the **ELSE branch** of the IF/ELSE block from Prompt 8, add:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.ACCLOGCHECKREPLYERROR`
- **Step Label:** `Log Check Reply Error (CIU Failed)`

Configure the **4 input parameters**:

| SP Parameter | Data Type | Map From |
|---|---|---|
| ERRORTYPE | VARCHAR2 | Step 3 output → step3.ErrorType |
| ERRORCODE | VARCHAR2 | Step 3 output → step3.ErrorCode |
| ERRORDESC | VARCHAR2 | Step 3 output → step3.ErrorDesc |
| CIUREFNBR | VARCHAR2 | Step 3 output → step3.CIURefNbr |

**Output:** None.

---

## PROMPT 11 — Add Step 6: Oracle SELECT — Select Customer and Request (JOIN Query)

Inside the Handle Errors block (after the IF/ELSE block), add an Oracle custom SQL action:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Run Custom SQL / Select Rows
- **Step Label:** `Select Customer and Request`

**SQL Query:**
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

**Input parameter:** `CIUREFNBR` → Step 3 output → `step3.CIURefNbr`

**Define the Output Schema** with the following 28 columns:

| Column | Type | Workato Datapill |
|---|---|---|
| ACCCUSTOMERID | number | step6.rows[0].ACCCUSTOMERID |
| CUSTOMERNBR | string | step6.rows[0].CUSTOMERNBR |
| CUSTOMERTYPE | string | step6.rows[0].CUSTOMERTYPE |
| BUSINESSNAME | string | step6.rows[0].BUSINESSNAME |
| FIRSTNAME | string | step6.rows[0].FIRSTNAME |
| MIDDLENAME | string | step6.rows[0].MIDDLENAME |
| LASTNAME | string | step6.rows[0].LASTNAME |
| ADDRESSLINE1 | string | step6.rows[0].ADDRESSLINE1 |
| ADDRESSLINE2 | string | step6.rows[0].ADDRESSLINE2 |
| ADDRESSLINE3 | string | step6.rows[0].ADDRESSLINE3 |
| ADDRESSLINE4 | string | step6.rows[0].ADDRESSLINE4 |
| CITY | string | step6.rows[0].CITY |
| STATE | string | step6.rows[0].STATE |
| ZIP | string | step6.rows[0].ZIP |
| COUNTRYCODE | string | step6.rows[0].COUNTRYCODE |
| SSNTIN | string | step6.rows[0].SSNTIN |
| PARTYTYPE | string | step6.rows[0].PARTYTYPE |
| DOB | date | step6.rows[0].DOB |
| ACCCHECKREQUESTID | number | step6.rows[0].ACCCHECKREQUESTID |
| APPLICATIONNBR | string | step6.rows[0].APPLICATIONNBR |
| CHANNEL | string | step6.rows[0].CHANNEL |
| LOB | string | step6.rows[0].LOB |
| PRODUCTCODE | string | step6.rows[0].PRODUCTCODE |
| SUBPRODUCTCODE | string | step6.rows[0].SUBPRODUCTCODE |
| POSTBACK | string | step6.rows[0].POSTBACK |
| COMPLIANCEREPLYEMAIL | string | step6.rows[0].COMPLIANCEREPLYEMAIL |
| CIUREFNBR | string | step6.rows[0].CIUREFNBR |
| REQUESTTIMESTAMP | timestamp | step6.rows[0].REQUESTTIMESTAMP |

---

## PROMPT 12 — Configure the Catch Block (on_error) — Log System Error

In the **on_error / catch path** of the Handle Errors block from Prompt 2, add:

- **App:** Oracle
- **Connection:** `MIG_WM_GLD_Oracle_Connection`
- **Action:** Execute Stored Procedure
- **Stored Procedure:** `GLD_SCHEMA.ACCLOGCHECKREPLYERROR`
- **Step Label:** `Log System Error`

Configure the **4 input parameters** using the error monitor's built-in datapills:

| SP Parameter | Data Type | Map From |
|---|---|---|
| ERRORTYPE | VARCHAR2 | Error monitor → `error.error_type` |
| ERRORCODE | VARCHAR2 | Error monitor → `error.error_code` |
| ERRORDESC | VARCHAR2 | Error monitor → `error.message` |
| CIUREFNBR | VARCHAR2 | Step 3 output → `step3.CIURefNbr` (may be blank if error occurred before Step 3) |

**Output:** None.

---

## PROMPT 13 — Configure the Recipe Reply (Return Response to Caller)

After the Handle Errors block closes, add a final **Send Reply** step to return the result to the calling system:

- **App:** Recipe Function by Workato
- **Action:** Return response
- **Step Label:** `Return Compliance Result`

Map the reply fields based on the reply schema defined in Prompt 1:
- `status` → use a formula: if Step 5 IF condition was true → `"COMPLIANCE_PASSED"`, else → `"COMPLIANCE_FAILED"`. Alternatively, map `step6.rows[0].CIUREFNBR` as the confirmation that data was retrieved.

**Note:** Workato callable recipes require an explicit Return Response step — without it the recipe will not send data back to the caller.

---

## Summary: Recipe Structure

```
Trigger: Callable Recipe — HTTP POST (25 input fields)
  └── Handle Errors (try block)
        ├── Step 1  — Oracle SP: ACCLOGCHECKREQUEST (25 params from trigger)
        ├── Step 1b — Oracle SELECT: GET ACCCHECKREQUESTID (follow-up query)
        ├── Step 2  — Oracle SP: LOGXMLREQUEST (5 params; REQUEST = JSON of trigger payload)
        ├── Step 3  — HTTP POST: CIU External System (25-field JSON body; 5-field JSON response)
        ├── Step 4  — Oracle SP: ACCUPDATECIUREFNBR (2 params)
        ├── Step 5  — IF/ELSE: CheckResult == "TRUE"
        │     ├── IF TRUE  → Step 5a: Oracle SP: ACCLOGCHECKREPLY (3 params)
        │     └── IF FALSE → Step 5b: Oracle SP: ACCLOGCHECKREPLYERROR (4 params from CIU response)
        ├── Step 6  — Oracle SELECT JOIN: Customer + Request (28 output columns)
        └── on_error → Oracle SP: ACCLOGCHECKREPLYERROR (4 params from error monitor)
  └── Step 13 — Return Response to caller
```

**Connections required:**
1. `MIG_WM_GLD_Oracle_Connection` — Oracle DB at CSC06DSHORA1S:1522/ILMSUM, schema GLD_SCHEMA
2. `MIG_WM_CIU_Connection` — HTTP connection to CIU external system (URL from SME)
