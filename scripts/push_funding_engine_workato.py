#!/usr/bin/env python3
"""
Push "FundingEngine" callable recipe to Workato.

Target folder : migrAIte_Training/webMethodsMigration (ID: 32050036)
Recipe name   : FundingEngine
Source        : WebMethods/GLDFundingEngine20080714 (processFundingRequest)

Reference docs:
  WebMethods/Analysis/MD/PackageAnalysis.md     (full analysis)
  WebMethods/MD/FundingEngine_WMToWorkato.md    (sequential build prompts)

Trigger schema (flat — Workato silently wipes nested type:object fields):
  id, customerName, customerID, sourceName, sourceSubCategory, salesRepName,
  payments (JSON string — each loop calls .parse_json at runtime)

Structure:
  0: trigger  workato_service/receive_request — "FundingEngine"
    1: try
      2: each loop — payment_loop (source: trigger.payments.parse_json)
        3:  if payment.type == "Check"
          4:    HTTP POST — invokeGetUniquePayee    (GLDExpressGateway)
          5:    if payeeKey is_empty
            6:      HTTP POST — invokeAddNewPayee   (register new payee)
          7:    HTTP POST — invokeCreateCheckRequest
        8:  elsif payment.type == "ACH"
          9:    HTTP POST — insertPayment           (ACH, 11 params)
        10: else (Other / Wire → Default)
          11:   Log placeholder                     (no external call)
        rescue (per-payment — last sibling in each.block):
          12:   HTTP POST — LogXMLRequest           (GLDMessageLog, AppID=3)
      catch (outer — last sibling in try.block):
        13:   HTTP POST — LogXMLRequest             (GLDMessageLog, AppID=3)
    14: workato_service/send_reply

Placeholder URLs (replace with real SME endpoints):
  GLDExpressGateway : https://webmethods-gateway.keybank.internal
  GLD_ACHAdapters   : https://webmethods-ach.keybank.internal
  GLDMessageLog     : https://webmethods-log.keybank.internal
"""
import sys, json, uuid, os, urllib.request, urllib.error

PROJECT_ROOT = r'C:\Users\manis\OneDrive\Desktop\iPaaS-Migration'
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')


def load_env(path):
    tok = None
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('WORKATO_API_TOKEN='):
                    tok = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    except Exception:
        pass
    return tok or os.environ.get('WORKATO_API_TOKEN', '')


tok = load_env(ENV_PATH)
if not tok:
    print('ERROR: WORKATO_API_TOKEN not found in .env or environment'); sys.exit(1)

HEADERS   = {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}
BASE      = 'https://www.workato.com/api'
FOLDER_ID = 32159265   # migrAIte_Training/webMethodsMigration (created 2026-07-30)


def uid():
    return str(uuid.uuid4())


