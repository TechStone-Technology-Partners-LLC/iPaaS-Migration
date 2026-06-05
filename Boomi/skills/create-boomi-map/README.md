# create-boomi-map skill

A Claude Code skill that builds Boomi Map components (source profile, target profile, and map XML)
from a structured mapping document such as an Excel spreadsheet, table, or written spec.

## What it does

Given a field mapping document, the skill will:
1. Parse the source and target field definitions and transformation rules
2. Ask you to confirm the source and target profile types (JSON / XML / Flat File / Database)
3. Generate and push the source profile XML to Boomi
4. Generate and push the target profile XML to Boomi
5. Generate and push the map component XML (with functions and defaults wired correctly)

## Supported profile types

| Type | Boomi component type |
|---|---|
| JSON | profile.json |
| XML | profile.xml |
| Flat File (CSV/delimited) | profile.flatfile |
| Database (read or write) | profile.db |

## Supported transformation patterns

- Direct field copy
- Date format conversion (any input/output mask)
- Value conversion via Groovy (e.g. true/false -> Y/N)
- Default values when source field is empty
- Field concatenation
- Static lookup / cross-reference

## Installation

### Prerequisites
- Claude Code with the skills plugin installed
- The `boomi-integration` skill must also be installed (this skill uses its CLI tools to push components)

### Install steps

1. Copy this folder to your skills directory:

   **Windows:**
   ```
   %APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\<session-id>\<user-id>\skills\create-boomi-map\
   ```

   **Mac / Linux:**
   ```
   ~/.config/Claude/local-agent-mode-sessions/skills-plugin/<session-id>/<user-id>/skills/create-boomi-map/
   ```

   The exact path can be found by checking where your other skills (e.g. `xlsx`, `docx`) are installed.

2. Package the skill using the skill-creator packager (run from the `skill-creator` directory):

   ```bash
   python -m scripts.package_skill ../create-boomi-map
   ```

3. Restart Claude Code — the skill will be available immediately.

## Usage

Trigger it by referencing a mapping document and asking Claude to build the map:

> "Create a Boomi map from the Excel mapping file in the Boomi folder"

> "Build the source profile, target profile, and map component from this table"

Claude will ask for source/target profile types before generating any XML.
