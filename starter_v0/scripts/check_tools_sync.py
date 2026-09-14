"""Deterministic sync check for tool declarations (no model, no network).

Verifies that artifacts/tools.yaml stays consistent with:
  - the registry in tools/__init__.py and each Python signature;
  - the frontmatter of tools/<name>/TOOL.md;
  - enum values the implementation and mock data actually support;
  - expected tool args in every data/eval_*.json file;
  - the Gemini SDK schema model (when google-genai is installed).

Usage (from starter_v0/):
    python scripts/check_tools_sync.py
    python scripts/check_tools_sync.py --tools artifacts/tools.yaml
"""
from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools  # noqa: E402
from tools.create_ticket.tool import ASSET_ID_PATTERN  # noqa: E402
from tools.search_device_info.tool import QUERY_LABELS  # noqa: E402

JSON_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}


def frontmatter(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {}
    parts = raw.split("---", 2)
    return dict(yaml.safe_load(parts[1]) or {}) if len(parts) == 3 else {}


def supported_enums() -> dict[tuple[str, str], set[str]]:
    """Enum values derived from implementation code and mock data, not from tools.yaml."""
    status = json.loads((ROOT / "helpdesk_data" / "service_status.json").read_text(encoding="utf-8"))
    assets = json.loads((ROOT / "helpdesk_data" / "assets.json").read_text(encoding="utf-8"))
    kb_categories = {str(frontmatter(p).get("category", "general")).lower() for p in (ROOT / "helpdesk_data" / "knowledge_base").glob("*.md")}
    policy_areas = {
        str(frontmatter(p).get("policy_area") or p.stem).lower()
        for p in (ROOT / "company_policy").glob("*.md")
        if frontmatter(p)
    }
    diagnostic_keys = {key for item in assets["assets"] for key in item["diagnostics"]}
    return {
        ("check_service_status", "service"): {item["service"] for item in status["services"]},
        ("check_service_status", "environment"): {item["environment"] for item in status["services"]},
        ("inspect_device", "check"): diagnostic_keys | {"all"},
        ("search_kb", "category"): kb_categories | {"all"},
        ("policy", "policy_area"): policy_areas | {"all"},
        ("create_ticket", "priority"): {"low", "medium", "high", "critical"},
        ("search_device_info", "query_type"): set(QUERY_LABELS),
        ("format_incident_report", "template"): {"brief", "technical", "handoff"},
        ("clarify", "response_type"): {"text", "yes_no", "choice"},
    }


def check_value(schema: dict[str, Any], value: Any) -> str | None:
    expected_type = JSON_TYPES.get(schema.get("type", ""))
    if expected_type and not isinstance(value, expected_type):
        return f"type {type(value).__name__} does not match {schema['type']}"
    if expected_type is int and isinstance(value, bool):
        return "boolean is not an integer"
    if "enum" in schema and value not in schema["enum"]:
        return f"{value!r} not in enum {schema['enum']}"
    if "pattern" in schema and isinstance(value, str) and not re.fullmatch(schema["pattern"], value):
        return f"{value!r} does not match pattern {schema['pattern']}"
    if "minimum" in schema and isinstance(value, (int, float)) and value < schema["minimum"]:
        return f"{value!r} below minimum {schema['minimum']}"
    if "maximum" in schema and isinstance(value, (int, float)) and value > schema["maximum"]:
        return f"{value!r} above maximum {schema['maximum']}"
    return None


def run_checks(tools_path: Path) -> list[str]:
    errors: list[str] = []
    declarations = load_tool_declarations(tools_path)
    by_name = {item["name"]: item for item in declarations}

    # 1. Registry <-> declarations
    if len(by_name) != len(declarations):
        errors.append("duplicate tool names in tools.yaml")
    for name in sorted(set(by_name) - set(TOOL_FUNCTIONS)):
        errors.append(f"{name}: declared in tools.yaml but missing from tools/__init__.py")
    for name in sorted(set(TOOL_FUNCTIONS) - set(by_name)):
        errors.append(f"{name}: registered in tools/__init__.py but not declared in tools.yaml")

    enums = supported_enums()
    for name, decl in by_name.items():
        func = TOOL_FUNCTIONS.get(name)
        if func is None:
            continue
        params = decl.get("parameters", {})
        props: dict[str, Any] = params.get("properties", {})
        required = params.get("required", [])
        signature = inspect.signature(func).parameters

        if not str(decl.get("description", "")).strip():
            errors.append(f"{name}: empty description")

        # 2. Declared args <-> Python signature
        for arg in props:
            if arg not in signature:
                errors.append(f"{name}.{arg}: declared but not accepted by {func.__name__}()")
        for arg, param in signature.items():
            if arg not in props:
                errors.append(f"{name}.{arg}: accepted by {func.__name__}() but not declared")
            elif param.default is inspect.Parameter.empty and arg not in required:
                errors.append(f"{name}.{arg}: has no Python default, must be required")
        for arg in required:
            if arg not in props:
                errors.append(f"{name}: required arg {arg!r} has no property")

        for arg, schema in props.items():
            if not str(schema.get("description", "")).strip():
                errors.append(f"{name}.{arg}: empty description")
            if "type" not in schema:
                errors.append(f"{name}.{arg}: missing type")
            if "default" in schema:
                problem = check_value(schema, schema["default"])
                if problem:
                    errors.append(f"{name}.{arg}: default {problem}")
            # 3. Enums <-> implementation / mock data
            supported = enums.get((name, arg))
            if supported is not None:
                declared = set(schema.get("enum", []))
                if not declared:
                    errors.append(f"{name}.{arg}: should declare enum {sorted(supported)}")
                elif declared != supported:
                    missing = sorted(supported - declared)
                    unsupported = sorted(declared - supported)
                    errors.append(f"{name}.{arg}: enum mismatch (missing={missing}, unsupported={unsupported})")

        # 4. TOOL.md frontmatter
        tool_md = ROOT / "tools" / name / "TOOL.md"
        if not tool_md.exists():
            errors.append(f"{name}: missing tools/{name}/TOOL.md")
        else:
            meta = frontmatter(tool_md)
            if meta.get("name") != name:
                errors.append(f"{name}: TOOL.md name is {meta.get('name')!r}")
            if set(meta.get("inputs") or []) != set(props):
                errors.append(f"{name}: TOOL.md inputs {meta.get('inputs')} != tools.yaml {sorted(props)}")

    # 5. Asset/employee patterns agree with implementation guards
    asset_pattern = by_name.get("inspect_device", {}).get("parameters", {}).get("properties", {}).get("asset_id", {}).get("pattern")
    if asset_pattern:
        assets = json.loads((ROOT / "helpdesk_data" / "assets.json").read_text(encoding="utf-8"))
        for item in assets["assets"]:
            if not re.fullmatch(asset_pattern, item["asset_id"]) or not ASSET_ID_PATTERN.fullmatch(item["asset_id"]):
                errors.append(f"inspect_device.asset_id: pattern rejects fixture {item['asset_id']}")
    employee_pattern = by_name.get("lookup_user", {}).get("parameters", {}).get("properties", {}).get("employee_id", {}).get("pattern")
    if employee_pattern:
        users = json.loads((ROOT / "helpdesk_data" / "users.json").read_text(encoding="utf-8"))
        for item in users["users"]:
            if not re.fullmatch(employee_pattern, item["employee_id"]):
                errors.append(f"lookup_user.employee_id: pattern rejects fixture {item['employee_id']}")

    # 6. Eval expectations <-> schema
    for eval_path in sorted((ROOT / "data").glob("eval_*.json")):
        data = json.loads(eval_path.read_text(encoding="utf-8"))
        for case in data.get("cases", []):
            for call in case.get("expect", {}).get("tool_calls", []):
                decl = by_name.get(call.get("name"))
                where = f"{eval_path.name}:{case.get('id')}"
                if decl is None:
                    errors.append(f"{where}: expected tool {call.get('name')!r} not declared")
                    continue
                props = decl.get("parameters", {}).get("properties", {})
                for arg, value in call.get("args", {}).items():
                    if arg not in props:
                        errors.append(f"{where}: expected arg {call['name']}.{arg} not declared")
                        continue
                    schema = props[arg]
                    if schema.get("type") == "array":
                        item_schema = schema.get("items", {})
                        for element in value:
                            problem = check_value(item_schema, element)
                            if problem:
                                errors.append(f"{where}: {call['name']}.{arg}[] {problem}")
                    else:
                        problem = check_value(schema, value)
                        if problem:
                            errors.append(f"{where}: {call['name']}.{arg} {problem}")

    # 7. Gemini SDK accepts the schema (offline pydantic validation)
    try:
        from google.genai import types
    except ImportError:
        print("note: google-genai not installed; skipped Gemini schema validation")
    else:
        for tool in to_openai_tools(declarations):
            function = tool["function"]
            try:
                types.Tool(function_declarations=[{
                    "name": function["name"],
                    "description": function["description"],
                    "parameters": function["parameters"],
                }])
            except Exception as exc:  # pydantic ValidationError
                errors.append(f"{function['name']}: rejected by Gemini SDK schema: {str(exc).splitlines()[0]}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    args = parser.parse_args()
    errors = run_checks(args.tools)
    declarations = load_tool_declarations(args.tools)
    if errors:
        print(f"FAIL {len(errors)} issue(s) in {args.tools}:")
        for line in errors:
            print(f"  - {line}")
        raise SystemExit(1)
    print(f"PASS {len(declarations)} tools in sync: {', '.join(item['name'] for item in declarations)}")


if __name__ == "__main__":
    main()
