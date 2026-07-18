from pathlib import Path
import json
import shutil
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.ingestion.worker import replay


class PublishedReleaseReplayTests(TestCase):
    def _require_local_raw(self, release):
        items = json.loads((release / "raw-artifacts.json").read_text(encoding="utf-8"))
        if not items or not all(Path(item["path"]).exists() for item in items):
            self.skipTest("Third-party raw artifacts are intentionally local and are not in Git.")

    def test_first_real_data_release_replays_from_raw_artifacts(self):
        release = Path("data/releases/2026-07-17.1")
        if not release.exists():
            self.skipTest("The first real-data release has not been built locally.")
        self._require_local_raw(release)
        self.assertTrue(replay(release))

    def test_stabilized_release_replays_with_manifest_checksums(self):
        release = Path("data/releases/2026-07-18.2")
        if not release.exists():
            self.skipTest("The stabilization release has not been built locally.")
        self._require_local_raw(release)
        self.assertTrue(replay(release))

    def test_replay_rejects_tampered_release_payload(self):
        release = Path("data/releases/2026-07-18.2")
        if not release.exists():
            self.skipTest("The stabilization release has not been built locally.")
        self._require_local_raw(release)
        with TemporaryDirectory() as directory:
            copied = Path(directory) / "release"
            shutil.copytree(release, copied)
            with (copied / "scores.jsonl").open("a", encoding="utf-8") as stream:
                stream.write("{}\n")
            self.assertFalse(replay(copied))
