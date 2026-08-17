#!/usr/bin/env python3
"""
Push script: Funding Engine Test1
Source: WebMethods/GLDFundingEngine20080714 (processFundingRequest flow)
Skill:  Workato/Companion/SKILL.md (workato-integration) — all 15 rules

RecipeComponent JSON references used for each step:
  Trigger   → Workato/RecipeComponents/WorkatoServiceTrigger.json
  try/catch → Workato/RecipeComponents/oracle.json
  foreach   → Workato/RecipeComponents/forEach.json
  if/else   → Workato/RecipeComponents/oracle.json (if/elsif/else examples)
  HTTP      → Workato/RecipeComponents/HTTP.json (rest/make_request_v2 pattern)
  Oracle SP → Workato/RecipeComponents/oracle.json
  Logger    → Workato/RecipeComponents/Log.json
  send_reply→ Workato/RecipeComponents/WorkatoServiceSendReply.json

Key corrections applied from reading the reference JSONs (vs previous push scripts):
  - logger name: "log_message" (Log.json), NOT "create_message"
  - else step:   has "input": {} (oracle.json)
  - catch step:  has "as" alias (oracle.json)
  - forEach:     keyword="foreach", repeat_mode="simple", clear_scope="false" (forEach.json)
  - dynamicPickListSelection: {} on every action step (SKILL.md Rule 3)
  - send_reply toggleCfg key: "reply.<field_name>": True (WorkatoServiceSendReply.json)

Recipe structure:
  TRIGGER (workato_service/receive_request)
    [1] try
      [2] foreach payment in payments.parse_json → payment_loop
        [3] if type == "Check"
          [4] HTTP POST invokeGetUniquePayee → get_payee
          [5] if payeeKey is_empty
            [6] HTTP POST invokeAddNewPayee → add_payee
          [7] HTTP POST invokeCreateCheckRequest → create_check
        [8] elsif type == "ACH"
          [9] Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT → oracle_ach
        [10] else (Default/Wire/Other)
          [11] logger log_message → log_default
        [12] rescue (LAST — Rule 5)
          [13] logger log_message → log_rescue  (wire error.message pill in GUI)
      [14] workato_service/send_reply → send_reply_ok (PAYMENTS_PROCESSED)
      [15] catch (LAST — Rule 6)
        [16] logger log_message → log_catch  (wire error.message pill in GUI)

Placeholders for manual GUI wiring after push:
  - GLDFundingEngine_CheckWriter_Connection: base URL from SME → wire to steps 4, 6, 7
  - MIG_WM_GLD_Oracle_Connection (ID 19657520): wire to step 9 (Oracle SP)
  - error.message datapill: wire in steps 13 and 16 in GUI
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
RECIPE_NAME     = "Funding Engine Test1"
PARENT_FOLDER_ID = 31835141          # migrAIte_Training — fallback if new folder fails
NEW_FOLDER_NAME = "FundingEngineTest1"
ORACLE_CONN_ID  = 19657520           # MIG_WM_GLD_Oracle_Connection
DRY_RUN         = "--dry-run" in sys.argv

# Placeholder URLs — replace with real SME-provided base URLs
CHECKWRITER_BASE = "https://webmethods-gateway.keybank.internal/GLDExpressGateway/CheckWriter"
MESSAGELOG_BASE  = "https://webmethods-log.keybank.internal/GLDMessageLog"

# ── Auth ──────────────────────────────────────────────────────────────────────
def load_env():
    p = Path(__file__).resolve().parent
    for _ in range(6):
        c = p / ".env"
        if c.exists():
            for line in c.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return
        p = p.parent

load_env()
TOKEN = os.environ.get("WORKATO_API_TOKEN", "")
if not TOKEN:
    sys.exit("ERROR: WORKATO_API_TOKEN not found in .env")

BASE = "https://www.workato.com/api"   # hardcoded — never use WORKATO_BASE_URL env var

def api(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type",  "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {e.read().decode(errors='replace')[:400]}")

# ── Folder creation (with graceful fallback if IP-whitelisted) ─────────────
def resolve_folder_id():
    """Try to create new folder; fall back to parent if API is whitelisted."""
    if DRY_RUN:
        print(f"[DRY RUN] Would create folder '{NEW_FOLDER_NAME}' under {PARENT_FOLDER_ID}")
        return str(PARENT_FOLDER_ID)
    try:
        # Rule 8: POST /folders uses flat JSON (no wrapper)
        result = api("POST", "/folders", {"name": NEW_FOLDER_NAME, "parent_id": PARENT_FOLDER_ID})
        fid = result.get("id") or result.get("folder_id")
        print(f"Created folder '{NEW_FOLDER_NAME}' (id={fid})")
        return str(fid)
    except RuntimeError as e:
        if "401" in str(e) or "403" in str(e) or "whitelisted" in str(e).lower():
            print(f"[WARN] Folder creation blocked (IP whitelist) — pushing to parent folder {PARENT_FOLDER_ID}")
            print(f"       Create folder '{NEW_FOLDER_NAME}' manually in Workato GUI, then update FOLDER_ID.")
        else:
            print(f"[WARN] Folder creation failed ({e}) — using parent folder {PARENT_FOLDER_ID}")
        return str(PARENT_FOLDER_ID)

# ── Helpers ───────────────────────────────────────────────────────────────────
def uid():
    return str(uuid.uuid4())

# Step aliases (short codes matching RecipeComponent reference style)
TRIG_AS     = "fe_trig"
LOOP_AS     = "payment_loop"
GET_PAYEE   = "get_payee"
ADD_PAYEE   = "add_payee"
CRT_CHECK   = "create_check"
ORC_ACH     = "oracle_ach"
LOG_DEF     = "log_default"
LOG_RSC     = "log_rescue"
LOG_CAT     = "log_catch"
CATCH_AS    = "outer_catch"
REPLY_AS    = "send_reply_ok"

# ── Datapill helpers ──────────────────────────────────────────────────────────
def _dp_json(provider, line, *path_parts):
    """Build datapill JSON object (not yet stringified)."""
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    return {"pill_type": "output", "provider": provider, "line": line, "path": path}

def dp(provider, line, *path_parts):
    """Return interpolated datapill string: #{_dp('...')}"""
    obj = json.dumps(_dp_json(provider, line, *path_parts)).replace('"', '\\"')
    return "#{_dp('" + obj + "')}"

