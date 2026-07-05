#!/usr/bin/env python3
"""
Push MIG_WM_GLDFundingEngine20080714 Workato recipe.

Implements WebMethods/Analysis/GLDFundingEngine20080714_Analysis.md exactly.

v2 fix: Workato silently wipes trigger input when input_fields_raw_schema
contains nested type:"object" with properties. Flattened:
  applicationInfo.* → applicationInfo_id, applicationInfo_customerName, ...
  payments[].payee.* → payments[].payee_name, payments[].payee_address1, ...

Trigger: callable_recipe (HTTP POST /process-funding-request)
  Inputs (flat):
    applicationInfo_id, applicationInfo_customerName, applicationInfo_customerID,
    applicationInfo_sourceName, applicationInfo_sourceSubCategory,
    applicationInfo_salesRepName
    payments[] (array of objects with flat payee_* fields)

Flow:
  Step 1: repeat_for_each over payments[]
    Step 2: IF payment.type == "Check"
      Step 3: HTTP POST invokeGetUniquePayee  (GLDExpressGateway CheckWriter)
      Step 4: IF payeeKey is empty
        Step 5: HTTP POST invokeAddNewPayee
      Step 6: HTTP POST invokeCreateCheckRequest
    Step 7: ELSE
      Step 8: IF payment.type == "ACH"
        Step 9: HTTP POST insertPayment  (GLD_ACHAdaptersServices)
      Step 10: ELSE (Other / Wire → Default, no external call)
    Step 11: rescue (per-payment catch)
      Step 12: HTTP POST GLDMessageLog:LogXMLRequest  (AppID=3)
"""
import sys, json, uuid, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from generators.generate_workato import _load_env_var
import urllib.request

tok = _load_env_var('WORKATO_API_TOKEN').strip()
FOLDER_ID = 31661117   # WebMethodsMigration

def uid(): return str(uuid.uuid4())


# ── Data pill builders ─────────────────────────────────────────────────────────

def _pill(provider, line, *path_parts):
    path = [{'path_element_type': 'current_item'} if p == '*' else p
            for p in path_parts]
    return json.dumps({'pill_type': 'output', 'provider': provider,
                       'line': line, 'path': path})

def dp(provider, line, *path_parts):
    return "#{_dp('" + _pill(provider, line, *path_parts).replace('"', '\\"') + "')}"

def raw(provider, line, *path_parts):
    return "_dp('" + _pill(provider, line, *path_parts).replace('"', '\\"') + "')"

# Trigger pills — flat schema, no nested applicationInfo object
def t(*path):      return dp('workato', 'callable_recipe', *path)
def t_raw(*path):  return raw('workato', 'callable_recipe', *path)

# Current payment item inside repeat_for_each (line alias = 'payment_loop')
def p(*path):      return dp('workato', 'payment_loop', '*', *path)
def p_raw(*path):  return raw('workato', 'payment_loop', '*', *path)

# Step output pills (HTTP connector responses)
def step_out(alias, *path): return dp('http', alias, *path)
def step_raw(alias, *path): return raw('http', alias, *path)


# ── HTTP action builder ────────────────────────────────────────────────────────

BASE_URL = 'https://webmethods-gateway.keybank.internal'
ACH_URL  = 'https://webmethods-ach.keybank.internal'
LOG_URL  = 'https://webmethods-log.keybank.internal'

def http_post(num, title, alias, url, payload_dict):
    return {
        'number':   num,
        'keyword':  'action',
        'provider': 'http',
        'name':     'post',
        'as':       alias,
        'title':    title,
        'uuid':     uid(),
        'dynamicPickListSelection': {},
        'toggleCfg': {},
        'input': {
            'url':          url,
            'content_type': 'application/json',
            'payload':      json.dumps(payload_dict),
        },
    }


# ── Step 3: invokeGetUniquePayee ───────────────────────────────────────────────
# Analysis §6.1 — PayeeInformation 11-field mapping
# payee_* pills map to flat fields in payments[] (flattened from payee object)
payee_info_payload = {
    'name':           p('payee_name'),
    'address1':       p('payee_address1'),
    'address2':       p('payee_address2'),
    'city':           p('payee_city'),
    'state_province': p('payee_state_province'),
    'zip':            p('payee_zip'),
    'phone':          p('payee_phone'),
    'fax':            p('payee_fax'),
    'contactName':    p('payee_contactName'),
    'contactPhone':   p('payee_contactPhone'),
    'Country':        'USA',   # static — GLDFundingEngine analysis §6.1
}

