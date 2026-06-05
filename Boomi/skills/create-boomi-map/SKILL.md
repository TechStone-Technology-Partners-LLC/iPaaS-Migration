---
name: create-boomi-map
description: >
  Builds Boomi Map components (with source profile, target profile, and map XML) from a
  structured mapping document such as an Excel spreadsheet, table, or written spec.
  Use this skill whenever the user provides field-to-field column mappings and asks to
  create a Boomi Map, profile, or transformation — even if they say "build a map",
  "create the profiles", "set up a transformation", or "wire up the fields".
  Supports all Boomi profile types: JSON, XML, Flat File, and Database.
---

# create-boomi-map

Builds the three Boomi artifacts that make up a field mapping:
1. Source profile (the input document structure)
2. Target profile (the output document structure)
3. Map component (field-to-field wiring with functions and defaults)

## Step 1 — Read the mapping spec

Read the provided file (Excel, table, or doc) to extract:
- Source field names and data types
- Target field names and data types
- Transformation rules per field (direct copy, date format, value conversion, default, lookup, concat, etc.)

## Step 2 — Ask the user for profile types

Before writing any XML, ask the user to confirm:
- What is the **source** profile type? (JSON / XML / Flat File / Database)
- What is the **target** profile type? (JSON / XML / Flat File / Database)

Do not assume — these are required to pick the correct XML schema for each profile.
Also ask for the component name prefix (e.g. `MIG_WM_LoanMapping`) if not already clear from the spec.

## Step 3 — Build the source profile

Use `references/profile-schemas.md` for the correct XML template for the chosen source profile type.

Key rules:
- Component `type` attribute must match the profile type (see schema reference)
- Assign keys starting from the correct offset for that profile type
- Use field data types from the mapping (character, boolean, number, date, etc.)
- Use `boomi-component-create.sh` to push; capture the returned component ID

## Step 4 — Build the target profile

Same as Step 3, using the target profile type. Push and capture the target component ID.

## Step 5 — Build the map component

Use `references/map-patterns.md` for function XML patterns.

Map component rules:
- `fromProfile` = source component ID
- `toProfile` = target component ID
- For each mapping row, write a `<Mapping>` element using field keys from the profiles
- For transformations, add `<FunctionStep>` elements — each must have `x` and `y` position floats (space them 140.0 apart vertically, starting at y=10.0)
- For default values, add `<Default>` elements inside `<Defaults>`
- The `<Functions>` block must have `optimizeExecutionOrder="true"`

## Step 6 — Push the map

Use `boomi-component-create.sh` to push the map XML. Report:
- Source profile name and ID
- Target profile name and ID
- Map name and ID
- Any TODO items (e.g. date Input Mask to confirm, placeholder connection to replace)

## Naming convention

Follow the pattern already established in the project or use:
```
MIG_<System>_<FlowName>_Source_Profile
MIG_<System>_<FlowName>_Target_<Type>_Profile
MIG_<System>_<FlowName>_Map
```

## Transformation type reference

| Spec language | Boomi mechanism | See |
|---|---|---|
| Direct copy | `<Mapping fromKey="N" toKey="M"/>` (no function) | map-patterns.md |
| Date format / reformat | FunctionStep type="DateFormat" | map-patterns.md |
| Boolean / value conversion (e.g. true->Y) | FunctionStep type="Scripting" (Groovy) | map-patterns.md |
| Default when source empty | `<Default toKey="M" value="..."/>` | map-patterns.md |
| Concatenate fields | FunctionStep type="Concat" | map-patterns.md |
| Static lookup / cross-reference | FunctionStep type="LookupTable" or cross-reference component | map-patterns.md |

## Reference files

- `references/profile-schemas.md` — XML templates for all four profile types with correct key offsets
- `references/map-patterns.md` — XML snippets for every map function pattern