def raw_dp(provider, line, *path_parts):
    """Return raw _dp('...') expression (for compound formulas)."""
    obj = json.dumps(_dp_json(provider, line, *path_parts)).replace('"', '\\"')
    return "_dp('" + obj + "')"

# Shorthand datapill functions
def trig(field):
    """Trigger input field datapill."""
    return dp("workato_service", TRIG_AS, "request", field)

def pay(field):
    """
    Loop item datapill (payment.field).
    Rule 12 + control_if_else.md: provider="workato_service", path=[{"path_element_type":"current_item"}, field]
    """
    return dp("workato_service", LOOP_AS, "*", field)

def http_resp(step_as, *fields):
    """HTTP step response datapill."""
    return dp("http", step_as, *fields)

# ── PayeeInformation (Section 5.2 — Check path fields) ───────────────────────
# Mapped from PackageAnalysis.md §5.2
PAYEE_INFO = {
    "PayeeName":          pay("payee.name"),
    "AddressLine1":       pay("payee.address1"),
    "AddressLine2":       pay("payee.address2"),
    "City":               pay("payee.city"),
    "State":              pay("payee.state_province"),
    "PostalCode":         pay("payee.zip"),
    "PhoneNumber":        pay("payee.phone"),
    "FaxNumber":          pay("payee.fax"),
    "ContactName":        pay("payee.contactName"),
    "ContactPhoneNumber": pay("payee.contactPhone"),
    "Country":            "USA",
}

# ═══════════════════════════════════════════════════════════════════════════════
# STEP BUILDERS — each follows its canonical RecipeComponent JSON reference
# ═══════════════════════════════════════════════════════════════════════════════

def make_http_post(num, alias, url, payload_dict, title=None):
    """
    HTTP POST step.
    Reference: Workato/RecipeComponents/HTTP.json (rest/make_request_v2 pattern)
    Using http/post (direct URL, no stored connection) for placeholder URLs.
    Rules: toggleCfg + dynamicPickListSelection on all action steps.
    """
    s = {
        "number":  num,
        "keyword": "action",
        "provider": "http",
        "name":    "post",
        "as":      alias,
        "uuid":    uid(),
        "dynamicPickListSelection": {},   # Rule 3
        "toggleCfg":               {},   # Rule 2
        "input": {
            "url":          url,
            "content_type": "application/json",
            "payload":      json.dumps(payload_dict),
        },
    }
    if title:
        s["title"] = title
    return s

