import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from konsider.research.feasibility_probe import load_definition, run_probe

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "phase3d"
DEFINITIONS = ROOT / "data" / "research" / "phase3d"
UNIVERSE = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
NOW = datetime(2026, 7, 24, tzinfo=UTC)


class FeasibilityProbeTests(TestCase):
    def _run(
        self,
        directory: str,
        definition_name: str,
        fixtures: tuple[str, ...],
        *,
        definition_override=None,
        run_id: str = "fixture-run",
        output_name: str = "reports",
        raw_name: str = "raw",
        release_name: str = "releases",
    ):
        root = Path(directory)
        release_root = root / release_name
        release_root.mkdir(parents=True, exist_ok=True)
        active = b'{"release_id":"stable-test"}\n'
        (release_root / "active.json").write_bytes(active)
        definition = definition_override or load_definition(DEFINITIONS / definition_name)
        output, summary = run_probe(
            definition,
            run_id,
            mode="fixture",
            output_root=root / output_name,
            raw_root=root / raw_name,
            universe_path=UNIVERSE,
            release_root=release_root,
            fixture_paths=tuple(FIXTURES / item for item in fixtures),
            clock=lambda: NOW,
        )
        self.assertEqual((release_root / "active.json").read_bytes(), active)
        return output, summary

    def test_c30_world_bank_fixture_is_clean_91_country_path(self):
        with TemporaryDirectory() as directory:
            output, summary = self._run(
                directory,
                "c30-world-bank.json",
                ("c30-world-bank.json",),
            )
            self.assertEqual(summary["found"], 91)
            self.assertEqual(summary["fresh"], 91)
            self.assertEqual(summary["parsed"], 91)
            self.assertEqual(summary["validated"], 91)
            self.assertEqual(summary["valid"], 91)
            self.assertEqual(summary["missing"], 0)
            self.assertEqual(summary["unmapped"], 0)
            self.assertTrue(summary["probe_threshold_passed"])
            self.assertTrue(summary["full_91_passed"])
            rows = [
                json.loads(line)
                for line in (output / "country-results.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertEqual(len(rows), 91)
            self.assertEqual({row["status"] for row in rows}, {"valid"})
            self.assertTrue((output / "manifest.json").exists())

    def test_c11_ilostat_fixture_has_explicit_88_valid_and_three_missing(self):
        with TemporaryDirectory() as directory:
            output, summary = self._run(
                directory,
                "c11-ilostat.json",
                (
                    "c11-unemployment.csv",
                    "c11-employment.csv",
                    "c11-participation.csv",
                ),
            )
            self.assertEqual(summary["found"], 88)
            self.assertEqual(summary["fresh"], 88)
            self.assertEqual(summary["parsed"], 88)
            self.assertEqual(summary["validated"], 88)
            self.assertEqual(summary["valid"], 88)
            self.assertEqual(summary["missing"], 3)
            self.assertTrue(summary["probe_threshold_passed"])
            self.assertFalse(summary["full_91_passed"])
            rows = [
                json.loads(line)
                for line in (output / "country-results.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            missing = {row["country_code"]: row for row in rows if row["status"] == "missing"}
            self.assertEqual(set(missing), {"ATG", "GRD", "UKR"})
            self.assertTrue(
                all(
                    row["reason_codes"] == ["COV_SOURCE_RECORD_MISSING"] for row in missing.values()
                )
            )
            self.assertTrue(
                all(
                    set(row["values"])
                    == {
                        "unemployment_rate",
                        "employment_to_population_ratio",
                        "labour_force_participation_rate",
                    }
                    for row in rows
                    if row["status"] == "valid"
                )
            )

    def test_freshness_rule_and_reason_codes_are_deterministic(self):
        definition = replace(
            load_definition(DEFINITIONS / "c11-ilostat.json"),
            freshness_min_year=2026,
        )
        with TemporaryDirectory() as directory:
            _, summary = self._run(
                directory,
                "c11-ilostat.json",
                (
                    "c11-unemployment.csv",
                    "c11-employment.csv",
                    "c11-participation.csv",
                ),
                definition_override=definition,
            )
            self.assertEqual(summary["found"], 88)
            self.assertEqual(summary["fresh"], 0)
            self.assertEqual(summary["validated"], 88)
            self.assertEqual(summary["stale"], 88)
            self.assertEqual(summary["missing"], 3)
            self.assertFalse(summary["probe_threshold_passed"])

    def test_mapping_validation_parse_and_unmapped_states_are_explicit(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            payload = json.loads((FIXTURES / "c30-world-bank.json").read_text())
            for row in payload[1]:
                if row["countryiso3code"] == "USA":
                    row["countryiso3code"] = "USA_ALT"
                    row["country"]["value"] = "United States of America"
                elif row["countryiso3code"] == "ALB":
                    row["value"] = 150
                elif row["countryiso3code"] == "ARE":
                    row["value"] = "not-a-number"
            payload[1].append(
                {
                    "country": {"id": "ZZZ", "value": "Zedland"},
                    "countryiso3code": "ZZZ",
                    "date": "2024",
                    "value": 1,
                }
            )
            fixture = root / "mutated.json"
            fixture.write_text(json.dumps(payload), encoding="utf-8")
            definition = load_definition(DEFINITIONS / "c30-world-bank.json")
            release_root = root / "releases"
            release_root.mkdir()
            (release_root / "active.json").write_text("stable", encoding="utf-8")
            output, summary = run_probe(
                definition,
                "state-test",
                mode="fixture",
                output_root=root / "reports",
                raw_root=root / "raw",
                universe_path=UNIVERSE,
                release_root=release_root,
                fixture_paths=(fixture,),
                clock=lambda: NOW,
            )
            self.assertEqual(summary["found"], 91)
            self.assertEqual(summary["valid"], 89)
            self.assertEqual(summary["invalid"], 1)
            self.assertEqual(summary["parse_failed"], 1)
            self.assertEqual(summary["unmapped"], 1)
            rows = {
                row["country_code"]: row
                for row in (
                    json.loads(line)
                    for line in (output / "country-results.jsonl")
                    .read_text(encoding="utf-8")
                    .splitlines()
                )
            }
            self.assertEqual(rows["USA"]["mapped_by"], "NAME_ALIAS")
            self.assertEqual(
                rows["ALB"]["reason_codes"],
                ["VAL_VALUE_OUT_OF_RANGE:international_migrant_stock_percent"],
            )
            self.assertEqual(rows["ARE"]["reason_codes"], ["PRS_VALUE_INVALID"])

    def test_output_is_byte_deterministic_and_offline_replay_matches(self):
        with TemporaryDirectory() as directory:
            first, first_summary = self._run(
                directory,
                "c30-world-bank.json",
                ("c30-world-bank.json",),
                output_name="reports-a",
                raw_name="raw-shared",
                release_name="releases-a",
            )
            second, second_summary = self._run(
                directory,
                "c30-world-bank.json",
                ("c30-world-bank.json",),
                output_name="reports-b",
                raw_name="raw-shared",
                release_name="releases-b",
            )
            self.assertEqual(first_summary, second_summary)
            for name in ("country-results.jsonl", "summary.json", "report.md"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            for path in [*first.glob("*.json"), *first.glob("*.jsonl")]:
                self.assertNotIn(b"\r\n", path.read_bytes())
            for name, expected in manifest["files"].items():
                actual = hashlib.sha256((first / name).read_bytes()).hexdigest()
                self.assertEqual(expected, f"sha256:{actual}")

            root = Path(directory)
            replay_release = root / "releases-replay"
            replay_release.mkdir()
            (replay_release / "active.json").write_text("stable", encoding="utf-8")
            replay, replay_summary = run_probe(
                load_definition(DEFINITIONS / "c30-world-bank.json"),
                "offline-replay",
                mode="offline",
                output_root=root / "reports-replay",
                raw_root=root / "raw-shared",
                universe_path=UNIVERSE,
                release_root=replay_release,
                artifact_manifest=first / "raw-artifacts.json",
            )
            self.assertEqual(
                first_summary["raw_artifact_checksums"], replay_summary["raw_artifact_checksums"]
            )
            self.assertEqual(
                (first / "country-results.jsonl").read_bytes(),
                (replay / "country-results.jsonl").read_bytes(),
            )
