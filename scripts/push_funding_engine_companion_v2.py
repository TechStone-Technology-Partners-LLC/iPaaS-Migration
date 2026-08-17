#!/usr/bin/env python3
"""
UPDATE script: Funding Engine using Companion (recipe 74633314)
Fixes applied vs v1:
  FIX 1: keyword "each" → "foreach" + repeat_mode="simple" + clear_scope="false"
          (forEach.json canonical reference confirms this format)
  FIX 2: Loop item datapills: provider="workato_service" (not "workato")
          (control_if_else.md + action_http.md both confirm workato_service)
  FIX 3: send_reply moved INSIDE try.block (before catch)
          (control_try_catch.md pattern: try.block = [foreach, send_reply, catch])
  FIX 4: toggleCfg removed from control-flow steps (if/elsif/else/try/foreach/rescue/catch)
          (Rule 2 applies to keyword="action" only, not control-flow keywords)

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
RECIPE_ID      = 74633314     # existing recipe — updating in place
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

# Aliases
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
    # Trigger fields: provider=workato_service, path=[request, field]
    return _pill("workato_service", TRIG_AS, "request", field)

def pay(field):
    # FIX 2: Loop item datapills use provider="workato_service" (not "workato")
    # Confirmed: control_if_else.md + action_http.md both use workato_service
    return _pill("workato_service", PAYEE_LOOP_AS, "*", field)

def http_out(step_as, field):
    return _pill("http", step_as, field)

def raw_http(step_as, field):
    return _raw("http", step_as, field)

# ── PayeeInformation (Section 5.2 rows 1-11) ─────────────────────────────────
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

# ── Step builders ─────────────────────────────────────────────────────────────
def http_action(num, alias, url, payload_dict, title=None):
    """keyword=action — toggleCfg required (Rule 2). dynamicPickListSelection not needed."""
    s = {
        "number":   num,
        "keyword":  "action",
        "provider": "http",
        "name":     "post",
        "as":       alias,
        "uuid":     uid(),
        "toggleCfg": {},    # Rule 2 — action steps only
        "input": {
            "url":          url,
            "content_type": "application/json",
            "payload":      json.dumps(payload_dict),
        },
    }
    if title:
        s["title"] = title
    return s

def oracle_sp(num, alias, proc_name, params, title=None):
    """Oracle: toggleCfg (Rule 2) + dynamicPickListSelection (Rule 3)."""
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
        "toggleCfg": {},                                             # Rule 2
        "input":    inp,
    }
    if title:
        s["title"] = title
    return s

# ═══════════════════════════════════════════════════════════════════════════════
# STEP DEFINITIONS  (bottom-up build order)
# ═══════════════════════════════════════════════════════════════════════════════

# [4] HTTP invokeGetUniquePayee (Section 5.2 rows 1-11)
step4 = http_action(
    4, GET_PAYEE_AS,
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeGetUniquePayee",
    PAYEE_INFO,
    title="Check.1 — invokeGetUniquePayee (search existing payee)",
)

# [6] HTTP invokeAddNewPayee (if payeeKey empty)
step6 = http_action(
    6, ADD_PAYEE_AS,
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeAddNewPayee",
    PAYEE_INFO,
    title="Check.1b — invokeAddNewPayee (register new payee)",
)

# [5] if payeeKey is_empty → addNewPayee  (Section 5.2 row 12 OR logic)
# FIX 4: no toggleCfg on if (control-flow step, not action)
step5 = {
    "number": 5,
    "keyword": "if",
    "uuid": uid(),
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

# [7] HTTP invokeCreateCheckRequest (Section 5.2 rows 12-17)
PAYEEKEY = "#{" + raw_http(GET_PAYEE_AS, "payeeKey") + ".presence || " + raw_http(ADD_PAYEE_AS, "payeeKey") + "}"
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
    title="Check.2 — invokeCreateCheckRequest",
)

# [3] if type == "Check"
# FIX 4: no toggleCfg
step3 = {
    "number": 3,
    "keyword": "if",
    "uuid": uid(),
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

# [9] Oracle execute_stored_procedure → GLD_ACH.INSERTPAYMENT (Section 5.3)
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
    title="ACH — Oracle GLD_ACH.INSERTPAYMENT (11 params)",
)

# [8] elsif type == "ACH"
# FIX 4: no toggleCfg on elsif
step8 = {
    "number": 8,
    "keyword": "elsif",     # Rule 7 — flat sibling, NOT nested
    "uuid": uid(),
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

# [11] Logger — Default/Wire path
step11 = {
    "number":   11,
    "keyword":  "action",
    "provider": "logger",
    "name":     "create_message",
    "as":       LOG_DEFAULT_AS,
    "uuid":     uid(),
    "toggleCfg": {},    # Rule 2 — action step
    "input": {
        "message": "Default path — type=" + pay("type"),
        "level":   "info",
    },
}

# [10] else — Default/Wire/Other
# FIX 4: no toggleCfg on else
step10 = {
    "number":  10,
    "keyword": "else",
    "uuid":    uid(),
    "block":   [step11],
}

# [13] HTTP log inside rescue
step13 = http_action(
    13, LOG_RESCUE_AS,
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {"AppID": "3", "RequestIdentifier1": pay("id")},
    title="RESCUE — LogXMLRequest (per-payment error)",
)

# rescue — LAST in foreach.block (Rule 5)
# FIX 4: no toggleCfg on rescue
rescue = {
    "number":  14,
    "keyword": "rescue",
    "uuid":    uid(),
    "block":   [step13],
}

# [2] foreach — FIX 1: "foreach" + repeat_mode + clear_scope (forEach.json reference)
# Also: no toggleCfg on foreach (control-flow step)
_pay_pill_json = json.dumps({
    "pill_type": "output",
    "provider":  "workato_service",
    "line":      TRIG_AS,
    "path":      ["request", "payments"],
}).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill_json + "').parse_json}"

step2_foreach = {
    "number":      2,
    "keyword":     "foreach",          # FIX 1 — "foreach" not "each"
    "as":          PAYEE_LOOP_AS,
    "repeat_mode": "simple",           # FIX 1 — required by forEach.json reference
    "clear_scope": "false",            # FIX 1 — required by forEach.json reference
    "uuid":        uid(),
    "input":       {"source": PAYMENTS_SOURCE},
    "block": [
        step3,    # if Check
        step8,    # elsif ACH     (Rule 7 — flat sibling)
        step10,   # else Default
        rescue,   # LAST (Rule 5)
    ],
}

# [16] send_reply — FIX 3: INSIDE try.block (before catch), per control_try_catch.md
send_reply = {
    "number":   16,
    "keyword":  "action",
    "provider": "workato_service",
    "name":     "send_reply",
    "as":       REPLY_AS,
    "uuid":     uid(),
    "dynamicPickListSelection": {},
    "toggleCfg": {"reply.status": True},   # Rule 2
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

# [15] HTTP log inside catch
step15 = http_action(
    15, LOG_CATCH_AS,
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {"AppID": "3"},
    title="CATCH — LogXMLRequest (outer error)",
)

# catch — LAST in try.block (Rule 6)
# FIX 4: no toggleCfg on catch
catch = {
    "number":  17,
    "keyword": "catch",
    "uuid":    uid(),
    "input":   {"max_retry_count": "0", "retry_interval": "2"},
    "block":   [step15],
}

# [1] try — FIX 3: try.block = [foreach, send_reply, catch]
# FIX 4: no toggleCfg on try
step1_try = {
    "number":  1,
    "keyword": "try",
    "uuid":    uid(),
    "input":   {},
    "block": [
        step2_foreach,  # foreach (each payments)
        send_reply,     # FIX 3 — send_reply inside try, before catch
        catch,          # LAST (Rule 6)
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# TRIGGER  (Rules 1, 4, 15)
# ═══════════════════════════════════════════════════════════════════════════════
request_schema = [
    {"name": "id",                "type": "string",  "optional": False, "control_type": "text",
     "label": "Application ID"},
    {"name": "customerName",      "type": "string",  "optional": False, "control_type": "text",
     "label": "Customer Name"},
    {"name": "customerID",        "type": "string",  "optional": False, "control_type": "text",
     "label": "Customer ID"},
    {"name": "sourceName",        "type": "string",  "optional": True,  "control_type": "text",
     "label": "Source Name"},
    {"name": "sourceSubCategory", "type": "string",  "optional": True,  "control_type": "text",
     "label": "Source Sub Category"},
    {"name": "salesRepName",      "type": "string",  "optional": True,  "control_type": "text",
     "label": "Sales Rep Name"},
    {"name": "payments",          "type": "string",  "optional": False, "control_type": "text",
     "label": "Payments (JSON array string) — fields: id, type, amount, invoiceReference, comment, checkMemo, payee_*"},
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
    "block": [step1_try],   # try is the only top-level step (send_reply is inside try)
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

# ── Payload (Rule 9: code + config as JSON strings) ───────────────────────────
update_payload = {
    "recipe": {
        "name":        RECIPE_NAME,
        "folder_id":   FOLDER_ID,
        "code":        json.dumps(trigger),   # Rule 9
        "config":      json.dumps(config),    # Rule 9
    }
}

# ── Quick structure validation ─────────────────────────────────────────────────
def validate():
    top = trigger["block"]
    assert top[0]["keyword"] == "try",     "Step 1 must be try"
    try_blk = top[0]["block"]
    assert try_blk[0]["keyword"] == "foreach", "Step 2 must be foreach (FIX 1)"
    assert try_blk[-1]["keyword"] == "catch",  "catch must be LAST in try.block (Rule 6)"
    foreach_blk = try_blk[0]["block"]
    assert foreach_blk[-1]["keyword"] == "rescue", "rescue must be LAST in foreach.block (Rule 5)"
    assert foreach_blk[1]["keyword"] == "elsif",   "step 8 must be elsif (Rule 7)"
    print("Structure validation passed:")
    print(f"  try.block    : {[s['keyword'] for s in try_blk]}")
    print(f"  foreach.block: {[s['keyword'] for s in foreach_blk]}")
    print(f"  foreach mode : {try_blk[0].get('repeat_mode')} / clear_scope={try_blk[0].get('clear_scope')}")
    print(f"  pay('type')  : {pay('type')[:60]}...")
    print(f"  provider in pay(): workato_service (FIX 2 applied)")

validate()

# ── Push ──────────────────────────────────────────────────────────────────────
if DRY_RUN:
    display = dict(update_payload["recipe"])
    display["code"]   = json.loads(display["code"])
    display["config"] = json.loads(display["config"])
    print("\n=== DRY RUN ===")
    print(json.dumps({"recipe": display}, indent=2))
else:
    print(f"\nUpdating recipe {RECIPE_ID} ('{RECIPE_NAME}')...")
    result = api("PUT", f"/recipes/{RECIPE_ID}", update_payload)

    rid = result.get("id") or RECIPE_ID
    print()
    print("SUCCESS")
    print(f"  Recipe ID : {rid}")
    print(f"  URL       : https://app.workato.com/recipes/{rid}")
    print()
    print("Remaining GUI steps:")
    print("  1. Reload the recipe in Workato GUI and verify step layout")
    print("  2. Create 'GLDFundingEngine_CheckWriter_Connection' (HTTP)")
    print(f"     Base URL: {CHECKWRITER_URL}  <- replace with real URL from SME")
    print("     Wire to: step4 (getUniquePayee), step6 (addNewPayee), step7 (createCheckRequest)")
    print("  3. Wire Oracle 'MIG_WM_GLD_Oracle_Connection' (ID 19657520) to step9 (insertPayment)")
    print("  4. Create 'GLDFundingEngine_MessageLog_Connection' (HTTP)")
    print(f"     Base URL: {MESSAGELOG_URL}  <- replace with real URL from SME")
    print("     Wire to: step13 (rescue log), step15 (catch log)")
    print("  5. Wire error.message pills in step13 and step15 in GUI")
