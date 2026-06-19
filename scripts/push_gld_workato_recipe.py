#!/usr/bin/env python3
"""
Push MIG_WM_GLDComplianceAdapterServices Workato recipe.
v4 — per Instruction_Workato Recipe.md:
  - Callable recipe trigger named "Compliance Check", 25 input fields
  - Handle error block: rescue keyword as last sibling in trigger.block
  - Action 1: execute_stored_procedure ACCLOGCHECKREQUEST (25 IN params)
  - Action 2: execute_stored_procedure LOGXMLREQUEST (5 IN params)
  - Action 3: HTTP POST to CIU endpoint (http/post — URL to be wired by SME)
  - Action 4: execute_stored_procedure ACCUPDATECIUREFNBR (2 IN params)
  - IF/ELSE block titled "Check CIU Result" (if keyword + else sibling)
    - IF TRUE: execute_stored_procedure ACCLOGCHECKREPLY (3 IN params)
    - ELSE:    execute_stored_procedure ACCLOGCHECKREPLYERROR (4 IN params)
  - Action 6: select_rows — 28-column JOIN on ACCCUSTOMER + ACCCHECKREQUEST
  - rescue (catch): execute_stored_procedure ACCLOGCHECKREPLYERROR on system error
"""
import sys, json, uuid, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from generators.generate_workato import _load_env_var
import urllib.request

tok = _load_env_var('WORKATO_API_TOKEN').strip()

ORACLE_CONN_ID = 19657520   # MIG_WM_GLD_Oracle_Connection
FOLDER_ID      = 31661117   # WebMethodsMigration

def uid(): return str(uuid.uuid4())


# ── Data pill builder ─────────────────────────────────────────────────────────
def dp(provider, line, *path_parts):
    path = [{'path_element_type': 'current_item'} if p == '*' else p for p in path_parts]
    pill = json.dumps({'pill_type': 'output', 'provider': provider, 'line': line, 'path': path})
    return "#{_dp('" + pill.replace('"', '\\"') + "')}"


TR = 'workato'
TL = 'callable_recipe'

def t(field):   return dp(TR, TL, field)           # trigger pill
def ciu(field): return dp('http', 'ciu_call', field)  # CIU HTTP response pill
def sp1(field): return dp('oracle', 'log_check_request', field)  # step 1 output pill


# ── Oracle Execute Stored Procedure ───────────────────────────────────────────
def oracle_sp(num, label, alias, proc_name, params_dict):
    inp = {'procedure_name': proc_name}
    inp.update(params_dict)
    return {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'execute_stored_procedure',
        'as': alias, 'title': label, 'uuid': uid(),
        'dynamicPickListSelection': {'procedure_name': proc_name},
        'toggleCfg': {},
        'input': inp,
    }


# ── Oracle Select Records (SELECT JOIN) ───────────────────────────────────────
def oracle_select(num, label, alias, sql):
    return {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'select_rows',
        'as': alias, 'title': label, 'uuid': uid(),
        'dynamicPickListSelection': {},
        'toggleCfg': {},
        'input': {'sql': sql},
    }


# ── SP parameter definitions ──────────────────────────────────────────────────
TRIGGER_FIELDS = [
    'CustomerNbr', 'CustomerType', 'PartyType', 'Businessname', 'ApplicationNbr',
    'Channel', 'LOB', 'ProductCode', 'SubProductCode', 'PostBack', 'ComplianceReplyEmail',
    'FirstName', 'MiddleName', 'LastName',
    'AddressLine1', 'AddressLine2', 'AddressLine3', 'AddressLine4',
    'City', 'State', 'Zip', 'CountryCode', 'SSNTIN', 'DOB', 'RequestorSystemRequestID',
]
SP_COL_NAMES = [
    'CUSTOMERNBR', 'CUSTOMERTYPE', 'PARTYTYPE', 'BUSINESSNAME', 'APPLICATIONNBR',
    'CHANNEL', 'LOB', 'PRODUCTCODE', 'SUBPRODUCTCODE', 'POSTBACK', 'COMPLIANCEREPLYEMAIL',
    'FIRSTNAME', 'MIDDLENAME', 'LASTNAME',
    'ADDRESSLINE1', 'ADDRESSLINE2', 'ADDRESSLINE3', 'ADDRESSLINE4',
    'CITY', 'STATE', 'ZIP', 'COUNTRYCODE', 'SSNTIN', 'DOB', 'REQUESTORSYSTEMREQUESTID',
]

