from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, cast

from jsonschema import Draft202012Validator

ProductRole = Literal[
    "ORDERING_CRITERION",
    "OPPORTUNITY_FILTER",
    "TYPED_FEASIBILITY_CHECK",
]
PRODUCT_ROLES: tuple[ProductRole, ...] = (
    "ORDERING_CRITERION",
    "OPPORTUNITY_FILTER",
    "TYPED_FEASIBILITY_CHECK",
)


class DisplayCatalogError(ValueError):
    pass


@dataclass(frozen=True)
class DisplaySection:
    product_role: ProductRole
    section_id: str
    section_name: str
    sort_order: int


@dataclass(frozen=True)
class DisplayDefinition:
    product_role: ProductRole
    id: str
    display_name: str
    compact_name: str | None
    section_id: str | None
    section_name: str | None
    sort_order: int


class ProductDisplayCatalog:
    def __init__(
        self,
        *,
        schema_version: str,
        catalog_version: str,
        checksum: str,
        sections: tuple[DisplaySection, ...],
        definitions: tuple[DisplayDefinition, ...],
    ) -> None:
        self.schema_version = schema_version
        self.catalog_version = catalog_version
        self.checksum = checksum
        self._sections = sections
        self._definitions = definitions
        self._section_index: Mapping[tuple[ProductRole, str], DisplaySection] = MappingProxyType(
            {(item.product_role, item.section_id): item for item in sections}
        )
        self._definition_index: Mapping[tuple[ProductRole, str], DisplayDefinition] = (
            MappingProxyType({(item.product_role, item.id): item for item in definitions})
        )

    def definition(self, product_role: ProductRole, definition_id: str) -> DisplayDefinition:
        try:
            return self._definition_index[(product_role, definition_id)]
        except KeyError as error:
            raise DisplayCatalogError(
                f"Missing display definition for {product_role}/{definition_id}."
            ) from error

    def definitions(self, product_role: ProductRole) -> tuple[DisplayDefinition, ...]:
        return tuple(item for item in self._definitions if item.product_role == product_role)

    def sections(self, product_role: ProductRole) -> tuple[DisplaySection, ...]:
        return tuple(item for item in self._sections if item.product_role == product_role)

    def require_exact_ids(
        self, expected_ids: Mapping[ProductRole, set[str] | frozenset[str]]
    ) -> None:
        for role in PRODUCT_ROLES:
            actual = {item.id for item in self.definitions(role)}
            expected = set(expected_ids.get(role, set()))
            if actual != expected:
                missing = sorted(expected - actual)
                unexpected = sorted(actual - expected)
                raise DisplayCatalogError(
                    f"Display ID inventory mismatch for {role}: "
                    f"missing={missing}, unexpected={unexpected}."
                )


def _nonblank(value: str, field: str, identity: str) -> None:
    if not value.strip():
        raise DisplayCatalogError(f"{field} must not be blank for {identity}.")


def load_product_display_catalog(
    catalog_path: Path,
    schema_path: Path,
    *,
    expected_ids: Mapping[ProductRole, set[str] | frozenset[str]] | None = None,
) -> ProductDisplayCatalog:
    raw_bytes = catalog_path.read_bytes()
    payload: dict[str, Any] = json.loads(raw_bytes.decode("utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload), key=lambda item: list(item.path)
    )
    if errors:
        error = errors[0]
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        raise DisplayCatalogError(f"Invalid display catalog at {location}: {error.message}")

    section_keys: set[tuple[ProductRole, str]] = set()
    section_orders: set[tuple[ProductRole, int]] = set()
    sections: list[DisplaySection] = []
    for raw in payload["sections"]:
        role = cast(ProductRole, raw["productRole"])
        identity = f"{role}/{raw['sectionId']}"
        _nonblank(raw["sectionName"], "sectionName", identity)
        key = (role, raw["sectionId"])
        if key in section_keys:
            raise DisplayCatalogError(f"Duplicate display section {identity}.")
        order_key = (role, raw["sortOrder"])
        if order_key in section_orders:
            raise DisplayCatalogError(f"Duplicate section sortOrder {raw['sortOrder']} for {role}.")
        section_keys.add(key)
        section_orders.add(order_key)
        sections.append(
            DisplaySection(role, raw["sectionId"], raw["sectionName"], raw["sortOrder"])
        )

    definition_keys: set[tuple[ProductRole, str]] = set()
    definition_orders: set[tuple[ProductRole, int]] = set()
    definitions: list[DisplayDefinition] = []
    section_names = {(item.product_role, item.section_id): item.section_name for item in sections}
    for raw in payload["definitions"]:
        role = cast(ProductRole, raw["productRole"])
        identity = f"{role}/{raw['id']}"
        _nonblank(raw["displayName"], "displayName", identity)
        if raw["compactName"] is not None:
            _nonblank(raw["compactName"], "compactName", identity)
        key = (role, raw["id"])
        if key in definition_keys:
            raise DisplayCatalogError(f"Duplicate display definition {identity}.")
        order_key = (role, raw["sortOrder"])
        if order_key in definition_orders:
            raise DisplayCatalogError(
                f"Duplicate definition sortOrder {raw['sortOrder']} for {role}."
            )
        section_key = (role, raw["sectionId"])
        if raw["sectionId"] is not None and section_key not in section_names:
            raise DisplayCatalogError(
                f"Display definition {identity} references missing section {raw['sectionId']}."
            )
        definition_keys.add(key)
        definition_orders.add(order_key)
        definitions.append(
            DisplayDefinition(
                product_role=role,
                id=raw["id"],
                display_name=raw["displayName"],
                compact_name=raw["compactName"],
                section_id=raw["sectionId"],
                section_name=section_names.get(section_key),
                sort_order=raw["sortOrder"],
            )
        )

    catalog = ProductDisplayCatalog(
        schema_version=payload["schemaVersion"],
        catalog_version=payload["catalogVersion"],
        checksum="sha256:" + hashlib.sha256(raw_bytes).hexdigest(),
        sections=tuple(sorted(sections, key=lambda item: (item.product_role, item.sort_order))),
        definitions=tuple(
            sorted(definitions, key=lambda item: (item.product_role, item.sort_order))
        ),
    )
    if expected_ids is not None:
        catalog.require_exact_ids(expected_ids)
    return catalog
