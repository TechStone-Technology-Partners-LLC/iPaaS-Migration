# Component Analysis: GLDComplianceAdapterEnv Package

---

## 1. Package Overview

| Attribute | Value |
|---|---|
| **Package Name** | `GLDComplianceAdapterEnv` |
| **Release Label** | `GLDComplianceAdapterEnv20080327-1` |
| **Version** | `1.0` (Build 1) |
| **Build Date** | 2008-03-27 14:01:54 EDT |
| **Source Server Version** | webMethods Integration Server 6.5 |
| **Target Server Version** | webMethods Integration Server 6.5 |
| **JVM Version** | 1.4.2 |
| **Publisher / Source Host** | `cwb02dwmis02.keybank.com` |
| **Package Type** | Full (not a patch) |
| **System Package** | No |
| **Enabled** | Yes |
| **Startup / Shutdown Services** | None defined |
| **Adapter Type** | JDBC Adapter (`JDBCAdapter`) |
| **Connection Factory Class** | `com.wm.adapter.wmjdbc.connection.JDBCConnectionFactory` |
| **Datasource Class** | `oracle.jdbc.pool.OracleDataSource` |
| **DB Host / SID** | `CSC06DSHORA1S` / SID: `ORASHRT4` |
| **DB Port** | `1522` |
| **DB Schema / User** | `GLD_SCHEMA` |
| **Transaction Mode** | `NO_TRANSACTION` |
| **Connection Pooling** | Enabled |

---

## 2. Namespace / Package Structure

```
GLDComplianceAdapterEnv/
├── manifest.bak
├── manifest.rel
├── manifest.v3
└── ns/
    ├── GLDComplianceAdapterEnv/
    │   ├── node.idf              ← Package root namespace node
    │   └── ExpressOS/
    │       └── node.ndf          ← JDBC Connection Alias definition
    └── GLDMessageLogAdapterEnv/
        └── node.idf              ← Secondary namespace node (no services defined)
```

> **Note:** No `flow.xml` service files, no JDBC adapter service `node.ndf` files beyond the connection alias, and no IS Document Type definitions were included in the provided source files. The analysis below is based solely on the files provided.

---

## 3. Service Inventory

| # | Service Name | Namespace | DB Operation | SQL Object | Notes |
|---|---|---|---|---|---|
| — | *(No adapter services found)* | — | — | — | Only a connection alias node was provided; no service `node.ndf` files were included in the package extract |

---

## 4. Detailed Service Definitions

> **⚠️ No service definition files (`node.ndf` of type `AdapterService` or `flow.xml`) were present in the provided package extract.** The package, as supplied, contains only:
> - Package manifest metadata
> - One JDBC Connection Alias (`ExpressOS`)
> - Two namespace interface nodes (`node.idf`)

If additional service files exist in the full package tree (e.g., under subdirectories of `ns/GLDComplianceAdapterEnv/` such as `ns/GLDComplianceAdapterEnv/services/` or similar), they were not included in this analysis request and must be provided for complete service-level documentation.

---

## 5. Connections

### 5.1 Connection Alias: `GLDComplianceAdapterEnv:ExpressOS`

This connection alias is defined in `ns/GLDComplianceAdapterEnv/ExpressOS/node.ndf`. The binary-encoded `IRTNODE_PROPERTY` field has been decoded to extract the following properties:

| Property | Value |
|---|---|
| **Alias / Node Name** | `GLDComplianceAdapterEnv:ExpressOS` |
| **Node Type** | `ConnectionData` |
| **Adapter Type Name** | `JDBCAdapter` |
| **Connection Factory Class** | `com.wm.adapter.wmjdbc.connection.JDBCConnectionFactory` |
| **Datasource Class** | `oracle.jdbc.pool.OracleDataSource` |
| **DB Server Name (Host)** | `CSC06DSHORA1S` |
| **Database Name (SID/Service)** | `ORASHRT4` |
| **Port Number** | `1522` |
| **DB Username** | `GLD_SCHEMA` |
| **Password** | `**REDACTED**` *(stored encrypted in node.ndf)* |
| **Transaction Type** | `NO_TRANSACTION` |
| **Network Protocol** | *(empty — defaults to TCP)* |
| **Driver Type** | `thin` *(Oracle JDBC thin driver)* |
| **Other Properties** | `driverType=thin` |

### 5.2 Connection Pool Settings

| Pool Parameter | Value |
|---|---|
| **Poolable** | `true` |
| **Minimum Pool Size** | `1` |
| **Maximum Pool Size** | `10` |
| **Pool Increment Size** | `%` *(encoded — likely a percentage or fixed increment)* |
| **Blocking Timeout** | `10000` ms |
| **Expire Timeout** | `+` *(encoded — likely unlimited or a specific value)* |
| **Startup Retry Count** | `0` |
| **Startup Backoff Seconds** | `'` *(encoded)* |
| **Connection Enabled** | `#` *(encoded — assumed true/enabled)* |

### 5.3 Derived JDBC Connection URL

Based on the decoded Oracle thin driver parameters:

```
jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHRT4
```

> **⚠️ Note:** The exact JDBC URL format may be `jdbc:oracle:thin:@//CSC06DSHORA1S:1522/ORASHRT4` if the target is an Oracle service name rather than a SID. This must be confirmed with the DBA.

### 5.4 Connection: `GLDMessageLogAdapterEnv` Namespace

