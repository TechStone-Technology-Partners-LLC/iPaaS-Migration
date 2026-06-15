"""
Generate all Boomi component XMLs for GLDComplianceAdapterServices migration.
Run after Boomi.md is finalized (Step 10).
Creates files in active-development/{profile.json,transform.map,connector-action,process}/

Usage:
  python scripts/gen_gld_cas_xml.py
  # Then push profiles first, note IDs, update map XML manually if needed.
"""
import os
import textwrap

FOLDER_ID = "Rjo4NjIxNDk3"
BRANCH_ID = "Qjo0NjEzODQ"
ACCOUNT_SUBFOLDER = "TPP-TechStone/MIG_gld_compliance"
CONNECTION_ID = "370bf544-60a9-4048-8197-0c442243571d"
PLACEHOLDER_ID = "00000000-0000-0000-0000-000000000000"

NS = 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bns="http://api.platform.boomi.com/"'


def component_wrapper(name, comp_type, subtype, description, inner_xml, comp_id=PLACEHOLDER_ID):
    sub = f' subType="{subtype}"' if subtype else ""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<bns:Component {NS} folderFullPath="{ACCOUNT_SUBFOLDER}" componentId="{comp_id}" version="1" name="{name}" type="{comp_type}"{sub} folderId="{FOLDER_ID}" branchName="main" branchId="{BRANCH_ID}">
  <bns:encryptedValues/>
  <bns:description>{description} | built with boomi-companion v1.0.0</bns:description>
  <bns:object>
{inner_xml}
  </bns:object>
</bns:Component>"""


# ─────────────────────────────────────────────────────────────────────────────
# JSON PROFILES
# ─────────────────────────────────────────────────────────────────────────────

def _data_format(dtype):
    if dtype == "number":
        return "<DataFormat><ProfileNumberFormat numberFormat=\"\"/></DataFormat>"
    return "<DataFormat><ProfileCharacterFormat/></DataFormat>"


def json_profile_xml(fields):
    """
    fields: list of (name, type) tuples — type is 'character', 'number', etc.
    Returns the JSONProfile inner XML (inside <bns:object>).
    Validated against Boomi API schema: DataElements, JSONRootValue, JSONObject, JSONObjectEntry.
    """
    entries = []
    for i, (fname, ftype) in enumerate(fields, start=3):
        dfmt = _data_format(ftype)
        entries.append(
            f'            <JSONObjectEntry dataType="{ftype}" isMappable="true" isNode="true" key="{i}" name="{fname}">\n'
            f'              {dfmt}\n'
            f'            </JSONObjectEntry>'
        )
    return """    <JSONProfile strict="false">
      <DataElements>
        <JSONRootValue dataType="character" isMappable="true" isNode="true" key="1" name="Root">
          <DataFormat><ProfileCharacterFormat/></DataFormat>
          <JSONObject isMappable="false" isNode="true" key="2" name="Object">
