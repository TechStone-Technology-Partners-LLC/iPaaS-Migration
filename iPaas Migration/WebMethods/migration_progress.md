# webMethods GLD → Boomi Migration Progress

**Last updated**: 2026-06-03
**Boomi folder**: `MIG_GLD_WebMethods` (ID: `Rjo4NTk0NDg0`)

---

## Phase 1 — Connections ✅ COMPLETE

All 6 DB connections pushed to Boomi. All passwords are **PLACEHOLDER_RESET_REQUIRED** — DBA must set real credentials before testing.

| Component | Boomi ID | Source webMethods Env | DB |
|---|---|---|---|
| MIG_WM_ComplianceDB_Connection | `9144104a-0623-4eab-bd6f-47827c7811a2` | GLDComplianceAdapterEnv:ExpressOS | Oracle CSC06DSHORA1S:1522 ORASHR4T GLD_SCHEMA |
| MIG_WM_MessageLogDB_Connection | `7752d15f-f16e-4a5a-b9c5-1ec7ab4ad091` | GLDMessageLogAdapterEnv | Oracle CSC06DSHORA1S:1522 ORASHR4T GLD_SCHEMA |
| MIG_WM_EDW_Connection | `716bc452-340c-4e9c-af29-72897f9f2c80` | GLDExpressAdapterEnv.EDW | Oracle CSC06DORASA:1521 KEF1 KEF_GLD_WEBMETHOD |
| MIG_WM_ODS_Connection | `f8379036-73f2-4962-84ce-b419aa917e5c` | GLDExpressAdapterEnv.ODS | Oracle CSC06DORASA:1521 KEF1 KEF_GLD_WEBMETHOD |
| MIG_WM_FundingACH_Connection | `458a54fe-58cb-434d-a99a-d62cd5989d16` | GLDExpressAdapterEnv.Funding | Oracle CSC06DORASA:1521 ORA01 GLD_ACHD_SCHEMA |
| MIG_WM_LeasePak_Connection | `408627b5-4959-47d7-a32f-127ce8ea5627` | GLDExpressAdapterEnv.LeasePak | Sybase csc06dsyb01:2048 ksc_cartman webmthd |

---

## Phase 2 — DB Operations ✅ COMPLETE

9 DB operations pushed covering GLDComplianceAdapterServices and GLDMessageLog adapter services.

| Component | Boomi ID | Type | Table/Purpose |
|---|---|---|---|
| MIG_WM_Compliance_logCheckRequest_Operation | `c5b81e65-156e-49f0-91c3-ca89952b4ce5` | Dynamic Insert | GLD_COMPLIANCE_REQUEST |
| MIG_WM_Compliance_logCheckReply_Operation | `29f60d20-af7c-422b-9d04-92d53593a803` | Dynamic Insert | GLD_COMPLIANCE_REPLY (per loop row) |
| MIG_WM_Compliance_logCheckReplyError_Operation | `a4941bbd-1e7b-481f-9b55-f4983e74e6c4` | Dynamic Insert | GLD_COMPLIANCE_REPLY_ERROR |
| MIG_WM_Compliance_selectCustomerAndRequest_Operation | `34da44ee-1a03-402b-b24b-6e3e1de4e7e5` | Standard Get | GLD_CUSTOMER_REQUEST (SQL placeholder) |
| MIG_WM_Compliance_updateCIURefNbr_Operation | `05aa6ed0-0063-4afc-95d6-4467d1d6fb2c` | Dynamic Update | GLD_COMPLIANCE_REQUEST (CIU ref update) |
| MIG_WM_Compliance_purgeData_Operation | `1210f659-87a9-4299-9009-150f95145716` | Standard Delete | GLD_COMPLIANCE_REQUEST (aged records) |
| MIG_WM_MessageLog_LogRequestAndResponse_Operation | `92d476cc-4967-49e1-b9f3-b320d0a37434` | Dynamic Insert | GLD_MESSAGE_LOG |
| MIG_WM_MessageLog_LogXMLRequest_Operation | `e4eec39f-cff4-4fd9-ae69-e2cac4059e38` | Dynamic Insert | GLD_MESSAGE_LOG |
| MIG_WM_MessageLog_LogXMLResponse_Operation | `c2288e7d-b3f7-47a8-8397-3b963d2c2a24` | Dynamic Insert | GLD_MESSAGE_LOG |

---

## Phase 3 — Processes (Session 1) ✅ COMPLETE

4 processes pushed covering GLDComplianceCheck main flows and GLDMessageLog utility.

| Component | Boomi ID | Source | Status |
|---|---|---|---|
| MIG_WM_Compliance_complianceCheckRequest | `34d2726c-e39a-4a58-a946-e47399f0ba37` | GLDComplianceCheck/MainFlows/complianceCheckRequest | Pushed — Start is Data Passthrough (was JMS trigger) |
| MIG_WM_Compliance_performComplianceCheck | `7fc6b2f3-dee0-4e2f-b826-af9325b64bcc` | GLDComplianceCheck/MainFlows/performComplianceCheck | Pushed — CIU HTTP connection is placeholder |
| MIG_WM_MessageLog_LogRequestAndResponse | `45038f05-9aa1-4449-8f4b-3e4d675839dc` | GLDMessageLog:LogRequestAndResponse | Pushed — ready to use |
| MIG_WM_Compliance_purgeData | `87f1a92d-25f6-4bf4-9b27-154466266279` | GLDComplianceAdapterServices:purgeData | Pushed — No Data start (scheduled) |

---

## Pending — Next Sessions

### GLDComplianceCheck remaining subprocesses (10 flows)
- validateRequiredFields
- validateFieldsFormat
- determineCheckRequestType
- mapRequestFieldsBasedOnCheckType
- getProfileData
- sendReply
- isPositiveNumber / isNullOrBlank (Utilities)
- selectCustomerAndRequest (subprocess wrapper)

### GLDSoap / GLDSoap20 (3-4 flows)
- Generic SOAP/HTTP invoker utility

### GLDFundingEngine (6 flows)
- ACH/NACHA flat file processor
- Requires MIG_WM_FundingACH_Connection

### GLDExpressWebServices (27 flows)
- SOAP web service wrappers
- Need WSS Start operations

### GLDExpressGateway (149 flows)
- Largest package — central orchestrator
- Requires EDW, ODS, LeasePak connections
- Build last

---

## Open Items (require human input)

1. **DB passwords**: All 6 connections have `PLACEHOLDER_RESET_REQUIRED` — DBA must set real passwords via Boomi GUI → Connection → Edit → Environment Extensions
2. **CIU endpoint URL**: `MIG_WM_Compliance_performComplianceCheck` shape5 uses placeholder `http://PLACEHOLDER_CIU_HOST/ciu/check` — confirm actual CIU host
3. **JMS/Event Streams broker**: `complianceCheckRequest` has a Data Passthrough start — was a webMethods JMS trigger. Need broker details to complete.
4. **Sybase JAR**: `MIG_WM_LeasePak_Connection` requires `sybjdbc.jar` deployed to Boomi Atom's `userlib/` folder
5. **Oracle JDBC JAR**: `ojdbc8.jar` (or `ojdbc11.jar`) must be on Boomi Atom classpath for all Oracle connections
6. **GLD_SCHEMA table names**: DB operations use placeholder table names (GLD_COMPLIANCE_REQUEST, GLD_MESSAGE_LOG etc.) — verify actual Oracle table names with DBA
