#!/usr/bin/env python3
"""
Push script: Funding Engine using Companion
Folder:      MigrAIte_Training (folder_id: 31835141)
Account:     manish@techstonellc.com

Source:      WebMethods/GLDFundingEngine20080714
Skill used:  Workato/Companion/SKILL.md (workato-integration) — all 15 rules applied
Analysis:    WebMethods/Analysis/MD/PackageAnalysis.md (Section 8, Recipe 1)

Recipe structure:
  TRIGGER: workato_service/receive_request "Funding Engine using Companion"
    Flat schema: id, customerName, customerID, sourceName,
                 sourceSubCategory, salesRepName, payments (JSON string)

  [1] try
    [2] each: payment_loop (source = trigger.payments.parse_json)
      [3]  if type == "Check"
        [4]  HTTP POST invokeGetUniquePayee  (11 payee fields)
        [5]  if payeeKey is_empty
          [6]  HTTP POST invokeAddNewPayee   (same 11 fields)
        [7]  HTTP POST invokeCreateCheckRequest (PayeeKey + 6 fields)
      [8]  elsif type == "ACH"    ← keyword: "elsif" flat sibling (Rule 7)
        [9]  Oracle execute_stored_procedure GLD_ACH.INSERTPAYMENT (11 params)
      [10] else Default/Wire
        [11] Logger info — no external processor
      rescue  ← LAST in each.block (Rule 5)
        [12] HTTP POST GLDMessageLog:LogXMLRequest  (per-payment error log)
    catch   ← LAST in try.block (Rule 6)
      [13] HTTP POST GLDMessageLog:LogXMLRequest  (outer error log)
  [14] workato_service/send_reply → {status: "PAYMENTS_PROCESSED"}

Connections (wire in Workato GUI after push):
  GLDFundingEngine_CheckWriter_Connection  → steps 4, 6, 7 (HTTP — base URL from SME)
  MIG_WM_GLD_Oracle_Connection (19657520) → step 9      (Oracle ACH insertPayment)
  GLDFundingEngine_MessageLog_Connection   → steps 12, 13 (HTTP — base URL from SME)

SKILL.md rules applied:
  Rule 1:  Trigger schema flat — payments as JSON string, parse_json in each
  Rule 2:  toggleCfg: {} on every action/control step
  Rule 3:  dynamicPickListSelection: {} on Oracle step
  Rule 4:  parameters_schema: "" on callable trigger
  Rule 5:  rescue LAST in each.block
  Rule 6:  catch LAST in try.block
  Rule 7:  keyword "elsif" — flat sibling, not nested
  Rule 8:  folder API flat JSON (create script)
  Rule 9:  recipe code + config as JSON strings in POST payload
  Rule 10: new recipe — GET-before-PUT not needed
  Rule 11: uuid on every step
  Rule 12: current_item path element for loop item datapills
  Rule 13: account_id integer for Oracle; null for http/logger/workato_service
  Rule 14: keyword "each" (confirmed working)
  Rule 15: extended_output_schema on trigger for GUI pill tree
"""

import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
RECIPE_NAME    = "Funding Engine using Companion"
FOLDER_ID      = "31835141"   # MigrAIte_Training (folder creation IP-blocked; move in GUI)
ORACLE_CONN_ID = 19657520     # MIG_WM_GLD_Oracle_Connection (already in account)
DRY_RUN        = "--dry-run" in sys.argv

# Placeholder URLs — replace with real values from SME
CHECKWRITER_URL  = "https://webmethods-gateway.keybank.internal"
MESSAGELOG_URL   = "https://webmethods-log.keybank.internal"

# ── Auth ──────────────────────────────────────────────────────────────────────
def load_env():
    """Walk ancestor dirs to find .env — SKILL.md credential pattern."""
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

BASE = "https://www.workato.com/api"   # hardcoded — avoids trailing-slash 404

# ── HTTP helper ───────────────────────────────────────────────────────────────
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
    """Rule 11 — every step must have a unique UUID4."""
    return str(uuid.uuid4())