""" + "\n".join(entries) + """
          </JSONObject>
          <Qualifiers><QualifierList/></Qualifiers>
        </JSONRootValue>
      </DataElements>
      <tagLists/>
    </JSONProfile>"""


def write_profile(name, fields, description, base_dir):
    inner = json_profile_xml(fields)
    xml = component_wrapper(name, "profile.json", None, description, inner)
    path = os.path.join(base_dir, "profile.json", f"{name}.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAP COMPONENT
# ─────────────────────────────────────────────────────────────────────────────

def write_map(source_profile_id, target_profile_id, base_dir):
    name = "MIG_WM_GLD_MapTestSkill_Map"
    # Profile field keys (from profiles above):
    # Source: Root=1, Object=2, A1=3, A2=4, A3=5, A4=6, A5=7
    # Target: Root=1, Object=2, B1=3, B2=4, B3=5, B4=6, B5=7
    # Mappings:
    # Direct: A3(key=5 src) → B3(key=5 tgt)
    # fn1: A2(key=4 src) → fn1.input_A2(key=1) → fn1.output_B2(key=2) → B2(key=4 tgt)
    # fn2: A4(key=6 src) → fn2.input_A4(key=1) → fn2.output_B4(key=2) → B4(key=6 tgt)
    # Default: B1(key=3 tgt) = "2000"
    # B5: no mapping

    inner = f"""    <Map fromProfile="{source_profile_id}" toProfile="{target_profile_id}">
      <Mappings>
        <Mapping fromKey="5" fromType="profile" toKey="5" toType="profile"/>
        <Mapping fromKey="4" fromType="profile" toFunction="1" toKey="1" toType="function"/>
        <Mapping fromFunction="1" fromKey="2" fromType="function" toKey="4" toType="profile"/>
        <Mapping fromKey="6" fromType="profile" toFunction="2" toKey="1" toType="function"/>
        <Mapping fromFunction="2" fromKey="2" fromType="function" toKey="6" toType="profile"/>
      </Mappings>
      <Functions optimizeExecutionOrder="true">
        <FunctionStep cacheEnabled="true" category="Scripting" key="1" name="Conditional_A2"
                      position="1" sumEnabled="false" type="Scripting" x="10.0" y="10.0">
          <Inputs>
            <Input key="1" name="input_A2"/>
          </Inputs>
          <Outputs>
            <Output key="2" name="output_B2"/>
          </Outputs>
          <Configuration>
            <Scripting language="groovy2">
              <ScriptToExecute><![CDATA[if (input_A2 == "Config") {{
  output_B2 = "Yes"
}} else {{
  output_B2 = "False"
}}
return [output_B2]]]></ScriptToExecute>
              <Input dataType="character" index="1" name="input_A2"/>
              <Output index="2" name="output_B2"/>
            </Scripting>
          </Configuration>
        </FunctionStep>
        <FunctionStep cacheEnabled="true" category="Scripting" key="2" name="StringToInt_A4"
                      position="2" sumEnabled="false" type="Scripting" x="10.0" y="150.0">
          <Inputs>
            <Input key="1" name="input_A4"/>
          </Inputs>
          <Outputs>
            <Output key="2" name="output_B4"/>
          </Outputs>
          <Configuration>
            <Scripting language="groovy2">
              <ScriptToExecute><![CDATA[def s = input_A4 ?: "0"
output_B4 = Integer.parseInt(s.trim()).toString()
return [output_B4]]]></ScriptToExecute>
              <Input dataType="character" index="1" name="input_A4"/>
              <Output index="2" name="output_B4"/>
            </Scripting>
          </Configuration>
        </FunctionStep>
      </Functions>
      <Defaults>
        <Default toKey="3" value="2000"/>
      </Defaults>
      <DocumentCacheJoins/>
    </Map>"""

    xml = component_wrapper(name, "transform.map", None,
                            "Map test from Boomi Map To Test Skill.xlsx: Default/Groovy/Direct/Integer transformations", inner)
    path = os.path.join(base_dir, "transform.map", f"{name}.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# DB OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_insert_op_xml(query, object_type="GLD_SCHEMA"):
    return f"""    <Operation xmlns="" returnApplicationErrors="true" trackResponse="false">
      <Archiving directory="" enabled="false"/>
      <Configuration>
        <GenericOperationConfig customOperationType="CREATE" objectTypeId="{object_type}" operationType="CREATE" requestProfileType="json" responseProfileType="json">
          <field id="InsertionType" type="string" value="Standard Insert"/>
          <field id="query" type="string" value="{query}"/>
          <field id="batchCount" type="integer"/>
          <field id="maxFieldSize" type="integer"/>
          <Options>
            <InsertOptions>
              <Fields>
                <ConnectorObject name="{object_type}">
                  <FieldList/>
                </ConnectorObject>
              </Fields>
            </InsertOptions>
          </Options>
        </GenericOperationConfig>
      </Configuration>
      <Tracking><TrackedFields/></Tracking>
      <Caching/>
    </Operation>"""


def db_get_op_xml(query, object_type="GLD_SCHEMA"):
    return f"""    <Operation xmlns="" returnApplicationErrors="true" trackResponse="false">
      <Archiving directory="" enabled="false"/>
      <Configuration>
        <GenericOperationConfig customOperationType="GET" objectTypeId="{object_type}" operationType="EXECUTE" requestProfileType="json" responseProfileType="json">
          <field id="GetType" type="string" value="Standard Get"/>
          <field id="INClause" type="boolean" value="false"/>
          <field id="query" type="string" value="{query}"/>
          <field id="linkElement" type="string" value=""/>
          <field id="maxRows" type="integer" value="1000"/>
          <field id="maxFieldSize" type="integer"/>
          <field id="batchCount" type="integer"/>
          <field id="fetchSize" type="integer" value="100"/>
          <Options>
            <QueryOptions>
              <Fields>
                <ConnectorObject name="{object_type}">
                  <FieldList/>
                </ConnectorObject>
              </Fields>
              <Inputs/>
            </QueryOptions>
          </Options>
        </GenericOperationConfig>
      </Configuration>
      <Tracking><TrackedFields/></Tracking>
      <Caching/>
    </Operation>"""


SELECT_SQL = (
    "SELECT DISTINCT "
    "t1.ACCCUSTOMERID, t1.CUSTOMERNBR, t1.CUSTOMERTYPE, t1.BUSINESSNAME, "
    "t1.FIRSTNAME, t1.MIDDLENAME, t1.LASTNAME, "
    "t1.ADDRESSLINE1, t1.ADDRESSLINE2, t1.ADDRESSLINE3, t1.ADDRESSLINE4, "
    "t1.CITY, t1.STATE, t1.ZIP, t1.COUNTRYCODE, t1.SSNTIN, "
    "t1.PARTYTYPE, t1.DOB, "
    "t2.ACCCHECKREQUESTID, t2.APPLICATIONNBR, t2.CHANNEL, t2.LOB, "
    "t2.PRODUCTCODE, t2.SUBPRODUCTCODE, t2.POSTBACK, "
    "t2.COMPLIANCEREPLYEMAIL, t2.CIUREFNBR, t2.REQUESTTIMESTAMP "
    "FROM GLD_SCHEMA.ACCCUSTOMER t1 "
    "JOIN GLD_SCHEMA.ACCCHECKREQUEST t2 ON t1.ACCCUSTOMERID = t2.ACCCUSTOMERID "
    "WHERE t2.CIUREFNBR = ?"
)

OPERATIONS = [
    ("MIG_WM_GLD_LogCheckRequest_Operation",
     "SP ACCLOGCHECKREQUEST — 25 IN params (customer/request fields), OUT: ACCCHECKREQUESTID",
     "insert",
     "{call GLD_SCHEMA.ACCLOGCHECKREQUEST(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}"),
    ("MIG_WM_GLD_LogCheckRequestXML_Operation",
     "SP LOGXMLREQUEST — 5 IN params (ApplicationID, raw XML, 3 identifiers)",
     "insert",
     "{call GLD_SCHEMA.LOGXMLREQUEST(?,?,?,?,?)}"),
    ("MIG_WM_GLD_LogCheckReply_Operation",
     "SP ACCLOGCHECKREPLY — 3 IN params (CIURefNbr, CheckType, Result)",
     "insert",
     "{call GLD_SCHEMA.ACCLOGCHECKREPLY(?,?,?)}"),
    ("MIG_WM_GLD_LogCheckReplyError_Operation",
     "SP ACCLOGCHECKREPLYERROR — 4 IN params (ErrorType, ErrorCode, ErrorDesc, CIURefNbr)",
     "insert",
     "{call GLD_SCHEMA.ACCLOGCHECKREPLYERROR(?,?,?,?)}"),
    ("MIG_WM_GLD_SelectCustomerRequest_Operation",
     "SELECT JOIN ACCCUSTOMER + ACCCHECKREQUEST — WHERE t2.CIUREFNBR = ? — 28 output fields",
     "get",
     SELECT_SQL),
    ("MIG_WM_GLD_UpdateCIURefNbr_Operation",
     "SP ACCUPDATECIUREFNBR — 2 IN params (ACCCHECKREQUESTID, CIUREFNBR)",
     "insert",
     "{call GLD_SCHEMA.ACCUPDATECIUREFNBR(?,?)}"),
    ("MIG_WM_GLD_PurgeData_Operation",
     "SP ACCPURGEDATA — no params, deletes old compliance records",
     "insert",
     "{call GLD_SCHEMA.ACCPURGEDATA()}"),
]


def write_operations(base_dir):
    for name, desc, op_type, query in OPERATIONS:
        if op_type == "insert":
            inner = db_insert_op_xml(query)
        else:
            inner = db_get_op_xml(query)
        xml = component_wrapper(name, "connector-action", "officialboomi-X3979C-dbv2da-prod",
                                desc, inner)
        path = os.path.join(base_dir, "connector-action", f"{name}.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"  Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# PROCESS
# ─────────────────────────────────────────────────────────────────────────────

def write_process(op_ids, map_id, base_dir):
    """
    op_ids: dict with keys matching operation names → their Boomi component IDs
    map_id: ID of MIG_WM_GLD_MapTestSkill_Map (or placeholder)
    """
    logcheck_req_id = op_ids.get("MIG_WM_GLD_LogCheckRequest_Operation", PLACEHOLDER_ID)
    logcheck_xml_id = op_ids.get("MIG_WM_GLD_LogCheckRequestXML_Operation", PLACEHOLDER_ID)
    logreply_id = op_ids.get("MIG_WM_GLD_LogCheckReply_Operation", PLACEHOLDER_ID)
    logreply_err_id = op_ids.get("MIG_WM_GLD_LogCheckReplyError_Operation", PLACEHOLDER_ID)
    select_id = op_ids.get("MIG_WM_GLD_SelectCustomerRequest_Operation", PLACEHOLDER_ID)
    update_ciu_id = op_ids.get("MIG_WM_GLD_UpdateCIURefNbr_Operation", PLACEHOLDER_ID)

    # DPP Set Properties macro builder
    def make_dpps(entries):
        """entries: list of (name, key_num, valueType, value_spec)"""
        lines = []
        for idx, (dname, key_num, vtype, vspec) in enumerate(entries, start=1):
            lines.append(f'          <dynamicDocProperty key="{idx}" name="{dname}" valueType="{vtype}">{vspec}</dynamicDocProperty>')
        return "\n".join(lines)

    # shape2 DDPs — extract 21 input fields from incoming JSON
    input_ddps = [
        ("DPP_CUSTOMER_NBR", 3, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/CustomerNbr"/>'),
        ("DPP_CUSTOMER_TYPE", 4, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/CustomerType"/>'),
        ("DPP_PARTY_TYPE", 5, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/PartyType"/>'),
        ("DPP_BUSINESS_NAME", 6, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/Businessname"/>'),
        ("DPP_APPLICATION_NBR", 7, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/ApplicationNbr"/>'),
        ("DPP_CHANNEL", 8, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/Channel"/>'),
        ("DPP_LOB", 9, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/LOB"/>'),
        ("DPP_PRODUCT_CODE", 10, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/ProductCode"/>'),
        ("DPP_SUB_PRODUCT_CODE", 11, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/SubProductCode"/>'),
        ("DPP_POSTBACK", 12, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/PostBack"/>'),
        ("DPP_COMPLIANCE_REPLY_EMAIL", 13, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/ComplianceReplyEmail"/>'),
        ("DPP_FIRST_NAME", 14, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/FirstName"/>'),
        ("DPP_MIDDLE_NAME", 15, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/MiddleName"/>'),
        ("DPP_LAST_NAME", 16, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/LastName"/>'),
        ("DPP_ADDRESS_LINE1", 17, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/AddressLine1"/>'),
        ("DPP_STATE", 18, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/State"/>'),
        ("DPP_ZIP", 19, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/Zip"/>'),
        ("DPP_COUNTRY_CODE", 20, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/CountryCode"/>'),
        ("DPP_SSNTIN", 21, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/SSNTIN"/>'),
        ("DPP_DOB", 22, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/DOB"/>'),
        ("DPP_REQUESTOR_SYSTEM_REQUEST_ID", 23, "profile", '<propertyvalue name="" profileId="PLACEHOLDER" xpath="payload/RequestorSystemRequestID"/>'),
    ]

    def make_set_props_shape(shape_id, label, x, y, ddps_xml):
        return f"""      <shape image="documentproperties_icon" name="{shape_id}" shapetype="documentproperties" userlabel="{label}" x="{x}" y="{y}">
        <configuration>
          <dynamicDocProperties>
{ddps_xml}
          </dynamicDocProperties>
        </configuration>
      </shape>"""

    # Build shape2 Set Properties XML
    shape2_ddps = []
    for idx, (dname, key_num, vtype, vspec) in enumerate(input_ddps, start=1):
        # Use static for now (profile xpath needs actual profile ID — placeholder note)
        shape2_ddps.append(
            f'            <dynamicDocProperty key="{idx}" name="{dname}" valueType="static">'
            f'<parametervalue key="{idx}" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>'
        )

    shape2_ddps_xml = "\n".join(shape2_ddps)

    # Message shape helper — builds a JSON body from DPPs using {N} substitution
    def message_shape(shape_id, label, x, y, message_body, num_params):
        params = "\n".join(
            f'          <parametervalue key="{i}" valueType="process">'
            f'<processparameter processproperty="DPP_PARAM_{i}" processpropertydefaultvalue=""/>'
            f'</parametervalue>'
            for i in range(1, num_params + 1)
        )
        return f"""      <shape image="message_icon" name="{shape_id}" shapetype="message" userlabel="{label}" x="{x}" y="{y}">
        <configuration>
          <messagetemplates>
            <messagetemplate contentType="application/json" messagetemplate="{message_body}"/>
          </messagetemplates>
          <parameters>
{params}
          </parameters>
        </configuration>
      </shape>"""

    inner = f"""    <process xmlns="" allowSimultaneous="false" enableUserLog="false" execMode="general" purgeImmediately="false" updateRunDates="false" workload="general">
      <shapes>
        <shape image="start_icon" name="shape1" shapetype="start" userlabel="Start" x="48" y="48">
          <configuration>
            <start actiontype="passthrough"/>
          </configuration>
        </shape>
        <shape image="documentproperties_icon" name="shape2" shapetype="documentproperties" userlabel="Extract Input DDPs" x="208" y="48">
          <configuration>
            <dynamicDocProperties>
              <dynamicDocProperty key="1" name="DPP_CUSTOMER_NBR" valueType="static"><parametervalue key="1" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="2" name="DPP_CUSTOMER_TYPE" valueType="static"><parametervalue key="2" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="3" name="DPP_PARTY_TYPE" valueType="static"><parametervalue key="3" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="4" name="DPP_BUSINESS_NAME" valueType="static"><parametervalue key="4" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="5" name="DPP_APPLICATION_NBR" valueType="static"><parametervalue key="5" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="6" name="DPP_CHANNEL" valueType="static"><parametervalue key="6" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="7" name="DPP_LOB" valueType="static"><parametervalue key="7" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="8" name="DPP_PRODUCT_CODE" valueType="static"><parametervalue key="8" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="9" name="DPP_SUB_PRODUCT_CODE" valueType="static"><parametervalue key="9" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="10" name="DPP_POSTBACK" valueType="static"><parametervalue key="10" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="11" name="DPP_COMPLIANCE_REPLY_EMAIL" valueType="static"><parametervalue key="11" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="12" name="DPP_FIRST_NAME" valueType="static"><parametervalue key="12" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="13" name="DPP_MIDDLE_NAME" valueType="static"><parametervalue key="13" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="14" name="DPP_LAST_NAME" valueType="static"><parametervalue key="14" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="15" name="DPP_ADDRESS_LINE1" valueType="static"><parametervalue key="15" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="16" name="DPP_STATE" valueType="static"><parametervalue key="16" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="17" name="DPP_ZIP" valueType="static"><parametervalue key="17" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="18" name="DPP_COUNTRY_CODE" valueType="static"><parametervalue key="18" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="19" name="DPP_SSNTIN" valueType="static"><parametervalue key="19" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="20" name="DPP_DOB" valueType="static"><parametervalue key="20" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
              <dynamicDocProperty key="21" name="DPP_REQUESTOR_SYSTEM_REQUEST_ID" valueType="static"><parametervalue key="21" valueType="static"><staticvalue value=""/></parametervalue></dynamicDocProperty>
            </dynamicDocProperties>
          </configuration>
        </shape>
        <shape image="catcherrors_icon" name="shape3" shapetype="catcherrors" userlabel="Try/Catch" x="368" y="48">
          <configuration>
            <catcherrors catchAll="true" retryAttempts="0" retryInterval="0"/>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape4" shapetype="message" userlabel="Build LogCheckRequest Input" x="528" y="48">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;CUSTOMERNBR\&quot;:\&quot;{{1}}\&quot;,\&quot;CUSTOMERTYPE\&quot;:\&quot;{{2}}\&quot;,\&quot;PARTYTYPE\&quot;:\&quot;{{3}}\&quot;,\&quot;BUSINESSNAME\&quot;:\&quot;{{4}}\&quot;,\&quot;APPLICATIONNBR\&quot;:\&quot;{{5}}\&quot;,\&quot;CHANNEL\&quot;:\&quot;{{6}}\&quot;,\&quot;LOB\&quot;:\&quot;{{7}}\&quot;,\&quot;PRODUCTCODE\&quot;:\&quot;{{8}}\&quot;,\&quot;SUBPRODUCTCODE\&quot;:\&quot;{{9}}\&quot;,\&quot;POSTBACK\&quot;:\&quot;{{10}}\&quot;,\&quot;COMPLIANCEREPLYEMAIL\&quot;:\&quot;{{11}}\&quot;,\&quot;FIRSTNAME\&quot;:\&quot;{{12}}\&quot;,\&quot;MIDDLENAME\&quot;:\&quot;{{13}}\&quot;,\&quot;LASTNAME\&quot;:\&quot;{{14}}\&quot;,\&quot;ADDRESSLINE1\&quot;:\&quot;{{15}}\&quot;,\&quot;ADDRESSLINE2\&quot;:\&quot;\&quot;,\&quot;ADDRESSLINE3\&quot;:\&quot;\&quot;,\&quot;ADDRESSLINE4\&quot;:\&quot;\&quot;,\&quot;CITY\&quot;:\&quot;\&quot;,\&quot;STATE\&quot;:\&quot;{{16}}\&quot;,\&quot;ZIP\&quot;:\&quot;{{17}}\&quot;,\&quot;COUNTRYCODE\&quot;:\&quot;{{18}}\&quot;,\&quot;SSNTIN\&quot;:\&quot;{{19}}\&quot;,\&quot;DOB\&quot;:\&quot;{{20}}\&quot;,\&quot;REQUESTORSYSTEMREQUESTID\&quot;:\&quot;{{21}}\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_CUSTOMER_NBR" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="2" valueType="process"><processparameter processproperty="DPP_CUSTOMER_TYPE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="3" valueType="process"><processparameter processproperty="DPP_PARTY_TYPE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="4" valueType="process"><processparameter processproperty="DPP_BUSINESS_NAME" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="5" valueType="process"><processparameter processproperty="DPP_APPLICATION_NBR" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="6" valueType="process"><processparameter processproperty="DPP_CHANNEL" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="7" valueType="process"><processparameter processproperty="DPP_LOB" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="8" valueType="process"><processparameter processproperty="DPP_PRODUCT_CODE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="9" valueType="process"><processparameter processproperty="DPP_SUB_PRODUCT_CODE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="10" valueType="process"><processparameter processproperty="DPP_POSTBACK" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="11" valueType="process"><processparameter processproperty="DPP_COMPLIANCE_REPLY_EMAIL" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="12" valueType="process"><processparameter processproperty="DPP_FIRST_NAME" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="13" valueType="process"><processparameter processproperty="DPP_MIDDLE_NAME" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="14" valueType="process"><processparameter processproperty="DPP_LAST_NAME" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="15" valueType="process"><processparameter processproperty="DPP_ADDRESS_LINE1" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="16" valueType="process"><processparameter processproperty="DPP_STATE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="17" valueType="process"><processparameter processproperty="DPP_ZIP" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="18" valueType="process"><processparameter processproperty="DPP_COUNTRY_CODE" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="19" valueType="process"><processparameter processproperty="DPP_SSNTIN" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="20" valueType="process"><processparameter processproperty="DPP_DOB" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="21" valueType="process"><processparameter processproperty="DPP_REQUESTOR_SYSTEM_REQUEST_ID" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape5" shapetype="connectoraction" userlabel="LogCheckRequest" x="688" y="48">
          <configuration>
            <connector actionType="CREATE" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{logcheck_req_id}"/>
          </configuration>
        </shape>
        <shape image="documentproperties_icon" name="shape6" shapetype="documentproperties" userlabel="Capture Request ID (TODO: wire after CIU)" x="848" y="48">
          <configuration>
            <dynamicDocProperties>
              <dynamicDocProperty key="1" name="DPP_ACC_CHECK_REQUEST_ID" valueType="static"><parametervalue key="1" valueType="static"><staticvalue value="PENDING_CIU_WIRE"/></parametervalue></dynamicDocProperty>
            </dynamicDocProperties>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape7" shapetype="message" userlabel="Build LogCheckRequestXML Input" x="1008" y="48">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;APPLICATIONID\&quot;:\&quot;{{1}}\&quot;,\&quot;REQUEST\&quot;:\&quot;{{2}}\&quot;,\&quot;REQUESTIDENTIFIER1\&quot;:\&quot;\&quot;,\&quot;REQUESTIDENTIFIER2\&quot;:\&quot;\&quot;,\&quot;REQUESTIDENTIFIER3\&quot;:\&quot;\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_APPLICATION_NBR" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="2" valueType="process"><processparameter processproperty="DPP_REQUESTOR_SYSTEM_REQUEST_ID" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape8" shapetype="connectoraction" userlabel="LogCheckRequestXML" x="1168" y="48">
          <configuration>
            <connector actionType="CREATE" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{logcheck_xml_id}"/>
          </configuration>
        </shape>
        <shape image="documentproperties_icon" name="shape9" shapetype="documentproperties" userlabel="Set CIU Placeholder (REPLACE with CIU connector)" x="1328" y="48">
          <configuration>
            <dynamicDocProperties>
              <dynamicDocProperty key="1" name="DPP_CIU_REF_NBR" valueType="static"><parametervalue key="1" valueType="static"><staticvalue value="PENDING_CIU_WIRE"/></parametervalue></dynamicDocProperty>
            </dynamicDocProperties>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape10" shapetype="message" userlabel="Build UpdateCIURefNbr Input" x="1488" y="48">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;ACCCHECKREQUESTID\&quot;:\&quot;{{1}}\&quot;,\&quot;CIUREFNBR\&quot;:\&quot;{{2}}\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_ACC_CHECK_REQUEST_ID" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="2" valueType="process"><processparameter processproperty="DPP_CIU_REF_NBR" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape11" shapetype="connectoraction" userlabel="UpdateCIURefNbr" x="1648" y="48">
          <configuration>
            <connector actionType="CREATE" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{update_ciu_id}"/>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape12" shapetype="message" userlabel="Build SelectCustomer Input" x="1808" y="48">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;CIUREFNBR\&quot;:\&quot;{{1}}\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_CIU_REF_NBR" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape13" shapetype="connectoraction" userlabel="SelectCustomerAndRequest" x="1968" y="48">
          <configuration>
            <connector actionType="GET" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{select_id}"/>
          </configuration>
        </shape>
        <shape image="map_icon" name="shape14" shapetype="map" userlabel="Map Result to DDPs" x="2128" y="48">
          <configuration>
            <map mapId="{map_id}"/>
          </configuration>
        </shape>
        <shape image="decision_icon" name="shape15" shapetype="decision" userlabel="Check Passed?" name="Check Passed?" x="2288" y="48">
          <configuration>
            <decision comparison="equals">
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_CHECK_RESULT" processpropertydefaultvalue=""/></parametervalue>
              <parametervalue key="2" valueType="static"><staticvalue value="TRUE"/></parametervalue>
            </decision>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape16" shapetype="message" userlabel="Build LogCheckReply Input" x="2448" y="48">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;CIUREFNBR\&quot;:\&quot;{{1}}\&quot;,\&quot;CHECKTYPE\&quot;:\&quot;GLD\&quot;,\&quot;RESULT\&quot;:\&quot;TRUE\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_CIU_REF_NBR" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape17" shapetype="connectoraction" userlabel="LogCheckReply" x="2608" y="48">
          <configuration>
            <connector actionType="CREATE" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{logreply_id}"/>
          </configuration>
        </shape>
        <shape image="stop_icon" name="shape18" shapetype="stop" userlabel="Success" x="2768" y="48">
          <configuration>
            <stop continueProcessing="true"/>
          </configuration>
        </shape>
        <shape image="message_icon" name="shape19" shapetype="message" userlabel="Build LogCheckReplyError Input" x="2448" y="248">
          <configuration>
            <messagetemplates>
              <messagetemplate contentType="application/json" messagetemplate="{{\&quot;ERRORTYPE\&quot;:\&quot;{{1}}\&quot;,\&quot;ERRORCODE\&quot;:\&quot;{{2}}\&quot;,\&quot;ERRORDESC\&quot;:\&quot;{{3}}\&quot;,\&quot;CIUREFNBR\&quot;:\&quot;{{4}}\&quot;}}"/>
            </messagetemplates>
            <parameters>
              <parametervalue key="1" valueType="static"><staticvalue value="VALIDATION_FAILURE"/></parametervalue>
              <parametervalue key="2" valueType="static"><staticvalue value="CHECK_FAILED"/></parametervalue>
              <parametervalue key="3" valueType="static"><staticvalue value="Compliance check did not pass"/></parametervalue>
              <parametervalue key="4" valueType="process"><processparameter processproperty="DPP_CIU_REF_NBR" processpropertydefaultvalue=""/></parametervalue>
            </parameters>
          </configuration>
        </shape>
        <shape image="connector_icon" name="shape20" shapetype="connectoraction" userlabel="LogCheckReplyError" x="2608" y="248">
          <configuration>
            <connector actionType="CREATE" connectorType="officialboomi-X3979C-dbv2da-prod" operationId="{logreply_err_id}"/>
          </configuration>
        </shape>
        <shape image="stop_icon" name="shape21" shapetype="stop" userlabel="Fail" x="2768" y="248">
          <configuration>
            <stop continueProcessing="false"/>
          </configuration>
        </shape>
        <shape image="notify_icon" name="shape22" shapetype="notify" userlabel="Log Error" x="528" y="248">
          <configuration>
            <notify notifyType="flow.notify" logLevel="WARNING">
              <messagetemplates>
                <messagetemplate contentType="text/plain" messagetemplate="GLD Compliance error: {{1}}"/>
              </messagetemplates>
              <parameters>
                <parametervalue key="1" valueType="process"><processparameter processproperty="DPP_ERROR_DESC" processpropertydefaultvalue="unknown error"/></parametervalue>
              </parameters>
            </notify>
          </configuration>
        </shape>
        <shape image="stop_icon" name="shape23" shapetype="stop" userlabel="Error" x="688" y="248">
          <configuration>
            <stop continueProcessing="false"/>
          </configuration>
        </shape>
      </shapes>
      <dragPoints>
        <dragPoint fromShape="shape1" toShape="shape2"/>
        <dragPoint fromShape="shape2" toShape="shape3"/>
        <dragPoint fromShape="shape3" identifier="default" toShape="shape4"/>
        <dragPoint fromShape="shape3" identifier="error" toShape="shape22"/>
        <dragPoint fromShape="shape4" toShape="shape5"/>
        <dragPoint fromShape="shape5" toShape="shape6"/>
        <dragPoint fromShape="shape6" toShape="shape7"/>
        <dragPoint fromShape="shape7" toShape="shape8"/>
        <dragPoint fromShape="shape8" toShape="shape9"/>
        <dragPoint fromShape="shape9" toShape="shape10"/>
        <dragPoint fromShape="shape10" toShape="shape11"/>
        <dragPoint fromShape="shape11" toShape="shape12"/>
        <dragPoint fromShape="shape12" toShape="shape13"/>
        <dragPoint fromShape="shape13" toShape="shape14"/>
        <dragPoint fromShape="shape14" toShape="shape15"/>
        <dragPoint fromShape="shape15" identifier="true" toShape="shape16"/>
        <dragPoint fromShape="shape15" identifier="false" toShape="shape19"/>
        <dragPoint fromShape="shape16" toShape="shape17"/>
        <dragPoint fromShape="shape17" toShape="shape18"/>
        <dragPoint fromShape="shape19" toShape="shape20"/>
        <dragPoint fromShape="shape20" toShape="shape21"/>
        <dragPoint fromShape="shape22" toShape="shape23"/>
      </dragPoints>
    </process>"""

    xml = component_wrapper(
        "MIG_WM_GLDComplianceAdapterServices_Process",
        "process", None,
        "GLDComplianceAdapterServices — webMethods to Boomi. 7 Oracle SP/SELECT operations. PII guard enabled (enableUserLog=false). Migrate from GLDComplianceAdapterServices webMethods package.",
        inner
    )
    path = os.path.join(base_dir, "process", "MIG_WM_GLDComplianceAdapterServices_Process.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"  Written: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = "active-development"
    for d in ["profile.json", "transform.map", "connector-action", "process"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    print("=== Writing JSON Profiles ===")
    write_profile(
        "MIG_WM_GLD_MapTest_Source_Profile",
        [("A1", "character"), ("A2", "character"), ("A3", "character"),
         ("A4", "character"), ("A5", "character")],
        "Map test source profile — fields A1-A5 from Boomi Map To Test Skill.xlsx",
        base
    )
    write_profile(
        "MIG_WM_GLD_MapTest_Target_Profile",
        [("B1", "character"), ("B2", "character"), ("B3", "character"),
         ("B4", "character"), ("B5", "character")],
        "Map test target profile — fields B1-B5 from Boomi Map To Test Skill.xlsx",
        base
    )

    print("\n=== Writing Map (with PLACEHOLDER profile IDs) ===")
    write_map(PLACEHOLDER_ID, PLACEHOLDER_ID, base)
    print("  NOTE: update map XML with real profile IDs after pushing profiles!")

    print("\n=== Writing DB Operations ===")
    write_operations(base)

    print("\n=== Writing Process (with PLACEHOLDER operation IDs) ===")
    write_process({}, PLACEHOLDER_ID, base)
    print("  NOTE: update process XML with real operation IDs after pushing operations!")

    print("\nDone. Push order:")
    print("  1. profile.json/MIG_WM_GLD_MapTest_Source_Profile.xml")
    print("  2. profile.json/MIG_WM_GLD_MapTest_Target_Profile.xml")
    print("  3. Update transform.map XML with real profile IDs, then push map")
    print("  4. Push all 7 connector-action/*.xml (no deps)")
    print("  5. Update process XML with real operation IDs, then push process")
