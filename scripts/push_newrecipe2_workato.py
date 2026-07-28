#!/usr/bin/env python3
"""
Push NewRecipe2 to Workato — migrAIte_Training/webMethodsMigration folder.
Recipe: GLD Compliance Check (webMethods IS GLDComplianceAdapterServices → Workato).
Based on WMToWorkato.md + RecipeComponents/oracle.json pattern.
"""
import sys, json, uuid, os, urllib.request, urllib.error

# Load env from project root
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
    if not tok:
        tok = os.environ.get('WORKATO_API_TOKEN', '')
    return tok

tok = load_env(ENV_PATH)
if not tok:
    print('ERROR: WORKATO_API_TOKEN not found'); sys.exit(1)

HEADERS = {'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'}
BASE = 'https://www.workato.com/api'

MIGRAITE_FOLDER_ID = 31835141   # MigrAIte_Training
ORACLE_CONN_ID     = 19657520   # MIG_WM_GLD_Oracle_Connection

def api_get(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_post(path, body_dict):
    data = json.dumps(body_dict).encode()
    req = urllib.request.Request(BASE + path, data=data, method='POST', headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, (e.code, e.read().decode(errors='replace'))

# ─── Step 1: Find or discover webMethodsMigration subfolder ───────────────────
print('Looking for webMethodsMigration under MigrAIte_Training...')
try:
    folders = api_get(f'/folders?parent_id={MIGRAITE_FOLDER_ID}')
    folder_list = folders if isinstance(folders, list) else folders.get('result', folders.get('items', []))
    wm_folder = next((f for f in folder_list if 'webmethods' in f.get('name','').lower()), None)
    if wm_folder:
        FOLDER_ID = wm_folder['id']
        print(f'Found folder: {wm_folder["name"]} (ID: {FOLDER_ID})')
    else:
        print(f'No webMethodsMigration subfolder found — using MigrAIte_Training root (ID: {MIGRAITE_FOLDER_ID})')
        FOLDER_ID = MIGRAITE_FOLDER_ID
except Exception as ex:
    print(f'Folder lookup error: {ex} — falling back to MigrAIte_Training ID')
    FOLDER_ID = MIGRAITE_FOLDER_ID

# ─── Unique aliases ────────────────────────────────────────────────────────────
TRIG_AS   = str(uuid.uuid4())[:8]
SP1_AS    = str(uuid.uuid4())[:8]
SEL1B_AS  = str(uuid.uuid4())[:8]
SP2_AS    = str(uuid.uuid4())[:8]
HTTP_AS   = str(uuid.uuid4())[:8]
SP4_AS    = str(uuid.uuid4())[:8]
SP5A_AS   = str(uuid.uuid4())[:8]
SP5B_AS   = str(uuid.uuid4())[:8]
SEL6_AS   = str(uuid.uuid4())[:8]
REPLY_AS  = str(uuid.uuid4())[:8]
CATCH_AS  = str(uuid.uuid4())[:8]
SP_ERR_AS = str(uuid.uuid4())[:8]

# ─── Data pill helpers ─────────────────────────────────────────────────────────
def dp(provider, line, *path_parts):
    path = []
    for p in path_parts:
        if p == '__size__':
            path.append({'path_element_type': 'size'})
        else:
            path.append(p)
    pill = json.dumps({'pill_type': 'output', 'provider': provider, 'line': line, 'path': path})
    return "#{_dp('" + pill.replace('"', '\\"') + "')}"

def trig(field):    return dp('workato_service', TRIG_AS, 'request', field)
def http(field):    return dp('http', HTTP_AS, 'body', field)
def catch_dp(field):return dp('catch', CATCH_AS, field)

# ─── 25 trigger fields ─────────────────────────────────────────────────────────
TRIGGER_FIELDS = [
    ('CustomerNbr',              'string',  False, 'Customer Number'),
    ('CustomerType',             'string',  True,  'Customer Type'),
    ('PartyType',                'string',  True,  'Party Type'),
    ('Businessname',             'string',  True,  'Business Name'),
    ('ApplicationNbr',           'string',  False, 'Application Number'),
    ('Channel',                  'string',  True,  'Channel'),
    ('LOB',                      'string',  True,  'Line of Business'),
    ('ProductCode',              'string',  True,  'Product Code'),
    ('SubProductCode',           'string',  True,  'Sub-Product Code'),
    ('PostBack',                 'string',  True,  'PostBack URL'),
    ('ComplianceReplyEmail',     'string',  True,  'Compliance Reply Email'),
    ('FirstName',                'string',  True,  'First Name'),
    ('MiddleName',               'string',  True,  'Middle Name'),
    ('LastName',                 'string',  True,  'Last Name'),
    ('AddressLine1',             'string',  True,  'Address Line 1'),
    ('AddressLine2',             'string',  True,  'Address Line 2'),
    ('AddressLine3',             'string',  True,  'Address Line 3'),
    ('AddressLine4',             'string',  True,  'Address Line 4'),
    ('City',                     'string',  True,  'City'),
    ('State',                    'string',  True,  'State'),
    ('Zip',                      'string',  True,  'ZIP Code'),
    ('CountryCode',              'string',  True,  'Country Code'),
    ('SSNTIN',                   'string',  True,  'SSN or TIN'),
    ('DOB',                      'date',    True,  'Date of Birth'),
    ('RequestorSystemRequestID', 'integer', True,  'Requestor System Request ID'),
]

req_schema = [
    {'name': n, 'type': t, 'optional': o, 'label': l,
     **(({'control_type': 'text'} if t == 'string' else {}))}
    for n, t, o, l in TRIGGER_FIELDS
]
reply_schema = [{'name': 'status', 'type': 'string', 'optional': False, 'label': 'Status'}]

# ─── SP column names (matching trigger field order) ────────────────────────────
SP_COLS = [
    'CUSTOMERNBR', 'CUSTOMERTYPE', 'PARTYTYPE', 'BUSINESSNAME', 'APPLICATIONNBR',
    'CHANNEL', 'LOB', 'PRODUCTCODE', 'SUBPRODUCTCODE', 'POSTBACK', 'COMPLIANCEREPLYEMAIL',
    'FIRSTNAME', 'MIDDLENAME', 'LASTNAME',
    'ADDRESSLINE1', 'ADDRESSLINE2', 'ADDRESSLINE3', 'ADDRESSLINE4',
    'CITY', 'STATE', 'ZIP', 'COUNTRYCODE', 'SSNTIN', 'DOB', 'REQUESTORSYSTEMREQUESTID',
]

# ─── Oracle SP action builder ──────────────────────────────────────────────────
def oracle_sp(num, alias, proc_name, params, title=None):
    inp = {'procedure_name': proc_name}
    inp.update(params)
    step = {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'execute_stored_procedure',
        'as': alias,
        'dynamicPickListSelection': {'procedure_name': proc_name},
        'toggleCfg': {},
        'input': inp,
        'uuid': str(uuid.uuid4()),
    }
    if title:
        step['title'] = title
    return step

# ─── Oracle SELECT rows action builder ────────────────────────────────────────
def oracle_select(num, alias, sql, title=None):
    step = {
        'number': num, 'keyword': 'action',
        'provider': 'oracle', 'name': 'select_rows',
        'as': alias,
        'dynamicPickListSelection': {},
        'toggleCfg': {},
        'input': {'sql': sql},
        'uuid': str(uuid.uuid4()),
    }
    if title:
        step['title'] = title
    return step

# ─── Action step parameters ────────────────────────────────────────────────────
SP1_PARAMS = {col: trig(name) for col, (name, *_) in zip(SP_COLS, TRIGGER_FIELDS)}

# Build JSON string of all trigger fields for REQUEST param (LOGXMLREQUEST)
req_json_parts = ', '.join(f'"{n}": "' + trig(n) + '"' for n, *_ in TRIGGER_FIELDS)
REQUEST_JSON = '{' + req_json_parts + '}'

SP2_PARAMS = {
    'APPLICATIONID':      dp('oracle', SEL1B_AS, 'rows', '0', 'ACCCHECKREQUESTID'),
    'REQUEST':            REQUEST_JSON,
    'REQUESTIDENTIFIER1': trig('CustomerNbr'),
    'REQUESTIDENTIFIER2': trig('ApplicationNbr'),
    'REQUESTIDENTIFIER3': trig('Channel'),
}

SP4_PARAMS = {
    'ACCCHECKREQUESTID': dp('oracle', SEL1B_AS, 'rows', '0', 'ACCCHECKREQUESTID'),
    'CIUREFNBR':         http('CIURefNbr'),
}

SP5A_PARAMS = {
    'CIUREFNBR':  http('CIURefNbr'),
    'CHECKTYPE':  'COMPLIANCE',
    'RESULT':     http('CheckResult'),
}

SP5B_PARAMS = {
    'ERRORTYPE': http('ErrorType'),
    'ERRORCODE': http('ErrorCode'),
    'ERRORDESC': http('ErrorDesc'),
    'CIUREFNBR': http('CIURefNbr'),
}

SP_CATCH_PARAMS = {
    'ERRORTYPE': catch_dp('type'),
    'ERRORCODE': 'SYSTEM_ERROR',
    'ERRORDESC': catch_dp('message'),
    'CIUREFNBR': 'N/A',
}

SELECT_6_SQL = (
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
    'WHERE t2.CIUREFNBR = ' + http('CIURefNbr')
)

# ─── HTTP CIU step ─────────────────────────────────────────────────────────────
ciu_step = {
    'number': 5, 'keyword': 'action',
    'provider': 'http', 'name': 'post',
    'as': HTTP_AS,
    'title': 'Call CIU System (HTTP POST) — wire endpoint URL in GUI',
    'dynamicPickListSelection': {}, 'toggleCfg': {},
    'input': {
        'url':          '[CIU_ENDPOINT_URL — obtain from SME]',
        'content_type': 'application/json',
        'payload': json.dumps({k: trig(k) for k, *_ in TRIGGER_FIELDS}),
    },
    'extended_output_schema': [
        {
            'label': 'Body', 'name': 'body', 'type': 'object',
            'properties': [
                {'name': 'CIURefNbr',  'type': 'string', 'label': 'CIU Reference Number'},
                {'name': 'CheckResult','type': 'string', 'label': 'Check Result (TRUE/FALSE)'},
                {'name': 'ErrorType',  'type': 'string', 'label': 'Error Type'},
                {'name': 'ErrorCode',  'type': 'string', 'label': 'Error Code'},
                {'name': 'ErrorDesc',  'type': 'string', 'label': 'Error Description'},
            ],
        }
    ],
    'uuid': str(uuid.uuid4()),
}

# ─── IF/ELSE block ─────────────────────────────────────────────────────────────
if_block = {
    'number': 7, 'keyword': 'if',
    'title': 'Check CIU Result',
    'input': {
        'type': 'compound', 'operand': 'and',
        'conditions': [{'operand': 'equals_to', 'lhs': http('CheckResult'), 'rhs': 'TRUE',
                        'uuid': str(uuid.uuid4())}],
    },
    'block': [
        oracle_sp(8, SP5A_AS, 'GLD_SCHEMA.ACCLOGCHECKREPLY', SP5A_PARAMS,
                  'Log Check Reply — ACCLOGCHECKREPLY (CIU TRUE path)'),
        {
            'number': 9, 'keyword': 'else', 'input': {},
            'block': [
                oracle_sp(10, SP5B_AS, 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP5B_PARAMS,
                          'Log Check Reply Error — ACCLOGCHECKREPLYERROR (CIU FALSE path)'),
            ],
            'uuid': str(uuid.uuid4()),
        },
    ],
    'uuid': str(uuid.uuid4()),
}

# ─── send_reply step ───────────────────────────────────────────────────────────
send_reply_step = {
    'number': 12, 'keyword': 'action',
    'provider': 'workato_service', 'name': 'send_reply',
    'as': REPLY_AS,
    'dynamicPickListSelection': {},
    'toggleCfg': {'reply.status': True},
    'input': {
        'reply_type': 'success',
        'reply': {'status': 'COMPLIANCE_CHECK_COMPLETE'},
    },
    'extended_input_schema': [
        {
            'label': 'Reply', 'name': 'reply', 'type': 'object',
            'properties': [
                {
                    'control_type': 'text', 'label': 'Status', 'name': 'status',
                    'type': 'string', 'optional': False,
                }
            ],
        }
    ],
    'uuid': str(uuid.uuid4()),
}

# ─── catch block ──────────────────────────────────────────────────────────────
catch_block = {
    'number': 13, 'keyword': 'catch',
    'as': CATCH_AS,
    'input': {'max_retry_count': '0', 'retry_interval': '2'},
    'block': [
        oracle_sp(14, SP_ERR_AS, 'GLD_SCHEMA.ACCLOGCHECKREPLYERROR', SP_CATCH_PARAMS,
                  'CATCH — Log System Error (ACCLOGCHECKREPLYERROR)'),
    ],
    'uuid': str(uuid.uuid4()),
}

# ─── try block ────────────────────────────────────────────────────────────────
try_block = {
    'number': 1, 'keyword': 'try', 'input': {},
    'block': [
        oracle_sp(2, SP1_AS,   'GLD_SCHEMA.ACCLOGCHECKREQUEST', SP1_PARAMS,
                  'Step 1 — Log Check Request (ACCLOGCHECKREQUEST, 25 params)'),
        oracle_select(3, SEL1B_AS,
                      'SELECT ACCCHECKREQUESTID FROM GLD_SCHEMA.ACCCHECKREQUEST '
                      'WHERE REQUESTORSYSTEMREQUESTID = ' + trig('RequestorSystemRequestID'),
                      'Step 1b — Get Check Request ID (follow-up SELECT)'),
        oracle_sp(4, SP2_AS,   'GLD_SCHEMA.LOGXMLREQUEST', SP2_PARAMS,
                  'Step 2 — Log Check Request XML (LOGXMLREQUEST, 5 params)'),
        ciu_step,
        oracle_sp(6, SP4_AS,   'GLD_SCHEMA.ACCUPDATECIUREFNBR', SP4_PARAMS,
                  'Step 4 — Update CIU Reference (ACCUPDATECIUREFNBR, 2 params)'),
        if_block,
        oracle_select(11, SEL6_AS, SELECT_6_SQL,
                      'Step 6 — Select Customer and Request (28-col JOIN)'),
        send_reply_step,
        catch_block,
    ],
    'uuid': str(uuid.uuid4()),
}

# ─── Trigger ───────────────────────────────────────────────────────────────────
code = {
    'number': 0, 'keyword': 'trigger',
    'provider': 'workato_service', 'name': 'receive_request',
    'as': TRIG_AS,
    'input': {
        'service_name':       'Compliance Check',
        'request_schema_json': json.dumps(req_schema),
        'reply_schema_json':   json.dumps(reply_schema),
    },
    'block': [try_block],
    'uuid': str(uuid.uuid4()),
}

config = [
    {'keyword': 'application', 'provider': 'oracle',
     'account_id': ORACLE_CONN_ID, 'skip_validation': False},
    {'keyword': 'application', 'provider': 'workato_service',
     'account_id': None, 'skip_validation': False},
]

# ─── Push ──────────────────────────────────────────────────────────────────────
print(f'\nPushing NewRecipe2 to folder ID: {FOLDER_ID}')
resp, err = api_post('/recipes', {
    'recipe': {
        'name':        'NewRecipe2',
        'folder_id':   str(FOLDER_ID),
        'description': (
            'GLD Compliance Check — webMethods IS 6.5 GLDComplianceAdapterServices → Workato. '
            'Callable recipe: 25-field trigger (CustomerNbr…RequestorSystemRequestID), '
            'Oracle SPs: ACCLOGCHECKREQUEST, LOGXMLREQUEST, ACCUPDATECIUREFNBR, '
            'ACCLOGCHECKREPLY/ACCLOGCHECKREPLYERROR, 28-col SELECT JOIN. '
            'HTTP POST to CIU (URL placeholder — wire in GUI).'
        ),
        'code':   json.dumps(code),
        'config': json.dumps(config),
    }
})

if err:
    print(f'HTTP ERROR {err[0]}:\n{err[1][:1500]}')
else:
    recipe_id = resp.get('id')
    if recipe_id:
        print(f'\nSUCCESS — Recipe ID: {recipe_id}')
        print(f'URL: https://app.workato.com/recipes/{recipe_id}')
    else:
        print('No ID in response:')
        print(json.dumps(resp, indent=2)[:800])
