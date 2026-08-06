"""Generate the display-metadata migration baseline from immutable releases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROLE_ORDERING = "ORDERING_CRITERION"
ROLE_OPPORTUNITY = "OPPORTUNITY_FILTER"
ROLE_TFC = "TYPED_FEASIBILITY_CHECK"
OFC_SECTION_NAMES = {"CAREER": "Career", "EDUCATION": "Education"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _value(record: dict[str, Any], new_key: str, old_key: str) -> Any:
    if new_key in record:
        return record[new_key]
    return record[old_key]


def _definition(
    product_role: str,
    definition_id: str,
    display_name: str,
    compact_name: str | None,
    section_name: str | None,
) -> dict[str, str | None]:
    return {
        "productRole": product_role,
        "id": definition_id,
        "displayName": display_name,
        "compactName": compact_name,
        "sectionName": section_name,
    }


def build_inventory(
    release_root: Path,
    *,
    base_release_id: str | None = None,
    overlay_release_id: str | None = None,
) -> dict[str, Any]:
    if base_release_id is None:
        pointer = _read_json(release_root / "active.json")
        active_release_id = pointer["release_id"]
        active_manifest = _read_json(release_root / active_release_id / "manifest.json")
        if "base_release" in active_manifest:
            base_release_id = active_manifest["base_release"]["release_id"]
            overlay_release_id = active_release_id
        else:
            base_release_id = active_release_id

    base_path = release_root / base_release_id
    consumer = _read_json(base_path / "consumer-catalog.json")
    opportunity = _read_json(base_path / "opportunity-filter-catalog.json")
    definitions: list[dict[str, str | None]] = []

    for item in consumer["criteria"]:
        definitions.append(
            _definition(
                ROLE_ORDERING,
                item["id"],
                _value(item, "displayName", "display_name"),
                item.get("compactName"),
                _value(item, "sectionName", "category"),
            )
        )

    for item in opportunity["definitions"]:
        section_name = item.get("sectionName")
        if "sectionName" not in item:
            try:
                section_name = OFC_SECTION_NAMES[item["category"]]
            except KeyError as error:
                raise ValueError(
                    f"Unknown OFC display category: {item.get('category')!r}"
                ) from error
        definitions.append(
            _definition(
                ROLE_OPPORTUNITY,
                item["id"],
                _value(item, "displayName", "display_name"),
                _value(item, "compactName", "compact_label"),
                section_name,
            )
        )

    if overlay_release_id is None:
        raise ValueError("The golden inventory requires a TFC overlay release.")
    tfc = _read_json(release_root / overlay_release_id / "tfc-catalog.json")
    for item in tfc["definitions"]:
        definitions.append(
            _definition(
                ROLE_TFC,
                item.get("id", item.get("tfc_id")),
                _value(item, "displayName", "name"),
                item.get("compactName"),
                item.get("sectionName"),
            )
        )

    return {
        "schemaVersion": "konsider-display-metadata-golden-1.0",
        "sourceReleases": {
            "baseReleaseId": base_release_id,
            "tfcOverlayReleaseId": overlay_release_id,
        },
        "definitions": definitions,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, default=Path("data/releases"))
    parser.add_argument("--base-release-id")
    parser.add_argument("--overlay-release-id")
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    inventory = build_inventory(
        args.release_root,
        base_release_id=args.base_release_id,
        overlay_release_id=args.overlay_release_id,
    )
    rendered = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    if args.check is not None:
        if args.check.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Display metadata differs from {args.check}")
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
