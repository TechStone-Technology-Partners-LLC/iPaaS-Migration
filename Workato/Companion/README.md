# Workato Companion Skill

A Claude Code skill for building, pushing, and managing Workato recipes programmatically via the Workato REST API. Designed for integration migration workflows (webMethods IS → Workato, Boomi → Workato, MuleSoft → Workato).

---

## What This Skill Does

- Builds Workato recipes as Python push scripts (callable, scheduled, event-based triggers)
- Pushes and updates recipes via the Workato REST API
- Manages folders and discovers connection `account_id` values
- Encodes all hard-won API rules (flatten schema, uuid on every step, toggleCfg, etc.)
- Serves as the navigation hub for recipe_components/, guides/, and platform_entities/ references

The authoritative reference for all rules, API patterns, and CLI tools is **[SKILL.md](SKILL.md)**.

---

## Prerequisites

1. **Python 3.8+** — stdlib only, no pip installs required
2. **Workato API token** — generate at Workato → Settings → API Tokens (any scope)
3. **`.env` file** in the workspace root with at least:
   ```
   WORKATO_API_TOKEN=your-token-here
   # Optional — only set if on a non-US datacenter
   # WORKATO_BASE_URL=https://www.workato.com/api
   ```

---

## Quick Start

**1. Verify your token and connectivity:**
```bash
python Workato/Companion/scripts/workato-env-check.py
```
Expected output: `OK — connected as <your email>`

**2. List your connections (get account_id values for recipes):**
```bash
python Workato/Companion/scripts/workato-connection-list.py
```
Copy the `id` column values — these are the `account_id` integers used in recipe `config` arrays.

**3. Search for existing recipes in a folder:**
```bash
python Workato/Companion/scripts/workato-recipe-search.py --folder-id 31835141
```

**4. Pull an existing recipe to inspect it:**
```bash
python Workato/Companion/scripts/workato-recipe-pull.py --recipe-id 74461604 --output recipe.json
```

**5. Create a new folder:**
```bash
python Workato/Companion/scripts/workato-folder-create.py --name "MyMigration" --parent-id 31835141
```

---

## Key Rules (Summary)

See [SKILL.md](SKILL.md) for the full 15-rule list with examples. The three most critical:

- **Flatten trigger schema** — Workato silently drops `type:"array"` and `type:"object"` fields from callable recipe schemas. Pass arrays as JSON strings.
- **`toggleCfg: {}` on every step** — Missing this causes silent breakage in the GUI.
- **`uuid` on every step** — Steps without UUIDs are silently dropped.

---

## Links

- [SKILL.md](SKILL.md) — Full skill definition, routing table, CLI reference, all hard-won rules
- [references/WORKATO_THINKING.md](references/WORKATO_THINKING.md) — Core mental models (read before building any recipe)
- [references/recipe_components/](references/recipe_components/) — Per-component JSON templates
- [references/guides/](references/guides/) — Datapill wiring, error handling, CLI tool reference
