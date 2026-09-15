# MigrAIte — How the Migration Workflow Works (internal)

The underlying flow that turns a webMethods package into a Workato recipe,
independent of how it is triggered (Claude Code session, CLI harness, or the
Google Chat bot). What the agent is given, what it produces at each step,
where the human is in the loop, and what rules govern the build.

Related: [Google Chat bot](migraite-gchat-bot.md) · [setup](migraite-bot-setup.md) · [client onboarding](migraite-client-onboarding.md) · [user guide](migraite-user-guide.md)

---

## 1. Overview

```
 webMethods package (zip)
        │
        ▼
 ┌─────────────┐   writes    WebMethods/Analysis/<pkg>_Analysis.md   (source-side detail)
 │ 1. ANALYZE  │ ─────────▶  WebMethods/MD/PackageAnalysis.md         (Workato blueprint)
 └─────────────┘
        │  summary + one question
        ▼
 ┌─────────────┐   human reads the blueprint, edits it / gives feedback
 │ 2. REVIEW   │ ◀────────▶ agent revises the files, checks in again
 └─────────────┘
        │  "approved"
        ▼
 ┌─────────────┐   which Workato folder?
 │ 3. APPROVAL │
 └─────────────┘
        │
        ▼
 ┌─────────────┐   Workato AIRO MCP: init → trigger → steps → fields → connections → push
 │ 4. BUILD    │ ─────────▶ recipe in the client's Workato workspace
 └─────────────┘
        │
        ▼
 ┌─────────────┐   recipe URL + remaining manual steps; notes in migration-specs/<pkg>_progress.md
 │ 5. DELIVER  │
 └─────────────┘
```

The agent is Claude running as the Claude Code engine (via the Claude Agent
SDK when headless) with this repository as its working directory. It is the
same agent whether a person drives it in a terminal or the bot drives it from
Chat; only the transport differs.

---

## 2. What the agent is given

Everything the agent knows comes from three sources.

### 2.1 Repository context (loaded automatically)

Because the session runs with the repository as `cwd` and project settings
enabled, the engine loads:

- **`CLAUDE.md`** — the project instructions: the migration agent overview,
  the 5-phase pipeline conventions, naming conventions, session-continuity
  rules, and the history of past migrations with their component IDs. This is
  the agent's standing knowledge of how work is done here.
- **Project skills and settings** under `.claude/`.

### 2.2 The instruction documents (referenced by the kickoff prompt)

