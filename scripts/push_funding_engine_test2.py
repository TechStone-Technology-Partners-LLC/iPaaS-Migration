#!/usr/bin/env python3
"""
Push script: Funding Engine Test2
Source:  WebMethods/GLDFundingEngine20080714 (processFundingRequest flow)
Skill:   Workato/Companion/SKILL.md (workato-integration) — all 15 rules applied
Folder:  FundingEngineTest2 (new, parent: migrAIte_Training 31835141)
Account: manish@techstonellc.com

RecipeComponent JSON references used for each step:
  Trigger    → Workato/RecipeComponents/WorkatoServiceTrigger.json
  try/catch  → Workato/RecipeComponents/oracle.json
  foreach    → Workato/RecipeComponents/forEach.json   ← CANONICAL (key correction vs Test1)
  if/else    → Workato/RecipeComponents/oracle.json (if/elsif/else examples)
  HTTP       → Workato/RecipeComponents/HTTP.json (http/post inline URL)
  Oracle SP  → Workato/RecipeComponents/oracle.json
  Logger     → Workato/RecipeComponents/Log.json
  send_reply → Workato/RecipeComponents/WorkatoServiceSendReply.json

KEY CORRECTION vs Funding Engine Test1:
  forEach.json canonical format shows "source" as TOP-LEVEL field (not inside "input"):
    { "keyword": "foreach", "repeat_mode": "simple", "clear_scope": "false",
      "input": {},          ← empty dict
      "source": "<pill>",   ← TOP-LEVEL, not in input
      "as": "alias", "uuid": "..." }
  Test2 follows this exactly; Test1 incorrectly put source inside input.

SKILL.md Rule Index applied:
  Rule 1  — flat trigger schema (payments as JSON string, not array)
  Rule 2  — toggleCfg: {} on every action step (NOT on control-flow steps)
  Rule 3  — dynamicPickListSelection: {} on every action step
  Rule 4  — parameters_schema: "" on callable trigger
  Rule 5  — rescue LAST in foreach.block
  Rule 6  — catch LAST in try.block
  Rule 7  — keyword "elsif" (flat sibling, not nested)
  Rule 8  — folder POST uses flat JSON body
  Rule 9  — code + config as JSON strings in payload
  Rule 10 — N/A (new recipe, no GET-before-PUT needed)
  Rule 11 — uuid on every step
  Rule 12 — {"path_element_type":"current_item"} for loop item datapills
  Rule 13 — account_id integer or null (never string)
  Rule 14 — "foreach" keyword accepted (canonical per forEach.json)
  Rule 15 — extended_output_schema on trigger

Recipe structure (step tree):
  TRIGGER (workato_service/receive_request "FundingEngine Test2")
    [1] try
      [2] foreach payment in payments.parse_json → payment_loop
          source: TOP-LEVEL (forEach.json canonical)
          input:  {} (empty)
        [3] if type == "Check"
          [4] HTTP POST invokeGetUniquePayee → get_payee
          [5] if payeeKey is_empty
            [6] HTTP POST invokeAddNewPayee → add_payee
          [7] HTTP POST invokeCreateCheckRequest → create_check
        [8] elsif type == "ACH"
          [9] Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT → oracle_ach
        [10] else (Default/Wire/Other)
          [11] logger log_message → log_default
        [12] rescue (LAST in foreach.block — Rule 5)
          [13] logger log_message → log_rescue
      [14] workato_service/send_reply PAYMENTS_PROCESSED → send_reply_ok
      [15] catch (LAST in try.block — Rule 6)
        [16] logger log_message → log_catch

Placeholders requiring manual GUI wiring after push:
  - GLDFundingEngine_CheckWriter_Connection (HTTP): wire to steps 4, 6, 7
    Base URL from SME: CHECKWRITER_BASE (see below)
  - MIG_WM_GLD_Oracle_Connection (ID 19657520): wire to step 9 (Oracle SP)
    Confirm SP name GLD_ACH.INSERTPAYMENT with SME
  - error.message datapill: wire in steps 13 (rescue) and 16 (catch) in GUI
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
RECIPE_NAME      = "Funding Engine Test2"
PARENT_FOLDER_ID = 31835141          # migrAIte_Training — fallback if folder creation fails
NEW_FOLDER_NAME  = "FundingEngineTest2"
ORACLE_CONN_ID   = 19657520          # MIG_WM_GLD_Oracle_Connection (confirmed account_id)
DRY_RUN          = "--dry-run" in sys.argv

# Placeholder URLs — replace with real SME-provided base URLs before go-live
CHECKWRITER_BASE = "https://webmethods-gateway.keybank.internal/GLDExpressGateway/CheckWriter"
MESSAGELOG_BASE  = "https://webmethods-log.keybank.internal/GLDMessageLog"

# ── Auth ──────────────────────────────────────────────────────────────────────
def load_env():
    """Walk ancestor dirs to find .env and load WORKATO_API_TOKEN."""
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
    raise RuntimeError(".env not found in ancestor directories")

load_env()
TOKEN = os.environ.get("WORKATO_API_TOKEN", "")
if not TOKEN:
    sys.exit("ERROR: WORKATO_API_TOKEN not found in .env")

# SKILL.md: hardcode base URL — never trust WORKATO_BASE_URL env var for routing
BASE = "https://www.workato.com/api"

def api(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type",  "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {e.read().decode(errors='replace')[:500]}")

# ── Folder creation (Rule 8 — flat JSON body) ─────────────────────────────────
def resolve_folder_id():
    """Create new folder under migrAIte_Training; fall back gracefully if blocked."""
    if DRY_RUN:
        print(f"[DRY RUN] Would create folder '{NEW_FOLDER_NAME}' under parent {PARENT_FOLDER_ID}")
        return str(PARENT_FOLDER_ID)
    try:
        # Rule 8: POST /folders uses flat JSON — NOT {"folder": {...}}
        result = api("POST", "/folders", {"name": NEW_FOLDER_NAME, "parent_id": PARENT_FOLDER_ID})
        fid = result.get("id") or result.get("folder_id")
        print(f"[OK] Created folder '{NEW_FOLDER_NAME}' (id={fid})")
        return str(fid)
    except RuntimeError as e:
        if "401" in str(e) or "403" in str(e):
            print(f"[WARN] Folder creation blocked (IP whitelist?) — using parent {PARENT_FOLDER_ID}")
            print(f"       Create '{NEW_FOLDER_NAME}' manually in Workato GUI, then move the recipe.")
        else:
            print(f"[WARN] Folder creation failed ({e}) — using parent folder {PARENT_FOLDER_ID}")
        return str(PARENT_FOLDER_ID)

# ── Helpers ───────────────────────────────────────────────────────────────────
def uid():
    """Rule 11: every step needs a unique UUID4."""
    return str(uuid.uuid4())

# Step aliases (short codes — referenced in datapills downstream)
TRIG_AS   = "fe_trig_t2"
LOOP_AS   = "payment_loop"
GET_PAYEE = "get_payee_t2"
ADD_PAYEE = "add_payee_t2"
CRT_CHECK = "create_check_t2"
ORC_ACH   = "oracle_ach_t2"
LOG_DEF   = "log_default_t2"
LOG_RSC   = "log_rescue_t2"
LOG_CAT   = "log_catch_t2"
CATCH_AS  = "outer_catch_t2"
REPLY_AS  = "send_reply_ok_t2"

# ── Datapill helpers (Rule 12 + datapill_guide.md) ───────────────────────────
def _dp_json(provider, line, *path_parts):
    """Build datapill path array. '*' → {"path_element_type": "current_item"} (Rule 12)."""
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    return {"pill_type": "output", "provider": provider, "line": line, "path": path}

def dp(provider, line, *path_parts):
    """Return interpolated datapill string: #{_dp('...')}"""
    obj = json.dumps(_dp_json(provider, line, *path_parts)).replace('"', '\\"')
    return "#{_dp('" + obj + "')}"

