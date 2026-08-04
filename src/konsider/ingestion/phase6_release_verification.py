"""Measure and record final Phase 6 active-release runtime verification."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path
from typing import Callable

from fastapi.testclient import TestClient

from konsider.api.app import create_app
from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseRepository
from konsider.text_io import write_text_lf

ROOT = Path(__file__).resolve().parents[3]
FINAL_RELEASE_ID = "2026-08-04.1"
DEFAULT_OUTPUT = ROOT / "data" / "reports" / "phase6i-2026-08-04" / "performance.json"


def _measure(call: Callable[[], object], repeats: int = 20) -> dict[str, float]:
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        call()
        samples.append((time.perf_counter() - started) * 1000)
    ordered = sorted(samples)
    return {
        "median_ms": round(statistics.median(samples), 3),
        "p95_ms": round(ordered[max(0, int(len(ordered) * 0.95) - 1)], 3),
        "maximum_ms": round(max(samples), 3),
    }


def verify(output: Path = DEFAULT_OUTPUT) -> dict:
    started = time.perf_counter()
    repository = CurrentReleaseRepository(ROOT / "data" / "releases")
    release = repository.load_active()
    load_ms = (time.perf_counter() - started) * 1000
    if release.manifest["release_id"] != FINAL_RELEASE_ID:
        raise RuntimeError("Phase 6 final release is not active.")

    with TestClient(create_app()) as client:
        requests = {
            "catalog": lambda: client.get("/api/v2/opportunity-filters"),
            "ranking_no_filter": lambda: client.post("/api/v2/rankings", json={"top_k": 10}),
            "ranking_one_filter": lambda: client.post(
                "/api/v2/rankings",
                json={
                    "top_k": 10,
                    "opportunity_filters": {
                        "mode": "ALL_REQUIRED",
                        "required_filter_ids": ["technology_software_opportunity"],
                    },
                },
            ),
            "ranking_multi_filter": lambda: client.post(
                "/api/v2/rankings",
                json={
                    "top_k": 10,
                    "opportunity_filters": {
                        "mode": "ALL_REQUIRED",
                        "required_filter_ids": [
                            "technology_software_opportunity",
                            "computer_science_ict_education_opportunity",
                        ],
                    },
                },
            ),
        }
        for request in requests.values():
            response = request()
            if response.status_code != 200:
                raise RuntimeError(f"Performance probe returned HTTP {response.status_code}.")
        timings = {name: _measure(request) for name, request in requests.items()}

    prior_release = repository.load(ROOT / "data" / "releases" / "2026-07-29.2")
    with TestClient(create_app(service=RecommendationService(prior_release))) as prior_client:
        prior_no_filter = _measure(
            lambda: prior_client.post("/api/v2/rankings", json={"top_k": 10})
        )
    no_filter_median_ratio = (
        timings["ranking_no_filter"]["median_ms"] / prior_no_filter["median_ms"]
    )

    thresholds = {
        "active_release_load_max_ms": 5000,
        "request_p95_max_ms": 2000,
        "no_filter_median_regression_ratio_max": 1.25,
    }
    passed = (
        load_ms <= thresholds["active_release_load_max_ms"]
        and all(result["p95_ms"] <= thresholds["request_p95_max_ms"] for result in timings.values())
        and no_filter_median_ratio <= thresholds["no_filter_median_regression_ratio_max"]
    )
    report = {
        "schema_version": "phase6i-performance-verification-1.0",
        "release_id": FINAL_RELEASE_ID,
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "transport": "FastAPI TestClient in-process",
        },
        "active_release_load_ms": round(load_ms, 3),
        "repeats_per_request": 20,
        "request_timings": timings,
        "prior_release_no_filter_timing": prior_no_filter,
        "no_filter_median_regression_ratio": round(no_filter_median_ratio, 4),
        "thresholds": thresholds,
        "passed": passed,
    }
    if not passed:
        raise RuntimeError(f"Phase 6 performance gate failed: {report}")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(output, json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = verify(args.output)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
