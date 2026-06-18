# Workato.md — GLDComplianceAdapterServices → Workato Recipe Reference

> **Purpose:** Authoritative specification for building the Workato recipe for the GLD Compliance workflow.
>
> **Generated from:** `PackageAnalysis.md` + `Agent Bridge Web Methods to Workato Component Mapping.xlsx` + `Workato_Map_Field_Mappings.xlsx`
>
> **Status:** Draft — pending CIU endpoint URL from SME and GLD_SCHEMA password from DBA/Admin.

---

## 1. Source Package Summary

| Field | Value |
|---|---|
| Package name | GLDComplianceAdapterServices |
| Source platform | webMethods Integration Server 6.5 |
| Database | Oracle — schema `GLD_SCHEMA`, host `CSC06DSHORA1S:1522`, SID `ILMSUM` |
| JDBC alias | ExpressOS (configured in IS Adapter > JDBC) |
| External system | CIU (Customer Identification Unit) — external compliance check service (HTTP) |
| Client | KeyBank compliance check workflow |
| DB services | 7 Oracle operations (5 stored procedures, 1 SELECT DISTINCT JOIN, 1 parameterless SP) |
| Trigger | Not found in flow.xml — recommend callable recipe (HTTP POST) |
| Constructs mapped | 22 webMethods constructs → Workato equivalents (see Agent Bridge Excel) |

**Workflow summary:** A client system submits customer data via HTTP POST. The recipe logs the compliance check request to Oracle (ACCLOGCHECKREQUEST SP), logs the raw XML request (LOGXMLREQUEST SP), calls the external CIU system to get a compliance determination, updates the CIU reference number back into Oracle (ACCUPDATECIUREFNBR SP), then branches on the CIU result: success path logs the reply (ACCLOGCHECKREPLY SP), failure path logs the error (ACCLOGCHECKREPLYERROR SP). A final SELECT retrieves the full customer + request record. An error monitor wraps all steps.

---

## 2. Workato Component Plan

| # | Component Name | Type | Source Artifact | Notes |
|---|---|---|---|---|
| 1 | MIG_WM_GLD_Oracle_Connection | Connection (Oracle DB) | Connection alias `ExpressOS` | host `CSC06DSHORA1S:1522`, SID `ILMSUM`, schema `GLD_SCHEMA` — create in Workato GUI |
| 2 | MIG_WM_GLDComplianceAdapterServices_Recipe | Recipe (callable) | `GLDComplianceCheck` flow service | Main compliance check recipe — HTTP POST trigger |
| 3 | MIG_WM_GLD_PurgeData_Recipe | Recipe (scheduled) — optional | `purgeData` service | Separate scheduled recipe; calls SP `ACCPURGEDATA` with no parameters |

---

## 3. Oracle Connection Setup

Create this connection in the Workato GUI (**Tools → Connections → New Connection → Oracle**) before building the recipe.

| Parameter | Value |
|---|---|
| Connection name | `MIG_WM_GLD_Oracle_Connection` |
| Provider | Oracle |
| Host | `CSC06DSHORA1S` |
| Port | `1522` |
| SID / Service name | `ILMSUM` |
| Schema / Username | `GLD_SCHEMA` |
| Password | Retrieve from IS Admin UI: **Adapters → JDBC → ExpressOS → Connection URL** — ask DBA or IS Admin for the password |
| SSL | Confirm with DBA (not specified in source) |

After entering credentials, click **Connect** to authorize. Once the connection shows a green check, it is available as a data pill source in recipe steps.

---

## 4. Recipe Actions — Step by Step

### Trigger: Callable Recipe (HTTP POST)

**Type:** Callable recipe trigger
**Workato block:** `trigger: callable_recipe`

The trigger receives a JSON body. Define the following input schema fields (all String unless noted):

