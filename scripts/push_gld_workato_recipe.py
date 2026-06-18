#!/usr/bin/env python3
"""Push MIG_WM_GLDComplianceAdapterServices Workato recipe."""
import sys, json, uuid, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from generators.generate_workato import _load_env_var
import urllib.request

tok = _load_env_var('WORKATO_API_TOKEN').strip()

ORACLE_CONN_ID = 19657520   # MIG_WM_GLD_Oracle_Connection
FOLDER_ID      = 31286666   # Workato-Migration

def uid(): return str(uuid.uuid4())


# ── Data pill builder ─────────────────────────────────────────────────────────
def dp(provider, line, *path_parts):
    path = [{'path_element_type': 'current_item'} if p == '*' else p for p in path_parts]
    pill = json.dumps({'pill_type': 'output', 'provider': provider, 'line': line, 'path': path})
    escaped = pill.replace('"', '\\"')
    return "#{_dp('" + escaped + "')}"


TR = 'workato'
TL = 'callable_recipe'

def t(field):   return dp(TR, TL, field)
def ciu(field): return dp('net_http', 'ciu_call', field)
def sp1(field): return dp('oracle',   'log_check_request', field)


# ── Oracle action builders ────────────────────────────────────────────────────
def oracle_sp(num, label, alias, sp_call):
    return {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'run_sql',
        'as': alias, 'title': label, 'uuid': uid(),
        'dynamicPickListSelection': {}, 'toggleCfg': {},
        'input': {'sql': sp_call},
    }


def oracle_select(num, label, alias, sql):
    return {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'select_rows',
        'as': alias, 'title': label, 'uuid': uid(),
        'dynamicPickListSelection': {}, 'toggleCfg': {},
        'input': {'sql': sql},
    }


# ── SP / SQL strings ──────────────────────────────────────────────────────────
TRIGGER_FIELDS = [
    'CustomerNbr', 'CustomerType', 'PartyType', 'Businessname', 'ApplicationNbr',
    'Channel', 'LOB', 'ProductCode', 'SubProductCode', 'PostBack', 'ComplianceReplyEmail',
    'FirstName', 'MiddleName', 'LastName',
    'AddressLine1', 'AddressLine2', 'AddressLine3', 'AddressLine4',
    'City', 'State', 'Zip', 'CountryCode', 'SSNTIN', 'DOB', 'RequestorSystemRequestID',
]

SP1 = 'CALL GLD_SCHEMA.ACCLOGCHECKREQUEST(' + ','.join(t(f) for f in TRIGGER_FIELDS) + ')'

SP2 = (
    'CALL GLD_SCHEMA.LOGXMLREQUEST(' +
    sp1('accCheckRequestID') + ',' +
    '[REQUEST_XML_BODY],' +
    t('CustomerNbr') + ',' + t('ApplicationNbr') + ',' + t('Channel') + ')'
)

SP4 = 'CALL GLD_SCHEMA.ACCUPDATECIUREFNBR(' + sp1('accCheckRequestID') + ',' + ciu('CIURefNbr') + ')'

SP5a = (
    'CALL GLD_SCHEMA.ACCLOGCHECKREPLY(' +
    ciu('CIURefNbr') + ',' + "'COMPLIANCE'," + ciu('CheckResult') + ')'
)

SP5b = (
    'CALL GLD_SCHEMA.ACCLOGCHECKREPLYERROR(' +
    ciu('ErrorType') + ',' + ciu('ErrorCode') + ',' + ciu('ErrorDesc') + ',' + ciu('CIURefNbr') + ')'
)

SQL6 = (
    'SELECT DISTINCT '
    't1.ACCCUSTOMERID,t1.CUSTOMERNBR,t1.CUSTOMERTYPE,t1.BUSINESSNAME,'
    't1.FIRSTNAME,t1.MIDDLENAME,t1.LASTNAME,'
    't1.ADDRESSLINE1,t1.ADDRESSLINE2,t1.ADDRESSLINE3,t1.ADDRESSLINE4,'
    't1.CITY,t1.STATE,t1.ZIP,t1.COUNTRYCODE,t1.SSNTIN,t1.PARTYTYPE,t1.DOB,'
    't2.ACCCHECKREQUESTID,t2.APPLICATIONNBR,t2.CHANNEL,t2.LOB,'
    't2.PRODUCTCODE,t2.SUBPRODUCTCODE,t2.POSTBACK,t2.COMPLIANCEREPLYEMAIL,'
    't2.CIUREFNBR,t2.REQUESTTIMESTAMP '
    'FROM GLD_SCHEMA.ACCCUSTOMER t1 '
    'JOIN GLD_SCHEMA.ACCCHECKREQUEST t2 ON t1.ACCCUSTOMERID=t2.ACCCUSTOMERID '
    'WHERE t2.CIUREFNBR=' + ciu('CIURefNbr')
)

