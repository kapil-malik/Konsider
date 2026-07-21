"""JSON Schema validation for immutable release-consumer contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class ContractError(ValueError):
    """Raised when a published consumer payload violates its contract."""


class UnsupportedContractError(ContractError):
    """Raised when a payload declares an unsupported contract major."""


SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "contracts" / "schemas" / "v1"
SUPPORTED_MAJORS = {
    "konsider-release": 3,
    "validation": 3,
    "consumer-catalog": 1,
}


def require_supported_version(value: object, family: str) -> None:
    match = re.fullmatch(rf"{re.escape(family)}-(\d+)\.\d+", str(value))
    if not match or int(match.group(1)) != SUPPORTED_MAJORS[family]:
        raise UnsupportedContractError(
            f"Unsupported {family} schema version {value!r}; "
            f"supported major is {SUPPORTED_MAJORS[family]}."
        )


def validate_contract(payload: Any, schema_name: str, *, context: str) -> None:
    schema_path = SCHEMA_ROOT / f"{schema_name}.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path)
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ContractError(f"Invalid {context} at {location}: {error.message}")
