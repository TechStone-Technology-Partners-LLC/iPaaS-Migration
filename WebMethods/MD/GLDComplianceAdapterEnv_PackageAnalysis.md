# Package Analysis Document: GLDComplianceAdapterEnv → Workato

**Source package:** `WebMethods/GLDComplianceAdapterEnv/` (webMethods Integration Server 6.5, built 2008-03-27, host `cwb02dwmis02.keybank.com`)
**Raw file inventory decoded from:** `manifest.v3`, `ns/GLDComplianceAdapterEnv/node.idf`, `ns/GLDComplianceAdapterEnv/ExpressOS/node.ndf`, `ns/GLDMessageLogAdapterEnv/node.idf`
**Underlying technical decode:** `WebMethods/Analysis/GLDComplianceAdapterEnv_Analysis.md` (Boomi-oriented pass, 2025 session) — connection facts re-verified against the raw `IRTNODE_PROPERTY` blob for this document; all values below are independently confirmed.
**Mapping reference consulted:** `WebMethods/Agent Bridge Web Method to Workato Component Mapping(Component Mapping - WebMethods ).csv`

---

## ⚠️ Critical Scope Note — Read Before Approving

This package, **as extracted to disk, contains no executable integration logic.** It is a webMethods **adapter environment package** — a container for a JDBC connection alias only. There is:

- **No `flow.xml`** anywhere in the package (confirmed via full recursive listing)
- **No adapter service `node.ndf`** files (SELECT / stored procedure / DML service definitions)
- **No IS Document Type / Record schemas**
- **No triggers, no scheduled tasks, no listeners**

The only real artifact is one **JDBC Connection Alias** (`ExpressOS`) plus an empty sibling namespace (`GLDMessageLogAdapterEnv`) that holds no services either.

This means Steps 5–7 of this document (Business Rules, Error Handling, Recipe Structure) have **nothing to migrate** — there is no orchestration, branching, looping, or error-handling logic anywhere in this package to translate. What follows documents that honestly rather than inventing logic that isn't there.

---

## 1. Package Overview

| Attribute | Value |
|---|---|
| Package Name | `GLDComplianceAdapterEnv` |
| Release Label | `GLDComplianceAdapterEnv20080327-1` |
| Version | 1.0 (Build 1) |
| Build Date | 2008-03-27 14:01:54 EDT |
| Source IS Version | webMethods Integration Server 6.5 |
| Adapter Type | JDBC Adapter (`JDBCAdapter`) |
| Purpose (inferred) | Defines the shared Oracle DB connection (`ExpressOS`) that other GLD packages (e.g. `GLDComplianceAdapterServices`) invoke against. It is an **environment/connection-provider package**, not a functional integration. |
| Systems involved | webMethods IS ↔ Oracle DB (`GLD_SCHEMA`) |
| Data flow | None within this package — it only provisions a connection for consumption elsewhere |

---

## 2. Shapes & Logic Breakdown

| WebMethods Construct Found | Count | Workato Equivalent | Notes |
|---|---|---|---|
| Flow steps (SEQUENCE, BRANCH, LOOP, IF, TRY/CATCH, MAP, etc.) | **0** | N/A | None present — no `flow.xml` in package |
| Adapter services (INVOKE targets) | **0** | N/A | None present — no service `node.ndf` files |
| JDBC Connection Alias | 1 (`ExpressOS`) | **Workato Oracle Database connection** | The only real component |
| Namespace container (`GLDMessageLogAdapterEnv`) | 1 (empty) | Workato **Project/Folder** grouping (organizational only) | No services under it |

Per the mapping CSV, every listed construct (BRANCH→Recipe Function, IF→If condition, LOOP→Repeat While, TRY/CATCH→Handle Errors, MAP→Data Pills Mapping, etc.) is a **flow-logic** mapping. None of them apply here because there is no flow logic in this package — the CSV has no entry for "bare connection alias" because that isn't normally a standalone migration unit in webMethods; it's infrastructure other packages depend on.

---

## 3. Connections

### 3.1 `GLDComplianceAdapterEnv:ExpressOS` (JDBC Connection Alias)

| Property | Value |
|---|---|
| Adapter Factory | `com.wm.adapter.wmjdbc.connection.JDBCConnectionFactory` |
| Datasource Class | `oracle.jdbc.pool.OracleDataSource` |
| DB Host | `CSC06DSHORA1S` |
| DB Port | `1522` |
| Database Name (SID) | `ORASHRT4` |
| DB User / Schema | `GLD_SCHEMA` |
| Password | Encrypted in `node.ndf` (webMethods-proprietary; not reusable) |
| Transaction Mode | `NO_TRANSACTION` |
| Driver | Oracle thin driver |
| Pool Size | min 1 / max 10 |
| Blocking Timeout | 10000 ms |

