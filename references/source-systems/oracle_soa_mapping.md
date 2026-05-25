# Oracle SOA Suite → Boomi Migration Mapping

This document is the authoritative reference for how Oracle SOA Suite (11g/12c) and Oracle EBS integration artifacts map to the canonical migration spec and ultimately to Boomi components.

---

## Oracle SOA Suite Architecture Overview

Oracle SOA Suite uses the **SCA (Service Component Architecture)** deployment model. Each composite (`.sar` zip) contains:

| File | Purpose |
|---|---|
| `composite.xml` | Composite topology: services (inbound), components (logic), references (outbound) |
| `*.bpel` | BPEL process definition (the integration logic) |
| `*.wsdl` | Interface contracts for services and references |
| `*.jca` | JCA adapter binding descriptors (which adapter, what JNDI name) |
| `*.xsd` | XML schemas for message types |
| `*.dvm` | Domain Value Maps (lookup tables) |
| `*.mplan` | Oracle Mediator routing rules |
| `*.rules` | Oracle Business Rules (Decision Service) |
| `*.task` | Oracle Human Task definitions |

---

## Component Type → Migration Approach

| SCA Component Type | Boomi Equivalent | Notes |
|---|---|---|
| **BPEL Process** | Process (full automatic migration) | Analyzer parses BPEL XML |
| **Oracle Mediator** | Decision / Route shapes | Content-based routing rules → Boomi Route step |
| **Oracle Human Task** | Boomi Flow (human task management) | Requires Boomi Flow platform — flag as gap |
| **Oracle Business Rules** | Decision step / Groovy script | Rules exported to Boomi Data Process Groovy |
| **Oracle BPMN Process** | Series of Boomi shapes | Map BPMN tasks to equivalent Boomi steps |
| **Spring Bean** | Groovy Data Process step | Direct code port from Java Spring to Groovy |

---

## BPEL Activity → Canonical Spec Step Mapping

### Core Activities

| BPEL Activity | Canonical Type | Boomi Shape | Notes |
|---|---|---|---|
| `<receive createInstance="yes">` | trigger | Start shape (type depends on adapter) | The process trigger |
| `<receive>` (mid-flow) | http_request | Set Properties + DPP | Correlation receive |
| `<invoke>` | adapter-dependent | Connector step | See JCA adapter table |
| `<reply>` | bpel_reply | Return Documents / WSS response | |
| `<assign>` | transform | Map or Set Properties | Simple → Set Properties, complex → Map |
| `<throw>` / `<rethrow>` | raise_error | Exception step | |
| `<exit>` / `<terminate>` | raise_error | Exception step | |
| `<empty>` | (dropped) | — | No-op, not emitted |

### Control Flow Activities

| BPEL Activity | Canonical Type | Boomi Shape | Behavioral Gap? |
|---|---|---|---|
| `<if>` / `<switch>` | choice_router | Decision step (2 paths) | No |
| `<if>` with multiple `<elseif>` | choice_router | Route step (3+ paths) | No |
| `<while>` / `<repeatUntil>` | foreach | Data Process (Split) | Loop count not always portable |
| `<forEach>` | foreach | Data Process (Split) | Similar to MuleSoft foreach |
| `<flow>` (parallel) | scatter_gather | Branch step | **GAP: Boomi Branch is sequential** |
| `<sequence>` | (transparent) | Inline | Children lifted into parent |
| `<pick>` (event-based) | choice_router | Decision step | Event routing simplified |
| `<wait>` (timer) | bpel_wait | **REVIEW REQUIRED** | **GAP: No native Boomi timer** |

### Fault Handling

| BPEL Element | Canonical Type | Boomi Shape |
|---|---|---|
| `<scope>` with `<faultHandlers>` | try_scope | Try/Catch |
| `<catch faultName="...">` | error_handler | Catch branch |
| `<catchAll>` | error_handler | Catch branch (catch all) |
| `<compensationHandler>` | custom | **REVIEW REQUIRED** |
| `<eventHandlers>` | custom | **REVIEW REQUIRED** — consider Event Streams |

---

## JCA Adapter → Boomi Connector Mapping