| Field | Type | Source webMethods field |
|---|---|---|
| CustomerNbr | String | CUSTOMERNBR |
| CustomerType | String | CUSTOMERTYPE |
| PartyType | String | PARTYTYPE |
| Businessname | String | BUSINESSNAME |
| ApplicationNbr | String | APPLICATIONNBR |
| Channel | String | CHANNEL |
| LOB | String | LOB |
| ProductCode | String | PRODUCTCODE |
| SubProductCode | String | SUBPRODUCTCODE |
| PostBack | String | POSTBACK |
| ComplianceReplyEmail | String | COMPLIANCEREPLYEMAIL |
| FirstName | String | FIRSTNAME |
| MiddleName | String | MIDDLENAME |
| LastName | String | LASTNAME |
| AddressLine1 | String | ADDRESSLINE1 |
| AddressLine2 | String | ADDRESSLINE2 |
| AddressLine3 | String | ADDRESSLINE3 |
| AddressLine4 | String | ADDRESSLINE4 |
| City | String | CITY |
| State | String | STATE |
| Zip | String | ZIP |
| CountryCode | String | COUNTRYCODE |
| SSNTIN | String | SSNTIN |
| DOB | String | DOB (convert to Oracle DATE format before passing to SP) |
| RequestorSystemRequestID | Integer | REQUESTORSYSTEMREQUESTID |

**Calling pattern:** Client systems POST to the Workato callable recipe URL with the JSON body above. Workato returns a synchronous response.

---

### Error Monitor (wraps Steps 1–7)

**Type:** `handle_errors` block
**Workato block:** Wrap all action steps inside an error monitor.

On error:
1. Capture `error_type` and `error_message` from the error data pill.
2. If `CIURefNbr` is available (set in Step 3), call **Step 6b** (ACCLOGCHECKREPLYERROR) to record the error.
3. Use a **Stop** action to return an error response from the callable recipe (HTTP 500 or structured error JSON).

Place the error monitor immediately after the trigger, before Step 1.

---

### Step 1: Log Check Request

**Action type:** Oracle → Stored procedure
**SP name:** `ACCLOGCHECKREQUEST`
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**Input field mappings (all 25 parameters):**

| SP Parameter | DB Type | Workato Formula / Data Pill |
|---|---|---|
| CUSTOMERNBR | VARCHAR2(18) | `trigger.CustomerNbr` |
| CUSTOMERTYPE | VARCHAR2(3) | `trigger.CustomerType` |
| PARTYTYPE | VARCHAR2(20) | `trigger.PartyType` |
| BUSINESSNAME | VARCHAR2(40) | `trigger.Businessname` |
| APPLICATIONNBR | VARCHAR2(18) | `trigger.ApplicationNbr` |
| CHANNEL | VARCHAR2(10) | `trigger.Channel` |
| LOB | VARCHAR2(10) | `trigger.LOB` |
| PRODUCTCODE | VARCHAR2(10) | `trigger.ProductCode` |
| SUBPRODUCTCODE | VARCHAR2(10) | `trigger.SubProductCode` |
| POSTBACK | VARCHAR2(200) | `trigger.PostBack` |
| COMPLIANCEREPLYEMAIL | VARCHAR2(75) | `trigger.ComplianceReplyEmail` |
| FIRSTNAME | VARCHAR2(20) | `trigger.FirstName` |
| MIDDLENAME | VARCHAR2(20) | `trigger.MiddleName` |
| LASTNAME | VARCHAR2(20) | `trigger.LastName` |
| ADDRESSLINE1 | VARCHAR2(40) | `trigger.AddressLine1` |
| ADDRESSLINE2 | VARCHAR2(40) | `trigger.AddressLine2` |
| ADDRESSLINE3 | VARCHAR2(40) | `trigger.AddressLine3` |
| ADDRESSLINE4 | VARCHAR2(40) | `trigger.AddressLine4` |
| CITY | VARCHAR2(20) | `trigger.City` |
| STATE | VARCHAR2(2) | `trigger.State` |
| ZIP | VARCHAR2(10) | `trigger.Zip` |
| COUNTRYCODE | VARCHAR2(3) | `trigger.CountryCode` |
| SSNTIN | VARCHAR2(9) | `trigger.SSNTIN` |
| DOB | DATE | `trigger.DOB.to_date("YYYY-MM-DD")` — convert string to Oracle DATE |
| REQUESTORSYSTEMREQUESTID | BIGINT | `trigger.RequestorSystemRequestID.to_i` |

**Output — accCheckRequestID:**

Oracle stored procedures do not return OUT parameters easily via Workato's standard Oracle action. Use this workaround immediately after Step 1:

Add a second Oracle action (custom SELECT):
```sql
SELECT ACCCHECKREQUESTID FROM GLD_SCHEMA.ACCCHECKREQUEST
WHERE REQUESTORSYSTEMREQUESTID = ?
ORDER BY REQUESTTIMESTAMP DESC
FETCH FIRST 1 ROWS ONLY
```
Input: `trigger.RequestorSystemRequestID`
Output data pill: `step1_select.rows[0].ACCCHECKREQUESTID` → store as recipe variable `accCheckRequestID`