step3_get_unique_payee = http_post(
    3,
    'Action Check.1 — invokeGetUniquePayee (GLDExpressGateway CheckWriter)',
    'payee_search',
    BASE_URL + '/GLDExpressGateway/CheckWriter/invokeGetUniquePayee',
    payee_info_payload,
)


# ── Step 5: invokeAddNewPayee (runs only if payeeKey not found) ────────────────
step5_add_new_payee = http_post(
    5,
    'Action Check.2 — invokeAddNewPayee (create new payee in CheckWriter)',
    'add_payee',
    BASE_URL + '/GLDExpressGateway/CheckWriter/invokeAddNewPayee',
    payee_info_payload,   # same PayeeInformation mapping as GetUniquePayee
)

# Step 4: IF payeeKey is empty → run AddNewPayee
step4_if_no_payee = {
    'number':  4,
    'keyword': 'if',
    'title':   'Payee not found — create new payee (invokeAddNewPayee)',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'is_empty',
            'lhs':     step_out('payee_search', 'payeeKey'),
        }],
    },
    'block': [step5_add_new_payee],
}


# ── Step 6: invokeCreateCheckRequest ──────────────────────────────────────────
# Analysis §6.2 — CheckRequest 7-field mapping
# payeeKey: use GetUniquePayee result if present; fall back to AddNewPayee result
payee_key_combined = (
    "#{" + step_raw('payee_search', 'payeeKey') + ".presence || "
         + step_raw('add_payee',    'payeeKey') + "}"
)

check_request_payload = {
    'PayeeKey':    payee_key_combined,
    'Notes':       p('invoiceReference'),       # invoiceReference → Notes
    'Comments':    p('comment'),                # comment → Comments
    'CheckAmount': p('amount'),                 # amount → CheckAmount
    'Memo':        p('checkMemo'),              # checkMemo → Memo
    'PayeeName':   p('payee_name'),             # payee.name → PayeeName (flat)
    'LeaseNumber': t('applicationInfo_id'),     # applicationInfo.id → LeaseNumber (flat)
}

step6_create_check = http_post(
    6,
    'Action Check.3 — invokeCreateCheckRequest (GLDExpressGateway CheckWriter)',
    'create_check',
    BASE_URL + '/GLDExpressGateway/CheckWriter/invokeCreateCheckRequest',
    check_request_payload,
)


# ── Step 2: IF payment.type == "Check" ────────────────────────────────────────
step2_if_check = {
    'number':  2,
    'keyword': 'if',
    'title':   'Payment type is Check',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'equals',
            'lhs':     p('type'),
            'rhs':     'Check',
        }],
    },
    'block': [
        step3_get_unique_payee,
        step4_if_no_payee,
        step6_create_check,
    ],
}


# ── Step 9: insertPayment (ACH path) ──────────────────────────────────────────
# Analysis §6.3 — 11-field ACH mapping via GLD_ACHAdaptersServices
ach_insert_payload = {
    'APP_ID':         t('applicationInfo_id'),           # applicationInfo.id (flat)
    'CUSTOMER_NAME':  t('applicationInfo_customerName'), # applicationInfo.customerName (flat)
    'PAYEE_NAME':     p('payee_name'),                   # payment.payee.name (flat)
    'PAYEE_ID':       p('payee_id'),                     # payment.payee.id (flat)
    'REFERENCE':      p('invoiceReference'),
    'AMOUNT':         p('amount'),
    'ROUTING_NUMBER': p('payee_routingNumber'),          # payment.payee.routingNumber (flat)
    'ACCOUNT_NUMBER': p('payee_accountNumber'),          # payment.payee.accountNumber (flat)
    'CUSTOMER_ID':    t('applicationInfo_customerID'),   # applicationInfo.customerID (flat)
    'REQUESTOR_ID':   '1',                               # static — hardcoded in webMethods flow
    'SOURCE':         t('applicationInfo_sourceName'),   # applicationInfo.sourceName (flat)
}

