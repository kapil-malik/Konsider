import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from konsider.domain.display_catalog import DisplayCatalogError, load_product_display_catalog

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "data" / "catalogs" / "product-display-catalog.json"
SCHEMA_PATH = ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json"


def _payload() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _load_payload(tmp_path: Path, payload: dict):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return load_product_display_catalog(path, SCHEMA_PATH)


def test_authoring_schema_is_valid_and_catalog_loads() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    catalog = load_product_display_catalog(CATALOG_PATH, SCHEMA_PATH)
    assert catalog.schema_version == "konsider-product-display-catalog-1.0"
    assert catalog.catalog_version == "2026-08-07.1"
    assert catalog.checksum.startswith("sha256:")
    assert [
        len(catalog.definitions(role))
        for role in (
            "ORDERING_CRITERION",
            "OPPORTUNITY_FILTER",
            "TYPED_FEASIBILITY_CHECK",
        )
    ] == [14, 9, 3]


def test_definition_resolves_immutable_section_metadata() -> None:
    catalog = load_product_display_catalog(CATALOG_PATH, SCHEMA_PATH)
    definition = catalog.definition("OPPORTUNITY_FILTER", "technology_software_opportunity")
    assert definition.display_name == "Technology and software employment ecosystem"
    assert definition.compact_name == "Technology and software"
    assert definition.section_id == "career"
    assert definition.section_name == "Career"
    with pytest.raises(AttributeError):
        definition.display_name = "Changed"  # type: ignore[misc]


def test_nullable_display_fields_are_preserved() -> None:
    catalog = load_product_display_catalog(CATALOG_PATH, SCHEMA_PATH)
    definition = catalog.definition("TYPED_FEASIBILITY_CHECK", "post_study_work_pathway")
    assert definition.compact_name == "Work options after College"
    assert definition.section_id is None
    assert definition.section_name is None
    assert catalog.definition("ORDERING_CRITERION", "political_stability").compact_name is None


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda value: value["definitions"].append(copy.deepcopy(value["definitions"][0])),
            "Duplicate display definition",
        ),
        (
            lambda value: value["sections"].append(copy.deepcopy(value["sections"][0])),
            "Duplicate display section",
        ),
        (
            lambda value: value["definitions"][0].update(sectionId="missing"),
            "references missing section",
        ),
        (
            lambda value: value["definitions"][0].update(displayName=" "),
            "displayName must not be blank",
        ),
        (
            lambda value: value["definitions"][0].update(compactName=" "),
            "compactName must not be blank",
        ),
        (
            lambda value: value["definitions"][1].update(sortOrder=10),
            "Duplicate definition sortOrder",
        ),
        (lambda value: value["sections"][1].update(sortOrder=10), "Duplicate section sortOrder"),
    ],
)
def test_semantic_invariants_fail_closed(tmp_path: Path, mutation, message: str) -> None:
    payload = _payload()
    mutation(payload)
    with pytest.raises(DisplayCatalogError, match=message):
        _load_payload(tmp_path, payload)


def test_exact_inventory_rejects_missing_and_unexpected_ids() -> None:
    catalog = load_product_display_catalog(CATALOG_PATH, SCHEMA_PATH)
    with pytest.raises(DisplayCatalogError, match="missing=.*expected.*unexpected=.*C66"):
        catalog.require_exact_ids(
            {
                "ORDERING_CRITERION": {"expected"},
                "OPPORTUNITY_FILTER": {
                    item.id for item in catalog.definitions("OPPORTUNITY_FILTER")
                },
                "TYPED_FEASIBILITY_CHECK": {
                    item.id for item in catalog.definitions("TYPED_FEASIBILITY_CHECK")
                },
            }
        )


def test_authoring_catalog_exactly_matches_golden_display_values() -> None:
    catalog = load_product_display_catalog(CATALOG_PATH, SCHEMA_PATH)
    golden = json.loads(
        (ROOT / "tests" / "fixtures" / "catalog-display-metadata-golden.json").read_text(
            encoding="utf-8"
        )
    )
    actual = [
        {
            "productRole": item.product_role,
            "id": item.id,
            "displayName": item.display_name,
            "compactName": item.compact_name,
            "sectionName": item.section_name,
        }
        for role in ("ORDERING_CRITERION", "OPPORTUNITY_FILTER", "TYPED_FEASIBILITY_CHECK")
        for item in catalog.definitions(role)
    ]
    assert actual == golden["definitions"]
