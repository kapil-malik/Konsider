import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "catalog-display-metadata-golden.json"


def test_golden_inventory_matches_source_release_pair() -> None:
    inventory = json.loads(FIXTURE.read_text(encoding="utf-8"))
    source = inventory["sourceReleases"]
    release_root = ROOT / "data" / "releases"
    if not (release_root / source["baseReleaseId"]).is_dir():
        release_root /= ".draft"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_display_metadata_inventory.py"),
            "--release-root",
            str(release_root),
            "--base-release-id",
            source["baseReleaseId"],
            "--overlay-release-id",
            source["tfcOverlayReleaseId"],
            "--check",
            str(FIXTURE),
        ],
        check=True,
    )


def test_golden_inventory_has_complete_unique_role_inventories() -> None:
    definitions = json.loads(FIXTURE.read_text(encoding="utf-8"))["definitions"]
    keys = [(item["productRole"], item["id"]) for item in definitions]
    assert len(keys) == len(set(keys))
    assert Counter(item["productRole"] for item in definitions) == {
        "ORDERING_CRITERION": 14,
        "OPPORTUNITY_FILTER": 9,
        "TYPED_FEASIBILITY_CHECK": 3,
    }
    assert all(item["displayName"].strip() == item["displayName"] for item in definitions)
    assert all(item["displayName"] for item in definitions)
