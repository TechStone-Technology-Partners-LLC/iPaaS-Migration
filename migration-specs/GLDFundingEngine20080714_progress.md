# Migration Progress — GLDFundingEngine20080714 → Workato

**Source:** webMethods IS 6.5 package `GLDFundingEngine20080714` (KeyBank GLD payment disbursement router, built 2008-07-14)
**Target:** Workato
**Run date:** 2026-09-09
**Driver:** MigrAIte over Google Chat, following `initiate_migration/Instruction_Workato.md`

---

## Status

| Phase | Status |
|---|---|
| 1 — Analyze | ✅ Complete, reviewed and approved by Rithwik |
| 2 — Approval gate | ✅ Approved ("yes looks good") |
| 3 — Build Recipe 1 (`processFundingRequest`) | ✅ Built and pushed |
| Phase 2 recipe (`processACHBatch`) | ⛔ Deferred — blocked on G-4 / G-7 / G-8 / G-11 |

## Artifacts

| File | Purpose |
|---|---|
| `WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md` | Source-side analysis (517 lines) |
| `WebMethods/MD/PackageAnalysis.md` | Approved Workato build blueprint (§8 = build spec) |

## Recipe

| Field | Value |
|---|---|
| Name | `GLD Funding Engine — processFundingRequest` |
| Recipe ID | **82201915** |
| URL | https://app.workato.com/recipes/82201915 |
| Folder | `AIRO Testing Rithwik` (id `33882168`, project 17447149) |
| Steps | 36 |
| Inconsistencies at push | none |

### Structure as built (matches PackageAnalysis §8)

```
1  trigger  workato_api_platform.receive_request   (nested JSON: applicationInfo + payments[])
2  declare_list  paymentResponses                  (G-2 fix — accumulate one per payment)
3  declare_list  Errors
4  TRY (outer)
5    HTTP  LogXMLRequest            AppID=3, RequestIdentifier1=FE  -> MessageLogID
6    FOREACH payments
7      TRY (per payment)            <-- INSIDE the loop (BR-8)
8        IF type == "Check"
9          HTTP invokeGetUniquePayee   (11 fields, Country="USA")  -> payeeKey
10         IF payeeKey blank
11           HTTP invokeAddNewPayee    (G-1 — payload inferred)     -> payeeKey
12         HTTP invokeCreateCheckRequest (7 fields)
13         paymentResponses << {id, status:"Paid"}
14       ELSIF type == "ACH"
15         ORACLE insert_row  GLD_ACH.ACH_PAYMENT_STAGING           (columns NOT mapped — no connection)
16         paymentResponses << {id, status:"Paid"}
17       ELSE
18         paymentResponses << {id, status:"Default"}
19     RESCUE (per payment)
20       TRY  21 HTTP LogXMLRequest "ERROR - processing payment"
22       RESCUE 23 logger WARN (swallow)
24       paymentResponses << {id, status:"Error", errorDescription}
25       Errors << {errorCode, errorDescription}
26       HTTP publishErrorDoc
27   HTTP  LogXMLResponse            ResponseIdentifier4=FE
28   return_response 200             {paymentResponses[], Errors[]}
29 CATCH (outer)
30   TRY  31 HTTP LogXMLRequest "ERROR - processFundingRequest"
32   RESCUE 33 logger WARN (swallow)
34   Errors << {errorCode: MessageLogID, errorDescription}
35   HTTP publishErrorDoc
36   return_response 200
```

## Connections

| Provider | Connection | Status |
|---|---|---|
| `rest` (HTTP) | `Workato HTTP Connector` id **18739382** | ✅ wired (auto-resolved, only connection) |
| `oracle` | none | ❌ must be created in GUI (per reviewer: generic placeholder, configure later) |
| `workato_api_platform` | n/a | ✅ no connection needed |
| `workato_variable`, `logger` | n/a | ✅ built-in |

## Remaining manual GUI steps

1. **Create the Oracle connection** and wire it to step 15. Then map the 11 columns — they are listed verbatim in step 15's comment in the recipe. Confirm the real table or stored procedure with the SME first (**G-13**); `GLD_ACH.ACH_PAYMENT_STAGING` is a placeholder.
2. **Replace the three placeholder base URLs** (currently `*.keybank.internal`) with real endpoints from the SME, and set the auth scheme on the HTTP connection:
   - CheckWriter — steps 9, 11, 12
   - GLDMessageLog — steps 5, 21, 27, 31
   - WSRProcessStatistics — steps 26, 35
   All three currently share one HTTP connection (`18739382`); if they need different auth, split into three connections.
3. **Confirm the `payeeKey` response field name** on `invokeGetUniquePayee` (SME question 6). Steps 9/11 declare a response schema of `{payeeKey: string}`; if the real name differs, update both and the step 10 condition.
4. **Verify the `invokeAddNewPayee` payload** (G-1) — the source had an empty input map, so the payload was inferred as the same `PayeeInformation` used for the search.
5. **Test the PayeeKey fallback in step 12.** It is built as the concatenation of step 9's and step 11's `payeeKey` (exactly one is ever populated, guaranteed by the step 10 condition). Confirm on a first run that a skipped step 11 renders as empty and not `null`.
6. **Publish the API endpoint** on Workato API Platform to give callers a URL.

## Decisions and deviations from the source

| ID | Decision |
|---|---|
| G-2 | **Fixed** — payment responses accumulate one per payment. The 2008 source overwrote them and returned only the last. Approved by Rithwik. |
| G-5 | **Fixed** — `errorDoc/service_name` set to `GLDFundingEngine.MainFlows:processFundingRequest`. Source had a copy-paste value from a different integration. |
| G-6 | **Fixed** — `system_message` mapped once (source mapped it twice, second overwriting the first). |
| G-15 | **SOAP → REST confirmed unavoidable.** Workato's `workato_api_platform.receive_soap_request` trigger exists but is **deprecated and rejected by the platform**, so REST/JSON is the only option. Existing SOAP callers need a façade or migration. |
| G-3 | **Replicated as-is** — `Wire`/unknown types return `"Default"` with no external call and no error. |
| G-10 | **Dropped** — the `debug` input and `savePipelineToFile`/`restorePipelineFromFile` harness were not migrated. |
| — | Wrapper + `processFundingRequest` merged into one recipe; SOAP/XML marshalling steps dropped as they have no Workato analogue. |
| — | `RequestIdentifier3` on the per-payment error log is mapped to the payment id (the source used a pipeline correlation variable with no Workato equivalent). |
| — | Outer catch also returns a 200 response, matching the source's behaviour of always returning a response document rather than a SOAP fault. |

## Not migrated

- `processACHBatch` — deferred; source never commits (`updateBatchIDs` and FTP both `DISABLED`), NACHA trace number and check digit hard-coded, and the flat-file schema emits only type-6 detail records (no file/batch headers), so the output is not a valid NACHA file.
- `processACHBatch_venkat` — dead developer copy (entire loop disabled).
- `registerFlowServiceForSOAP` / `unregisterFlowServiceForSOAP` — replaced by Workato API Platform.
- `ACH_Schema`, `NACHA_SchemaDT1`, `NACHA_SchemaDT2` — unreferenced.