def api_post(path, body_dict):
    data = json.dumps(body_dict).encode()
    req  = urllib.request.Request(BASE + path, data=data, method='POST', headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, (e.code, e.read().decode(errors='replace'))


# ── Step-alias constants ────────────────────────────────────────────────────────
TRIG_AS       = uid()[:8]   # trigger
GET_PAYEE_AS  = uid()[:8]   # invokeGetUniquePayee
ADD_PAYEE_AS  = uid()[:8]   # invokeAddNewPayee
CREATE_CHK_AS = uid()[:8]   # invokeCreateCheckRequest
INS_ACH_AS    = uid()[:8]   # insertPayment (ACH)
LOG_ERR_AS    = uid()[:8]   # per-payment rescue log
OUTER_ERR_AS  = uid()[:8]   # outer catch log
REPLY_AS      = uid()[:8]   # send_reply


# ── Datapill helpers ────────────────────────────────────────────────────────────

def _pill_json(provider, line, *path_parts):
    path = [{'path_element_type': 'current_item'} if p == '*' else p
            for p in path_parts]
    return json.dumps({'pill_type': 'output', 'provider': provider,
                       'line': line, 'path': path}).replace('"', '\\"')


def dp(provider, line, *path_parts):
    return "#{_dp('" + _pill_json(provider, line, *path_parts) + "')}"


def raw_dp(provider, line, *path_parts):
    return "_dp('" + _pill_json(provider, line, *path_parts) + "')"


def trig(field):
    """Trigger input field — clean flat names (id, customerName, …)."""
    return dp('workato_service', TRIG_AS, 'request', field)


def pay(field):
    """Current payment item field inside the each loop."""
    return dp('workato', 'payment_loop', '*', field)


def http_out(alias, field):
    return dp('http', alias, field)


def http_raw(alias, field):
    return raw_dp('http', alias, field)


# ── Placeholder base URLs ────────────────────────────────────────────────────────
GW_URL  = 'https://webmethods-gateway.keybank.internal'
ACH_URL = 'https://webmethods-ach.keybank.internal'
LOG_URL = 'https://webmethods-log.keybank.internal'


# ── HTTP POST builder ───────────────────────────────────────────────────────────

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


# ── Payee info payload (shared by GetUniquePayee + AddNewPayee) ─────────────────
# Flat payee_* field names matching the each-loop payment item schema.
PAYEE_INFO = {
    'name':           pay('payee_name'),
    'address1':       pay('payee_address1'),
    'address2':       pay('payee_address2'),
    'city':           pay('payee_city'),
    'state_province': pay('payee_state_province'),
    'zip':            pay('payee_zip'),
    'phone':          pay('payee_phone'),
    'fax':            pay('payee_fax'),
    'contactName':    pay('payee_contactName'),
    'contactPhone':   pay('payee_contactPhone'),
    'Country':        'USA',   # static — hardcoded in webMethods source
}


# ── Step 4: invokeGetUniquePayee ────────────────────────────────────────────────
step4_get_payee = http_post(
    4,
    'Check.1 — invokeGetUniquePayee (GLDExpressGateway CheckWriter)',
    GET_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeGetUniquePayee',
    PAYEE_INFO,
)


# ── Step 6: invokeAddNewPayee ───────────────────────────────────────────────────
step6_add_payee = http_post(
    6,
    'Check.2 — invokeAddNewPayee (register new payee in CheckWriter)',
    ADD_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeAddNewPayee',
    PAYEE_INFO,
)

# Step 5: if payeeKey is empty → run AddNewPayee
step5_if_no_payee = {
    'number':  5,
    'keyword': 'if',
    'title':   'Payee not found — create new payee',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'is_empty',
            'lhs':     http_out(GET_PAYEE_AS, 'payeeKey'),
            'uuid':    uid(),
        }],
    },
    'block': [step6_add_payee],
}


# ── Step 7: invokeCreateCheckRequest ───────────────────────────────────────────
# payeeKey: GetUniquePayee result if present, else AddNewPayee result.
PAYEE_KEY = (
    "#{" + http_raw(GET_PAYEE_AS, 'payeeKey') + ".presence || "
          + http_raw(ADD_PAYEE_AS, 'payeeKey') + "}"
)

step7_create_check = http_post(
    7,
    'Check.3 — invokeCreateCheckRequest (GLDExpressGateway CheckWriter)',
    CREATE_CHK_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeCreateCheckRequest',
    {
        'PayeeKey':    PAYEE_KEY,
        'Notes':       pay('invoiceReference'),
        'Comments':    pay('comment'),
        'CheckAmount': pay('amount'),
        'Memo':        pay('checkMemo'),
        'PayeeName':   pay('payee_name'),
        'LeaseNumber': trig('id'),   # applicationInfo.id → LeaseNumber
    },
)


# ── Step 3: if payment.type == "Check" ─────────────────────────────────────────
step3_if_check = {
    'number':  3,
    'keyword': 'if',
    'title':   'Payment type is Check',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'equals',
            'lhs':     pay('type'),
            'rhs':     'Check',
            'uuid':    uid(),
        }],
    },
    'block': [step4_get_payee, step5_if_no_payee, step7_create_check],
}


# ── Step 9: insertPayment (ACH path) ───────────────────────────────────────────
step9_insert_ach = http_post(
    9,
    'ACH.1 — insertPayment (GLD_ACHAdaptersServices, 11 params)',
    INS_ACH_AS,
    ACH_URL + '/GLD_ACHAdaptersServices/insertPayment',
    {
        'APP_ID':         trig('id'),
        'CUSTOMER_NAME':  trig('customerName'),
        'PAYEE_NAME':     pay('payee_name'),
        'PAYEE_ID':       pay('payee_id'),
        'REFERENCE':      pay('invoiceReference'),
        'AMOUNT':         pay('amount'),
        'ROUTING_NUMBER': pay('payee_routingNumber'),
        'ACCOUNT_NUMBER': pay('payee_accountNumber'),
        'CUSTOMER_ID':    trig('customerID'),
        'REQUESTOR_ID':   '1',   # static — hardcoded in webMethods source
        'SOURCE':         trig('sourceName'),
    },
)