**Derived JDBC URL:** `jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHRT4`

**Workato equivalent:** Native **Oracle DB connector connection**, configured with:
- Host: `CSC06DSHORA1S`
- Port: `1522`
- SID/Service: `ORASHRT4`
- Username: `GLD_SCHEMA`
- Password: must be re-obtained from secrets vault (cannot decrypt webMethods' internal encryption)

**⚠️ Flag — different target from existing Oracle connection already in Workato:** This account already has `MIG_WM_GLD_Oracle_Connection` (ID `19657520`) configured for the related `GLDComplianceAdapterServices`/`GLDFundingEngine` migrations — but that connection targets a **different Oracle SID** (per CLAUDE.md history, `ILMSUM`, not `ORASHRT4`). Same host and port, different database. These are almost certainly **not the same target** — this needs a **new, separate** Workato Oracle connection, not a reuse of `19657520`. Please confirm with the DBA/SME whether `ORASHRT4` is a distinct (e.g., pre-prod/test) database before we assume reuse is safe.

### 3.2 `GLDMessageLogAdapterEnv` namespace

Empty interface node — no connection, no services. Nothing to migrate.

---

## 4. Operations

**None.** No adapter services (SELECT / INSERT / UPDATE / stored procedure) are defined anywhere in the extracted package. There is nothing to invoke.

---

## 5. Data Mappings

**None.** No `flow.xml` MAP steps, no pipeline transformations, no document/record schemas were found.

---

## 6. Business Rules & Conditions

**None.** No IF/ELSE, BRANCH, SWITCH, or decision logic exists in this package.

---

## 7. Error Handling

**None.** No TRY/CATCH blocks exist in this package.

---

## 8. Equivalent Recipe Structure

Because this package has no trigger, no steps, and no logic, there is **no meaningful "recipe" to build** from it in the traditional sense (a recipe needs a trigger + at least one action). The only artifact worth carrying into Workato is the **connection definition** itself, so that downstream recipes (e.g., a future rebuild of `GLDComplianceAdapterServices`) can reference it.

Two honest options for Step 3, depending on what you actually want delivered:

| Option | What gets built | When it makes sense |
|---|---|---|
| **A. Connection-only** | Create the Workato Oracle connection (`GLD_ComplianceAdapterEnv_Oracle_Connection`) with the decoded host/port/SID/user, dummy password placeholder. No recipe, since there's no logic to trigger on. | If the goal is just to stand up the shared DB connection for later use |
| **B. Placeholder recipe** | A minimal callable recipe with a `workato_service/receive_request` trigger and a single Oracle "test connection" style action (e.g., a trivial `SELECT 1 FROM DUAL`), documented explicitly as a stand-in with no real business logic | If a recipe artifact is specifically required as a deliverable even though there's nothing to migrate |

---

## 9. Mapping Gaps / Deviations

| # | Gap | Severity | Action Required |
|---|---|---|---|
| 1 | No `flow.xml` / adapter service files in the extracted package | 🔴 High | If real logic exists in the source webMethods server, a fuller extract is needed. As supplied, there is nothing to migrate beyond the connection. |
| 2 | Connection SID (`ORASHRT4`) differs from the SID already wired into this Workato account's existing GLD Oracle connection (`ILMSUM`, ID `19657520`) | 🟡 Medium | Confirm with SME whether these are genuinely separate databases before deciding to reuse or create a new Workato connection |
| 3 | Password is webMethods-encrypted and cannot be reused directly | 🟡 Medium | Retrieve `GLD_SCHEMA` password from vault/DBA for the new Workato connection |
| 4 | Oracle SID vs. Service Name ambiguity (`ORASHRT4`) | 🟢 Low | Confirm JDBC connect string format with DBA — affects Workato Oracle connection config field |

---

## Recommendation

Given there is no orchestration logic in this package, I'd suggest confirming with you before building anything:
1. Do you want **Option A** (connection-only, no recipe) or **Option B** (placeholder recipe) from Section 8?
2. Should I proceed with a **new** Oracle connection (given the differing SID), or do you already know `ORASHRT4` and `ILMSUM` are the same target under different names?
3. If real flow logic for this package exists elsewhere (a fuller export), point me to it and I'll re-run this analysis — that would change this document substantially.

**Per the migration workflow, I will not create any Workato recipe or connection until you approve this document and answer the above.**