def make_oracle_sp(num, alias, proc_name, params, title=None):
    """
    Oracle execute_stored_procedure step.
    Reference: Workato/RecipeComponents/oracle.json
    dynamicPickListSelection selects the SP; toggleCfg marks the pick-list toggle field.
    """
    inp = {"procedure_name": proc_name}
    inp.update(params)
    s = {
        "number":  num,
        "keyword": "action",
        "provider": "oracle",
        "name":    "execute_stored_procedure",
        "as":      alias,
        "uuid":    uid(),
        "dynamicPickListSelection": {"procedure_name": proc_name},  # Rule 3
        "toggleCfg": {"procedure_name": True},                      # matches oracle.json pattern
        "input":   inp,
    }
    if title:
        s["title"] = title
    return s

def make_logger(num, alias, message, title=None):
    """
    Logger step.
    Reference: Workato/RecipeComponents/Log.json
    CORRECTED: name="log_message" (NOT "create_message" — Log.json is authoritative)
    """
    s = {
        "number":  num,
        "keyword": "action",
        "provider": "logger",
        "name":    "log_message",   # Log.json reference — was "create_message" in older scripts
        "as":      alias,
        "uuid":    uid(),
        "dynamicPickListSelection": {},   # Rule 3
        "toggleCfg":               {},   # Rule 2
        "input": {
            "message": message,
        },
    }
    if title:
        s["title"] = title
    return s

# ═══════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS — consecutive numbering 0..16
# ═══════════════════════════════════════════════════════════════════════════════

# [4] HTTP invokeGetUniquePayee
step4_get_payee = make_http_post(
    4, GET_PAYEE,
    CHECKWRITER_BASE + "/invokeGetUniquePayee",
    PAYEE_INFO,
    title="Check invokeGetUniquePayee",
)

# [6] HTTP invokeAddNewPayee (inside nested if payeeKey empty)
step6_add_payee = make_http_post(
    6, ADD_PAYEE,
    CHECKWRITER_BASE + "/invokeAddNewPayee",
    PAYEE_INFO,
    title="Check invokeAddNewPayee (payee not found)",
)

# [5] if payeeKey is_empty → addNewPayee
# Reference: oracle.json (if/condition pattern)
step5_if_payeekey = {
    "number": 5,
    "keyword": "if",
    "uuid":   uid(),
    "input": {
        "type":    "compound",
        "operand": "and",
        "conditions": [{
            "operand": "is_empty",
            "lhs":     http_resp(GET_PAYEE, "payeeKey"),
            "uuid":    uid(),
        }],
    },
    "block": [step6_add_payee],
}

# PayeeKey: use getPayee result, fall back to addPayee result
PAYEEKEY = (
    "#{" + raw_dp("http", GET_PAYEE, "payeeKey") +
    ".presence || " + raw_dp("http", ADD_PAYEE, "payeeKey") + "}"
)

# [7] HTTP invokeCreateCheckRequest (Section 5.2 complete mapping)
step7_create_check = make_http_post(
    7, CRT_CHECK,
    CHECKWRITER_BASE + "/invokeCreateCheckRequest",
    {
        "PayeeKey":    PAYEEKEY,
        "Notes":       pay("invoiceReference"),
        "Comments":    pay("comment"),
        "CheckAmount": pay("amount"),
        "Memo":        pay("checkMemo"),
        "PayeeName":   pay("payee.name"),
        "LeaseNumber": trig("id"),
    },
    title="Check invokeCreateCheckRequest",
)

# [3] if type == "Check"
# Reference: oracle.json (if/condition pattern with "equals" operand)
step3_if_check = {
    "number": 3,
    "keyword": "if",
    "uuid":   uid(),
    "input": {
        "type":    "compound",
        "operand": "and",
        "conditions": [{
            "operand": "equals",
            "lhs":     pay("type"),
            "rhs":     "Check",
            "uuid":    uid(),
        }],
    },
    "block": [step4_get_payee, step5_if_payeekey, step7_create_check],
}

