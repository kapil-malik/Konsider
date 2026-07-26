from dataclasses import replace
from unittest import TestCase

from konsider.ingestion.models import MetricObservation, RawArtifact, SourceRecordReference
from konsider.ingestion.registry import SOURCES
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release


class ValidationTests(TestCase):
    def setUp(self):
        self.artifact = RawArtifact(
            "sha256:a",
            "source",
            "url",
            "url",
            "2026-01-01T00:00:00+00:00",
            "json",
            1,
            "a",
            "v",
            "p",
            "path",
        )
        self.observation = MetricObservation(
            "obs",
            "IND",
            "uhc_service_coverage_index",
            75,
            "index_0_100",
            "2023-01-01",
            "2023-12-31",
            "source",
            ("sha256:a",),
            (SourceRecordReference("sha256:a", "$[0]", "IND|2023"),),
            "estimated",
            "national",
            "parser-v",
            "method-v",
            ("wdi_distribution", "population_level_not_expat_access"),
        )

    def test_missing_provenance_blocks_publication(self):
        bad = replace(self.observation, raw_artifact_ids=("sha256:missing",))
        report = validate_release(
            [bad],
            score_observations([bad]),
            [self.artifact],
            min_criteria=1,
            min_country_coverage=1,
        )
        self.assertFalse(report.passed)
        self.assertIn("incomplete_record_provenance", {issue.code for issue in report.issues})

    def test_valid_minimal_release_passes(self):
        report = validate_release(
            [self.observation],
            score_observations([self.observation]),
            [self.artifact],
            min_criteria=1,
            min_country_coverage=1,
        )
        self.assertTrue(report.passed)

    def test_expected_attempt_matrix_is_required_when_sources_are_supplied(self):
        report = validate_release(
            [self.observation],
            score_observations([self.observation]),
            [self.artifact],
            [],
            [SOURCES["world_bank_uhc"]],
            min_criteria=1,
            min_country_coverage=1,
        )
        self.assertFalse(report.structural_passed)
        self.assertIn("attempt_matrix_incomplete", {issue.code for issue in report.issues})

    def test_material_change_is_flagged_for_product_review(self):
        previous = replace(self.observation, value=50)
        report = validate_release(
            [self.observation],
            score_observations([self.observation]),
            [self.artifact],
            min_criteria=1,
            min_country_coverage=1,
            previous_observations=[previous],
        )
        self.assertIn("material_change_review", {issue.code for issue in report.issues})