- **`initiate_migration/Instruction_Workato.md`** — the workflow contract.
  Step 1 defines the Package Analysis Document and its required sections
  (Package Overview; Shapes & Logic Breakdown; Connections; Operations; Data
  Mappings; Business Rules & Conditions; Error Handling; Equivalent Recipe
  Structure; Mapping Gaps / Deviations). Step 2 is the approval gate ("do not
  create any Workato recipe or components until approval is confirmed").
  Step 3 states the build rules (best purpose-built connector; fully
  configure each connection and operation before moving on; realistic dummy
  values for missing auth, never blanks; stay true to the approved document
  and flag deviations).
- **`WebMethods/Agent Bridge Web Methods to Workato Component Mapping.xlsx`**
  — the construct-mapping reference (TRY/CATCH, LOOP, BRANCH, MAP, INVOKE …
  → Workato constructs). The instructions say: consult it first, prefer the
  most specific connector, treat it as a guide not a rulebook, and flag every
  gap in the Mapping Gaps section rather than guessing.
- **`Workato/RecipeComponents/*.json`** — canonical examples of Workato
  step JSON per construct, used when the agent needs to know what a correct
  step looks like.
- **`WebMethods/start.md`** and the historical `WebMethods/MD/*` documents —
  prior runs' outputs, available as reference when useful.

### 2.3 The kickoff prompt (`gchat/prompts.py`)

The prompt does not re-teach the workflow; it points at the documents above
and adds what the delivery channel needs:

- where the package is (`WebMethods/<pkg>/`) and that it was pre-extracted;
- the user's own instructions, if any were sent with the upload;
- the phase sequence and the gates (below);
- when to pause with a question versus record a gap and continue;
- chat-oriented output rules (one question per turn, short messages, no
  narration, full file paths in summaries);
- where run notes go (`migration-specs/<pkg>_progress.md`, never
  `CLAUDE.md`).

A short **re-anchor header** is prepended to every subsequent user reply
(package, phase, the one-question rule) so a long session that has been
context-compacted re-grounds itself; the files on disk stay the source of
truth.

---

## 3. Phase 1 — Analyze

**Input.** The package directory: `manifest.v3`, `ns/` (flow services as
`flow.xml`, node definitions `node.ndf`, document types, adapter services),
`pub/`, and any sibling packages already present in the repository that the
package invokes.

**What the agent does.** Reads every file (it typically shells out to walk
the tree, decodes base64-embedded schemas, follows `INVOKE` references into
sibling packages when present), then writes:

- `WebMethods/Analysis/<pkg>_Analysis.md` — the **source-side** record:
  every service and shape, pipeline in/out, adapter configurations, data
  formats, defects noticed in the source. Audience: someone who knows the
  webMethods package and wants to verify the agent understood it.
- `WebMethods/MD/PackageAnalysis.md` — the **target-side blueprint** with
  the required sections, plus explicit deviations (e.g. "BRANCH mapped to
  if/elsif/else, not the Excel's parallel-step row, because the source is a
  value switch") and a numbered gap list (unsourced endpoints, missing
  packages, source defects, constructs absent from the mapping Excel).

**Rules during analysis.**
- AIRO is not used. The analysis is grounded in the package and the mapping
  documents only, so it describes what is faithful to the source rather than
  what happens to exist in a workspace.
- Pause and ask when an answer would change the analysis (ambiguous business
  logic, contradictory files). Do not pause for build-time details (URLs,
  credentials, SME confirmations) — record them as gaps.
- End the phase with a concise summary and exactly one question.

**Output to the human.** The summary: what the package does, systems
involved, proposed recipe structure, gaps needing attention, full paths of
the files written, and the question. Through the bot, the two files also
arrive as Google Docs.

---

## 4. Phase 2 — Review loop

The human reviews the blueprint and responds in one or both ways:

- feedback in conversation ("Wire is intentional, drop G-4"; "use the Oracle
  connector for ACH"), or
- direct edits to the analysis text (in the Google Doc when using the bot;
  in the file when working locally).

The agent revises both files as needed, states what changed, and checks in
again. This repeats until the human explicitly approves. Nothing is created
in Workato during this phase.

---

## 5. Phase 3 — Approval and target folder

On approval the agent asks one question: which Workato folder to build in
(it lists folders via AIRO and suggests the configured default). This is the
first AIRO call of the run.

---

## 6. Phase 4 — Build via the Workato AIRO MCP

**What AIRO is.** Workato's MCP server (`https://app.workato.com/airo_mcp`)
exposes a structured recipe-builder API — `recipe_builder_init`,
`recipe_builder_add_step`, `recipe_builder_set_input_field`,
`recipe_builder_get_datapills`, `recipe_builder_set_condition`,
`recipe_builder_set_foreach_source`, `recipe_builder_select_connections`,
`recipe_builder_push`, and more — plus its own documentation served through
`docs_get`. It is not a "prose in, recipe out" endpoint; the natural-language
intelligence is the agent driving these tools. It validates each step against
real connector schemas and datapills, which is why it replaced the earlier
hand-authored recipe-JSON push scripts.

**Rules the agent follows.**
1. First call `docs_get(id="guides:recipe-builder")` and follow that guide;
   load per-tool docs as it directs.
2. Build from the approved `WebMethods/MD/PackageAnalysis.md` — its
   "Equivalent Recipe Structure" section is the spec. Consult the detailed
   analysis for source detail.
3. Never hand-author datapill paths; always resolve them with
   `recipe_builder_get_datapills`.
4. Use `recipe_builder_list_connections` to find existing connections and
   select them. Where a connector has no connection, configure the step as
   far as the schema allows (AIRO cannot expose connector field schemas
   without a live connection) and record the wiring as a manual step — the
   11-column Oracle mapping, for example, is placed in the step comment so it
   is visible in the GUI.
5. Preserve structural rules from the blueprint: outer try/catch, per-item
   try/rescue *inside* the loop so one bad payment does not abort the rest,
   reply outside the try, typed nested arrays where a loop needs a list
   datapill.
6. Finish with `recipe_builder_push`.

**Where it runs.** The recipe is created in the workspace of the Workato user
whose AIRO login the session carries — the client's, in the target model
(see [client onboarding](migraite-client-onboarding.md)).

---

## 7. Phase 5 — Deliver

The final message contains the recipe URL, what was built (trigger, loops,
branches, error handling), and the remaining manual steps — typically
creating and authorizing connections in the Workato GUI and wiring them to
the listed steps, plus values needing an SME. Run notes go to
`migration-specs/<pkg>_progress.md`. Afterwards, change requests are applied
to the same recipe via `recipe_builder_pull` and pushed again.

---

## 8. Artifacts at a glance

| Artifact | Path | Phase |
|---|---|---|
| Extracted package | `WebMethods/<pkg>/` | intake |
| Source analysis | `WebMethods/Analysis/<pkg>_Analysis.md` | 1 |
| Blueprint | `WebMethods/MD/PackageAnalysis.md` | 1–2 |
| Recipe | Workato workspace / chosen folder | 4 |
| Run notes | `migration-specs/<pkg>_progress.md` | 5 |

Today the blueprint path is fixed, which is why only one migration runs at a
time per working directory; per-client working directories remove that limit
(see the bot doc).

---

## 9. Cost, models, timing

Sessions inherit the engine's defaults — observed `claude-opus-5` at `high`
effort. Analysis ≈ 10–15 minutes and $4–5; build ≈ 20–30 minutes; a full run
≈ $10–20. Quality of the analysis has been the strongest part of the flow
(e.g. NACHA field layouts decoded from base64 schemas, source defects
detected); the build phase is where a project skill capturing our
migration-specific conventions would be distilled from real runs.
