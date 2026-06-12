# GLD Compliance Adapter Services — Migration Approval Brief

**Migration:** webMethods → Boomi  
**Package:** GLDComplianceAdapterServices  
**Prepared for:** Review and sign-off before Boomi build begins  
**Technical Reference:** `WebMethods/MD/PackageAnalysis.md`

---

## 1. What Are We Building in Boomi?

We are recreating 9 components in Boomi that together replace the `GLDComplianceAdapterServices` webMethods package. These components handle all Oracle database communication for the GLD compliance check workflow.

### The 9 Boomi Components

| # | Component | Type | What It Does |
|---|---|---|---|
| 1 | GLD Database Connection | Connection | Connects Boomi to the Oracle GLD database (`CSC06DSHORA1S:1522`, schema `GLD_SCHEMA`) |
| 2 | Log Check Request | Database Operation | Calls the `ACCLOGCHECKREQUEST` stored procedure to save a new compliance check request |
| 3 | Log Check Request XML | Database Operation | Calls the `LOGXMLREQUEST` stored procedure to save the raw XML audit copy |
| 4 | Log Check Reply | Database Operation | Calls the `ACCLOGCHECKREPLY` stored procedure to record the pass/fail outcome |
| 5 | Log Check Reply Error | Database Operation | Calls the `ACCLOGCHECKREPLYERROR` stored procedure to record error details |
| 6 | Select Customer and Request | Database Operation | Runs a SELECT query joining two tables to retrieve the full customer + request record |
| 7 | Update CIU Reference Number | Database Operation | Calls the `ACCUPDATECIUREFNBR` stored procedure to link the internal request to the CIU reference |
| 8 | Purge Data | Database Operation | Calls the `ACCPURGEDATA` stored procedure to remove old records (maintenance) |
| 9 | GLDComplianceAdapterServices Process | Integration Process | The main process that orchestrates all of the above in the correct order |

---

## 2. How the Boomi Process Works — Narrative Flow

The integration runs as follows when a compliance check is needed:

**Step 1 — Receive the request**  
The process starts when it receives a compliance check request containing the customer's personal and application details (name, address, SSN/TIN, DOB, product information).

**Step 2 — Save to the database**  
All 25 fields from the incoming request are written to the Oracle database using the `Log Check Request` operation. Oracle generates a unique Request ID that will be used to track this compliance check throughout its lifecycle.

**Step 3 — Save the audit copy**  
The full XML payload of the original request is saved to the database using `Log Check Request XML`. This creates an unmodified archive copy for regulatory audit purposes.

**Step 4 — Contact the external CIU system**  
The compliance check request is forwarded to the external CIU (Compliance Identity Unit) system. CIU returns a reference number that links the external record to our internal record.  
> ⚠️ *The CIU endpoint is not defined in this package — this must be provided separately.*

**Step 5 — Save the CIU reference number**  
The CIU reference number is written back into the original request record using `Update CIU Reference Number`.

**Step 6 — Wait for the result**  
The CIU system processes the request and returns a result asynchronously (pass or fail).

**Step 7 — Retrieve full context**  
Using the CIU reference number, the process looks up the complete customer and request details with `Select Customer and Request`.

**Step 8 — Record the outcome**  
- If the compliance check **passed**: `Log Check Reply` records the success with Check Type and CIU Reference
- If the compliance check **failed or errored**: `Log Check Reply Error` records the error type, code, and description

**Step 9 — Maintenance**  
On a scheduled basis (independent of live checks), `Purge Data` removes compliance records older than the configured threshold from the Oracle database.

---

## 3. Data The Integration Handles

### Fields Sent to the Database on Every Request

| Category | Fields |
|---|---|
| Customer Identity | First Name, Middle Name, Last Name, Business Name, Customer Number, Customer Type, Party Type |
| Address | Address Lines 1–4, City, State (2 chars), ZIP, Country Code |
| **Sensitive / PII** | **SSN or Tax ID (SSNTIN)**, **Date of Birth (DOB)** |
| Product / Application | Application Number, Channel, Line of Business, Product Code, Sub-Product Code, Post-Back |
| Contact | Compliance Reply Email |
| Tracking | Requestor's System Request ID |

### Fields Generated or Returned During the Process

| Field | When It Appears | What It Is |
|---|---|---|
| Internal Request ID | After Step 2 | Oracle-generated unique ID for the compliance record |
| CIU Reference Number | After Step 4 | External reference assigned by the CIU compliance system |
| Compliance Result | After Step 6 | TRUE (passed) or FALSE (failed) |

---

## 4. Database Tables Involved

Two Oracle tables are written to and read from by this integration:

### ACCCUSTOMER — Customer Master
Stores one row per customer. The compliance request starts here.

