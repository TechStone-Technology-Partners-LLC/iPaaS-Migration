# Workato Recipe Reference Guide
> Compiled from official Workato documentation + confirmed live API behaviour.
> Source: https://docs.workato.com/en/recipes/building-recipes

---

## 1. Recipe Architecture

A Workato recipe is a JSON document with two top-level sections:

| Field | Type | Description |
|---|---|---|
| `code` | JSON string | Serialised trigger step (root) containing all child steps in `block` |
| `config` | JSON array | Connection bindings — maps a provider to an account ID |

```json
{
  "recipe": {
    "name": "My Recipe",
    "folder_id": "12345",
    "code": "<serialised trigger+block JSON>",
    "config": "[{\"keyword\":\"application\",\"name\":\"oracle\",\"provider\":\"oracle\",\"account_id\":19661065,\"skip_validation\":false}]"
  }
}
```

---

## 2. Trigger Types

### 2.1 Polling Trigger
Checks for new events at a fixed interval (minimum 5 minutes).

```json
{
  "number": 0, "keyword": "trigger",
  "provider": "rest", "name": "new_event_via_polling",
  "as": "rest_new_event_via_polling",
  "dynamicPickListSelection": {}, "toggleCfg": {},
  "input": {},
  "uuid": "<uuid>", "block": [ ... ]
}
```

### 2.2 Scheduled Trigger (Clock)
Runs on a fixed schedule.

```json
{
  "number": 0, "keyword": "trigger",
  "provider": "clock", "name": "scheduled_event",
  "as": "scheduled_event",
  "dynamicPickListSelection": {}, "toggleCfg": {},
  "input": { "time_unit": "minutes", "trigger_every": "5" },
  "uuid": "<uuid>", "block": [ ... ]
}
```

- `time_unit`: `"seconds"` | `"minutes"` | `"hours"` | `"days"` | `"weeks"` | `"months"`
- `trigger_every`: string integer; minimum `"5"` for minutes.
- **Note**: Workato's GET API strips `trigger_every` when it equals the default — it is still applied at runtime.

### 2.3 Callable Recipe Trigger (HTTP Endpoint)
Exposes the recipe as a synchronous HTTP endpoint.

```json
{
  "number": 0, "keyword": "trigger",
  "provider": "workato", "name": "callable_recipe",
  "as": "callable_recipe",
  "dynamicPickListSelection": {}, "toggleCfg": {},
  "input": {
    "http_method": "post",
    "request_url_suffix": "/my-endpoint",
    "response_type": "dynamic",
    "input_fields_raw_schema": "[{\"name\":\"field1\",\"type\":\"string\",\"optional\":false,\"label\":\"Field 1\"}]"
  },
  "uuid": "<uuid>", "block": [ ... ]
}
```

- `input_fields_raw_schema`: JSON-serialised array. Fields must be **scalar only** (`string`, `integer`, `number`, `boolean`, `date`, `datetime`). Using `type:"object"` or `type:"array"` silently wipes the entire trigger input.
- Workato's GET API never returns `callable_recipe` trigger input — this is expected.

### 2.4 Recipe Function Trigger
Exposes the recipe as a callable function (newer pattern).

```json
{
  "number": 0, "keyword": "trigger",
  "provider": "workato_recipe_function", "name": "execute",
  "as": "<short-uuid>",
  "input": {
    "parameters_schema_json": "[{\"name\":\"firstName\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"First Name\"}]"
  },
  "extended_output_schema": [{
    "label": "Parameters", "name": "parameters", "type": "object",
    "properties": [
      {"control_type":"text","label":"First Name","name":"firstName","type":"string","optional":false}
    ]
  }],
  "uuid": "<uuid>", "block": [ ..., { "number": N, "keyword": "action", "provider": "workato_recipe_function", "name": "return_result", "as": "<uuid>", "input": {} } ]
}
```

- Always end the block with a `workato_recipe_function/return_result` action so callers receive a response.

### 2.5 Database Trigger (New/Updated Row)
```json
{
  "number": 0, "keyword": "trigger",
  "provider": "oracle", "name": "new_updated_row",
  "as": "oracle_new_updated_row",
  "dynamicPickListSelection": {}, "toggleCfg": {},
  "input": { "table": "", "unique_key": "", "since": "" },
  "uuid": "<uuid>", "block": [ ... ]
}
```
Connection reference goes in recipe `config` (see §8).

---

## 3. Step (Action) Types

All steps live in the `block` array of the trigger (or a parent step).

