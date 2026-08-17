# CLI Tool Reference

All scripts live under `scripts/` in the Workato Companion workspace.
Run from the workspace root. Credentials are read from `.env` (WORKATO_API_TOKEN,
WORKATO_EMAIL). The Workato API base URL is `https://www.workato.com/api`.

---

## 1. workato-recipe-list.py

List recipes in a folder.

```bash
python scripts/workato-recipe-list.py --folder-id FOLDER_ID
python scripts/workato-recipe-list.py --folder-id FOLDER_ID --active-only
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--folder-id` | (required) Workato folder ID (integer) |
| `--active-only` | Filter to running recipes only |

**Output:** Table of `id`, `name`, `running` status.

---

## 2. workato-recipe-get.py

Fetch full recipe JSON (trigger + all steps) for inspection.

```bash
python scripts/workato-recipe-get.py --recipe-id RECIPE_ID
python scripts/workato-recipe-get.py --recipe-id RECIPE_ID --pretty
python scripts/workato-recipe-get.py --recipe-id RECIPE_ID --out recipe_backup.json
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--recipe-id` | (required) Recipe ID (integer) |
| `--pretty` | Pretty-print the code and config JSON |
| `--out FILE` | Write JSON to file instead of stdout |

**Use this before any PUT update** to read current state and avoid clobbering changes.

---

## 3. workato-recipe-create.py

Create a new recipe by posting a code/config JSON file.

```bash
python scripts/workato-recipe-create.py --name "My Recipe" --folder-id FOLDER_ID --code recipe.json
python scripts/workato-recipe-create.py --name "My Recipe" --folder-id FOLDER_ID --code recipe.json --config config.json
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--name` | (required) Recipe display name |
| `--folder-id` | (required) Target folder ID (integer) |
| `--code FILE` | Path to trigger JSON file (`code` field) |
| `--config FILE` | Path to config JSON file (`config` field); optional |

**Output:** Recipe ID on success.

---

## 4. workato-recipe-update.py

Update an existing recipe. Reads current state first, merges changes, then PUTs.

```bash
python scripts/workato-recipe-update.py --recipe-id RECIPE_ID --code new_code.json
python scripts/workato-recipe-update.py --recipe-id RECIPE_ID --code new_code.json --config new_config.json
python scripts/workato-recipe-update.py --recipe-id RECIPE_ID --name "New Name"
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--recipe-id` | (required) Recipe ID to update |
| `--code FILE` | New trigger JSON file; replaces existing code |
| `--config FILE` | New config JSON file; replaces existing config |
| `--name STR` | New recipe name |

**Note:** Stop the recipe in GUI before updating if it is currently running.

---

## 5. workato-folder-list.py

List folders in the account.

```bash
python scripts/workato-folder-list.py
python scripts/workato-folder-list.py --parent-id FOLDER_ID
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--parent-id` | Filter to subfolders of this parent folder |

**Output:** Table of `id`, `name`, `parent_id`.

---

## 6. workato-folder-create.py

Create a new folder.

```bash
python scripts/workato-folder-create.py --name "MyFolder"
python scripts/workato-folder-create.py --name "SubFolder" --parent-id PARENT_ID
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--name` | (required) Folder display name |
| `--parent-id` | Parent folder ID; omit for root-level folder |

**Output:** New folder ID.

---

## 7. workato-connection-list.py

List all connections (apps) in the account with their IDs.

```bash
python scripts/workato-connection-list.py
python scripts/workato-connection-list.py --provider oracle
python scripts/workato-connection-list.py --provider salesforce
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--provider` | Filter by provider name (partial match) |

**Output:** Table of `id`, `name`, `provider`, `authorized` status.

Use this to find the correct `account_id` integer for the config array.

---

## 8. workato-lookup-table-list.py

List lookup tables in the account.

```bash
python scripts/workato-lookup-table-list.py
python scripts/workato-lookup-table-list.py --name "Payment Types"
```

**Flags:**
| Flag | Description |
|------|-------------|
| `--name` | Filter by lookup table name (partial match) |

**Output:** Table of `id`, `name`, `columns`, `entry_count`.

---

## General Notes

- All scripts load credentials from `.env` using `python-dotenv` or environment variables.
  Do not pass tokens on the command line.
- All scripts exit with code 0 on success, non-zero on error.
- Most scripts print the raw Workato API response on failure for debugging.
- The Workato API rate limit is approximately 100 requests/minute. For bulk operations,
  add `time.sleep(0.6)` between calls.
- The US datacenter URL is `https://www.workato.com/api`. EU datacenter uses
  `https://app.eu.workato.com/api`. The `wrkaus-` token prefix does NOT mean AU region —
  the US endpoint is still correct for accounts with this prefix.
