"""
Generate MIG_WM_GLDComplianceAdapterServices_Process.xml using the validated Boomi process schema.
All 7 operation IDs are filled from the previous push session.

Usage:
  python scripts/gen_gld_process.py
"""
import os
import xml.etree.ElementTree as ET

FOLDER_ID = "Rjo4NjIxNDk3"
CONNECTION_ID = "370bf544-60a9-4048-8197-0c442243571d"

OP = {
    "logCheckRequest":    "c398179a-9679-4727-b666-9efe7c0ed969",
    "logCheckRequestXML": "f9571d99-a2bd-4945-893a-5ac49ace2770",
    "logCheckReply":      "50970f87-b37a-4d82-8244-92afff5fbb17",
    "logCheckReplyError": "1d853cdf-75fb-4603-9cbc-7aa3d055b5ad",
    "selectCustomer":     "72e81746-77ca-4351-b866-1bad57a1fecf",
    "updateCIURefNbr":    "ae2ca2df-cd5c-47c9-bcdf-bb76c2857244",
    "purgeData":          "b2488392-5fc5-4c1f-9a09-91210a3188bd",
}
MAP_ID = "9f06d114-4131-4e80-adf8-891da4563641"

x_start = 48.0
x_step = 200.0
y_main = 46.0
y_false = 246.0
y_catch = 446.0


def shape_x(n):
    return x_start + (n - 1) * x_step


def dragpoint(name, to_shape, fx, fy, identifier=None):
    ident = (' identifier="' + identifier + '"') if identifier else ""
    return (
        '<dragpoint' + ident + ' name="' + name + '" toShape="' + to_shape + '" '
        'x="' + str(fx + 152.0) + '" y="' + str(fy + 10.0) + '"/>'
    )


def dpp_read_param(key, dpp_name):
    """trackparameter for reading a Dynamic Process Property in Message/Notify shapes."""
    return (
        '<parametervalue key="' + str(key) + '" valueType="track">'
        '<trackparameter defaultValue="" propertyId="process.' + dpp_name + '" '
        'propertyName="Dynamic Process Property - ' + dpp_name + '"/>'
        '</parametervalue>'
    )


def static_write_param(key, val=""):
    """staticparameter for Set Properties (writing a DPP to a literal)."""
    return (
        '<parametervalue key="' + str(key) + '" valueType="static">'
        '<staticparameter staticproperty="' + val + '"/>'
        '</parametervalue>'
    )


def dpp_write_prop(dpp_name, source_param_xml):
    """One <documentproperty> element that writes to process.DPP_NAME."""
    return (
        '<documentproperty defaultValue="" isDynamicCredential="false" isTradingPartner="false" '
        'name="Dynamic Process Property - ' + dpp_name + '" persist="false" '
        'propertyId="process.' + dpp_name + '" shouldEncrypt="false">'
        '<sourcevalues>' + source_param_xml + '</sourcevalues></documentproperty>'
    )


def build_msg_template(fields):
    """
    Build a Boomi message template for a JSON body.

    fields: list of (json_field_name, dpp_name_or_None)
      dpp_name is not None -> substituted from DPP at runtime
      dpp_name is None     -> empty string literal in output JSON

    Boomi template escaping rule:
      Text inside '...' is literal.
      {N} outside single quotes = Nth parametervalue.
      Example: '{"key": "'{1}'"}'  produces  {"key": "<DPP_value>"}

    Returns: (msg_txt_string, params_xml_string)
    """
    segments = []   # list of str (literal text) or None (variable marker)
    params_xml = []
    p = 1

    segments.append('{"')
    first = True
    for fname, dpp in fields:
        if not first:
            segments.append(', "')
        first = False
        segments.append(fname + '": "')
        if dpp is not None:
            segments.append(None)
            params_xml.append(dpp_read_param(p, dpp))
            p += 1
        segments.append('"')
    segments.append("}")

    # Assemble template using single-quote literal/variable interleaving
    tpl = "'"
    var_idx = 1
    for seg in segments:
        if seg is None:
            tpl = tpl + "'"               # close literal
            tpl = tpl + "{" + str(var_idx) + "}"  # variable reference
            tpl = tpl + "'"               # reopen literal
            var_idx += 1
        else:
            tpl = tpl + seg
    tpl = tpl + "'"                       # close final literal

    return tpl, "\n            ".join(params_xml)