# Action 1: ACCLOGCHECKREQUEST — 25 IN params wired from trigger
SP1_PARAMS = {col: t(field) for col, field in zip(SP_COL_NAMES, TRIGGER_FIELDS)}

# Action 2: LOGXMLREQUEST — 5 IN params
SP2_PARAMS = {
    'APPLICATIONID':        sp1('accCheckRequestID'),  # OUT from step 1
    'REQUEST':              t('CustomerNbr'),            # placeholder — full JSON body in GUI
    'REQUESTIDENTIFIER1':   t('CustomerNbr'),
    'REQUESTIDENTIFIER2':   t('ApplicationNbr'),
    'REQUESTIDENTIFIER3':   t('Channel'),
}

# Action 4: ACCUPDATECIUREFNBR — 2 IN params
SP4_PARAMS = {
    'ACCCHECKREQUESTID': sp1('accCheckRequestID'),
    'CIUREFNBR':         ciu('CIURefNbr'),
}

# Action 5a (IF TRUE): ACCLOGCHECKREPLY — 3 IN params
SP5A_PARAMS = {
    'CIUREFNBR':  ciu('CIURefNbr'),
    'CHECKTYPE':  'COMPLIANCE',
    'RESULT':     ciu('CheckResult'),
}

# Action 5b (ELSE): ACCLOGCHECKREPLYERROR — 4 IN params
SP5B_PARAMS = {
    'ERRORTYPE':  ciu('ErrorType'),
    'ERRORCODE':  ciu('ErrorCode'),
    'ERRORDESC':  ciu('ErrorDesc'),
    'CIUREFNBR':  ciu('CIURefNbr'),
}

# rescue / catch: ACCLOGCHECKREPLYERROR — pulls error details from Workato error object
SP5B_CATCH_PARAMS = {
    'ERRORTYPE':  dp('workato', 'error_monitor', 'error', 'type'),
    'ERRORCODE':  'SYSTEM_ERROR',
    'ERRORDESC':  dp('workato', 'error_monitor', 'error', 'message'),
    'CIUREFNBR':  'N/A',
}

# Action 6 SQL — 28-column DISTINCT JOIN
SQL6 = (
    'SELECT DISTINCT '
    't1.ACCCUSTOMERID, t1.CUSTOMERNBR, t1.CUSTOMERTYPE, t1.BUSINESSNAME, '
    't1.FIRSTNAME, t1.MIDDLENAME, t1.LASTNAME, '
    't1.ADDRESSLINE1, t1.ADDRESSLINE2, t1.ADDRESSLINE3, t1.ADDRESSLINE4, '
    't1.CITY, t1.STATE, t1.ZIP, t1.COUNTRYCODE, t1.SSNTIN, t1.PARTYTYPE, t1.DOB, '
    't2.ACCCHECKREQUESTID, t2.APPLICATIONNBR, t2.CHANNEL, t2.LOB, '
    't2.PRODUCTCODE, t2.SUBPRODUCTCODE, t2.POSTBACK, '
    't2.COMPLIANCEREPLYEMAIL, t2.CIUREFNBR, t2.REQUESTTIMESTAMP '
    'FROM GLD_SCHEMA.ACCCUSTOMER t1 '
    'JOIN GLD_SCHEMA.ACCCHECKREQUEST t2 ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID '
    'WHERE t2.CIUREFNBR = ' + ciu('CIURefNbr')
)


