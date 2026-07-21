import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.ingestion.models import MetricObservation, RawArtifact, SourceRecordReference
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release
from konsider.repositories.release_repository import ReleaseRepository


class PublicationTests(TestCase):
    def test_published_release_is_immutable_and_pointer_is_atomic(self):
        with TemporaryDirectory() as directory:
            artifact = RawArtifact(
                "sha256:a",
                "source",
                "u",
                "u",
                "2026-01-01T00:00:00+00:00",
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
            scores = score_observations([observation])
            report = validate_release(
                [observation], scores, [artifact], min_criteria=1, min_country_coverage=1
            )
            repository = ReleaseRepository(Path(directory))
            repository.write_draft("r1", [observation], scores, [artifact], [], report)
            published = repository.publish("r1", require_product_ready=False)
            self.assertTrue(published.exists())
            self.assertEqual(
                json.loads((Path(directory) / "active.json").read_text())["release_id"], "r1"
            )
            with self.assertRaises(FileExistsError):
                repository.write_draft("r1", [observation], scores, [artifact], [], report)

    def test_structural_validation_error_blocks_publication(self):
        with TemporaryDirectory() as directory:
            artifact = RawArtifact(
                "sha256:a",
                "source",
                "u",
                "u",
                "2026-01-01T00:00:00+00:00",
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
                "2023-01-01",
                "2023-12-31",
                "source",
                ("sha256:missing",),
                (SourceRecordReference("sha256:missing", "$[0]", "IND|2023"),),
                "estimated",
                "national",
                "parser-v",
                "method-v",
                ("wdi_distribution", "population_level_not_expat_access"),
            )
            scores = score_observations([observation])
            report = validate_release(
                [observation], scores, [artifact], min_criteria=1, min_country_coverage=1
            )
            repository = ReleaseRepository(Path(directory))
            repository.write_draft("invalid", [observation], scores, [artifact], [], report)
            with self.assertRaises(ValueError):
                repository.publish("invalid", require_product_ready=False)

    def test_product_readiness_gate_blocks_structurally_valid_candidate(self):
        with TemporaryDirectory() as directory:
            artifact = RawArtifact(
                "sha256:a",
                "source",
                "u",
                "u",
                "2026-01-01T00:00:00+00:00",
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
            scores = score_observations([observation])
            report = validate_release(
                [observation], scores, [artifact], min_criteria=1, min_country_coverage=1
            )
            report = replace(report, structural_passed=True, product_ready=False)
            repository = ReleaseRepository(Path(directory))
            repository.write_draft("not-ready", [observation], scores, [artifact], [], report)

            with self.assertRaisesRegex(ValueError, "fewer than five"):
                repository.publish("not-ready")