> **Note:** See Missing Components item #4 for the full explanation of why this SELECT is needed.

---

### Step 2: Log Check Request XML

**Action type:** Oracle → Stored procedure
**SP name:** `LOGXMLREQUEST`
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**Input field mappings (5 parameters):**

| SP Parameter | DB Type | Workato Formula / Data Pill |
|---|---|---|
| APPLICATIONID | NUMBER | `accCheckRequestID` (from Step 1 SELECT) |
| REQUEST | CLOB | `trigger.to_json` — serialize the full trigger payload as JSON string |
| REQUESTIDENTIFIER1 | VARCHAR2 | `trigger.CustomerNbr` |
| REQUESTIDENTIFIER2 | VARCHAR2 | `trigger.ApplicationNbr` |
| REQUESTIDENTIFIER3 | VARCHAR2 | `trigger.Channel` |

**Output:** None (fire-and-forget logging step).

---

### Step 3: Call CIU External System (Placeholder — Manual Wiring Required)

**Action type:** HTTP → POST
**Connection:** Create a new HTTP connection in Workato GUI pointing to the CIU endpoint.

> **BLOCKED:** The CIU endpoint URL is not documented in any source artifact. An SME must provide the URL, authentication method (API key / OAuth / Basic Auth), and request/response schema before this step can be fully configured.

**Planned input (wire once URL is known):**

| CIU Request Field | Source |
|---|---|
| CustomerNbr | `trigger.CustomerNbr` |
| CustomerType | `trigger.CustomerType` |
| ApplicationNbr | `trigger.ApplicationNbr` |
| Channel | `trigger.Channel` |
| LOB | `trigger.LOB` |
| SSNTIN | `trigger.SSNTIN` |
| DOB | `trigger.DOB` |
| (all other customer fields) | Direct from trigger data pills |

**Expected output data pills:**

