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

## Migration Agent Workflow

Every migration follows this pipeline. Never skip phases.

```
PHASE 0 — PULL         (if source is a live platform)
                       Boomi: boomi-component-search.sh + boomi-component-pull.sh
                       MuleSoft: project files already on disk (no pull needed)

PHASE 1 — ANALYZE      Run the analyzer for the source system.
                       Output: migration-specs/<project>.json
                       This spec is platform-agnostic — it has no target-specific concepts.

PHASE 2 — GENERATE     Run the generator for the target system.
                       One target artifact per source flow.
```

### Single-command entry point

For real-world usage, use `migrate.py` — it orchestrates all phases:

```bash
# Migrate a Boomi folder to Workato (pulls live from Boomi, generates in Workato)
python migrate.py --from boomi --boomi-folder "My Folder Name" --to workato

# Migrate a MuleSoft project to Workato
python migrate.py --from mulesoft --source-dir samples/mulesoft/customer-api/ --to workato

# Dry run (print Workato recipe JSON without pushing)
python migrate.py --from boomi --boomi-folder "My Folder" --to workato --dry-run

# Skip pull (analyze already-downloaded active-development/ files)
python migrate.py --from boomi --source-dir active-development/ --to workato
```

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

### webMethods IS → Workato: GLD Compliance Migration (COMPLETE — 2026-06-19)
Source: `GLDComplianceAdapterServices` (webMethods IS 6.5, Oracle JDBC adapter, keybank.com).
Folder: `WebMethodsMigration` (folderId `31661117`, account `manish@techstonellc.com`)

| Component | ID / Details | Status |
|---|---|---|
| MIG_WM_GLD_Oracle_Connection | `19657520` — oracle, host CSC06DSHORA1S:1522 SID ILMSUM | Created (not authorized — needs GLD_SCHEMA password) |
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