| Oracle JCA Adapter | Boomi Connector | Notes |
|---|---|---|
| **DB Adapter** (`oracle.tip.adapter.db.OracleDBAdapter`) | DatabaseV2 | Map SQL operations directly |
| **Oracle EBS Adapter** (`oracle.tip.adapter.apps.AppsAdapter`) | Oracle EBS native connector or REST | Search Boomi account first: `boomi-component-search.sh --name "%EBS%"` |
| **File Adapter** (`oracle.tip.adapter.file.FileAdapter`) | Disk V2 (local) | |
| **FTP Adapter** (`oracle.tip.adapter.ftp.FTPAdapter`) | Disk V2 (SFTP/FTP) | |
| **JMS Adapter** (`oracle.tip.adapter.jms.IJmsAdapter`) | Event Streams or JMS connector | Prefer Event Streams for new implementations |
| **AQ Adapter** (`oracle.tip.adapter.aq.AQAdapter`) | Event Streams | Oracle Advanced Queuing → Event Streams topic |
| **MQ Adapter** (`oracle.tip.adapter.mq.MQSeriesAdapter`) | Event Streams | IBM MQ → Event Streams |
| **HTTP Adapter** (`oracle.tip.adapter.http.HttpAdapter`) | REST connector | |
| **WS Adapter** (`oracle.tip.adapter.soa.ws.WSAdapter`) | REST connector | Convert SOAP to REST in Boomi |
| **B2B Adapter** (`oracle.tip.adapter.b2b.B2BAdapter`) | Trading Partner | Map to Boomi B2B module |
| **SAP Adapter** (`oracle.tip.adapter.sap.SAPAdapter`) | Boomi for SAP | Search account for SAP connector first |
| **Siebel Adapter** | Custom / REST | No native connector — use REST API |
| **LDAP Adapter** | Custom / REST | No native connector — use REST API or Groovy |
| **Socket Adapter** | Custom | Implement via Groovy + JVM socket API |

---

## Trigger Type Mapping (inbound)

When BPEL `<receive createInstance="yes">` uses a service binding:

| Oracle Service Binding | Boomi Start Shape |
|---|---|
| HTTP/REST binding | WSS Listener |
| SOAP/WS binding | WSS Listener (SOAP) |
| JCA File Adapter | Disk V2 Listen |
| JCA FTP Adapter | Disk V2 Listen (SFTP) |
| JCA JMS Adapter | Event Streams Listen |
| JCA AQ Adapter | Event Streams Listen |
| JCA DB Adapter (polling) | Database V2 polling (workaround: Scheduled + GET) |
| JCA EBS Adapter (event) | **REVIEW REQUIRED** — EBS event via connector |
| JCA B2B | Trading Partner Start |
| SOA Direct Binding | Process Call (called by parent) |
| EDN (Event Delivery Network) | Event Streams (bridge EDN → Boomi via REST) |

---

## Oracle `<assign>` → Boomi Mapping

BPEL `<assign>` copies data between variables using XPath. Migration strategy:

| Assign Pattern | Boomi Equivalent |
|---|---|
| Single field copy: `$inputVar/field → $outputVar/field` | Set Properties (DPP) |
| Multiple field copies (< 5) | Set Properties with multiple parameters |
| Multiple field copies (≥ 5) | Map component with profiles |
| XPath expression with functions | Map component with functions |
| Conditional copy (`bpelx:assign conditional`) | Decision + Set Properties |
| Variable to string literal | Message step |

---

## Oracle DVM → Boomi Cross-Reference Table

Oracle Domain Value Maps (`.dvm` files) are lookup tables mapping values between systems. These map directly to Boomi Cross-Reference Table components.

Example DVM:
```xml
<dvm:map xmlns:dvm="..." name="StatusCode">
  <dvm:row>
    <dvm:cell>ACTIVE</dvm:cell>    <!-- Oracle -->
    <dvm:cell>A</dvm:cell>         <!-- Salesforce -->
  </dvm:row>
</dvm:map>
```
→ Boomi Cross-Reference Table with two columns (Oracle, Salesforce).

---

## Oracle Mediator → Boomi Routing

Oracle Mediator implements content-based routing (CBR). Migration:

| Mediator Feature | Boomi Equivalent |
|---|---|
| Routing rules (if/then) | Route step with conditions |
| Transformation (XSLT/XQuery) | Map component |
| Resequencing | Data Process (Groovy) |
| Error hospital routing | Try/Catch with error branch |
| Parallel routing | Branch step (sequential gap) |
| Sequential routing | Branch step |
| Filtering (condition = false) | Decision step (discard path) |

---

## Oracle Human Task → Boomi Flow

