import hashlib
import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.ingestion.models import MetricObservation, RawArtifact, SourceRecordReference
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release
from konsider.repositories.release_repository import ReleaseRepository


def _publish_sample_release(root: Path, release_id: str) -> tuple[ReleaseRepository, Path]:
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
    repository = ReleaseRepository(root)
    repository.write_draft(release_id, [observation], scores, [artifact], [], report)
    return repository, repository.publish(release_id, require_product_ready=False)


class PublicationTests(TestCase):
    def test_published_release_is_immutable_and_pointer_is_atomic(self):
        with TemporaryDirectory() as directory:
            repository, published = _publish_sample_release(Path(directory), "r1")
            self.assertTrue(published.exists())
            self.assertEqual(
                json.loads((Path(directory) / "active.json").read_text())["release_id"], "r1"
            )
            with self.assertRaises(FileExistsError):
                repository.write_draft("r1", [], [], [], [], validate_release([], [], []))

    def test_generated_release_text_is_lf_and_checksums_match_final_bytes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _, published = _publish_sample_release(root, "lf-release")
            manifest = json.loads((published / "manifest.json").read_text(encoding="utf-8"))

            for path in [*published.glob("*.json"), *published.glob("*.jsonl")]:
                payload = path.read_bytes()
                self.assertNotIn(b"\r\n", payload)
                self.assertEqual(payload.replace(b"\r\n", b"\n"), payload)

            for filename, expected in manifest["file_checksums"].items():
                actual = hashlib.sha256((published / filename).read_bytes()).hexdigest()
                self.assertEqual(expected, f"sha256:{actual}")

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

    def test_catalog_ready_criterion_must_pass_before_pointer_activation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text(
                json.dumps(
                    {
                        "criteria": [
                            {
                                "id": "required_metric",
                                "ready": True,
                                "default_enabled": True,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            repository = ReleaseRepository(root / "releases", catalog)
            (root / "releases" / ".draft" / "candidate").mkdir(parents=True)
            (root / "releases" / ".draft" / "candidate" / "validation.json").write_text(
                json.dumps(
                    {
                        "structural_passed": True,
                        "product_ready": True,
                        "criterion_readiness": {"required_metric": False},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "required_metric"):
                repository.publish("candidate")
            self.assertFalse((root / "releases" / "active.json").exists())
