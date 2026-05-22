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


def extract_map_step(shape, sequence):
    config = shape.find("configuration/map")
    map_id = config.get("mapId") if config is not None else None
    return {
        "source_tag": "ee:transform",
        "type": "transform",
        "label": shape.get("userlabel", "Map"),
        "config_ref": None,
        "requires_review": False,
        "boomi_step": "Map",
        "boomi_component": "transform.map + profiles",
        "complexity": "medium",
        "has_dataweave": False,
        "map_id": map_id,
        "sequence": sequence,
    }


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


def _extract_decision_condition(shape):
    """Pull condition text from a Boomi decision shape XML."""
    cfg = shape.find("configuration/decision")
    if cfg is None:
        return ""
    field, operator, value = "", "EQUALS", ""
    cv = cfg.find("comparevalue")
    if cv is not None:
        pp = cv.find(".//processparameter")
        sp = cv.find(".//staticparameter")
        if pp is not None:
            field = pp.get("processproperty", pp.get("name", ""))
        elif sp is not None:
            field = sp.get("staticproperty", "")
    op_el = cfg.find("comparevalueoperator")
    if op_el is not None and op_el.text:
        operator = op_el.text.strip()
    ct = cfg.find("compareto")
    if ct is not None:
        pp = ct.find(".//processparameter")
        sp = ct.find(".//staticparameter")
        if pp is not None:
            value = pp.get("processproperty", pp.get("name", ""))
        elif sp is not None:
            value = sp.get("staticproperty", "")
    return f"{field} {operator} {value}".strip()


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
        step = extract_map_step(shape, seq)
        step["label"] = userlabel or step["label"]
        return step, seq

    if shape_type == "message":
        seq += 1
        step = extract_message_step(shape, seq)
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

    return None, seq


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
        if shape_type in ("returndocuments", "stop"):
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
                "requires_review": True,
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
            branch_steps_list = []
            for dp in dps:
                if dp["to"]:
                    b_steps, _ = _traverse(
                        dp["to"], shape_map, conn_map, component_index,
                        connections_used, seq, set(visited)
                    )
                    branch_steps_list.append({
                        "identifier": dp["identifier"] or dp["to"],
                        "steps": b_steps,
                    })
            steps.append({
                "source_tag": f"boomi:{shape_type}",
                "type": "choice_router",
                "label": userlabel or shape_type.capitalize(),
                "requires_review": True,
                "boomi_step": shape_type.capitalize(),
                "complexity": "medium",
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
