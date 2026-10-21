#!/usr/bin/env python3
"""
Boomi Process Analyzer
Reads a Boomi active-development directory and produces a platform-agnostic
migration spec (same format as analyze_mulesoft.py output).

Usage:
    python analyzers/analyze_boomi.py active-development/
    python analyzers/analyze_boomi.py active-development/ --output migration-specs/boomi-customer-api.json
    python analyzers/analyze_boomi.py active-development/ --project my-project
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


BOOMI_NS = "http://api.platform.boomi.com/"

WSS_OP_TYPE_TO_HTTP = {
    "QUERY": "GET",
    "CREATE": "POST",
    "UPDATE": "PUT",
    "DELETE": "DELETE",
}

DB_OP_TYPE_TO_STEP_TYPE = {
    "GET": "db_select",
    "CREATE": "db_insert",
    "UPDATE": "db_update",
    "DELETE": "db_delete",
    "EXECUTE": "db_select",  # Boomi uses EXECUTE for Standard Get
}

SHAPE_TYPE_LABELS = {
    "start": "trigger",
    "map": "transform",
    "dataprocess": "custom_script",
    "message": "set_payload",
    "documentproperties": "set_variable",
    "decision": "choice_router",
    "route": "choice_router",
    "branch": "branch",
    "stop": "exception",
    "notify": "logger",
    "processcall": "subprocess_call",
    "returndocuments": "return_response",
    "connectoraction": "connector_action",
}


def build_component_index(directory):
    """
    Walk the directory tree and build a dict of componentId -> (file_path, ElementTree).
    This allows resolving operation/connection references by GUID.
    """
    index = {}
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            if not fname.endswith(".xml"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                tree = ET.parse(fpath)
                root = tree.getroot()
                comp_id = root.get("componentId")
                if comp_id:
                    index[comp_id] = (fpath, tree)
            except ET.ParseError:
                pass
    return index


def find_elem(root, *tag_names):
    """Search for an element matching any of the tag names (no namespace)."""
    for tag in tag_names:
        for elem in root.iter():
            local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if local == tag:
                return elem
    return None


def extract_wss_trigger(operation_id, component_index):
    """Look up WSS operation XML and extract HTTP trigger metadata."""
    if operation_id not in component_index:
        return {
            "type": "unknown",
            "source_tag": "wss:listen",
            "label": "WSS Listen",
            "requires_review": True,
            "operation_id": operation_id,
            "note": "WSS operation XML not found in index",
        }

    _, tree = component_index[operation_id]
    root = tree.getroot()

    listen_action = find_elem(root, "WebServicesServerListenAction")
    if listen_action is None:
        return {
            "type": "http_listener",
            "source_tag": "wss:listen",
            "requires_review": True,
            "operation_id": operation_id,
            "note": "Could not parse WSS operation XML",
        }

    op_type = listen_action.get("operationType", "QUERY")
    object_name = listen_action.get("objectName", "")
    input_type = listen_action.get("inputType", "none")

    http_method = WSS_OP_TYPE_TO_HTTP.get(op_type, "GET")
    has_body = input_type not in ("none",)

    # Reconstruct Boomi WSS path convention
    boomi_path = f"/ws/simple/{op_type.lower()}{object_name[0].upper() + object_name[1:] if object_name else ''}"

    # Infer clean REST path from the object name
    rest_path, path_params = infer_rest_path(object_name, http_method)

    return {
        "source_tag": "wss:listen",
        "type": "http_listener",
        "label": f"WSS Listen {http_method} {boomi_path}",
        "config_ref": None,
        "requires_review": False,
        "boomi_step": "Start_WSS_Listen",
        "boomi_component": "wss_operation",
        "complexity": "low",
        "http_method": http_method,
        "boomi_path": boomi_path,
        "path": rest_path,
        "path_params": path_params,
        "allowed_methods": http_method,
        "has_request_body": has_body,
        "boomi_operation_type": op_type,
        "boomi_object_name": object_name,
        "boomi_input_type": input_type,
    }


def infer_rest_path(object_name, http_method):
    """
    Map a Boomi WSS objectName to a clean REST path.
    Returns (path, list_of_path_params).

    Examples:
      customers  → /customers          []
      customerById → /customers/{id}   [id]
      customer   → /customers          []  (POST context)
    """
    name_lower = object_name.lower()

    # Patterns that imply a single-resource path with an ID
    if "byid" in name_lower or name_lower.endswith("id"):
        base = re.sub(r"byid$|id$", "", name_lower).rstrip("_")
        # pluralize naively
        resource = base if base.endswith("s") else base + "s"
        return f"/{resource}/{{id}}", ["id"]

    # If the name is already plural, use it as-is
    if name_lower.endswith("s"):
        return f"/{name_lower}", []

    # Singular → pluralize
    return f"/{name_lower}s", []


def parse_sql_metadata(sql):
    """
    Extract table name and parameter names from a Boomi SQL string.
    Boomi uses $param_name notation for named parameters.

    Returns:
        table      - first table name found (FROM/INTO/UPDATE)
        params     - list of parameter names (without $)
        operation  - SELECT / INSERT / UPDATE / DELETE
    """
    if not sql:
        return None, [], "UNKNOWN"

    sql_upper = sql.upper().strip()
    operation = sql_upper.split()[0] if sql_upper else "UNKNOWN"

    # Extract table name
    table = None
    for pattern in [r"FROM\s+(\w+)", r"INTO\s+(\w+)", r"UPDATE\s+(\w+)"]:
        m = re.search(pattern, sql, re.IGNORECASE)
        if m:
            table = m.group(1).lower()
            break

    # Extract $param_name placeholders
    params = re.findall(r"\$(\w+)", sql)

    return table, params, operation


def extract_db_step(shape, operation_id, connection_id, component_index, sequence):
    """Look up DB operation XML and extract full step metadata."""
    step = {
        "source_tag": "db:operation",
        "type": "db_select",
        "label": shape.get("userlabel", "DB Operation"),
        "config_ref": connection_id,
        "requires_review": False,
        "boomi_step": "DatabaseV2",
        "boomi_component": "databasev2_connection + databasev2_operation",
        "complexity": "low",
        "sql": None,
        "table": None,
        "params": [],
        "has_parameters": False,
        "operation_id": operation_id,
        "connection_id": connection_id,
        "sequence": sequence,
    }

    if operation_id not in component_index:
        step["requires_review"] = True
        step["note"] = "DB operation XML not found in component index"
        return step

    _, tree = component_index[operation_id]
    root = tree.getroot()

    # customOperationType on GenericOperationConfig tells us GET/CREATE/UPDATE/DELETE
    gen_config = find_elem(root, "GenericOperationConfig")
    if gen_config is not None:
        custom_op = gen_config.get("customOperationType", gen_config.get("operationType", "GET"))
        step["type"] = DB_OP_TYPE_TO_STEP_TYPE.get(custom_op, "db_select")
        step["boomi_step"] = f"DatabaseV2_{custom_op}"

        # SQL lives in <field id="query" type="string" value="..."/>
        for field in gen_config.findall("field"):
            if field.get("id") == "query":
                sql = field.get("value", "")
                table, params, operation = parse_sql_metadata(sql)
                step["sql"] = sql
                step["table"] = table
                step["params"] = params
                step["has_parameters"] = bool(params)
                step["sql_operation"] = operation
                break

    return step


def _parse_map_component(map_elem, component_index):
    """
    Parse a Boomi transform.map <Map> element into clean field mappings.

    A Mapping that goes straight profile-to-profile (fromType="profile",
    toType="profile") is a simple rename/copy. But Boomi also routes mappings
    through a <FunctionStep> (Scripting, Cross-Reference Lookup, a reusable
    "Custom Function", etc.) -- those show up as TWO disconnected <Mapping>
    edges (profile->function input, function output->profile), with the real
    transformation logic sitting in a separate <Functions><FunctionStep>
    block keyed by a shared function key. Confirmed live against real Map
    components: a Scripting function concatenating FirstName+LastName into
    ContactName, a Cross-Reference Lookup resolving AccountId into
    CompanyName, and a category="userdefined" Custom Function ("Remove
    Address Returns") whose actual logic lives in a separate customfunction
    component (referenced by the FunctionStep's own `id` attribute, not
    inlined in the Map XML at all) -- all reconstructable, with the
    Custom Function case only fully resolvable if that component was also
    pulled locally.

    Returns (field_mappings, unresolved_mappings, fully_resolved).
    field_mappings follows the same {source, target, type, transformation,
    expression, notes} shape used by analyze_mulesoft.py's DataWeave
    extractor and enrich_spec.py's TRANSFORM_PROMPT, so a Boomi Map step
    looks identical downstream to a MuleSoft transform step instead of
    needing its own schema. fully_resolved is False whenever a mapped field's
    real transformation logic could not be retrieved (e.g. a Custom Function
    component that isn't in the local pull) -- callers should use this to
    flag the step for review even though most fields resolved cleanly,
    rather than silently presenting partial data as complete.
    """
    functions = {}
    fully_resolved = True
    functions_elem = map_elem.find("Functions")
    if functions_elem is not None:
        for fstep in functions_elem.findall("FunctionStep"):
            key = fstep.get("key", "")
            category = fstep.get("category", "")
            ftype = fstep.get("type", "")
            name = fstep.get("name", "")
            inputs = {i.get("key", ""): i.get("name", "") for i in fstep.findall("Inputs/Input")}
            outputs = {o.get("key", ""): o.get("name", "") for o in fstep.findall("Outputs/Output")}

            if category == "Scripting":
                scripting = fstep.find("Configuration/Scripting")
                lang = scripting.get("language", "") if scripting is not None else ""
                script_elem = fstep.find("Configuration/Scripting/ScriptToExecute")
                script = (script_elem.text or "").strip() if script_elem is not None else ""
                detail = f"[{lang} script] {script}" if script else f"[{lang} script] (script body not captured)"
            elif ftype == "CrossRefLookup":
                crl = fstep.find("Configuration/CrossRefLookup")
                table_id = crl.get("crossRefTableId", "") if crl is not None else ""
                detail = f"Cross-reference table lookup (crossRefTableId={table_id})"
            elif category == "userdefined":
                # Boomi "Custom Function" -- the Map XML never inlines its
                # logic, only a pointer to a separate customfunction
                # component. Try to resolve it; be honest when we can't.
                fn_comp_id = fstep.get("id", "")
                if fn_comp_id and fn_comp_id in component_index:
                    _, fn_tree = component_index[fn_comp_id]
                    fn_root = fn_tree.getroot()
                    # Schema for customfunction components hasn't been seen in
                    # any real pull yet -- don't guess at its internal
                    # structure, just confirm we have it and surface the raw
                    # XML for a human/AI reviewer rather than parsing blind.
                    raw_xml = ET.tostring(fn_root, encoding="unicode")
                    detail = f"Custom Function '{name}' (id={fn_comp_id}) -- raw component XML: {raw_xml[:2000]}"
                else:
                    detail = (
                        f"Custom Function '{name}' (id={fn_comp_id}) -- component NOT found in local "
                        f"pull, actual transformation logic is unknown. Pull the customfunction "
                        f"component with this id to resolve it before trusting this field mapping."
                    )
                    fully_resolved = False
            else:
                # Unhandled function category/type -- don't silently drop it,
                # surface the raw config so a human/AI reviewer can still
                # reconstruct the logic instead of losing it entirely.
                cfg = fstep.find("Configuration")
                cfg_child = list(cfg)[0] if cfg is not None and len(cfg) else None
                attrs = dict(cfg_child.attrib) if cfg_child is not None else {}
                if cfg_child is None:
                    detail = f"[Unrecognized function type '{category or ftype}' name='{name}' -- no configuration captured, logic unknown]"
                    fully_resolved = False
                else:
                    detail = f"[Unrecognized function type '{category or ftype}' name='{name}' -- raw config: {attrs}]"

            functions[key] = {
                "name": name, "inputs": inputs, "outputs": outputs, "detail": detail,
                "bound_inputs": {}, "bound_outputs": {},
            }

    field_mappings = []
    unresolved = []

    mappings_elem = map_elem.find("Mappings")
    if mappings_elem is None:
        return field_mappings, unresolved, fully_resolved

    for m in mappings_elem.findall("Mapping"):
        from_type = m.get("fromType", "profile")
        to_type = m.get("toType", "profile")
        from_name = m.get("fromNamePath", "")
        to_name = m.get("toNamePath", "")

        if from_type == "profile" and to_type == "profile":
            field_mappings.append({
                "source": from_name,
                "target": to_name,
                "type": "string",
                "transformation": "passthrough",
            })
        elif from_type == "profile" and to_type == "function":
            fn = functions.get(m.get("toFunction", ""))
            if fn is not None:
                fn["bound_inputs"][m.get("toKey", "")] = from_name
            else:
                unresolved.append(dict(m.attrib))
        elif from_type == "function" and to_type == "profile":
            fn = functions.get(m.get("fromFunction", ""))
            if fn is not None:
                fn["bound_outputs"][m.get("fromKey", "")] = to_name
            else:
                unresolved.append(dict(m.attrib))
        else:
            # function -> function chaining: no real example seen yet.
            # Surface raw rather than guess at a resolution.
            unresolved.append(dict(m.attrib))

    # Join each function's bound inputs/outputs into one readable mapping
    # that carries the actual transformation logic, instead of leaving two
    # disconnected profile<->function edges for a downstream reader to guess at.
    for fn in functions.values():
        if not fn["bound_outputs"]:
            if fn["bound_inputs"]:
                unresolved.append({
                    "function": fn["name"],
                    "note": "Function inputs bound but no output mapped to a profile field",
                    "bound_inputs": fn["bound_inputs"],
                })
            continue
        input_desc = ", ".join(
            f"{port_name}={fn['bound_inputs'].get(port_key) or '(unbound)'}"
            for port_key, port_name in fn["inputs"].items()
        ) or "(no inputs captured)"
        source_paths = [v for v in fn["bound_inputs"].values() if v]
        source_str = " + ".join(source_paths) if source_paths else "(unresolved input)"
        for target in fn["bound_outputs"].values():
            field_mappings.append({
                "source": source_str,
                "target": target,
                "type": "string",
                "transformation": "custom",
                "expression": fn["detail"],
                "notes": f"Via Boomi Map function '{fn['name']}' -- inputs: {input_desc}",
            })

    return field_mappings, unresolved, fully_resolved


def extract_map_step(shape, sequence, component_index):
    config = shape.find("configuration/map")
    map_id = config.get("mapId") if config is not None else None
    step = {
        "source_tag": "ee:transform",
        "type": "transform",
        "label": shape.get("userlabel", "Map"),
        "config_ref": None,
        "requires_review": True,
        "boomi_step": "Map",
        "boomi_component": "transform.map + profiles",
        "complexity": "medium",
        "has_dataweave": False,
        "map_id": map_id,
        "field_mappings": [],
        "sequence": sequence,
    }

    if not map_id or map_id not in component_index:
        step["note"] = "transform.map component not found in local index -- field mappings not captured"
        return step

    _, tree = component_index[map_id]
    root = tree.getroot()
    map_elem = find_elem(root, "Map")
    if map_elem is None:
        step["note"] = "transform.map component found but <Map> element could not be parsed"
        return step

    field_mappings, unresolved, fully_resolved = _parse_map_component(map_elem, component_index)
    step["field_mappings"] = field_mappings
    step["has_complex_logic"] = any(fm.get("transformation") == "custom" for fm in field_mappings)
    if unresolved:
        step["unresolved_mappings"] = unresolved
    # Real mapping data was found and parsed -- this is no longer a blind
    # map_id-only stub. Still flag for review if any mapped field's logic
    # (e.g. a Custom Function component not present in the local pull)
    # couldn't actually be resolved -- partial data should never present
    # itself as fully trustworthy.
    step["requires_review"] = (not field_mappings) or (not fully_resolved)
    if not fully_resolved:
        step["note"] = "One or more mapped fields route through logic that could not be fully resolved locally -- see field_mappings entries with transformation=custom for details"
    return step


def extract_message_step(shape, sequence):
    msg_elem = shape.find("configuration/message/msgTxt")
    msg_text = msg_elem.text if msg_elem is not None else ""
    # Strip enclosing single quotes that Boomi uses for literal JSON
    clean = msg_text.strip("'") if msg_text else ""
    return {
        "source_tag": "message:step",
        "type": "set_payload",
        "label": shape.get("userlabel", "Message"),
        "config_ref": None,
        "requires_review": False,
        "boomi_step": "Message",
        "boomi_component": "message_step",
        "complexity": "low",
        "static_content": clean,
        "sequence": sequence,
    }


def extract_notify_step(shape, sequence):
    """
    Boomi's Notify shape (alert/log message, distinct from the Message shape
    which just sets payload content) -- was previously unhandled entirely:
    shapetype="notify" has no branch in _classify_and_extract_shape, so it
    silently fell through to `return None` and the step vanished, along with
    whatever it actually did. Confirmed live: this is exactly what was
    silently dropping the Notify step on a real process's "Cancelled" branch,
    making that branch look like a pure no-op when it actually sends an
    alert.
    """
    cfg = shape.find("configuration/notify")
    msg_elem = cfg.find("notifyMessage") if cfg is not None else None
    msg_text = (msg_elem.text or "").strip() if msg_elem is not None else ""
    level_elem = cfg.find("notifyMessageLevel") if cfg is not None else None
    level = level_elem.text.strip() if level_elem is not None and level_elem.text else "INFO"
    params = []
    if cfg is not None:
        for pv in cfg.findall(".//notifyParameters/parametervalue"):
            pe = pv.find(".//profileelement")
            if pe is not None:
                params.append(pe.get("elementName", ""))
    return {
        "source_tag": "notify:step",
        "type": "logger",
        "label": shape.get("userlabel", "Notify"),
        "config_ref": None,
        "requires_review": False,
        "boomi_step": "Notify",
        "boomi_component": "notify_step",
        "complexity": "low",
        "message_template": msg_text,
        "message_level": level,
        "message_parameters": params,
        "sequence": sequence,
    }


def extract_set_properties_step(shape, sequence):
    props = []
    for dp in shape.findall(".//documentproperty"):
        name = dp.get("name", "")
        prop_id = dp.get("propertyId", "")
        # Find source value
        source = shape.find(f".//documentproperty[@name='{name}']/sourcevalues/parametervalue")
        source_type = source.get("valueType", "") if source is not None else ""
        source_value = ""
        if source is not None:
            pp = source.find("processparameter")
            if pp is not None:
                source_value = pp.get("processproperty", "")
        props.append({"name": name, "property_id": prop_id, "source_type": source_type, "source_value": source_value})
    return {
        "source_tag": "core:set-variable",
        "type": "set_variable",
        "label": shape.get("userlabel", "Set Properties"),
        "config_ref": None,
        "requires_review": False,
        "boomi_step": "Set_Properties",
        "boomi_component": "set_properties_step",
        "complexity": "low",
        "properties": props,
        "sequence": sequence,
    }


def extract_groovy_step(shape, sequence):
    script_elem = shape.find(".//script")
    script_text = script_elem.text if script_elem is not None else ""

    # Infer the script's purpose from its content
    purpose = "custom_transform"
    if "not found" in script_text.lower() or "404" in script_text:
        purpose = "not_found_handler"
    elif re.search(r"sb\.append|JSON\s*array|getDataCount", script_text):
        purpose = "array_combiner"
    elif "JsonSlurper" in script_text or "parseText" in script_text:
        purpose = "json_transformer"

    return {
        "source_tag": "dataprocess:groovy",
        "type": "custom_script",
        "label": shape.get("userlabel", "Groovy Script"),
        "config_ref": None,
        "requires_review": True,
        "boomi_step": "Data_Process_Groovy",
        "boomi_component": "data_process_step",
        "complexity": "high",
        "language": "groovy",
        "purpose": purpose,
        "script": script_text,
        "note": "Groovy script requires manual mapping to target platform equivalent",
        "sequence": sequence,
    }


def extract_connection_info(connection_id, component_index):
    """Extract connection metadata from a connection component XML."""
    if connection_id not in component_index:
        return {"id": connection_id, "type": "unknown", "requires_review": True}

    _, tree = component_index[connection_id]
    root = tree.getroot()

    name = root.get("name", "")
    sub_type = root.get("subType", "")

    # DatabaseV2: look for JDBC URL
    url_elem = find_elem(root, "url")
    jdbc_url = url_elem.text.strip() if url_elem is not None and url_elem.text else ""

    driver = ""
    conn_type = "unknown"
    if "postgresql" in jdbc_url.lower():
        driver = "postgresql"
        conn_type = "db"
    elif "mysql" in jdbc_url.lower():
        driver = "mysql"
        conn_type = "db"
    elif "sqlserver" in jdbc_url.lower() or "mssql" in jdbc_url.lower():
        driver = "mssql"
        conn_type = "db"
    elif "oracle" in jdbc_url.lower():
        driver = "oracle"
        conn_type = "db"
    elif sub_type == "wss":
        conn_type = "http_listener"
    elif "rest" in sub_type.lower():
        conn_type = "http"

    # Parse JDBC URL components
    host, port, database = "", "", ""
    m = re.match(r"jdbc:\w+://([^:/]+):?(\d*)/(\w+)", jdbc_url)
    if m:
        host, port, database = m.group(1), m.group(2) or "5432", m.group(3)

    return {
        "id": connection_id,
        "name": name,
        "type": conn_type,
        "driver": driver,
        "jdbc_url": jdbc_url,
        "host": host,
        "port": port,
        "database": database,
        "boomi_connector_type": sub_type,
        "requires_review": False,
    }


def _build_shape_map(all_shapes):
    return {s.get("name"): s for s in all_shapes}


def _build_conn_map(all_shapes):
    """Map shapeName -> list of {to, identifier} dicts from dragpoints."""
    conn_map = {}
    for shape in all_shapes:
        name = shape.get("name")
        dps = []
        for dp in shape.findall(".//dragpoint"):
            dps.append({"to": dp.get("toShape"), "identifier": dp.get("identifier", "")})
        conn_map[name] = dps
    return conn_map


def _extract_decision_value(decisionvalue_elem):
    """
    Resolve one Boomi <decisionvalue> operand into a human-readable string.
    Boomi nests the actual comparison operand under a value-type-specific
    child element depending on the decisionvalue's own valueType attribute.
    """
    if decisionvalue_elem is None:
        return ""
    value_type = decisionvalue_elem.get("valueType", "")
    pe = decisionvalue_elem.find(".//profileelement")
    if pe is not None:
        return pe.get("elementName", "")
    sp = decisionvalue_elem.find(".//staticparameter")
    if sp is not None:
        return sp.get("staticproperty", "")
    pp = decisionvalue_elem.find(".//processparameter")
    if pp is not None:
        return pp.get("processproperty", pp.get("name", ""))
    dp = decisionvalue_elem.find(".//dateparameter")
    if dp is not None:
        return f"<date:{dp.get('dateparametertype', '')}>"
    # Unrecognized operand shape -- surface raw rather than silently return
    # empty, same "don't guess, don't drop" discipline used for Map functions.
    child = list(decisionvalue_elem)[0] if len(decisionvalue_elem) else None
    if child is not None:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        return f"<unrecognized {value_type or local} operand: {dict(child.attrib)}>"
    return f"<empty {value_type} operand>"


def _extract_decision_condition(shape):
    """
    Pull condition text from a Boomi decision shape.

    Confirmed live against a real Decision shape ("Active Account?", testing
    Account.Active == true) that the previous implementation read the WRONG
    element names entirely -- it searched for <comparevalue>/
    <comparevalueoperator>/<compareto>, none of which exist anywhere in the
    real schema, and silently returned a bare operator string like "EQUALS"
    with NO field and NO value for every single Decision shape ever
    extracted. The real shape is:
        <decision comparison="equals">
          <decisionvalue valueType="profile">...</decisionvalue>
          <decisionvalue valueType="static">...</decisionvalue>
        </decision>
    -- the operator is an ATTRIBUTE on <decision> itself, and the two
    operands are TWO sibling <decisionvalue> elements in document order
    (tested value first, comparison value second), each nesting a
    <profileelement>/<staticparameter>/<processparameter> depending on its
    own valueType. This was likely the single highest-impact extraction bug
    in this analyzer: Decision (plain if/else) is far more common across
    Boomi processes than Route ever is, so every migrated branch condition
    was coming out meaningless.
    """
    cfg = shape.find("configuration/decision")
    if cfg is None:
        return ""
    operator = cfg.get("comparison", "equals")
    decision_values = cfg.findall("decisionvalue")
    field = _extract_decision_value(decision_values[0]) if len(decision_values) > 0 else ""
    value = _extract_decision_value(decision_values[1]) if len(decision_values) > 1 else ""
    return f"{field} {operator} {value}".strip()


def _extract_route_values(shape):
    """
    Pull the tested field + per-branch match values from a Boomi route
    shape's <route><routeproperty>/<routevalues> config. This is the actual
    routing condition (e.g. "Contact.Status__c equals Installed/New/
    Cancelled") -- distinct from the branch identifiers/steps already walked
    via dragpoints, and previously dropped entirely: the route/branch
    handling below only ever read dragpoint "identifier"/"toShape", never
    shape.find("configuration/route"), so every migrated recipe's Route
    conditions came out as unexplained raw keys ("3"/"5"/"7") with no
    indication of what field or value each one actually tests -- confirmed
    live against a real process where the generator had to fall back to a
    fabricated placeholder condition for exactly this reason.
    Returns (field_label, {key: {"name":..., "qualifier":..., "value":...}}).
    """
    cfg = shape.find("configuration/route")
    if cfg is None:
        return "", {}
    field_label = ""
    rp = cfg.find("routeproperty")
    if rp is not None:
        pe = rp.find(".//profileelement")
        if pe is not None:
            field_label = pe.get("elementName", "")
        else:
            sp = rp.find(".//staticparameter")
            if sp is not None:
                field_label = sp.get("staticproperty", "")
    values = {}
    rvs = cfg.find("routevalues")
    if rvs is not None:
        for rv in rvs.findall("routevalue"):
            key = rv.get("key", "")
            if key:
                values[key] = {
                    "name": rv.get("name", ""),
                    "qualifier": rv.get("qualifier", ""),
                    "value": rv.get("value", ""),
                }
    return field_label, values


def _classify_and_extract_shape(shape, component_index, connections_used, seq):
    """Convert a single shape element to a step dict. Returns (step_dict, seq)."""
    shape_type = shape.get("shapetype", "")
    userlabel = shape.get("userlabel", "")
    connector_cfg = shape.find("configuration/connectoraction")

    if shape_type == "connectoraction" and connector_cfg is not None:
        conn_type = connector_cfg.get("connectorType", "")
        op_id = connector_cfg.get("operationId", "")
        conn_id = connector_cfg.get("connectionId", "")
        if "dbv2" in conn_type or "db" in conn_type.lower():
            seq += 1
            step = extract_db_step(shape, op_id, conn_id, component_index, seq)
            step["label"] = userlabel or step["label"]
            connections_used.add(conn_id)
            return step, seq
        elif "rest" in conn_type.lower() or conn_type == "http":
            seq += 1
            connections_used.add(conn_id)
            return {
                "source_tag": f"{conn_type}:request",
                "type": "http_request",
                "label": userlabel,
                "config_ref": conn_id,
                "requires_review": True,
                "boomi_step": "REST_Connector",
                "complexity": "medium",
                "operation_id": op_id,
                "connection_id": conn_id,
                "sequence": seq,
            }, seq
        else:
            seq += 1
            return {
                "source_tag": f"{conn_type}:action",
                "type": "connector_action",
                "label": userlabel,
                "connector_type": conn_type,
                "operation_id": op_id,
                "connection_id": conn_id,
                "requires_review": True,
                "sequence": seq,
            }, seq

    if shape_type == "map":
        seq += 1
        step = extract_map_step(shape, seq, component_index)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "message":
        seq += 1
        step = extract_message_step(shape, seq)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "notify":
        seq += 1
        step = extract_notify_step(shape, seq)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "documentproperties":
        seq += 1
        step = extract_set_properties_step(shape, seq)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "dataprocess":
        seq += 1
        step = extract_groovy_step(shape, seq)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "processcall":
        seq += 1
        called_cfg = shape.find("configuration/processcall")
        called_id = called_cfg.get("processId") if called_cfg is not None else ""
        return {
            "source_tag": "boomi:processcall",
            "type": "subprocess_call",
            "label": userlabel,
            "requires_review": True,
            "called_process_id": called_id,
            "note": "Subprocess call — ensure called process is also migrated",
            "sequence": seq + 1,
        }, seq + 1

    # Unhandled shape type -- previously returned None here, which the caller
    # (`if step: steps.append(step)`) silently swallows: the shape, and
    # whatever it actually did, would vanish from the spec with no trace.
    # This was exactly how the Notify shape's alert-on-Cancelled logic went
    # missing before that case was added explicitly. Any shape type not yet
    # special-cased above now produces a loud, reviewable stub instead.
    seq += 1
    return {
        "source_tag": f"boomi:{shape_type}",
        "type": "unsupported_shape",
        "label": userlabel or shape_type.capitalize() or "Unknown Shape",
        "requires_review": True,
        "boomi_step": shape_type.capitalize() if shape_type else "Unknown",
        "note": f"Shape type '{shape_type}' has no extraction logic yet -- this step's real behavior was not captured",
        "sequence": seq,
    }, seq


def _traverse(start_name, shape_map, conn_map, component_index, connections_used,
              seq_start=0, visited=None):
    """
    Follow dragpoints from start_name, returning (steps, seq).
    Recurses into decision true/false branches and catcherrors branches.
    """
    if visited is None:
        visited = set()

    steps = []
    seq = seq_start
    current_name = start_name

    while current_name and current_name not in visited:
        shape = shape_map.get(current_name)
        if shape is None:
            break

        visited.add(current_name)
        shape_type = shape.get("shapetype", "")
        userlabel = shape.get("userlabel", "")
        dps = conn_map.get(current_name, [])

        # ── Terminal shapes — stop traversal ──────────────────────────────
        if shape_type == "stop":
            cfg = shape.find("configuration/stop")
            continues = cfg.get("continue", "true") if cfg is not None else "true"
            if continues == "false":
                # continue="false" is a HARD process exit (Boomi's "Exit"
                # semantics) -- distinct from continue="true" ("Break", just
                # the end of this path while the rest of the process keeps
                # running). Both were previously treated identically via a
                # silent break. Confirmed live: all 6 stop shapes in the real
                # "Integration Troubleshooting - Professional" process use
                # continue="true", so this was harmless there -- but any
                # process relying on hard-exit semantics would have lost that
                # distinction entirely with no trace in the spec.
                seq += 1
                steps.append({
                    "source_tag": "boomi:stop",
                    "type": "halt_process",
                    "label": userlabel or "Stop (Exit Process)",
                    "requires_review": False,
                    "boomi_step": "Stop",
                    "boomi_component": "stop_shape",
                    "complexity": "low",
                    "note": "continue=\"false\" -- this immediately terminates the entire process, not just this path",
                    "sequence": seq,
                })
            break

        if shape_type == "returndocuments":
            # No real example of this shape has turned up in any process
            # pulled so far, so its exact behavior is unverified -- flag it
            # loudly instead of silently treating it the same as a plain stop.
            seq += 1
            steps.append({
                "source_tag": "boomi:returndocuments",
                "type": "unsupported_shape",
                "label": userlabel or "Return Documents",
                "requires_review": True,
                "boomi_step": "ReturnDocuments",
                "note": "returndocuments shape type has no verified extraction logic yet -- no real example was available to confirm its structure",
                "sequence": seq,
            })
            break

        # ── Start shape — only extract trigger, then follow ───────────────
        if shape_type == "start":
            next_dp = dps[0] if dps else None
            current_name = next_dp["to"] if next_dp else None
            continue

        # ── Decision shape — recurse into true/false branches ─────────────
        if shape_type == "decision":
            seq += 1
            condition = _extract_decision_condition(shape)

            true_dp  = next((d for d in dps if d["identifier"] == "true"),  dps[0] if dps else None)
            false_dp = next((d for d in dps if d["identifier"] == "false"), None)

            true_steps = []
            false_steps = []
            true_end_name = None

            if true_dp and true_dp["to"]:
                true_steps, _ = _traverse(
                    true_dp["to"], shape_map, conn_map, component_index,
                    connections_used, seq, set(visited)
                )
                # Find first shape after the true branch (for main path continuation)
                true_end_name = true_dp["to"]

            if false_dp and false_dp["to"]:
                false_steps, _ = _traverse(
                    false_dp["to"], shape_map, conn_map, component_index,
                    connections_used, seq, set(visited)
                )

            steps.append({
                "source_tag": "boomi:decision",
                "type": "choice_router",
                "label": userlabel or "Decision",
                "config_ref": None,
                # Hardcoded True before this fix regardless of whether a real
                # condition was captured -- now reflects whether the
                # extraction above actually resolved a left/right operand.
                "requires_review": not condition,
                "boomi_step": "Decision",
                "complexity": "medium",
                "condition": condition,
                "true_steps": true_steps,
                "false_steps": false_steps,
                "sequence": seq,
            })
            # Continue on the main path (true branch direction)
            current_name = true_dp["to"] if true_dp else None
            # Skip shapes already visited via recursion
            while current_name and current_name in visited:
                sub_dps = conn_map.get(current_name, [])
                current_name = sub_dps[0]["to"] if sub_dps else None
            continue

        # ── CatchErrors shape — recurse into success / error branches ──────
        if shape_type == "catcherrors":
            seq += 1
            # First dragpoint = success (try) path; second = error path
            success_dp = next((d for d in dps if d["identifier"] != "false"), dps[0] if dps else None)
            error_dp   = next((d for d in dps if d["identifier"] == "false"), dps[1] if len(dps) > 1 else None)

            monitored_steps = []
            error_steps = []

            if success_dp and success_dp["to"]:
                monitored_steps, _ = _traverse(
                    success_dp["to"], shape_map, conn_map, component_index,
                    connections_used, seq, set(visited)
                )
            if error_dp and error_dp["to"]:
                error_steps, _ = _traverse(
                    error_dp["to"], shape_map, conn_map, component_index,
                    connections_used, seq, set(visited)
                )

            steps.append({
                "source_tag": "boomi:catcherrors",
                "type": "try_catch",
                "label": userlabel or "Try/Catch",
                "config_ref": None,
                "requires_review": False,
                "boomi_step": "CatchErrors",
                "complexity": "low",
                "monitored_steps": monitored_steps,
                "error_steps": error_steps,
                "sequence": seq,
            })
            # Continue on the success path after the monitored block
            current_name = success_dp["to"] if success_dp else None
            while current_name and current_name in visited:
                sub_dps = conn_map.get(current_name, [])
                current_name = sub_dps[0]["to"] if sub_dps else None
            continue

        # ── Route / Branch — treat as multi-way choice_router ─────────────
        if shape_type in ("route", "branch"):
            seq += 1
            # Only "route" shapes are conditional (status/value-based); a
            # Boomi "branch" shape is the unconditional parallel-track
            # construct (<branch numBranches="N"/>, no route config at all)
            # and genuinely has no condition to extract.
            condition_field, route_values = (
                _extract_route_values(shape) if shape_type == "route" else ("", {})
            )
            branch_steps_list = []
            for dp in dps:
                if dp["to"]:
                    b_steps, _ = _traverse(
                        dp["to"], shape_map, conn_map, component_index,
                        connections_used, seq, set(visited)
                    )
                    branch_id = dp["identifier"] or dp["to"]
                    branch_entry = {
                        "identifier": branch_id,
                        "steps": b_steps,
                    }
                    rv = route_values.get(branch_id)
                    if rv:
                        branch_entry["condition"] = (
                            f"{condition_field} {rv['qualifier']} \"{rv['value']}\"".strip()
                        )
                    elif branch_id == "default":
                        branch_entry["condition"] = "default (no other branch matched)"
                    branch_steps_list.append(branch_entry)
            steps.append({
                "source_tag": f"boomi:{shape_type}",
                "type": "choice_router",
                "label": userlabel or shape_type.capitalize(),
                # Real condition data now captured for a "route" shape with
                # routevalues -- only still needs a human look if we came up
                # empty (no routevalues found) or it's the unconditional
                # "branch" construct.
                "requires_review": not route_values,
                "boomi_step": shape_type.capitalize(),
                "complexity": "medium",
                "condition_field": condition_field,
                "branches": branch_steps_list,
                "true_steps": branch_steps_list[0]["steps"] if branch_steps_list else [],
                "false_steps": branch_steps_list[1]["steps"] if len(branch_steps_list) > 1 else [],
                "sequence": seq,
            })
            break

        # ── All other linear shapes ────────────────────────────────────────
        step, seq = _classify_and_extract_shape(
            shape, component_index, connections_used, seq
        )
        if step:
            steps.append(step)

        # Advance: follow first dragpoint
        next_dp = dps[0] if dps else None
        current_name = next_dp["to"] if next_dp else None

    return steps, seq


def analyze_process(process_file, component_index):
    """Analyze a single Boomi process XML → return a normalized flow spec dict."""
    tree = ET.parse(process_file)
    root = tree.getroot()

    name = root.get("name", Path(process_file).stem)
    component_id = root.get("componentId", "")
    description = ""
    desc_elem = find_elem(root, "description")
    if desc_elem is not None and desc_elem.text:
        description = desc_elem.text.strip()

    all_shapes = root.findall(".//shape")
    shape_map = _build_shape_map(all_shapes)
    conn_map  = _build_conn_map(all_shapes)

    # Find start shape and extract trigger
    trigger = None
    connections_used = set()
    start_name = None

    for shape in all_shapes:
        if shape.get("shapetype") == "start":
            start_name = shape.get("name")
            connector_cfg = shape.find("configuration/connectoraction")
            if connector_cfg is not None:
                conn_type = connector_cfg.get("connectorType", "")
                op_id = connector_cfg.get("operationId", "")
                if conn_type == "wss":
                    trigger = extract_wss_trigger(op_id, component_index)
                else:
                    trigger = {
                        "source_tag": f"{conn_type}:listen",
                        "type": "connector_trigger",
                        "label": shape.get("userlabel", ""),
                        "connector_type": conn_type,
                        "operation_id": op_id,
                        "requires_review": True,
                        "note": f"Non-WSS trigger ({conn_type}) — manual mapping required",
                    }
            break

    # Graph traversal from start shape — preserves decision/try branch structure
    steps, _ = _traverse(
        start_name, shape_map, conn_map, component_index, connections_used
    )

    # Detect whether any catcherrors shape exists for the error_handling summary
    has_error_handler = any(s.get("shapetype") == "catcherrors" for s in all_shapes)

    return {
        "name": name,
        "source_name": name,
        "component_id": component_id,
        "description": description,
        "flow_type": "primary",
        "trigger": trigger or {"type": "unknown", "requires_review": True},
        "steps": steps,
        "connections_used": list(connections_used),
        "error_handling": {
            "has_error_handler": has_error_handler,
            "strategies": [],
        },
        "boomi_suggestions": {
            "process_name": name,
            "pattern": "request_reply_api" if trigger and trigger.get("type") == "http_listener" else "unknown",
        },
    }


def analyze_directory(directory, project_name=None, output_path=None):
    """Analyze all Boomi processes in a directory and produce a migration spec."""
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print(f"ERROR: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Building component index from {directory}...")
    component_index = build_component_index(directory)
    print(f"  Indexed {len(component_index)} Boomi components")

    process_dir = os.path.join(directory, "process")
    if not os.path.isdir(process_dir):
        print(f"WARNING: No 'process/' subdirectory found. Scanning root for process XMLs.")
        process_dir = directory

    process_files = sorted([
        os.path.join(process_dir, f)
        for f in os.listdir(process_dir)
        if f.endswith(".xml")
    ])
    print(f"  Found {len(process_files)} process files")

    flows = []
    all_connection_ids = set()

    for pf in process_files:
        print(f"  Analyzing {os.path.basename(pf)}...")
        try:
            flow = analyze_process(pf, component_index)
            flows.append(flow)
            all_connection_ids.update(flow.get("connections_used", []))
        except Exception as e:
            print(f"    WARNING: {e}", file=sys.stderr)

    # Resolve connections
    connections = {}
    for conn_id in all_connection_ids:
        info = extract_connection_info(conn_id, component_index)
        key = info.get("name") or conn_id
        connections[key] = info

    # Collect gaps
    gaps = []
    for flow in flows:
        if flow["trigger"] and flow["trigger"].get("requires_review"):
            gaps.append({"flow": flow["name"], "component": "trigger", "note": flow["trigger"].get("note", "")})
        for step in flow.get("steps", []):
            if step.get("requires_review"):
                gaps.append({
                    "flow": flow["name"],
                    "step_type": step.get("type"),
                    "sequence": step.get("sequence"),
                    "label": step.get("label", ""),
                    "note": step.get("note", "Requires manual review"),
                })

    if not project_name:
        project_name = Path(directory).name

    spec = {
        "schema_version": "1.0",
        "source_system": "boomi",
        "source_version": "boomi_integration_platform",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "project_name": project_name,
        "source_files_analyzed": [os.path.relpath(pf) for pf in process_files],
        "summary": {
            "total_flows": len(flows),
            "primary_flows": len(flows),
            "sub_flows": 0,
            "total_connections": len(connections),
            "gaps_found": len(gaps),
            "overall_complexity": "high" if any(g.get("step_type") == "custom_script" for g in gaps) else "medium",
        },
        "connections": connections,
        "integrations": flows,
        "gaps": gaps,
        "migration_notes": "",
    }

    if not output_path:
        os.makedirs("migration-specs", exist_ok=True)
        output_path = os.path.join("migration-specs", f"{project_name}.json")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)

    print(f"\nSpec written to: {output_path}")
    print(f"  Flows:       {len(flows)}")
    print(f"  Connections: {len(connections)}")
    print(f"  Gaps:        {len(gaps)}")

    return spec


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a Boomi active-development directory into a migration spec JSON."
    )
    parser.add_argument(
        "directory",
        help="Path to Boomi active-development/ directory (must contain a process/ subdirectory)",
    )
    parser.add_argument("--output", help="Output file path (default: migration-specs/<project>.json)")
    parser.add_argument("--project", help="Project name (default: directory name)")
    args = parser.parse_args()

    analyze_directory(args.directory, project_name=args.project, output_path=args.output)


if __name__ == "__main__":
    main()
