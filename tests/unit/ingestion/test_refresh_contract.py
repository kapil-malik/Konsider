from datetime import UTC, datetime

import pytest

from konsider.ingestion.models import MetricObservation, RawArtifact, SourceRecordReference
from konsider.ingestion.registry import SOURCES, world_bank_query_range
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release
from konsider.ingestion.worker import refresh


def test_world_bank_range_advances_beyond_2026() -> None:
    assert world_bank_query_range(2018, 2031) == "2018:2031"


def test_freshness_uses_injected_clock() -> None:
    artifact = RawArtifact(
        "sha256:a",
        "source",
        "url",
        "url",
        "2030-01-01T00:00:00+00:00",
        "json",
        1,
        "a",
        "v",
        "p",
        "path",
    )
    observation = MetricObservation(
        "obs",
        "IND",
        "uhc_service_coverage_index",
        75,
        "index_0_100",
        "2026-01-01",
        "2026-12-31",
        "world_bank_uhc",
        ("sha256:a",),
        (SourceRecordReference("sha256:a", "$[0]", "IND|2026"),),
        "estimated",
        "national",
        "parser-v",
        "method-v",
        ("wdi_distribution", "population_level_not_expat_access"),
    )
    report = validate_release(
        [observation],
        score_observations([observation]),
        [artifact],
        sources=[SOURCES["world_bank_uhc"]],
        min_criteria=1,
        min_country_coverage=1,
        clock=lambda: datetime(2030, 1, 1, tzinfo=UTC),
    )
    assert any(issue.code == "source_stale" for issue in report.issues)


def test_refresh_requires_explicit_source_version_acknowledgement(tmp_path) -> None:
    with pytest.raises(ValueError, match="explicit source_versions"):
        refresh("future", raw_root=tmp_path / "raw", release_root=tmp_path / "releases")