### 3.1 Connector Action
```json
{
  "number": N, "keyword": "action",
  "provider": "<app>", "name": "<operation>",
  "as": "<alias>",
  "dynamicPickListSelection": {}, "toggleCfg": {},
  "input": { "<field>": "<value or datapill>" },
  "uuid": "<uuid>"
}
```

Common `provider`/`name` pairs (confirmed live):

| App | provider | name |
|---|---|---|
| Oracle DB | `oracle` | `execute_stored_procedure`, `select_rows`, `run_sql` |
| PostgreSQL | `postgresql` | `select_rows`, `insert_row`, `update_rows` |
| Salesforce | `salesforce` | `create`, `update`, `search` |
| Google Sheets | `google_sheets` | `add_spreadsheet_row_v4` |
| HTTP/REST | `http` | `post`, `get`, `put`, `patch`, `delete` |
| Workato | `workato` | `callable_recipe_response` |
| Recipe Function | `workato_recipe_function` | `return_result` |

### 3.2 Action Categories

| Category | Behaviour |
|---|---|
| **Create** | Creates a new record; returns ID or full object |
| **Update** | Modifies existing record by ID |
| **Search** | Returns all matching records or empty list (never throws error) |
| **Get** | Returns single record by ID; throws error if not found |
| **Upsert** | Search first, then create or update |
| **Delete** | Removes record by ID (limited connector support) |

---

## 4. Control Flow Steps

All control-flow steps use `keyword` only — **no** `provider`/`name`/`as`/`dynamicPickListSelection`.

### 4.1 IF / ELSE

```json
{
  "number": N, "keyword": "if",
  "uuid": "<uuid>",
  "input": {
    "type": "compound", "operand": "and",
    "conditions": [{ "operand": "equals", "lhs": "#{datapill}", "rhs": "value" }]
  },
  "block": [ ... ]
}
```

```json
{ "number": N+1, "keyword": "else", "uuid": "<uuid>", "block": [ ... ] }
```

**Condition operands**: `equals`, `not_equals`, `greater_than`, `less_than`, `contains`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty`

### 4.2 Repeat For Each (Loop)

```json
{
  "number": N, "keyword": "each",
  "as": "loop_item",
  "uuid": "<uuid>",
  "input": { "source": "#{datapill_to_array}" },
  "block": [ ... ]
}
```

- `source`: a datapill resolving to an array/list.
- If the source is a JSON string pill, append `.parse_json`: `"#{pill.parse_json}"`
- Access iteration variable: `"#{_['loop_item']['field_name']}"`

### 4.3 Handle Errors (Monitor + Rescue)

**Pattern**: `monitor` (outer try-body wrapper) → `rescue` (nested catch block).

```json
{
  "number": 1, "keyword": "monitor",
  "uuid": "<uuid>",
  "title": "Handle errors",
  "block": [
    { "number": 2, "keyword": "action", ... },
    { "number": 3, "keyword": "action", ... },
    {
      "number": 4, "keyword": "rescue",
      "uuid": "<uuid>",
      "block": [
        { "number": 5, "keyword": "action", ... }
      ]
    }
  ]
}
```

**Rules**:
- `monitor` = labelled "Handle errors" in the Workato canvas. All try-body steps go INSIDE the monitor `block`, before the rescue.
- `rescue` = the catch block. Must always be the LAST item in the monitor's `block`.
- A `rescue` with empty `block: []` is valid — users add error-handler steps in the GUI.
- Step numbers must be globally unique and increasing: container < children.
- Retry is configured in the GUI on the rescue block (not in JSON).
- **Never** use `keyword:"action"` with `name:"monitor"` — Workato renders it as "Select an app and action".

### 4.4 Stop Job

```json
{ "number": N, "keyword": "stop", "uuid": "<uuid>", "input": { "status": "failed", "message": "..." } }
```

`status`: `"failed"` | `"succeeded"`

---

## 5. Data Pills

Datapills are variables referencing output from any prior step.

### 5.1 Pill Syntax in JSON

```
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"<provider>\",\"line\":\"<as_alias>\",\"path\":[\"field\",\"nested_field\"]}')}""
```

Shorthand (used directly in `input` field values):

```
"#{callable_recipe['field_name']}"
"#{loop_item['amount']}"
"#{oracle_new_updated_row['id']}"
```

### 5.2 Data Types

| Type | Notes |
|---|---|
| `string` | Default; use `.to_s` to convert |
| `integer` | Use `.to_i` to convert |
| `number` | Float; use `.to_f` |
| `boolean` | `true` / `false` |
| `date` | Format: `YYYY-MM-DD` |
| `datetime` | UTC timestamp |
| `array`/`list` | Ordered collection; iterable with `each` |
| `object`/`hash` | Key-value pairs |

### 5.3 System Datapills (always available via Properties)
- `#{_('job_id')}` — current job ID
- `#{_('recipe_id')}` — recipe ID
- `#{_('job_created_at')}` — job start timestamp