# ── Step 8: elsif payment.type == "ACH" ────────────────────────────────────────
step8_if_ach = {
    'number':  8,
    'keyword': 'elsif',
    'title':   'Payment type is ACH',
    'uuid':    uid(),
    'input': {
        'type':    'compound',
        'operand': 'and',
        'conditions': [{
            'operand': 'equals',
            'lhs':     pay('type'),
            'rhs':     'ACH',
            'uuid':    uid(),
        }],
    },
    'block': [step9_insert_ach],
}


# ── Step 11: noop log for Other/Wire (Default path) ────────────────────────────
step11_default_log = {
    'number':   11,
    'keyword':  'action',
    'provider': 'logger',
    'name':     'create_message',
    'as':       uid()[:8],
    'title':    'Default — no external call (Other/Wire payment type)',
    'uuid':     uid(),
    'dynamicPickListSelection': {},
    'toggleCfg': {},
    'input': {
        'message': (
            'Payment ' + pay('id') + ' type ' + pay('type') +
            ' — Default path (no external processor per GLDFundingEngine business rules)'
        ),
        'level': 'info',
    },
}


# ── Step 10: else (Other/Wire → Default) ───────────────────────────────────────
step10_else_default = {
    'number':  10,
    'keyword': 'else',
    'title':   'Payment type Other/Wire — Default',
    'uuid':    uid(),
    'block':   [step11_default_log],
}


# ── Step 12: rescue — per-payment error log ─────────────────────────────────────
step12_rescue_log = http_post(
    12,
    'RESCUE — Log payment error (GLDMessageLog:LogXMLRequest, AppID=3)',
    LOG_ERR_AS,
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    {
        'AppID':              '3',
        'RequestIdentifier1': 'ERROR - processing payment',
        'PaymentID':          pay('id'),
        'PaymentType':        pay('type'),
        'ApplicationID':      trig('id'),
        'ErrorMessage':       '[wire error.message pill in Workato GUI]',
    },
)

step_rescue = {
    'number':  14,   # rescue sits last in each.block, numbered after elsif/else
    'keyword': 'rescue',
    'uuid':    uid(),
    'block':   [step12_rescue_log],
}


# ── Step 2: each loop over payments ────────────────────────────────────────────
_pay_pill = json.dumps({
    'pill_type': 'output',
    'provider':  'workato_service',
    'line':      TRIG_AS,
    'path':      ['request', 'payments'],
}).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill + "').parse_json}"

step2_each = {
    'number':  2,
    'keyword': 'each',
    'as':      'payment_loop',
    'title':   'Repeat for each payment',
    'uuid':    uid(),
    'input':   {'source': PAYMENTS_SOURCE},
    'block':   [step3_if_check, step8_if_ach, step10_else_default, step_rescue],
}


# ── Step 13: outer catch error log ─────────────────────────────────────────────
step13_outer_err = http_post(
    13,
    'OUTER CATCH — Log system error (GLDMessageLog, AppID=3)',
    OUTER_ERR_AS,
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    {
        'AppID':              '3',
        'RequestIdentifier1': 'SYSTEM_ERROR',
        'ApplicationID':      trig('id'),
        'ErrorMessage':       '[wire error.message pill in Workato GUI]',
    },
)

step_catch = {
    'number':  15,
    'keyword': 'catch',
    'uuid':    uid(),
    'input':   {'max_retry_count': '0', 'retry_interval': '2'},
    'block':   [step13_outer_err],
}


# ── Step 14: send_reply ─────────────────────────────────────────────────────────
step14_send_reply = {
    'number':   16,
    'keyword':  'action',
    'provider': 'workato_service',
    'name':     'send_reply',
    'as':        REPLY_AS,
    'uuid':      uid(),
    'dynamicPickListSelection': {},
    'toggleCfg': {'reply.status': True},
    'input': {
        'reply_type': 'success',
        'reply': {'status': 'PAYMENTS_PROCESSED'},
    },
    'extended_input_schema': [{
        'label': 'Reply',
        'name':  'reply',
        'type':  'object',
        'properties': [{
            'control_type': 'text',
            'label':        'Status',
            'name':         'status',
            'type':         'string',
            'optional':     False,
        }],
    }],
}


# ── Step 1: outer try block ─────────────────────────────────────────────────────
step1_try = {
    'number':  1,
    'keyword': 'try',
    'input':   {},
    'uuid':    uid(),
    'block':   [step2_each, step14_send_reply, step_catch],
}