step9_insert_ach = http_post(
    9,
    'Action ACH.1 — insertPayment (GLD_ACHAdaptersServices, 11 params)',
    'insert_ach',
    ACH_URL + '/GLD_ACHAdaptersServices/insertPayment',
    ach_insert_payload,
)


# ── Step 8: IF payment.type == "ACH" (nested inside ELSE of step 2) ───────────
step8_if_ach = {
    'number':  8,
    'keyword': 'if',
    'title':   'Payment type is ACH',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'equals',
            'lhs':     p('type'),
            'rhs':     'ACH',
        }],
    },
    'block': [step9_insert_ach],
}

# Step 10: ELSE — Default path (Other / Wire)
# Analysis Business Rules §7: Other/Wire → status="Default", no external call.
# A non-empty block prevents Workato from showing "Select an app and action".
step10_else_default = {
    'number':  10,
    'keyword': 'else',
    'uuid':    uid(),
    'title':   'Payment type is Other/Wire — Default (no processing)',
    'block':   [{
        'number':   10,
        'keyword':  'action',
        'provider': 'http',
        'name':     'post',
        'as':       'default_path_noop',
        'title':    '[Other/Wire] No external call — payment status = Default (see analysis §7)',
        'uuid':     uid(),
        'dynamicPickListSelection': {},
        'toggleCfg': {},
        'input': {
            'url':          'https://placeholder.internal/noop',
            'content_type': 'application/json',
            'payload':      json.dumps({
                'payment_id': p('id'),
                'status':     'Default',
                'reason':     'Payment type Other/Wire — not processed per business rules',
            }),
        },
    }],
}


# ── Step 7: ELSE (not Check) ───────────────────────────────────────────────────
step7_else_not_check = {
    'number':  7,
    'keyword': 'else',
    'uuid':    uid(),
    'block':   [step8_if_ach, step10_else_default],
}


# ── Step 12: Error log ─────────────────────────────────────────────────────────
# Analysis §3.1 shape #21 / §8: AppID=3, RequestIdentifier1 static,
# RequestIdentifier3 = payment.id (identifies failed payment)
error_log_payload = {
    'AppID':              '3',
    'RequestIdentifier1': 'ERROR - processing payment',
    'RequestIdentifier3': p('id'),
    'Request':            '[wire Workato error pill in GUI]',
    'RequestDoc':         {},
}

step12_log_error = http_post(
    12,
    'CATCH — Log payment error (GLDMessageLog:LogXMLRequest, AppID=3)',
    'log_payment_error',
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    error_log_payload,
)

# Step 11: rescue — per-payment catch (last sibling in repeat block)
# Analysis §8: catch logs error, loop continues to next payment
step11_rescue = {
    'number':  11,
    'keyword': 'rescue',
    'uuid':    uid(),
    'block':   [step12_log_error],
}


# ── Step 1: each loop over payments[] ─────────────────────────────────────────
# keyword:"each" is the correct Workato JSON format for a foreach loop.
# payments is a JSON string (scalar) in the trigger schema — apply .parse_json
# formula on the pill so the each loop gets an actual array to iterate over.
_payments_raw = _pill('workato', 'callable_recipe', 'payments').replace('"', '\\"')
payments_source = "#{_dp('" + _payments_raw + "').parse_json}"

step1_repeat = {
    'number': 1,
    'keyword': 'each',
    'as':     'payment_loop',
    'title':  'Repeat for each payment in request',
    'uuid':   uid(),
    'input': {
        'source': payments_source,  # callable_recipe.payments (JSON string) → parsed array
    },
    'block': [
        step2_if_check,
        step7_else_not_check,
        step11_rescue,    # last sibling — catches errors from any step in this iteration
    ],
}


