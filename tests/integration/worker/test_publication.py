import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.ingestion.models import MetricObservation, RawArtifact
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release
from konsider.repositories.release_repository import ReleaseRepository


class PublicationTests(TestCase):
    def test_published_release_is_immutable_and_pointer_is_atomic(self):
        with TemporaryDirectory() as directory:
            artifact = RawArtifact("sha256:a", "source", "u", "u", "now", "json", 1, "a", "v", "p", "path")
            observation = MetricObservation("obs", "IND", "uhc_service_coverage_index", 75, "index_0_100", "2023-01-01", "2023-12-31", "source", ("sha256:a",), "estimated", "national", "v")
            scores = score_observations([observation])
            report = validate_release([observation], scores, [artifact], min_criteria=1, min_country_coverage=1)
            repository = ReleaseRepository(Path(directory))
            repository.write_draft("r1", [observation], scores, [artifact], [], report)
            published = repository.publish("r1")
            self.assertTrue(published.exists())
            self.assertEqual(json.loads((Path(directory) / "active.json").read_text())["release_id"], "r1")
            with self.assertRaises(FileExistsError):
                repository.write_draft("r1", [observation], scores, [artifact], [], report)
