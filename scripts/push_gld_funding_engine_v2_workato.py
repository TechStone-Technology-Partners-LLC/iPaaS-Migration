#!/usr/bin/env python3
"""
Push MIG_WM_GLDFundingEngine_processFundingRequest to Workato.

Target folder : migrAIte_Training (ID: 31835141)
Recipe name   : MIG_WM_GLDFundingEngine_processFundingRequest

Source analysis:
  WebMethods/MD/GLDFundingEngine_PackageAnalysis.md  (Phase 1)
  WebMethods/MD/GLDFundingEngine_WMToWorkato.md       (Phase 2 prompts)

Structure:
  Trigger: workato_service/receive_request (callable recipe — HTTP POST)
    Input:  6 flat applicationInfo_* fields + payments (JSON string)
    Reply:  status (string)

  1: try (outer error wrapper)
    2: HTTP POST — GLDMessageLog:LogXMLRequest  (log incoming request, AppID=3)
    3: each loop — repeat for each payment (source: trigger.payments.parse_json)
      4:  if payment.type == "Check"
        5:    HTTP POST — invokeGetUniquePayee    (GLDExpressGateway CheckWriter)
        6:    if payeeKey is_empty
          7:      HTTP POST — invokeAddNewPayee   (register new payee)
        8:    HTTP POST — invokeCreateCheckRequest
      9:  else (not Check)
        10:   if payment.type == "ACH"
          11:     HTTP POST — insertPayment       (GLD_ACHAdaptersServices, 11 params)
        12:   else (Other / Wire → Default)
          13:     noop placeholder                (business rule: no external call)
      14: rescue (per-payment — loop continues after catch)
        15:   HTTP POST — GLDMessageLog:LogXMLRequest  (log payment error, AppID=3)
    16: HTTP POST — GLDMessageLog:LogXMLResponse (log outgoing response, AppID=3)
    17: workato_service/send_reply               (return status to caller)
    18: catch (outer — catches any unhandled recipe-level error)
      19:   HTTP POST — GLDMessageLog:LogXMLRequest  (log system error)

Placeholder URLs (all must be replaced with real endpoints from SME):
  GLDExpressGateway : https://webmethods-gateway.keybank.internal
  GLD_ACHAdapters   : https://webmethods-ach.keybank.internal
  GLDMessageLog     : https://webmethods-log.keybank.internal

NOTE: payments field is a JSON string in the trigger schema.
Workato's workato_service/receive_request silently wipes array/object fields
when passed in request_schema_json as type:array.  Passing as a string and
applying .parse_json in the each loop source is the confirmed workaround.
"""
import sys, json, uuid, os, urllib.request, urllib.error

PROJECT_ROOT = r'C:\Users\manis\OneDrive\Desktop\iPaaS-Migration'
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')


def load_env(path):
    """Read WORKATO_API_TOKEN from .env file or environment variable."""
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

HEADERS    = {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}
BASE       = 'https://www.workato.com/api'
FOLDER_ID  = 31835141   # migrAIte_Training


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
TRIG_AS       = uid()[:8]   # trigger — used to build all trigger datapills
LOG_REQ_AS    = uid()[:8]   # step 2:  log request
GET_PAYEE_AS  = uid()[:8]   # step 5:  invokeGetUniquePayee
ADD_PAYEE_AS  = uid()[:8]   # step 7:  invokeAddNewPayee
CREATE_CHK_AS = uid()[:8]   # step 8:  invokeCreateCheckRequest
INS_ACH_AS    = uid()[:8]   # step 11: insertPayment
NOOP_AS       = uid()[:8]   # step 13: noop placeholder (Other/Wire)
LOG_ERR_AS    = uid()[:8]   # step 15: per-payment error log
LOG_RESP_AS   = uid()[:8]   # step 16: log response
REPLY_AS      = uid()[:8]   # step 17: send_reply
OUTER_ERR_AS  = uid()[:8]   # step 19: outer catch error log
CATCH_AS      = uid()[:8]   # step 18: outer catch block


# ── Data pill builders ──────────────────────────────────────────────────────────

def _pill_json(provider, line, *path_parts):
    """Build the raw pill dict as a JSON string (with quotes escaped)."""
    path = [{'path_element_type': 'current_item'} if p == '*' else p
            for p in path_parts]
    return json.dumps({'pill_type': 'output', 'provider': provider,
                       'line': line, 'path': path}).replace('"', '\\"')


def dp(provider, line, *path_parts):
    """Return a full Workato datapill interpolation: #{_dp('...')}."""
    return "#{_dp('" + _pill_json(provider, line, *path_parts) + "')}"


def raw_dp(provider, line, *path_parts):
    """Return just _dp('...') — for embedding inside formula interpolations."""
    return "_dp('" + _pill_json(provider, line, *path_parts) + "')"


