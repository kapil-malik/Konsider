"""JSON Schema validation for immutable release-consumer contracts."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


class ContractError(ValueError):
    """Raised when a published consumer payload violates its contract."""


class UnsupportedContractError(ContractError):
    """Raised when a payload declares an unsupported contract major."""


SCHEMA_BASE = Path(__file__).resolve().parents[2] / "contracts" / "schemas"
SCHEMA_ROOT = SCHEMA_BASE / "v1"
SUPPORTED_MAJORS = {
    # The v1 API consumer remains pinned to historical production generations.
    # Schema 5/catalog 3 use CurrentReleaseRepository until the API-v2 migration.
    "konsider-release": frozenset({3, 4}),
    "validation": frozenset({3, 4}),
    "consumer-catalog": frozenset({1, 2}),
}


def require_supported_version(value: object, family: str) -> int:
    match = re.fullmatch(rf"{re.escape(family)}-(\d+)\.\d+", str(value))
    major = int(match.group(1)) if match else None
    supported = SUPPORTED_MAJORS[family]
    if major not in supported:
        rendered = ", ".join(str(item) for item in sorted(supported))
        raise UnsupportedContractError(
            f"Unsupported {family} schema version {value!r}; " f"supported majors are {rendered}."
        )
    return major


def validate_contract(
    payload: Any,
    schema_name: str,
    *,
    context: str,
    schema_generation: int = 1,
) -> None:
    validator = _validator(schema_name, schema_generation)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: list(error.path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ContractError(f"Invalid {context} at {location}: {error.message}")


@lru_cache(maxsize=None)
def _validator(schema_name: str, schema_generation: int) -> Draft202012Validator:
    schema_path = SCHEMA_BASE / f"v{schema_generation}" / f"{schema_name}.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = Registry()
    for candidate in schema_path.parent.glob("*.schema.json"):
        candidate_schema = json.loads(candidate.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            candidate_schema["$id"], Resource.from_contents(candidate_schema)
        )
    return Draft202012Validator(schema, registry=registry)