# ── Trigger input schema (flat — no nested type:"object") ─────────────────────
# Workato silently wipes trigger input if input_fields_raw_schema contains
# nested type:"object" with properties (confirmed via API inspection).
# Flattened: applicationInfo.* → applicationInfo_* top-level fields.
#            payments[].payee.* → payments[].payee_* flat string fields.
input_fields = [
    # applicationInfo (6 fields, flattened from nested object)
    {'name': 'applicationInfo_id',               'type': 'string', 'optional': False, 'label': 'Application ID (1-100 chars)'},
    {'name': 'applicationInfo_customerName',     'type': 'string', 'optional': False, 'label': 'Customer Name (max 100 chars)'},
    {'name': 'applicationInfo_customerID',       'type': 'string', 'optional': False, 'label': 'Customer ID (integer 1-999999999999)'},
    {'name': 'applicationInfo_sourceName',       'type': 'string', 'optional': True,  'label': 'Source Name'},
    {'name': 'applicationInfo_sourceSubCategory','type': 'string', 'optional': True,  'label': 'Source Sub-Category'},
    {'name': 'applicationInfo_salesRepName',     'type': 'string', 'optional': True,  'label': 'Sales Rep Name'},
    # payments passed as JSON-encoded string — Workato input_fields_raw_schema
    # silently wipes trigger input for any type:"array" or type:"object" field.
    # Caller serializes payments as JSON string; loop source uses .parse_json.
    {'name': 'payments', 'type': 'string', 'optional': False,
     'label': 'Payments array (JSON string — each item: id, type, amount, invoiceReference, '
              'comment, checkMemo, status, glCode, glAmount, glDescription, '
              'payee_id, payee_type, payee_name, payee_address1, payee_address2, '
              'payee_city, payee_state_province, payee_zip, payee_phone, payee_fax, '
              'payee_contactName, payee_contactPhone, payee_routingNumber, payee_accountNumber)'},
]


# ── Trigger — callable recipe "Process Funding Request" ───────────────────────
trigger = {
    'number':   0,
    'keyword':  'trigger',
    'provider': 'workato',
    'name':     'callable_recipe',
    'as':       'callable_recipe',
    'uuid':     uid(),
    'dynamicPickListSelection': {},
    'toggleCfg': {},
    'input': {
        'http_method':             'post',
        'request_url_suffix':      '/process-funding-request',
        'response_type':           'dynamic',
        'input_fields_raw_schema': json.dumps(input_fields),
    },
    'block': [step1_repeat],
}

config = []   # no database connections — all steps use HTTP connector


# ── Push ───────────────────────────────────────────────────────────────────────
recipe_body = json.dumps({
    'recipe': {
        'name':      'Process Funding Request — MIG_WM_GLDFundingEngine20080714',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLDFundingEngine20080714 — webMethods IS 6.5 → Workato migration. '
            'Callable recipe (HTTP POST /process-funding-request). '
            'Input: 6 applicationInfo_* flat fields + payments[] array with flat payee_* fields. '
            'Repeat for each payment: '
            '  Check → invokeGetUniquePayee [→ invokeAddNewPayee if new] → invokeCreateCheckRequest; '
            '  ACH → insertPayment (GLD_ACHAdaptersServices, 11 params); '
            '  Other/Wire → Default (no external call). '
            'rescue per payment: logs to GLDMessageLog:LogXMLRequest (AppID=3). '
            'v2: flattened applicationInfo.* and payee.* — nested type:object in '
            'input_fields_raw_schema silently wipes trigger input in Workato.'
        ),
        'code':   json.dumps(trigger),
        'config': json.dumps(config),
    }
}).encode()

req = urllib.request.Request(
    'https://www.workato.com/api/recipes',
    data=recipe_body,
    method='POST',
    headers={
        'Authorization': 'Bearer ' + tok,
        'Content-Type':  'application/json',
    },
)

try:
    with urllib.request.urlopen(req, timeout=30) as r:
        raw_resp = r.read()
        resp = json.loads(raw_resp)
        recipe_id = resp.get('id')
        if recipe_id:
            print(f'SUCCESS — Recipe ID: {recipe_id}')
            print(f'URL: https://www.workato.com/recipes/{recipe_id}')
        else:
            print('PUSH RETURNED 200 BUT NO ID:')
            print(raw_resp[:1200].decode(errors='replace'))
except urllib.error.HTTPError as e:
    err_body = e.read()
    print(f'HTTP ERROR {e.code}')
    print(err_body[:1500].decode(errors='replace'))
except Exception as ex:
    print(f'EXCEPTION: {ex}')
