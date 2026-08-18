# Migration Agent

This workspace is a **platform-agnostic integration migration agent**. It migrates integrations between any supported platforms — in any direction. Source and target can each be Boomi, MuleSoft, Workato, SAP, or any future platform. It is built on top of Boomi Companion for Boomi-side operations.

## Supported Platforms

| Role | Supported |
|---|---|
| Source (pull + analyze) | Boomi, MuleSoft, Oracle SOA Suite / EBS, Workato, Celigo, webMethods.io |
| Target (generate + push) | Workato, Boomi |
| Future | SAP, Azure Logic Apps |

## WebmethodsToWorkato_Migration Agent

Dedicated agent for webMethods IS → Workato migrations. Follows the steps in `WebMethods/Instruction_Workato.md`.

**Steps:**
1. Analyze webMethods package → `WebMethods/Analysis/<PackageName>_Analysis.md`
2. Synthesize `WebMethods/MD/PackageAnalysis.md` (Workato-oriented)
3. Create `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx` (22 construct mappings)
4. Create `Workato/Workato_Map_Field_Mappings.xlsx` (field-level + output + gap sheets)
5. Create `WebMethods/MD/Workato.md` (full recipe build reference)
6. Push Workato recipe via API (`scripts/push_gld_workato_recipe.py` as reference)

**Reference files:**
- `WebMethods/Instruction_Workato.md` — full step-by-step migration instructions
- `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx` — construct mapping
- `Workato/Workato_Map_Field_Mappings.xlsx` — field-level data mapping
- `WebMethods/MD/Workato.md` — authoritative Workato recipe build reference

---

## WebmethodsToBoomi_Migration Agent

Dedicated agent for webMethods IS → Boomi migrations. Follows the 4-phase pipeline from `WebMethods/Instruction_Boomi copy.md`.

```bash
# Interactive (will prompt for package name)
python scripts/wm_migration_agent.py

# Non-interactive
python scripts/wm_migration_agent.py --package GLDComplianceAdapterServices
python scripts/wm_migration_agent.py --package MyPackage --source-dir /path/to/exports/MyPackage
```

**Phase 1 (analysis — runs automatically):**
1. Scans `iPaas Migration/WebMethods/GLDProject/<PackageName>/` for `.ndf`, `.idf`, `manifest.v3`, `flow.xml` files
2. Calls Claude API to produce `WebMethods/Analysis/<PackageName>_Analysis.md`
3. Synthesizes `WebMethods/MD/PackageAnalysis.md` (the Boomi build reference)
4. **Stops** — awaits user instruction

**Subsequent phases (manual, following Instruction.md):**
- Step 8: Create Map component from Boomi Map Test Skill Excel
- Step 9: Apply Agent Bridge Excel to process structure
- Step 10: Generate `Boomi.md` from PackageAnalysis.md + Excel files
- Step 13: Generate and push all Boomi components

**Reference files:**
- `WebMethods/Instruction.md` — full step-by-step migration instructions
- `WebMethods/Agent Bridge Web Methods to Boomi Component Mapping.xlsx` — construct mapping
- `WebMethods/MD/PackageAnalysis.md` — output: Boomi migration reference

---

## MigrAlte UI

Branded Streamlit app (`app.py`). Source locked to webMethods IS. Package input: local zip upload or Google Drive share URL.

```bash
python -m streamlit run app.py --server.port 8501
```

Features: project name auto-derived from zip filename, dry-run / skip-analyze / skip-enrich / skip-document checkboxes, tabbed results (Migration Spec JSON + Design Document download).

---

## Migration Agent Workflow

Every migration follows this 5-phase pipeline. Never skip phases.

```
PHASE 1 — PULL         (if source is a live platform)
                       Boomi: boomi-component-search.sh + boomi-component-pull.sh
                       MuleSoft / webMethods: project files already on disk (no pull needed)

PHASE 2 — ANALYZE      Run the analyzer for the source system.
                       Output: migration-specs/<project>.json
                       This spec is platform-agnostic — it has no target-specific concepts.
                       webMethods: python analyzers/analyze_webmethods.py <source-dir> --project <name>

PHASE 3 — ENRICH       AI enrichment pass — expands nested service logic Claude cannot infer statically.
                       webMethods: python enrichers/enrich_webmethods.py migration-specs/<proj>.json --source-dir <dir>
                       Other sources: python enrichers/enrich_spec.py migration-specs/<proj>.json
                       Skip flag: --skip-enrich

PHASE 4 — DOCUMENT     Generate Word design document (TechStone branded).
                       Output: migration-specs/<project>_design_document.docx
                       python generators/generate_word_doc.py migration-specs/<proj>.json --target <platform>
                       Skip flag: --skip-document

PHASE 5 — GENERATE     Run the generator for the target system.
                       One target artifact per source flow.
```

### Single-command entry point

For real-world usage, use `migrate.py` (at workspace root) — it orchestrates all 5 phases:

```bash
# Migrate a Boomi folder to Workato (pulls live from Boomi, generates in Workato)
python migrate.py --from boomi --boomi-folder "My Folder Name" --to workato

# Migrate a webMethods package to Workato (with AI enrichment + Word doc)
python migrate.py --from webmethods --source-dir active-development/wm_upload/extracted --to workato --project mypackage

# Migrate a MuleSoft project to Workato
python migrate.py --from mulesoft --source-dir samples/mulesoft/customer-api/ --to workato

# Dry run (print target recipe/process JSON without pushing)
python migrate.py --from webmethods --source-dir ... --to workato --dry-run

# Skip individual phases
python migrate.py --from webmethods --source-dir ... --to workato --skip-enrich --skip-document

# Skip pull (analyze already-downloaded active-development/ files)
python migrate.py --from boomi --source-dir active-development/ --to workato
```

New flags: `--skip-enrich`, `--skip-document`, `--md-dir <path>` (attach markdown files to Word doc appendix).

Always read `references/MIGRATION_THINKING.md` before starting any migration task.

## Running Individual Phases Manually

