import hashlib
import json
import shutil
from pathlib import Path
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

    def test_world_bank_candidate_release_contract(self):
        release = Path("data/releases/2026-07-21.1")
        self.assertTrue(release.exists())
        manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
        validation = json.loads((release / "validation.json").read_text(encoding="utf-8"))
        sources = json.loads((release / "sources.json").read_text(encoding="utf-8"))
        artifacts = json.loads((release / "raw-artifacts.json").read_text(encoding="utf-8"))
        observations = [
            json.loads(row)
            for row in (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        attempts = [
            json.loads(row)
            for row in (release / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(manifest["schema_version"], "konsider-release-3.0")
        self.assertEqual(manifest["status"], "published")
        self.assertEqual(manifest["observation_count"], 120)
        self.assertEqual(manifest["attempt_count"], 120)
        self.assertTrue(validation["structural_passed"])
        self.assertTrue(validation["product_ready"])
        self.assertEqual(validation["ready_criterion_count"], 5)
        self.assertFalse(validation["criterion_readiness"]["uhc_service_coverage_index"])
        self.assertEqual(len(sources), 6)
        self.assertTrue(
            all(
                source["license_name"] == "Creative Commons Attribution 4.0 International"
                for source in sources
            )
        )
        self.assertTrue(
            all(
                source["license_evidence"] and source["methodology_url"] and source["attribution"]
                for source in sources
            )
        )
        self.assertEqual(
            len(
                {
                    (item["source_id"], item["country_code"], item["criterion_id"])
                    for item in attempts
                }
            ),
            120,
        )
        self.assertEqual({item["status"] for item in attempts}, {"success"})
        artifact_ids = {item["artifact_id"] for item in artifacts}
        for observation in observations:
            referenced = {record["artifact_id"] for record in observation["source_records"]}
            self.assertEqual(set(observation["raw_artifact_ids"]), referenced)
            self.assertTrue(referenced <= artifact_ids)
            self.assertTrue(
                all(
                    record["locator"] and record["record_id"]
                    for record in observation["source_records"]
                )
            )
            for component in observation.get("components", []):
                self.assertIn(component["source_record"], observation["source_records"])

        file_checksums = {}
        for name, expected in manifest["file_checksums"].items():
            actual = hashlib.sha256((release / name).read_bytes()).hexdigest()
            self.assertEqual(expected, f"sha256:{actual}")
            file_checksums[name] = expected
        release_digest = hashlib.sha256(
            json.dumps(file_checksums, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.assertEqual(manifest["release_checksum"], f"sha256:{release_digest}")

    def test_packaging_corrected_release_is_lf_and_semantically_unchanged(self):
        original = Path("data/releases/2026-07-20.2")
        corrected = Path("data/releases/2026-07-21.1")
        manifest = json.loads((corrected / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["previous_release_id"], "2026-07-20.2")
        for name in manifest["file_checksums"]:
            corrected_bytes = (corrected / name).read_bytes()
            self.assertNotIn(b"\r\n", corrected_bytes)
            if name.endswith(".jsonl"):
                original_payload = [
                    json.loads(row)
                    for row in (original / name).read_text(encoding="utf-8").splitlines()
                ]
                corrected_payload = [
                    json.loads(row) for row in corrected_bytes.decode("utf-8").splitlines()
                ]
            else:
                original_payload = json.loads((original / name).read_text(encoding="utf-8"))
                corrected_payload = json.loads(corrected_bytes)
            self.assertEqual(corrected_payload, original_payload)

    def test_world_bank_candidate_release_replays_from_local_raw(self):
        release = Path("data/releases/2026-07-21.1")
        self._require_local_raw(release)
        self.assertTrue(replay(release))

    def test_final_91_country_release_contract_and_replay(self):
        release = Path("data/releases/2026-07-27.1")
        manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
        validation = json.loads((release / "validation.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["previous_release_id"], "2026-07-26.3")
        self.assertEqual(manifest["country_count"], 91)
        self.assertEqual(manifest["country_universe"]["universe_id"], "stable_supported_v1")
        self.assertEqual(manifest["observation_count"], 819)
        self.assertEqual(manifest["score_count"], 819)
        self.assertEqual(set(validation["criterion_coverage"].values()), {91})
        self.assertTrue(validation["structural_passed"])
        self.assertTrue(validation["product_ready"])
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