# [9] Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT (Section 5.3 mapping)
# Reference: Workato/RecipeComponents/oracle.json
step9_oracle_sp = make_oracle_sp(
    9, ORC_ACH,
    "GLD_ACH.INSERTPAYMENT",
    {
        "REQUESTOR_ID":   "1",                    # static constant (Section 6, Rule 4)
        "APP_ID":         trig("id"),
        "CUSTOMER_NAME":  trig("customerName"),
        "CUSTOMER_ID":    trig("customerID"),
        "SOURCE":         trig("sourceName"),
        "AMOUNT":         pay("amount"),
        "REFERENCE":      pay("invoiceReference"),
        "PAYEE_ID":       pay("payee.id"),
        "PAYEE_NAME":     pay("payee.name"),
        "ACCOUNT_NUMBER": pay("payee.accountNumber"),
        "ROUTING_NUMBER": pay("payee.routingNumber"),
    },
    title="ACH Oracle GLD_ACH.INSERTPAYMENT (11 params)",
)

# [8] elsif type == "ACH"
# Rule 7: flat sibling — NOT nested inside else
step8_elsif_ach = {
    "number": 8,
    "keyword": "elsif",    # Rule 7
    "uuid":   uid(),
    "input": {
        "type":    "compound",
        "operand": "and",
        "conditions": [{
            "operand": "equals",
            "lhs":     pay("type"),
            "rhs":     "ACH",
            "uuid":    uid(),
        }],
    },
    "block": [step9_oracle_sp],
}

# [11] logger — Default path
# Reference: Log.json (name="log_message")
step11_log_default = make_logger(
    11, LOG_DEF,
    "Default payment path — type=" + pay("type"),
    title="Default path (Wire/Other — no external call)",
)

# [10] else — Default/Wire/Other
# Reference: oracle.json — else has "input": {} (not omitted)
step10_else = {
    "number":  10,
    "keyword": "else",
    "uuid":    uid(),
    "input":   {},     # oracle.json reference shows else carries input: {}
    "block":   [step11_log_default],
}

# [13] logger inside rescue
# Reference: Log.json
step13_log_rescue = make_logger(
    13, LOG_RSC,
    "Payment error — wire error.message pill in GUI",
    title="Per-payment rescue (wire error.message datapill in GUI)",
)

# [12] rescue — LAST in foreach.block (Rule 5)
# Reference: control_try_catch.md — no input, no provider, no as
step12_rescue = {
    "number":  12,
    "keyword": "rescue",
    "uuid":    uid(),
    "block":   [step13_log_rescue],
}

# [2] foreach — payment_loop
# Reference: Workato/RecipeComponents/forEach.json (canonical)
# Fields: keyword="foreach", repeat_mode="simple", clear_scope="false", as, input.source, uuid, block
_pay_pill = json.dumps(
    _dp_json("workato_service", TRIG_AS, "request", "payments")
).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill + "').parse_json}"

step2_foreach = {
    "number":      2,
    "keyword":     "foreach",        # forEach.json canonical keyword
    "as":          LOOP_AS,
    "repeat_mode": "simple",         # forEach.json required field
    "clear_scope": "false",          # forEach.json required field
    "uuid":        uid(),
    "input":       {"source": PAYMENTS_SOURCE},
    "block": [
        step3_if_check,    # if Check
        step8_elsif_ach,   # elsif ACH   (Rule 7 — flat sibling)
        step10_else,       # else Default
        step12_rescue,     # LAST (Rule 5)
    ],
}

# [14] send_reply — PAYMENTS_PROCESSED
# Reference: Workato/RecipeComponents/WorkatoServiceSendReply.json
# toggleCfg key = "reply.<field_name>": True per WorkatoServiceSendReply.json
step14_send_reply = {
    "number":   14,
    "keyword":  "action",
    "provider": "workato_service",
    "name":     "send_reply",
    "as":       REPLY_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},              # Rule 3
    "toggleCfg": {"reply.status": True},        # WorkatoServiceSendReply.json pattern
    "input": {
        "reply_type": "success",
        "reply": {"status": "PAYMENTS_PROCESSED"},
    },
    "extended_input_schema": [{
        "label": "Reply",
        "name":  "reply",
        "type":  "object",
        "properties": [{
            "control_type": "text",
            "label":        "Status",
            "name":         "status",
            "type":         "string",
            "optional":     False,
        }],
    }],
}

# [16] logger inside catch
# Reference: Log.json
step16_log_catch = make_logger(
    16, LOG_CAT,
    "Outer error — wire error.message pill in GUI",
    title="Outer catch (wire error.message datapill in GUI)",
)

