"""Export authoritative API v2 OpenAPI and generated TypeScript component types."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from konsider.api.app import create_app  # noqa: E402


def type_script_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return f'components["schemas"][{json.dumps(name)}]'
    if "anyOf" in schema:
        return " | ".join(type_script_type(item) for item in schema["anyOf"])
    if "allOf" in schema:
        return " & ".join(type_script_type(item) for item in schema["allOf"])
    if "enum" in schema:
        return " | ".join(json.dumps(item) for item in schema["enum"])
    kind = schema.get("type")
    if kind == "string":
        return "string"
    if kind in {"number", "integer"}:
        return "number"
    if kind == "boolean":
        return "boolean"
    if kind == "null":
        return "null"
    if kind == "array":
        return f"Array<{type_script_type(schema.get('items', {}))}>"
    if kind == "object" or "properties" in schema or "additionalProperties" in schema:
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        fields = [
            f"{json.dumps(name)}{'?' if name not in required else ''}: {type_script_type(value)}"
            for name, value in properties.items()
        ]
        additional = schema.get("additionalProperties")
        if additional:
            value_type = "unknown" if additional is True else type_script_type(additional)
            if not fields:
                return f"Record<string, {value_type}>"
        return "{ " + "; ".join(fields) + " }"
    return "unknown"


openapi = create_app().openapi()
api_directory = ROOT / "web" / "src" / "api"
api_directory.mkdir(parents=True, exist_ok=True)
serialized_openapi = json.dumps(openapi, indent=2, sort_keys=True) + "\n"
(api_directory / "openapi.json").write_text(serialized_openapi, encoding="utf-8")
contract_directory = ROOT / "contracts" / "openapi"
contract_directory.mkdir(parents=True, exist_ok=True)
(contract_directory / "konsider-api-2.0.json").write_text(
    serialized_openapi,
    encoding="utf-8",
)

component_lines = [
    "// konsider-api-types-2.0",
    "// Generated from FastAPI OpenAPI by scripts/export_openapi.py. Do not edit.",
    "export interface components {",
    "  schemas: {",
]
for name, schema in sorted(openapi["components"]["schemas"].items()):
    component_lines.append(f"    {json.dumps(name)}: {type_script_type(schema)}")
component_lines.extend(["  }", "}", ""])
(api_directory / "schema.d.ts").write_text("\n".join(component_lines), encoding="utf-8")
