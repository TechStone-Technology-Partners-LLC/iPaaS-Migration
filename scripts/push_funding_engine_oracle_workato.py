#!/usr/bin/env python3
"""
Push "FundingEngine" Workato recipe — Oracle for ACH insertPayment.

Target folder : migrAIte_Training/webMethodsMigration (ID: 32159265)
Recipe name   : FundingEngine
Source        : WebMethods/GLDFundingEngine20080714 (processFundingRequest)

Key change from push_funding_engine_workato.py:
  ACH insertPayment step uses oracle/execute_stored_procedure (not HTTP).
  Per RecipeComponents/oracle.json + push_newrecipe2_workato.py pattern.

RecipeComponent references used:
  WorkatoServiceTrigger.json  → trigger format (workato_service/receive_request)
  oracle.json                 → Oracle action pattern (search_rows / execute_stored_procedure)
  IF-ELSE.json                → if/elsif/else block structure
  forEach.json                → each loop (keyword: "each", alias)
  HTTP.json                   → HTTP POST for CheckWriter + MessageLog
  Log.json                    → logger/create_message for Default path
  WorkatoServiceSendReply.json→ send_reply format

Structure:
  0: trigger  workato_service/receive_request — "FundingEngine" (7 flat fields)
    1: try
      2: each — payment_loop (source: trigger.payments.parse_json)
        3:  if  payment.type == "Check"
          4:    HTTP POST → invokeGetUniquePayee    (CheckWriter)
          5:    if payeeKey is_empty
            6:      HTTP POST → invokeAddNewPayee   (CheckWriter)
          7:    HTTP POST → invokeCreateCheckRequest (CheckWriter)
        8:  elsif payment.type == "ACH"
          9:    Oracle execute_stored_procedure → insertPayment  ← ORACLE
        10: else (Other / Wire → Default)
          11:   Log → Default path
        rescue (last in each.block):
          12:   HTTP POST → LogXMLRequest (GLDMessageLog)
      catch (last in try.block):
        13:   HTTP POST → LogXMLRequest (GLDMessageLog)
      14: workato_service/send_reply

Oracle connection: MIG_WM_GLD_Oracle_Connection (account_id: 19657520)
  Note: This is the GLD schema Oracle connection. For production, configure
  a dedicated connection pointing to the GLD_ACHAdaptersServices Oracle instance.

HTTP connections (wire in GUI after push):
  GLDFundingEngine_CheckWriter_Connection — steps 4, 6, 7
  GLDFundingEngine_MessageLog_Connection  — steps 12, 13
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
    print('ERROR: WORKATO_API_TOKEN not found'); sys.exit(1)

HEADERS   = {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}
BASE      = 'https://www.workato.com/api'
FOLDER_ID = 32159265       # migrAIte_Training/webMethodsMigration
ORACLE_CONN_ID = 19657520  # MIG_WM_GLD_Oracle_Connection


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
TRIG_AS       = uid()[:8]
GET_PAYEE_AS  = uid()[:8]
ADD_PAYEE_AS  = uid()[:8]
CREATE_CHK_AS = uid()[:8]
INS_ACH_AS    = uid()[:8]   # Oracle SP step
LOG_ERR_AS    = uid()[:8]
OUTER_ERR_AS  = uid()[:8]
REPLY_AS      = uid()[:8]


# ── Datapill helpers ────────────────────────────────────────────────────────────
# Pattern from RecipeComponents/oracle.json and RecipeComponents/datapill.recipe.json

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
    """Flat trigger input field datapill (WorkatoServiceTrigger.json pattern)."""
    return dp('workato_service', TRIG_AS, 'request', field)


def pay(field):
    """Current payment item field inside the each loop."""
    return dp('workato', 'payment_loop', '*', field)


def http_out(alias, field):
    return dp('http', alias, field)


def http_raw(alias, field):
    return raw_dp('http', alias, field)


# ── Placeholder CheckWriter URL (wire real URL in GUI) ─────────────────────────
GW_URL  = 'https://webmethods-gateway.keybank.internal'
LOG_URL = 'https://webmethods-log.keybank.internal'


# ── HTTP POST builder (RecipeComponents/HTTP.json pattern) ─────────────────────

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


# ── Oracle SP builder (RecipeComponents/oracle.json pattern) ───────────────────
# Pattern source: push_newrecipe2_workato.py oracle_sp() + oracle.json reference.

def oracle_sp(num, alias, proc_name, params, title=None):
    inp = {'procedure_name': proc_name}
    inp.update(params)
    step = {
        'number':   num,
        'keyword':  'action',
        'provider': 'oracle',
        'name':     'execute_stored_procedure',
        'as':       alias,
        'dynamicPickListSelection': {'procedure_name': proc_name},
        'toggleCfg': {},
        'input':    inp,
        'uuid':     uid(),
    }
    if title:
        step['title'] = title
    return step


# ── Shared payee info payload (PayeeInformation 11 fields) ─────────────────────
# Section 5.2 rows 1–11 from PackageAnalysis.md
PAYEE_INFO = {
    'name':           pay('payee_name'),         # payment.payee.name → PayeeName
    'address1':       pay('payee_address1'),      # payment.payee.address1 → AddressLine1
    'address2':       pay('payee_address2'),      # payment.payee.address2 → AddressLine2
    'city':           pay('payee_city'),           # payment.payee.city → City
    'state_province': pay('payee_state_province'), # payment.payee.state_province → State
    'zip':            pay('payee_zip'),            # payment.payee.zip → PostalCode
    'phone':          pay('payee_phone'),          # payment.payee.phone → PhoneNumber
    'fax':            pay('payee_fax'),            # payment.payee.fax → FaxNumber
    'contactName':    pay('payee_contactName'),    # payment.payee.contactName → ContactName
    'contactPhone':   pay('payee_contactPhone'),   # payment.payee.contactPhone → ContactPhoneNumber
    'Country':        'USA',                       # static — hardcoded in source
}


# ── Step 4: HTTP invokeGetUniquePayee (Check path) ─────────────────────────────
step4_get_payee = http_post(
    4,
    'Check.1 — invokeGetUniquePayee (GLDExpressGateway CheckWriter)',
    GET_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeGetUniquePayee',
    PAYEE_INFO,
)


# ── Step 6: HTTP invokeAddNewPayee (if payeeKey empty) ─────────────────────────
step6_add_payee = http_post(
    6,
    'Check.2 — invokeAddNewPayee (register new payee in CheckWriter)',
    ADD_PAYEE_AS,
    GW_URL + '/GLDExpressGateway/CheckWriter/invokeAddNewPayee',
    PAYEE_INFO,
)

# Step 5: if payeeKey is_empty → invokeAddNewPayee
# IF-ELSE.json pattern: conditions array with operand field
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


# ── Step 7: HTTP invokeCreateCheckRequest ──────────────────────────────────────
# Section 5.2 rows 12–17 from PackageAnalysis.md
# payeeKey combined formula: getUniquePayee result if present, else addNewPayee result
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
        'PayeeKey':    PAYEE_KEY,                 # OR formula from step 5.2 row 12
        'Notes':       pay('invoiceReference'),    # payment.invoiceReference → Notes
        'Comments':    pay('comment'),             # payment.comment → Comments
        'CheckAmount': pay('amount'),              # payment.amount → CheckAmount
        'Memo':        pay('checkMemo'),           # payment.checkMemo → Memo
        'PayeeName':   pay('payee_name'),          # payment.payee.name → PayeeName
        'LeaseNumber': trig('id'),                 # applicationInfo.id → LeaseNumber
    },
)


# ── Step 3: if payment.type == "Check" (IF-ELSE.json pattern) ──────────────────
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


# ── Step 9: Oracle execute_stored_procedure → insertPayment ────────────────────
# oracle.json + OracleSearchRows.json pattern:
#   provider: "oracle", name: "execute_stored_procedure"
#   dynamicPickListSelection: {"procedure_name": "SCHEMA.PROC"}
#   input: {"procedure_name": ..., "PARAM1": datapill, ...}
#
# Section 5.3 rows 1–11 from PackageAnalysis.md
step9_insert_ach = oracle_sp(
    9,
    INS_ACH_AS,
    'GLD_ACH.INSERTPAYMENT',   # placeholder — confirm exact SP name/schema with SME
    {
        'APP_ID':         trig('id'),             # applicationInfo.id → APP_ID
        'CUSTOMER_NAME':  trig('customerName'),   # applicationInfo.customerName → CUSTOMER_NAME
        'PAYEE_NAME':     pay('payee_name'),       # payment.payee.name → PAYEE_NAME
        'PAYEE_ID':       pay('payee_id'),         # payment.payee.id → PAYEE_ID
        'REFERENCE':      pay('invoiceReference'), # payment.invoiceReference → REFERENCE
        'AMOUNT':         pay('amount'),           # payment.amount → AMOUNT
        'ROUTING_NUMBER': pay('payee_routingNumber'),  # payment.payee.routingNumber → ROUTING_NUMBER
        'ACCOUNT_NUMBER': pay('payee_accountNumber'),  # payment.payee.accountNumber → ACCOUNT_NUMBER
        'CUSTOMER_ID':    trig('customerID'),      # applicationInfo.customerID → CUSTOMER_ID
        'REQUESTOR_ID':   '1',                     # static "1" — hardcoded in source
        'SOURCE':         trig('sourceName'),      # applicationInfo.sourceName → SOURCE
    },
    title='ACH.1 — Oracle insertPayment (GLD_ACHAdaptersServices, 11 params)',
)


# ── Step 8: elsif payment.type == "ACH" (IF-ELSE.json pattern) ─────────────────
step8_elsif_ach = {
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


# ── Step 11: Log Default path (Log.json pattern) ────────────────────────────────
step11_default_log = {
    'number':   11,
    'keyword':  'action',
    'provider': 'logger',
    'name':     'create_message',
    'as':       uid()[:8],
    'title':    'Default — Other/Wire payment type (no external call)',
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


# ── Step 10: else (Other / Wire → Default) ─────────────────────────────────────
step10_else_default = {
    'number':  10,
    'keyword': 'else',
    'title':   'Payment type Other/Wire — Default',
    'uuid':    uid(),
    'block':   [step11_default_log],
}


# ── Rescue: per-payment error log (HTTP.json pattern) ──────────────────────────
step_rescue_log = http_post(
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
    'number':  14,   # rescue is last in each.block
    'keyword': 'rescue',
    'uuid':    uid(),
    'block':   [step_rescue_log],
}


# ── Step 2: each loop over payments[] (forEach.json pattern) ──────────────────
# forEach.json uses keyword "foreach" but Workato API accepts "each" for
# the repeat-for-each construct; "each" confirmed working in pushed recipes.
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
    'block':   [step3_if_check, step8_elsif_ach, step10_else_default, step_rescue],
}


# ── Outer catch error log ───────────────────────────────────────────────────────
step_catch_log = http_post(
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
    'block':   [step_catch_log],
}


# ── send_reply (WorkatoServiceSendReply.json pattern) ──────────────────────────
step_send_reply = {
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


# ── Outer try block ─────────────────────────────────────────────────────────────
step1_try = {
    'number':  1,
    'keyword': 'try',
    'input':   {},
    'uuid':    uid(),
    'block':   [step2_each, step_send_reply, step_catch],
}


# ── Trigger (WorkatoServiceTrigger.json pattern — flat 7-field schema) ──────────
req_schema = [
    {'name': 'id',               'type': 'string', 'optional': False, 'control_type': 'text',
     'label': 'Application ID (1-100 chars, maps to LeaseNumber in CheckWriter)'},
    {'name': 'customerName',     'type': 'string', 'optional': False, 'control_type': 'text',
     'label': 'Customer Name (max 100 chars)'},
    {'name': 'customerID',       'type': 'string', 'optional': False, 'control_type': 'text',
     'label': 'Customer ID (integer 1-999999999999, as string)'},
    {'name': 'sourceName',       'type': 'string', 'optional': True, 'control_type': 'text',
     'label': 'Source Name (maps to SOURCE in Oracle insertPayment)'},
    {'name': 'sourceSubCategory','type': 'string', 'optional': True, 'control_type': 'text',
     'label': 'Source Sub Category'},
    {'name': 'salesRepName',     'type': 'string', 'optional': True, 'control_type': 'text',
     'label': 'Sales Rep Name'},
    {'name': 'payments',         'type': 'string', 'optional': False, 'control_type': 'text',
     'label': (
         'Payments JSON array. Each item: id, type (Check|ACH|Other|Wire), amount, '
         'invoiceReference, comment, checkMemo, status, glCode, glAmount, glDescription, '
         'payee_id, payee_type, payee_name, payee_address1, payee_address2, payee_city, '
         'payee_state_province, payee_zip, payee_phone, payee_fax, payee_contactName, '
         'payee_contactPhone, payee_routingNumber, payee_accountNumber'
     )},
]

reply_schema = [
    {'name': 'status', 'type': 'string', 'optional': False, 'control_type': 'text',
     'label': 'Processing status (PAYMENTS_PROCESSED)'},
]

code = {
    'number':   0,
    'keyword':  'trigger',
    'provider': 'workato_service',
    'name':     'receive_request',
    'as':       TRIG_AS,
    'uuid':     uid(),
    'dynamicPickListSelection': {},
    'toggleCfg': {},
    'parameters_schema': '',
    'input': {
        'service_name':        'FundingEngine',
        'request_schema_json': json.dumps(req_schema),
        'reply_schema_json':   json.dumps(reply_schema),
    },
    'block': [step1_try],
}

# ── Config (oracle.json pattern — add Oracle connection alongside workato_service + http) ──
config = [
    {'keyword': 'application', 'provider': 'workato_service',
     'account_id': None, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'http',
     'account_id': None, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'oracle',
     'account_id': ORACLE_CONN_ID, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'logger',
     'account_id': None, 'skip_validation': False},
]


# ── Push ────────────────────────────────────────────────────────────────────────
print(f'Pushing FundingEngine (Oracle ACH) to folder {FOLDER_ID} (migrAIte_Training/webMethodsMigration)...')
resp, err = api_post('/recipes', {
    'recipe': {
        'name':      'FundingEngine',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLDFundingEngine20080714 — webMethods IS 6.5 → Workato. '
            'Callable recipe: HTTP POST /FundingEngine. '
            'Trigger: 7 flat fields (id, customerName, customerID, sourceName, '
            'sourceSubCategory, salesRepName, payments JSON string). '
            'ACH path uses Oracle execute_stored_procedure (not HTTP). '
            'Check path uses HTTP to GLDExpressGateway CheckWriter (3 steps). '
            'Error logging via HTTP to GLDMessageLog. '
            'RecipeComponents used: WorkatoServiceTrigger, oracle, IF-ELSE, forEach, '
            'HTTP, Log, WorkatoServiceSendReply. '
            'Source: WebMethods/Analysis/MD/PackageAnalysis.md + '
            'WebMethods/MD/GLDFundingEngine_WMToWorkato.md'
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
        print(f'\nRemaining GUI steps:')
        print('  1. Create HTTP connections in Workato GUI and wire to steps:')
        print(f'     - GLDFundingEngine_CheckWriter_Connection → steps 4, 6, 7 ({GW_URL})')
        print(f'     - GLDFundingEngine_MessageLog_Connection  → steps 12, 13 ({LOG_URL})')
        print('  2. Oracle connection (MIG_WM_GLD_Oracle_Connection, ID 19657520):')
        print('     - Confirm this points to the GLD_ACHAdaptersServices Oracle instance')
        print('     - If needed, create a new Oracle connection for the ACH schema')
        print('     - Verify SP name: GLD_ACH.INSERTPAYMENT (confirm exact name/schema with SME)')
        print('  3. Steps 12 + 13 (error logs): wire error.message pill in Workato GUI')
        print('  4. Obtain real CheckWriter and MessageLog base URLs from SME')
    else:
        print('\nPush returned 200 but no recipe ID:')
        print(json.dumps(resp, indent=2)[:800])
