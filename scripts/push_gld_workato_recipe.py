#!/usr/bin/env python3
"""
Push MIG_WM_GLDComplianceAdapterServices Workato recipe.
v2 — updated per PackageAnalysis.md §5.2:
  - Workato Handle Error block wrapping all DB/HTTP steps
  - Oracle execute_stored_procedure action for all 5 SPs
  - Oracle select_rows action for the SELECT JOIN
  - Full SP parameter binding for each step
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

def t(field):   return dp(TR, TL, field)
def ciu(field): return dp('workato', 'ciu_call', field)
def sp1(field): return dp('oracle',  'log_check_request', field)


# ── Oracle Execute Stored Procedure action ────────────────────────────────────
def oracle_sp(num, label, alias, proc_name, params_dict):
    """
    Uses oracle/execute_stored_procedure.
    params_dict: {SP_PARAM_NAME: workato_data_pill_or_value}
    """
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


# ── Oracle Select Records action ──────────────────────────────────────────────
def oracle_select(num, label, alias, sql, where_input):
    return {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'select_rows',
        'as': alias, 'title': label, 'uuid': uid(),
        'dynamicPickListSelection': {},
        'toggleCfg': {},
        'input': {
            'sql': sql,
            'parameters': where_input,
        },
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

SP1_PARAMS = {col: t(field) for col, field in zip(SP_COL_NAMES, TRIGGER_FIELDS)}

SP2_PARAMS = {
    'APPLICATIONID':        sp1('accCheckRequestID'),
    'REQUEST':              t('CustomerNbr'),   # placeholder — full JSON body to be wired in GUI
    'REQUESTIDENTIFIER1':   t('CustomerNbr'),
    'REQUESTIDENTIFIER2':   t('ApplicationNbr'),
    'REQUESTIDENTIFIER3':   t('Channel'),
}

SP4_PARAMS = {
    'ACCCHECKREQUESTID': sp1('accCheckRequestID'),
    'CIUREFNBR':         ciu('CIURefNbr'),
}

SP5A_PARAMS = {
    'CIUREFNBR':  ciu('CIURefNbr'),
    'CHECKTYPE':  'COMPLIANCE',
    'RESULT':     ciu('CheckResult'),
}

SP5B_PARAMS = {
    'ERRORTYPE':  ciu('ErrorType'),
    'ERRORCODE':  ciu('ErrorCode'),
    'ERRORDESC':  ciu('ErrorDesc'),
    'CIUREFNBR':  ciu('CIURefNbr'),
}

SP5B_CATCH_PARAMS = {
    'ERRORTYPE':  dp('workato', 'error_monitor', 'error', 'type'),
    'ERRORCODE':  'SYSTEM_ERROR',
    'ERRORDESC':  dp('workato', 'error_monitor', 'error', 'message'),
    'CIUREFNBR':  'N/A',
}

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


# ── IF blocks ─────────────────────────────────────────────────────────────────
if_true = {
    'number': 5, 'keyword': 'if', 'uuid': uid(),
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'equals', 'lhs': ciu('CheckResult'), 'rhs': 'TRUE'}],
    },
    'block': [
        oracle_sp(6,  'Log Check Reply — ACCLOGCHECKREPLY (TRUE path)',
                  'log_check_reply', 'GLD_SCHEMA.ACCLOGCHECKREPLY', SP5A_PARAMS),
    ],
}

if_false = {
    'number': 7, 'keyword': 'if', 'uuid': uid(),
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'not_equals', 'lhs': ciu('CheckResult'), 'rhs': 'TRUE'}],
    },
    'block': [
        oracle_sp(8,  'Log Check Reply Error — ACCLOGCHECKREPLYERROR (ELSE path)',
                  'log_check_reply_error', 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP5B_PARAMS),
    ],
}


# ── CIU HTTP placeholder step ─────────────────────────────────────────────────
# webMethods connection used: GLDComplianceAdapterEnv:ExpressOS (Oracle JDBC)
# CIU is an EXTERNAL HTTP service — Oracle connection details do not apply here.
# Replace URL and auth when SME provides CIU endpoint details.
ciu_step = {
    'number': 3, 'keyword': 'action',
    'provider': 'workato', 'name': 'callable_recipe',
    'as': 'ciu_call',
    'title': (
        'Call CIU External System (PLACEHOLDER) — '
        'Replace with HTTP POST to CIU endpoint. '
        'webMethods connection: GLDComplianceAdapterEnv:ExpressOS '
        '(Oracle JDBC CSC06DSHORA1S:1522 GLD_SCHEMA) is the DB connection, not CIU. '
        'Wire CIU endpoint URL from SME.'
    ),
    'uuid': uid(), 'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'http_method': 'post',
        'request_url_suffix': '/placeholder-ciu-endpoint',
    },
}


# ── Recipe steps — flat in trigger block, rescue as last sibling ─────────────
# workato/error_monitor as an action wrapper is not a valid Workato provider/name
# (renders as "Select an app and action" in the GUI).
# The correct structure: all steps sit directly in trigger.block; a step with
# keyword="rescue" placed last in that same block acts as the catch handler for
# any error raised by any preceding step in the trigger scope.
catch_step = oracle_sp(
    11, 'CATCH — Log System Error (ACCLOGCHECKREPLYERROR)',
    'log_system_error', 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP5B_CATCH_PARAMS,
)

rescue_block = {
    'number': 10, 'keyword': 'rescue', 'uuid': uid(),
    'block': [catch_step],
}

trigger_steps = [
    oracle_sp(1, 'Step 1 — Log Check Request (ACCLOGCHECKREQUEST, 25 params)',
              'log_check_request', 'GLD_SCHEMA.ACCLOGCHECKREQUEST', SP1_PARAMS),
    oracle_sp(2, 'Step 2 — Log Check Request XML (LOGXMLREQUEST, 5 params)',
              'log_check_request_xml', 'GLD_SCHEMA.LOGXMLREQUEST', SP2_PARAMS),
    ciu_step,
    oracle_sp(4, 'Step 4 — Update CIU Reference (ACCUPDATECIUREFNBR, 2 params)',
              'update_ciu_ref', 'GLD_SCHEMA.ACCUPDATECIUREFNBR', SP4_PARAMS),
    if_true,
    if_false,
    oracle_select(9, 'Step 6 — Select Customer and Request (28 columns)', 'select_customer',
                  SQL6, {'CIUREFNBR': ciu('CIURefNbr')}),
    rescue_block,
]


# ── Trigger input fields (25) ─────────────────────────────────────────────────
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


# ── Trigger ───────────────────────────────────────────────────────────────────
trigger = {
    'number': 0, 'keyword': 'trigger',
    'provider': 'workato', 'name': 'callable_recipe',
    'as': 'callable_recipe', 'uuid': uid(),
    'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'http_method': 'post',
        'request_url_suffix': '/gld-compliance-check',
        'response_type': 'dynamic',
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
        'name': 'MIG_WM_GLDComplianceAdapterServices',
        'folder_id': str(FOLDER_ID),
        'description': (
            'GLD Compliance check — webMethods IS 6.5 GLDComplianceAdapterServices → Workato. '
            'v2: error monitor block, execute_stored_procedure actions, select_rows for JOIN query. '
            'Trigger: HTTP POST (callable recipe). Steps: SP×5 + HTTP CIU placeholder + SELECT JOIN. '
            'Error handler: ACCLOGCHECKREPLYERROR on any exception.'
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
            print(raw[:600].decode(errors='replace'))
except urllib.error.HTTPError as e:
    body = e.read()
    print(f'HTTP ERROR {e.code}')
    print(body[:1200].decode(errors='replace'))
except Exception as ex:
    print(f'EXCEPTION: {ex}')