# ── Shorthand pill helpers ──────────────────────────────────────────────────────

def trig(field):
    """Datapill for a top-level trigger input field (workato_service provider)."""
    return dp('workato_service', TRIG_AS, 'request', field)


def pay(field):
    """Datapill for a field on the current payment item inside the each loop."""
    return dp('workato', 'payment_loop', '*', field)


def http_out(alias, field):
    """Datapill for a top-level field in an HTTP step's response body."""
    return dp('http', alias, field)


def http_raw(alias, field):
    """Raw _dp(...) for an HTTP response field — use inside formula strings."""
    return raw_dp('http', alias, field)


# ── Placeholder URLs (replace with real endpoints from SME) ────────────────────
GW_URL  = 'https://webmethods-gateway.keybank.internal'   # GLDExpressGateway
ACH_URL = 'https://webmethods-ach.keybank.internal'       # GLD_ACHAdaptersServices
LOG_URL = 'https://webmethods-log.keybank.internal'       # GLDMessageLog


# ── Generic HTTP POST action builder ──────────────────────────────────────────

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


# ── STEP 2: Log incoming funding request ───────────────────────────────────────
step2_log_req = http_post(
    2,
    'Log funding request — GLDMessageLog:LogXMLRequest (AppID=3, FE)',
    LOG_REQ_AS,
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    {
        'AppID':              '3',
        'RequestIdentifier1': 'FE',
        'ApplicationID':      trig('applicationInfo_id'),
        'CustomerName':       trig('applicationInfo_customerName'),
    },
)


# ── STEP 5: invokeGetUniquePayee ───────────────────────────────────────────────
# Analysis §6.1 — PayeeInformation 11-field mapping (flat payee_* fields)
PAYEE_INFO_PAYLOAD = {
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
    'Country':        'USA',   # static — analysis §6.1
}

step5_get_payee = http_post(
    5,
    'Check.1 — invokeGetUniquePayee (GLDExpressGateway CheckWriter)',
    GET_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeGetUniquePayee',
    PAYEE_INFO_PAYLOAD,
)


# ── STEP 7: invokeAddNewPayee (only if payeeKey is empty) ─────────────────────
step7_add_payee = http_post(
    7,
    'Check.2 — invokeAddNewPayee (register new payee in CheckWriter)',
    ADD_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeAddNewPayee',
    PAYEE_INFO_PAYLOAD,   # same 11-field mapping
)

# STEP 6: if payeeKey is empty → run AddNewPayee
step6_if_no_payee = {
    'number':  6,
    'keyword': 'if',
    'title':   'Payee not found — create new payee (invokeAddNewPayee)',
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
    'block': [step7_add_payee],
}


# ── STEP 8: invokeCreateCheckRequest ──────────────────────────────────────────
# Analysis §6.2 — CheckRequest 7-field mapping
# payeeKey: use GetUniquePayee result if present, fall back to AddNewPayee result
PAYEE_KEY = (
    "#{" + http_raw(GET_PAYEE_AS, 'payeeKey') + ".presence || "
          + http_raw(ADD_PAYEE_AS, 'payeeKey') + "}"
)

step8_create_check = http_post(
    8,
    'Check.3 — invokeCreateCheckRequest (GLDExpressGateway CheckWriter)',
    CREATE_CHK_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeCreateCheckRequest',
    {
        'PayeeKey':    PAYEE_KEY,
        'Notes':       pay('invoiceReference'),   # invoiceReference → Notes
        'Comments':    pay('comment'),            # comment → Comments
        'CheckAmount': pay('amount'),             # amount → CheckAmount
        'Memo':        pay('checkMemo'),          # checkMemo → Memo
        'PayeeName':   pay('payee_name'),         # payee.name → PayeeName (flat)
        'LeaseNumber': trig('applicationInfo_id'), # applicationInfo.id → LeaseNumber
    },
)


# ── STEP 4: if payment.type == "Check" ────────────────────────────────────────
step4_if_check = {
    'number':  4,
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
    'block': [step5_get_payee, step6_if_no_payee, step8_create_check],
}


# ── STEP 11: insertPayment (ACH path) ─────────────────────────────────────────
# Analysis §6.3 — 11-field ACH mapping (flat payee_* fields, REQUESTOR_ID static)
step11_insert_ach = http_post(
    11,
    'ACH.1 — insertPayment (GLD_ACHAdaptersServices, 11 params)',
    INS_ACH_AS,
    ACH_URL + '/GLD_ACHAdaptersServices/insertPayment',
    {
        'APP_ID':         trig('applicationInfo_id'),           # applicationInfo.id
        'CUSTOMER_NAME':  trig('applicationInfo_customerName'), # applicationInfo.customerName
        'PAYEE_NAME':     pay('payee_name'),                    # payment.payee.name
        'PAYEE_ID':       pay('payee_id'),                      # payment.payee.id
        'REFERENCE':      pay('invoiceReference'),
        'AMOUNT':         pay('amount'),
        'ROUTING_NUMBER': pay('payee_routingNumber'),           # payment.payee.routingNumber
        'ACCOUNT_NUMBER': pay('payee_accountNumber'),           # payment.payee.accountNumber
        'CUSTOMER_ID':    trig('applicationInfo_customerID'),   # applicationInfo.customerID
        'REQUESTOR_ID':   '1',                                  # static — hardcoded in webMethods
        'SOURCE':         trig('applicationInfo_sourceName'),   # applicationInfo.sourceName
    },
)