# ── Trigger schema — flat (7 fields) ───────────────────────────────────────────
req_schema = [
    {'name': 'id',               'type': 'string', 'optional': False,
     'label': 'Application ID (1-100 chars, maps to LeaseNumber in CheckWriter)'},
    {'name': 'customerName',     'type': 'string', 'optional': False,
     'label': 'Customer Name (max 100 chars)'},
    {'name': 'customerID',       'type': 'string', 'optional': False,
     'label': 'Customer ID (integer 1-999999999999, sent as string)'},
    {'name': 'sourceName',       'type': 'string', 'optional': True,
     'label': 'Source Name (maps to SOURCE in ACH insertPayment)'},
    {'name': 'sourceSubCategory','type': 'string', 'optional': True,
     'label': 'Source Sub Category'},
    {'name': 'salesRepName',     'type': 'string', 'optional': True,
     'label': 'Sales Rep Name'},
    {'name': 'payments',         'type': 'string', 'optional': False,
     'label': (
         'Payments array as JSON string. Each item: '
         'id, type (Check|ACH|Other|Wire), amount, invoiceReference, comment, '
         'checkMemo, status, glCode, glAmount, glDescription, '
         'payee_id, payee_type, payee_name, payee_address1, payee_address2, '
         'payee_city, payee_state_province, payee_zip, payee_phone, payee_fax, '
         'payee_contactName, payee_contactPhone, payee_routingNumber, payee_accountNumber'
     )},
]

reply_schema = [
    {'name': 'status', 'type': 'string', 'optional': False,
     'label': 'Processing status (PAYMENTS_PROCESSED)'},
]


# ── Trigger (step 0) ────────────────────────────────────────────────────────────
code = {
    'number':   0,
    'keyword':  'trigger',
    'provider': 'workato_service',
    'name':     'receive_request',
    'as':       TRIG_AS,
    'uuid':     uid(),
    'dynamicPickListSelection': {},
    'toggleCfg': {},
    'input': {
        'service_name':        'FundingEngine',
        'request_schema_json': json.dumps(req_schema),
        'reply_schema_json':   json.dumps(reply_schema),
    },
    'block': [step1_try],
}

config = [
    {'keyword': 'application', 'provider': 'workato_service',
     'account_id': None, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'http',
     'account_id': None, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'logger',
     'account_id': None, 'skip_validation': False},
]


# ── Push ────────────────────────────────────────────────────────────────────────
print(f'Pushing FundingEngine to Workato folder ID: {FOLDER_ID} (migrAIte_Training/webMethodsMigration)...')
resp, err = api_post('/recipes', {
    'recipe': {
        'name':      'FundingEngine',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLDFundingEngine20080714 — webMethods IS 6.5 → Workato. '
            'Callable recipe: HTTP POST /FundingEngine. '
            'Trigger: 7 flat fields (id, customerName, customerID, sourceName, '
            'sourceSubCategory, salesRepName, payments as JSON string). '
            'Flow: outer try → each over payments.parse_json → '
            'Check: invokeGetUniquePayee [→ invokeAddNewPayee if new] → invokeCreateCheckRequest; '
            'ACH: insertPayment (11 params, REQUESTOR_ID=1 static); '
            'Other/Wire: Default log (no external call); '
            'rescue per payment: GLDMessageLog:LogXMLRequest (AppID=3). '
            '→ send_reply(status=PAYMENTS_PROCESSED). outer catch: LogXMLRequest. '
            'Placeholder URLs — wire real endpoints from SME in GUI. '
            'Source: WebMethods/Analysis/MD/PackageAnalysis.md + '
            'WebMethods/MD/FundingEngine_WMToWorkato.md'
        ),
        'code':   json.dumps(code),
        'config': json.dumps(config),
    }
})

if err:
    print(f'\nHTTP ERROR {err[0]}:')
    print(err[1][:2000])
else:
    recipe_id = resp.get('id')
    if recipe_id:
        print(f'\nSUCCESS — Recipe ID: {recipe_id}')
        print(f'URL: https://app.workato.com/recipes/{recipe_id}')
        print('\nRemaining GUI steps:')
        print('  1. Create HTTP connections in Workato GUI:')
        print(f'     - GLDFundingEngine_CheckWriter_Connection ({GW_URL})')
        print(f'     - GLDFundingEngine_ACH_Connection ({ACH_URL})')
        print(f'     - GLDFundingEngine_MessageLog_Connection ({LOG_URL})')
        print('  2. Wire each HTTP step to its connection in the recipe editor')
        print('  3. Steps 12 + 13 (error logs): replace error.message placeholder with error.message pill')
        print('  4. Obtain real base URLs for all three endpoints from SME')
    else:
        print('\nPush returned 200 but no recipe ID:')
        print(json.dumps(resp, indent=2)[:800])
