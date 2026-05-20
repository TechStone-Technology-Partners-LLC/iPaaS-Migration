# Migration Thinking — Core Mental Models

## The Migration Agent's Job

This agent migrates integration logic — not code. The goal is to produce a Boomi integration that does the same thing as the source, not one that looks like the source. MuleSoft DataWeave becomes a Boomi Map. A MuleSoft choice router becomes a Boomi Decision or Route step. Don't try to port idioms; find the Boomi-native equivalent.

---

## The Three-Phase Model

Every migration follows the same three phases:

```
ANALYZE → MAP → GENERATE
```

**Phase 1 — Analyze**: Parse the source system artifacts into a normalized migration spec (`migration-spec.json`). The analyzer scripts handle this. The output is source-agnostic.

**Phase 2 — Map**: Read the migration spec and determine the Boomi equivalent for each component. Use `references/source-systems/<system>_mapping.md` and the boomi-integration skill's reference docs. Identify gaps (components that have no clean mapping) and note them.

**Phase 3 — Generate**: Use the boomi-integration skill to build the Boomi components from the mapping decisions. Follow the standard push-as-you-go workflow. One Boomi process per source flow.

Never skip to Phase 3 from a source artifact. Always go through the normalized spec.

---

## The Migration Spec as Lingua Franca

The `migration-spec.json` is the central contract between the analyzer and the generator. It is source-agnostic JSON that describes:
- What triggers the integration
- What steps it performs (in order)
- What connections/systems it depends on
- What data transformations occur
- How errors are handled

See `references/migration_spec_schema.md` for the full schema.

**Rule**: If the analyzer cannot represent something in the migration spec, flag it as `"type": "custom"` with `"requires_review": true`. Never silently drop a step.

---

## Mapping Principles

### 1. Conservative Mapping
When a source component has multiple plausible Boomi equivalents, pick the simpler one. A Boomi Message step is better than a Data Process Groovy step if both would work. Complexity should be introduced only when the simpler option provably can't do the job.

### 2. Pattern-Over-Component Mapping
Don't map component-by-component in isolation. First identify the integration pattern:
- **Request-Reply API**: HTTP listener → process → response
- **Scheduled Batch**: Scheduler → data fetch → transform → push
- **Event-Driven**: Message listener → process → acknowledge
- **File Processing**: File listener → parse → transform → deliver
- **System Sync**: Scheduler → query source → upsert target

The pattern determines the overall Boomi process structure. Individual components fill in the steps within that structure.

### 3. Transformation Complexity Tiers
MuleSoft DataWeave transformations map to Boomi differently based on complexity:

| DataWeave Complexity | Boomi Equivalent |
|---|---|
| Simple field mapping (rename, reorder) | Map component |
| Conditional field logic (`if`, `when`) | Map component with functions |
| Array iteration, filtering | Map component with functions |
| Complex business logic, recursive | Data Process (Groovy) step |
| Just setting a static payload | Message step |

Default to Map component. Escalate to Groovy only when Map component functions cannot express the logic.

### 4. Variable → Property Mapping
- MuleSoft `set-variable` (flow-scoped) → Boomi DPP (Dynamic Process Property)
- MuleSoft `set-payload` → Boomi Message step (static) or stays as document payload (dynamic)
- MuleSoft `attributes` (inbound HTTP headers/params) → Boomi DDPs extracted via Set Properties step

### 5. Sub-flows → Subprocesses
Every MuleSoft `<sub-flow>` becomes a separate Boomi process connected via a Process Call step. This preserves modularity and makes individual flows independently testable.

### 6. Error Handling
- `on-error-propagate` → Boomi Try/Catch with re-throw (Exception step in catch branch)
- `on-error-continue` → Boomi Try/Catch that logs and continues (no Exception step)
- Global error handlers → Boomi parent process wrapping subprocess with Try/Catch

---

## Naming Conventions for Migrated Components

Use a consistent prefix to identify migrated components in Boomi:

```
MIG_<SourceSystem>_<FlowName>_<ComponentType>
```

Examples:
- `MIG_MS_GetCustomers_Process` — MuleSoft "get-customers-flow" migrated process
- `MIG_MS_PostgreSQL_Connection` — MuleSoft DB config migrated to Boomi connection
- `MIG_MS_CustomerResponse_JSON_Profile` — JSON profile for customer response

Folder structure in Boomi:
```
ClaudeCode/
  MIG_<ProjectName>/
    Processes/
    Connections/
    Operations/
    Profiles/
```

---

## Handling Gaps

Not every source component has a clean Boomi equivalent. Common gaps:

| Source Pattern | Gap | Resolution |
|---|---|---|
| MuleSoft scatter-gather (true parallel) | Boomi Branch is sequential | Use Branch with note that parallel execution is not preserved |
| MuleSoft batch job (record-level error isolation) | No direct equivalent | Use Data Process split + subprocess with Try/Catch per record |
| MuleSoft async scope | No direct async step | Separate Boomi process deployed independently |
| Complex DataWeave (recursive, reduce) | Map component can't express | Data Process Groovy step |
| OAuth user grant flows | Requires GUI setup | Flag for user action; create connection placeholder |

When a gap is identified:
1. Note it in the migration spec under `"gaps"`
2. Implement the closest Boomi equivalent
3. Add a shape note in the Boomi canvas describing the behavioral difference
4. Inform the user explicitly

---

## What NOT to Migrate

Some things in source systems should be left behind, not ported:

- **Source-specific config keys** (`${sf.username}` etc.) → use Boomi process extensions / environment extensions
- **Platform-specific retry logic** → Boomi handles retries at the atom level; simplify in-process retry
- **Dead code / unused flows** → skip if a flow has no listener and no flow-ref callers
- **Logging verbosity** → migrate only ERROR and WARN-level logic; DEBUG loggers become Notify steps for key checkpoints only

---

## Session Continuity

Migration projects are multi-session. Save progress by:
1. Committing `migration-specs/` outputs to the repo after each analysis run
2. Updating `migration-specs/<project>_progress.md` after each generation session (which flows done, which pending, which blocked)
3. Using Boomi component `.sync-state/` to track what's been pushed to the platform

At the start of each new session: read the progress file first, then resume from where the previous session left off.
