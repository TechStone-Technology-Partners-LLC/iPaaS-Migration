# -*- coding: utf-8 -*-
import json, urllib.request, subprocess

result = subprocess.run(['bash', '-c', 'source .env && echo $WORKATO_API_TOKEN'], capture_output=True, text=True)
tok = result.stdout.strip()

recipe_id = 73717572
GSHEET_CONN_ID = 19682603
SPREADSHEET_ID = "1d1875U6UXi_amnzdsRq2vvNeLgwGJM9BM8UWgxrG8eE"

# GET live state (read-before-write rule)
req = urllib.request.Request(f"https://www.workato.com/api/recipes/{recipe_id}",
    headers={"Authorization": f"Bearer {tok}"})
with urllib.request.urlopen(req, timeout=15) as r:
    live = json.loads(r.read())

live_code = json.loads(live.get('code', '{}'))
trigger = {k: v for k, v in live_code.items() if k != 'block'}

# Keep existing UUIDs from live recipe steps
s1_uuid = live_code['block'][0]['uuid']
s2_uuid = live_code['block'][1]['uuid']
s3_uuid = live_code['block'][2]['uuid']

print(f"Existing UUIDs: s1={s1_uuid[:8]}, s2={s2_uuid[:8]}, s3={s3_uuid[:8]}")

# Short as-aliases
S1_AS = "a1step1g"
S2_AS = "b2step2v"
S3_AS = "c3step3i"

list_schema_props = [
    {"control_type": "text", "label": "firsName", "name": "firsName", "type": "string", "optional": False},
    {"control_type": "text", "label": "lastName", "name": "lastName", "type": "string", "optional": False},
    {"control_type": "text", "label": "email",    "name": "email",    "type": "string", "optional": False},
    {"control_type": "text", "label": "phone",    "name": "phone",    "type": "string", "optional": False},
]

# STEP 1: google_sheets / get_spreadsheet_rows_v4
step1 = {
    "number": 1,
    "provider": "google_sheets",
    "name": "get_spreadsheet_rows_v4",
    "as": S1_AS,
    "keyword": "action",
    "dynamicPickListSelection": {"spreadsheet": "Sample_Claude"},
    "toggleCfg": {},
    "input": {
        "team_drives": "my_drive",
        "spreadsheet": SPREADSHEET_ID,
        "sheet": "Sheet1",
        "range": "2:5"
    },
    "extended_output_schema": [
        {"control_type": "text", "label": "Spreadsheet ID",   "name": "spreadsheet_id",   "type": "string"},
        {"control_type": "text", "label": "Spreadsheet name", "name": "spreadsheet_name", "type": "string"},
        {"control_type": "text", "label": "Sheet name",       "name": "sheet",            "type": "string"},
        {
            "label": "Rows", "name": "rows", "of": "object", "type": "array",
            "properties": [
                {"control_type": "number", "label": "Row number",   "parse_output": "integer_conversion", "type": "integer", "name": "row_number"},
                {"control_type": "text",   "label": "To_Email",    "old_name": "col_To_Email",    "custom_attribute": 1, "type": "string", "name": "col_To_Email"},
                {"control_type": "text",   "label": "Description", "old_name": "col_Description", "custom_attribute": 2, "type": "string", "name": "col_Description"},
            ]
        }
    ],
    "extended_input_schema": [
        {
            "control_type": "select", "extends_schema": True,
            "label": "Sheet", "name": "sheet", "optional": False,
            "pick_list": [["Sheet1", "Sheet1"]],
            "toggle_field": {
                "control_type": "text", "label": "Sheet name", "name": "sheet_name",
                "type": "string", "extends_schema": True
            },
            "type": "string"
        },
        {"control_type": "text", "label": "Range", "name": "range", "optional": True, "sticky": True, "type": "string"}
    ],
    "uuid": s1_uuid
}