# ── CIU HTTP placeholder ──────────────────────────────────────────────────────
ciu_step = {
    'number': 3, 'keyword': 'action',
    'provider': 'workato', 'name': 'callable_recipe',
    'as': 'ciu_call', 'title': 'Call CIU External System (PLACEHOLDER)',
    'uuid': uid(), 'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'http_method': 'post',
        'request_url_suffix': '/placeholder-ciu-endpoint',
    },
}

# ── IF blocks (two consecutive — TRUE path and ELSE path) ────────────────────
if_true = {
    'number': 5, 'keyword': 'if', 'uuid': uid(),
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'equals', 'lhs': ciu('CheckResult'), 'rhs': 'TRUE'}],
    },
    'block': [oracle_sp(6, 'Log Check Reply (ACCLOGCHECKREPLY)', 'log_check_reply', SP5a)],
}

if_false = {
    'number': 7, 'keyword': 'if', 'uuid': uid(),
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'not_equals', 'lhs': ciu('CheckResult'), 'rhs': 'TRUE'}],
    },
    'block': [oracle_sp(8, 'Log Reply Error (ACCLOGCHECKREPLYERROR)', 'log_check_reply_error', SP5b)],
}

# ── Trigger input fields (25) ─────────────────────────────────────────────────
input_fields = [
    {'name': 'CustomerNbr',               'type': 'string',  'optional': False, 'label': 'Customer Number'},
    {'name': 'CustomerType',              'type': 'string',  'optional': False, 'label': 'Customer Type'},
    {'name': 'PartyType',                 'type': 'string',  'optional': True,  'label': 'Party Type'},
    {'name': 'Businessname',              'type': 'string',  'optional': True,  'label': 'Business Name'},
    {'name': 'ApplicationNbr',            'type': 'string',  'optional': False, 'label': 'Application Number'},
    {'name': 'Channel',                   'type': 'string',  'optional': True,  'label': 'Channel'},
    {'name': 'LOB',                       'type': 'string',  'optional': True,  'label': 'Line of Business'},
    {'name': 'ProductCode',               'type': 'string',  'optional': True,  'label': 'Product Code'},
    {'name': 'SubProductCode',            'type': 'string',  'optional': True,  'label': 'Sub-Product Code'},
    {'name': 'PostBack',                  'type': 'string',  'optional': True,  'label': 'PostBack URL'},
    {'name': 'ComplianceReplyEmail',      'type': 'string',  'optional': True,  'label': 'Compliance Reply Email'},
    {'name': 'FirstName',                 'type': 'string',  'optional': True,  'label': 'First Name'},
    {'name': 'MiddleName',                'type': 'string',  'optional': True,  'label': 'Middle Name'},
    {'name': 'LastName',                  'type': 'string',  'optional': True,  'label': 'Last Name'},
    {'name': 'AddressLine1',              'type': 'string',  'optional': True,  'label': 'Address Line 1'},
    {'name': 'AddressLine2',              'type': 'string',  'optional': True,  'label': 'Address Line 2'},
    {'name': 'AddressLine3',              'type': 'string',  'optional': True,  'label': 'Address Line 3'},
    {'name': 'AddressLine4',              'type': 'string',  'optional': True,  'label': 'Address Line 4'},
    {'name': 'City',                      'type': 'string',  'optional': True,  'label': 'City'},
    {'name': 'State',                     'type': 'string',  'optional': True,  'label': 'State'},
    {'name': 'Zip',                       'type': 'string',  'optional': True,  'label': 'ZIP Code'},
    {'name': 'CountryCode',               'type': 'string',  'optional': True,  'label': 'Country Code'},
    {'name': 'SSNTIN',                    'type': 'string',  'optional': True,  'label': 'SSN or TIN'},
    {'name': 'DOB',                       'type': 'date',    'optional': True,  'label': 'Date of Birth'},
    {'name': 'RequestorSystemRequestID',  'type': 'integer', 'optional': True,  'label': 'Requestor System Request ID'},
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
    'block': [
        oracle_sp(1, 'Log Check Request (ACCLOGCHECKREQUEST 25 params)', 'log_check_request', SP1),
        oracle_sp(2, 'Log Check Request XML (LOGXMLREQUEST 5 params)',   'log_check_request_xml', SP2),
        ciu_step,
        oracle_sp(4, 'Update CIU Reference (ACCUPDATECIUREFNBR)',       'update_ciu_ref', SP4),
        if_true,
        if_false,
        oracle_select(9, 'Select Customer and Request (28 cols)',        'select_customer', SQL6),
    ],
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
            'GLD Compliance check migrated from webMethods IS 6.5 GLDComplianceAdapterServices. '
            'HTTP POST trigger -> Log SP -> Log XML -> CIU call -> Update CIU -> IF/ELSE reply/error log -> SELECT.'
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
        resp = json.loads(r.read())
        print('SUCCESS')
        print(f"Recipe ID : {resp.get('id')}")
        print(f"Full resp : {json.dumps(resp)[:400]}")
except urllib.error.HTTPError as e:
    print(f'ERROR {e.code}')
    print(e.read()[:800].decode(errors='replace'))
except Exception as ex:
    print(f'EXCEPTION: {ex}')
