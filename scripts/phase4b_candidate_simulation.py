"""Generate deterministic Phase 4B candidate and robustness research artifacts.

This is a non-publishing research tool. It reads the active Phase 3 release and committed
feasibility-probe results, applies explicitly provisional transforms, and writes only to the
Phase 4B research-report directory.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import itertools
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "reports" / "phase4b-2026-07-27"
POLICY_VERSION = "uncertainty-aware-ranking-policy-1.0"
RESEARCH_SCHEMA_VERSION = "phase4b-candidate-simulation-1.0"
TOLERANCE = 1e-8
SCORE_MAX = 10.0
TOP_K_VALUES = (5, 10, 20)
CANDIDATE_IDS = ("C08", "C11", "C26", "C53")


@dataclass(frozen=True)
class CandidateInput:
    criterion_id: str
    name: str
    definition_path: Path
    results_path: Path
    replay_verified: bool
    recommendation_bucket: str
    recommendation_rationale: str
    license_gate: str
    semantic_gate: str


CANDIDATES = {
    "C08": CandidateInput(
        criterion_id="C08",
        name="School education quality",
        definition_path=ROOT / "data" / "research" / "phase3e" / "c08-hciplus.json",
        results_path=(
            ROOT
            / "data"
            / "reports"
            / "feasibility-probes"
            / "phase3e-2026-07-26-c08-online-v2"
            / "country-results.jsonl"
        ),
        replay_verified=True,
        recommendation_bucket="SECOND_WAVE",
        recommendation_rationale=(
            "High decision value and acceptable coverage, but the exact HLO/LAYS/published-"
            "component scoring construct must be frozen and remain experimental."
        ),
        license_gate="PASS_CC_BY_4_0",
        semantic_gate="EXPERIMENTAL_CONSTRUCT_REQUIRES_FREEZE",
    ),
    "C11": CandidateInput(
        criterion_id="C11",
        name="Overall job-market opportunity",
        definition_path=ROOT / "data" / "research" / "phase3e" / "c11-ilostat.json",
        results_path=(
            ROOT
            / "data"
            / "reports"
            / "feasibility-probes"
            / "phase3e-2026-07-26-c11-online"
            / "country-results.jsonl"
        ),
        replay_verified=True,
        recommendation_bucket="INITIAL",
        recommendation_rationale=(
            "Highest practical decision value, 88/91 coverage, deterministic replay, and clear "
            "CC BY 4.0 evidence; Phase 4F must freeze the composite and component weights."
        ),
        license_gate="PASS_CC_BY_4_0",
        semantic_gate="CONDITIONAL_PASS_REQUIRES_COMPOSITE_FREEZE",
    ),
    "C26": CandidateInput(
        criterion_id="C26",
        name="Financial protection from health costs",
        definition_path=ROOT / "data" / "research" / "phase3g0" / "c26-ghed.json",
        results_path=(
            ROOT
            / "data"
            / "reports"
            / "feasibility-probes"
            / "phase3g0-2026-07-26-c26-online"
            / "country-results.jsonl"
        ),
        replay_verified=True,
        recommendation_bucket="DEFERRED",
        recommendation_rationale=(
            "Excellent 90/91 coverage and useful national proxy, but committed evidence retains "
            "LIC_REDISTRIBUTION_REVIEW; production compatibility must be resolved before selection."
        ),
        license_gate="REVIEW_REQUIRED_LIC_REDISTRIBUTION_REVIEW",
        semantic_gate="CONDITIONAL_PASS_PROXY_LABEL_AND_METHOD_REQUIRED",
    ),
    "C53": CandidateInput(
        criterion_id="C53",
        name="Basic water and sanitation service access",
        definition_path=ROOT / "data" / "research" / "phase3e" / "c53-water-sanitation.json",
        results_path=(
            ROOT
            / "data"
            / "reports"
            / "feasibility-probes"
            / "phase3e-2026-07-26-c53-online"
            / "country-results.jsonl"
        ),
        replay_verified=True,
        recommendation_bucket="RESERVE",
        recommendation_rationale=(
            "Coverage passes, but the construct is saturated, weakly discriminating among likely "
            "destinations, and does not measure safety, continuity, or local utility reliability."
        ),
        license_gate="PASS_CC_BY_4_0",
        semantic_gate="RESERVE_WEAK_DISCRIMINATION_AND_NARROW_PROXY",
    ),
}


TRANSFORM_DEFINITIONS = [
    {
        "criterion_id": "C08",
        "transform_id": "C08_LAYS_PERCENTILE_PROVISIONAL_V1",
        "role": "BASE",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Average-rank percentile of learning-adjusted years of schooling, mapped to 1-10."
        ),
    },
    {
        "criterion_id": "C08",
        "transform_id": "C08_HLO_PERCENTILE_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": ("Average-rank percentile of harmonized learning outcome, mapped to 1-10."),
    },
    {
        "criterion_id": "C08",
        "transform_id": "C08_SCHOOLING_COMPONENT_PERCENTILE_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Average-rank percentile of the published HCI+ schooling component. The component is "
            "not interpreted as a percentage."
        ),
    },
    {
        "criterion_id": "C11",
        "transform_id": "C11_EQUAL_COMPONENT_PERCENTILES_PROVISIONAL_V1",
        "role": "BASE",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Equal mean of employment and participation percentiles plus reverse-unemployment "
            "percentile."
        ),
    },
    {
        "criterion_id": "C11",
        "transform_id": "C11_EMPLOYMENT_HEAVY_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Employment-heavy composite: 0.50 employment, 0.25 participation, and 0.25 reverse "
            "unemployment percentiles."
        ),
    },
    {
        "criterion_id": "C11",
        "transform_id": "C11_UNEMPLOYMENT_HEAVY_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Unemployment-heavy composite: 0.25 employment, 0.15 participation, and 0.60 reverse "
            "unemployment percentiles."
        ),
    },
    {
        "criterion_id": "C26",
        "transform_id": "C26_OOP_BROAD_BANDS_PROVISIONAL_V1",
        "role": "BASE",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "lower_is_better",
        "description": (
            "Fixed piecewise broad bands for OOP share: 0->10, 10->9, 20->8, 30->6.5, 40->5, "
            "50->3.5, 60->2, and 80->1."
        ),
    },
    {
        "criterion_id": "C26",
        "transform_id": "C26_OOP_REVERSE_PERCENTILE_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "lower_is_better",
        "description": "Reverse average-rank percentile of OOP share, mapped to 1-10.",
    },
    {
        "criterion_id": "C26",
        "transform_id": "C26_OOP_LINEAR_0_70_PROVISIONAL_V1",
        "role": "SENSITIVITY",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "lower_is_better",
        "description": "Fixed linear mapping from OOP share 0%=10 to 70%=1, clamped to 1-10.",
    },
    {
        "criterion_id": "C53",
        "transform_id": "C53_MINIMUM_BASIC_SERVICE_BANDS_PROVISIONAL_V1",
        "role": "BASE",
        "status": "PROVISIONAL_RESEARCH_ONLY",
        "direction": "higher_is_better",
        "description": (
            "Fixed piecewise bands applied to min(basic water %, basic sanitation %): "
            "70->1, 80->3, 90->5, 95->7, 99->9, 100->10."
        ),
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_gzip_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )
    path.write_bytes(gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def round_score(value: float) -> float:
    return round(float(value), 8)


def interpolate(value: float, points: list[tuple[float, float]]) -> float:
    ordered = sorted(points)
    if value <= ordered[0][0]:
        return ordered[0][1]
    if value >= ordered[-1][0]:
        return ordered[-1][1]
    for (x0, y0), (x1, y1) in zip(ordered, ordered[1:], strict=True):
        if x0 <= value <= x1:
            ratio = (value - x0) / (x1 - x0)
            return y0 + ratio * (y1 - y0)
    raise AssertionError("Interpolation interval was not found.")


def percentile_scores(values: dict[str, float], *, higher_is_better: bool) -> dict[str, float]:
    """Map values to average-rank percentiles with exact-value ties."""

    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    count = len(ordered)
    if count == 1:
        return {ordered[0][0]: 5.5}
    ranks: dict[str, float] = {}
    start = 0
    while start < count:
        end = start + 1
        while end < count and ordered[end][1] == ordered[start][1]:
            end += 1
        average_index = (start + end - 1) / 2
        percentile = average_index / (count - 1)
        if not higher_is_better:
            percentile = 1 - percentile
        score = round_score(1 + 9 * percentile)
        for index in range(start, end):
            ranks[ordered[index][0]] = score
        start = end
    return ranks


def build_transform_scores(
    results_by_candidate: dict[str, dict[str, dict[str, Any]]],
) -> tuple[dict[str, dict[str, dict[str, float]]], list[dict[str, Any]]]:
    scores: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)

    c08_valid = {
        code: row for code, row in results_by_candidate["C08"].items() if row["status"] == "valid"
    }
    c08_fields = {
        "C08_LAYS_PERCENTILE_PROVISIONAL_V1": "learning_adjusted_years_schooling",
        "C08_HLO_PERCENTILE_PROVISIONAL_V1": "harmonized_learning_outcome",
        "C08_SCHOOLING_COMPONENT_PERCENTILE_PROVISIONAL_V1": "hci_plus_schooling_component",
    }
    for transform_id, field in c08_fields.items():
        values = {code: float(row["values"][field]) for code, row in c08_valid.items()}
        scores["C08"][transform_id] = percentile_scores(values, higher_is_better=True)

    c11_valid = {
        code: row for code, row in results_by_candidate["C11"].items() if row["status"] == "valid"
    }
    employment = percentile_scores(
        {
            code: float(row["values"]["employment_to_population_ratio"])
            for code, row in c11_valid.items()
        },
        higher_is_better=True,
    )
    participation = percentile_scores(
        {
            code: float(row["values"]["labour_force_participation_rate"])
            for code, row in c11_valid.items()
        },
        higher_is_better=True,
    )
    reverse_unemployment = percentile_scores(
        {code: float(row["values"]["unemployment_rate"]) for code, row in c11_valid.items()},
        higher_is_better=False,
    )
    c11_weights = {
        "C11_EQUAL_COMPONENT_PERCENTILES_PROVISIONAL_V1": (1 / 3, 1 / 3, 1 / 3),
        "C11_EMPLOYMENT_HEAVY_PROVISIONAL_V1": (0.50, 0.25, 0.25),
        "C11_UNEMPLOYMENT_HEAVY_PROVISIONAL_V1": (0.25, 0.15, 0.60),
    }
    for transform_id, weights in c11_weights.items():
        scores["C11"][transform_id] = {
            code: round_score(
                weights[0] * employment[code]
                + weights[1] * participation[code]
                + weights[2] * reverse_unemployment[code]
            )
            for code in c11_valid
        }

    c26_valid = {
        code: row for code, row in results_by_candidate["C26"].items() if row["status"] == "valid"
    }
    c26_values = {
        code: float(row["values"]["out_of_pocket_share_of_current_health_expenditure"])
        for code, row in c26_valid.items()
    }
    scores["C26"]["C26_OOP_REVERSE_PERCENTILE_PROVISIONAL_V1"] = percentile_scores(
        c26_values, higher_is_better=False
    )
    scores["C26"]["C26_OOP_BROAD_BANDS_PROVISIONAL_V1"] = {
        code: round_score(
            interpolate(
                value,
                [
                    (0, 10),
                    (10, 9),
                    (20, 8),
                    (30, 6.5),
                    (40, 5),
                    (50, 3.5),
                    (60, 2),
                    (80, 1),
                ],
            )
        )
        for code, value in c26_values.items()
    }
    scores["C26"]["C26_OOP_LINEAR_0_70_PROVISIONAL_V1"] = {
        code: round_score(max(1.0, min(10.0, 10.0 - (value / 70.0) * 9.0)))
        for code, value in c26_values.items()
    }

    c53_valid = {
        code: row for code, row in results_by_candidate["C53"].items() if row["status"] == "valid"
    }
    scores["C53"]["C53_MINIMUM_BASIC_SERVICE_BANDS_PROVISIONAL_V1"] = {
        code: round_score(
            interpolate(
                min(
                    float(row["values"]["basic_drinking_water_access"]),
                    float(row["values"]["basic_sanitation_access"]),
                ),
                [(70, 1), (80, 3), (90, 5), (95, 7), (99, 9), (100, 10)],
            )
        )
        for code, row in c53_valid.items()
    }

    definitions = []
    for definition in TRANSFORM_DEFINITIONS:
        criterion_scores = scores[definition["criterion_id"]][definition["transform_id"]]
        definitions.append(
            {
                **definition,
                "valid_score_count": len(criterion_scores),
                "score_min": min(criterion_scores.values()),
                "score_max": max(criterion_scores.values()),
                "scores": dict(sorted(criterion_scores.items())),
            }
        )
    return dict(scores), definitions


def normalize_weights(raw_weights: dict[str, float]) -> dict[str, float]:
    positive = {key: float(value) for key, value in raw_weights.items() if value > 0}
    total = sum(positive.values())
    if total <= 0:
        raise ValueError("At least one positive weight is required.")
    return {key: value / total for key, value in sorted(positive.items())}


def weighted_total(scores: dict[str, float], normalized_weights: dict[str, float]) -> float:
    contributions = [
        round_score(scores[criterion_id] * weight)
        for criterion_id, weight in normalized_weights.items()
    ]
    return round_score(sum(contributions))


def rank_scores(scores: dict[str, float]) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def top_k_boundary(ranking: list[tuple[str, float]], top_k: int) -> tuple[float, list[str], int]:
    boundary = ranking[top_k - 1][1]
    members = [code for code, score in ranking if score >= boundary - TOLERANCE]
    return boundary, members, len(members) - top_k


def outcome_class(status: str) -> str:
    return {
        "missing": "PCC_OBSERVATION_MISSING",
        "stale": "PCC_OBSERVATION_STALE",
        "invalid": "PCC_OBSERVATION_INVALID",
        "rejected": "PCC_OBSERVATION_REJECTED",
        "parse_failed": "PCC_OBSERVATION_PARSE_FAILED",
        "mapping_failed": "PCC_OBSERVATION_MAPPING_FAILED",
    }.get(status, "PCC_OBSERVATION_OTHER_NON_READY")


def concentration_flag(region_rows: list[dict[str, Any]], excluded_count: int) -> tuple[str, str]:
    if excluded_count == 0:
        return "NO_VISIBLE_CONCENTRATION", "No countries are excluded."
    leading = max(
        region_rows,
        key=lambda row: (
            row["excluded_country_share"],
            row["overrepresentation_ratio"],
            row["region"],
        ),
    )
    if (
        excluded_count >= 3
        and leading["excluded_country_share"] >= 0.60
        and leading["overrepresentation_ratio"] >= 2.0
    ):
        flag = "STRONG_REGIONAL_CONCENTRATION"
    elif leading["overrepresentation_ratio"] >= 1.5:
        flag = "SOME_REGIONAL_CONCENTRATION"
    else:
        flag = "NO_VISIBLE_CONCENTRATION"
    evidence = (
        f"{leading['region']} contains {leading['excluded_count']} of {excluded_count} exclusions "
        f"({leading['excluded_country_share']:.1%}) versus "
        f"{leading['stable_catalog_share']:.1%} of the stable catalog; "
        f"overrepresentation ratio {leading['overrepresentation_ratio']:.2f}."
    )
    return flag, evidence


def build_regional_analysis(
    excluded_codes: list[str],
    countries: dict[str, dict[str, Any]],
    region_counts: Counter[str],
) -> dict[str, Any]:
    excluded_by_region = Counter(countries[code]["region"] for code in excluded_codes)
    rows = []
    excluded_count = len(excluded_codes)
    stable_count = len(countries)
    for region in sorted(region_counts):
        stable_region_count = region_counts[region]
        excluded_region_count = excluded_by_region[region]
        stable_share = stable_region_count / stable_count
        exclusion_share = excluded_region_count / excluded_count if excluded_count else 0.0
        rows.append(
            {
                "region": region,
                "stable_country_count": stable_region_count,
                "stable_catalog_share": round_score(stable_share),
                "excluded_count": excluded_region_count,
                "excluded_rate_within_region": round_score(
                    excluded_region_count / stable_region_count
                ),
                "excluded_country_share": round_score(exclusion_share),
                "overrepresentation_ratio": round_score(
                    exclusion_share / stable_share if stable_share else 0.0
                ),
            }
        )
    flag, evidence = concentration_flag(rows, excluded_count)
    return {
        "flag": flag,
        "evidence": evidence,
        "regions": rows,
    }


def build_candidate_matrix(
    definitions: dict[str, dict[str, Any]],
    results_by_candidate: dict[str, dict[str, dict[str, Any]]],
    countries: dict[str, dict[str, Any]],
    region_counts: Counter[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    machine_rows = []
    csv_rows = []
    for criterion_id in CANDIDATE_IDS:
        candidate = CANDIDATES[criterion_id]
        definition = definitions[criterion_id]
        outcomes = results_by_candidate[criterion_id]
        counts = Counter(row["status"] for row in outcomes.values())
        non_valid = []
        for code, row in sorted(outcomes.items()):
            if row["status"] == "valid":
                continue
            non_valid.append(
                {
                    "country_code": code,
                    "country_name": countries[code]["display_name"],
                    "region": countries[code]["region"],
                    "status": row["status"],
                    "outcome_code": outcome_class(row["status"]),
                    "reason_codes": row.get("reason_codes", []),
                    "reference_start": row.get("reference_start"),
                    "reference_end": row.get("reference_end"),
                }
            )
        regional = build_regional_analysis(
            [row["country_code"] for row in non_valid], countries, region_counts
        )
        source = definition["source"]
        blockers = list(definition.get("blocker_codes", []))
        row = {
            "criterion_id": criterion_id,
            "name": candidate.name,
            "recommendation_bucket": candidate.recommendation_bucket,
            "recommendation_rationale": candidate.recommendation_rationale,
            "decision_status": "USER_APPROVED",
            "valid_count": counts["valid"],
            "missing_count": counts["missing"],
            "stale_count": counts["stale"],
            "invalid_count": counts["invalid"],
            "rejected_count": counts["rejected"],
            "other_non_ready_count": (
                91
                - counts["valid"]
                - counts["missing"]
                - counts["stale"]
                - counts["invalid"]
                - counts["rejected"]
            ),
            "stable_country_count": 91,
            "coverage_percentage": round_score((counts["valid"] / 91) * 100),
            "coverage_gate": "PASS" if counts["valid"] >= 82 else "FAIL",
            "license_gate": candidate.license_gate,
            "semantic_scoring_gate": candidate.semantic_gate,
            "authority_gate": "PASS",
            "national_granularity_gate": "PASS_WITH_DOCUMENTED_CAVEAT",
            "deterministic_replay_gate": ("PASS" if candidate.replay_verified else "NOT_VERIFIED"),
            "source_candidate_id": source["source_candidate_id"],
            "publisher": source["publisher"],
            "dataset": source["dataset"],
            "dataset_version": source["dataset_version"],
            "source_version": source["source_version"],
            "parser_version": source["parser_version"],
            "licence_name": source["licence_name"],
            "licence_evidence": source["licence_evidence"],
            "freshness_min_year": definition["freshness_min_year"],
            "blocker_codes": blockers,
            "non_valid_countries": non_valid,
            "regional_bias": regional,
        }
        machine_rows.append(row)
        csv_rows.append(
            {
                "criterion_id": criterion_id,
                "name": candidate.name,
                "valid_count": counts["valid"],
                "missing_count": counts["missing"],
                "stale_count": counts["stale"],
                "invalid_count": counts["invalid"],
                "coverage_percentage": row["coverage_percentage"],
                "source_candidate_id": row["source_candidate_id"],
                "dataset_version": row["dataset_version"],
                "source_version": row["source_version"],
                "freshness_min_year": row["freshness_min_year"],
                "license_gate": row["license_gate"],
                "semantic_scoring_gate": row["semantic_scoring_gate"],
                "replay_gate": row["deterministic_replay_gate"],
                "regional_bias_flag": regional["flag"],
                "non_valid_country_codes": "|".join(item["country_code"] for item in non_valid),
                "blocker_codes": "|".join(blockers),
                "recommendation_bucket": row["recommendation_bucket"],
                "decision_status": row["decision_status"],
            }
        )
    return machine_rows, csv_rows


def all_candidate_combinations() -> list[tuple[str, ...]]:
    return [
        combination
        for size in range(1, len(CANDIDATE_IDS) + 1)
        for combination in itertools.combinations(CANDIDATE_IDS, size)
    ]


def build_combinations(
    results_by_candidate: dict[str, dict[str, dict[str, Any]]],
    countries: dict[str, dict[str, Any]],
    region_counts: Counter[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    machine_rows = []
    csv_rows = []
    for combination in all_candidate_combinations():
        excluded = sorted(
            {
                code
                for criterion_id in combination
                for code, row in results_by_candidate[criterion_id].items()
                if row["status"] != "valid"
            }
        )
        excluded_details = []
        for code in excluded:
            reasons = []
            for criterion_id in combination:
                row = results_by_candidate[criterion_id][code]
                if row["status"] != "valid":
                    reasons.append(
                        {
                            "criterion_id": criterion_id,
                            "status": row["status"],
                            "outcome_code": outcome_class(row["status"]),
                            "reason_codes": row.get("reason_codes", []),
                        }
                    )
            excluded_details.append(
                {
                    "country_code": code,
                    "country_name": countries[code]["display_name"],
                    "region": countries[code]["region"],
                    "non_ready_criteria": reasons,
                }
            )
        count = len(excluded)
        band = "PREFERRED" if count <= 5 else "ELEVATED" if count <= 9 else "BLOCKED"
        regional = build_regional_analysis(excluded, countries, region_counts)
        combination_id = "+".join(combination)
        row = {
            "combination_id": combination_id,
            "criterion_ids": list(combination),
            "candidate_count": len(combination),
            "excluded_country_count": count,
            "eligible_country_count": 91 - count,
            "coverage_band": band,
            "excluded_countries": excluded_details,
            "regional_bias": regional,
        }
        machine_rows.append(row)
        csv_rows.append(
            {
                "combination_id": combination_id,
                "candidate_count": len(combination),
                "excluded_country_count": count,
                "eligible_country_count": 91 - count,
                "coverage_band": band,
                "excluded_country_codes": "|".join(excluded),
                "regional_bias_flag": regional["flag"],
                "regional_bias_evidence": regional["evidence"],
            }
        )
    return machine_rows, csv_rows


def make_weight_cases() -> list[dict[str, Any]]:
    cases = [
        {
            "weight_case_id": "FCC_ONLY",
            "combination_id": "NONE",
            "requested_pcc_ids": [],
            "pcc_raw_weights": {},
            "case_type": "CONTROL_FCC_ONLY",
        }
    ]
    for criterion_id in CANDIDATE_IDS:
        cases.append(
            {
                "weight_case_id": f"{criterion_id}_LOW_0_4_IGNORED",
                "combination_id": criterion_id,
                "requested_pcc_ids": [criterion_id],
                "pcc_raw_weights": {criterion_id: 0.4},
                "case_type": "CONTROL_BELOW_THRESHOLD",
            }
        )
    for combination in all_candidate_combinations():
        combination_id = "+".join(combination)
        for raw_weight in (0.6, 0.8, 1.0):
            cases.append(
                {
                    "weight_case_id": (
                        f"{combination_id}_UNIFORM_{str(raw_weight).replace('.', '_')}"
                    ),
                    "combination_id": combination_id,
                    "requested_pcc_ids": list(combination),
                    "pcc_raw_weights": {criterion_id: raw_weight for criterion_id in combination},
                    "case_type": "ACTIVE_UNIFORM",
                }
            )
        if len(combination) > 1:
            for dominant in combination:
                cases.append(
                    {
                        "weight_case_id": f"{combination_id}_DOMINANT_{dominant}",
                        "combination_id": combination_id,
                        "requested_pcc_ids": list(combination),
                        "pcc_raw_weights": {
                            criterion_id: (1.0 if criterion_id == dominant else 0.6)
                            for criterion_id in combination
                        },
                        "case_type": "ACTIVE_ONE_DOMINANT",
                    }
                )
    return cases


def transform_combinations_for(
    active_pcc_ids: list[str],
    transform_scores: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, str]]:
    if not active_pcc_ids:
        return [{}]
    choices = [sorted(transform_scores[criterion_id]) for criterion_id in active_pcc_ids]
    return [
        dict(zip(active_pcc_ids, selected, strict=True)) for selected in itertools.product(*choices)
    ]


def simulate(
    countries: dict[str, dict[str, Any]],
    profiles: list[dict[str, Any]],
    fcc_scores: dict[str, dict[str, float]],
    results_by_candidate: dict[str, dict[str, dict[str, Any]]],
    transform_scores: dict[str, dict[str, dict[str, float]]],
    combination_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    combination_by_id = {row["combination_id"]: row for row in combination_rows}
    weight_cases = make_weight_cases()
    detailed_rows = []
    group_rows = []
    simulation_number = 0

    for profile in profiles:
        profile_id = profile["id"]
        fcc_raw_weights = {
            criterion_id: float(weight) for criterion_id, weight in profile["weights"].items()
        }
        baseline_weights = normalize_weights(fcc_raw_weights)
        baseline_totals = {
            code: weighted_total(fcc_scores[code], baseline_weights) for code in countries
        }
        baseline_ranking = rank_scores(baseline_totals)
        baseline_rank = {code: index for index, (code, _) in enumerate(baseline_ranking, start=1)}

        for weight_case in weight_cases:
            active_pcc_ids = sorted(
                criterion_id
                for criterion_id, weight in weight_case["pcc_raw_weights"].items()
                if weight >= 0.6
            )
            ignored_pcc_ids = sorted(
                criterion_id
                for criterion_id, weight in weight_case["pcc_raw_weights"].items()
                if weight < 0.6
            )
            if active_pcc_ids:
                combination = combination_by_id["+".join(active_pcc_ids)]
                excluded_codes = [row["country_code"] for row in combination["excluded_countries"]]
            else:
                combination = None
                excluded_codes = []
            eligible_codes = sorted(set(countries) - set(excluded_codes))
            raw_active_weights = {
                **fcc_raw_weights,
                **{
                    criterion_id: weight_case["pcc_raw_weights"][criterion_id]
                    for criterion_id in active_pcc_ids
                },
            }
            normalized_active_weights = normalize_weights(raw_active_weights)
            transform_combinations = transform_combinations_for(active_pcc_ids, transform_scores)

            for top_k in TOP_K_VALUES:
                r0_boundary, r0_top_codes, r0_tie_overflow = top_k_boundary(baseline_ranking, top_k)
                group_simulations = []

                for selected_transforms in transform_combinations:
                    simulation_number += 1
                    simulation_id = f"phase4b-sim-{simulation_number:05d}"
                    if not active_pcc_ids:
                        row = {
                            "schema_version": RESEARCH_SCHEMA_VERSION,
                            "simulation_id": simulation_id,
                            "profile_id": profile_id,
                            "weight_case_id": weight_case["weight_case_id"],
                            "case_type": weight_case["case_type"],
                            "requested_pcc_ids": weight_case["requested_pcc_ids"],
                            "active_pcc_ids": [],
                            "ignored_pcc_ids": ignored_pcc_ids,
                            "pcc_raw_weights": weight_case["pcc_raw_weights"],
                            "transform_ids": {},
                            "top_k": top_k,
                            "status": "NO_PARTIAL_CRITERIA_ACTIVE",
                            "stable_country_count": 91,
                            "eligible_country_count": 91,
                            "excluded_country_count": 0,
                            "coverage_band": "FULL_COVERAGE",
                            "r0_boundary_score": r0_boundary,
                            "r0_top_k_result_count": len(r0_top_codes),
                            "r0_boundary_tie_overflow": r0_tie_overflow,
                            "r1_boundary_score": None,
                            "r1_top_k_result_count": None,
                            "r1_boundary_tie_overflow": None,
                            "excluded_results": [],
                            "potential_entrant_codes": [],
                            "baseline_top_k_excluded_codes": [],
                        }
                        detailed_rows.append(row)
                        group_simulations.append(row)
                        continue

                    r1_totals = {}
                    for code in eligible_codes:
                        all_scores = dict(fcc_scores[code])
                        for criterion_id in active_pcc_ids:
                            transform_id = selected_transforms[criterion_id]
                            all_scores[criterion_id] = transform_scores[criterion_id][transform_id][
                                code
                            ]
                        r1_totals[code] = weighted_total(all_scores, normalized_active_weights)
                    r1_ranking = rank_scores(r1_totals)
                    r1_boundary, r1_top_codes, r1_tie_overflow = top_k_boundary(r1_ranking, top_k)

                    excluded_results = []
                    baseline_excluded_codes = []
                    potential_codes = []
                    for code in excluded_codes:
                        missing_criteria = []
                        upper_scores = dict(fcc_scores[code])
                        for criterion_id in active_pcc_ids:
                            source_row = results_by_candidate[criterion_id][code]
                            if source_row["status"] == "valid":
                                transform_id = selected_transforms[criterion_id]
                                upper_scores[criterion_id] = transform_scores[criterion_id][
                                    transform_id
                                ][code]
                            else:
                                upper_scores[criterion_id] = SCORE_MAX
                                missing_criteria.append(
                                    {
                                        "criterion_id": criterion_id,
                                        "status": source_row["status"],
                                        "outcome_code": outcome_class(source_row["status"]),
                                        "reason_codes": source_row.get("reason_codes", []),
                                    }
                                )
                        upper_bound = weighted_total(upper_scores, normalized_active_weights)
                        in_baseline_top_k = baseline_totals[code] >= r0_boundary - TOLERANCE
                        could_enter = upper_bound >= r1_boundary - TOLERANCE
                        if in_baseline_top_k:
                            baseline_excluded_codes.append(code)
                        if could_enter:
                            potential_codes.append(code)
                        excluded_results.append(
                            {
                                "country_code": code,
                                "r0_ordinal_rank": baseline_rank[code],
                                "r0_score": baseline_totals[code],
                                "in_score_bounded_r0_top_k": in_baseline_top_k,
                                "optimistic_upper_bound": upper_bound,
                                "could_enter_score_bounded_r1_top_k": could_enter,
                                "non_ready_active_pcc": missing_criteria,
                            }
                        )
                    if baseline_excluded_codes:
                        status = "BASELINE_TOP_K_EXCLUDED"
                    elif potential_codes:
                        status = "POTENTIALLY_AFFECTED"
                    else:
                        status = "ROBUST_TOP_K"

                    row = {
                        "schema_version": RESEARCH_SCHEMA_VERSION,
                        "simulation_id": simulation_id,
                        "profile_id": profile_id,
                        "weight_case_id": weight_case["weight_case_id"],
                        "case_type": weight_case["case_type"],
                        "requested_pcc_ids": weight_case["requested_pcc_ids"],
                        "active_pcc_ids": active_pcc_ids,
                        "ignored_pcc_ids": ignored_pcc_ids,
                        "pcc_raw_weights": weight_case["pcc_raw_weights"],
                        "transform_ids": selected_transforms,
                        "top_k": top_k,
                        "status": status,
                        "stable_country_count": 91,
                        "eligible_country_count": len(eligible_codes),
                        "excluded_country_count": len(excluded_codes),
                        "coverage_band": combination["coverage_band"],
                        "r0_boundary_score": r0_boundary,
                        "r0_top_k_result_count": len(r0_top_codes),
                        "r0_boundary_tie_overflow": r0_tie_overflow,
                        "r1_boundary_score": r1_boundary,
                        "r1_top_k_result_count": len(r1_top_codes),
                        "r1_boundary_tie_overflow": r1_tie_overflow,
                        "excluded_results": excluded_results,
                        "potential_entrant_codes": sorted(potential_codes),
                        "baseline_top_k_excluded_codes": sorted(baseline_excluded_codes),
                    }
                    detailed_rows.append(row)
                    group_simulations.append(row)

                statuses = Counter(row["status"] for row in group_simulations)
                if not active_pcc_ids:
                    classification = "NOT_APPLICABLE_NO_ACTIVE_PCC"
                else:
                    affected = [
                        row["status"] in {"POTENTIALLY_AFFECTED", "BASELINE_TOP_K_EXCLUDED"}
                        for row in group_simulations
                    ]
                    if all(not value for value in affected):
                        classification = "ROBUST_ACROSS_VARIANTS"
                    elif all(affected):
                        classification = "POTENTIALLY_AFFECTED_ACROSS_VARIANTS"
                    else:
                        classification = "TRANSFORM_SENSITIVE"
                r1_boundaries = [
                    row["r1_boundary_score"]
                    for row in group_simulations
                    if row["r1_boundary_score"] is not None
                ]
                group_rows.append(
                    {
                        "profile_id": profile_id,
                        "weight_case_id": weight_case["weight_case_id"],
                        "case_type": weight_case["case_type"],
                        "requested_pcc_ids": weight_case["requested_pcc_ids"],
                        "active_pcc_ids": active_pcc_ids,
                        "ignored_pcc_ids": ignored_pcc_ids,
                        "pcc_raw_weights": weight_case["pcc_raw_weights"],
                        "top_k": top_k,
                        "transform_variant_count": len(group_simulations),
                        "status_counts": dict(sorted(statuses.items())),
                        "variant_classification": classification,
                        "eligible_country_count": len(eligible_codes),
                        "excluded_country_count": len(excluded_codes),
                        "r0_boundary_score": r0_boundary,
                        "r1_boundary_score_min": (min(r1_boundaries) if r1_boundaries else None),
                        "r1_boundary_score_max": (max(r1_boundaries) if r1_boundaries else None),
                        "potential_entrant_union": sorted(
                            {
                                code
                                for row in group_simulations
                                for code in row["potential_entrant_codes"]
                            }
                        ),
                        "baseline_top_k_excluded_codes": sorted(
                            {
                                code
                                for row in group_simulations
                                for code in row["baseline_top_k_excluded_codes"]
                            }
                        ),
                    }
                )

    summary = {
        "schema_version": RESEARCH_SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "profile_count": len(profiles),
        "weight_case_count_per_profile": len(weight_cases),
        "active_weight_case_count_per_profile": sum(
            case["case_type"].startswith("ACTIVE") for case in weight_cases
        ),
        "control_weight_case_count_per_profile": sum(
            case["case_type"].startswith("CONTROL") for case in weight_cases
        ),
        "top_k_values": list(TOP_K_VALUES),
        "grouped_simulation_count": len(group_rows),
        "transform_expanded_simulation_count": len(detailed_rows),
        "variant_classification_counts": dict(
            sorted(Counter(row["variant_classification"] for row in group_rows).items())
        ),
        "status_counts": dict(sorted(Counter(row["status"] for row in detailed_rows).items())),
        "groups": group_rows,
    }
    return detailed_rows, summary


def build_manifest(input_paths: list[Path], output_paths: list[Path]) -> dict[str, Any]:
    return {
        "schema_version": RESEARCH_SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "generated_at": "2026-07-27",
        "generator": "scripts/phase4b_candidate_simulation.py",
        "classification": "NON_PUBLISHING_RESEARCH",
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in sorted(input_paths)
        },
        "outputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
            for path in sorted(output_paths)
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    catalog_path = ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json"
    active_path = ROOT / "data" / "releases" / "active.json"
    active_before = active_path.read_bytes()
    active = load_json(active_path)
    release_dir = ROOT / "data" / "releases" / active["release_id"]
    release_scores_path = release_dir / "scores.jsonl"
    catalog = load_json(catalog_path)
    countries = {row["code"]: row for row in catalog["countries"]}
    assert len(countries) == 91
    region_counts = Counter(row["region"] for row in countries.values())

    definitions = {
        criterion_id: load_json(candidate.definition_path)
        for criterion_id, candidate in CANDIDATES.items()
    }
    results_by_candidate = {
        criterion_id: {row["country_code"]: row for row in load_jsonl(candidate.results_path)}
        for criterion_id, candidate in CANDIDATES.items()
    }
    for criterion_id, rows in results_by_candidate.items():
        assert set(rows) == set(countries), f"{criterion_id} does not contain all 91 outcomes."

    release_scores = load_jsonl(release_scores_path)
    enabled_fcc_ids = {
        row["id"] for row in catalog["criteria"] if row["ready"] and row["default_enabled"]
    }
    assert len(enabled_fcc_ids) == 8
    fcc_scores: dict[str, dict[str, float]] = defaultdict(dict)
    for row in release_scores:
        if row["criterion_id"] in enabled_fcc_ids:
            fcc_scores[row["country_code"]][row["criterion_id"]] = float(row["score"])
    assert set(fcc_scores) == set(countries)
    assert all(set(scores) == enabled_fcc_ids for scores in fcc_scores.values())

    transform_scores, transform_definitions = build_transform_scores(results_by_candidate)
    for criterion_id in CANDIDATE_IDS:
        valid_codes = {
            code
            for code, row in results_by_candidate[criterion_id].items()
            if row["status"] == "valid"
        }
        assert all(set(scores) == valid_codes for scores in transform_scores[criterion_id].values())

    candidate_rows, candidate_csv_rows = build_candidate_matrix(
        definitions, results_by_candidate, countries, region_counts
    )
    combination_rows, combination_csv_rows = build_combinations(
        results_by_candidate, countries, region_counts
    )
    known_unions = {
        row["combination_id"]: row["excluded_country_count"] for row in combination_rows
    }
    assert known_unions["C11+C26"] == 3
    assert known_unions["C08+C26"] == 5
    assert known_unions["C08+C11+C26"] == 6
    assert known_unions["C08+C11+C26+C53"] == 9

    detailed_simulations, robustness_summary = simulate(
        countries,
        catalog["profiles"],
        dict(fcc_scores),
        results_by_candidate,
        transform_scores,
        combination_rows,
    )
    assert robustness_summary["weight_case_count_per_profile"] == 78
    assert robustness_summary["active_weight_case_count_per_profile"] == 73
    assert robustness_summary["control_weight_case_count_per_profile"] == 5
    assert robustness_summary["grouped_simulation_count"] == 936
    assert robustness_summary["transform_expanded_simulation_count"] == 8736

    recommendations = {
        "decision_status": "USER_APPROVED",
        "recommended_initial_pcc_ids": ["C11"],
        "recommended_second_wave_pcc_ids": ["C08"],
        "recommended_reserve_pcc_ids": ["C53"],
        "recommended_deferred_pcc_ids": ["C26"],
        "full_coverage_future_candidates_not_pcc": ["C29", "C66"],
    }
    summary = {
        "schema_version": RESEARCH_SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "active_release_id": active["release_id"],
        "stable_country_count": 91,
        "enabled_fcc_count": len(enabled_fcc_ids),
        "candidate_count": len(CANDIDATE_IDS),
        "candidate_combination_count": len(combination_rows),
        "preferred_combination_count": sum(
            row["coverage_band"] == "PREFERRED" for row in combination_rows
        ),
        "elevated_combination_count": sum(
            row["coverage_band"] == "ELEVATED" for row in combination_rows
        ),
        "blocked_combination_count": sum(
            row["coverage_band"] == "BLOCKED" for row in combination_rows
        ),
        "simulation_counts": {
            key: robustness_summary[key]
            for key in (
                "profile_count",
                "weight_case_count_per_profile",
                "active_weight_case_count_per_profile",
                "control_weight_case_count_per_profile",
                "grouped_simulation_count",
                "transform_expanded_simulation_count",
            )
        },
        "variant_classification_counts": robustness_summary["variant_classification_counts"],
        "status_counts": robustness_summary["status_counts"],
        **recommendations,
    }

    candidate_json_path = OUTPUT_DIR / "candidate-matrix.json"
    candidate_csv_path = OUTPUT_DIR / "candidate-matrix.csv"
    combination_json_path = OUTPUT_DIR / "combination-unions.json"
    combination_csv_path = OUTPUT_DIR / "combination-unions.csv"
    regional_json_path = OUTPUT_DIR / "regional-bias.json"
    transforms_json_path = OUTPUT_DIR / "provisional-transforms.json"
    simulations_jsonl_path = OUTPUT_DIR / "robustness-simulations.jsonl.gz"
    robustness_json_path = OUTPUT_DIR / "robustness-summary.json"
    summary_json_path = OUTPUT_DIR / "summary.json"

    write_json(
        candidate_json_path,
        {
            "schema_version": RESEARCH_SCHEMA_VERSION,
            "policy_version": POLICY_VERSION,
            "candidates": candidate_rows,
        },
    )
    write_csv(
        candidate_csv_path,
        candidate_csv_rows,
        [
            "criterion_id",
            "name",
            "valid_count",
            "missing_count",
            "stale_count",
            "invalid_count",
            "coverage_percentage",
            "source_candidate_id",
            "dataset_version",
            "source_version",
            "freshness_min_year",
            "license_gate",
            "semantic_scoring_gate",
            "replay_gate",
            "regional_bias_flag",
            "non_valid_country_codes",
            "blocker_codes",
            "recommendation_bucket",
            "decision_status",
        ],
    )
    write_json(
        combination_json_path,
        {
            "schema_version": RESEARCH_SCHEMA_VERSION,
            "policy_version": POLICY_VERSION,
            "combinations": combination_rows,
        },
    )
    write_csv(
        combination_csv_path,
        combination_csv_rows,
        [
            "combination_id",
            "candidate_count",
            "excluded_country_count",
            "eligible_country_count",
            "coverage_band",
            "excluded_country_codes",
            "regional_bias_flag",
            "regional_bias_evidence",
        ],
    )
    write_json(
        regional_json_path,
        {
            "schema_version": RESEARCH_SCHEMA_VERSION,
            "classification": "DESCRIPTIVE_RESEARCH_ONLY",
            "flag_method": {
                "NO_VISIBLE_CONCENTRATION": (
                    "No region has an overrepresentation ratio of at least 1.5."
                ),
                "SOME_REGIONAL_CONCENTRATION": (
                    "A region has an overrepresentation ratio of at least 1.5, but the strong "
                    "descriptive condition is not met."
                ),
                "STRONG_REGIONAL_CONCENTRATION": (
                    "At least three countries are excluded and one region has at least 60% of "
                    "exclusions with an overrepresentation ratio of at least 2.0."
                ),
                "policy_note": (
                    "These are descriptive Phase 4B labels, not automatic blocking thresholds."
                ),
            },
            "stable_region_counts": dict(sorted(region_counts.items())),
            "candidate_analysis": {
                row["criterion_id"]: row["regional_bias"] for row in candidate_rows
            },
            "combination_analysis": {
                row["combination_id"]: row["regional_bias"] for row in combination_rows
            },
        },
    )
    write_json(
        transforms_json_path,
        {
            "schema_version": RESEARCH_SCHEMA_VERSION,
            "classification": "PROVISIONAL_RESEARCH_ONLY",
            "production_approval": False,
            "coverage_invariant": (
                "Every variant uses exactly the countries marked valid by its Phase 3 probe."
            ),
            "optimistic_bound_rule": (
                "Score 10 for every non-ready active PCC observation; this is policy-driven and "
                "is not a provisional imputation."
            ),
            "transforms": transform_definitions,
        },
    )
    write_gzip_jsonl(simulations_jsonl_path, detailed_simulations)
    write_json(robustness_json_path, robustness_summary)
    write_json(summary_json_path, summary)

    output_paths = [
        candidate_json_path,
        candidate_csv_path,
        combination_json_path,
        combination_csv_path,
        regional_json_path,
        transforms_json_path,
        simulations_jsonl_path,
        robustness_json_path,
        summary_json_path,
    ]
    input_paths = [
        ROOT / "scripts" / "phase4b_candidate_simulation.py",
        catalog_path,
        active_path,
        release_scores_path,
        *[candidate.definition_path for candidate in CANDIDATES.values()],
        *[candidate.results_path for candidate in CANDIDATES.values()],
    ]
    manifest_path = OUTPUT_DIR / "manifest.json"
    write_json(manifest_path, build_manifest(input_paths, output_paths))

    assert active_path.read_bytes() == active_before, "The active release pointer changed."
    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "grouped_simulations": robustness_summary["grouped_simulation_count"],
                "transform_expanded_simulations": robustness_summary[
                    "transform_expanded_simulation_count"
                ],
                "variant_classifications": robustness_summary["variant_classification_counts"],
                "status_counts": robustness_summary["status_counts"],
                "recommendations": recommendations,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
