from pathlib import Path

import pytest

from konsider.repositories.published_release_repository import PublishedReleaseRepository

ROOT = Path(__file__).resolve().parents[2]


def test_frontend_runtime_has_no_deprecated_phase4_contract_access() -> None:
    deprecated = (
        ".profile_id",
        ".resolved_profile_id",
        ".uncertainty_status",
        ".locality_status",
        ".profiles",
    )
    violations: list[str] = []
    for path in sorted((ROOT / "web" / "src").rglob("*")):
        if path.suffix not in {".ts", ".tsx"} or path.name == "generatedContractChecks.ts":
            continue
        text = path.read_text(encoding="utf-8")
        for token in deprecated:
            if token in text:
                violations.append(f"{path.relative_to(ROOT)}: {token}")

    assert not violations, "Deprecated frontend contract access:\n" + "\n".join(violations)


def test_removed_public_api_modules_stay_removed() -> None:
    for relative_path in (
        "src/konsider/api/mappers.py",
        "src/konsider/api/models/catalog.py",
        "src/konsider/api/models/countries.py",
        "src/konsider/api/models/rankings.py",
    ):
        assert not (ROOT / relative_path).exists()


def test_historical_loader_has_no_implicit_active_runtime_path() -> None:
    with pytest.raises(ValueError, match="explicit pointer or release ID"):
        PublishedReleaseRepository()