def raw_dp(provider, line, *path_parts):
    """Return raw _dp('...') expression — for compound formulas like .presence ||"""
    obj = json.dumps(_dp_json(provider, line, *path_parts)).replace('"', '\\"')
    return "_dp('" + obj + "')"

def trig(field):
    """Trigger field datapill — provider=workato_service, path=[request, field]."""
    return dp("workato_service", TRIG_AS, "request", field)

def pay(field):
    """
    Loop item datapill (current payment field).
    Rule 12: {"path_element_type": "current_item"} for loop item.
    provider="workato_service" per control_if_else.md reference.
    path_parts: ["*", field] → [current_item_marker, field]
    """
    return dp("workato_service", LOOP_AS, "*", field)

def http_resp(step_as, *fields):
    """HTTP step response datapill."""
    return dp("http", step_as, *fields)

# ── Payee information mapping (PackageAnalysis §5.2 — Check path) ─────────────
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
# STEP BUILDERS — each builder documents its RecipeComponent JSON reference
# ═══════════════════════════════════════════════════════════════════════════════

def make_http_post(num, alias, url, payload_dict, title=None):
    """
    HTTP POST action step.
    Reference: Workato/RecipeComponents/HTTP.json
    Using http/post (inline URL, no stored connection) for placeholder base URLs.
    Rules applied: toggleCfg:{} (Rule 2), dynamicPickListSelection:{} (Rule 3), uuid (Rule 11)
    """
    s = {
        "number":   num,
        "keyword":  "action",
        "provider": "http",
        "name":     "post",
        "as":       alias,
        "uuid":     uid(),
        "dynamicPickListSelection": {},    # Rule 3 — required on ALL action steps
        "toggleCfg":               {},    # Rule 2 — required on ALL action steps
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
    Oracle execute_stored_procedure action step.
    Reference: Workato/RecipeComponents/oracle.json
    dynamicPickListSelection selects the procedure; toggleCfg marks it as a toggle field.
    Rules applied: dynamicPickListSelection (Rule 3), toggleCfg (Rule 2), uuid (Rule 11)
    """
    inp = {"procedure_name": proc_name}
    inp.update(params)
    s = {
        "number":   num,
        "keyword":  "action",
        "provider": "oracle",
        "name":     "execute_stored_procedure",
        "as":       alias,
        "uuid":     uid(),
        "dynamicPickListSelection": {"procedure_name": proc_name},  # Rule 3
        "toggleCfg": {"procedure_name": True},                      # oracle.json pattern
        "input":    inp,
    }
    if title:
        s["title"] = title
    return s

def make_logger(num, alias, message, title=None):
    """
    Logger action step.
    Reference: Workato/RecipeComponents/Log.json
    CRITICAL: name="log_message" — NOT "create_message" (Log.json is authoritative)
    Rules applied: dynamicPickListSelection (Rule 3), toggleCfg (Rule 2), uuid (Rule 11)
    """
    s = {
        "number":   num,
        "keyword":  "action",
        "provider": "logger",
        "name":     "log_message",    # Log.json reference — never "create_message"
        "as":       alias,
        "uuid":     uid(),
        "dynamicPickListSelection": {},    # Rule 3
        "toggleCfg":               {},    # Rule 2
        "input": {"message": message},
    }
    if title:
        s["title"] = title
    return s

# ═══════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS — consecutive numbering 0..16
# ═══════════════════════════════════════════════════════════════════════════════

# [4] invokeGetUniquePayee (Check path, step 1 of 3)
step4_get_payee = make_http_post(
    4, GET_PAYEE,
    CHECKWRITER_BASE + "/invokeGetUniquePayee",
    PAYEE_INFO,
    title="Check — invokeGetUniquePayee",
)

# [6] invokeAddNewPayee (inside nested if: payeeKey empty)
step6_add_payee = make_http_post(
    6, ADD_PAYEE,
    CHECKWRITER_BASE + "/invokeAddNewPayee",
    PAYEE_INFO,
    title="Check — invokeAddNewPayee (payee not found)",
)

# [5] if payeeKey is_empty → add new payee
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

# PayeeKey pill: prefer getPayee result, fall back to addPayee result
PAYEEKEY = (
    "#{" + raw_dp("http", GET_PAYEE, "payeeKey") +
    ".presence || " + raw_dp("http", ADD_PAYEE, "payeeKey") + "}"
)

# [7] invokeCreateCheckRequest (Check path, step 3 of 3)
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
    title="Check — invokeCreateCheckRequest",
)

# [3] if type == "Check"
# Reference: oracle.json (if/condition pattern — "equals" operand)
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

# [9] Oracle GLD_ACH.INSERTPAYMENT (ACH path — PackageAnalysis §5.3 mapping)
# Reference: Workato/RecipeComponents/oracle.json
step9_oracle_sp = make_oracle_sp(
    9, ORC_ACH,
    "GLD_ACH.INSERTPAYMENT",
    {
        "REQUESTOR_ID":   "1",                   # static constant per PackageAnalysis §6 Rule 4
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
    title="ACH — Oracle GLD_ACH.INSERTPAYMENT (11 params)",
)

# [8] elsif type == "ACH"
# Rule 7: "elsif" keyword, flat sibling (NOT nested inside else block)
step8_elsif_ach = {
    "number": 8,
    "keyword": "elsif",    # Rule 7 — flat sibling at same level as if/else
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

# [11] Default path logger
# Reference: Workato/RecipeComponents/Log.json → name="log_message"
step11_log_default = make_logger(
    11, LOG_DEF,
    "Default payment path — type=" + pay("type"),
    title="Default path (Wire/Other — no external call)",
)

# [10] else — Default/Wire/Other
# Reference: oracle.json — else MUST carry "input": {} (confirmed from canonical JSON)
step10_else = {
    "number":  10,
    "keyword": "else",
    "uuid":    uid(),
    "input":   {},        # oracle.json shows else carries input:{} — do NOT omit
    "block":   [step11_log_default],
}

# [13] rescue logger — error.message pill must be wired in GUI
# Reference: Workato/RecipeComponents/Log.json
step13_log_rescue = make_logger(
    13, LOG_RSC,
    "Per-payment error — wire error.message datapill in GUI",
    title="Rescue logger (wire error.message in GUI)",
)

# [12] rescue — LAST in foreach.block (Rule 5)
# Reference: control_try_catch.md — no provider, no name, no as, no input, no toggleCfg
step12_rescue = {
    "number":  12,
    "keyword": "rescue",
    "uuid":    uid(),
    "block":   [step13_log_rescue],
}

# ── forEach.json canonical "source" placement ────────────────────────────────
# KEY CORRECTION vs Test1:
#   forEach.json canonical JSON shows "source" as a TOP-LEVEL field of the foreach step,
#   with "input": {} empty. Test1 incorrectly placed source inside "input": {"source": ...}
#
# forEach.json structure:
#   { "keyword": "foreach", "repeat_mode": "simple", "clear_scope": "false",
#     "input": {},          ← always empty
#     "source": "<pill>",   ← TOP-LEVEL sibling of input
#     "as": "alias", "uuid": "..." }

_pay_pill_json = json.dumps(
    _dp_json("workato_service", TRIG_AS, "request", "payments")
).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill_json + "').parse_json}"

# [2] foreach — payment_loop
# Reference: Workato/RecipeComponents/forEach.json (all fields carried exactly)
step2_foreach = {
    "number":      2,
    "keyword":     "foreach",    # Rule 14 — "foreach" accepted (forEach.json canonical)
    "as":          LOOP_AS,
    "repeat_mode": "simple",     # forEach.json required field
    "clear_scope": "false",      # forEach.json required field (string "false", not bool)
    "uuid":        uid(),
    "input":       {},           # forEach.json: input is EMPTY — source is top-level
    "source":      PAYMENTS_SOURCE,  # KEY FIX vs Test1: source at top level per forEach.json
    "block": [
        step3_if_check,    # [3] if Check
        step8_elsif_ach,   # [8] elsif ACH  — flat sibling (Rule 7)
        step10_else,       # [10] else Default
        step12_rescue,     # [12] LAST (Rule 5)
    ],
}

# [14] send_reply — PAYMENTS_PROCESSED
# Reference: Workato/RecipeComponents/WorkatoServiceSendReply.json
# toggleCfg key format: "reply.<field_name>": True (WorkatoServiceSendReply.json)
step14_send_reply = {
    "number":   14,
    "keyword":  "action",
    "provider": "workato_service",
    "name":     "send_reply",
    "as":       REPLY_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},                # Rule 3
    "toggleCfg": {"reply.status": True},          # WorkatoServiceSendReply.json pattern
    "input": {
        "reply_type": "success",
        "reply":      {"status": "PAYMENTS_PROCESSED"},
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

# [16] catch logger — wire error.message pill in GUI
# Reference: Workato/RecipeComponents/Log.json
step16_log_catch = make_logger(
    16, LOG_CAT,
    "Outer error — wire error.message datapill in GUI",
    title="Catch logger (wire error.message in GUI)",
)

# [15] catch — LAST in try.block (Rule 6)
# Reference: oracle.json — catch carries "as" alias + retry config in "input"
step15_catch = {
    "number":  15,
    "keyword": "catch",
    "as":      CATCH_AS,    # oracle.json shows catch has "as" alias
    "uuid":    uid(),
    "input":   {"max_retry_count": "0", "retry_interval": "2"},
    "block":   [step16_log_catch],
}

# [1] try — wraps: foreach → send_reply → catch (Rule 6: catch LAST)
# Reference: oracle.json (try/catch wrapper pattern; try has input: {})
step1_try = {
    "number":  1,
    "keyword": "try",
    "uuid":    uid(),
    "input":   {},    # oracle.json: try always has input: {}
    "block": [
        step2_foreach,      # [2] foreach payment loop
        step14_send_reply,  # [14] send_reply (before catch, inside try)
        step15_catch,       # [15] LAST (Rule 6)
    ],
}

# ── Trigger (WorkatoServiceTrigger.json) ──────────────────────────────────────
# Rule 1: ALL fields must be scalar (no array/object) — payments passed as JSON string
# Rule 4: parameters_schema: ""
# Rule 15: extended_output_schema wraps fields under "request" object

request_schema = [
    {"name": "id",                "type": "string",  "optional": False,
     "control_type": "text",  "label": "Application ID"},
    {"name": "customerName",      "type": "string",  "optional": False,
     "control_type": "text",  "label": "Customer Name"},
    {"name": "customerID",        "type": "string",  "optional": False,
     "control_type": "text",  "label": "Customer ID"},
    {"name": "sourceName",        "type": "string",  "optional": True,
     "control_type": "text",  "label": "Source Name"},
    {"name": "sourceSubCategory", "type": "string",  "optional": True,
     "control_type": "text",  "label": "Source Sub Category"},
    {"name": "salesRepName",      "type": "string",  "optional": True,
     "control_type": "text",  "label": "Sales Rep Name"},
    {"name": "payments",          "type": "string",  "optional": False,
     "control_type": "text",
     "label": "Payments JSON array — Rule 1: flattened scalar; parse_json inside loop"},
]

reply_schema = [
    {"name": "status", "type": "string", "optional": False,
     "control_type": "text", "label": "Processing Status"},
]

trigger = {
    "number":   0,
    "provider": "workato_service",
    "name":     "receive_request",
    "as":       TRIG_AS,
    "keyword":  "trigger",
    "uuid":     uid(),
    "dynamicPickListSelection": {},     # Rule 3
    "toggleCfg":               {},     # Rule 2
    "parameters_schema":       "",     # Rule 4 — required on callable triggers
    "input": {
        "service_name":        RECIPE_NAME,
        "request_schema_json": json.dumps(request_schema),
        "reply_schema_json":   json.dumps(reply_schema),
    },
    # Rule 15: extended_output_schema wraps under "request" object (WorkatoServiceTrigger.json)
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

# ── Config (Rule 13: account_id = integer or null — NEVER string) ─────────────
config = [
    # workato_service: trigger + send_reply (null account_id per WorkatoServiceTrigger.json)
    {"keyword": "application", "provider": "workato_service",
     "account_id": None,           "skip_validation": False},
    # http: http/post inline URL steps (null account_id — no stored connection)
    {"keyword": "application", "provider": "http",
     "account_id": None,           "skip_validation": False},
    # oracle: MIG_WM_GLD_Oracle_Connection — integer account_id (Rule 13)
    {"keyword": "application", "provider": "oracle",
     "account_id": ORACLE_CONN_ID, "skip_validation": False},
    # logger: Log.json shows account_id: null
    {"keyword": "application", "provider": "logger",
     "account_id": None,           "skip_validation": False},
]

# ── Structure validation ───────────────────────────────────────────────────────
def validate():
    """Assert all SKILL.md structural rules are satisfied before pushing."""
    try_blk     = trigger["block"][0]["block"]
    foreach_blk = try_blk[0]["block"]

    assert trigger["block"][0]["keyword"] == "try",              "Step 1 must be try"
    assert try_blk[0]["keyword"]  == "foreach",                  "Step 2 must be foreach (forEach.json)"
    assert try_blk[0].get("repeat_mode") == "simple",            "repeat_mode must be 'simple'"
    assert try_blk[0].get("clear_scope") == "false",             "clear_scope must be 'false' (string)"
    assert "source" in try_blk[0],                               "forEach source must be top-level field"
    assert "source" not in try_blk[0].get("input", {}),         "source must NOT be inside input (forEach.json)"
    assert try_blk[0].get("input") == {},                        "forEach input must be empty dict"
    assert try_blk[-1]["keyword"] == "catch",                    "catch must be LAST in try.block (Rule 6)"
    assert foreach_blk[-1]["keyword"] == "rescue",               "rescue must be LAST in foreach.block (Rule 5)"
    assert foreach_blk[1]["keyword"] == "elsif",                 "Step 8 must be elsif flat sibling (Rule 7)"
    assert foreach_blk[2].get("input") == {},                   "else must have input:{} (oracle.json)"
    assert "as" in try_blk[-1],                                  "catch must have 'as' alias (oracle.json)"
    assert trigger["parameters_schema"] == "",                   "Rule 4: parameters_schema must be ''"

    # Logger name from Log.json
    for s in [step11_log_default, step13_log_rescue, step16_log_catch]:
        assert s["name"] == "log_message", f"Step {s['number']} must use log_message (Log.json)"

    # dynamicPickListSelection present on all action steps (Rule 3)
    actions = [step4_get_payee, step6_add_payee, step7_create_check,
               step9_oracle_sp, step11_log_default, step13_log_rescue,
               step14_send_reply, step16_log_catch]
    for s in actions:
        assert "dynamicPickListSelection" in s, f"Missing dynamicPickListSelection on step {s['number']}"

    # toggleCfg present on all action steps (Rule 2)
    for s in actions:
        assert "toggleCfg" in s, f"Missing toggleCfg on step {s['number']}"

    print("Structure validation PASSED:")
    print(f"  try.block          : {[s['keyword'] for s in try_blk]}")
    print(f"  foreach.block      : {[s['keyword'] for s in foreach_blk]}")
    print(f"  forEach keyword    : {try_blk[0]['keyword']} (forEach.json canonical)")
    print(f"  forEach repeat_mode: {try_blk[0].get('repeat_mode')}")
    print(f"  forEach clear_scope: {try_blk[0].get('clear_scope')}")
    print(f"  forEach source     : TOP-LEVEL (key fix vs Test1) = '{try_blk[0].get('source', '')[:50]}...'")
    print(f"  forEach input      : {try_blk[0].get('input')} (empty — forEach.json canonical)")
    print(f"  else.input         : {foreach_blk[2].get('input')} (oracle.json ref)")
    print(f"  catch.as           : {try_blk[-1].get('as')}")
    print(f"  logger name        : log_message on all {len([step11_log_default, step13_log_rescue, step16_log_catch])} logger steps")
    print(f"  dynamicPL          : present on all {len(actions)} action steps")
    print(f"  toggleCfg          : present on all {len(actions)} action steps")
    print()

validate()

# ── Payload builder (Rule 9: code + config as JSON strings) ───────────────────
def build_payload(folder_id):
    return {
        "recipe": {
            "name":      RECIPE_NAME,
            "folder_id": str(folder_id),        # Rule 9: string for create
            "code":      json.dumps(trigger),   # Rule 9: JSON string, not dict
            "config":    json.dumps(config),    # Rule 9: JSON string, not list
        }
    }

# ── Main ──────────────────────────────────────────────────────────────────────
if DRY_RUN:
    payload = build_payload(PARENT_FOLDER_ID)
    display = dict(payload["recipe"])
    display["code"]   = json.loads(display["code"])
    display["config"] = json.loads(display["config"])
    print("\n=== DRY RUN ===")
    print(json.dumps({"recipe": display}, indent=2)[:5000], "...")
else:
    folder_id = resolve_folder_id()
    payload   = build_payload(folder_id)

    print(f"\nPushing '{RECIPE_NAME}' to folder {folder_id}...")
    try:
        result = api("POST", "/recipes", payload)
        rid = result.get("id") or result.get("recipe", {}).get("id")
        print()
        print("=" * 60)
        print("PUSH SUCCESSFUL")
        print("=" * 60)
        print(f"  Recipe Name : {RECIPE_NAME}")
        print(f"  Recipe ID   : {rid}")
        print(f"  Folder ID   : {folder_id}")
        print(f"  URL         : https://app.workato.com/recipes/{rid}")
        print()
        print("REMAINING MANUAL GUI STEPS:")
        print("  1. Open recipe — confirm all 17 steps render without grey boxes")
        print()
        print("  2. CheckWriter HTTP connection:")
        print(f"     Name: GLDFundingEngine_CheckWriter_Connection")
        print(f"     Base URL: {CHECKWRITER_BASE}  (obtain real URL from SME)")
        print("     Wire to: step 4 (invokeGetUniquePayee)")
        print("              step 6 (invokeAddNewPayee)")
        print("              step 7 (invokeCreateCheckRequest)")
        print()
        print("  3. Oracle connection:")
        print(f"     Use existing: MIG_WM_GLD_Oracle_Connection (account_id={ORACLE_CONN_ID})")
        print("     Wire to: step 9 (Oracle GLD_ACH.INSERTPAYMENT)")
        print("     Confirm SP name 'GLD_ACH.INSERTPAYMENT' with SME")
        print()
        print("  4. Error message datapills (requires GUI):")
        print("     Step 13 (rescue logger): wire error.message datapill")
        print("     Step 16 (catch logger):  wire error.message datapill")
        print()
        print("  5. KEY CHANGE vs Test1:")
        print("     forEach 'source' field is now at TOP LEVEL (not inside input)")
        print("     This follows forEach.json canonical reference exactly.")
        print("     Verify step 2 (foreach) shows the payments list as loop source in GUI.")
    except RuntimeError as e:
        sys.exit(f"Push failed: {e}")
