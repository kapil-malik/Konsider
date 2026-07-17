from dataclasses import replace
from unittest import TestCase

from konsider.ingestion.models import MetricObservation, RawArtifact
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release


class ValidationTests(TestCase):
    def setUp(self):
        self.artifact = RawArtifact("sha256:a", "source", "url", "url", "now", "json", 1, "a", "v", "p", "path")
        self.observation = MetricObservation("obs", "IND", "uhc_service_coverage_index", 75, "index_0_100", "2023-01-01", "2023-12-31", "source", ("sha256:a",), "estimated", "national", "v")

    def test_missing_provenance_blocks_publication(self):
        bad = replace(self.observation, raw_artifact_ids=("sha256:missing",))
        report = validate_release([bad], score_observations([bad]), [self.artifact], min_criteria=1, min_country_coverage=1)
        self.assertFalse(report.passed)
        self.assertIn("incomplete_provenance", {issue.code for issue in report.issues})

    def test_valid_minimal_release_passes(self):
        report = validate_release([self.observation], score_observations([self.observation]), [self.artifact], min_criteria=1, min_country_coverage=1)
        self.assertTrue(report.passed)