**Analyzers:**
```bash
python analyzers/analyze_boomi.py active-development/ --project my-project
python analyzers/analyze_mulesoft.py samples/mulesoft/customer-api/
python analyzers/analyze_mulesoft.py <path> --output migration-specs/myproject.json

# Oracle SOA Suite — live pull from Oracle SOA REST API (credentials in .env)
python analyzers/analyze_oracle_soa.py --project my-oracle-project

# Oracle SOA Suite — from local SAR exports
python analyzers/analyze_oracle_soa.py --source-dir /path/to/sars/ --project my-oracle-project

# Oracle SOA Suite — filter to specific composites
python analyzers/analyze_oracle_soa.py --composite-filter "Order*" --project orders

# Full pipeline — Oracle SOA → Boomi
python migrate.py --from oracle_soa --to boomi --project my-oracle-project
python migrate.py --from oracle_soa --source-dir /path/to/sars/ --to boomi --project my-oracle-project
```

**Generators:**
```bash
python generators/generate_workato.py migration-specs/my-project.json --folder "My Folder"
python generators/generate_workato.py migration-specs/my-project.json --dry-run
```

## Required Environment Variables

See `.env.example` for the full annotated list. Key sections:

**Boomi (for pull operations):** Already in `.env` from Boomi Companion setup.

**Workato (for generate/push):**
```
WORKATO_API_TOKEN=<from Settings → API Tokens>
WORKATO_EMAIL=<your workato email>
```

**Oracle SOA Suite (for oracle_soa source):**
```
ORACLE_SOA_HOST=soaserver.internal
ORACLE_SOA_PORT=7001
ORACLE_SOA_USERNAME=weblogic
ORACLE_SOA_PASSWORD=<password>
ORACLE_SOA_PARTITION=default          # composite partition, usually "default"
ORACLE_SOA_EM_PORT=7001               # optional: EM Console port for SAR export
```

**Anthropic (for LLM enrichment):**
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Reference Documentation

- `references/MIGRATION_THINKING.md` — Core migration mental models (read first)
- `references/migration_spec_schema.md` — Migration spec JSON schema
- `references/source-systems/mulesoft_mapping.md` — MuleSoft → canonical spec mapping
- `references/source-systems/boomi_mapping.md` — Boomi → canonical spec mapping
- `references/source-systems/oracle_soa_mapping.md` — Oracle SOA Suite / EBS → canonical spec mapping
- `references/target-systems/workato_mapping.md` — canonical spec → Workato mapping

## Sample Artifacts

Realistic source system examples for testing:
- `samples/mulesoft/customer-api/` — REST CRUD API with PostgreSQL backend
- `samples/mulesoft/file-processor/` — SFTP file pickup, CSV parse, HTTP post with retry
- `samples/mulesoft/crm-sync/` — Scheduled Salesforce-to-MySQL sync with email notification
- `samples/oracle-soa/CustomerOrderProcessing/` — AQ trigger, EBS credit check, DB inventory, JMS error queue (BPEL 2.0)
- `samples/oracle-soa/AccountSyncBatch/` — FTP trigger, EBS account lookup, DB upsert, forEach loop (BPEL 2.0)
- `samples/oracle-soa/NotificationFanout/` — HTTP trigger, parallel `<flow>` with email/DB/B2B EDI branches (BPEL 2.0)

## Naming Convention for Migrated Components

```
MIG_<SourceSystem>_<FlowName>_<ComponentType>

Examples:
  MIG_MS_GetCustomers_Process
  MIG_MS_PostgreSQL_Connection
  MIG_MS_CustomerResponse_JSON_Profile
```

Boomi folder structure:
```
ClaudeCode/
  MIG_<ProjectName>/
```

## Session Continuity

Migration projects span multiple sessions. At session start:
1. Check `migration-specs/` for existing specs and progress notes
2. Resume from where the previous session left off
3. Do not re-analyze if a spec already exists (unless source files changed)

After each generation session, note which flows are done/pending/blocked in `migration-specs/<project>_progress.md`.

---

This is a Boomi oriented workspace, load and use the `boomi-integration` skill for all Boomi tasks. 