# STEP 2: workato_variable / declare_list
step2 = {
    "number": 2,
    "provider": "workato_variable",
    "name": "declare_list",
    "as": S2_AS,
    "keyword": "action",
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "name": "Transform1",
        "list_item_schema_json": json.dumps([
            {"name": "firsName", "type": "string", "optional": False, "label": "firsName", "control_type": "text"},
            {"name": "lastName", "type": "string", "optional": False, "label": "lastName", "control_type": "text"},
            {"name": "email",    "type": "string", "optional": False, "label": "email",    "control_type": "text"},
            {"name": "phone",    "type": "string", "optional": False, "label": "phone",    "control_type": "text"},
        ])
    },
    "extended_output_schema": [
        {
            "hint": "", "label": "Transform1", "name": "list_items",
            "of": "object", "optional": False, "type": "array",
            "properties": list_schema_props
        }
    ],
    "extended_input_schema": [
        {
            "hint": "Set the initial items in the list. Defaults to an empty list if not supplied.",
            "label": "Items", "name": "list_items", "of": "object", "optional": True,
            "properties": list_schema_props, "type": "array"
        }
    ],
    "uuid": s2_uuid
}

# STEP 3: workato_variable / insert_to_list_batch
# List reference = "{s2_uuid}:{S2_AS}" — confirmed from test.recipe.json
list_ref = f"{s2_uuid}:{S2_AS}"

def dp(provider, line, path):
    pill = json.dumps(
        {"pill_type": "output", "provider": provider, "line": line, "path": path},
        separators=(',', ':')
    )
    # Workato data pill format: #{_dp('...')}
    escaped = pill.replace('"', '\\"')
    return '#{_dp("' + escaped + '")}'

step3 = {
    "number": 3,
    "provider": "workato_variable",
    "name": "insert_to_list_batch",
    "as": S3_AS,
    "keyword": "action",
    "dynamicPickListSelection": {"name": "Transform1 (step 3)"},
    "toggleCfg": {},
    "input": {
        "location": "end",
        "name": list_ref,
        "list_items": {
            "____source": dp("google_sheets", S1_AS, ["rows"]),
            "firsName":   dp("google_sheets", S1_AS, ["rows", {"path_element_type": "current_item"}, "col_To_Email"]),
            "lastName":   dp("google_sheets", S1_AS, ["rows", {"path_element_type": "current_item"}, "col_Description"]),
        }
    },
    "extended_input_schema": [
        {
            "hint": "", "label": "List items", "name": "list_items",
            "of": "object", "optional": False, "type": "array",
            "properties": list_schema_props
        }
    ],
    "uuid": s3_uuid
}

trigger["block"] = [step1, step2, step3]

config = [
    {"keyword": "application", "name": "google_sheets", "provider": "google_sheets",
     "account_id": GSHEET_CONN_ID, "skip_validation": False},
    {"keyword": "application", "provider": "workato_variable", "skip_validation": False, "account_id": None}
]

payload = json.dumps({
    "recipe": {
        "code":   json.dumps(trigger),
        "config": json.dumps(config)
    }
}).encode()

req2 = urllib.request.Request(f"https://www.workato.com/api/recipes/{recipe_id}",
    data=payload, method="PUT",
    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req2, timeout=15) as r2:
        resp = json.loads(r2.read())
    print(f"PUT: {resp}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")
    raise

# Verify
req3 = urllib.request.Request(f"https://www.workato.com/api/recipes/{recipe_id}",
    headers={"Authorization": f"Bearer {tok}"})
with urllib.request.urlopen(req3, timeout=15) as r3:
    check = json.loads(r3.read())

check_code = json.loads(check.get('code', '{}'))
print("\n=== Verification ===")
for s in check_code.get('block', []):
    inp = s.get('input', {})
    eos = s.get('extended_output_schema', [])
    print(f"  [{s['number']}] {s.get('provider','')}/{s.get('name','')}  as={s.get('as','')}")
    print(f"       input keys: {list(inp.keys())}")
    print(f"       extended_output_schema: {bool(eos)}")
    if inp:
        for k, v in list(inp.items())[:4]:
            print(f"         {k}: {str(v)[:60]}")