---

## 6. Formula Mode (Ruby)

Formula mode is activated per-field in the Workato step editor. All formulas are **allowlisted Ruby methods**.

> Most formulas return an error if they operate on null values — except `present?`, `presence`, and `blank?`.

### 6.1 String Formulas

| Formula | Description | Example |
|---|---|---|
| `blank?` | True for null / empty / whitespace | `"".blank?` → `true` |
| `present?` | True for non-null non-empty | `"abc".present?` → `true` |
| `strip` / `lstrip` / `rstrip` | Remove whitespace | `" abc ".strip` → `"abc"` |
| `upcase` / `downcase` | Case conversion | `"abc".upcase` → `"ABC"` |
| `capitalize` / `titleize` | Sentence / title case | |
| `gsub(find, replace)` | Global find-replace | `"hello".gsub("l","r")` → `"herro"` |
| `sub(find, replace)` | First occurrence only | |
| `split(delimiter)` | String → array | `"a,b".split(",")` → `["a","b"]` |
| `include?` / `exclude?` | Substring check | |
| `starts_with?` / `ends_with?` | Positional check | |
| `match?(regex)` | Regex match | |
| `slice(start, len)` | Substring extraction | |
| `reverse` | Invert string | |
| `to_i` / `to_f` | Type conversion | |
| `to_currency` | Format as currency | `"345.6".to_currency` → `"$345.60"` |
| `to_phone` | Format phone number | |

### 6.2 Number Formulas

| Formula | Description | Example |
|---|---|---|
| `abs` | Absolute value | `-5.abs` → `5` |
| `round(n)` | Round to n decimals | `1.567.round(2)` → `1.57` |
| `ceil` / `floor` | Round up/down | `1.2.ceil` → `2` |
| `even?` / `odd?` | Parity check | |
| `to_s` / `to_f` / `to_i` | Type conversions | |
| `**` | Exponent | `5**3` → `125` |
| `%` | Modulo | `7 % 4` → `3` |

> Integer division truncates: `7 / 4` → `1`. Use `7 / 4.0` → `1.75`.

### 6.3 Date / DateTime Formulas

| Formula | Description |
|---|---|
| `now` | Current timestamp (US Pacific) |
| `today` | Current date (no time component) |
| `2.days.from_now` | Future relative time |
| `3.days.ago` | Past relative time |
| `date + 2.months` | Date arithmetic |
| `in_time_zone("America/New_York")` | Timezone conversion (IANA names) |
| `strftime("%Y-%m-%d %H:%M")` | Custom format output |
| `to_date(format: "MM/DD/YYYY")` | Parse date string |
| `to_time` | Convert to UTC timestamp |
| `to_i` | Convert to Unix epoch seconds |
| `beginning_of_day` / `end_of_month` | Boundary functions |
| `wday` | Day of week (0=Sunday) |
| `dst?` | Daylight Saving Time check |

### 6.4 Array / List Formulas

| Formula | Description | Example |
|---|---|---|
| `first` / `last` | Access elements | `list.first` |
| `list[0]` | Zero-based index | |
| `length` / `size` | Count | |
| `pluck("field")` | Extract single column | `list.pluck("id")` |
| `where("field == value")` | Filter | |
| `join(", ")` | Array → string | |
| `flatten` | Multi-dim → 1D | |
| `compact` | Remove nil values | |
| `uniq` | Remove duplicates | |
| `concat(other_list)` | Merge two lists | |
| `include?(val)` | Membership check | |
| `blank?` / `present?` | Empty check | |
| `to_json` | Serialise to JSON string | |
| `to_csv` | Serialise to CSV string | |

---

## 7. Handle Errors — Full Implementation Guide

> Source: https://docs.workato.com/en/recipes/monitor-errors-recipeops

### 7.1 Inline Error Handling (per-recipe)

Use `monitor` + `rescue` keywords inside the recipe block (see §4.3).

**Flow**:
1. Workato executes all steps inside the `monitor` block.
2. If ALL steps succeed → `rescue` block is skipped.
3. If ANY step fails → execution jumps to `rescue` block.
4. Configure retries on the rescue block in the Workato GUI (N attempts, interval).

