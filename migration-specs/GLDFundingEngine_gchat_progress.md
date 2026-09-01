### webMethods IS → Workato: GLDFundingEngine20080714 "processFundingRequest" — AVOCADO (BUILT — 2026-09-01)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com). Analysis codename **AVOCADO**.
Folder: `AIRO Testing Rithwik` (folderId `33882168`, project 17447149) — **different Workato account** from earlier GLD builds.
Built via: AIRO MCP `recipe_builder_*` tools following `docs_get(guides:recipe-builder)`.

| Component | ID / Details | Status |
|---|---|---|
| GLDFundingEngine — processFundingRequest | `81912107` — recipe function (`workato_recipe_function.execute`) | Pushed (2026-09-01) |

URL: https://app.workato.com/recipes/81912107

**Reference files:**
- `WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md` — 12-section source analysis (AVOCADO)
- `WebMethods/MD/PackageAnalysis.md` — Workato blueprint (9 required sections + 16 gaps G-1..G-16)

**Recipe structure (24 steps):**
- Trigger: `workato_recipe_function.execute` — 6 applicationInfo fields + `payments[]` **typed nested array** (10 fields + 14-field `payee` object). NOTE: modelled as a real array, not a JSON string, because Workato foreach requires a list datapill.
- Step 2 `try` → step 3 HTTP MessageLog LogXMLRequest
- Step 4 `foreach` over `execute_1['parameters']['payments']`
  - Step 5 per-payment `try` (BR-7 — failed payment continues loop)
    - Step 6 `if` type=="Check" → 7 getUniquePayee → 8 `if` body blank → 9 addNewPayee → 10 createCheckRequest → 11 logger "Paid"
    - Step 12 `elsif` type=="ACH" → 13 oracle `execute_procedure` GLD_ACH.INSERTPAYMENT → 14 logger "Paid"
    - Step 15 `else` → 16 logger "Default" (no external call)
    - Step 17 `catch` → 18 HTTP MessageLog error → 19 logger "Error"
- Step 20 HTTP MessageLog LogXMLResponse
- Step 21 outer `catch` → 22 HTTP MessageLog system error → 23 logger
- Step 24 `return_result` status=PAYMENTS_PROCESSED (outside try)

**BLOCKER — no connections in this workspace:**
This Workato account has **no HTTP (`rest`) and no Oracle connections** (only built-in workato_recipe_function + logger). Workato will not load a connector step's input schema without a connection, so the 6 HTTP steps (3, 7, 9, 10, 18, 20, 22) and the Oracle SP parameters could NOT be configured via MCP. `recipe_builder_select_connections` with null (embedded) was rejected.

**Remaining manual GUI steps:**
1. Create HTTP connection `GLDFundingEngine_CheckWriter_Connection` → wire steps 7, 9, 10; set method POST + URL + PayeeInformation/CheckRequest bodies (see PackageAnalysis §5.2/§5.3)
2. Create HTTP connection `GLDFundingEngine_MessageLog_Connection` → wire steps 3, 18, 20, 22; AppID=3, RequestIdentifier1 per step (FE / "ERROR - processing payment" / "ERROR - processFundingRequest")
3. Create Oracle connection → wire step 13; confirm SP name `GLD_ACH.INSERTPAYMENT` and bind the 11 params (PackageAnalysis §5.4, REQUESTOR_ID=1 static)
4. Step 8 condition currently tests `make_request_v2_7['body']` **blank** — repoint to the real `payeeKey` response field once the HTTP response schema is defined (gap G-13)
5. `processACHBatch` (NACHA) not migrated — HIGH gap G-3

---