| Property | Value |
|---|---|
| **Node Name** | `GLDMessageLogAdapterEnv` |
| **Node Type** | `interface` |
| **Connection Alias** | *(None defined — this is a namespace container only)* |

No connection alias or service definitions were found under the `GLDMessageLogAdapterEnv` namespace in the provided files.

---

## 6. Flow Services

> **No flow service files (`flow.xml`) were present in the provided package extract.**

If flow services exist in the full package, they would be located under paths such as:
```
ns/GLDComplianceAdapterEnv/<ServiceName>/flow.xml
ns/GLDComplianceAdapterEnv/<ServiceName>/node.ndf
```

These must be provided for flow orchestration analysis.

---

## 7. Data Documents / IS Document Types

> **No IS Document Type definitions (record/document schemas) were found in the provided files.**

Document types in webMethods IS are typically stored as `node.ndf` files with `node_type = Record` or as separate schema files. None were present in this extract.

---

## 8. Migration Notes

### 8.1 Critical Gaps — Items Requiring Additional Files

| # | Gap | Impact | Action Required |
|---|---|---|---|
| 1 | **No adapter service `node.ndf` files provided** | Cannot document any stored procedure calls, SELECT queries, or DML operations | Provide full package directory tree including all service subdirectories |
| 2 | **No `flow.xml` files provided** | Cannot document orchestration logic, branching, mappings, or pipeline transformations | Provide all flow service directories |
| 3 | **`GLDMessageLogAdapterEnv` namespace is empty** | Unknown whether this namespace contains services not extracted | Confirm if this namespace has a separate package or if services are missing from the extract |
| 4 | **Binary-encoded connection properties** | Some pool timeout values could not be precisely decoded from Base64/custom encoding | Validate pool settings directly on the source IS server via Administrator UI |

### 8.2 Architecture / DBA Clarification Items

| # | Item | Details |
|---|---|---|
| 1 | **Oracle SID vs. Service Name** | `ORASHRT4` — confirm whether this is a SID or Oracle service name; affects Boomi connection URL format |
| 2 | **`ORASHRT4` environment** | Name suggests `ORA` + `SHR` (shared?) + `T4` — likely a non-production/test environment; confirm target environment for migration |
| 3 | **`GLD_SCHEMA` credentials** | Obtain current credentials from the secrets vault; the encrypted password in `node.ndf` uses webMethods IS internal encryption and cannot be directly reused |
| 4 | **`NO_TRANSACTION` mode** | Verify whether any services in the package require transactional behavior; if so, Boomi connection must be configured with appropriate transaction management |
| 5 | **Oracle JDBC thin driver** | Boomi uses its own Oracle connector; confirm `ojdbc` version compatibility with target Oracle DB version |
| 6 | **`CSC06DSHORA1S` hostname** | Confirm DNS/network reachability from Boomi Atom/Molecule host; may require firewall rules on port `1522` |

### 8.3 Boomi Migration Mapping

| webMethods Component | Boomi Equivalent |
|---|---|
| JDBC Adapter Connection Alias (`ExpressOS`) | Boomi **Oracle Database V2 Connection** component |
| Connection pool (min=1, max=10) | Boomi Atom/Molecule container-level connection pooling |
| `NO_TRANSACTION` | Boomi connector default (no explicit transaction group) |
| `oracle.jdbc.pool.OracleDataSource` | Boomi Oracle connector (built-in; no manual driver class needed) |
| JDBC Adapter Service (SELECT) | Boomi **Database V2 Query** operation |
| JDBC Adapter Service (Stored Procedure) | Boomi **Database V2 Execute Stored Procedure** operation |
| JDBC Adapter Service (INSERT/UPDATE) | Boomi **Database V2 Execute** or **Upsert** operation |
| Flow Service | Boomi **Process** (with shapes: Decision, Map, Connector, etc.) |
| IS Document Type (Record) | Boomi **JSON/XML Profile** or **Database Profile** |
| Package-level namespace (`GLDMessageLogAdapterEnv`) | Boomi **Component Folder** grouping |

### 8.4 Risk Flags

| Risk | Severity | Notes |
|---|---|---|
| JVM 1.4.2 compiled artifacts | 🔴 High | webMethods IS 6.5 / JVM 1.4.2 era — any custom Java services will need recompilation or replacement |
| 2008-era build | 🟡 Medium | Long-running legacy integration; undocumented business rules likely embedded in services not yet provided |
| Encrypted password in `node.ndf` | 🟡 Medium | webMethods IS password encryption is proprietary; password must be retrieved from IS Admin or secrets management before decommissioning |
| Missing service files | 🔴 High | Without service definitions, migration scope cannot be estimated or completed |

---

## 9. Summary

The **GLDComplianceAdapterEnv** package is a **legacy webMethods IS 6.5 JDBC Adapter package** built in 2008, targeting an **Oracle database** (`ORASHRT4` on host `CSC06DSHORA1S:1522`) under the schema `GLD_SCHEMA`. The package defines **one JDBC connection alias** (`ExpressOS`) configured with Oracle thin driver, connection pooling (1–10 connections), and no transaction management.

**The provided file extract is incomplete** — it contains only the package manifests and the connection alias definition. No adapter service definitions, flow services, or document types were included. A complete migration analysis requires the full package directory tree to be re-extracted and provided.

---

*Document prepared by: Senior Integration Architect | Date: Based on source files dated 2008-03-27*