import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGETS = (
    "src/konsider/ingestion/phase4f.py",
    "src/konsider/ingestion/phase4_wave2.py",
    "src/konsider/ingestion/phase5_locality_onboarding.py",
    "src/konsider/ingestion/phase6_career_opportunity.py",
    "src/konsider/ingestion/phase6_education_opportunity.py",
    "src/konsider/ingestion/phase6_release_publication.py",
    "src/konsider/ingestion/tfc_first_wave.py",
)
CONFIG_CLASSES = {
    "LocalityCriterionConfig",
    "CareerFilterConfig",
    "EducationFilterConfig",
}
FORBIDDEN_CONFIG_FIELDS = {
    "display_name",
    "displayName",
    "compact_label",
    "compactName",
    "name",
    "category",
}


def _trees() -> list[tuple[str, ast.Module]]:
    return [
        (relative, ast.parse((ROOT / relative).read_text(encoding="utf-8"))) for relative in TARGETS
    ]


def test_production_configs_have_no_display_metadata_fields() -> None:
    found: dict[str, set[str]] = {}
    for relative, tree in _trees():
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in CONFIG_CLASSES:
                fields = {
                    child.target.id
                    for child in node.body
                    if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)
                }
                forbidden = fields & FORBIDDEN_CONFIG_FIELDS
                if forbidden:
                    found[f"{relative}:{node.name}"] = forbidden
    assert found == {}


def test_publication_has_no_accepted_name_dictionary() -> None:
    publication = dict(_trees())["src/konsider/ingestion/phase6_release_publication.py"]
    assigned_names = {
        target.id
        for node in ast.walk(publication)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(target, ast.Name)
    }
    assert "EXPECTED_NAMES" not in assigned_names
    assert "EXPECTED_FILTER_IDS" in assigned_names


def test_production_builders_contain_no_standalone_current_title_literals() -> None:
    golden = json.loads(
        (ROOT / "tests" / "fixtures" / "catalog-display-metadata-golden.json").read_text(
            encoding="utf-8"
        )
    )
    current_titles = {
        value
        for item in golden["definitions"]
        for value in (item["displayName"], item["compactName"], item["sectionName"])
        if value is not None
    }
    occurrences = []
    for relative, tree in _trees():
        occurrences.extend(
            (relative, node.lineno, node.value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value in current_titles
        )
    assert occurrences == []
