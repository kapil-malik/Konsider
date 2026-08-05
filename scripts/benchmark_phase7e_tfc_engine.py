"""Benchmark Phase 7E with 91 countries, three synthetic route TFCs, and one metric."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from konsider.domain.tfc_assessment import TfcAssessmentEngine, benchmark_tfc_assessment
from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.tfc_release import build_tfc_release_artifacts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / "tests" / "fixtures" / "phase7d" / "synthetic-capture.json"
DEFAULT_CONTEXTS = ROOT / "tests" / "fixtures" / "phase7e" / "golden-contexts.json"
ROUTE_TFC = "synthetic_skilled_route"
METRIC_TFC = "synthetic_housing_metric"


def _performance_capture(path: Path) -> dict:
    capture = json.loads(path.read_text(encoding="utf-8"))
    route_definition = copy.deepcopy(capture["catalog"]["definitions"][0])
    route_policy = copy.deepcopy(capture["policy_bundles"]["policies"][0])
    source_rules = [
        row
        for row in capture["rules"]
        if row["tfc_id"] == ROUTE_TFC and row["jurisdiction_id"] == "country:DEU"
    ]
    for suffix in ("family", "study"):
        tfc_id = f"synthetic_{suffix}_route"
        definition = copy.deepcopy(route_definition)
        definition.update(
            tfc_id=tfc_id,
            name=f"Fictional {suffix} route performance check",
            policy_id=f"{tfc_id}.v1",
            applicable_purposes=["EXPLORATION"],
        )
        capture["catalog"]["definitions"].append(definition)
        policy = copy.deepcopy(route_policy)
        policy.update(tfc_id=tfc_id, policy_id=f"{tfc_id}.v1")
        capture["policy_bundles"]["policies"].append(policy)
        rule_ids = []
        for index, source in enumerate(source_rules, start=1):
            rule = copy.deepcopy(source)
            rule.update(
                record_id=f"rule:{tfc_id}:deu:{index}:v1",
                tfc_id=tfc_id,
                route_id=f"FX.{suffix.upper()}_{index}",
                overrides_record_id=None,
            )
            capture["rules"].append(rule)
            rule_ids.append(rule["record_id"])
        capture["support_overrides"].append(
            {
                "tfc_id": tfc_id,
                "country_code": "DEU",
                "support_status": "SUPPORTED",
                "jurisdiction_ids": ["country:DEU"],
                "rule_record_ids": rule_ids,
                "reason_code": None,
            }
        )
    return capture


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    parser.add_argument("--contexts", type=Path, default=DEFAULT_CONTEXTS)
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()
    capture = _performance_capture(args.capture)
    context = json.loads(args.contexts.read_text(encoding="utf-8"))["metric_range"]
    artifacts = build_tfc_release_artifacts(capture)
    engine = TfcAssessmentEngine(
        artifacts,
        active_release_id="2026-08-04.1",
        tfc_release_id="synthetic-phase7e-performance-6.0",
    )
    payload = {
        "release_id": "2026-08-04.1",
        "rankings": [
            {
                "rank": index,
                "base_rank": index,
                "country_code": country_code,
                "affinity_score": 10.0 - index / 100,
            }
            for index, country_code in enumerate(COUNTRY_CODES, start=1)
        ],
        "assessments": {},
    }
    result = benchmark_tfc_assessment(
        engine,
        payload,
        context,
        [ROUTE_TFC, "synthetic_family_route", "synthetic_study_route", METRIC_TFC],
        iterations=args.iterations,
    )
    result["route_tfc_count"] = 3
    result["metric_tfc_count"] = 1
    result["synthetic_only"] = True
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