# ── Action 3: HTTP CIU call ───────────────────────────────────────────────────
# webMethods source: GLDComplianceAdapterEnv:ExpressOS (Oracle JDBC, CSC06DSHORA1S:1522)
# is the DB connection — the CIU endpoint is a SEPARATE external HTTP service.
# URL must be obtained from SME; wire the HTTP connection in Workato GUI.
# Response expected: {"CIURefNbr":"...","CheckResult":"TRUE/FALSE","ErrorType":"...","ErrorCode":"...","ErrorDesc":"..."}
ciu_step = {
    'number': 3, 'keyword': 'action',
    'provider': 'http', 'name': 'post',
    'as': 'ciu_call',
    'title': 'Action 3 — Call CIU System (HTTP POST) [wire endpoint URL in GUI]',
    'uuid': uid(), 'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'url':          '[CIU_ENDPOINT_URL — obtain from SME]',
        'content_type': 'application/json',
        'payload': json.dumps({
            'CustomerNbr':    t('CustomerNbr'),
            'ApplicationNbr': t('ApplicationNbr'),
            'Channel':        t('Channel'),
            'SSNTIN':         t('SSNTIN'),
            'DOB':            t('DOB'),
        }),
    },
}


# ── IF/ELSE "Check CIU Result" ────────────────────────────────────────────────
if_block = {
    'number': 5, 'keyword': 'if',
    'title': 'Check CIU Result',
    'uuid': uid(),
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'equals', 'lhs': ciu('CheckResult'), 'rhs': 'TRUE'}],
    },
    'block': [
        oracle_sp(6, 'Action 5.1 — Log Check Reply — ACCLOGCHECKREPLY (TRUE path)',
                  'log_check_reply', 'GLD_SCHEMA.ACCLOGCHECKREPLY', SP5A_PARAMS),
    ],
}

else_block = {
    'number': 7, 'keyword': 'else', 'uuid': uid(),
    'block': [
        oracle_sp(8, 'Action 5.2 — Log Check Reply Error — ACCLOGCHECKREPLYERROR (ELSE path)',
                  'log_check_reply_error', 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP5B_PARAMS),
    ],
}


# ── rescue (catch) block ──────────────────────────────────────────────────────
rescue_block = {
    'number': 11, 'keyword': 'rescue', 'uuid': uid(),
    'block': [
        oracle_sp(12, 'CATCH — Log System Error (ACCLOGCHECKREPLYERROR)',
                  'log_system_error', 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP5B_CATCH_PARAMS),
    ],
}


# ── All trigger steps (flat) ──────────────────────────────────────────────────
trigger_steps = [
    oracle_sp(1, 'Action 1 — Log Check Request (ACCLOGCHECKREQUEST, 25 params)',
              'log_check_request', 'GLD_SCHEMA.ACCLOGCHECKREQUEST', SP1_PARAMS),
    oracle_sp(2, 'Action 2 — Log Check Request XML (LOGXMLREQUEST, 5 params)',
              'log_check_request_xml', 'GLD_SCHEMA.LOGXMLREQUEST', SP2_PARAMS),
    ciu_step,
    oracle_sp(4, 'Action 4 — Update CIU Reference (ACCUPDATECIUREFNBR, 2 params)',
              'update_ciu_ref', 'GLD_SCHEMA.ACCUPDATECIUREFNBR', SP4_PARAMS),
    if_block,
    else_block,
    oracle_select(9, 'Action 6 — Select Customer and Request (28 columns, JOIN)',
                  'select_customer', SQL6),
    rescue_block,
]


