"""Build and offline-verify the Phase 3E deterministic aggregate report."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path

from konsider.research.feasibility_probe import load_definition, run_probe
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "data" / "reports" / "feasibility-probes"
OUTPUT = REPORT_ROOT / "phase3e-deterministic-2026-07-26"
RAW_ROOT = ROOT / "data" / "raw" / "feasibility-probes"
UNIVERSE = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
RELEASE_ROOT = ROOT / "data" / "releases"

CANDIDATES = [
    {
        "criterion_id": "C08",
        "definition": "data/research/phase3e/c08-hciplus.json",
        "run_id": "phase3e-2026-07-26-c08-online-v2",
        "superseded_runs": ["phase3e-2026-07-26-c08-online"],
        "phase3c_expected_valid": 88,
        "phase3c_expectation": (
            "89 countries with HLO/LAYS, of which 88 had a 2024+ label; BHS and BOL missing."
        ),
        "recommendation": "EXPERIMENTAL_CANDIDATE",
        "recommendation_rationale": (
            "Coverage passes, but ATG lacks the schooling component, GUY is stale, the published "
            "schooling component is not a 0-100 percentage, and the primary HLO/LAYS/component "
            "choice must be settled before production scoring."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_WITH_ATTRIBUTION",
    },
    {
        "criterion_id": "C11",
        "definition": "data/research/phase3e/c11-ilostat.json",
        "run_id": "phase3e-2026-07-26-c11-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 88,
        "phase3c_expectation": "88/91 current intersection; ATG, GRD and UKR previously absent.",
        "recommendation": "PRODUCTION_CANDIDATE",
        "recommendation_rationale": (
            "The exact three-component ILOSTAT source passes at 88/91 with deterministic mapping "
            "and favourable reuse. Production consideration requires an explicit missing/stale "
            "policy and scoring sensitivity review."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_WITH_ATTRIBUTION",
    },
    {
        "criterion_id": "C30",
        "definition": "data/research/phase3e/c30-world-bank.json",
        "run_id": "phase3e-2026-07-26-c30-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 91,
        "phase3c_expectation": "91/91 current WDI observations.",
        "recommendation": "PRODUCTION_CANDIDATE",
        "recommendation_rationale": (
            "The exact source is fresh, valid and complete for 91/91. Keep the construct label "
            "narrow and resolve whether immigrant share is scored higher-better or treated as "
            "preference/context."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_WITH_ATTRIBUTION",
    },
    {
        "criterion_id": "C29",
        "definition": "data/research/phase3e/c29-world-bank.json",
        "run_id": "phase3e-2026-07-26-c29-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 91,
        "phase3c_expectation": (
            "91/91 with at least three 2020-2024 observations in both components and a 2023+ latest year."
        ),
        "recommendation": "EXPERIMENTAL_CANDIDATE",
        "recommendation_rationale": (
            "Both exact time series pass for 91/91, but exchange-rate regime flags, currency "
            "breaks, log-return construction and component weighting remain criterion-level "
            "methodology decisions."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_WITH_ATTRIBUTION",
    },
    {
        "criterion_id": "C48",
        "definition": "data/research/phase3e/c48-wgi.json",
        "run_id": "phase3e-2026-07-26-c48-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 91,
        "phase3c_expectation": "91/91 for GOV_WGI_PV_EST in 2024.",
        "recommendation": "PRODUCTION_CANDIDATE",
        "recommendation_rationale": (
            "The published aggregate estimate is fresh and valid for 91/91. A production "
            "implementation must retain or separately capture WGI uncertainty and avoid treating "
            "small rank differences as precise."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_FOR_PUBLISHED_AGGREGATES",
    },
    {
        "criterion_id": "C49",
        "definition": "data/research/phase3e/c49-wgi.json",
        "run_id": "phase3e-2026-07-26-c49-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 91,
        "phase3c_expectation": "91/91 for GOV_WGI_RL_EST in 2024.",
        "recommendation": "PRODUCTION_CANDIDATE",
        "recommendation_rationale": (
            "The narrowed Rule of law source is fresh and valid for 91/91. Production consideration "
            "requires uncertainty handling and an overlap decision against other governance criteria."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_FOR_PUBLISHED_AGGREGATES",
    },
    {
        "criterion_id": "C53",
        "definition": "data/research/phase3e/c53-water-sanitation.json",
        "run_id": "phase3e-2026-07-26-c53-online",
        "superseded_runs": [],
        "phase3c_expected_valid": 86,
        "phase3c_expectation": (
            "86/91 had both basic-water and basic-sanitation observations from 2022-2024."
        ),
        "recommendation": "RESERVE_CANDIDATE",
        "recommendation_rationale": (
            "The exact pair reproduces 86 valid countries and passes the threshold, but basic "
            "service access is not water safety or continuity and is highly saturated across many "
            "likely destinations. Retain as a reserve/foundation indicator unless Phase 3F shows "
            "meaningful ranking discrimination."
        ),
        "licensing_conclusion": "PASS_CC_BY_4_0_WITH_WHO_UNICEF_ATTRIBUTION",
    },
]


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_json(path: Path, value) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _offline_replay(candidate: dict[str, object], online_path: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        replay_path, replay_summary = run_probe(
            load_definition(ROOT / str(candidate["definition"])),
            f"{candidate['run_id']}-offline-replay",
            mode="offline",
            output_root=temporary / "reports",
            raw_root=RAW_ROOT,
            universe_path=UNIVERSE,
            release_root=RELEASE_ROOT,
            artifact_manifest=online_path / "raw-artifacts.json",
        )
        country_results_match = (online_path / "country-results.jsonl").read_bytes() == (
            replay_path / "country-results.jsonl"
        ).read_bytes()
        online_summary = _read_json(online_path / "summary.json")
        normalized_online = {
            key: value for key, value in online_summary.items() if key not in {"run_id", "mode"}
        }
        normalized_replay = {
            key: value for key, value in replay_summary.items() if key not in {"run_id", "mode"}
        }
        return {
            "criterion_id": candidate["criterion_id"],
            "online_run_id": candidate["run_id"],
            "country_results_byte_match": country_results_match,
            "normalized_summary_match": normalized_online == normalized_replay,
            "raw_artifact_checksums_match": (
                online_summary["raw_artifact_checksums"] == replay_summary["raw_artifact_checksums"]
            ),
            "passed": (
                country_results_match
                and normalized_online == normalized_replay
                and online_summary["raw_artifact_checksums"]
                == replay_summary["raw_artifact_checksums"]
            ),
        }


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    active_before = (
        (RELEASE_ROOT / "active.json").read_bytes()
        if (RELEASE_ROOT / "active.json").exists()
        else None
    )
    results_by_criterion: dict[str, list[dict[str, object]]] = {}
    entries = []
    raw_inventory = []
    replay_results = []
    for candidate in CANDIDATES:
        online_path = REPORT_ROOT / str(candidate["run_id"])
        summary = _read_json(online_path / "summary.json")
        results = _read_jsonl(online_path / "country-results.jsonl")
        if len(results) != 91:
            raise ValueError(f"{candidate['criterion_id']} does not have 91 country outcomes.")
        results_by_criterion[str(candidate["criterion_id"])] = results
        nonvalid = [
            {
                "country_code": row["country_code"],
                "display_name": row["display_name"],
                "status": row["status"],
                "reason_codes": row["reason_codes"],
            }
            for row in results
            if row["status"] != "valid"
        ]
        artifacts = _read_json(online_path / "raw-artifacts.json")
        raw_inventory.extend(
            {
                "criterion_id": candidate["criterion_id"],
                "run_id": candidate["run_id"],
                **artifact,
            }
            for artifact in artifacts
        )
        replay = _offline_replay(candidate, online_path)
        replay_results.append(replay)
        entries.append(
            {
                **candidate,
                "definition": str(candidate["definition"]),
                "measured": {
                    key: summary[key]
                    for key in (
                        "denominator",
                        "found",
                        "fresh",
                        "parsed",
                        "validated",
                        "valid",
                        "missing",
                        "stale",
                        "parse_failed",
                        "invalid",
                        "rejected",
                        "unmapped",
                        "probe_threshold_passed",
                        "full_91_passed",
                    )
                },
                "phase3c_delta_valid": (
                    summary["valid"] - int(candidate["phase3c_expected_valid"])
                ),
                "nonvalid_country_outcomes": nonvalid,
                "raw_artifact_count": len(artifacts),
                "source_version": summary["source_version"],
                "dataset_version": summary["dataset_version"],
                "offline_replay_verified": replay["passed"],
            }
        )

    country_codes = [row["country_code"] for row in results_by_criterion["C08"]]
    result_index = {
        criterion_id: {row["country_code"]: row for row in rows}
        for criterion_id, rows in results_by_criterion.items()
    }
    matrix = []
    only_blockers: dict[str, list[str]] = {
        str(candidate["criterion_id"]): [] for candidate in CANDIDATES
    }
    for code in country_codes:
        statuses = {
            criterion_id: result_index[criterion_id][code]["status"]
            for criterion_id in result_index
        }
        failing = [criterion_id for criterion_id, status in statuses.items() if status != "valid"]
        if len(failing) == 1:
            only_blockers[failing[0]].append(code)
        matrix.append({"country_code": code, **statuses, "nonvalid_count": len(failing)})
    for entry in entries:
        entry["only_blocker_countries"] = only_blockers[str(entry["criterion_id"])]

    aggregate = {
        "schema_version": "phase3e-deterministic-aggregate-1.0",
        "phase_id": "3E",
        "batch_id": "PHASE3E_DETERMINISTIC_2026-07-26",
        "generated_at": "2026-07-26",
        "universe_id": "stable_supported_v1",
        "denominator": 91,
        "research_only": True,
        "production_release_modified": False,
        "superseded_diagnostic_runs": ["phase3e-2026-07-26-c08-online"],
        "recommendation_summary": {
            category: [
                entry["criterion_id"] for entry in entries if entry["recommendation"] == category
            ]
            for category in (
                "PRODUCTION_CANDIDATE",
                "EXPERIMENTAL_CANDIDATE",
                "RESERVE_CANDIDATE",
                "REJECT",
            )
        },
        "all_probe_thresholds_passed": all(
            entry["measured"]["probe_threshold_passed"] for entry in entries
        ),
        "all_offline_replays_passed": all(item["passed"] for item in replay_results),
        "candidates": entries,
    }
    _write_json(OUTPUT / "aggregate.json", aggregate)
    _write_json(OUTPUT / "raw-artifact-inventory.json", raw_inventory)
    _write_json(OUTPUT / "offline-replay-verification.json", replay_results)
    _write_json(OUTPUT / "country-status-matrix.json", matrix)

    with (OUTPUT / "aggregate.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "criterion_id",
            "run_id",
            "recommendation",
            "phase3c_expected_valid",
            "valid",
            "phase3c_delta_valid",
            "found",
            "fresh",
            "missing",
            "stale",
            "invalid",
            "unmapped",
            "probe_threshold_passed",
            "full_91_passed",
            "offline_replay_verified",
            "licensing_conclusion",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for entry in entries:
            writer.writerow({key: entry["measured"].get(key, entry.get(key)) for key in fields})
    with (OUTPUT / "country-status-matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["country_code", *result_index, "nonvalid_count"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(matrix)

    lines = [
        "# Konsider Phase 3E — deterministic measured probes",
        "",
        "> Research output only. No production scoring, imputation, release publication, or source substitution was performed.",
        "",
        "## Executive result",
        "",
        (
            f"All seven probes passed the Phase 3 coverage threshold of 82/91. "
            f"Offline replay passed for {sum(item['passed'] for item in replay_results)}/7."
        ),
        "",
        "| ID | Valid | Missing | Stale | Invalid | Phase 3C delta | Full 91 | Recommendation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for entry in entries:
        measured = entry["measured"]
        lines.append(
            f"| {entry['criterion_id']} | {measured['valid']}/91 | "
            f"{measured['missing']} | {measured['stale']} | {measured['invalid']} | "
            f"{entry['phase3c_delta_valid']:+d} | "
            f"{'PASS' if measured['full_91_passed'] else 'FAIL'} | "
            f"{entry['recommendation']} |"
        )
    lines.extend(
        [
            "",
            "## Aggregate recommendations",
            "",
            (
                "- **Production candidates:** "
                + ", ".join(aggregate["recommendation_summary"]["PRODUCTION_CANDIDATE"])
            ),
            (
                "- **Experimental candidates:** "
                + ", ".join(aggregate["recommendation_summary"]["EXPERIMENTAL_CANDIDATE"])
            ),
            (
                "- **Reserve candidates:** "
                + ", ".join(aggregate["recommendation_summary"]["RESERVE_CANDIDATE"])
            ),
            "- **Rejected:** none.",
            "",
            "## Evidence interpretation",
            "",
            (
                "- `valid` requires presence, parsing, the candidate-specific freshness rule, "
                "and all declared component checks."
            ),
            (
                "- `unmapped` counts source records outside the stable 91-country registry, "
                "including excluded countries/economies; it is not a count of missing stable countries."
            ),
            (
                "- Raw source bytes are retained in the ignored content-addressed repository. "
                "The inventory records exact checksums, URLs, HTTP metadata and versions."
            ),
            (
                "- The first C08 diagnostic run was discarded from committed artifacts after it "
                "incorrectly treated the published schooling component as a 0-100 percentage. "
                "The corrected v2 run removes that unsupported maximum and is the result used below."
            ),
            "",
        ]
    )
    for entry in entries:
        measured = entry["measured"]
        lines.extend(
            [
                f"## {entry['criterion_id']}",
                "",
                f"- **Run:** `{entry['run_id']}`",
                f"- **Phase 3C expectation:** {entry['phase3c_expectation']}",
                (
                    f"- **Measured:** {measured['valid']}/91 valid; "
                    f"{measured['missing']} missing; {measured['stale']} stale; "
                    f"{measured['invalid']} invalid; {measured['parse_failed']} parse-failed."
                ),
                (
                    f"- **Comparison:** valid-count delta versus Phase 3C "
                    f"{entry['phase3c_delta_valid']:+d}."
                ),
                f"- **Licence:** {entry['licensing_conclusion']}.",
                f"- **Recommendation:** **{entry['recommendation']}** — {entry['recommendation_rationale']}",
                (
                    "- **Non-valid countries:** "
                    + (
                        "; ".join(
                            f"{item['country_code']}={item['status']}"
                            f" ({', '.join(item['reason_codes'])})"
                            for item in entry["nonvalid_country_outcomes"]
                        )
                        or "none"
                    )
                ),
                (
                    "- **Only-blocker countries across this seven-probe batch:** "
                    + (", ".join(entry["only_blocker_countries"]) or "none")
                ),
                f"- **Offline replay:** {'PASS' if entry['offline_replay_verified'] else 'FAIL'}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Output inventory",
            "",
            "- `aggregate.json` and `aggregate.csv`: measured comparison and recommendations.",
            "- `country-status-matrix.json` and `.csv`: all seven statuses for each stable country.",
            "- `raw-artifact-inventory.json`: exact content-addressed inputs.",
            "- `offline-replay-verification.json`: replay checks for every candidate.",
            (
                "- Each candidate run directory contains `country-results.jsonl`, "
                "`summary.json`, `sources.json`, `raw-artifacts.json`, `report.md`, and a manifest."
            ),
            "",
        ]
    )
    write_text_lf(OUTPUT / "report.md", "\n".join(lines))

    payload_names = (
        "aggregate.json",
        "aggregate.csv",
        "country-status-matrix.json",
        "country-status-matrix.csv",
        "raw-artifact-inventory.json",
        "offline-replay-verification.json",
        "report.md",
    )
    _write_json(
        OUTPUT / "manifest.json",
        {
            "schema_version": "phase3e-deterministic-manifest-1.0",
            "batch_id": aggregate["batch_id"],
            "research_only": True,
            "files": {
                name: f"sha256:{hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest()}"
                for name in payload_names
            },
        },
    )
    active_after = (
        (RELEASE_ROOT / "active.json").read_bytes()
        if (RELEASE_ROOT / "active.json").exists()
        else None
    )
    if active_after != active_before:
        raise RuntimeError("Phase 3E aggregate build changed the active release pointer.")
    print(f"Wrote {OUTPUT}")
    print(
        json.dumps(
            {
                "all_thresholds_passed": aggregate["all_probe_thresholds_passed"],
                "all_replays_passed": aggregate["all_offline_replays_passed"],
                "recommendations": aggregate["recommendation_summary"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