# ── STEP 10: if payment.type == "ACH" ─────────────────────────────────────────
step10_if_ach = {
    'number':  10,
    'keyword': 'if',
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
    'block': [step11_insert_ach],
}


# ── STEP 12 / 13: else (Other / Wire → Default) ───────────────────────────────
# Analysis §7: Other and Wire types are not processed — status="Default".
# A non-empty block is required to prevent Workato showing "Select an app".
step13_noop = http_post(
    13,
    '[Other/Wire] Default — no external call (analysis §7 business rule)',
    NOOP_AS,
    'https://placeholder.internal/noop',
    {
        'payment_id': pay('id'),
        'status':     'Default',
        'note':       'Other/Wire payment type — not processed per GLDFundingEngine business rules',
    },
)

step12_else_default = {
    'number':  12,
    'keyword': 'else',
    'title':   'Payment type Other/Wire — Default (no external call)',
    'uuid':    uid(),
    'block':   [step13_noop],
}


# ── STEP 9: else (not Check path) — contains ACH if + default else ────────────
step9_else_not_check = {
    'number':  9,
    'keyword': 'else',
    'title':   'Payment type is not Check',
    'uuid':    uid(),
    'block':   [step10_if_ach, step12_else_default],
}


# ── STEP 15: per-payment error log ────────────────────────────────────────────
step15_log_err = http_post(
    15,
    'RESCUE — Log payment error (GLDMessageLog:LogXMLRequest, AppID=3)',
    LOG_ERR_AS,
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    {
        'AppID':              '3',
        'RequestIdentifier1': 'ERROR - processing payment',
        'PaymentID':          pay('id'),
        'ErrorMessage':       '[wire Workato error.message pill in GUI]',
        'ErrorType':          '[wire Workato error.error_type pill in GUI]',
    },
)


# ── STEP 14: rescue (per-payment — loop continues to next payment) ─────────────
# Matches webMethods CATCH inside LOOP: EXIT-ON="DONE" catches per-payment failures.
step14_rescue = {
    'number':  14,
    'keyword': 'rescue',
    'uuid':    uid(),
    'block':   [step15_log_err],
}


# ── STEP 3: each loop over payments[] ─────────────────────────────────────────
# payments is a JSON string in the trigger schema — apply .parse_json so the
# each loop receives an actual array.  See module docstring for the rationale.
_pay_pill = json.dumps({
    'pill_type': 'output',
    'provider':  'workato_service',
    'line':      TRIG_AS,
    'path':      ['request', 'payments'],
}).replace('"', '\\"')
PAYMENTS_SOURCE = "#{_dp('" + _pay_pill + "').parse_json}"

step3_each = {
    'number':  3,
    'keyword': 'each',
    'as':      'payment_loop',
    'title':   'Repeat for each payment in request',
    'uuid':    uid(),
    'input':   {'source': PAYMENTS_SOURCE},
    'block':   [step4_if_check, step9_else_not_check, step14_rescue],
}


# ── STEP 16: Log outgoing response ────────────────────────────────────────────
step16_log_resp = http_post(
    16,
    'Log funding response — GLDMessageLog:LogXMLResponse (AppID=3, FE)',
    LOG_RESP_AS,
    LOG_URL + '/GLDMessageLog/LogXMLResponse',
    {
        'AppID':               '3',
        'ResponseIdentifier4': 'FE',
        'ApplicationID':       trig('applicationInfo_id'),
        'Status':              'PAYMENTS_PROCESSED',
    },
)


# ── STEP 17: send_reply ────────────────────────────────────────────────────────
step17_send_reply = {
    'number':   17,
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
    'extended_input_schema': [
        {
            'label': 'Reply',
            'name':  'reply',
            'type':  'object',
            'properties': [
                {
                    'control_type': 'text',
                    'label':        'Status',
                    'name':         'status',
                    'type':         'string',
                    'optional':     False,
                }
            ],
        }
    ],
}


# ── STEP 19: outer catch error log ────────────────────────────────────────────
step19_outer_err = http_post(
    19,
    'OUTER CATCH — Log system error (GLDMessageLog, AppID=3)',
    OUTER_ERR_AS,
    LOG_URL + '/GLDMessageLog/LogXMLRequest',
    {
        'AppID':              '3',
        'RequestIdentifier1': 'SYSTEM_ERROR',
        'ApplicationID':      trig('applicationInfo_id'),
        'ErrorMessage':       '[wire Workato error.message pill in GUI]',
    },
)