| Output Field | Notes |
|---|---|
| `step3.CIURefNbr` | CIU-assigned reference number |
| `step3.CheckResult` | String `"TRUE"` or `"FALSE"` (or derive via formula — see Missing Components #5) |

**CheckResult formula (if CIU returns HTTP status only):**
```
if step3.response_code == "200" then "TRUE" else "FALSE" end
```

---

### Step 4: Update CIU Reference Number

**Action type:** Oracle → Stored procedure
**SP name:** `ACCUPDATECIUREFNBR`
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**Input field mappings (2 parameters):**

| SP Parameter | DB Type | Workato Data Pill |
|---|---|---|
| ACCCHECKREQUESTID | NUMBER | `accCheckRequestID` (from Step 1) |
| CIUREFNBR | VARCHAR2 | `step3.CIURefNbr` |

**Output:** None.

---

### Step 5: Decision — Check Passed?

**Type:** `if` / `else` conditional block

**Condition:** `step3.CheckResult == "TRUE"`

- **TRUE path** → Step 6a (Log Check Reply)
- **ELSE path** → Step 6b (Log Check Reply Error)

---

### Step 6a: Log Check Reply (TRUE path)

**Action type:** Oracle → Stored procedure
**SP name:** `ACCLOGCHECKREPLY`
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**Input field mappings (3 parameters):**

| SP Parameter | DB Type | Workato Data Pill |
|---|---|---|
| CIUREFNBR | VARCHAR2 | `step3.CIURefNbr` |
| CHECKTYPE | VARCHAR2 | `trigger.CustomerType` (confirm with SME — CheckType not explicitly mapped in source) |
| RESULT | VARCHAR2 | `"true"` (literal string for success path) |

**Output:** None.

---

### Step 6b: Log Check Reply Error (ELSE path)

**Action type:** Oracle → Stored procedure
**SP name:** `ACCLOGCHECKREPLYERROR`
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**Input field mappings (4 parameters):**

| SP Parameter | DB Type | Workato Data Pill |
|---|---|---|
| ERRORTYPE | VARCHAR2 | `step3.error_type` or `"COMPLIANCE_FAILURE"` literal |
| ERRORCODE | VARCHAR2 | `step3.error_code` or `step3.response_code` |
| ERRORDESC | VARCHAR2 | `step3.error_message` or `step3.response_body` |
| CIUREFNBR | VARCHAR2 | `step3.CIURefNbr` |

**Output:** None.

---

### Step 7: Select Customer and Request

**Action type:** Oracle → Custom SQL query (SELECT)
**Connection:** `MIG_WM_GLD_Oracle_Connection`

**SQL:**
```sql
SELECT DISTINCT
  t1.ACCCUSTOMERID,
  t1.CUSTOMERNBR,
  t1.CUSTOMERTYPE,
  t1.BUSINESSNAME,
  t1.FIRSTNAME,
  t1.MIDDLENAME,
  t1.LASTNAME,
  t1.ADDRESSLINE1,
  t1.ADDRESSLINE2,
  t1.ADDRESSLINE3,
  t1.ADDRESSLINE4,
  t1.CITY,
  t1.STATE,
  t1.ZIP,
  t1.COUNTRYCODE,
  t1.SSNTIN,
  t1.PARTYTYPE,
  t1.DOB,
  t2.ACCCHECKREQUESTID,
  t2.APPLICATIONNBR,
  t2.CHANNEL,
  t2.LOB,
  t2.PRODUCTCODE,
  t2.SUBPRODUCTCODE,
  t2.POSTBACK,
  t2.COMPLIANCEREPLYEMAIL,
  t2.CIUREFNBR,
  t2.REQUESTTIMESTAMP
FROM GLD_SCHEMA.ACCCUSTOMER t1
JOIN GLD_SCHEMA.ACCCHECKREQUEST t2
  ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID
WHERE t2.CIUREFNBR = ?
```

**Input:** `step3.CIURefNbr` (bind parameter `?`)

**Output data pills (28 columns):** All accessible as `step7.rows[0].<COLUMN_NAME>`. See `Workato_Map_Field_Mappings.xlsx → SelectCustomer_Output` tab for the full pill path table.

**Recipe response:** Return `step7.rows[0]` as the callable recipe response body (HTTP 200).

---

### Optional: Purge Data Recipe

**Recipe name:** `MIG_WM_GLD_PurgeData_Recipe`
**Trigger:** Scheduled (daily or weekly — confirm schedule with ops team)
**Step 1 action:** Oracle → Stored procedure `ACCPURGEDATA` — no input parameters required.

---

## 5. webMethods → Workato Construct Mapping

Quick-reference table from `Agent Bridge Web Methods to Workato Component Mapping.xlsx`:

| # | webMethods Construct | webMethods XML | Workato Equivalent | Workato Block |
|---|---|---|---|---|
| 1 | Workflow | `<SEQUENCE>` | Recipe | Recipe trigger + action chain |
| 2 | TRY | `<SEQUENCE catch="true">` | Error monitor (try block) | `handle_error` block |
| 3 | CATCH | Error path of catch sequence | Error handler | `on_error` block |
| 4 | FINALLY | Post-processing sequence | After-recipe actions | Separate end step |
| 5 | IF | `<BRANCH evaluateLabels="true">` | Conditional action | `if/elsif/else` block |
| 6 | CASE | `<BRANCH>` labeled paths | Conditional branches | `elsif` clause (value match) |
| 7 | ELSE | `<SEQUENCE>` default path | Else branch | `else` clause |
| 8 | ELSEIF | Chained `<BRANCH>` | elsif branch | `elsif` clause |
| 9 | BRANCH | Parallel `<SEQUENCE>` blocks | Parallel step | Async callable recipes (no native parallel) |
| 10 | SWITCH | `<BRANCH switch="...">` | Value-based routing | `if/elsif` chain (value ==) |
| 11 | SEQUENCE | `<SEQUENCE>` | Sequential actions | Default action order |
| 12 | LOOP | `<LOOP count="..." ref="...">` | Repeat for each | `repeat` / `for each item` action |
| 13 | DO | DO-WHILE loop | Repeat block | `repeat` with exit condition |
| 14 | WHILE | WHILE loop | Conditional repeat | `repeat` with while condition |
| 15 | REPEAT | REPEAT-UNTIL loop | Repeat until | `repeat` with until condition |
| 16 | UNTIL | Stop condition in loop | Exit condition | `repeat` exit_condition field |
| 17 | CONTINUE | Skip iteration | Skip to next | Conditional `if` block to skip |
| 18 | BREAK | Exit loop early | Exit loop | Flag variable pattern |
| 19 | EXIT | `<EXIT signal="failure">` | Stop recipe | `stop` action |
| 20 | INVOKE (DB) | `<INVOKE service="adapter:...">` | Database action | Oracle connector action |
| 21 | MAP | `<MAP>` | Data mapping | Formula fields / lookup table |
| 22 | INVOKE (HTTP) | `<INVOKE service="pub.client:http">` | HTTP action | HTTP connector action |

---

## 6. Missing Components / Manual Steps

The following items are gaps that cannot be resolved from the source artifacts alone. An engineer must resolve each before the recipe can run end-to-end.

| # | Gap / Missing Item | Impact | Resolution |
|---|---|---|---|
| 1 | **External CIU HTTP connector** | Cannot call external compliance system | Create HTTP connection in Workato GUI with CIU endpoint URL — **needs URL from SME** |
| 2 | **Oracle DB connection credentials (password)** | Recipe cannot authenticate without `GLD_SCHEMA` password | Create Oracle connection in Workato GUI: host `CSC06DSHORA1S`, port `1522`, SID `ILMSUM`, schema `GLD_SCHEMA` — retrieve password from IS Admin UI (Adapters → JDBC → ExpressOS) |
| 3 | **Trigger — no flow.xml found** | Unknown what originally triggered the compliance check | Use **callable recipe (HTTP POST)** as trigger — client systems call this recipe endpoint synchronously |
| 4 | **accCheckRequestID OUT from SP** | Oracle `ACCLOGCHECKREQUEST` SP does not return OUT params via Workato standard action | Add a `SELECT ACCCHECKREQUESTID FROM ACCCHECKREQUEST WHERE REQUESTORSYSTEMREQUESTID=?` step immediately after Step 1 to retrieve the generated ID |
| 5 | **CIU result field mapping** | No source mapping shows where CIU sets `CHECK_RESULT` | Add formula field: `if step3.response_code == "200" then "TRUE" else "FALSE" end` — adjust when CIU response schema is known |

---

## 7. Recipe JSON Structure (Reference Skeleton)

The structure below shows the high-level shape of the Workato recipe. Data pills are shown as `<placeholder>` — fill in from the data pill tree in the Workato recipe editor.

```json
{
  "name": "MIG_WM_GLDComplianceAdapterServices_Recipe",
  "trigger": {
    "provider": "callable_recipe",
    "name": "receive_request",
    "input": {
      "schema": "<25-field JSON schema from Section 4 Trigger table>"
    }
  },
  "actions": [
    {
      "provider": "workato",
      "name": "handle_errors",
      "block": [
        {
          "provider": "oracle",
          "name": "run_stored_procedure",
          "label": "Step 1: Log Check Request",
          "input": {
            "procedure": "GLD_SCHEMA.ACCLOGCHECKREQUEST",
            "parameters": "<25 trigger field mappings>"
          }
        },
        {
          "provider": "oracle",
          "name": "select_rows",
          "label": "Step 1b: Get accCheckRequestID",
          "input": {
            "sql": "SELECT ACCCHECKREQUESTID FROM GLD_SCHEMA.ACCCHECKREQUEST WHERE REQUESTORSYSTEMREQUESTID = ?",
            "parameters": ["<trigger.RequestorSystemRequestID>"]
          }
        },
        {
          "provider": "oracle",
          "name": "run_stored_procedure",
          "label": "Step 2: Log Check Request XML",
          "input": {
            "procedure": "GLD_SCHEMA.LOGXMLREQUEST",
            "parameters": {
              "APPLICATIONID": "<accCheckRequestID>",
              "REQUEST": "<trigger JSON>",
              "REQUESTIDENTIFIER1": "<trigger.CustomerNbr>",
              "REQUESTIDENTIFIER2": "<trigger.ApplicationNbr>",
              "REQUESTIDENTIFIER3": "<trigger.Channel>"
            }
          }
        },
        {
          "provider": "http",
          "name": "post",
          "label": "Step 3: Call CIU — PLACEHOLDER",
          "input": {
            "url": "<CIU_ENDPOINT_URL — get from SME>",
            "body": "<customer fields from trigger>"
          }
        },
        {
          "provider": "oracle",
          "name": "run_stored_procedure",
          "label": "Step 4: Update CIU Reference Number",
          "input": {
            "procedure": "GLD_SCHEMA.ACCUPDATECIUREFNBR",
            "parameters": {
              "ACCCHECKREQUESTID": "<accCheckRequestID>",
              "CIUREFNBR": "<step3.CIURefNbr>"
            }
          }
        },
        {
          "provider": "workato",
          "name": "if",
          "label": "Step 5: Check Passed?",
          "condition": "<step3.CheckResult> == 'TRUE'",
          "if_block": [
            {
              "provider": "oracle",
              "name": "run_stored_procedure",
              "label": "Step 6a: Log Check Reply",
              "input": {
                "procedure": "GLD_SCHEMA.ACCLOGCHECKREPLY",
                "parameters": {
                  "CIUREFNBR": "<step3.CIURefNbr>",
                  "CHECKTYPE": "<trigger.CustomerType>",
                  "RESULT": "true"
                }
              }
            }
          ],
          "else_block": [
            {
              "provider": "oracle",
              "name": "run_stored_procedure",
              "label": "Step 6b: Log Check Reply Error",
              "input": {
                "procedure": "GLD_SCHEMA.ACCLOGCHECKREPLYERROR",
                "parameters": {
                  "ERRORTYPE": "<step3.error_type>",
                  "ERRORCODE": "<step3.error_code>",
                  "ERRORDESC": "<step3.error_message>",
                  "CIUREFNBR": "<step3.CIURefNbr>"
                }
              }
            }
          ]
        },
        {
          "provider": "oracle",
          "name": "select_rows",
          "label": "Step 7: Select Customer and Request",
          "input": {
            "sql": "SELECT DISTINCT t1.*, t2.* FROM GLD_SCHEMA.ACCCUSTOMER t1 JOIN GLD_SCHEMA.ACCCHECKREQUEST t2 ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID WHERE t2.CIUREFNBR = ?",
            "parameters": ["<step3.CIURefNbr>"]
          }
        }
      ],
      "on_error": [
        {
          "provider": "oracle",
          "name": "run_stored_procedure",
          "label": "Error: Log Reply Error",
          "input": {
            "procedure": "GLD_SCHEMA.ACCLOGCHECKREPLYERROR",
            "parameters": {
              "ERRORTYPE": "<error.type>",
              "ERRORCODE": "<error.code>",
              "ERRORDESC": "<error.message>",
              "CIUREFNBR": "<step3.CIURefNbr or empty>"
            }
          }
        },
        {
          "provider": "workato",
          "name": "stop",
          "label": "Return error response",
          "input": {
            "message": "<error.message>"
          }
        }
      ]
    }
  ]
}
```

---

## 8. Build Checklist

Use this checklist when building the recipe in the Workato GUI:

- [ ] Create Oracle DB connection (`MIG_WM_GLD_Oracle_Connection`) — authorize with GLD_SCHEMA credentials
- [ ] Create HTTP connection for CIU — get endpoint URL from SME
- [ ] Create callable recipe with 25-field trigger input schema
- [ ] Add error monitor wrapping all steps
- [ ] Step 1: ACCLOGCHECKREQUEST SP — map all 25 parameters
- [ ] Step 1b: SELECT to retrieve ACCCHECKREQUESTID — use REQUESTORSYSTEMREQUESTID as filter
- [ ] Step 2: LOGXMLREQUEST SP — 5 parameters including JSON-serialized trigger payload
- [ ] Step 3: HTTP POST to CIU — wire all customer fields; BLOCKED on endpoint URL
- [ ] Step 4: ACCUPDATECIUREFNBR SP — accCheckRequestID + CIURefNbr
- [ ] Step 5: if/else on CheckResult == "TRUE"
- [ ] Step 6a (TRUE): ACCLOGCHECKREPLY SP — 3 parameters
- [ ] Step 6b (ELSE): ACCLOGCHECKREPLYERROR SP — 4 parameters
- [ ] Step 7: Custom SELECT DISTINCT JOIN — CIURefNbr as bind param, return 28 columns
- [ ] Wire callable recipe response to return Step 7 result rows
- [ ] Test end-to-end with a sample customer payload (use Workato test runner)
- [ ] (Optional) Create `MIG_WM_GLD_PurgeData_Recipe` — scheduled trigger + ACCPURGEDATA SP

---

*Document prepared by the iPaaS Migration Agent. Last updated: 2026-06-18.*
