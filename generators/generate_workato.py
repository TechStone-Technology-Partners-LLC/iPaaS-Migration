#!/usr/bin/env python3
"""
Workato Recipe Generator (Spec-Driven)
Reads any platform-agnostic migration spec and creates Workato recipes via the API.
Works with specs produced by analyze_mulesoft.py, analyze_boomi.py, or any future analyzer.

Usage:
    python generators/generate_workato.py migration-specs/boomi-customer-api.json
    python generators/generate_workato.py migration-specs/boomi-customer-api.json --folder MIG_CustomerAPI
    python generators/generate_workato.py migration-specs/boomi-customer-api.json --dry-run

Required environment variables (add to .env):
    WORKATO_API_TOKEN   Workato API token (Settings → API Tokens)
    WORKATO_EMAIL       Workato account email

Optional DB connection variables (for auto-creating the PostgreSQL connection):
    WORKATO_PG_HOST     PostgreSQL host       (default: db.internal)
    WORKATO_PG_PORT     PostgreSQL port       (default: 5432)
    WORKATO_PG_DATABASE PostgreSQL database   (default: from JDBC URL in spec)
    WORKATO_PG_USERNAME PostgreSQL username
    WORKATO_PG_PASSWORD PostgreSQL password
    WORKATO_PG_CONN_ID  Skip creation, use this existing Workato connection ID
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime


# ─── Workato API Client ───────────────────────────────────────────────────────

class WorkatoClient:
    BASE_URL = "https://www.workato.com/api"

    def __init__(self, api_token, email=None, base_url=None):
        try:
            import requests
            self._requests = requests
        except ImportError:
            print("ERROR: 'requests' library not found. Run: pip install requests", file=sys.stderr)
            sys.exit(1)

        # Strip all whitespace — tokens copy-pasted from the UI may have embedded newlines
        api_token = "".join(api_token.split())
        self.api_token = api_token
        # Allow base_url override for non-US regions (AU: app.au.workato.com, EU: app.eu.workato.com)
        if base_url:
            self.BASE_URL = base_url.rstrip("/") + "/api" if not base_url.rstrip("/").endswith("/api") else base_url.rstrip("/")
        self.session = self._requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if email:
            self.session.headers.update({"x-user-email": email})

    def _get(self, path, params=None):
        r = self.session.get(f"{self.BASE_URL}{path}", params=params)
        if not r.ok:
            raise RuntimeError(f"GET {path} → {r.status_code}: {r.text[:300]}")
        return r.json()

    def _post(self, path, body):
        r = self.session.post(f"{self.BASE_URL}{path}", json=body)
        if not r.ok:
            raise RuntimeError(f"POST {path} → {r.status_code}: {r.text[:500]}")
        return r.json()

    # Folders
    def list_folders(self):
        data = self._get("/folders")
        return data.get("items", data) if isinstance(data, dict) else data

    def create_folder(self, name, parent_id=None):
        body = {"name": name}
        if parent_id:
            body["parent_id"] = str(parent_id)
        return self._post("/folders", body)

    def find_or_create_folder(self, name):
        for folder in self.list_folders():
            if folder.get("name") == name:
                return folder["id"]
        result = self.create_folder(name)
        return result["id"]

    # Connections
    def list_connections(self, folder_id=None):
        params = {"folder_id": str(folder_id)} if folder_id else {}
        data = self._get("/connections", params=params)
        return data.get("items", data) if isinstance(data, dict) else data

    def create_connection(self, name, provider, folder_id, input_cfg=None):
        body = {
            "name": name,
            "provider": provider,
            "folder_id": folder_id,
        }
        if input_cfg:
            body["input"] = input_cfg
        return self._post("/connections", body)

    def find_or_create_connection(self, name, provider, folder_id, input_cfg=None):
        for conn in self.list_connections(folder_id):
            if conn.get("name") == name:
                return conn["id"]
        result = self.create_connection(name, provider, folder_id, input_cfg)
        return result["id"]

    # Recipes
    def list_recipes(self, folder_id=None):
        params = {"folder_id": str(folder_id)} if folder_id else {}
        data = self._get("/recipes", params=params)
        return data.get("items", data) if isinstance(data, dict) else data

    def create_recipe(self, name, code, config, folder_id, description=""):
        body = {
            "recipe": {
                "name": name,
                "code": json.dumps(code) if not isinstance(code, str) else code,
                "config": json.dumps(config) if not isinstance(config, str) else config,
                "folder_id": str(folder_id),
                "description": description,
            }
        }
        return self._post("/recipes", body)

    def get_recipe(self, recipe_id):
        return self._get(f"/recipes/{recipe_id}")


# ─── Recipe Code Builders ────────────────────────────────────────────────────

def new_uuid():
    return str(uuid.uuid4())


def _step(number, provider, name, keyword, input_cfg, block=None, label=None):
    """Build a Workato recipe step dict."""
    s = {
        "number": number,
        "provider": provider,
        "name": name,
        "as": name,
        "title": label,
        "keyword": keyword,
        "dynamicPickListSelection": {},
        "toggleCfg": {},
        "input": input_cfg,
        "uuid": new_uuid(),
    }
    if block is not None:
        s["block"] = block
    return s


# ── Trigger builders ─────────────────────────────────────────────────────────

def trigger_http(http_method, path, description="", input_schema=None):
    """
    Workato callable recipe trigger — exposes the recipe as an HTTP endpoint.
    provider: workato, name: callable_recipe, as: callable_recipe (required for pills).

    input_schema: list of flat field dicts with name/type/optional/label.
    IMPORTANT: Workato silently wipes trigger input if input_fields_raw_schema
    contains any type:"object" or type:"array" field — use only scalar types
    (string, integer, number, boolean, date, datetime).
    """
    input_cfg = {
        "http_method": http_method.lower(),
        "request_url_suffix": path,
        "response_type": "dynamic",
    }
    if input_schema:
        input_cfg["input_fields_raw_schema"] = json.dumps(input_schema)
    return {
        "number": 0,
        "keyword": "trigger",
        "provider": "workato",
        "name": "callable_recipe",
        "as": "callable_recipe",
        "title": description or f"Receive {http_method.upper()} {path}",
        "dynamicPickListSelection": {},
        "toggleCfg": {},
        "input": input_cfg,
        "uuid": new_uuid(),
    }


def trigger_scheduler(time_unit="minutes", trigger_every="5", label="Run on schedule"):
    """
    Workato scheduled trigger (clock/scheduled_event).
    time_unit: "seconds" | "minutes" | "hours" | "days" | "weeks" | "months"
    trigger_every: string integer; minimum is "5" when time_unit is "minutes".
    Note: Workato's API does not echo trigger_every back in GET responses when it
    equals the platform default (5 for minutes), but the value is applied at runtime.
    """
    return _step(
        number=0,
        provider="clock",
        name="scheduled_event",
        keyword="trigger",
        input_cfg={"time_unit": time_unit, "trigger_every": str(trigger_every)},
        label=label,
    )


# ── Action builders ──────────────────────────────────────────────────────────

def action_pg_search(number, table, where_clause="", where_params=None, label="Search rows"):
    """PostgreSQL search_rows action."""
    input_cfg = {"schema_table_name": f"public.{table}"}
    if where_clause:
        input_cfg["where_clause"] = where_clause
    if where_params:
        input_cfg["input"] = [
            {"name": k, "type": "string", "value": v} for k, v in where_params.items()
        ]
    return _step(number, "postgresql", "search_rows", "action", input_cfg, label=label)


def action_pg_insert(number, table, field_map, label="Insert row"):
    """PostgreSQL insert_row action."""
    return _step(number, "postgresql", "insert_row", "action", {
        "schema_table_name": f"public.{table}",
        "input": [{"name": k, "value": v} for k, v in field_map.items()],
    }, label=label)


def action_pg_update(number, table, field_map, where_clause="", where_params=None, label="Update rows"):
    """PostgreSQL update_rows action."""
    input_cfg = {
        "schema_table_name": f"public.{table}",
        "input": [{"name": k, "value": v} for k, v in field_map.items()],
    }
    if where_clause:
        input_cfg["where_clause"] = where_clause
    if where_params:
        input_cfg["where_input"] = [
            {"name": k, "type": "string", "value": v} for k, v in where_params.items()
        ]
    return _step(number, "postgresql", "update_rows", "action", input_cfg, label=label)


def action_http_response(number, body_expr, status_code="200", label="Return response"):
    """Callable recipe HTTP response action."""
    return _step(number, "workato", "callable_recipe_response", "action", {
        "response_body": body_expr,
        "response_status_code": str(status_code),
        "reply_content_type": "application/json",
    }, label=label)


def _control_step(number, keyword, input_cfg=None, block=None, label=None, as_alias=None):
    """
    Build a Workato built-in keyword step (if, else, each, rescue).
    These must NOT have provider/name/as/dynamicPickListSelection — Workato will
    reject or misrender them if those fields are present.
    """
    s = {
        "number": number,
        "keyword": keyword,
        "uuid": new_uuid(),
    }
    if label:
        s["title"] = label
    if as_alias:
        s["as"] = as_alias
    if input_cfg:
        s["input"] = input_cfg
    if block is not None:
        s["block"] = block
    return s


def action_if(number, lhs, operator, rhs, true_block, label="If condition"):
    """
    Workato IF keyword step.

    Correct format: keyword="if" with compound conditions input.
    DO NOT use keyword="action" + provider="workato" + name="if_condition" —
    that renders as 'Select an app and action' in the Workato UI.

    operator: one of equals, not_equals, greater_than, less_than, contains,
              starts_with, is_empty, is_not_empty
    """
    cond = {"operand": operator, "lhs": lhs}
    if operator not in ("is_empty", "is_not_empty"):
        cond["rhs"] = rhs
    return _control_step(number, "if", input_cfg={
        "type": "compound",
        "operand": "and",
        "conditions": [cond],
    }, block=true_block, label=label)


def action_if_multi(number, conditions, conjunction, true_block, label="If condition"):
    """
    Workato IF with multiple conditions (AND/OR).
    conditions: list of {"operand": op, "lhs": lhs_pill, "rhs": rhs_value}
    conjunction: "and" | "or"
    """
    return _control_step(number, "if", input_cfg={
        "type": "compound",
        "operand": conjunction,
        "conditions": conditions,
    }, block=true_block, label=label)


def action_else(number, block, label=None):
    """
    Workato ELSE keyword step.
    Must immediately follow an IF step at the same nesting level.
    DO NOT use keyword="action" + name="else_condition".
    """
    return _control_step(number, "else", block=block, label=label)


def action_note(number, message, label="Note"):
    """Placeholder step for logic that requires manual implementation."""
    return _step(number, "workato", "custom_action", "action", {
        "note": message,
    }, label=f"[REVIEW REQUIRED] {label}")


def action_repeat(number, source_list, block, label="Repeat for each", as_alias="loop_item"):
    """
    Workato EACH keyword step (foreach loop).

    Correct format: keyword="each" with input={"source": "<pill or array>"}.
    DO NOT use keyword="action" + name="repeat" or name="repeat_for_each" —
    that renders as 'Select an app and action' in the Workato UI.

    source_list: a data pill string or literal array. If the source is a JSON
    string pill (e.g. from a callable_recipe string field), append .parse_json:
        "#{_dp('...').parse_json}"
    as_alias: the loop variable name (default "loop_item").
    """
    return _control_step(number, "each", input_cfg={"source": source_list or "[]"},
                         block=block, label=label, as_alias=as_alias)


def action_monitor(monitor_num, rescue_num, try_steps, catch_steps, label=None):
    """
    Build a Workato 'Handle errors' monitor+rescue block.

    Pattern: monitor (outer try-body wrapper) contains all try_steps followed
    by a rescue (nested catch block) that contains catch_steps.

        monitor  ← labeled "Handle errors" in the UI
          try_step_1
          try_step_2
          rescue  ← catch block (nested inside monitor)
            catch_step_1

    rescue_num MUST come from self.next_num() AFTER all try_steps and catch_steps
    are built, so the counter is correct and there are no number collisions.
    """
    rescue = _control_step(rescue_num, "rescue", block=list(catch_steps), label=None)
    return {
        "number": monitor_num,
        "keyword": "monitor",
        "uuid": new_uuid(),
        "title": label or "Handle errors",
        "block": list(try_steps) + [rescue],
    }


def _parse_condition_text(condition_text):
    """
    Try to split 'field OPERATOR value' condition text into (operand, operator, value).
    Falls back gracefully if the text doesn't match a known pattern.
    """
    if not condition_text:
        return "condition", "equals", "true"
    # Handle 'field EQUALS value', 'field == value', 'field != value', etc.
    patterns = [
        (r"(.+?)\s+(EQUALS|==|IS EQUAL TO)\s+(.+)", "equals"),
        (r"(.+?)\s+(NOT EQUALS|!=|IS NOT EQUAL TO)\s+(.+)", "not_equals"),
        (r"(.+?)\s+(GREATER THAN|>)\s+(.+)", "greater_than"),
        (r"(.+?)\s+(LESS THAN|<)\s+(.+)", "less_than"),
        (r"(.+?)\s+(CONTAINS)\s+(.+)", "contains"),
        (r"(.+?)\s+(STARTS WITH)\s+(.+)", "starts_with"),
        (r"(.+?)\s+(IS EMPTY|IS NULL)", None),
    ]
    import re as _re
    for pattern, wt_op in patterns:
        m = _re.match(pattern, condition_text.strip(), _re.IGNORECASE)
        if m:
            operand = m.group(1).strip()
            value   = m.group(3).strip() if len(m.groups()) >= 3 else ""
            return operand, wt_op or "equals", value
    # If no pattern matched, use the full condition as operand with a note
    return condition_text.strip(), "equals", "true"


# ─── Spec → Workato Recipe Translator ────────────────────────────────────────

class RecipeBuilder:
    """
    Translates a single flow from the migration spec into a Workato recipe.
    Handles: HTTP triggers, DB CRUD, static responses, transforms, Groovy scripts.
    """

    def __init__(self, flow, spec):
        self.flow = flow
        self.spec = spec
        self.step_counter = 0
        self.notes = []  # Items flagged for manual review

    def next_num(self):
        self.step_counter += 1
        return self.step_counter

    def build(self):
        """Build and return (trigger_with_block, config_list, notes)."""
        trigger = self._build_trigger()
        if trigger is None:
            return None, [], ["No trigger built — flow trigger type not supported"]

        steps = self._build_steps()
        trigger["block"] = steps

        config = self._build_config()
        return trigger, config, self.notes

    def _build_trigger(self):
        t = self.flow.get("trigger", {})
        ttype = t.get("type", "")

        if ttype == "http_listener":
            method = t.get("http_method", "GET")
            path = t.get("rest_path") or t.get("path", "/endpoint")
            description = t.get("label", "")
            # Build a flat input schema from the trigger's input field definitions.
            # CRITICAL: Only scalar types (string/integer/number/boolean/date/datetime).
            # type:"object" or type:"array" with of:"object" silently wipes the whole
            # trigger input in Workato — flatten them before passing.
            raw_fields = t.get("input_fields") or t.get("inputs") or []
            input_schema = self._flatten_fields_to_scalar(raw_fields) if raw_fields else None
            return trigger_http(method, path, description, input_schema=input_schema)

        if ttype in ("scheduler", "scheduled"):
            return trigger_scheduler()

        self.notes.append(f"Trigger type '{ttype}' not automatically mapped — created placeholder")
        return trigger_http("GET", "/migrated-endpoint", f"Placeholder trigger for '{self.flow['name']}'")

    def _flatten_fields_to_scalar(self, fields, prefix=""):
        """
        Recursively flatten a nested field list to only scalar Workato types.
        type:"object" fields are exploded to prefix_fieldname_subfieldname.
        type:"array" fields are converted to type:"string" (caller serializes as JSON).
        Workato silently wipes trigger input if any non-scalar type appears.
        """
        scalar_types = {"string", "integer", "number", "boolean", "date", "datetime"}
        result = []
        for f in fields:
            name = (prefix + f.get("name", "field")) if not prefix else f"{prefix}_{f.get('name', 'field')}"
            ftype = f.get("type", "string")
            sub_fields = f.get("properties") or f.get("fields") or []
            if ftype == "object" and sub_fields:
                result.extend(self._flatten_fields_to_scalar(sub_fields, prefix=name))
            elif ftype == "array":
                # Represent as a JSON string — caller parses with .parse_json pill
                result.append({
                    "name": name,
                    "type": "string",
                    "optional": f.get("optional", True),
                    "label": f.get("label", name) + " (JSON string)",
                })
            elif ftype in scalar_types:
                result.append({
                    "name": name,
                    "type": ftype,
                    "optional": f.get("optional", True),
                    "label": f.get("label", name),
                })
            else:
                # Unknown type — default to string
                result.append({
                    "name": name,
                    "type": "string",
                    "optional": f.get("optional", True),
                    "label": f.get("label", name),
                })
        return result

    def _build_steps(self):
        """
        Build all top-level recipe steps wrapped in a Workato 'Handle errors' monitor block.
        Structure: monitor { ...action steps..., rescue {} }
        The rescue block is always present (empty by default — add handlers in the GUI).
        """
        # Reserve number 1 for the monitor wrapper before building inner steps
        monitor_num = self.next_num()

        inner = []
        for step in self.flow.get("steps", []):
            inner.extend(self._build_one_step(step))

        # Add callable-recipe default response if none was generated
        trigger_type = self.flow.get("trigger", {}).get("type", "")
        if inner and trigger_type == "http_listener":
            if not any(s.get("name") == "callable_recipe_response" for s in inner):
                inner.append(action_http_response(
                    self.next_num(), '{"status": "ok"}', "200", "Return response"
                ))

        # Wrap all steps in a top-level Handle Errors monitor block.
        # Empty rescue catch block — add error-handling steps in the Workato GUI.
        rescue_num = self.next_num()   # must come AFTER all inner steps are built
        return [action_monitor(monitor_num, rescue_num, inner, [], label="Handle errors")]

    def _build_steps_list(self, steps):
        """Build steps from a nested list (true_steps, false_steps, loop_steps, etc.)."""
        blocks = []
        for step in (steps or []):
            blocks.extend(self._build_one_step(step))
        return blocks

    def _build_one_step(self, step):
        """
        Convert a single spec step to a list of Workato action dicts.
        Returns a list so branching steps (IF+ELSE) can emit multiple actions.
        """
        stype = step.get("type", "")
        num   = self.next_num()
        label = step.get("label") or stype

        # ── Control flow: IF / ELSE ───────────────────────────────────────
        if stype in ("choice_router", "choice_router_multi"):
            condition   = step.get("condition", "")
            true_steps  = self._build_steps_list(step.get("true_steps", []))
            false_steps = self._build_steps_list(step.get("false_steps", []))
            operand, operator, value = _parse_condition_text(condition)

            result = [action_if(num, operand, operator, value, true_steps, label=label)]
            if false_steps:
                result.append(action_else(self.next_num(), false_steps))
            return result

        # ── Loop: foreach / while ─────────────────────────────────────────
        if stype in ("loop", "foreach", "try_scope"):
            # try_scope is a monitoring wrapper, not a real loop — handled below
            if stype == "try_scope":
                pass
            else:
                loop_steps = self._build_steps_list(
                    step.get("loop_steps", step.get("monitored_steps", []))
                )
                loop_over = step.get("loop_over", step.get("collection", ""))
                return [action_repeat(num, loop_over, loop_steps, label=label)]

        # ── Try/Catch: monitor+rescue ────────────────────────────────────
        if stype in ("try_catch", "try_scope"):
            # Pattern: monitor (labeled "Handle errors") is the outer try-body wrapper;
            # rescue is the nested catch block inside the monitor.
            # spec can use {try_steps, catch_steps} or legacy {monitored_steps}.
            try_steps_raw   = step.get("try_steps") or step.get("monitored_steps") or []
            catch_steps_raw = step.get("catch_steps") or step.get("error_steps") or []
            try_steps   = self._build_steps_list(try_steps_raw)
            rescue_num  = self.next_num()   # after try_steps, before catch_steps
            catch_steps = self._build_steps_list(catch_steps_raw)  # get nums > rescue_num
            return [action_monitor(num, rescue_num, try_steps, catch_steps, label=label)]

        # ── Database ──────────────────────────────────────────────────────
        if stype == "db_select":
            return [self._db_select(num, step)]
        if stype == "db_insert":
            return [self._db_insert(num, step)]
        if stype == "db_update":
            return [self._db_update(num, step)]
        if stype == "db_delete":
            note = f"DB DELETE on table '{step.get('table')}' — implement as Workato delete_rows action"
            self.notes.append(note)
            return [action_note(num, note, label=label)]

        # ── Sequence (structural container) ──────────────────────────────
        if stype == "sequence":
            sub = step.get("steps") or step.get("loop_steps") or []
            return self._build_steps_list(sub)

        # ── Route / Switch (multi-way branch) ────────────────────────────
        if stype == "route":
            # Workato has no switch keyword — model as nested IF/ELSE chain.
            paths = step.get("paths") or []
            switch_var = step.get("switch_variable", "variable")
            if not paths:
                note = f"Empty route on '{switch_var}' — no paths to generate"
                self.notes.append(note)
                return [action_note(num, note, label=label)]
            result = []
            for j, path in enumerate(paths):
                p_label = path.get("label") or path.get("condition") or f"path_{j+1}"
                p_steps = self._build_steps_list(path.get("steps", []))
                if j < len(paths) - 1:
                    step_num = num if j == 0 else self.next_num()
                    result.append(action_if(step_num, switch_var, "equals", p_label, p_steps,
                                            label=f"If {switch_var} = {p_label}"))
                else:
                    result.append(action_else(self.next_num(), p_steps))
            return result

        # ── Exception / Exit ─────────────────────────────────────────────
        if stype == "exception":
            note = f"EXIT — implement as Workato 'Stop job' action"
            return [action_note(num, note, label=label)]

        # ── Response / Payload ────────────────────────────────────────────
        if stype in ("set_payload", "return_response"):
            content = step.get("static_content", step.get("response_body", ""))
            status  = step.get("status_code", "200")
            return [action_http_response(num, content, status, label)]

        # ── Transform (Map) ───────────────────────────────────────────────
        if stype == "transform":
            note = (
                f"Map step '{label}' — implement field mapping in Workato using "
                f"formula pills or a dedicated recipe step"
            )
            self.notes.append(note)
            return [action_note(num, note, label=label)]

        # ── Set Variable / Properties ─────────────────────────────────────
        if stype == "set_variable":
            var_name  = step.get("variable_name", label)
            var_value = step.get("variable_value", step.get("value", ""))
            return [_step(num, "workato", "set_variable", "action",
                          {"variable_name": var_name, "value": var_value},
                          label=f"Set {var_name}")]

        # ── Custom Script (Groovy / DataWeave) ────────────────────────────
        if stype == "custom_script":
            purpose = step.get("purpose", "custom_transform")
            script  = step.get("script", "")
            note = (
                f"{purpose} script — implement in Workato using formula pills or custom Ruby. "
                f"Original:\n{script[:300]}{'...' if len(script) > 300 else ''}"
            )
            self.notes.append(note)
            return [action_note(num, note, label=label)]

        # ── Logger ────────────────────────────────────────────────────────
        if stype in ("logger", "log_message"):
            return []   # Workato has built-in execution logs

        # ── Subprocess / flow_ref ─────────────────────────────────────────
        if stype in ("subprocess_call", "flow_ref"):
            note = f"Subprocess '{label}' — create a separate callable Workato recipe and invoke it here"
            self.notes.append(note)
            return [action_note(num, note, label=label)]

        # ── HTTP Request ──────────────────────────────────────────────────
        if stype == "http_request":
            method = step.get("http_method", step.get("method", "GET")).lower()
            path   = step.get("path", step.get("url", "/"))
            return [_step(num, "http", method, "action",
                          {"url": path, "request_type": "json"},
                          label=label)]

        # ── Salesforce ────────────────────────────────────────────────────
        if stype in ("salesforce_action", "salesforce_query", "salesforce_create",
                     "salesforce_update", "salesforce_upsert", "salesforce_delete"):
            sf_op  = step.get("salesforce_operation", stype.split("_")[-1].upper())
            sf_obj = step.get("salesforce_object", step.get("object_type", ""))
            return [_step(num, "salesforce", sf_op.lower(), "action",
                          {"sobject_name": sf_obj},
                          label=label)]

        # ── Connector action (generic catch-all) ──────────────────────────
        if stype == "connector_action":
            provider = step.get("workato_provider") or step.get("config_ref") or "workato"
            wt_name  = step.get("workato_name") or "custom_action"
            if provider and wt_name:
                return [_step(num, provider, wt_name, "action", {}, label=label)]

        # ── Fallback ──────────────────────────────────────────────────────
        note = f"Step type '{stype}' ('{label}') — manual Workato implementation required"
        self.notes.append(note)
        return [action_note(num, note, label=label)]

    def _db_select(self, number, step):
        sql = step.get("sql", "")
        table = step.get("table", "table")
        params = step.get("params", [])
        label = step.get("label", f"Search {table}")

        # Build Workato where clause from SQL params
        where_clause, where_params = self._sql_to_workato_where(sql, params)

        return action_pg_search(
            number=number,
            table=table,
            where_clause=where_clause,
            where_params=where_params,
            label=label,
        )

    def _db_insert(self, number, step):
        sql = step.get("sql", "")
        table = step.get("table", "table")
        params = step.get("params", [])
        label = step.get("label", f"Insert into {table}")

        # Map $param_name → trigger input pill
        field_map = {p: self._param_to_workato_ref(p) for p in params}
        return action_pg_insert(number, table, field_map, label=label)

    def _db_update(self, number, step):
        sql = step.get("sql", "")
        table = step.get("table", "table")
        params = step.get("params", [])
        label = step.get("label", f"Update {table}")

        # For UPDATE: separate SET params from WHERE params
        # Heuristic: "id" param is a WHERE param, rest are SET params
        where_params_list = [p for p in params if p.lower() in ("id", "key")]
        set_params_list = [p for p in params if p not in where_params_list]

        # If no obvious WHERE param found, use all as SET and note it
        if not where_params_list and params:
            where_params_list = [params[-1]]
            set_params_list = params[:-1]

        field_map = {p: self._param_to_workato_ref(p) for p in set_params_list}
        where_clause = " AND ".join(f'{p} = "{{{{input.{p}}}}}"' for p in where_params_list)
        where_params = {p: self._param_to_workato_ref(p) for p in where_params_list}

        return action_pg_update(number, table, field_map, where_clause, where_params, label=label)

    def _sql_to_workato_where(self, sql, params):
        """
        Convert a Boomi SQL WHERE clause ($param notation) to Workato format.
        Returns (where_clause_str, where_params_dict).
        """
        if not sql or not params:
            return "", {}

        # Extract WHERE clause
        m = re.search(r"WHERE\s+(.+?)(?:ORDER BY|GROUP BY|LIMIT|$)", sql, re.IGNORECASE | re.DOTALL)
        if not m:
            return "", {p: self._param_to_workato_ref(p) for p in params}

        where_raw = m.group(1).strip()
        # Replace $param with Workato pill syntax for the where_clause display
        where_display = re.sub(r"\$(\w+)", lambda m: f'"{{{{input.{m.group(1)}}}}}"', where_raw)

        where_params = {p: self._param_to_workato_ref(p) for p in params}
        return where_display, where_params

    def _param_to_workato_ref(self, param_name):
        """Map a Boomi SQL $param_name to a Workato formula pill."""
        # Common REST patterns: camelCase in body, snake_case in DB
        camel = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), param_name)
        return f"#{{trigger_input['{camel}'] || trigger_input['{param_name}']}}"

    def _build_config(self):
        """
        Build the config list declaring which external connectors are used.
        Only external provider connections belong here — never "workato" itself.
        """
        config = []
        for step in self.flow.get("steps", []):
            step_type = step.get("type", "")
            if step_type.startswith("db_"):
                entry = {"keyword": "application", "name": "postgresql", "provider": "postgresql"}
                if entry not in config:
                    config.append(entry)
        return config


# ─── DB Connection Setup ─────────────────────────────────────────────────────

def get_pg_connection_id(client, spec, folder_id):
    """Find or create a PostgreSQL connection for this migration."""
    existing = os.environ.get("WORKATO_PG_CONN_ID")
    if existing:
        print(f"  Using existing PostgreSQL connection: {existing}")
        return existing

    # Try to extract connection info from spec
    conn_info = {}
    for conn in spec.get("connections", {}).values():
        if conn.get("type") == "db" and conn.get("driver") in ("postgresql", "postgres"):
            conn_info = conn
            break

    conn_name = f"MIG_{spec.get('project_name', 'Project')}_PostgreSQL"
    input_cfg = {
        "host": os.environ.get("WORKATO_PG_HOST", conn_info.get("host", "db.internal")),
        "port": os.environ.get("WORKATO_PG_PORT", conn_info.get("port", "5432")),
        "database": os.environ.get("WORKATO_PG_DATABASE", conn_info.get("database", "crm")),
        "username": os.environ.get("WORKATO_PG_USERNAME", ""),
        "password": os.environ.get("WORKATO_PG_PASSWORD", ""),
    }

    conn_id = client.find_or_create_connection(conn_name, "postgresql", folder_id, input_cfg)
    print(f"  PostgreSQL connection: '{conn_name}' (id: {conn_id})")
    return conn_id


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate Workato recipes from any migration spec JSON."
    )
    parser.add_argument("spec", nargs="?", default="migration-specs/boomi-customer-api.json",
                        help="Path to migration spec JSON (default: migration-specs/boomi-customer-api.json)")
    parser.add_argument("--folder", default=None,
                        help="Workato folder name (default: MIG_<project_name>)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print generated recipe JSON without calling the Workato API")
    args = parser.parse_args()

    # Load spec
    if not os.path.isfile(args.spec):
        print(f"ERROR: Spec file not found: {args.spec}", file=sys.stderr)
        sys.exit(1)

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    project_name = spec.get("project_name", "MigrationProject")
    folder_name = args.folder or f"MIG_{project_name}"
    flows = spec.get("integrations", [])

    print(f"Loaded spec: {project_name}")
    print(f"  Source system : {spec.get('source_system', 'unknown')}")
    print(f"  Flows         : {len(flows)}")
    print(f"  Target folder : {folder_name}")

    # Dry run — just print
    if args.dry_run:
        print("\n=== DRY RUN ===\n")
        for flow in flows:
            builder = RecipeBuilder(flow, spec)
            code, config, notes = builder.build()
            flow_name = flow['name']
            recipe_name = flow_name if flow_name.upper().startswith("MIG_") else f"MIG_{flow_name}"
            print(f"Recipe: {recipe_name}")
            print(json.dumps(code, indent=2))
            if notes:
                print(f"\nManual review required ({len(notes)} items):")
                for n in notes:
                    print(f"  • {n[:120]}")
            print("-" * 60)
        return

    # Live run
    api_token = os.environ.get("WORKATO_API_TOKEN") or _load_env_var("WORKATO_API_TOKEN")
    email     = os.environ.get("WORKATO_EMAIL")     or _load_env_var("WORKATO_EMAIL")
    base_url  = os.environ.get("WORKATO_BASE_URL")  or _load_env_var("WORKATO_BASE_URL") or ""

    if not api_token:
        print("ERROR: WORKATO_API_TOKEN not set.", file=sys.stderr)
        print("  Add it to your .env file: WORKATO_API_TOKEN=your_token_here", file=sys.stderr)
        sys.exit(1)

    # Show token prefix so the user can verify which token is being used
    token_preview = api_token[:12] + "..." if len(api_token) > 12 else api_token
    print(f"  Token loaded : {token_preview}  (email: {email or 'not set'})")
    if base_url:
        print(f"  Base URL     : {base_url}")

    client = WorkatoClient(api_token, email, base_url=base_url or None)

    print(f"\nConnecting to Workato API...")

    # Ensure folder
    print(f"Ensuring folder '{folder_name}'...")
    folder_id = client.find_or_create_folder(folder_name)
    print(f"  Folder id: {folder_id}")

    # Ensure DB connection (if any flows use a DB)
    needs_pg = any(
        step.get("type", "").startswith("db_")
        for flow in flows
        for step in flow.get("steps", [])
    )
    pg_conn_id = None
    if needs_pg:
        print(f"\nEnsuring PostgreSQL connection...")
        pg_conn_id = get_pg_connection_id(client, spec, folder_id)

    # Generate and push recipes
    print(f"\nCreating {len(flows)} recipes...")
    results = []
    all_notes = []

    for flow in flows:
        flow_name = flow['name']
        # Avoid double MIG_ prefix if the source name already starts with MIG_
        if flow_name.upper().startswith("MIG_"):
            recipe_name = flow_name
        else:
            recipe_name = f"MIG_{flow_name}"
        print(f"  Creating '{recipe_name}'...")

        builder = RecipeBuilder(flow, spec)
        code, config, notes = builder.build()
        all_notes.extend([(recipe_name, n) for n in notes])

        if code is None:
            print(f"    SKIP: no recipe built")
            results.append({"name": recipe_name, "status": "skipped"})
            continue

        description = (
            f"Migrated from {spec.get('source_system', 'source')} by migration-agent. "
            f"Source flow: {flow['name']}. Generated: {datetime.utcnow().isoformat()}Z"
        )

        try:
            result = client.create_recipe(recipe_name, code, config, folder_id, description)
            recipe_id = result.get("id")
            print(f"    Created (id: {recipe_id})")
            results.append({"name": recipe_name, "id": recipe_id, "status": "created", "manual_review_items": len(notes)})
            time.sleep(0.3)
        except Exception as e:
            print(f"    FAILED: {e}", file=sys.stderr)
            results.append({"name": recipe_name, "status": "failed", "error": str(e)})

    # Save output
    output = {
        "project": project_name,
        "folder_id": folder_id,
        "folder_name": folder_name,
        "pg_connection_id": pg_conn_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "recipes": results,
        "manual_review_required": [
            {"recipe": name, "note": note} for name, note in all_notes
        ],
    }

    output_path = args.spec.replace(".json", "_workato_output.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 50}")
    created = sum(1 for r in results if r["status"] == "created")
    print(f"Done. {created}/{len(flows)} recipes created.")
    print(f"Output saved to: {output_path}")

    if all_notes:
        print(f"\n[!] {len(all_notes)} items require manual review in Workato:")
        for recipe_name, note in all_notes[:10]:
            print(f"   [{recipe_name}] {note[:100]}")
        if len(all_notes) > 10:
            print(f"   ... and {len(all_notes) - 10} more (see output file)")


def _load_env_var(key):
    """Try to load a variable from .env file (fallback if not in environment)."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.isfile(env_path):
        return None
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


if __name__ == "__main__":
    main()