| Column | Meaning |
|---|---|
| ACCCUSTOMERID | Unique customer ID (generated by Oracle) |
| CUSTOMERNBR | Customer number from source system |
| FIRSTNAME / MIDDLENAME / LASTNAME | Customer name |
| ADDRESSLINE1–4, CITY, STATE, ZIP | Address |
| SSNTIN | Social Security Number or Tax ID *(sensitive)* |
| DOB | Date of birth *(sensitive)* |
| CUSTOMERTYPE, PARTYTYPE, BUSINESSNAME | Classification fields |

### ACCCHECKREQUEST — Compliance Request Log
Stores one row per compliance check. Linked to ACCCUSTOMER by the internal ID.

| Column | Meaning |
|---|---|
| ACCCHECKREQUESTID | Unique request ID (generated by Oracle) |
| ACCCUSTOMERID | Links back to ACCCUSTOMER |
| APPLICATIONNBR, CHANNEL, LOB | What product/channel triggered the check |
| PRODUCTCODE, SUBPRODUCTCODE | Product details |
| CIUREFNBR | Filled in after CIU responds (initially empty) |
| REQUESTTIMESTAMP | When the check was submitted |

---

## 5. Data Transformations — What Changes and Why

Most fields pass through unchanged ("direct copy"). The two exceptions:

| Field | Change Made | Reason |
|---|---|---|
| Date of Birth | Format converted from text `yyyy-MM-dd` → Oracle `DATE` type | Oracle's stored procedure expects a native Oracle date, not a string |
| Compliance Result | Boolean `true/false` → text `'TRUE'` / `'FALSE'` | The Oracle procedure expects text; webMethods passed a Boolean |

---

## 6. Risks and Considerations

### Sensitive Data (PII)
- SSN/TIN and Date of Birth flow through the Boomi integration and are stored in Oracle
- **Boomi process logging will be disabled** to prevent these values from appearing in integration audit logs
- The database-level controls (encryption, access, masking) remain the same — Boomi calls the same Oracle stored procedures as webMethods did

### External CIU System (Step 4)
- The external compliance system URL, credentials, and request format are **not part of this package**
- In webMethods, this was handled by a separate companion package (`GLDComplianceCheck`)
- **This is the most significant open item** — without the CIU endpoint, the Boomi process will be built with a placeholder for that step

### Database Credentials
- The Oracle database password is **not stored in the Boomi integration**
- It will be configured separately through Boomi's secure environment settings (equivalent to a secrets vault)

### Stored Procedure Logic
- The business logic inside each Oracle stored procedure (INSERT rules, validation, error handling) is not visible to the migration team — it runs entirely on the Oracle server
- Boomi's role is to **call** the procedures with the correct inputs — the procedure body is unchanged

---

## 7. Comparison: Before (webMethods) vs After (Boomi)

| Aspect | webMethods (Before) | Boomi (After) |
|---|---|---|
| Platform | webMethods IS 6.5 (2008, decommissioning) | Boomi AtomSphere (current, cloud-native) |
| Database Calls | 7 JDBC Adapter Services | 7 DatabaseV2 Operations (same Oracle stored procedures) |
| Connection Management | `GLDComplianceAdapterEnv:ExpressOS` alias | Boomi DatabaseV2 Connection component (same JDBC URL) |
| PII Logging | Dependent on IS logging config | Explicitly disabled in Boomi process config |
| Credentials | Stored in webMethods adapter config | Stored in Boomi Environment Extensions (secure) |
| Maintenance Purge | Scheduled IS trigger | Boomi scheduled process (same SP called) |
| Functionality | 100% preserved | 100% of database operations preserved |

---

## 8. What Needs Sign-Off Before Build

| # | Item | Owner | Decision Needed |
|---|---|---|---|
| 1 | **CIU system endpoint, credentials, and format** | Architecture / Business | Must be provided — blocks Step 4 of process |
| 2 | **Target database host** | Infrastructure / DBA | Confirm `CSC06DSHORA1S:1522/ILMSUM` is the correct database for the migrated environment |
| 3 | **Database password** | DBA / Security | Provide via Boomi Environment Extensions (not written here) |
| 4 | **PII handling confirmation** | Security / Compliance | Confirm that disabling Boomi logging for SSN/TIN fields meets compliance requirements |
| 5 | **Purge data threshold** | DBA | Confirm that the `ACCPURGEDATA` stored procedure retains the correct date threshold for the new environment |

---

## 9. What Remains After Build

Once the 9 Boomi components are created, the following manual steps must be completed in the Boomi user interface:

| # | Step | Who |
|---|---|---|
| 1 | Configure Oracle database password | Admin (via Environment Extensions) |
| 2 | Wire in the CIU connector (Step 4 placeholder) | Developer — needs CIU endpoint details |
| 3 | Set the process trigger (scheduled? API listener?) | Developer — depends on how GLDComplianceCheck triggers this |
| 4 | Test with a sample compliance request | QA / Developer |

---

*This document is a business-readable summary of `WebMethods/MD/PackageAnalysis.md`.  
For complete technical field-level specifications, refer to that document.*