The skill contains .sh cli tools for all common tasks you would need to achieve. Always look for these tools as a first option. The path to run these cli tools will always be <skill-base-path>/scripts/*

If you find yourself needing to craft custom curl - stop and discuss with the user before proceeding. This is unexpected.

If you attempt to call into the Boomi platform and get an auth error - stop and discuss with the user before proceeding. Repeated calls with invalid auth will get us locked out of the platform.

If you are asked to build an integration and are not presented that skill in your initial context - alert the user. The skill includes critical information for your project. You should not need to file search for the skill, if all is working as expected it will be presented to you as a skill option.

## Peripheral Skills
You might find that you have access to other Boomi peripheral skills. Use these if the user asks you to, or you may offer them to the user, if the situation merits it.  

## Credentials & .env files
You will not be able to read `.env` files directly — access is blocked by project settings by default. The CLI tools load credentials internally via `source .env` in bash. Variables expand inside the bash subprocess.

Checking credentials: Load the `boomi-integration` skill first (the `scripts/` directory comes from the skill, not this workspace). Run `bash scripts/boomi-env-check.sh` to see which variables are SET vs UNSET. Run `bash scripts/boomi-folder-create.sh --test-connection` to verify platform connectivity. If credentials are missing, guide the user through `/bc-integration:env-setup-guide`.

**Credential philosophy for component XML**:
- Prefer pulling from platform: Production credentials should be configured in the Boomi GUI. Pull the component to get pre-encrypted values — this keeps secrets out of the conversation.
- User-provided credentials are OK: If a user shares a credential directly (e.g., "here's the API key"), you may use it in component XML. If it appears to be a production secret, remind them of the pull-from-platform option — but respect their choice.
- Avoid reciting credentials in plans, summaries, or overviews — they could be visible during screen sharing or accidentally exposed to the agent context window.

## Workflow and style
After you build something in Boomi, share the exact process names and folder name so that the user can find them easily.

Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns. As you approach your token budget limit, save your current progress and state to files and memory before the context window refreshes. Always be as persistent and autonomous as possible and complete tasks fully, even if the end of your budget is approaching. Never artificially stop any task early regardless of the context remaining.

After completing a task that involves tool use, provide a quick summary of the work you've done.

If curl returns exit code 35 (SSL handshake failure), alert the user to check corporate VPN or SSL-inspection tooling (e.g., Zscaler, Netskope, Cisco Umbrella) before troubleshooting.

## Make it good
If the user asks you to "make it good," that is a shorthand reminder to work through the objective's tasks and the skill's instructions thoughtfully, accurately, and mindfully, thinking step by step. 

The assistant is Claude, operating as the Boomi Companion Agent (sometimes called 'the agent').

## Boomi XML Schema — Hard-won Rules

These were learned through live push failures and confirmed against the Boomi platform API. Trust these over skill docs when there is a conflict.

### Groovy / Data Process shapes
- `shapetype="dataprocess"` and `image="dataprocess_icon"` (NOT `"data"` / `"data_icon"`)
- Step element: `<step index="1" key="1" name="Custom Scripting" processtype="12">` — no `function` attribute
- Script element: `<dataprocessscript language="groovy2" useCache="true">` — NO `checkForMoreData` attribute
- Groovy code goes inside `<script><![CDATA[...]]></script>` child of `<dataprocessscript>`, NOT directly as CDATA

### Message shape parameters
- Use `<parametervalue key="N" valueType="process">` NOT `<msgParameter>`
- Use `<processparameter processproperty="DPP_NAME" processpropertydefaultvalue=""/>` NOT `<processPropertyValue propertyId="process.DPP_NAME"/>`
- `valueType="process"` for DPP refs (NOT `"processproperty"`)

### Decision shapes (DPP comparison)
Same `valueType="process"` + `<processparameter>` pattern as Message shapes.

### REST connector actionType
Always `actionType="EXECUTE"` for `connectorType="officialboomi-X3979C-rest-prod"` shapes — never "GET", "POST", etc.

### create.sh vs push.sh
- **No sync state or "ComponentId invalid" error** → use `boomi-component-create.sh`
- **Sync state exists** → use `boomi-component-push.sh`

## Connector Discovery Rule

At the start of any migration or integration task, run `boomi-component-search.sh` against the live account before designing the approach. The account has native connectors (netsuitesdk, salesforce, etc.) that are far more appropriate than generic REST. Always check:
```bash
bash <skill-path>/scripts/boomi-component-search.sh --name "%SystemName%" --type "connector-settings,connector-action"
```

## Account Context

**IMPORTANT for new sessions:** Component IDs and folderIds in the Active Migrations section below are tied to the **personal Boomi account** used during initial development. On the **org/team account**, those components do not exist.

When resuming any migration on a new Boomi account:
1. Run `/bc-integration:env-setup-guide` to configure new account credentials in `.env`
2. Run `bash <skill-path>/scripts/boomi-folder-create.sh --test-connection` to verify connectivity
3. Run connector discovery before generating: `bash <skill-path>/scripts/boomi-component-search.sh --name "%SystemName%" --type "connector-settings,connector-action"`
4. Migration specs in `migration-specs/*.json` are reusable — **do not re-analyze**, go straight to GENERATE
5. The `active-development/` folder and `.sync-state/` are gitignored — they will be empty on a fresh clone. Use `boomi-component-create.sh` (not `push.sh`) for all first-time pushes on the new account
6. New components will get new IDs — update CLAUDE.md with the new IDs after each generation run

---

## Active Migrations

### Workato → Boomi: SF Account sync to NetSuite (COMPLETE — personal account)
All 5 components pushed. Folder: `ClaudeCode/MIG_<project>` (folderId `Rjo4NTY2MjA1`)

| Component | ID |
|---|---|
| MIG_Sync new/updated account from Salesforce to NetSuite (process) | c41bc08e-100e-43da-865d-808f15db3ba6 |
| MIG_NS_SuiteQL_Search_Operation | ea187caa-fbbc-4287-b5a3-b4a6031fe566 |
| MIG_NS_Get_Subsidiaries_Operation | a115a877-de21-49c1-ab86-f726093b282c |
| MIG_NS_Create_Customer | eda0db3d-e7cf-4569-90ac-1673606279b7 |
| MIG_NS_Update_Customer | 51bafc9a-d812-4db1-af13-4feeaab2369f |

**Reused connections:** Salesforce `647ff483`, NetSuite REST `1cce1777`, NetSuite TBA `15c076fa`

**Remaining manual GUI steps:**
1. shape2: Import "Query Modified Accounts" Salesforce operation → add operationId
2. shape1: Change Passthrough Start to scheduled or Salesforce listener trigger
3. NetSuite TBA connection `15c076fa`: Configure via Environment Extensions
4. NetSuite REST connection `1cce1777`: Configure OAuth2 credentials

### Workato → Boomi: Upload Salesforce account files to Box (IN PROGRESS — personal account)
Folder: `ClaudeCode/MIG_<project>` (folderId `Rjo4NTY2MjA1`)

| Component | ID | Status |
|---|---|---|
| MIG_Upload Salesforce account files to Box (process) | b7b973d4-5b4d-4bf9-9af0-b6f2b9736aa8 | PUSHED |
| MIG_Box_Connection | (not yet on platform) | NEEDS GUI CREATE |

**Box connection note:** The Box native connector XML schema is not known — Boomi rejected `<Connection/>` as invalid. User must create the Box connection in Boomi GUI, then update the process to reference it.

**Remaining manual GUI steps:**
1. Create Box connection in GUI → configure OAuth2 Client ID, Client Secret, Access Token
2. shape2: Import Salesforce "New Account" query/GET operation → add operationId
3. shape4: Configure Box Search operation — search term = `DPP_SF_ACCOUNT_NAME`, type = folder
4. shape7: Configure Box Create Folder operation — name = `DPP_SF_ACCOUNT_NAME`, parent folder ID = 0 (root)
5. shape9: Import Salesforce QUERY Attachment operation — filter WHERE `ParentId = DPP_SF_ACCOUNT_ID`
6. shape11: Configure Box Upload operation — folder = `DPP_BOX_FOLDER_ID`, filename = `DPP_ATTACHMENT_NAME`
7. Box connector shapes (4, 7, 11): Wire to the Box connection created in step 1

### Workato → Boomi: AIMigrationTest5 (COMPLETE — 2026-06-08)
Folder: `MIG_AIMigrationTest5` (folderId `Rjo4NjE4MDg5`). Preservation score: 90% (Grade B).
Source: Workato `/AI` folder (folder_id 31266135), recipe_id 73034327. Trigger: daily scheduler.

| Component | ID |
|---|---|
| MIG_AIMigrationTest5 (process) | 8dd63d96-621e-48b1-b13a-ec8306ebbfed |

**Remaining manual GUI steps:**
1. Shape 1 (connector_action): Unknown provider — open process in Boomi canvas and configure the connector/operation
2. Shape 2 (connector_action, label `04557745`): Unknown provider — configure connector/operation in canvas
> Both steps were flagged `requires_review` in the Workato source (connector metadata not exposed via API).

---

### Oracle SOA Suite → Boomi: Sample Pipeline Test (COMPLETE — 2026-05-25, personal account)
End-to-end test with 3 sample composites. Score: 80% (C). All 6 components pushed to Boomi folder **`MIG_oracle_soa_test`** (folderId `Rjo4NTY4NTU1` on personal account — does not exist on org account).

| Component | ID | Notes |
|---|---|---|
| MIG_AccountSyncBPEL (process) | c615d5ae | FTP trigger → EBS → DB forEach loop |
| MIG_oracle_soa_test_DB_Connection | 8b5ab902 | Shared DB connection (was double-prefix in old code — fixed) |
| MIG_OrderProcessingBPEL_CheckInventory_Operation | 124698bd | REST operation for inventory check |
| MIG_OrderProcessingBPEL (process) | 5eb02954 | AQ trigger → DB → EBS credit check |
| MIG_NotificationFanoutBPEL_WSSOperation | 4359a68f | WSS operation for HTTP listener |
| MIG_NotificationFanoutBPEL (process) | 4435d9a4 | HTTP trigger → parallel Branch (email/DB/EDI) |

**Gaps flagged by validator:**
- `[OrderProcessingBPEL]` ValidateCredit — EBS Adapter needs Oracle EBS connector in account
- `[NotificationFanoutBPEL]` ParallelNotificationFanout — BPEL `<flow>` mapped to sequential Branch

**Bugs fixed during test run (committed in 6b55fdd):**
- `generate_boomi.py`: double `MIG_MIG_` prefix on DB connection name
- `validators/validate_logic.py`: transform steps over-penalized (score was 30%→80% after fix)

---

### Workato → Boomi: Jira issue sync to Salesforce (COMPLETE — 2026-06-09, org account)
Folder: `MIG_workato_migration` (folderId `Rjo4NjE3OTg3`, account `tpptechstone-O6Y5DV`)

| Component | ID | Notes |
|---|---|---|
| MIG_Sync new/updated issue from Jira to Salesforce (process) | 6f2c697a-98ef-498b-8217-4f7b4abd0b3b | Pushed |

**Remaining manual GUI steps:**
1. shape1 (Start): Configure as WSS listener OR Jira polling schedule — currently passthrough
2. shape2 (Message placeholder): Replace with HTTP connector polling Jira API for updated issues
3. shape3 (Search Cases): Import Salesforce QUERY Case operation → add operationId
4. shape4 (Search Accounts): Import Salesforce QUERY Account operation → add operationId
5. shape5/7/9 (Decisions): Reconfigure to compare actual SF query result count vs blank/present
6. shape6 (Create Account): Import Salesforce CREATE Account operation → add operationId
7. shape8 (Create Case): Import Salesforce CREATE Case operation → add operationId
8. shape10 (Update Case): Import Salesforce UPDATE Case operation → add operationId
**Reuse Salesforce connection:** `647ff483-9f3e-4b49-a32f-a906f65c347c` (Salesforce Connection, Manish A folder)

---

### webMethods IS → Workato: GLDFundingEngine20080714 Migration (COMPLETE — 2026-06-20)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com — payment routing engine).
Folder: `WebMethodsMigration` (folderId `31661117`, account `manish@techstonellc.com`)

| Component | ID / Details | Status |
|---|---|---|
| MIG_WM_GLDFundingEngine20080714_Recipe | `73596434` — callable recipe (HTTP POST /process-funding-request) | Pushed (2026-06-22, all steps non-empty) |

**Recipe structure** (per [GLDFundingEngine20080714_Analysis.md](WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md)):
- Trigger: callable_recipe — input schema: `applicationInfo` (object, 6 fields) + `payments[]` (array, 14 fields + nested `payee` object, 14 fields)
- `repeat_for_each` over payments[] (line alias: `payment_loop`)
- 3-way payment type branch:
  - `Check`: invokeGetUniquePayee → [IF payeeKey empty: invokeAddNewPayee] → invokeCreateCheckRequest
  - `ACH`: insertPayment (GLD_ACHAdaptersServices, 11 params: APP_ID, CUSTOMER_NAME, PAYEE_NAME, PAYEE_ID, REFERENCE, AMOUNT, ROUTING_NUMBER, ACCOUNT_NUMBER, CUSTOMER_ID, REQUESTOR_ID="1", SOURCE)
  - `Other`/`Wire`: Default — no external call, status="Default"
- `rescue` block per iteration: HTTP POST GLDMessageLog:LogXMLRequest (AppID=3)
- Push script: `scripts/push_gld_funding_engine_workato_recipe.py`

**Remaining manual steps:**
1. Create HTTP connection for GLDExpressGateway in Workato GUI → wire to steps 3, 5, 6 (Check path)
   - Base URL: `https://webmethods-gateway.keybank.internal` (placeholder — obtain real URL from SME)
2. Create HTTP connection for GLD_ACHAdaptersServices in Workato GUI → wire to step 9 (ACH path)
   - Base URL: `https://webmethods-ach.keybank.internal` (placeholder — obtain real URL from SME)
3. Create HTTP connection for GLDMessageLog → wire to step 12 (rescue block)
4. Confirm CheckWriter response field name for `payeeKey` (step 3 response) — update pill path if different
5. Add `fundingEngineWrapperResponse` return body to callable recipe trigger response settings in GUI
6. `processACHBatch` flow: **not migrated** — NACHA flat-file generation requires custom implementation (see Analysis §10 gap #1/#7)

### webMethods IS → Workato: GLDFundingEngine20080714 "FundingEngine" — initiate_migration/start.md + WebMethods/start.md (COMPLETE — 2026-07-30)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com).
Folder: `migrAIte_Training/webMethodsMigration` (folderId `32159265`, account `manish@techstonellc.com`)
Built via: `initiate_migration/start.md` + `WebMethods/start.md` 6-step workflows using `initiate_migration/Instruction_Workato.md`.

| Component | ID / Details | Status |
|---|---|---|
| FundingEngine v1 (HTTP ACH) | `74461604` — callable recipe (workato_service/receive_request "FundingEngine") | Pushed (2026-07-30) |
| FundingEngine v2 (Oracle ACH) | `74461729` — callable recipe, ACH uses Oracle execute_stored_procedure | Pushed (2026-07-30) |

**Reference files produced:**
- `WebMethods/Analysis/MD/PackageAnalysis.md` — comprehensive 10-section analysis
- `WebMethods/MD/FundingEngine_WMToWorkato.md` — 22 sequential build prompts (initiate_migration/start.md workflow)
- `WebMethods/MD/GLDFundingEngine_WMToWorkato.md` — 24 section-5.2-derived prompts (WebMethods/start.md workflow)
- `scripts/push_funding_engine_workato.py` — push script v1 (HTTP ACH, folder ID: 32159265)
- `scripts/push_funding_engine_oracle_workato.py` — push script v2 (Oracle ACH, RecipeComponents patterns)

**Recipe structure:**
- Trigger: `workato_service/receive_request` — 7 flat fields (id, customerName, customerID, sourceName, sourceSubCategory, salesRepName, payments JSON string)
- Step 1: outer try
- Step 2: each loop over payments[] (`.parse_json` applied to payments string), alias: `payment_loop`
  - Step 3: IF type=="Check" → invokeGetUniquePayee (step 4) → IF payeeKey empty → invokeAddNewPayee (step 5-6) → invokeCreateCheckRequest (step 7)
  - Step 8: ELSIF type=="ACH" → insertPayment (step 9, 11 params incl. REQUESTOR_ID=1 static)
  - Step 10: ELSE → Log Default (step 11, no external call)
  - rescue (per-payment): log error (step 12)
- outer catch: log system error (step 13)
- Step 14: workato_service/send_reply (status=PAYMENTS_PROCESSED)

**Remaining manual GUI steps (v2 — Oracle ACH, recipe 74461729):**
1. Create HTTP connections and wire to CheckWriter + MessageLog steps:
   - `GLDFundingEngine_CheckWriter_Connection` → steps 4, 6, 7 (CheckWriter URL from SME)
   - `GLDFundingEngine_MessageLog_Connection` → steps 12, 13 (MessageLog URL from SME)
2. Oracle ACH connection (MIG_WM_GLD_Oracle_Connection, ID 19657520):
   - Confirm Oracle connection points to GLD_ACHAdaptersServices Oracle instance
   - Verify SP name: `GLD_ACH.INSERTPAYMENT` (confirm exact schema.proc name with SME)
   - If needed, create a dedicated Oracle connection for the ACH schema in GUI
3. Steps 12 and 13 (error logs): wire `error.message` Workato pill in GUI
4. Obtain real base URLs from SME to replace placeholders (see push script header)
5. `processACHBatch` recipe: prompts 16-24 in GLDFundingEngine_WMToWorkato.md — not built; NACHA generation is a HIGH gap

---

### webMethods IS → Workato: GLDFundingEngine20080714 "Funding Engine Test2" (COMPLETE — 2026-08-18)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com).
Folder: `FundingEngineTest2` (folderId `32367278`, parent: migrAIte_Training `31835141`, account `manish@techstonellc.com`)
Built via: `Workato/Companion/SKILL.md` (workato-integration skill) — all 15 rules applied.
Source analysis: `WebMethods/Analysis/MD/PackageAnalysis.md` (Section 8, Recipe 1).

| Component | ID / Details | Status |
|---|---|---|
| Funding Engine Test2 | `74824702` — callable recipe (workato_service/receive_request "Funding Engine Test2") | Pushed (2026-08-18) |

**Recipe structure (all RecipeComponent JSONs used as canonical references):**
- Trigger: 7 flat fields (id, customerName, customerID, sourceName, sourceSubCategory, salesRepName, payments JSON string)
- `try` → `foreach` (payment_loop, parse_json) → `if` Check (steps 4-7) / `elsif` ACH (step 9 Oracle) / `else` Default (logger) → `rescue` (step 13, last) → `send_reply` → `catch` (step 15, last in try)
- **Key fix vs Test1:** `forEach.json` canonical: `"source"` at TOP LEVEL (not inside `"input"`); `"input": {}` empty
- Push script: `scripts/push_funding_engine_test2.py`
- URL: https://app.workato.com/recipes/74824702

**Remaining GUI steps:**
1. Create `GLDFundingEngine_CheckWriter_Connection` (HTTP) → wire to steps 4, 6, 7 (CheckWriter URL from SME)
2. Wire `MIG_WM_GLD_Oracle_Connection` (ID 19657520) → step 9 (confirm SP name GLD_ACH.INSERTPAYMENT)
3. Wire `error.message` datapills in step 13 (rescue logger) and step 16 (catch logger) in GUI

---

### webMethods IS → Workato: GLDFundingEngine20080714 "Funding Engine using Companion" (COMPLETE — 2026-08-09)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com).
Folder: `migrAIte_Training` (folderId `31835141`, account `manish@techstonellc.com`)
Built via: `Workato/Companion/SKILL.md` (workato-integration skill) — all 15 rules applied.
Source analysis: `WebMethods/Analysis/MD/PackageAnalysis.md` (Section 8, Recipe 1).

| Component | ID / Details | Status |
|---|---|---|
| Funding Engine using Companion | `74633314` — callable recipe (workato_service/receive_request) | Pushed (2026-08-09) |

**Recipe structure (companion build — PackageAnalysis Section 8 exact structure):**
- Trigger: 7 flat fields (id, customerName, customerID, sourceName, sourceSubCategory, salesRepName, payments JSON string)
- `try` → `each` (payment_loop, parse_json) → `if` Check (steps 4-7) / `elsif` ACH (step 9 Oracle) / `else` Default (logger) → `rescue` (step 12, last) → `catch` (last in try)
- `send_reply` OUTSIDE try block — sibling in trigger.block → status=PAYMENTS_PROCESSED
- Push script: `scripts/push_funding_engine_companion.py`
- URL: https://app.workato.com/recipes/74633314

**Remaining GUI steps:**
1. Create folder "FundingEngine Companion" in Workato GUI (folder API is IP-whitelisted); move recipe there
2. Create `GLDFundingEngine_CheckWriter_Connection` (HTTP) → wire to steps 4, 6, 7 (CheckWriter URL from SME)
3. Wire `MIG_WM_GLD_Oracle_Connection` (ID 19657520) → step 9 (confirm SP name GLD_ACH.INSERTPAYMENT)
4. Create `GLDFundingEngine_MessageLog_Connection` (HTTP) → wire to steps 12, 14 (MessageLog URL from SME)
5. Wire `error.message` pills in rescue step 12 and catch step 14 in GUI

---

### webMethods IS → Workato: GLDFundingEngine20080714 v3 — initiate_migration/Instruction_Workato.md 6-step workflow (COMPLETE — 2026-08-06)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com).
Folder: `migrAIte_Training` (folderId `31835141`, account `manish@techstonellc.com`)
Built via: `initiate_migration/Instruction_Workato.md` 6-step workflow + `Workato/Companion/SKILL.md` (workato-integration skill).

| Component | ID / Details | Status |
|---|---|---|
| GLD FundingEngine — processFundingRequest (v3) | `74597322` — callable recipe (workato_service/receive_request "FundingEngine") | Pushed (2026-08-06) |

**Recipe structure (v3 — streamlined: no log request/response, Oracle ACH, all 15 SKILL.md rules):**
- Trigger: `workato_service/receive_request` "FundingEngine" — 7 flat fields (id, customerName, customerID, sourceName, sourceSubCategory, salesRepName, payments JSON string)
- Step 1: outer try
- Step 2: each loop over payments[] (`.parse_json` applied to payments string), alias: `payment_loop`
  - Step 3: IF type=="Check" → invokeGetUniquePayee (step 4) → IF payeeKey empty → invokeAddNewPayee (step 5-6) → invokeCreateCheckRequest (step 7)
  - Step 8: ELSIF type=="ACH" → Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT (step 9, 11 params)
  - Step 10: ELSE → Logger Default path (step 11)
  - rescue (step 14, last in each.block): HTTP POST GLDMessageLog (step 12)
- Step 15: catch (last in try.block): HTTP POST GLDMessageLog (step 13)
- Step 16: workato_service/send_reply (status=PAYMENTS_PROCESSED)

**Reference files:**
- `WebMethods/MD/GLDFundingEngine_WMToWorkato.md` — 24 sequential build prompts (Recipes 1 + 2)
- `scripts/push_gld_funding_engine_v3_workato.py` — push script (all 15 workato-integration SKILL.md rules applied)

**Remaining manual GUI steps:**
1. Create HTTP connection `GLDFundingEngine_CheckWriter_Connection` → wire to steps 4, 6, 7 (CheckWriter URL from SME)
2. Wire Oracle connection `MIG_WM_GLD_Oracle_Connection` (ID: 19657520) → step 9 (confirm SP name GLD_ACH.INSERTPAYMENT with SME)
3. Create HTTP connection `GLDFundingEngine_MessageLog_Connection` → wire to steps 12, 13 (MessageLog URL from SME)
4. Wire `error.message` pills in rescue step 12 and catch step 13 in GUI
5. URL: https://app.workato.com/recipes/74597322

---

### webMethods IS → Workato: GLDFundingEngine20080714 v2 — initiate_migration workflow (COMPLETE — 2026-07-30)
Source: `GLDFundingEngine20080714` (webMethods IS 6.5, keybank.com).
Folder: `migrAIte_Training` (folderId `31835141`, account `manish@techstonellc.com`)
Built via: `initiate_migration/Instruction_Workato copy.md` 3-phase workflow.

| Component | ID / Details | Status |
|---|---|---|
| MIG_WM_GLDFundingEngine_processFundingRequest | `74460780` — callable recipe (workato_service/receive_request) | Pushed (2026-07-30) |

**Reference files produced:**
- `WebMethods/MD/GLDFundingEngine_PackageAnalysis.md` — Phase 1 consolidated analysis (11 sections)
- `WebMethods/MD/GLDFundingEngine_WMToWorkato.md` — Phase 2 sequential build prompts (27 prompts, 2 recipes)
- `scripts/push_gld_funding_engine_v2_workato.py` — Phase 3 push script

**Recipe structure (v2 — full outer try/catch + log request/response + send_reply):**
- Trigger: `workato_service/receive_request` — 6 flat applicationInfo_* fields + payments (JSON string)
- Step 1: outer try/catch wrapper
- Step 2: HTTP POST GLDMessageLog:LogXMLRequest (log request, AppID=3, FE)
- Step 3: each loop over payments[] (`.parse_json` applied to payments string)
  - Step 4: IF type=="Check" → Get/Add payee (steps 5-7) → invokeCreateCheckRequest (step 8)
  - Step 9: ELSE → IF type=="ACH" (step 10) → insertPayment (step 11) / ELSE Default noop (step 12-13)
  - Step 14: rescue (per-payment) → log error (step 15)
- Step 16: HTTP POST GLDMessageLog:LogXMLResponse (log response, AppID=3, FE)
- Step 17: workato_service/send_reply (status=PAYMENTS_PROCESSED)
- Step 18: catch (outer) → log system error (step 19)

**Remaining manual GUI steps:**
1. Create 3 HTTP connections and wire to all HTTP steps:
   - `GLDFundingEngine_CheckWriter_Connection` → steps 5, 7, 8 (CheckWriter URL from SME)
   - `GLDFundingEngine_ACH_Connection` → step 11 (ACH URL from SME)
   - `GLDFundingEngine_MessageLog_Connection` → steps 2, 15, 16, 19 (MessageLog URL from SME)
2. Steps 15 and 19 (error logs): wire `error.message` and `error.error_type` Workato pills in GUI
3. Obtain real base URLs from SME to replace placeholders (see push script header)
4. `processACHBatch` recipe: not built — NACHA generation requires custom JS (see WMToWorkato.md Prompt 26)

---

### webMethods IS → Workato: GLD Compliance Migration (COMPLETE — 2026-06-19)
Source: `GLDComplianceAdapterServices` (webMethods IS 6.5, Oracle JDBC adapter, keybank.com).
Folder: `WebMethodsMigration` (folderId `31661117`, account `manish@techstonellc.com`)

| Component | ID / Details | Status |
|---|---|---|
| MIG_WM_GLD_Oracle_Connection | `19657520` — oracle, host CSC06DSHORA1S:1522 SID ILMSUM | Created (not authorized — needs GLD_SCHEMA password) |
| OracleConnection | `19661065` — oracle, credentials not yet set | Created (new — wire to step 2 new ACCLOGCHECKREQUEST action in GUI) |
| MIG_WM_GLDComplianceAdapterServices_Recipe | `73560615` — callable recipe (HTTP POST /compliance-check) | Pushed (v4 — IF/ELSE "Check CIU Result", http/post CIU, execute_stored_procedure, select_rows, rescue) |

**Reference files:**
- `WebMethods/MD/Workato.md` — authoritative recipe build reference
- `WebMethods/MD/PackageAnalysis.md` — Workato-oriented package analysis
- `WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx` — 22 construct mappings
- `Workato/Workato_Map_Field_Mappings.xlsx` — field mappings (3 sheets)
- `scripts/push_gld_workato_recipe.py` — recipe push script

**Remaining manual steps:**
1. Authorize Oracle connection `19657520` in Workato GUI (provide GLD_SCHEMA password, host, port, SID)
2. Step 3 (CIU placeholder): replace callable_recipe stub with HTTP action pointing to CIU endpoint URL
3. Retrieve `accCheckRequestID` after SP1: add SELECT query `SELECT MAX(ACCCHECKREQUESTID) FROM GLD_SCHEMA.ACCCHECKREQUEST WHERE REQUESTORSYSTEMREQUESTID=?`
4. Wire all oracle/run_sql steps with proper SP parameter bindings in Workato GUI
5. Test end-to-end with sample compliance check request

### webMethods IS → Workato: NewRecipe2 — GLD Compliance (COMPLETE — 2026-07-21)
Source: `GLDComplianceAdapterServices` (webMethods IS 6.5, Oracle JDBC adapter, keybank.com).
Folder: `migrAIte_Training/webMethodsMigration` (folderId `32050036`, account `manish@techstonellc.com`)
Built from: `WebMethods/MD/WMToWorkato.md` + `Workato/RecipeComponents/oracle.json` pattern.

| Component | ID / Details | Status |
|---|---|---|
| NewRecipe2 | `74259459` — callable recipe "Compliance Check" (25-field trigger) | Pushed (2026-07-21) |

**Recipe structure:** workato_service/receive_request trigger → try/catch block → Oracle SPs: ACCLOGCHECKREQUEST (25 params), SELECT ACCCHECKREQUESTID, LOGXMLREQUEST (5 params) → HTTP POST CIU → ACCUPDATECIUREFNBR → IF/ELSE CheckResult==TRUE → ACCLOGCHECKREPLY / ACCLOGCHECKREPLYERROR → 28-col JOIN SELECT → send_reply → catch: ACCLOGCHECKREPLYERROR
Push script: `scripts/push_newrecipe2_workato.py`

**Remaining manual steps:**
1. Wire Oracle connection `MIG_WM_GLD_Oracle_Connection` (ID: `19657520`) — authorize with GLD_SCHEMA password in GUI
2. Step 3 (HTTP CIU): replace `[CIU_ENDPOINT_URL]` placeholder with actual endpoint URL from SME; create HTTP connection in Workato GUI
3. Verify Step 1b SELECT correctly binds `REQUESTORSYSTEMREQUESTID` pill from trigger
4. Test end-to-end with sample compliance check request

---

### webMethods IS → Boomi: GLD Compliance Migration (COMPLETE — 2026-06-14, org account)
Source: `GLDComplianceAdapterEnv` + `GLDComplianceAdapterServices` (webMethods IS 6.5, Oracle JDBC adapter, keybank.com package).
Folder: `MIG_gld_compliance` (folderId `Rjo4NjIxNDk3`, account `tpptechstone-O6Y5DV`)

#### Sub-project A: GLDComplianceAdapterEnv (skeleton — 21 webMethods construct coverage)
| Component | ID | Notes |
|---|---|---|
| MIG_WM_GLD_DB_Connection (connector-settings) | 370bf544-60a9-4048-8197-0c442243571d | Oracle DatabaseV2, jdbc:oracle:thin:@CSC06DSHORA1S:1522:ILMSUM, user GLD_SCHEMA |
| MIG_WM_GLD_QueryCompliance_Operation (connector-action) | 62cc118c-14b6-4c10-bf56-08d37c208458 | SELECT from GLD_SCHEMA.COMPLIANCE_RECORDS WHERE STATUS='PENDING' ROWNUM<=1000 |
| MIG_WM_GLDCompliance_Process (process) | 8c2d51b4-d929-4fc5-baa9-814e4a3769d0 | 15-shape process covering all 21 webMethods constructs |

#### Sub-project B: GLDComplianceAdapterServices (functional migration — 7 Oracle SP/SELECT ops)
All 12 components pushed. Generator: `scripts/gen_gld_process.py`

| Component | ID | Notes |
|---|---|---|
| MIG_WM_GLD_DB_Connection (connector-settings) | 370bf544-60a9-4048-8197-0c442243571d | Reused from sub-project A |
| MIG_WM_GLD_MapTest_Source_Profile (profile.json) | bb7ed930-f04a-44e6-b09c-eb8a01965b98 | A1-A5 test fields |
| MIG_WM_GLD_MapTest_Target_Profile (profile.json) | 53c00ca7-9209-429a-ae57-ab87004d5343 | B1-B5 test fields |
| MIG_WM_GLD_MapTestSkill_Map (transform.map) | 9f06d114-4131-4e80-adf8-891da4563641 | Direct/Groovy/Default/Integer transformations |
| MIG_WM_GLD_LogCheckRequest_Operation (connector-action) | c398179a-9679-4727-b666-9efe7c0ed969 | SP: ACCLOGCHECKREQUEST, 25 IN params |
| MIG_WM_GLD_LogCheckRequestXML_Operation (connector-action) | f9571d99-a2bd-4945-893a-5ac49ace2770 | SP: LOGXMLREQUEST, 5 IN params |
| MIG_WM_GLD_LogCheckReply_Operation (connector-action) | 50970f87-b37a-4d82-8244-92afff5fbb17 | SP: ACCLOGCHECKREPLY, 3 IN params |
| MIG_WM_GLD_LogCheckReplyError_Operation (connector-action) | 1d853cdf-75fb-4603-9cbc-7aa3d055b5ad | SP: ACCLOGCHECKREPLYERROR, 4 IN params |
| MIG_WM_GLD_SelectCustomerRequest_Operation (connector-action) | 72e81746-77ca-4351-b866-1bad57a1fecf | SELECT DISTINCT JOIN, 1 IN (CIUREFNBR), 28 OUT fields |
| MIG_WM_GLD_UpdateCIURefNbr_Operation (connector-action) | ae2ca2df-cd5c-47c9-bcdf-bb76c2857244 | SP: ACCUPDATECIUREFNBR, 2 IN params |
| MIG_WM_GLD_PurgeData_Operation (connector-action) | b2488392-5fc5-4c1f-9a09-91210a3188bd | SP: ACCPURGEDATA, no params |
| MIG_WM_GLDComplianceAdapterServices_Process (process) | 9f634c7f-e394-49c0-a0c7-5a745a5788e2 | 23-shape process: Try/Catch, 7 DB ops, Map, Decision (true/false paths) |

**Output files:**
- `WebMethods/missing_components.xlsx` — 9 gap constructs not in the Excel mapping
- `WebMethods/map_field_mappings.xlsx` — Map shape field mapping template
- `WebMethods/MD/Boomi.md` — authoritative build reference synthesizing all source docs
- `scripts/gen_gld_process.py` — process XML generator (all shape types with correct schema)

**Remaining manual steps:**
1. shape2 (Set Properties): Wire 21 DDPs to actual input source fields — currently set to empty static placeholders
2. shape9 (Set Properties CIU): Replace with actual CIU HTTP/REST connector call, wire DPP_CIU_REF_NBR from response
3. shape6 (Set Properties): Wire DPP_ACC_CHECK_REQUEST_ID from logCheckRequest response (OUT param not auto-captured via Standard Insert)
4. shape15 (Decision): Wire DPP_CHECK_RESULT from CIU response — currently no DPP is being set to "TRUE"
5. DB Connection: Set `GLD_SCHEMA` password via Boomi Environment Extensions (password field is blank in XML)

#### webMethods → Boomi Component Mapping Reference
Source: `WebMethods/Agent Bridge Web Methods to Boomi Component Mapping.xlsx`

| # | webMethods Construct | Boomi Equivalent | Shape / Component | Notes |
|---|---|---|---|---|
| 1 | Workflow | Process | Start shape | Top-level container |
| 2 | TRY | Try/Catch (try path) | catcherrors shape, Try dragpoint | catchAll="true" |
| 3 | CATCH | Try/Catch (catch path) | catcherrors shape, Catch dragpoint | retryCount configurable |
| 4 | FINALLY | Route default branch | Route shape, Default dragpoint | Always executes |
| 5 | IF | Decision (true path) | decision shape | comparison="notequals" etc. |
| 6 | CASE | Route path (N≥3) | Route shape, keyed dragpoint | qualifier="equals" |
| 7 | ELSE | Decision (false path) | decision shape, false dragpoint | |
| 8 | ELSEIF | Chained Decision (false path) | Second decision shape on false path | Not in original mapping — see missing_components.xlsx |
| 9 | BRANCH | Branch shape | branch shape | numBranches=N |
| 10 | SWITCH | Route shape | route shape | routevalues keyed by value |
| 11 | SEQUENCE | Branch shape (2 tracks) | branch shape, identifier="1"/"2" | |
| 12 | LOOP | Data Process Groovy | dataprocess shape | Iterates over doc count |
| 13 | DO | Data Process Groovy | dataprocess shape | do-while variant in Groovy |
| 14 | WHILE | Data Process Groovy | dataprocess shape | while loop in Groovy |
| 15 | REPEAT | Data Process Groovy | dataprocess shape | repeat-until variant |
| 16 | UNTIL | Data Process Groovy | dataprocess shape | condition check in Groovy |
| 17 | CONTINUE | dataContext.discard() | Inside Groovy script | Skip current iteration |
| 18 | BREAK | Stop shape (continue=true) | stop shape | Exits current path, continues process |
| 19 | EXIT | Stop shape (continue=false) | stop shape | Terminates process execution |
| 20 | INVOKE | Connector step | connectoraction shape | DB/REST/etc. connector |
| 21 | MAP | Map shape | map shape | Requires Map component (mapId) |

---

### Oracle SOA Suite → Boomi: EBS Integrations (IN PROGRESS — SETUP PHASE)
25+ BPEL composites. Pipeline built and validated with samples; awaiting Oracle SOA credentials.

**Pipeline command (once credentials are in .env):**
```bash
# Live pull from Oracle SOA REST API
python migrate.py --from oracle_soa --to boomi --project oracle_ebs_migration

# OR from exported SAR files
python migrate.py --from oracle_soa --source-dir /path/to/sars/ --to boomi --project oracle_ebs_migration
```

**Pre-flight checklist:**
1. Add Oracle SOA credentials to `.env` (see `.env.example` for all required vars)
2. Run connector discovery: `bash <skill-path>/scripts/boomi-component-search.sh --name "%Oracle%EBS%" --type "connector-settings,connector-action"`
3. Run analyzer: `python analyzers/analyze_oracle_soa.py --project oracle_ebs_migration`
4. Review gaps in generated spec (BPEL `<flow>` parallel execution, `<wait>` timers, Human Tasks)
5. Run enrichment: `python enrichers/enrich_spec.py migration-specs/oracle_ebs_migration.json`
6. Generate Boomi processes: `python generators/generate_boomi.py migration-specs/oracle_ebs_migration.json`

**Key mapping decisions to review per composite:**
- Oracle EBS Adapter → check native connector in account, fallback to DatabaseV2 + PL/SQL
- Oracle AQ / JMS → Event Streams
- File/FTP Adapter → Disk V2
- DB Adapter → DatabaseV2 (direct mapping)
- `<flow>` parallel → Boomi Branch (sequential — medium severity gap)
- Oracle Mediator composites → flagged for manual analysis (not auto-migrated)
- Human Task composites → requires separate Boomi Flow implementation



