#!/usr/bin/env python3
"""
UPDATE script: Funding Engine using Companion (recipe 74633314) — v3
Builds on v2 fixes and adds:

  FIX 5: dynamicPickListSelection: {} on ALL HTTP action steps
          (action_http.md reference confirms it is required for http/post)
          Without it, the HTTP step inside rescue.block is invisible
          → rescue renders as an empty grey box

  FIX 6: Loop keyword → "foreach" per Workato/RecipeComponents/forEach.json reference
          forEach.json is the canonical loop-shape definition: keyword="foreach"
          + repeat_mode="simple" + clear_scope="false"
          control_try_catch.md used "each" illustratively; forEach.json is authoritative

  KEPT from v2:
  FIX 1: repeat_mode="simple", clear_scope="false" on loop step
  FIX 2: Loop item datapills provider="workato_service"
  FIX 3: send_reply inside try.block (before catch)
  FIX 4: No toggleCfg on control-flow keywords

  Step numbering: consecutive 0-16, no gaps
    0  trigger
    1  try
    2  each (payment_loop)
    3    if type==Check
    4      HTTP invokeGetUniquePayee
    5      if payeeKey is_empty
    6        HTTP invokeAddNewPayee
    7      HTTP invokeCreateCheckRequest
    8    elsif type==ACH
    9      Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT
   10    else (Default/Wire/Other)
   11      logger (Default path)
   12    rescue (LAST in each.block)
   13      HTTP log rescue error
   14  send_reply (inside try.block, before catch)  <- FIX 3
   15  catch (LAST in try.block)
   16    HTTP log catch error

Skill: Workato/Companion/SKILL.md (workato-integration) — all 15 rules
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
RECIPE_ID      = 74633314
RECIPE_NAME    = "Funding Engine using Companion"
FOLDER_ID      = "31835141"
ORACLE_CONN_ID = 19657520
DRY_RUN        = "--dry-run" in sys.argv

CHECKWRITER_URL = "https://webmethods-gateway.keybank.internal"
MESSAGELOG_URL  = "https://webmethods-log.keybank.internal"

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
        sys.exit(f"HTTP {e.code} {method} {path}: {e.read().decode(errors='replace')[:600]}")

# ── Helpers ───────────────────────────────────────────────────────────────────
def uid():
    return str(uuid.uuid4())

# Step aliases
TRIG_AS         = "fe_companion_trig"
PAYEE_LOOP_AS   = "payment_loop"
GET_PAYEE_AS    = "get_payee"
ADD_PAYEE_AS    = "add_payee"
CREATE_CHECK_AS = "create_check"
ORACLE_ACH_AS   = "oracle_ach"
LOG_DEFAULT_AS  = "log_default"
LOG_RESCUE_AS   = "log_rescue"
LOG_CATCH_AS    = "log_catch"
REPLY_AS        = "send_reply_step"

# ── Datapill builders ─────────────────────────────────────────────────────────
def _pill(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    obj  = json.dumps({"pill_type": "output", "provider": provider,
                       "line": line, "path": path}).replace('"', '\\"')
    return "#{_dp('" + obj + "')}"

def _raw(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    obj  = json.dumps({"pill_type": "output", "provider": provider,
                       "line": line, "path": path}).replace('"', '\\"')
    return "_dp('" + obj + "')"

def trig(field):
    return _pill("workato_service", TRIG_AS, "request", field)

def pay(field):
    # FIX 2 (v2): provider="workato_service" for loop items
    return _pill("workato_service", PAYEE_LOOP_AS, "*", field)

def http_out(step_as, field):
    return _pill("http", step_as, field)

def raw_http(step_as, field):
    return _raw("http", step_as, field)

# ── Payee info dict (Section 5.2, rows 1-11) ─────────────────────────────────
PAYEE_INFO = {
    "PayeeName":          pay("payee_name"),
    "AddressLine1":       pay("payee_address1"),
    "AddressLine2":       pay("payee_address2"),
    "City":               pay("payee_city"),
    "State":              pay("payee_state_province"),
    "PostalCode":         pay("payee_zip"),
    "PhoneNumber":        pay("payee_phone"),
    "FaxNumber":          pay("payee_fax"),
    "ContactName":        pay("payee_contactName"),
    "ContactPhoneNumber": pay("payee_contactPhone"),
    "Country":            "USA",
}

# ── HTTP action builder ───────────────────────────────────────────────────────
def http_action(num, alias, url, payload_dict, title=None):
    """
    FIX 5: dynamicPickListSelection: {} required on ALL http/post steps.
    Without it the step is invisible inside its parent container.
    """
    s = {
        "number":   num,
        "keyword":  "action",
        "provider": "http",
        "name":     "post",
        "as":       alias,
        "uuid":     uid(),
        "dynamicPickListSelection": {},   # FIX 5 -- was missing in v2
        "toggleCfg":                {},   # Rule 2
        "input": {
            "url":          url,
            "content_type": "application/json",
            "payload":      json.dumps(payload_dict),
        },
    }
    if title:
        s["title"] = title
    return s

# ── Oracle SP builder ─────────────────────────────────────────────────────────
def oracle_sp(num, alias, proc_name, params, title=None):
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
        "toggleCfg":               {},                               # Rule 2
        "input":    inp,
    }
    if title:
        s["title"] = title
    return s

# ═══════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS — consecutive numbering 0-16
# ═══════════════════════════════════════════════════════════════════════════════

# [4] HTTP invokeGetUniquePayee
step4 = http_action(
    4, GET_PAYEE_AS,
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeGetUniquePayee",
    PAYEE_INFO,
    title="Check.1 invokeGetUniquePayee",
)

# [6] HTTP invokeAddNewPayee (inside nested if.block)
step6 = http_action(
    6, ADD_PAYEE_AS,
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeAddNewPayee",
    PAYEE_INFO,
    title="Check.1b invokeAddNewPayee",
)

# [5] if payeeKey is_empty => addNewPayee
step5 = {
    "number": 5,
    "keyword": "if",
    "uuid":   uid(),
    "input": {
        "type":    "compound",
        "operand": "and",
        "conditions": [{
            "operand": "is_empty",
            "lhs":     http_out(GET_PAYEE_AS, "payeeKey"),
            "uuid":    uid(),
        }],
    },
    "block": [step6],
}

# payeeKey pill: presence-chain for get OR add result
PAYEEKEY = "#{" + raw_http(GET_PAYEE_AS, "payeeKey") + ".presence || " + raw_http(ADD_PAYEE_AS, "payeeKey") + "}"

# [7] HTTP invokeCreateCheckRequest
step7 = http_action(
    7, CREATE_CHECK_AS,
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeCreateCheckRequest",
    {
        "PayeeKey":    PAYEEKEY,
        "Notes":       pay("invoiceReference"),
        "Comments":    pay("comment"),
        "CheckAmount": pay("amount"),
        "Memo":        pay("checkMemo"),
        "LeaseNumber": trig("id"),
    },
    title="Check.2 invokeCreateCheckRequest",
)

# [3] if type == "Check"
step3 = {
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
    "block": [step4, step5, step7],
}

# [9] Oracle GLD_ACH.INSERTPAYMENT (Section 5.3)
step9 = oracle_sp(
    9, ORACLE_ACH_AS,
    "GLD_ACH.INSERTPAYMENT",
    {
        "REQUESTOR_ID":   "1",
        "APP_ID":         trig("id"),
        "CUSTOMER_NAME":  trig("customerName"),
        "CUSTOMER_ID":    trig("customerID"),
        "SOURCE":         trig("sourceName"),
        "AMOUNT":         pay("amount"),
        "REFERENCE":      pay("invoiceReference"),
        "PAYEE_ID":       pay("payee_id"),
        "PAYEE_NAME":     pay("payee_name"),
        "ACCOUNT_NUMBER": pay("payee_accountNumber"),
        "ROUTING_NUMBER": pay("payee_routingNumber"),
    },
    title="ACH Oracle GLD_ACH.INSERTPAYMENT",
)

# [8] elsif type == "ACH" (Rule 7: flat sibling, NOT nested)
step8 = {
    "number": 8,
    "keyword": "elsif",
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
    "block": [step9],
}

# [11] Logger — Default path
step11 = {
    "number":   11,
    "keyword":  "action",
    "provider": "logger",
    "name":     "create_message",
    "as":       LOG_DEFAULT_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},
    "toggleCfg":               {},
    "input": {
        "message": "Default path payment type=" + pay("type"),
        "level":   "info",
    },
}

# [10] else — Default/Wire/Other (no input field per reference)
step10 = {
    "number":  10,
    "keyword": "else",
    "uuid":    uid(),
    "block":   [step11],
}

# [13] HTTP log inside rescue block
step13 = http_action(
    13, LOG_RESCUE_AS,
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {"AppID": "3"},
    title="RESCUE log error (wire error.message pill in GUI)",
)

# [12] rescue — LAST in each.block (Rule 5)
# FIX 6 (v3): rescue control block has NO input, NO provider, NO name, NO as
rescue = {
    "number":  12,
    "keyword": "rescue",
    "uuid":    uid(),
    "block":   [step13],
}

# [2] foreach — rendered exactly per Workato/RecipeComponents/forEach.json
#   forEach.json canonical fields:
#     "keyword":     "foreach"
#     "repeat_mode": "simple"
#     "clear_scope": "false"
#     "as":          "<alias>"
#     "input":       {"source": <datapill>}   ← source added for actual recipe
#     "uuid":        "<uuid>"
_pay_pill_json = json.dumps({
    "pill_type": "output",
    "provider":  "workato_service",
    "line":      TRIG_AS,
    "path":      ["request", "payments"],
}).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill_json + "').parse_json}"

step2_each = {
    "number":      2,
    "keyword":     "foreach",        # forEach.json canonical reference
    "as":          PAYEE_LOOP_AS,
    "repeat_mode": "simple",         # forEach.json required field
    "clear_scope": "false",          # forEach.json required field
    "uuid":        uid(),
    "input":       {"source": PAYMENTS_SOURCE},
    "block": [
        step3,   # if Check
        step8,   # elsif ACH  (Rule 7 -- flat sibling)
        step10,  # else Default
        rescue,  # LAST (Rule 5)
    ],
}

# [16] HTTP log inside catch block
step16 = http_action(
    16, LOG_CATCH_AS,
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {"AppID": "3"},
    title="CATCH log error (wire error.message pill in GUI)",
)

# [15] catch — LAST in try.block (Rule 6)
catch = {
    "number":  15,
    "keyword": "catch",
    "uuid":    uid(),
    "input":   {"max_retry_count": "0", "retry_interval": "2"},
    "block":   [step16],
}

# [14] send_reply — FIX 3: INSIDE try.block before catch
send_reply = {
    "number":   14,
    "keyword":  "action",
    "provider": "workato_service",
    "name":     "send_reply",
    "as":       REPLY_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {"reply.status": True},
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

# [1] try — try.block = [each, send_reply, catch]
step1_try = {
    "number":  1,
    "keyword": "try",
    "uuid":    uid(),
    "input":   {},           # always empty dict per reference
    "block": [
        step2_each,  # each loop
        send_reply,  # FIX 3 -- inside try, before catch
        catch,       # LAST (Rule 6)
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# TRIGGER (Rules 1, 4, 15)
# ═══════════════════════════════════════════════════════════════════════════════
request_schema = [
    {"name": "id",                "type": "string",  "optional": False,
     "control_type": "text", "label": "Application ID"},
    {"name": "customerName",      "type": "string",  "optional": False,
     "control_type": "text", "label": "Customer Name"},
    {"name": "customerID",        "type": "string",  "optional": False,
     "control_type": "text", "label": "Customer ID"},
    {"name": "sourceName",        "type": "string",  "optional": True,
     "control_type": "text", "label": "Source Name"},
    {"name": "sourceSubCategory", "type": "string",  "optional": True,
     "control_type": "text", "label": "Source Sub Category"},
    {"name": "salesRepName",      "type": "string",  "optional": True,
     "control_type": "text", "label": "Sales Rep Name"},
    {"name": "payments",          "type": "string",  "optional": False,
     "control_type": "text",
     "label": "Payments JSON array — fields: id, type, amount, invoiceReference, comment, checkMemo, payee_*"},
]

reply_schema = [
    {"name": "status", "type": "string", "optional": False,
     "control_type": "text", "label": "Processing status"},
]

trigger = {
    "number":   0,
    "keyword":  "trigger",
    "provider": "workato_service",
    "name":     "receive_request",
    "as":       TRIG_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "parameters_schema": "",   # Rule 4
    "input": {
        "service_name":        RECIPE_NAME,
        "request_schema_json": json.dumps(request_schema),
        "reply_schema_json":   json.dumps(reply_schema),
    },
    "extended_output_schema": [   # Rule 15
        {"name": f["name"], "type": f["type"],
         "control_type": f["control_type"], "label": f["label"]}
        for f in request_schema
    ],
    "block": [step1_try],    # trigger.block = [try]
}

# ── Config (Rule 13) ──────────────────────────────────────────────────────────
config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None,            "skip_validation": False},
    {"keyword": "application", "provider": "http",
     "account_id": None,            "skip_validation": False},
    {"keyword": "application", "provider": "oracle",
     "account_id": ORACLE_CONN_ID,  "skip_validation": False},
    {"keyword": "application", "provider": "logger",
     "account_id": None,            "skip_validation": False},
]

# ── Payload (Rule 9) ──────────────────────────────────────────────────────────
update_payload = {
    "recipe": {
        "name":      RECIPE_NAME,
        "folder_id": FOLDER_ID,
        "code":      json.dumps(trigger),   # Rule 9: JSON string
        "config":    json.dumps(config),    # Rule 9: JSON string
    }
}

# ── Validation ────────────────────────────────────────────────────────────────
def validate():
    top     = trigger["block"]
    try_blk = top[0]["block"]
    each_blk = try_blk[0]["block"]

    assert top[0]["keyword"] == "try",                 "Step 1 must be try"
    assert try_blk[0]["keyword"] == "foreach",          "Step 2 must be foreach (forEach.json ref)"
    assert try_blk[0].get("repeat_mode") == "simple",  "repeat_mode missing"
    assert try_blk[-1]["keyword"] == "catch",           "catch must be LAST in try.block"
    assert each_blk[-1]["keyword"] == "rescue",         "rescue must be LAST in foreach.block"
    assert each_blk[1]["keyword"] == "elsif",           "step 8 must be elsif (flat sibling)"

    # Check dynamicPickListSelection on all HTTP steps
    for s in [step4, step6, step7, step13, step16]:
        assert "dynamicPickListSelection" in s, f"Missing dynamicPickListSelection on step {s['number']}"

    print("Structure validation passed (v3):")
    print(f"  try.block  : {[s['keyword'] for s in try_blk]}")
    print(f"  foreach.block: {[s['keyword'] for s in each_blk]}")
    print(f"  foreach mode : {try_blk[0].get('repeat_mode')} / clear_scope={try_blk[0].get('clear_scope')}")
    print(f"  foreach keyword: {try_blk[0]['keyword']} (forEach.json canonical ref)")
    print(f"  HTTP dynamicPickListSelection: present on all 5 HTTP steps")
    print(f"  pay('type'): provider=workato_service, line={PAYEE_LOOP_AS}")
    print()
    print("  Step map (JSON number -> expected GUI display):")
    print("    0 trigger  -> GUI step 1")
    print("    1 try      -> GUI step 2")
    print("    2 each     -> GUI step 3")
    print("    3 if       -> GUI step 4")
    print("    4 HTTP     -> GUI step 5")
    print("    5 if(key)  -> GUI step 6")
    print("    6 HTTP     -> GUI step 7")
    print("    7 HTTP     -> GUI step 8")
    print("    8 elsif    -> GUI step 9")
    print("    9 oracle   -> GUI step 10")
    print("   10 else     -> GUI step 11")
    print("   11 logger   -> GUI step 12")
    print("   12 rescue   -> GUI step 13")
    print("   13 HTTP     -> GUI step 14 (inside rescue)")
    print("   14 reply    -> GUI step 15")
    print("   15 catch    -> GUI step 16")
    print("   16 HTTP     -> GUI step 17 (inside catch)")

validate()

# ── Push ──────────────────────────────────────────────────────────────────────
if DRY_RUN:
    display = dict(update_payload["recipe"])
    display["code"]   = json.loads(display["code"])
    display["config"] = json.loads(display["config"])
    print("\n=== DRY RUN ===")
    print(json.dumps({"recipe": display}, indent=2)[:3000], "...")
else:
    print(f"\nPushing update to recipe {RECIPE_ID} ('{RECIPE_NAME}')...")
    result = api("PUT", f"/recipes/{RECIPE_ID}", update_payload)

    rid = result.get("id") or RECIPE_ID
    print()
    print("SUCCESS")
    print(f"  Recipe ID : {rid}")
    print(f"  URL       : https://app.workato.com/recipes/{rid}")
    print()
    print("Remaining GUI steps after reload:")
    print("  1. Verify step layout renders correctly (rescue should now show content)")
    print("  2. Create 'GLDFundingEngine_CheckWriter_Connection' (HTTP)")
    print(f"     Base URL: {CHECKWRITER_URL}  <- replace with real URL from SME")
    print("     Wire to: steps 5,7,8 (getUniquePayee, addNewPayee, createCheckRequest)")
    print("  3. Wire Oracle 'MIG_WM_GLD_Oracle_Connection' (ID 19657520) to step 10")
    print("  4. Create 'GLDFundingEngine_MessageLog_Connection' (HTTP)")
    print(f"     Base URL: {MESSAGELOG_URL}  <- replace with real URL from SME")
    print("     Wire to: steps 14,17 (rescue log, catch log)")
    print("  5. Wire error.message datapills in steps 14 and 17 in GUI")