# ── Trigger input fields (25) — named "Compliance Check" ─────────────────────
input_fields = [
    {'name': 'CustomerNbr',              'type': 'string',  'optional': False, 'label': 'Customer Number'},
    {'name': 'CustomerType',             'type': 'string',  'optional': False, 'label': 'Customer Type'},
    {'name': 'PartyType',                'type': 'string',  'optional': True,  'label': 'Party Type'},
    {'name': 'Businessname',             'type': 'string',  'optional': True,  'label': 'Business Name'},
    {'name': 'ApplicationNbr',           'type': 'string',  'optional': False, 'label': 'Application Number'},
    {'name': 'Channel',                  'type': 'string',  'optional': True,  'label': 'Channel'},
    {'name': 'LOB',                      'type': 'string',  'optional': True,  'label': 'Line of Business'},
    {'name': 'ProductCode',              'type': 'string',  'optional': True,  'label': 'Product Code'},
    {'name': 'SubProductCode',           'type': 'string',  'optional': True,  'label': 'Sub-Product Code'},
    {'name': 'PostBack',                 'type': 'string',  'optional': True,  'label': 'PostBack URL'},
    {'name': 'ComplianceReplyEmail',     'type': 'string',  'optional': True,  'label': 'Compliance Reply Email'},
    {'name': 'FirstName',                'type': 'string',  'optional': True,  'label': 'First Name'},
    {'name': 'MiddleName',               'type': 'string',  'optional': True,  'label': 'Middle Name'},
    {'name': 'LastName',                 'type': 'string',  'optional': True,  'label': 'Last Name'},
    {'name': 'AddressLine1',             'type': 'string',  'optional': True,  'label': 'Address Line 1'},
    {'name': 'AddressLine2',             'type': 'string',  'optional': True,  'label': 'Address Line 2'},
    {'name': 'AddressLine3',             'type': 'string',  'optional': True,  'label': 'Address Line 3'},
    {'name': 'AddressLine4',             'type': 'string',  'optional': True,  'label': 'Address Line 4'},
    {'name': 'City',                     'type': 'string',  'optional': True,  'label': 'City'},
    {'name': 'State',                    'type': 'string',  'optional': True,  'label': 'State'},
    {'name': 'Zip',                      'type': 'string',  'optional': True,  'label': 'ZIP Code'},
    {'name': 'CountryCode',              'type': 'string',  'optional': True,  'label': 'Country Code'},
    {'name': 'SSNTIN',                   'type': 'string',  'optional': True,  'label': 'SSN or TIN'},
    {'name': 'DOB',                      'type': 'date',    'optional': True,  'label': 'Date of Birth'},
    {'name': 'RequestorSystemRequestID', 'type': 'integer', 'optional': True,  'label': 'Requestor System Request ID'},
]


# ── Trigger — callable recipe "Compliance Check" ──────────────────────────────
trigger = {
    'number': 0, 'keyword': 'trigger',
    'provider': 'workato', 'name': 'callable_recipe',
    'as': 'callable_recipe', 'uuid': uid(),
    'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'http_method':             'post',
        'request_url_suffix':      '/compliance-check',
        'response_type':           'dynamic',
        'input_fields_raw_schema': json.dumps(input_fields),
    },
    'block': trigger_steps,
}

config = [
    {
        'keyword': 'application', 'name': 'oracle', 'provider': 'oracle',
        'account_id': ORACLE_CONN_ID, 'skip_validation': False,
    },
]


# ── Push ──────────────────────────────────────────────────────────────────────
body = json.dumps({
    'recipe': {
        'name': 'Compliance Check — MIG_WM_GLDComplianceAdapterServices',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLD Compliance check — webMethods IS 6.5 GLDComplianceAdapterServices → Workato. '
            'v4: callable_recipe trigger (HTTP POST /compliance-check, 25 fields), '
            'Actions 1-2 execute_stored_procedure, '
            'Action 3 HTTP POST CIU (wire URL from SME), '
            'Action 4 execute_stored_procedure, '
            'IF/ELSE "Check CIU Result" (5a ACCLOGCHECKREPLY / 5b ACCLOGCHECKREPLYERROR), '
            'Action 6 select_rows 28-col JOIN, '
            'rescue block: ACCLOGCHECKREPLYERROR on system error.'
        ),
        'code':   json.dumps(trigger),
        'config': json.dumps(config),
    }
}).encode()

req = urllib.request.Request(
    'https://www.workato.com/api/recipes', data=body, method='POST',
    headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        resp = json.loads(raw)
        recipe_id = resp.get('id')
        if recipe_id:
            print(f'SUCCESS — Recipe ID: {recipe_id}')
        else:
            print('PUSH RETURNED 200 BUT NO ID:')
            print(raw[:800].decode(errors='replace'))
except urllib.error.HTTPError as e:
    body_err = e.read()
    print(f'HTTP ERROR {e.code}')
    print(body_err[:1200].decode(errors='replace'))
except Exception as ex:
    print(f'EXCEPTION: {ex}')