### 7.2 Workspace-Level Error Monitoring (RecipeOps)

Use a separate monitoring recipe with RecipeOps triggers:

**Job Failed Trigger** — fires when a monitored recipe job fails:
```
provider: "recipeops", name: "job_failed"
config scope: all recipes | specific recipe IDs | tagged recipes
outputs: error_type, error_message, app, action, step, timestamps, job_id, recipe_id
filter: by error_type, by errored_app, by recipe_id
```

**Recipe Stopped Trigger** — fires when Workato auto-stops a recipe (e.g. 60 consecutive auth failures):
```
provider: "recipeops", name: "recipe_stopped_by_workato"
outputs: recipe_id, error_type, connector, error_count, auth_flags, rate_limit flags
```

### 7.3 Generator Pattern (generate_workato.py)

Every recipe built by the generator automatically wraps its action steps in a `monitor`/`rescue` block:

```
[0] trigger
  [1] monitor  "Handle errors"
    [2] action  (step 1 from spec)
    [3] action  (step 2 from spec)
    [4] rescue  (empty — add handler steps in GUI)
```

For specs with `try_catch` steps, those emit a nested monitor/rescue inside the outer wrapper:
```
  [1] monitor  "Handle errors"
    [2] monitor  "Safe DB call"
      [3] action  (try-step 1)
      [4] rescue  { [5] action (catch-step) }
    [6] action  (next step)
    [7] rescue  (outer catch-all)
```

---

## 8. Connections (config array)

Connections are referenced in the recipe-level `config` array, not inside step `input`.

```json
[
  {
    "keyword": "application",
    "name": "<provider>",
    "provider": "<provider>",
    "account_id": <connection_id_integer>,
    "skip_validation": false
  }
]
```

Examples:

| Connector | provider | Confirmed account_id |
|---|---|---|
| Oracle | `oracle` | `19661065` (OracleConnection) |
| Oracle | `oracle` | `19657520` (MIG_WM_GLD_Oracle_Connection) |
| HTTP/REST | `rest` | `19669301` (Claude HTTP) |
| PostgreSQL | `postgresql` | `19512394` (MIG_claudecode_PostgreSQL) |
| Salesforce | `salesforce` | `16278922` (My Salesforce account) |
| Google Sheets | `google_sheets` | `16266402` (My Google Sheets account) |

Multiple connections in one recipe: add one entry per provider in the config array.

---

## 9. Complete Recipe JSON Template

```json
{
  "number": 0,
  "keyword": "trigger",
  "provider": "<trigger_provider>",
  "name": "<trigger_name>",
  "as": "<alias>",
  "dynamicPickListSelection": {},
  "toggleCfg": {},
  "input": { ... },
  "uuid": "<uuid>",
  "block": [
    {
      "number": 1,
      "keyword": "monitor",
      "uuid": "<uuid>",
      "title": "Handle errors",
      "block": [
        {
          "number": 2, "keyword": "action",
          "provider": "<app>", "name": "<operation>",
          "as": "<alias>",
          "dynamicPickListSelection": {}, "toggleCfg": {},
          "input": { "field": "value or #{datapill}" },
          "uuid": "<uuid>"
        },
        {
          "number": 3, "keyword": "rescue",
          "uuid": "<uuid>",
          "block": []
        }
      ]
    }
  ]
}
```

**Step numbering rules**:
- Trigger is always `0`.
- Every step has a globally unique number.
- A container step's number is always LOWER than any step inside its `block`.
- Reserve the monitor number BEFORE building inner steps; reserve the rescue number AFTER try-steps but BEFORE catch-steps.

---

## 10. Known API Behaviours (confirmed by live testing)

| Behaviour | Detail |
|---|---|
| `callable_recipe` trigger input hidden | GET API always returns `input: {}` for callable recipe triggers |
| `new_event_via_polling` block hidden | GET API strips `block` from polling trigger when block is added then re-fetched via a PUT that mutated the fetched object — rebuild from scratch instead |
| `trigger_every` stripped | Workato strips `trigger_every` from GET response when it equals the default (5 for minutes) — it is applied at runtime |
| `input_fields_raw_schema` wiped | Any `type:"object"` or `type:"array"` field in the schema wipes the entire trigger input silently |
| `workato_recipe_function` needs `return_result` | Recipe Function recipes must end with a `workato_recipe_function/return_result` action |
| Connection `account_id` integer | Must be integer, not string |
| Control-flow keywords | `if`, `else`, `each`, `monitor`, `rescue` must NOT have `provider`/`name`/`dynamicPickListSelection` |
