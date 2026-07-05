#!/usr/bin/env python3
"""
webMethods Analyzer
Reads webMethods Integration Server flow services (XML) or webMethods.io
workflow JSON exports and produces a platform-agnostic migration spec.

Usage:
    # Analyze webMethods IS flow service XML files
    python analyzers/analyze_webmethods.py --source-dir path/to/packages/ --project my-project

    # Pull from webMethods.io (cloud)
    python analyzers/analyze_webmethods.py --wmio-project "My Project" --project my-project

Required environment variables (webMethods.io pull):
    WMIO_TENANT_URL     e.g. https://mycompany.int-aws-us.webmethods.io
    WMIO_USERNAME       webMethods.io username
    WMIO_PASSWORD       webMethods.io password
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


# webMethods IS built-in services → canonical step type
WM_SERVICE_MAP = {
    "pub.flow:sequence":            "sequence",
    "pub.flow:branch":              "choice_router",
    "pub.flow:loop":                "loop",
    "pub.flow:invoke":              "subprocess_call",
    "pub.flow:exit":                "exception",
    "pub.flow:map":                 "transform",
    "pub.client:http":              "http_request",
    "pub.client:httpsClient":       "http_request",
    "pub.soap.handler:invoke":      "http_request",
    "pub.db.jdbc:call":             "db_select",
    "pub.db.jdbc:select":           "db_select",
    "pub.db.jdbc:insert":           "db_insert",
    "pub.db.jdbc:update":           "db_update",
    "pub.db.jdbc:delete":           "db_delete",
    "pub.jms:send":                 "event_trigger",
    "pub.jms:receive":              "event_trigger",
    "pub.transform:transformValues":"transform",
    "pub.string:concat":            "transform",
    "WmPublic:pub.flow:sequence":   "sequence",
}

# webMethods.io step types → canonical
WMIO_STEP_MAP = {
    "trigger":      "http_listener",
    "action":       "connector_action",
    "condition":    "choice_router",
    "transformer":  "transform",
    "loop":         "loop",
    "parallel":     "branch",
    "sub_workflow": "subprocess_call",
}


def _comment_text(elem):
    """Extract COMMENT child text from a flow element."""
    c = elem.find("COMMENT")
    return (c.text or "").strip() if c is not None else ""


def _parse_wm_elements(children, seq_counter):
    """
    Recursive descent parser for webMethods IS flow XML children.
    Returns a list of canonical step dicts.
    seq_counter: a list[int] used as a mutable counter (pass [1]).

    webMethods IS control-flow conventions:
    - SEQUENCE EXIT-ON="FAILURE" with COMMENT "TRY Block" → try block
    - SEQUENCE EXIT-ON="SUCCESS" wrapping a "FAILURE" SEQUENCE → TRY/CATCH wrapper
    - BRANCH SWITCH="var" → choice_router (multi-branch)
    - LOOP COUNT="var" → loop (foreach)
    - INVOKE SERVICE="..." → subprocess_call or connector_action
    - MAP → transform
    - EXIT → exception / stop
    """
    steps = []
    i = 0
    while i < len(children):
        elem = children[i]
        tag = elem.tag
        svc = elem.get("SERVICE") or ""
        comment = _comment_text(elem) or elem.get("COMMENT") or ""
        label = comment or svc or tag
        seq = seq_counter[0]
        seq_counter[0] += 1

        # ── SEQUENCE ──────────────────────────────────────────────────────
        if tag == "SEQUENCE":
            exit_on = (elem.get("EXIT-ON") or "").upper()
            seq_comment = comment.upper()
            sub_children = list(elem)

            # Pattern: SEQUENCE EXIT-ON="SUCCESS" containing a SEQUENCE EXIT-ON="FAILURE"
            # This is the webMethods TRY/CATCH wrapper: the outer SEQUENCE gives
            # control to the next step if the inner (try) SEQUENCE exits on failure.
            inner_try = None
            catch_elems = []
            if exit_on == "SUCCESS":
                for j, child in enumerate(sub_children):
                    if child.tag == "SEQUENCE" and (child.get("EXIT-ON") or "").upper() == "FAILURE":
                        inner_try = child
                        catch_elems = sub_children[j+1:]
                        break

            if inner_try is not None:
                try_steps  = _parse_wm_elements(list(inner_try), seq_counter)
                catch_steps = _parse_wm_elements(catch_elems, seq_counter)
                steps.append({
                    "source_tag": "wm:SEQUENCE:try_catch",
                    "type": "try_catch",
                    "label": comment or "Try/Catch block",
                    "try_steps": try_steps,
                    "catch_steps": catch_steps,
                    "requires_review": False,
                    "sequence": seq,
                })
            elif exit_on == "FAILURE":
                # Standalone TRY block without an explicit catch — wrap in try_catch.
                # EXIT-ON="FAILURE" is the standard webMethods IS convention for a try
                # body that aborts the sequence when any step fails.
                try_steps = _parse_wm_elements(sub_children, seq_counter)
                steps.append({
                    "source_tag": "wm:SEQUENCE:try",
                    "type": "try_catch",
                    "label": comment or "Try block",
                    "try_steps": try_steps,
                    "catch_steps": [],
                    "requires_review": True,
                    "sequence": seq,
                })
            else:
                # Plain SEQUENCE — flatten into parent (sequences are structural containers)
                steps.extend(_parse_wm_elements(sub_children, seq_counter))

        # ── BRANCH → multi-way conditional ────────────────────────────────
        elif tag == "BRANCH":
            switch_var = elem.get("SWITCH") or ""
            branch_children = [c for c in elem if c.tag not in ("COMMENT",)]
            if len(branch_children) == 2:
                # Two-branch → IF/ELSE
                true_elem, false_elem = branch_children[0], branch_children[1]
                true_label  = _comment_text(true_elem) or true_elem.get("LABEL") or "true path"
                false_label = _comment_text(false_elem) or false_elem.get("LABEL") or "false/default path"
                true_steps  = _parse_wm_elements(list(true_elem), seq_counter)
                false_steps = _parse_wm_elements(list(false_elem), seq_counter)
                steps.append({
                    "source_tag": f"wm:BRANCH:{switch_var}",
                    "type": "choice_router",
                    "label": comment or f"Branch on {switch_var}",
                    "condition": f"{switch_var} EQUALS {true_label}",
                    "true_steps": true_steps,
                    "false_steps": false_steps,
                    "requires_review": True,
                    "sequence": seq,
                })
            else:
                # N-way branch → route (multiple paths)
                paths = []
                for b in branch_children:
                    b_label = _comment_text(b) or b.get("LABEL") or b.get("NAME") or "path"
                    b_steps = _parse_wm_elements(list(b), seq_counter)
                    paths.append({"label": b_label, "condition": b_label, "steps": b_steps})
                steps.append({
                    "source_tag": f"wm:BRANCH:{switch_var}",
                    "type": "route",
                    "label": comment or f"Switch on {switch_var}",
                    "switch_variable": switch_var,
                    "paths": paths,
                    "requires_review": True,
                    "sequence": seq,
                })

        # ── LOOP → foreach ────────────────────────────────────────────────
        elif tag == "LOOP":
            count_var = elem.get("COUNT") or elem.get("ARRAY") or ""
            loop_children = [c for c in elem if c.tag not in ("COMMENT",)]
            loop_steps = _parse_wm_elements(loop_children, seq_counter)
            steps.append({
                "source_tag": f"wm:LOOP:{count_var}",
                "type": "foreach",
                "label": comment or f"Loop over {count_var}",
                "loop_over": count_var,
                "loop_steps": loop_steps,
                "requires_review": False,
                "sequence": seq,
            })

        # ── INVOKE → service call ─────────────────────────────────────────
        elif tag == "INVOKE":
            canon_type = WM_SERVICE_MAP.get(svc) or "connector_action"
            step = {
                "source_tag": f"wm:INVOKE:{svc}",
                "type": canon_type,
                "label": label or svc,
                "config_ref": svc,
                "wm_service": svc,
                "requires_review": True,
                "complexity": "medium" if canon_type in ("transform", "choice_router") else "low",
                "sequence": seq,
            }
            # Extract SQL for JDBC calls
            if canon_type in ("db_select", "db_insert", "db_update", "db_delete"):
                sql_elem = elem.find(".//VALUE[@name='sql']") or elem.find(".//sql")
                if sql_elem is not None:
                    step["sql"] = (sql_elem.text or "").strip()
            steps.append(step)

        # ── MAP → transform ───────────────────────────────────────────────
        elif tag == "MAP":
            mode = elem.get("MODE") or ""
            if mode != "INPUT" and mode != "OUTPUT":  # skip connector param maps
                steps.append({
                    "source_tag": "wm:MAP",
                    "type": "transform",
                    "label": comment or f"Map ({mode})",
                    "requires_review": True,
                    "sequence": seq,
                })

        # ── EXIT → exception / stop ───────────────────────────────────────
        elif tag == "EXIT":
            steps.append({
                "source_tag": "wm:EXIT",
                "type": "exception",
                "label": comment or "Exit flow",
                "requires_review": False,
                "sequence": seq,
            })

        i += 1
    return steps


def analyze_wm_flow_xml(fpath):
    """
    Analyze a webMethods IS flow service XML file using recursive descent parsing.
    Preserves nested control-flow structure (TRY/CATCH, BRANCH, LOOP) in the spec.
    """
    try:
        tree = ET.parse(fpath)
        root = tree.getroot()
    except ET.ParseError:
        return None

    name = Path(fpath).stem
    seq_counter = [1]

    # Root children are the top-level flow steps
    root_children = [c for c in root if c.tag not in ("COMMENT",)]
    steps = _parse_wm_elements(root_children, seq_counter)

    # Detect error handling presence
    has_try_catch = any(s.get("type") == "try_catch" for s in steps)

    # Trigger — webMethods IS services are triggered by HTTP or JMS or scheduler
    trigger = {
        "type": "http_listener",
        "source_tag": "wm:http:trigger",
        "label": f"IS Service: {name}",
        "requires_review": True,
        "note": "webMethods IS trigger type needs manual verification (HTTP, JMS, or scheduler)",
    }

    return {
        "name": name,
        "source_name": name,
        "flow_type": "primary",
        "trigger": trigger,
        "steps": steps,
        "connections_used": [],
        "error_handling": {
            "has_error_handler": has_try_catch,
            "strategies": ["try_catch"] if has_try_catch else [],
        },
    }


def analyze_wmio_workflow(wf_data):
    """Analyze a webMethods.io workflow JSON export."""
    name = wf_data.get("name", "unknown")
    wf_id = wf_data.get("uid", "")

    trigger = {"type": "unknown", "requires_review": True}
    steps = []
    seq = 0

    for node in wf_data.get("nodes", []):
        node_type = node.get("type", "action")
        canon_type = WMIO_STEP_MAP.get(node_type, "connector_action")
        label = node.get("name", node_type)

        if node_type == "trigger":
            trigger = {
                "source_tag": f"wmio:trigger",
                "type": "http_listener",
                "label": label,
                "requires_review": False,
            }
        else:
            seq += 1
            steps.append({
                "source_tag": f"wmio:{node_type}",
                "type": canon_type,
                "label": label,
                "config_ref": node.get("service"),
                "requires_review": canon_type in ("connector_action", "custom_script"),
                "wmio_service": node.get("service"),
                "complexity": "medium",
                "sequence": seq,
            })

    return {
        "name": name,
        "source_name": name,
        "workflow_id": wf_id,
        "flow_type": "primary",
        "trigger": trigger,
        "steps": steps,
        "connections_used": [],
        "error_handling": {"has_error_handler": False, "strategies": []},
    }


def analyze_from_files(source_dir, project_name, output_path):
    source_dir = os.path.abspath(source_dir)
    flows = []

    for dirpath, _, filenames in os.walk(source_dir):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            if fname.endswith(".xml"):
                print(f"  Analyzing IS flow: {fname}")
                flow = analyze_wm_flow_xml(fpath)
                if flow and flow.get("steps"):
                    flows.append(flow)
            elif fname.endswith(".json"):
                print(f"  Analyzing webMethods.io workflow: {fname}")
                try:
                    with open(fpath, encoding="utf-8") as f:
                        data = json.load(f)
                    wf_list = data if isinstance(data, list) else [data]
                    for wf in wf_list:
                        flows.append(analyze_wmio_workflow(wf))
                except Exception as e:
                    print(f"    WARNING: {e}", file=sys.stderr)

    return _build_spec(flows, project_name, output_path, [source_dir])


def _build_spec(flows, project_name, output_path, source_files):
    gaps = []
    for flow in flows:
        if flow["trigger"].get("requires_review"):
            gaps.append({"flow": flow["name"], "component": "trigger"})
        for step in flow.get("steps", []):
            if step.get("requires_review"):
                gaps.append({"flow": flow["name"], "step_type": step.get("type"), "sequence": step.get("sequence")})

    spec = {
        "schema_version": "1.0",
        "source_system": "webmethods",
        "source_version": "webmethods_is_or_io",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "project_name": project_name,
        "source_files_analyzed": [str(s) for s in source_files],
        "summary": {
            "total_flows": len(flows),
            "primary_flows": len(flows),
            "sub_flows": 0,
            "total_connections": 0,
            "gaps_found": len(gaps),
            "overall_complexity": "high" if gaps else "medium",
        },
        "connections": {},
        "integrations": flows,
        "gaps": gaps,
        "migration_notes": "webMethods IS INVOKE steps referencing custom packages require manual review.",
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"\nSpec written to: {output_path}")
    return spec


def main():
    parser = argparse.ArgumentParser(description="Analyze webMethods IS or webMethods.io projects.")
    parser.add_argument("--source-dir", help="Directory of webMethods IS packages or wmio exports")
    parser.add_argument("--wmio-project", help="webMethods.io project name (requires API creds)")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    output_path = args.output or os.path.join("migration-specs", f"{args.project}.json")

    if args.source_dir:
        analyze_from_files(args.source_dir, args.project, output_path)
    else:
        parser.error("Provide --source-dir (wmio live pull coming soon)")


if __name__ == "__main__":
    main()