# Step aliases (Rule 12 — line field in datapills must match the step's "as" alias)
TRIG_AS          = "fe_companion_trig"
GET_PAYEE_AS     = "get_payee"
ADD_PAYEE_AS     = "add_payee"
CREATE_CHECK_AS  = "create_check"
ORACLE_ACH_AS    = "oracle_ach"
LOG_DEFAULT_AS   = "log_default"
LOG_RESCUE_AS    = "log_rescue"
LOG_CATCH_AS     = "log_catch"
REPLY_AS         = "send_reply"

# ── Datapill builders ─────────────────────────────────────────────────────────
def _pill(provider, line, *path_parts):
    """Build a Workato datapill template string."""
    path = []
    for p in path_parts:
        path.append({"path_element_type": "current_item"} if p == "*" else p)
    obj = json.dumps({"pill_type": "output", "provider": provider,
                      "line": line, "path": path}).replace('"', '\\"')
    return "#{_dp('" + obj + "')}"

def trig(field):
    """Trigger field pill — workato_service, nested under 'request'."""
    return _pill("workato_service", TRIG_AS, "request", field)

def pay(field):
    """Current payment loop item field — Rule 12: provider=workato, current_item."""
    return _pill("workato", PAYEE_LOOP_AS, "*", field)

PAYEE_LOOP_AS = "payment_loop"  # alias for the each step

def http_out(step_as, field):
    """Output field from a previous HTTP action step."""
    return _pill("http", step_as, field)

def raw_pill(provider, line, *path_parts):
    """Raw _dp(...) expression for use inside #{formula} strings."""
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    obj = json.dumps({"pill_type": "output", "provider": provider,
                      "line": line, "path": path}).replace('"', '\\"')
    return "_dp('" + obj + "')"

# ── PayeeInformation payload (Section 5.2 rows 1–11) ─────────────────────────
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
def http_action(num, alias, title, url, payload_dict):
    """Rule 2 (toggleCfg) + Rule 11 (uuid). No dynamicPickListSelection needed for HTTP."""
    return {
        "number":   num,
        "keyword":  "action",
        "provider": "http",
        "name":     "post",
        "as":       alias,
        "title":    title,
        "uuid":     uid(),
        "toggleCfg": {},
        "input": {
            "url":          url,
            "content_type": "application/json",
            "payload":      json.dumps(payload_dict),
        },
    }