Oracle Human Task components require human approval/action. The closest Boomi equivalent is **Boomi Flow**:

1. Boomi Integration process reaches the approval point → calls Boomi Flow via FSS (Flow Services Server)
2. Boomi Flow creates a human task form and sends notification
3. When the human approves/rejects, Flow calls back to Integration via webhook or FSS
4. Integration continues on the appropriate branch

This is a **high complexity** gap — always flag as `requires_review: true`.

---

## Oracle EBS-Specific Patterns

### EBS API Calls via Oracle EBS Adapter
Oracle EBS Adapter calls Oracle's PL/SQL APIs (function modules, business events). In Boomi:

1. **Check first**: Run `boomi-component-search.sh --name "%Oracle%EBS%" --type connector-settings` to find existing EBS connector
2. **If EBS connector available**: Use it with appropriate operation
3. **If not available**: Use DatabaseV2 connector with Oracle JDBC + PL/SQL procedure calls
4. **REST alternative**: If EBS 12.2+ with REST APIs enabled, use REST connector

### EBS Business Events
Oracle EBS fires business events (e.g., OM: Order Line Shipped) via XML Gateway. In Boomi:
- Subscribe via AQ Adapter → Event Streams Listen
- Or use Oracle EBS REST API polling (scheduled trigger)

### EBS Interface Tables
EBS uses interface tables for bulk data loading. Pattern:
1. Boomi writes to interface table (DatabaseV2 INSERT)
2. Calls Oracle concurrent program via EBS API (REST or stored procedure)
3. Oracle processes and moves data to base tables
4. Boomi polls for completion status

---

## Known Gaps (Behavioral Differences)

| Oracle SOA Feature | Gap | Resolution |
|---|---|---|
| BPEL `<flow>` (true parallel execution) | Boomi Branch is sequential | Flag medium severity; use separate processes + Event Streams for true parallel |
| BPEL `<wait>` (timer suspension) | No native Boomi timer in process | Split process; use scheduler for timer |
| BPEL `<compensate>` (saga compensation) | No direct equivalent | Implement compensation logic as separate error-path process |
| BPEL `<eventHandlers>` | No equivalent | Implement as separate Event Streams listener process |
| Oracle Mediator resequencing | No native resequencing in Boomi | Use Event Streams + sequence ID tracking in DB |
| Oracle EDN (Event Delivery Network) | Not natively supported | Use REST bridge to Event Streams |
| Oracle BPMN (complex state machines) | Partial: task-by-task mapping | Manual analysis required per process |
| Human Tasks | Requires Boomi Flow | Separate implementation on Boomi Flow platform |
| Oracle B2B (EDI X12/EDIFACT) | Boomi B2B Trading Partner module | Use Boomi's built-in EDI support (close match) |
| SOA Direct Bindings | Process Call step | Direct calls preserved as subprocess invocations |

---

## Environment Variables Required

Add these to `.env` for live SOA Suite pull:

```bash
ORACLE_SOA_HOST=soaserver.internal
ORACLE_SOA_PORT=7001
ORACLE_SOA_EM_PORT=7001          # Optional: EM Console port for SAR export
ORACLE_SOA_USERNAME=weblogic
ORACLE_SOA_PASSWORD=<password>
ORACLE_SOA_PARTITION=default     # Composite partition (default: 'default')
```

---

## Migration Checklist for Oracle SOA → Boomi

1. [ ] Run `boomi-component-search.sh` to find native Oracle connectors in the account
2. [ ] Export or pull all composites (SAR files or via REST API)
3. [ ] Run `analyze_oracle_soa.py` to generate canonical spec
4. [ ] Review all `requires_review: true` steps in the spec
5. [ ] For Oracle EBS Adapter: confirm connector availability or plan REST/DB alternative
6. [ ] For `<flow>` parallel gaps: decide if true parallel execution is required
7. [ ] For `<wait>` timer gaps: design timer replacement strategy
8. [ ] For Oracle Mediator components: manually document routing rules
9. [ ] For Oracle Human Tasks: plan Boomi Flow implementation separately
10. [ ] For Oracle DVMs: create corresponding Boomi Cross-Reference Tables
11. [ ] Run `enrich_spec.py` to LLM-enrich complex steps
12. [ ] Run `validate_logic.py` to score logic preservation
13. [ ] Generate Boomi processes with `generate_boomi.py`
14. [ ] Configure credentials via Boomi Environment Extensions (not hardcoded)