# ── STEP 18: outer catch block ────────────────────────────────────────────────
step18_catch = {
    'number':  18,
    'keyword': 'catch',
    'as':      CATCH_AS,
    'uuid':    uid(),
    'input':   {'max_retry_count': '0', 'retry_interval': '2'},
    'block':   [step19_outer_err],
}


# ── STEP 1: outer try block ───────────────────────────────────────────────────
step1_try = {
    'number':  1,
    'keyword': 'try',
    'input':   {},
    'uuid':    uid(),
    'block': [
        step2_log_req,
        step3_each,
        step16_log_resp,
        step17_send_reply,
        step18_catch,     # catch must be last sibling in try.block
    ],
}


# ── Trigger input / reply schema ──────────────────────────────────────────────
# Flat schema — see docstring for why payments is a string (not array).
req_schema = [
    {'name': 'applicationInfo_id',
     'type': 'string', 'optional': False,
     'label': 'Application ID (1-100 chars, maps to LeaseNumber in CheckWriter)'},
    {'name': 'applicationInfo_customerName',
     'type': 'string', 'optional': False,
     'label': 'Customer Name (max 100 chars)'},
    {'name': 'applicationInfo_customerID',
     'type': 'string', 'optional': False,
     'label': 'Customer ID (integer 1-999999999999, sent as string for Workato compatibility)'},
    {'name': 'applicationInfo_sourceName',
     'type': 'string', 'optional': True,
     'label': 'Source Name (maps to SOURCE in ACH insertPayment)'},
    {'name': 'applicationInfo_sourceSubCategory',
     'type': 'string', 'optional': True,
     'label': 'Source Sub-Category'},
    {'name': 'applicationInfo_salesRepName',
     'type': 'string', 'optional': True,
     'label': 'Sales Rep Name'},
    {'name': 'payments',
     'type': 'string', 'optional': False,
     'label': (
         'Payments (JSON array — each item: '
         'id, type (Check|ACH|Other|Wire), amount, invoiceReference, comment, '
         'checkMemo, status, glCode, glAmount, glDescription, payee_id, payee_type, '
         'payee_name, payee_address1, payee_address2, payee_city, payee_state_province, '
         'payee_zip, payee_phone, payee_fax, payee_contactName, payee_contactPhone, '
         'payee_routingNumber, payee_accountNumber)'
     )},
]

reply_schema = [
    {'name': 'status', 'type': 'string', 'optional': False,
     'label': 'Processing status (PAYMENTS_PROCESSED or error message)'},
]


# ── Trigger ───────────────────────────────────────────────────────────────────
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
        'service_name':        'Process Funding Request',
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
]


# ── Push ──────────────────────────────────────────────────────────────────────
print(f'Pushing to Workato folder ID: {FOLDER_ID} (migrAIte_Training)...')
resp, err = api_post('/recipes', {
    'recipe': {
        'name':      'MIG_WM_GLDFundingEngine_processFundingRequest',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLDFundingEngine20080714 — webMethods IS 6.5 → Workato (migrAIte_Training). '
            'Callable recipe: HTTP POST /process-funding-request. '
            'Trigger: 6 flat applicationInfo_* fields + payments (JSON string). '
            'Flow: outer try/catch → log request → each loop over payments → '
            '  Check: invokeGetUniquePayee [→ invokeAddNewPayee if new] → invokeCreateCheckRequest; '
            '  ACH: insertPayment (11 params); '
            '  Other/Wire: Default (no external call, business rule); '
            '  rescue per payment: GLDMessageLog:LogXMLRequest (AppID=3). '
            '→ log response → send_reply(status=PAYMENTS_PROCESSED). '
            'Placeholder URLs in all HTTP steps — wire real endpoints in GUI. '
            'Phase 3 of initiate_migration/Instruction_Workato copy.md workflow.'
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
        print(f'\nRemaining manual GUI steps:')
        print('  1. Wire HTTP connections: create GLDExpressGateway, ACH, and MessageLog HTTP connections')
        print('     Real base URLs (obtain from SME):')
        print(f'     - CheckWriter: {GW_URL}  (placeholder)')
        print(f'     - ACH:         {ACH_URL}  (placeholder)')
        print(f'     - MessageLog:  {LOG_URL}  (placeholder)')
        print('  2. Step 15 + 19 (error logs): replace error message placeholder with error.message pill')
        print('  3. Review send_reply response — consider piping actual paymentResponses array via variable')
    else:
        print('\nPush returned 200 but no recipe ID:')
        print(json.dumps(resp, indent=2)[:800])
