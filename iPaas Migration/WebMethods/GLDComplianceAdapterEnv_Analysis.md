# WebMethods Package Analysis: GLDComplianceAdapterEnv

> **Purpose of this document**: Full reverse-engineering of the webMethods `GLDComplianceAdapterEnv` package for migration into Boomi. Every property extracted here maps directly to a Boomi component attribute.

---

## 1. Package Overview

| Property | Value |
|---|---|
| **Package Name** | `GLDComplianceAdapterEnv` |
| **Package Type** | Environment Package (`*Env` convention) |
| **Version** | 1.0 (Build 1) |
| **Release Label** | `GLDComplianceAdapterEnv20080327-1` |
| **Created** | 2008-03-27 14:01:54 EDT |
| **Published From** | `cwb02dwmis02.keybank.com` |
| **Source Server Version** | webMethods Integration Server 6.5 |
| **Target Server Version** | webMethods Integration Server 6.5 |
| **JVM Version** | 1.4.2 |
| **Release Type** | Full |
| **Enabled** | Yes |
| **System Package** | No |

### Package Architecture Pattern

This is an **environment-only package** — a standard webMethods pattern where:

- `GLDComplianceAdapter` (not included here) = the **logic package** containing flow services, triggers, mappings, and business logic.
- `GLDComplianceAdapterEnv` (this package) = the **environment package** containing connection credentials and pool settings specific to a deployment environment (DEV/QA/PROD).

**Boomi equivalent**: This package maps directly to Boomi **Connection components** and **Environment Extensions**. There is no flow logic in this package — only connectivity configuration.

---

## 2. Namespace Structure

The package declares two namespace interfaces (logical groupings):

| Namespace | Type | Description |
|---|---|---|
| `GLDComplianceAdapterEnv` | `interface` | Root namespace for compliance adapter connections |
| `GLDMessageLogAdapterEnv` | `interface` | Namespace for message log adapter connections |

> **Note**: Both are empty namespace containers in the committed files. The `GLDMessageLogAdapterEnv` namespace has a `node.idf` identity file but no connection node — its connection definition is either not committed or was in a separate sub-package.

---

## 3. Connection Node: `GLDComplianceAdapterEnv:ExpressOS`

This is the only fully-defined component in the package. It is a **JDBC Adapter connection node** targeting an Oracle database.

### 3.1 Adapter Identity

| Property | Value |
|---|---|
| **Node Name** | `ExpressOS` |
| **Full Qualified Name** | `GLDComplianceAdapterEnv:ExpressOS` |
| **Node Type** | `ConnectionData` |
| **Adapter Type** | `JDBCAdapter` |
| **Connection Factory Class** | `com.wm.adapter.wmjdbc.connection.JDBCConnectionFactory` |

### 3.2 Database Connection Properties

| Property | Value | Notes |
|---|---|---|
| **Datasource Class** | `oracle.jdbc.pool.OracleDataSource` | Oracle JDBC pooling datasource |
| **Driver Type** | `thin` | Oracle Thin JDBC driver (no Oracle client install needed) |
| **Server / Host** | `CSC06DSHORA1S` | Oracle DB hostname |
| **Database Name / SID** | `ORASHR4T` | Oracle SID/service name |
| **Port** | `1522` | Non-standard Oracle port (default is 1521) |
| **Username** | `GLD_SCHEMA` | Oracle schema/user |
| **Password** | `EtOk7oXXx0Y=OHKvmpqVk3AiPzwED0wMdw==` | **Encrypted** — webMethods proprietary encryption. Must be reset in Boomi. |
| **Transaction Type** | `NO_TRANSACTION` | No XA/distributed transactions |
| **Network Protocol** | *(empty)* | Uses default TCP |
| **Other Properties** | `driverType=thin` | Redundant confirmation of thin driver |

**Derived JDBC URL**:
```
jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHR4T
```

### 3.3 Connection Pool Properties

| Property | Value | Boomi Equivalent |
|---|---|---|
| **Poolable** | `true` | Connection pooling enabled |
| **Minimum Pool Size** | `1` | Min connections kept alive |
| **Maximum Pool Size** | `10` | Max concurrent connections |
| **Pool Increment Size** | `%` (1 step) | Grow by 1 when needed |
| **Blocking Timeout** | `10000 ms` (10 seconds) | Max wait for a connection from pool |
| **Expire Timeout** | `+` (1 ms — effectively immediate) | Connection max lifetime |
| **Startup Retry Count** | `0` | No retries on startup failure |
| **Startup Backoff Seconds** | `'` (39 seconds) | Backoff between retries |
| **Connection Enabled** | `#` (enabled) | Connection is active |

---

## 4. Startup / Shutdown Services

| Service Type | Value |
|---|---|
| Startup Services | *(none defined)* |
| Shutdown Services | *(none defined)* |
| Replication Services | *(none defined)* |