# [15] catch — LAST in try.block (Rule 6)
# Reference: oracle.json — catch carries "as" alias + "input" with retry config
step15_catch = {
    "number":  15,
    "keyword": "catch",
    "as":      CATCH_AS,    # oracle.json reference shows catch has "as"
    "uuid":    uid(),
    "input":   {"max_retry_count": "0", "retry_interval": "2"},
    "block":   [step16_log_catch],
}

# [1] try — Rule 6: catch LAST; send_reply before catch
# Reference: oracle.json (try/catch wrapper pattern)
step1_try = {
    "number":  1,
    "keyword": "try",
    "uuid":    uid(),
    "input":   {},     # oracle.json: try always has input: {}
    "block": [
        step2_foreach,    # foreach loop
        step14_send_reply,  # send_reply inside try, before catch
        step15_catch,     # LAST (Rule 6)
    ],
}

# ── Trigger (WorkatoServiceTrigger.json) ──────────────────────────────────────
# Fields from reference: number=0, provider, name, as (short alias), keyword="trigger",
# input: { service_name, request_schema_json, reply_schema_json },
# extended_output_schema, parameters_schema="", block, uuid
request_schema = [
    {"name": "id",                "type": "string", "optional": False,
     "control_type": "text", "label": "Application ID"},
    {"name": "customerName",      "type": "string", "optional": False,
     "control_type": "text", "label": "Customer Name"},
    {"name": "customerID",        "type": "string", "optional": False,
     "control_type": "text", "label": "Customer ID"},
    {"name": "sourceName",        "type": "string", "optional": True,
     "control_type": "text", "label": "Source Name"},
    {"name": "sourceSubCategory", "type": "string", "optional": True,
     "control_type": "text", "label": "Source Sub Category"},
    {"name": "salesRepName",      "type": "string", "optional": True,
     "control_type": "text", "label": "Sales Rep Name"},
    {"name": "payments",          "type": "string", "optional": False,
     "control_type": "text",
     "label": "Payments (JSON array string) — Rule 1: flattened to avoid schema wipe"},
]

reply_schema = [
    {"name": "status", "type": "string", "optional": False,
     "control_type": "text", "label": "Processing Status"},
]

# extended_output_schema: WorkatoServiceTrigger.json wraps fields under "request" object
# Rule 15: must match request_schema_json field names
trigger = {
    "number":   0,
    "provider": "workato_service",
    "name":     "receive_request",
    "as":       TRIG_AS,             # short alias per WorkatoServiceTrigger.json style
    "keyword":  "trigger",
    "uuid":     uid(),
    "dynamicPickListSelection": {},   # Rule 3
    "toggleCfg":               {},   # Rule 2
    "parameters_schema":       "",   # Rule 4 — required on callable triggers
    "input": {
        "service_name":        RECIPE_NAME,
        "request_schema_json": json.dumps(request_schema),
        "reply_schema_json":   json.dumps(reply_schema),
    },
    # Rule 15: extended_output_schema wraps under "request" to match WorkatoServiceTrigger.json
    "extended_output_schema": [{
        "label":      "Recipe input",
        "name":       "request",
        "type":       "object",
        "properties": [
            {"name": f["name"], "type": f["type"],
             "label": f["label"], "control_type": f["control_type"]}
            for f in request_schema
        ],
    }],
    "block": [step1_try],
}

# ── Config (Rule 13: account_id is integer or null, never string) ─────────────
config = [
    # WorkatoServiceTrigger.json + WorkatoServiceSendReply.json
    {"keyword": "application", "provider": "workato_service",
     "account_id": None,            "skip_validation": False},
    # HTTP.json — http/post (direct URL, no stored connection)
    {"keyword": "application", "provider": "http",
     "account_id": None,            "skip_validation": False},
    # oracle.json — MIG_WM_GLD_Oracle_Connection
    {"keyword": "application", "provider": "oracle",
     "account_id": ORACLE_CONN_ID,  "skip_validation": False},
    # Log.json — logger (account_id: null in Log.json reference)
    {"keyword": "application", "provider": "logger",
     "account_id": None,            "skip_validation": False},
]