def oracle_sp(num, alias, proc_name, params, title=None):
    """
    Rule 2 (toggleCfg) + Rule 3 (dynamicPickListSelection) + Rule 11 (uuid)
    + Rule 13 (account_id integer in config).
    """
    inp = {"procedure_name": proc_name}
    inp.update(params)
    step = {
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
        step["title"] = title
    return step

# ═══════════════════════════════════════════════════════════════════════════════
# RECIPE STEPS  (built bottom-up — inner steps first)
# ═══════════════════════════════════════════════════════════════════════════════

# ── [4] HTTP POST invokeGetUniquePayee (Section 5.2, rows 1-11) ──────────────
step4 = http_action(
    4, GET_PAYEE_AS,
    "Check.1 — invokeGetUniquePayee (search for existing payee by name+address)",
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeGetUniquePayee",
    PAYEE_INFO,
)

# ── [6] HTTP POST invokeAddNewPayee (same 11 fields — only if payeeKey empty) ─
step6 = http_action(
    6, ADD_PAYEE_AS,
    "Check.1b — invokeAddNewPayee (register new payee; payeeKey was empty)",
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeAddNewPayee",
    PAYEE_INFO,
)

# ── [5] if payeeKey is_empty → invokeAddNewPayee  (Section 6, Business Rule 2) ─
# Section 5.2 row 12: OR logic → If Else block (Instruction_Workato.md rule)
step5 = {
    "number":  5,
    "keyword": "if",
    "title":   "Check.1a — payeeKey empty? If so, register new payee",
    "uuid":    uid(),
    "toggleCfg": {},   # Rule 2
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

# ── [7] HTTP POST invokeCreateCheckRequest (Section 5.2 rows 12-17) ──────────
# PayeeKey: use getUniquePayee result; fallback to addNewPayee result (Gap G6)
PAYEEKEY_FORMULA = (
    "#{" + raw_pill("http", GET_PAYEE_AS, "payeeKey") +
    ".presence || " + raw_pill("http", ADD_PAYEE_AS, "payeeKey") + "}"
)
step7 = http_action(
    7, CREATE_CHECK_AS,
    "Check.2 — invokeCreateCheckRequest (PayeeKey + amount/memo/reference)",
    CHECKWRITER_URL + "/GLDExpressGateway/CheckWriter/invokeCreateCheckRequest",
    {
        "PayeeKey":    PAYEEKEY_FORMULA,
        "Notes":       pay("invoiceReference"),
        "Comments":    pay("comment"),
        "CheckAmount": pay("amount"),
        "Memo":        pay("checkMemo"),
        "LeaseNumber": trig("id"),
    },
)

# ── [3] if type == "Check" ────────────────────────────────────────────────────
step3 = {
    "number":  3,
    "keyword": "if",
    "title":   "Route: payment.type == Check",
    "uuid":    uid(),
    "toggleCfg": {},   # Rule 2
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

# ── [9] Oracle execute_stored_procedure → GLD_ACH.INSERTPAYMENT ──────────────
# Section 5.3: ACH → Oracle rule (all 11 rows)
step9 = oracle_sp(
    9, ORACLE_ACH_AS,
    "GLD_ACH.INSERTPAYMENT",   # confirm exact schema.procedure name with SME
    {
        "REQUESTOR_ID":   "1",                   # Section 5.3 row 1 — hardcoded (Gap G7)
        "APP_ID":         trig("id"),             # Section 5.3 row 2
        "CUSTOMER_NAME":  trig("customerName"),   # Section 5.3 row 3
        "CUSTOMER_ID":    trig("customerID"),     # Section 5.3 row 4
        "SOURCE":         trig("sourceName"),     # Section 5.3 row 5
        "AMOUNT":         pay("amount"),           # Section 5.3 row 6
        "REFERENCE":      pay("invoiceReference"), # Section 5.3 row 7
        "PAYEE_ID":       pay("payee_id"),         # Section 5.3 row 8
        "PAYEE_NAME":     pay("payee_name"),        # Section 5.3 row 9
        "ACCOUNT_NUMBER": pay("payee_accountNumber"), # Section 5.3 row 10
        "ROUTING_NUMBER": pay("payee_routingNumber"),  # Section 5.3 row 11
    },
    title="ACH — Oracle GLD_ACH.INSERTPAYMENT (11 params, Section 5.3)",
)

# ── [8] elsif type == "ACH" — Rule 7: flat sibling, keyword="elsif" ───────────
step8 = {
    "number":  8,
    "keyword": "elsif",   # Rule 7 — NOT "elseif", NOT nested inside else
    "title":   "Route: payment.type == ACH",
    "uuid":    uid(),
    "toggleCfg": {},   # Rule 2
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

# ── [11] Logger — Default/Wire path (Section 6, Business Rule 1) ──────────────
step11 = {
    "number":   11,
    "keyword":  "action",
    "provider": "logger",
    "name":     "create_message",
    "as":       LOG_DEFAULT_AS,
    "title":    "Default/Wire — no external processor",
    "uuid":     uid(),
    "toggleCfg": {},   # Rule 2
    "input": {
        "message": "Default path: type=" + pay("type") + " id=" + pay("id"),
        "level": "info",
    },
}

# ── [10] else — Default / Wire / Other ────────────────────────────────────────
step10 = {
    "number":  10,
    "keyword": "else",
    "title":   "Route: Default (Wire / Other / unmapped type)",
    "uuid":    uid(),
    "block":   [step11],
}

# ── rescue log — [12] HTTP POST LogXMLRequest (per-payment error) ─────────────
step12 = http_action(
    12, LOG_RESCUE_AS,
    "RESCUE — LogXMLRequest (per-payment error, AppID=3)",
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {
        "AppID":              "3",
        "RequestIdentifier1": pay("id"),
        # wire error.message pill manually in Workato GUI
    },
)

# ── rescue — LAST in each.block (Rule 5) ──────────────────────────────────────
rescue = {
    "number":  13,
    "keyword": "rescue",
    "uuid":    uid(),
    "block":   [step12],
}

# ── [2] each: payment_loop (source = trigger.payments.parse_json) ─────────────
_payments_pill_json = json.dumps({
    "pill_type": "output",
    "provider":  "workato_service",
    "line":      TRIG_AS,
    "path":      ["request", "payments"],
}).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _payments_pill_json + "').parse_json}"

step2 = {
    "number":  2,
    "keyword": "each",        # Rule 14 — "each" confirmed working
    "as":      PAYEE_LOOP_AS,  # alias referenced in all pay() datapills
    "title":   "Repeat for each payment in payments.parse_json",
    "uuid":    uid(),
    "toggleCfg": {},   # Rule 2
    "input":   {"source": PAYMENTS_SOURCE},
    "block": [
        step3,    # if Check
        step8,    # elsif ACH     (Rule 7 flat sibling)
        step10,   # else Default
        rescue,   # LAST (Rule 5)
    ],
}

# ── catch log — [14] HTTP POST LogXMLRequest (outer recipe error) ─────────────
step14 = http_action(
    14, LOG_CATCH_AS,
    "CATCH — LogXMLRequest (outer recipe error, AppID=3)",
    MESSAGELOG_URL + "/GLDMessageLog/LogXMLRequest",
    {
        "AppID": "3",
        # wire error.message pill manually in Workato GUI
    },
)

# ── catch — LAST in try.block (Rule 6) ────────────────────────────────────────
catch = {
    "number":  15,
    "keyword": "catch",
    "uuid":    uid(),
    "input":   {"max_retry_count": "0"},
    "block":   [step14],
}

# ── [1] try — outer error wrapper ─────────────────────────────────────────────
step1 = {
    "number":  1,
    "keyword": "try",
    "title":   "Outer try — wraps all payment processing",
    "uuid":    uid(),
    "input":   {},
    "block": [
        step2,   # each loop
        catch,   # LAST (Rule 6)
    ],
}

# ── [16] send_reply — OUTSIDE try block (sibling in trigger.block) ────────────
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

# ═══════════════════════════════════════════════════════════════════════════════
# TRIGGER  (Rules 1, 4, 15)
# ═══════════════════════════════════════════════════════════════════════════════
request_schema = [
    {"name": "id",                "type": "string",  "optional": False,
     "control_type": "text",  "label": "Application ID (maps to LeaseNumber)"},
    {"name": "customerName",      "type": "string",  "optional": False,
     "control_type": "text",  "label": "Customer Name"},
    {"name": "customerID",        "type": "string",  "optional": False,
     "control_type": "text",  "label": "Customer ID"},
    {"name": "sourceName",        "type": "string",  "optional": True,
     "control_type": "text",  "label": "Source Name (maps to SOURCE in Oracle SP)"},
    {"name": "sourceSubCategory", "type": "string",  "optional": True,
     "control_type": "text",  "label": "Source Sub Category"},
    {"name": "salesRepName",      "type": "string",  "optional": True,
     "control_type": "text",  "label": "Sales Rep Name"},
    {"name": "payments",          "type": "string",  "optional": False,
     "control_type": "text",
     "label": (
         "Payments JSON array. Fields per item: id, type (Check|ACH|Wire|Other), "
         "amount, invoiceReference, comment, checkMemo, payee_id, payee_name, "
         "payee_address1, payee_address2, payee_city, payee_state_province, payee_zip, "
         "payee_phone, payee_fax, payee_contactName, payee_contactPhone, "
         "payee_routingNumber, payee_accountNumber"
     )},
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
    "parameters_schema": "",   # Rule 4 — required, must be empty string
    "input": {
        "service_name":        RECIPE_NAME,
        "request_schema_json": json.dumps(request_schema),
        "reply_schema_json":   json.dumps(reply_schema),
    },
    # Rule 15 — extended_output_schema for GUI pill tree
    "extended_output_schema": [
        {"name": f["name"], "type": f["type"],
         "control_type": f["control_type"], "label": f["label"]}
        for f in request_schema
    ],
    "block": [
        step1,      # try (contains each + catch)
        send_reply, # send_reply AFTER try (sibling, not nested inside try)
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG  (Rule 13: account_id is integer or null — never a string)
# ═══════════════════════════════════════════════════════════════════════════════
config = [
    {"keyword": "application", "provider": "workato_service",
     "account_id": None,            "skip_validation": False},
    {"keyword": "application", "provider": "http",
     "account_id": None,            "skip_validation": False},
    {"keyword": "application", "provider": "oracle",
     "account_id": ORACLE_CONN_ID,  "skip_validation": False},  # integer (Rule 13)
    {"keyword": "application", "provider": "logger",
     "account_id": None,            "skip_validation": False},
]

# ═══════════════════════════════════════════════════════════════════════════════
# PAYLOAD  (Rule 9: code and config MUST be JSON strings, not dicts)
# ═══════════════════════════════════════════════════════════════════════════════
payload = {
    "recipe": {
        "name":        RECIPE_NAME,
        "folder_id":   FOLDER_ID,          # string (Rule 9)
        "description": (
            "GLDFundingEngine20080714 -> Workato. "
            "Built via: Workato/Companion/SKILL.md (workato-integration), all 15 rules. "
            "Source: WebMethods/Analysis/MD/PackageAnalysis.md (Section 8, Recipe 1). "
            "Trigger: callable workato_service/receive_request (7 flat fields). "
            "Payment routing: Check (HTTP CheckWriter 3 steps) | "
            "ACH (Oracle GLD_ACH.INSERTPAYMENT 11 params) | Default (Logger). "
            "Per-payment rescue + outer catch -> GLDMessageLog."
        ),
        "code":   json.dumps(trigger),  # Rule 9 — JSON string
        "config": json.dumps(config),   # Rule 9 — JSON string
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# PUSH
# ═══════════════════════════════════════════════════════════════════════════════
if DRY_RUN:
    display = dict(payload["recipe"])
    display["code"]   = json.loads(display["code"])
    display["config"] = json.loads(display["config"])
    print("=== DRY RUN ===")
    print(json.dumps({"recipe": display}, indent=2))
else:
    print(f"Pushing '{RECIPE_NAME}' to MigrAIte_Training (folder {FOLDER_ID})...")
    result = api("POST", "/recipes", payload)

    rid  = result.get("id")
    name = result.get("name") or RECIPE_NAME
    if rid:
        print()
        print("SUCCESS")
        print(f"  Recipe ID : {rid}")
        print(f"  Name      : {name}")
        print(f"  URL       : https://app.workato.com/recipes/{rid}")
        print()
        print("GUI steps required:")
        print("  1. Create folder 'FundingEngine Companion' in Workato GUI")
        print("     (folder API is IP-whitelisted; folder must be created manually)")
        print("     Then move this recipe into that folder via Workato GUI.")
        print()
        print("  2. Create HTTP connection 'GLDFundingEngine_CheckWriter_Connection'")
        print(f"     Base URL: {CHECKWRITER_URL}  <- replace with real URL from SME")
        print("     Wire to steps: invokeGetUniquePayee (4), invokeAddNewPayee (6),")
        print("                    invokeCreateCheckRequest (7)")
        print()
        print("  3. Wire Oracle connection 'MIG_WM_GLD_Oracle_Connection' (ID 19657520)")
        print("     Step: Oracle insertPayment (9)")
        print("     SP name: GLD_ACH.INSERTPAYMENT  <- confirm with SME")
        print()
        print("  4. Create HTTP connection 'GLDFundingEngine_MessageLog_Connection'")
        print(f"     Base URL: {MESSAGELOG_URL}  <- replace with real URL from SME")
        print("     Wire to steps: rescue LogXMLRequest (12), catch LogXMLRequest (14)")
        print()
        print("  5. Wire error.message pill in rescue step 12 and catch step 14 (GUI only)")
    else:
        print("Unexpected response (no recipe ID):")
        print(json.dumps(result, indent=2)[:600])