---

## 5. Dependencies and ACLs

| Property | Value |
|---|---|
| Required Packages | *(none declared)* |
| ACL (Access Control List) | *(none defined — open access)* |

---

## 6. What Is NOT Present in This Package

The following components are **expected to exist in the companion logic package** (`GLDComplianceAdapter`) but are **not present** in this `Env` package:

| Missing Component Type | What to Look For |
|---|---|
| **Flow Services** | `.flow` files — the business logic steps (equivalent to Boomi process shapes) |
| **Triggers** | `trigger.cnf` files — JMS/messaging triggers that fire flow services |
| **Document Types** | IS Document Type definitions (equivalent to Boomi profiles) |
| **Adapter Services** | JDBC query/execute services using the `ExpressOS` connection |
| **Mappings** | Field-level transformations within flow services |
| **Scripting** | Java services or custom scripts inside flow steps |
| **Schemas** | XSD or flat-file schemas used by document types |
| **GLDMessageLogAdapterEnv connection** | The second namespace has no connection node committed |

> **Action Required**: Obtain the `GLDComplianceAdapter` (non-Env) package to capture all flow services, triggers, and mappings. This `Env` package alone is insufficient to reconstruct the full integration.

---

## 7. Boomi Migration Mapping

### 7.1 Connection Component

| Boomi Component | Type | Configuration |
|---|---|---|
| `MIG_WM_ExpressOS_Connection` | **Database Connection** | Oracle thin JDBC |

**Boomi Connection Settings**:

```
Connection Type:  Database (DatabaseV2 connector)
Driver:           Oracle (built-in)  OR  Custom JAR: ojdbc.jar
Host:             CSC06DSHORA1S
Port:             1522
Database:         ORASHR4T
Username:         GLD_SCHEMA
Password:         [RESET — original is webMethods-encrypted, unusable in Boomi]
Connection URL:   jdbc:oracle:thin:@CSC06DSHORA1S:1522:ORASHR4T
```

**Pool Settings** (map to Boomi Connection → Advanced):
```
Max Connections:  10
Min Connections:  1
Connection Timeout: 10000 ms
```

### 7.2 Environment Extension Recommendation

Since this was an environment-specific package in webMethods, configure the Oracle credentials as **Boomi Environment Extensions** rather than hardcoding them in the Connection component. This preserves the DEV/QA/PROD separation pattern.

### 7.3 Message Log Adapter

The `GLDMessageLogAdapterEnv` namespace indicates a second adapter exists for message logging. This likely means:
- A separate Oracle DB connection for writing message/audit logs
- Possibly the same Oracle instance with a different schema, or a separate logging DB

A second Boomi connection component should be created once the connection details are obtained:
```
MIG_WM_MessageLog_Connection  (Database Connection — details TBD)
```

---

## 8. Open Questions / Pre-Migration Checklist

- [ ] **Obtain `GLDComplianceAdapter` package** — contains the actual flow services, triggers, mappings
- [ ] **Confirm Oracle host is reachable** — `CSC06DSHORA1S:1522` — verify from Boomi Atom host
- [ ] **Reset database password** — the webMethods-encrypted value cannot be reused in Boomi
- [ ] **Confirm Oracle SID vs Service Name** — verify whether `ORASHR4T` is an SID or a service name (affects JDBC URL format: `@host:port:SID` vs `@//host:port/service`)
- [ ] **GLDMessageLogAdapterEnv connection details** — host, port, schema, credentials for the log DB
- [ ] **Transaction mode** — `NO_TRANSACTION` in webMethods maps to Boomi's default; confirm no XA is needed
- [ ] **Oracle JDBC driver JAR** — confirm Boomi Atom has `ojdbc8.jar` (or appropriate version) available

---

## 9. File Inventory

| File | Type | Content |
|---|---|---|
| `manifest.rel` | Release manifest | Package metadata: name, version, build date, source server |
| `manifest.bak` | Package manifest backup | Runtime config: enabled flag, startup/shutdown services, ACLs |
| `manifest.v3` | Package manifest v3 | Same as `.bak` — duplicate for version compatibility |
| `ns/GLDComplianceAdapterEnv/node.idf` | Namespace identity | Declares `GLDComplianceAdapterEnv` as namespace interface |
| `ns/GLDComplianceAdapterEnv/ExpressOS/node.ndf` | **Connection node definition** | Full JDBC connection config (binary-encoded, decoded above) |
| `ns/GLDMessageLogAdapterEnv/node.idf` | Namespace identity | Declares `GLDMessageLogAdapterEnv` as namespace interface |
| `pub/index.html` | Package homepage | Static HTML — no technical content |

---

*Analysis generated: 2026-06-01 | Source: webMethods IS 6.5 package export*
