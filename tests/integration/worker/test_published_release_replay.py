from pathlib import Path
from unittest import TestCase

from konsider.ingestion.worker import replay


class PublishedReleaseReplayTests(TestCase):
    def test_first_real_data_release_replays_from_raw_artifacts(self):
        release = Path("data/releases/2026-07-17.1")
        if not release.exists():
            self.skipTest("The first real-data release has not been built locally.")
        self.assertTrue(replay(release))