def connector_shape(n, x, y, label, action_type, op_key, next_shape):
    dp = dragpoint("shape" + str(n) + ".dp1", next_shape, x, y)
    return (
        '    <shape image="connectoraction_icon" name="shape' + str(n) + '" shapetype="connectoraction"\n'
        '      userlabel="' + label + '" x="' + str(x) + '" y="' + str(y) + '">\n'
        '      <configuration>\n'
        '        <connectoraction actionType="' + action_type + '" allowDynamicCredentials="NONE"\n'
        '          connectionId="' + CONNECTION_ID + '"\n'
        '          connectorType="officialboomi-X3979C-dbv2da-prod"\n'
        '          hideSettings="false"\n'
        '          operationId="' + OP[op_key] + '">\n'
        '          <parameters/>\n'
        '          <dynamicProperties/>\n'
        '        </connectoraction>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )


def message_shape(n, x, y, label, fields, next_shape):
    tpl, params = build_msg_template(fields)
    dp = dragpoint("shape" + str(n) + ".dp1", next_shape, x, y)
    return (
        '    <shape image="message_icon" name="shape' + str(n) + '" shapetype="message"\n'
        '      userlabel="' + label + '" x="' + str(x) + '" y="' + str(y) + '">\n'
        '      <configuration>\n'
        '        <message combined="false">\n'
        '          <msgTxt>' + tpl + '</msgTxt>\n'
        '          <msgParameters>\n'
        '            ' + params + '\n'
        '          </msgParameters>\n'
        '        </message>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )


def set_props_shape(n, x, y, label, dpp_writes_xml, next_shape):
    dp = dragpoint("shape" + str(n) + ".dp1", next_shape, x, y)
    return (
        '    <shape image="documentproperties_icon" name="shape' + str(n) + '" shapetype="documentproperties"\n'
        '      userlabel="' + label + '" x="' + str(x) + '" y="' + str(y) + '">\n'
        '      <configuration>\n'
        '        <documentproperties>\n'
        '          ' + dpp_writes_xml + '\n'
        '        </documentproperties>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )


def stop_shape(n, x, y, label, continue_val):
    cont = "true" if continue_val else "false"
    return (
        '    <shape image="stop_icon" name="shape' + str(n) + '" shapetype="stop"\n'
        '      userlabel="' + label + '" x="' + str(x) + '" y="' + str(y) + '">\n'
        '      <configuration><stop continue="' + cont + '"/></configuration>\n'
        '      <dragpoints/>\n'
        '    </shape>'
    )


def build_process():
    shapes = []

    # ── shape1: Start ────────────────────────────────────────────────
    s1x = shape_x(1)
    dp1 = dragpoint("shape1.dp1", "shape2", s1x, y_main)
    shapes.append(
        '    <shape image="start" name="shape1" shapetype="start"\n'
        '      userlabel="Start" x="' + str(s1x) + '" y="' + str(y_main) + '">\n'
        '      <configuration><noaction/></configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp1 + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )

    # ── shape2: Set Properties — extract DDPs ───────────────────────
    s2x = shape_x(2)
    dpp_names = [
        "DPP_CUSTOMER_NBR", "DPP_CUSTOMER_TYPE", "DPP_PARTY_TYPE",
        "DPP_BUSINESS_NAME", "DPP_APPLICATION_NBR", "DPP_CHANNEL",
        "DPP_LOB", "DPP_PRODUCT_CODE", "DPP_SUB_PRODUCT_CODE",
        "DPP_POSTBACK", "DPP_COMPLIANCE_REPLY_EMAIL",
        "DPP_FIRST_NAME", "DPP_MIDDLE_NAME", "DPP_LAST_NAME",
        "DPP_ADDRESS_LINE1", "DPP_STATE", "DPP_ZIP", "DPP_COUNTRY_CODE",
        "DPP_SSNTIN", "DPP_DOB", "DPP_REQUESTOR_SYSTEM_REQUEST_ID",
    ]
    dpp_writes = "\n          ".join(
        dpp_write_prop(name, static_write_param(i + 1, ""))
        for i, name in enumerate(dpp_names)
    )
    shapes.append(set_props_shape(
        2, s2x, y_main, "Extract Input DDPs (wire to input source)", dpp_writes, "shape3"
    ))

    # ── shape3: Try/Catch ────────────────────────────────────────────
    s3x = shape_x(3)
    dp3a = dragpoint("shape3.dp1", "shape4", s3x, y_main, identifier="default")
    dp3b = dragpoint("shape3.dp2", "shape22", s3x, y_catch, identifier="error")
    shapes.append(
        '    <shape image="catcherrors_icon" name="shape3" shapetype="catcherrors"\n'
        '      userlabel="Try/Catch" x="' + str(s3x) + '" y="' + str(y_main) + '">\n'
        '      <configuration>\n'
        '        <catcherrors catchAll="true" retryCount="0"/>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp3a + '\n'
        '        ' + dp3b + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )

    # ── shape4: Message — logCheckRequest (25 params) ────────────────
    lcr_fields = [
        ("CUSTOMERNBR", "DPP_CUSTOMER_NBR"),
        ("CUSTOMERTYPE", "DPP_CUSTOMER_TYPE"),
        ("PARTYTYPE", "DPP_PARTY_TYPE"),
        ("BUSINESSNAME", "DPP_BUSINESS_NAME"),
        ("APPLICATIONNBR", "DPP_APPLICATION_NBR"),
        ("CHANNEL", "DPP_CHANNEL"),
        ("LOB", "DPP_LOB"),
        ("PRODUCTCODE", "DPP_PRODUCT_CODE"),
        ("SUBPRODUCTCODE", "DPP_SUB_PRODUCT_CODE"),
        ("POSTBACK", "DPP_POSTBACK"),
        ("COMPLIANCEREPLYEMAIL", "DPP_COMPLIANCE_REPLY_EMAIL"),
        ("FIRSTNAME", "DPP_FIRST_NAME"),
        ("MIDDLENAME", "DPP_MIDDLE_NAME"),
        ("LASTNAME", "DPP_LAST_NAME"),
        ("ADDRESSLINE1", "DPP_ADDRESS_LINE1"),
        ("ADDRESSLINE2", None),
        ("ADDRESSLINE3", None),
        ("ADDRESSLINE4", None),
        ("CITY", None),
        ("STATE", "DPP_STATE"),
        ("ZIP", "DPP_ZIP"),
        ("COUNTRYCODE", "DPP_COUNTRY_CODE"),
        ("SSNTIN", "DPP_SSNTIN"),
        ("DOB", "DPP_DOB"),
        ("REQUESTORSYSTEMREQUESTID", "DPP_REQUESTOR_SYSTEM_REQUEST_ID"),
    ]
    shapes.append(message_shape(4, shape_x(4), y_main, "Build LogCheckRequest Input", lcr_fields, "shape5"))

    # ── shape5: DB — ACCLOGCHECKREQUEST ─────────────────────────────
    shapes.append(connector_shape(5, shape_x(5), y_main, "LogCheckRequest", "CREATE", "logCheckRequest", "shape6"))

    # ── shape6: Set Properties — request ID placeholder ─────────────
    shapes.append(set_props_shape(
        6, shape_x(6), y_main, "Capture Request ID (TODO: wire after CIU)",
        dpp_write_prop("DPP_ACC_CHECK_REQUEST_ID", static_write_param(1, "PENDING_CIU_WIRE")),
        "shape7"
    ))

    # ── shape7: Message — logCheckRequestXML (5 params) ──────────────
    lcrxml_fields = [
        ("APPLICATIONID", "DPP_APPLICATION_NBR"),
        ("REQUEST", "DPP_REQUESTOR_SYSTEM_REQUEST_ID"),
        ("REQUESTIDENTIFIER1", None),
        ("REQUESTIDENTIFIER2", None),
        ("REQUESTIDENTIFIER3", None),
    ]
    shapes.append(message_shape(7, shape_x(7), y_main, "Build LogCheckRequestXML Input", lcrxml_fields, "shape8"))

    # ── shape8: DB — LOGXMLREQUEST ───────────────────────────────────
    shapes.append(connector_shape(8, shape_x(8), y_main, "LogCheckRequestXML", "CREATE", "logCheckRequestXML", "shape9"))

    # ── shape9: Set Properties — CIU placeholder ────────────────────
    shapes.append(set_props_shape(
        9, shape_x(9), y_main, "Set CIU RefNbr - REPLACE with CIU connector call",
        dpp_write_prop("DPP_CIU_REF_NBR", static_write_param(1, "PENDING_CIU_WIRE")),
        "shape10"
    ))

    # ── shape10: Message — updateCIURefNbr (2 params) ────────────────
    ciu_fields = [
        ("ACCCHECKREQUESTID", "DPP_ACC_CHECK_REQUEST_ID"),
        ("CIUREFNBR", "DPP_CIU_REF_NBR"),
    ]
    shapes.append(message_shape(10, shape_x(10), y_main, "Build UpdateCIURefNbr Input", ciu_fields, "shape11"))

    # ── shape11: DB — ACCUPDATECIUREFNBR ────────────────────────────
    shapes.append(connector_shape(11, shape_x(11), y_main, "UpdateCIURefNbr", "CREATE", "updateCIURefNbr", "shape12"))

    # ── shape12: Message — selectCustomerRequest (1 param) ───────────
    sel_fields = [("CIUREFNBR", "DPP_CIU_REF_NBR")]
    shapes.append(message_shape(12, shape_x(12), y_main, "Build SelectCustomer Input", sel_fields, "shape13"))

    # ── shape13: DB — SELECT DISTINCT ────────────────────────────────
    shapes.append(connector_shape(13, shape_x(13), y_main, "SelectCustomerAndRequest", "GET", "selectCustomer", "shape14"))

    # ── shape14: Map ─────────────────────────────────────────────────
    s14x = shape_x(14)
    dp14 = dragpoint("shape14.dp1", "shape15", s14x, y_main)
    shapes.append(
        '    <shape image="map_icon" name="shape14" shapetype="map"\n'
        '      userlabel="Map Result to DDPs" x="' + str(s14x) + '" y="' + str(y_main) + '">\n'
        '      <configuration><map mapId="' + MAP_ID + '"/></configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp14 + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )

    # ── shape15: Decision ────────────────────────────────────────────
    s15x = shape_x(15)
    dp15a = dragpoint("shape15.dp1", "shape16", s15x, y_main, identifier="true")
    dp15b = dragpoint("shape15.dp2", "shape19", s15x, y_false, identifier="false")
    shapes.append(
        '    <shape image="decision_icon" name="shape15" shapetype="decision"\n'
        '      userlabel="Check Passed?" x="' + str(s15x) + '" y="' + str(y_main) + '">\n'
        '      <configuration>\n'
        '        <decision comparison="equals" name="Check Passed?">\n'
        '          <decisionvalue valueType="track">\n'
        '            <trackparameter defaultValue="" propertyId="process.DPP_CHECK_RESULT"\n'
        '                           propertyName="Dynamic Process Property - DPP_CHECK_RESULT"/>\n'
        '          </decisionvalue>\n'
        '          <decisionvalue valueType="static">\n'
        '            <staticparameter staticproperty="TRUE"/>\n'
        '          </decisionvalue>\n'
        '        </decision>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp15a + '\n'
        '        ' + dp15b + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )

    # ── TRUE PATH ────────────────────────────────────────────────────

    # ── shape16: Message — logCheckReply (3 params) ───────────────────
    reply_fields = [
        ("CIUREFNBR", "DPP_CIU_REF_NBR"),
        ("CHECKTYPE", None),
        ("RESULT", None),
    ]
    shapes.append(message_shape(16, shape_x(16), y_main, "Build LogCheckReply Input", reply_fields, "shape17"))

    # ── shape17: DB — ACCLOGCHECKREPLY ───────────────────────────────
    shapes.append(connector_shape(17, shape_x(17), y_main, "LogCheckReply", "CREATE", "logCheckReply", "shape18"))

    # ── shape18: Stop — success ──────────────────────────────────────
    shapes.append(stop_shape(18, shape_x(18), y_main, "Success", True))

    # ── FALSE PATH ───────────────────────────────────────────────────

    # ── shape19: Message — logCheckReplyError (4 params) ─────────────
    err_fields = [
        ("ERRORTYPE", None),
        ("ERRORCODE", None),
        ("ERRORDESC", None),
        ("CIUREFNBR", "DPP_CIU_REF_NBR"),
    ]
    shapes.append(message_shape(19, shape_x(16), y_false, "Build LogCheckReplyError Input", err_fields, "shape20"))

    # ── shape20: DB — ACCLOGCHECKREPLYERROR ──────────────────────────
    shapes.append(connector_shape(20, shape_x(17), y_false, "LogCheckReplyError", "CREATE", "logCheckReplyError", "shape21"))

    # ── shape21: Stop — fail ─────────────────────────────────────────
    shapes.append(stop_shape(21, shape_x(18), y_false, "Fail", False))

    # ── CATCH PATH ───────────────────────────────────────────────────

    # ── shape22: Notify ───────────────────────────────────────────────
    s22x = shape_x(4)
    dp22 = dragpoint("shape22.dp1", "shape23", s22x, y_catch)
    shapes.append(
        '    <shape image="notify_icon" name="shape22" shapetype="notify"\n'
        '      userlabel="Log Error" x="' + str(s22x) + '" y="' + str(y_catch) + '">\n'
        '      <configuration>\n'
        '        <notify disableEvent="true" enableUserLog="false" perExecution="false" title="">\n'
        '          <notifyMessage>GLD Compliance error: {1}</notifyMessage>\n'
        '          <notifyMessageLevel>WARNING</notifyMessageLevel>\n'
        '          <notifyParameters>\n'
        '            <parametervalue key="1" valueType="track">\n'
        '              <trackparameter defaultValue="" propertyId="meta.base.catcherrorsmessage"\n'
        '                             propertyName="Base - Try/Catch Message"/>\n'
        '            </parametervalue>\n'
        '          </notifyParameters>\n'
        '        </notify>\n'
        '      </configuration>\n'
        '      <dragpoints>\n'
        '        ' + dp22 + '\n'
        '      </dragpoints>\n'
        '    </shape>'
    )

    # ── shape23: Stop — error ────────────────────────────────────────
    shapes.append(stop_shape(23, shape_x(5), y_catch, "Error", False))

    shapes_xml = "\n\n".join(shapes)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<bns:Component xmlns:bns="http://api.platform.boomi.com/"\n'
        '               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '               componentId=""\n'
        '               name="MIG_WM_GLDComplianceAdapterServices_Process"\n'
        '               type="process"\n'
        '               folderId="' + FOLDER_ID + '">\n'
        '  <bns:encryptedValues/>\n'
        '  <bns:description>GLDComplianceAdapterServices migrated from webMethods IS 6.5. '
        '7 Oracle SP/SELECT ops. enableUserLog=false for PII guard. | built with boomi-companion v1.0.0</bns:description>\n'
        '  <bns:object>\n'
        '<process allowSimultaneous="false" enableUserLog="false" processLogOnErrorOnly="false"\n'
        '         purgeDataImmediately="false" updateRunDates="true" workload="general">\n'
        '  <shapes>\n\n'
        + shapes_xml +
        '\n\n  </shapes>\n'
        '</process>\n'
        '  </bns:object>\n'
        '</bns:Component>'
    )


if __name__ == "__main__":
    out_dir = os.path.join("active-development", "process")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "MIG_WM_GLDComplianceAdapterServices_Process.xml")

    xml_str = build_process()

    with open(path, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print("Written: " + path)

    try:
        ET.parse(path)
        print("XML validation: OK")
    except ET.ParseError as e:
        print("XML validation FAILED: " + str(e))