# ── Structure validation ──────────────────────────────────────────────────────
def validate():
    try_blk     = trigger["block"][0]["block"]
    foreach_blk = try_blk[0]["block"]

    assert trigger["block"][0]["keyword"] == "try",          "Step 1 must be try"
    assert try_blk[0]["keyword"]  == "foreach",              "Step 2 must be foreach (forEach.json)"
    assert try_blk[0].get("repeat_mode") == "simple",        "repeat_mode missing"
    assert try_blk[0].get("clear_scope") == "false",         "clear_scope missing"
    assert try_blk[-1]["keyword"] == "catch",                 "catch must be LAST in try.block (Rule 6)"
    assert foreach_blk[-1]["keyword"] == "rescue",            "rescue must be LAST in foreach.block (Rule 5)"
    assert foreach_blk[1]["keyword"] == "elsif",              "step 8 must be elsif flat sibling (Rule 7)"
    assert foreach_blk[2].get("input") == {},                 "else must have input: {} (oracle.json ref)"
    assert trigger["block"][0].get("as") == CATCH_AS or "as" in try_blk[-1], "catch must have 'as'"

    # Logger name check (Log.json ref)
    for s in [step11_log_default, step13_log_rescue, step16_log_catch]:
        assert s["name"] == "log_message", f"Logger step {s['number']} must use log_message (Log.json)"

    # dynamicPickListSelection check on all action steps
    actions = [step4_get_payee, step6_add_payee, step7_create_check,
               step9_oracle_sp, step11_log_default, step13_log_rescue,
               step14_send_reply, step16_log_catch]
    for s in actions:
        assert "dynamicPickListSelection" in s, f"Missing dynamicPickListSelection on step {s['number']}"

    print("Structure validation PASSED:")
    print(f"  try.block     : {[s['keyword'] for s in try_blk]}")
    print(f"  foreach.block : {[s['keyword'] for s in foreach_blk]}")
    print(f"  foreach mode  : {try_blk[0].get('repeat_mode')} / clear_scope={try_blk[0].get('clear_scope')}")
    print("  else.input    : {} (oracle.json ref)")
    print(f"  catch.as      : {try_blk[-1].get('as')}")
    print(f"  logger name   : log_message (Log.json ref)")
    print(f"  dynamicPL     : present on all {len(actions)} action steps")
    print()

validate()

# ── Payload (Rule 9: code + config as JSON strings) ───────────────────────────
def build_payload(folder_id):
    return {
        "recipe": {
            "name":      RECIPE_NAME,
            "folder_id": str(folder_id),       # Rule 9: string for create
            "code":      json.dumps(trigger),  # Rule 9: JSON string, not dict
            "config":    json.dumps(config),   # Rule 9: JSON string, not list
        }
    }

# ── Main ──────────────────────────────────────────────────────────────────────
if DRY_RUN:
    payload = build_payload(PARENT_FOLDER_ID)
    display = dict(payload["recipe"])
    display["code"]   = json.loads(display["code"])
    display["config"] = json.loads(display["config"])
    print("\n=== DRY RUN ===")
    print(json.dumps({"recipe": display}, indent=2)[:4000], "...")
else:
    folder_id = resolve_folder_id()
    payload   = build_payload(folder_id)

    print(f"\nCreating recipe '{RECIPE_NAME}' in folder {folder_id}...")
    try:
        result = api("POST", "/recipes", payload)
        rid = result.get("id") or result.get("recipe", {}).get("id")
        print()
        print("SUCCESS")
        print(f"  Recipe ID  : {rid}")
        print(f"  Folder ID  : {folder_id}")
        print(f"  URL        : https://app.workato.com/recipes/{rid}")
        print()
        print("Remaining GUI steps:")
        print("  1. Open recipe and verify all steps render correctly")
        print("  2. Create HTTP connection 'GLDFundingEngine_CheckWriter_Connection'")
        print(f"     Base URL: {CHECKWRITER_BASE}  <- replace with real URL from SME")
        print("     Wire to: steps 4 (getUniquePayee), 6 (addNewPayee), 7 (createCheckRequest)")
        print(f"  3. Wire Oracle connection MIG_WM_GLD_Oracle_Connection (ID {ORACLE_CONN_ID})")
        print("     to step 9 (Oracle GLD_ACH.INSERTPAYMENT SP)")
        print("     Confirm exact SP name 'GLD_ACH.INSERTPAYMENT' with SME")
        print("  4. Wire error.message datapill in step 13 (rescue logger) and step 16 (catch logger)")
        print(f"  5. If folder was created as migrAIte_Training fallback, move recipe")
        print(f"     to '{NEW_FOLDER_NAME}' folder in Workato GUI")
    except RuntimeError as e:
        sys.exit(f"Push failed: {e}")
