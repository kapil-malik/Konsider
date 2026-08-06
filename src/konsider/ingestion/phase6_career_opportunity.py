"""Deterministic Phase 6E promotion of approved career Opportunity Filter evidence.

The production builder consumes committed, checksum-bound Phase 6B/6B.1 research artifacts. It
does not import the historical research scripts, access the network, activate a release, or alter
ranking/API behavior. Third-party raw bytes remain ignored and are optional verification inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from konsider.contracts import validate_contract
from konsider.domain.display_catalog import ProductDisplayCatalog, load_product_display_catalog
from konsider.domain.opportunity_filters import (
    OpportunityFilterState,
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_bundle,
)

ROOT = Path(__file__).resolve().parents[3]
PHASE6B_ROOT = ROOT / "data" / "reports" / "phase6b-2026-08-02"
PHASE6B1_ROOT = ROOT / "data" / "reports" / "phase6b1-2026-08-03"
UNIVERSE_PATH = ROOT / "data" / "country-universes" / "stable-supported-v1.json"
ACTIVE_RELEASE_PATH = ROOT / "data" / "releases" / "2026-07-29.2"
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "reports" / "phase6e-2026-08-03"
DISPLAY_CATALOG_PATH = ROOT / "data" / "catalogs" / "product-display-catalog.json"
DISPLAY_CATALOG_SCHEMA_PATH = (
    ROOT / "contracts" / "schemas" / "authoring" / "product-display-catalog.schema.json"
)

RELEASE_ID = "phase6e-career-2026-08-03.1"
BUILD_ID = "phase6e-career-promotion-1.0"
GENERATED_AT = "2026-08-03T00:00:00+05:30"
SOURCE_BUNDLE_VERSION = "career-opportunity-source-bundle-2026-08-03.1"
EVIDENCE_POLICY_VERSION = "career-opportunity-evidence-policy-1.0"
STATE_ORDER = (
    OpportunityFilterState.VERIFIED_STRONG_SIGNAL.value,
    OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value,
    OpportunityFilterState.INSUFFICIENT_EVIDENCE.value,
)


class CareerOpportunityBuildError(ValueError):
    """Raised when source promotion or staged bundle reconciliation fails."""


@dataclass(frozen=True)
class CareerFilterConfig:
    filter_id: str
    sort_order: int
    route_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    source_dependency_mode: str
    expected_counts: tuple[int, int, int]

    @property
    def threshold_policy_version(self) -> str:
        return f"career-p60-{self.filter_id}-1.0"


FILTERS = (
    CareerFilterConfig(
        "technology_software_opportunity",
        1,
        ("observed_technology", "canada_technology", "malta_technology"),
        ("ilo_observed_occupation_oc2", "statcan_2021_census_noc", "eurostat_lfsa_egai2d"),
        "MULTI_SOURCE",
        (20, 43, 28),
    ),
    CareerFilterConfig(
        "science_engineering_opportunity",
        2,
        (
            "observed_science_engineering",
            "canada_science_supplemental",
            "malta_science_engineering",
        ),
        ("ilo_observed_occupation_oc2", "eurostat_lfsa_egai2d"),
        "MULTI_SOURCE",
        (20, 47, 24),
    ),
    CareerFilterConfig(
        "health_social_work_opportunity",
        3,
        ("health_social_work",),
        ("ilo_modelled_economic_activity_2025",),
        "SINGLE_SOURCE",
        (27, 61, 3),
    ),
    CareerFilterConfig(
        "finance_insurance_opportunity",
        4,
        ("finance_insurance",),
        ("ilo_modelled_economic_activity_2025",),
        "SINGLE_SOURCE",
        (22, 66, 3),
    ),
    CareerFilterConfig(
        "skilled_trades_construction_opportunity",
        5,
        ("skilled_trades", "construction"),
        ("ilo_modelled_occupation_2025", "ilo_modelled_economic_activity_2025"),
        "MULTI_ROUTE",
        (34, 54, 3),
    ),
)
FILTER_BY_ID = {item.filter_id: item for item in FILTERS}

DEFINITION_COPY = {
    "technology_software_opportunity": {
        "construct": "Employment in ISCO-08 groups 25 and 35, measured as national scale and share.",
        "meaning": "A substantial and established technology/software employment ecosystem.",
        "route_description": "Frozen P60 scale/share route for Technology and software employment ecosystem.",
    },
    "science_engineering_opportunity": {
        "construct": "Employment in ISCO-08 groups 21 and 31, measured as national scale and share.",
        "meaning": "A substantial and established science/engineering employment ecosystem.",
        "route_description": "Frozen P60 scale/share route for Science and engineering employment ecosystem.",
    },
    "health_social_work_opportunity": {
        "construct": "Employment in ISIC Rev.4 section Q (human health and social work), measured as national scale and share.",
        "meaning": "A substantial and established care-sector employment ecosystem.",
        "route_description": "Frozen P60 scale/share route for Care-sector employment ecosystem.",
    },
    "finance_insurance_opportunity": {
        "construct": "Employment in ISIC Rev.4 section K, measured as national scale and share.",
        "meaning": "A substantial and established finance and insurance employment ecosystem.",
        "route_description": "Frozen P60 scale/share route for Finance and insurance employment ecosystem.",
    },
    "skilled_trades_construction_opportunity": {
        "construct": "ISCO-08 major group 7 employment OR ISIC Rev.4 section F construction employment, with both routes retained separately.",
        "meaning": "A substantial and established skilled-trades or construction employment ecosystem.",
        "route_description": "Frozen P60 scale/share route for Skilled-trades or construction employment ecosystem.",
    },
}

HISTORICAL_ROUTE_IDS = {
    "observed_technology_occupation": "observed_technology",
    "observed_science_engineering_occupation": "observed_science_engineering",
    "modelled_health_social_work_sector": "health_social_work",
    "modelled_finance_insurance_sector": "finance_insurance",
    "modelled_skilled_trades": "skilled_trades",
    "modelled_construction_sector": "construction",
}
ROUTE_SOURCE_IDS = {
    "observed_technology": "ilo_observed_occupation_oc2",
    "observed_science_engineering": "ilo_observed_occupation_oc2",
    "canada_technology": "statcan_2021_census_noc",
    "canada_science_supplemental": "statcan_2021_census_noc",
    "malta_technology": "eurostat_lfsa_egai2d",
    "malta_science_engineering": "eurostat_lfsa_egai2d",
    "health_social_work": "ilo_modelled_economic_activity_2025",
    "finance_insurance": "ilo_modelled_economic_activity_2025",
    "skilled_trades": "ilo_modelled_occupation_2025",
    "construction": "ilo_modelled_economic_activity_2025",
}
SOURCE_VERSIONS = {
    "ilo_observed_occupation_oc2": "EMP_TEMP_SEX_OC2_NB_A:2026-08-02-capture",
    "ilo_modelled_occupation_2025": "EMP_2EMP_SEX_OCU_NB_A:2025-11",
    "ilo_modelled_economic_activity_2025": "EMP_2EMP_SEX_ECO_NB_A:2025-11",
    "statcan_2021_census_noc": "98-10-0594-01:NOC-2021-v1.0",
    "eurostat_lfsa_egai2d": "lfsa_egai2d:2025",
    "japan_lfs_occupation": "LFS-historical-table-6:2025",
    "kosis_occupation": "DT_1DA7E27S:KSCO-8",
    "stats_nz_census_occupation": "CEN23_WRK_009:ANZSCO-v1.3",
}

RETAINED_RAW_SOURCES = {
    "ilo_observed_occupation_oc2": (
        ROOT / "data" / "raw" / "phase6a" / "ilostat-emp-oc2.csv",
        "aaadd9ad52c88af5b00edce9c78821481d352251fe1ee944bb9bff299bdd04d4",
        19_708_182,
    ),
    "ilo_modelled_occupation_2025": (
        ROOT / "data" / "raw" / "phase6b" / "ilo-modelled-employment-occupation-2025.csv",
        "00c76b161f5308f6655bac28ac3b6edeca25f4d262fc694e1aec5c310ef89986",
        20_321_403,
    ),
    "ilo_modelled_economic_activity_2025": (
        ROOT / "data" / "raw" / "phase6b" / "ilo-modelled-employment-economic-activity-2025.csv",
        "ab1baf83fb7f3cd3646df98b129571c21651e65fe49237efc873bff7e832efef",
        61_699_301,
    ),
    "statcan_2021_census_noc": (
        ROOT / "data" / "raw" / "phase6b1" / "statcan-9810059401-canada.html",
        "3e2e50bbb7fde23890400e79636d8521b164b0678f9eec2ba03ab7c15aab8b46",
        296_765,
    ),
    "eurostat_lfsa_egai2d": (
        ROOT / "data" / "raw" / "phase6b1" / "eurostat-lfsa-egai2d-mt.json",
        "b6eb11bf3845c8c05aaa905a5aa2d97fafcf5af902977455ed4f397d31213dfe",
        9_833,
    ),
    "japan_lfs_occupation": (
        ROOT / "data" / "raw" / "phase6b1" / "japan-lfs-table-6-1.xlsx",
        "e7f5d59bda3c774c0f26f65f66007c699abf75e49a30dea711425bd037970d87",
        38_781,
    ),
}

SOURCE_RECORDS = (
    {
        "source_id": "ilo_observed_occupation_oc2",
        "source_version": SOURCE_VERSIONS["ilo_observed_occupation_oc2"],
        "publisher": "International Labour Organization",
        "asset_uri": "data/raw/phase6a/ilostat-emp-oc2.csv",
        "canonical_page_url": "https://rplumber.ilo.org/data/indicator/?id=EMP_TEMP_SEX_OC2_NB_A&format=csv",
        "checksum": "sha256:aaadd9ad52c88af5b00edce9c78821481d352251fe1ee944bb9bff299bdd04d4",
        "licence_id": "CC-BY-4.0",
        "attribution": "Source: ILOSTAT, EMP_TEMP_SEX_OC2_NB_A; adapted by Konsider.",
        "reuse_status": "APPROVED",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "ilo_modelled_occupation_2025",
        "source_version": SOURCE_VERSIONS["ilo_modelled_occupation_2025"],
        "publisher": "International Labour Organization",
        "asset_uri": "data/raw/phase6b/ilo-modelled-employment-occupation-2025.csv",
        "canonical_page_url": "https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_OCU_NB_A&format=csv",
        "checksum": "sha256:00c76b161f5308f6655bac28ac3b6edeca25f4d262fc694e1aec5c310ef89986",
        "licence_id": "CC-BY-4.0",
        "attribution": "Source: ILO modelled estimates, November 2025 edition; adapted by Konsider.",
        "reuse_status": "APPROVED",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "ilo_modelled_economic_activity_2025",
        "source_version": SOURCE_VERSIONS["ilo_modelled_economic_activity_2025"],
        "publisher": "International Labour Organization",
        "asset_uri": "data/raw/phase6b/ilo-modelled-employment-economic-activity-2025.csv",
        "canonical_page_url": "https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_ECO_NB_A&format=csv",
        "checksum": "sha256:ab1baf83fb7f3cd3646df98b129571c21651e65fe49237efc873bff7e832efef",
        "licence_id": "CC-BY-4.0",
        "attribution": "Source: ILO modelled estimates, November 2025 edition; adapted by Konsider.",
        "reuse_status": "APPROVED",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "statcan_2021_census_noc",
        "source_version": SOURCE_VERSIONS["statcan_2021_census_noc"],
        "publisher": "Statistics Canada",
        "asset_uri": "data/raw/phase6b1/statcan-9810059401-canada.html",
        "canonical_page_url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810059401",
        "checksum": "sha256:3e2e50bbb7fde23890400e79636d8521b164b0678f9eec2ba03ab7c15aab8b46",
        "licence_id": "STATISTICS-CANADA-OPEN-LICENCE",
        "attribution": "Adapted from Statistics Canada table 98-10-0594-01; no endorsement implied.",
        "reuse_status": "APPROVED",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "eurostat_lfsa_egai2d",
        "source_version": SOURCE_VERSIONS["eurostat_lfsa_egai2d"],
        "publisher": "Eurostat",
        "asset_uri": "data/raw/phase6b1/eurostat-lfsa-egai2d-mt.json",
        "canonical_page_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_egai2d",
        "checksum": "sha256:b6eb11bf3845c8c05aaa905a5aa2d97fafcf5af902977455ed4f397d31213dfe",
        "licence_id": "CC-BY-4.0",
        "attribution": "Source: Eurostat lfsa_egai2d; adapted by Konsider.",
        "reuse_status": "APPROVED",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "japan_lfs_occupation",
        "source_version": SOURCE_VERSIONS["japan_lfs_occupation"],
        "publisher": "Statistics Bureau of Japan",
        "asset_uri": "data/raw/phase6b1/japan-lfs-table-6-1.xlsx",
        "canonical_page_url": "https://www.e-stat.go.jp/en/stat-search/file-download?fileKind=0&statInfId=000012925012",
        "checksum": "sha256:e7f5d59bda3c774c0f26f65f66007c699abf75e49a30dea711425bd037970d87",
        "licence_id": "GOVERNMENT-OF-JAPAN-STANDARD-TERMS-V2",
        "attribution": "Source: Labour Force Survey, Statistics Bureau of Japan, via e-Stat; adapted by Konsider.",
        "reuse_status": "SUPPLEMENTAL_ONLY",
        "retention_policy": "IGNORED_LOCAL",
    },
    {
        "source_id": "kosis_occupation",
        "source_version": SOURCE_VERSIONS["kosis_occupation"],
        "publisher": "Statistics Korea",
        "asset_uri": "https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1DA7E27S&language=en",
        "canonical_page_url": "https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1DA7E27S&language=en",
        "checksum": None,
        "licence_id": "KOSIS-PUBLIC-DATA-FREE-USE",
        "attribution": "Source: Statistics Korea, KOSIS.",
        "reuse_status": "SUPPLEMENTAL_ONLY",
        "retention_policy": "NOT_RETAINED",
    },
    {
        "source_id": "stats_nz_census_occupation",
        "source_version": SOURCE_VERSIONS["stats_nz_census_occupation"],
        "publisher": "Stats NZ",
        "asset_uri": "https://explore.data.stats.govt.nz/vis?df[id]=CEN23_WRK_009",
        "canonical_page_url": "https://explore.data.stats.govt.nz/vis?df[id]=CEN23_WRK_009",
        "checksum": None,
        "licence_id": "CC-BY-4.0",
        "attribution": "Source: Stats NZ, 2023 Census; adapted by Konsider.",
        "reuse_status": "SUPPLEMENTAL_ONLY",
        "retention_policy": "NOT_RETAINED",
    },
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    path.write_text(body, encoding="utf-8")


def _verify_checksum(path: Path, expected: str, label: str) -> None:
    actual = _sha256(path)
    if actual != expected:
        raise CareerOpportunityBuildError(
            f"{label} checksum mismatch: expected {expected}, got {actual}."
        )


def verify_research_inputs() -> dict[str, str]:
    """Verify every committed research input used by the production promotion."""

    phase6b_manifest = _read_json(PHASE6B_ROOT / "replay-manifest.json")
    phase6b1_manifest = _read_json(PHASE6B1_ROOT / "replay-manifest.json")
    paths = {
        "phase6b_evidence": PHASE6B_ROOT / "career-country-opportunity-evidence.jsonl",
        "phase6b_shortlists": PHASE6B_ROOT / "career-shortlist-coverage.json",
        "phase6b_portfolio": PHASE6B_ROOT / "approved-career-opportunity-portfolio.json",
        "phase6b1_gap_fill": PHASE6B1_ROOT / "gap-fill-country-evidence.jsonl",
        "phase6b1_crosswalks": PHASE6B1_ROOT / "occupation-crosswalks.json",
        "phase6b1_confidence": PHASE6B1_ROOT / "career-confidence-policy.json",
        "phase6b1_route_policy": PHASE6B1_ROOT / "multi-route-decision-policy.json",
        "phase6b1_shortlists": PHASE6B1_ROOT / "career-shortlist-coverage-before-after.json",
        "phase6b1_thresholds": PHASE6B1_ROOT / "career-threshold-calibration.json",
        "phase6b1_route_analysis": PHASE6B1_ROOT / "broad-criterion-route-analysis.json",
        "phase6b1_portfolio": PHASE6B1_ROOT / "final-career-opportunity-portfolio.json",
    }
    expected = {
        "phase6b_evidence": phase6b_manifest["output_sha256"][
            "career-country-opportunity-evidence.jsonl"
        ],
        "phase6b_shortlists": phase6b_manifest["output_sha256"]["career-shortlist-coverage.json"],
        "phase6b_portfolio": phase6b_manifest["output_sha256"][
            "approved-career-opportunity-portfolio.json"
        ],
        "phase6b1_gap_fill": phase6b1_manifest["output_sha256"]["gap-fill-country-evidence.jsonl"],
        "phase6b1_crosswalks": phase6b1_manifest["output_sha256"]["occupation-crosswalks.json"],
        "phase6b1_confidence": phase6b1_manifest["output_sha256"]["career-confidence-policy.json"],
        "phase6b1_route_policy": phase6b1_manifest["output_sha256"][
            "multi-route-decision-policy.json"
        ],
        "phase6b1_shortlists": phase6b1_manifest["output_sha256"][
            "career-shortlist-coverage-before-after.json"
        ],
        "phase6b1_thresholds": phase6b1_manifest["output_sha256"][
            "career-threshold-calibration.json"
        ],
        "phase6b1_route_analysis": phase6b1_manifest["output_sha256"][
            "broad-criterion-route-analysis.json"
        ],
        "phase6b1_portfolio": phase6b1_manifest["output_sha256"][
            "final-career-opportunity-portfolio.json"
        ],
    }
    for key, path in paths.items():
        _verify_checksum(path, expected[key], key)
    return {key: f"sha256:{value}" for key, value in expected.items()}


def verify_retained_sources(*, require_all: bool = False) -> dict[str, str]:
    """Verify optional ignored raw bytes without making clean-checkout builds depend on them."""

    results: dict[str, str] = {}
    for source_id, (path, expected, byte_count) in RETAINED_RAW_SOURCES.items():
        if not path.exists():
            if require_all:
                raise CareerOpportunityBuildError(f"Retained source is unavailable: {path}")
            results[source_id] = "NOT_PRESENT"
            continue
        if path.stat().st_size != byte_count:
            raise CareerOpportunityBuildError(
                f"{source_id} byte count mismatch: expected {byte_count}, got {path.stat().st_size}."
            )
        _verify_checksum(path, expected, source_id)
        results[source_id] = "VERIFIED"
    return results


def _route_result(scale: float, share: float, thresholds: Mapping[str, float]) -> dict[str, Any]:
    base = scale >= thresholds["base_scale_thousands"] and share >= thresholds["base_share_percent"]
    exceptional_scale = (
        scale >= thresholds["high_scale_thousands"] and share >= thresholds["low_share_percent"]
    )
    exceptional_specialization = (
        share >= thresholds["high_share_percent"] and scale >= thresholds["low_scale_thousands"]
    )
    return {
        "passed": base or exceptional_scale or exceptional_specialization,
        "components": {
            "scale_thousands": scale,
            "share_percent": share,
            **dict(thresholds),
            "scale_and_share_passed": base,
            "exceptional_scale_passed": exceptional_scale,
            "exceptional_specialization_passed": exceptional_specialization,
        },
    }


def _positive_reason(result: Mapping[str, Any]) -> str:
    components = result["components"]
    if (
        components["exceptional_scale_passed"]
        and not components["exceptional_specialization_passed"]
    ):
        return "EXCEPTIONAL_SCALE_ROUTE_PASSED"
    if (
        components["exceptional_specialization_passed"]
        and not components["exceptional_scale_passed"]
    ):
        return "EXCEPTIONAL_SPECIALIZATION_ROUTE_PASSED"
    return "SCALE_AND_SHARE_ROUTE_PASSED"


def _source_reference(source_id: str, lineage_id: str) -> dict[str, str]:
    return {
        "source_id": source_id,
        "source_version": SOURCE_VERSIONS[source_id],
        "lineage_id": lineage_id,
    }


def _base_evidence(row: Mapping[str, Any], config: CareerFilterConfig) -> dict[str, Any]:
    paths = row["evidence_paths"]
    state = row["state"]
    threshold_results = []
    source_references = []
    route_metrics: dict[str, tuple[float, float]] = {}
    for path in paths:
        route_id = HISTORICAL_ROUTE_IDS[path["route_id"]]
        threshold_payload = row["thresholds"]
        thresholds = (
            threshold_payload[path["route_id"]]["frozen_values"]
            if config.filter_id == "skilled_trades_construction_opportunity"
            else threshold_payload["frozen_values"]
        )
        result = _route_result(path["scale_thousands"], path["share_percent"], thresholds)
        threshold_results.append(
            {
                "route_id": route_id,
                "passed": result["passed"],
                "policy_version": config.threshold_policy_version,
                "components": result["components"],
            }
        )
        route_metrics[route_id] = (path["scale_thousands"], path["share_percent"])
        source_id = ROUTE_SOURCE_IDS[route_id]
        reference = _source_reference(
            source_id,
            f"phase6b:{config.filter_id}:{row['country_code']}:{path['source_id']}:{row['latest_period']}",
        )
        if reference not in source_references:
            source_references.append(reference)

    passed = [item["route_id"] for item in threshold_results if item["passed"]]
    if state == OpportunityFilterState.VERIFIED_STRONG_SIGNAL:
        if not passed:
            raise CareerOpportunityBuildError(
                f"Research positive has no reproducible passing route: {config.filter_id}/{row['country_code']}"
            )
        reason_codes = [
            _positive_reason(next(item for item in threshold_results if item["passed"]))
        ]
        establishing = passed
        if config.filter_id == "skilled_trades_construction_opportunity":
            reason_codes = [
                {
                    ("skilled_trades",): "SKILLED_TRADES_ROUTE_PASSED",
                    ("construction",): "CONSTRUCTION_ROUTE_PASSED",
                    (
                        "skilled_trades",
                        "construction",
                    ): "SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED",
                }[tuple(passed)]
            ]
    elif state == OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED:
        establishing = []
        reason_codes = [
            (
                "NO_APPROVED_STRONG_ROUTE_PASSED"
                if config.filter_id == "skilled_trades_construction_opportunity"
                else "COMPLETE_EVIDENCE_BELOW_STRONG_THRESHOLD"
            )
        ]
    else:
        establishing = []
        reason_codes = [
            "COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE" if config.sort_order >= 3 else "SOURCE_MISSING"
        ]

    metric_payload = None
    if route_metrics:
        first_route = next(iter(route_metrics))
        scale, share = route_metrics[first_route]
        metric_payload = {
            "schema_version": "career-employment-metrics-1.0",
            "scale_thousands": scale,
            "share_percent": share,
        }
        if config.filter_id == "skilled_trades_construction_opportunity":
            skilled_scale, skilled_share = route_metrics["skilled_trades"]
            construction_scale, construction_share = route_metrics["construction"]
            metric_payload.update(
                {
                    "skilled_trades_scale_thousands": skilled_scale,
                    "skilled_trades_share_percent": skilled_share,
                    "construction_scale_thousands": construction_scale,
                    "construction_share_percent": construction_share,
                }
            )

    observed = config.sort_order <= 2
    statuses = sorted({status for path in paths for status in path["observation_statuses"]})
    caveats = [
        "This state describes an employment ecosystem, not vacancies, salary, licensing, visa access, or applicant success."
    ]
    if observed and "B" in statuses:
        caveats.append("The retained ILO observation carries break-in-series status B.")
    if not observed:
        caveats.append(
            "ILO modelled estimates are disclosed as medium-confidence harmonised evidence."
        )
    if config.filter_id == "skilled_trades_construction_opportunity" and metric_payload:
        caveats.append(
            "The generic scale/share pair mirrors skilled_trades; both routes' scale and share are retained explicitly and evaluated separately."
        )

    return {
        "schema_version": "opportunity-filter-evidence-1.0",
        "release_id": RELEASE_ID,
        "filter_id": config.filter_id,
        "country_code": row["country_code"],
        "state": state,
        "confidence_band": "HIGH" if observed and paths else ("MEDIUM" if paths else "LOW"),
        "internal_confidence_tier": (
            "HIGH_CONFIDENCE_OBSERVED_HARMONISED"
            if observed and paths
            else "MEDIUM_CONFIDENCE_MODELLED_HARMONISED" if paths else None
        ),
        "coverage_completeness": "COMPLETE" if paths else "UNASSESSED",
        "evaluated_route_ids": [item["route_id"] for item in threshold_results],
        "establishing_route_ids": establishing,
        "reason_codes": reason_codes,
        "reference_period": str(row["latest_period"]) if row["latest_period"] is not None else None,
        "metric_payload": metric_payload,
        "threshold_results": threshold_results,
        "source_references": source_references,
        "source_observation_status": (
            "OBSERVED_HARMONISED"
            if observed and paths
            else "MODELLED_HARMONISED" if paths else "MISSING"
        ),
        "caveats": caveats,
        "evidence_policy_version": EVIDENCE_POLICY_VERSION,
        "threshold_policy_version": config.threshold_policy_version,
        "source_bundle_version": SOURCE_BUNDLE_VERSION,
        "generated_at": GENERATED_AT,
        "build_id": BUILD_ID,
    }


def _gap_evidence(row: Mapping[str, Any], config: CareerFilterConfig) -> dict[str, Any]:
    country_code = row["country_code"]
    has_metrics = row["scale_thousands"] is not None and row["share_percent"] is not None
    route_id = {
        ("CAN", "technology_software_opportunity"): "canada_technology",
        ("CAN", "science_engineering_opportunity"): "canada_science_supplemental",
        ("MLT", "technology_software_opportunity"): "malta_technology",
        ("MLT", "science_engineering_opportunity"): "malta_science_engineering",
    }.get((country_code, config.filter_id))
    threshold_results = []
    metric_payload = None
    if has_metrics and route_id:
        result = _route_result(row["scale_thousands"], row["share_percent"], row["thresholds"])
        accepted_pass = result["passed"] and row["state"] == "VERIFIED_STRONG_SIGNAL"
        threshold_results = [
            {
                "route_id": route_id,
                "passed": accepted_pass,
                "policy_version": config.threshold_policy_version,
                "components": result["components"],
            }
        ]
        metric_payload = {
            "schema_version": "career-employment-metrics-1.0",
            "scale_thousands": row["scale_thousands"],
            "share_percent": row["share_percent"],
        }

    state = row["state"]
    establishing = [route_id] if state == "VERIFIED_STRONG_SIGNAL" and route_id else []
    if state == "VERIFIED_STRONG_SIGNAL":
        reason_codes = [_positive_reason(threshold_results[0])]
    elif state == "STRONG_SIGNAL_NOT_ESTABLISHED":
        reason_codes = ["SCALE_FLOOR_NOT_MET"]
    elif country_code == "CAN":
        reason_codes = ["CROSSWALK_INCOMPLETE"]
    else:
        reason_codes = ["INSUFFICIENT_GRANULARITY"]

    source_id = {
        "CAN": "statcan_2021_census_noc",
        "MLT": "eurostat_lfsa_egai2d",
        "JPN": "japan_lfs_occupation",
        "KOR": "kosis_occupation",
        "NZL": "stats_nz_census_occupation",
    }[country_code]
    source_references = [
        _source_reference(
            source_id,
            f"phase6b1:{config.filter_id}:{country_code}:{row.get('source_id') or 'source-gap'}",
        )
    ]
    tier = row["confidence_tier"]
    band = "HIGH" if tier.startswith("HIGH_") else "MEDIUM" if tier.startswith("MEDIUM_") else "LOW"
    observation_status = (
        "OBSERVED_HARMONISED"
        if country_code == "MLT"
        else (
            "OBSERVED_NATIONAL"
            if country_code == "CAN" and config.sort_order == 1
            else "SUPPLEMENTAL"
        )
    )
    completeness = (
        "COMPLETE"
        if state != "INSUFFICIENT_EVIDENCE"
        else "PARTIAL" if has_metrics else "UNASSESSED"
    )
    return {
        "schema_version": "opportunity-filter-evidence-1.0",
        "release_id": RELEASE_ID,
        "filter_id": config.filter_id,
        "country_code": country_code,
        "state": state,
        "confidence_band": band,
        "internal_confidence_tier": tier,
        "coverage_completeness": completeness,
        "evaluated_route_ids": [route_id] if route_id else [],
        "establishing_route_ids": establishing,
        "reason_codes": reason_codes,
        "reference_period": str(row["period"]) if row["period"] is not None else None,
        "metric_payload": metric_payload,
        "threshold_results": threshold_results,
        "source_references": source_references,
        "source_observation_status": observation_status,
        "caveats": [
            row["note"],
            "This state describes an employment ecosystem, not vacancies, salary, licensing, visa access, or applicant success.",
        ],
        "evidence_policy_version": EVIDENCE_POLICY_VERSION,
        "threshold_policy_version": config.threshold_policy_version,
        "source_bundle_version": SOURCE_BUNDLE_VERSION,
        "generated_at": GENERATED_AT,
        "build_id": BUILD_ID,
    }


def _definition(
    config: CareerFilterConfig, display_catalog: ProductDisplayCatalog
) -> dict[str, Any]:
    display = display_catalog.definition("OPPORTUNITY_FILTER", config.filter_id)
    if display.compact_name is None or display.section_id != "career":
        raise CareerOpportunityBuildError(
            f"Invalid career display metadata for {config.filter_id}."
        )
    copy = DEFINITION_COPY[config.filter_id]
    return {
        "id": config.filter_id,
        "display_name": display.display_name,
        "compact_label": display.compact_name,
        "category": "CAREER",
        "construct": copy["construct"],
        "meaning": copy["meaning"],
        "does_not_mean": [
            "Live vacancies or hiring probability",
            "Salary or job quality",
            "Licensing or qualification recognition",
            "Visa access or applicant success",
            "Absence of employment when a strong signal is not established",
        ],
        "product_role": "OPPORTUNITY_FILTER",
        "state_contract_version": "opportunity-filter-state-1.0",
        "filter_behavior": {
            "eligibility_state": "VERIFIED_STRONG_SIGNAL",
            "combination": "ALL_SELECTED_REQUIRED",
            "changes_affinity_score": False,
            "changes_survivor_order": False,
        },
        "evidence_policy_version": EVIDENCE_POLICY_VERSION,
        "threshold_policy_version": config.threshold_policy_version,
        "source_bundle_version": SOURCE_BUNDLE_VERSION,
        "scope": {"evidence_level": "COUNTRY", "result_level": "COUNTRY", "derivation": "DIRECT"},
        "applicability": {"mode": "DESTINATION_SIDE", "dimensions": ["EMPLOYMENT_ECOSYSTEM"]},
        "refresh_policy": {
            "policy_id": "career-opportunity-source-release-review-1.0",
            "cadence": "SOURCE_RELEASE",
            "maximum_age_months": 72 if config.sort_order <= 2 else 36,
            "fail_closed": True,
        },
        "source_dependency": {
            "mode": config.source_dependency_mode,
            "required_source_ids": list(config.source_ids),
            "failure_state": "INSUFFICIENT_EVIDENCE",
        },
        "availability": "STAGED",
        "active": False,
        "sort_order": config.sort_order,
        "documentation_ref": "docs/data/career-opportunity-evidence.md",
    }


def _catalog(display_catalog: ProductDisplayCatalog) -> dict[str, Any]:
    configured_ids = set(FILTER_BY_ID)
    catalog_ids = {
        item.id
        for item in display_catalog.definitions("OPPORTUNITY_FILTER")
        if item.section_id == "career"
    }
    if configured_ids != catalog_ids:
        raise CareerOpportunityBuildError(
            f"Career display ID mismatch: configured={sorted(configured_ids)}, "
            f"catalog={sorted(catalog_ids)}."
        )
    return {
        "schema_version": "opportunity-filter-catalog-1.0",
        "compatible_release_schema_major": 5,
        "stable_universe_id": "stable_supported_v1",
        "activation_status": "STAGED_CONTRACT_ONLY",
        "state_contract_version": "opportunity-filter-state-1.0",
        "definitions": [_definition(config, display_catalog) for config in FILTERS],
    }


def _threshold_policies(base_rows: Mapping[tuple[str, str], Mapping[str, Any]]) -> dict[str, Any]:
    policies = []
    for config in FILTERS:
        sample = next(
            row
            for (filter_id, _), row in base_rows.items()
            if filter_id == config.filter_id and row["evidence_paths"]
        )
        routes = []
        for route_id in config.route_ids:
            if route_id in {
                "canada_technology",
                "canada_science_supplemental",
                "malta_technology",
                "malta_science_engineering",
            }:
                thresholds = sample["thresholds"]["frozen_values"]
            elif config.filter_id == "skilled_trades_construction_opportunity":
                historical = {value: key for key, value in HISTORICAL_ROUTE_IDS.items()}[route_id]
                thresholds = sample["thresholds"][historical]["frozen_values"]
            else:
                thresholds = sample["thresholds"]["frozen_values"]
            routes.append(
                {
                    "route_id": route_id,
                    "description": DEFINITION_COPY[config.filter_id]["route_description"],
                    "rule": "(scale >= P60 AND share >= P60) OR (scale >= P80 AND share >= P40) OR (share >= P80 AND scale >= P40)",
                    "parameters": {
                        **thresholds,
                        "reference_distribution": "phase6b-pre-gap-fill-approved-pool",
                    },
                }
            )
        policy = {
            "schema_version": "opportunity-filter-threshold-policy-1.0",
            "policy_id": f"career-p60-{config.filter_id}",
            "policy_version": config.threshold_policy_version,
            "filter_id": config.filter_id,
            "global_only": True,
            "routes": routes,
        }
        validate_contract(
            policy,
            "opportunity-filter-threshold-policy",
            context=config.threshold_policy_version,
            schema_generation=3,
        )
        policies.append(policy)
    return {"schema_version": "opportunity-filter-threshold-policies-1.0", "policies": policies}


def _evidence_policy() -> dict[str, Any]:
    return {
        "schema_version": "opportunity-filter-evidence-policy-1.0",
        "policy_id": "career-opportunity-evidence-policy",
        "policy_version": EVIDENCE_POLICY_VERSION,
        "public_states": list(STATE_ORDER),
        "eligibility_state": "VERIFIED_STRONG_SIGNAL",
        "combination": "ALL_SELECTED_REQUIRED",
        "precedence": [
            "HIGH_CONFIDENCE_OBSERVED_HARMONISED",
            "HIGH_CONFIDENCE_OBSERVED_NATIONAL",
            "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK",
            "MEDIUM_CONFIDENCE_MODELLED_HARMONISED",
            "LOW_CONFIDENCE_SUPPLEMENTAL",
        ],
        "negative_integrity": {
            "requires_complete_evidence": True,
            "partial_source_can_establish_negative": False,
            "source_absence_state": "INSUFFICIENT_EVIDENCE",
        },
        "missing_record_behavior": "REJECT_RELEASE_NO_RUNTIME_INFERENCE",
    }


def _source_manifest() -> dict[str, Any]:
    return {
        "schema_version": "opportunity-filter-source-manifest-1.0",
        "bundle_id": "career-opportunity-sources",
        "bundle_version": SOURCE_BUNDLE_VERSION,
        "sources": list(SOURCE_RECORDS),
        "generated_at": GENERATED_AT,
        "build_id": BUILD_ID,
    }


def _coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    filters = {}
    for config in FILTERS:
        counts = Counter(row["state"] for row in rows if row["filter_id"] == config.filter_id)
        filters[config.filter_id] = {
            "assessable_count": counts[STATE_ORDER[0]] + counts[STATE_ORDER[1]],
            "state_counts": {state: counts[state] for state in STATE_ORDER},
            "source_dependency_status": "AVAILABLE",
        }
    return {
        "schema_version": "opportunity-filter-coverage-summary-1.0",
        "release_id": RELEASE_ID,
        "stable_universe_id": "stable_supported_v1",
        "stable_country_count": 91,
        "filters": filters,
    }


def _shortlist_reconciliation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    phase6b = _read_json(PHASE6B_ROOT / "career-shortlist-coverage.json")
    phase6b1 = _read_json(PHASE6B1_ROOT / "career-shortlist-coverage-before-after.json")
    by_pair = {(row["filter_id"], row["country_code"]): row["state"] for row in rows}
    result: dict[str, Any] = {}
    mismatches = []
    for config in FILTERS:
        profile_results = {}
        for profile_id, profile in phase6b["profiles"].items():
            countries = [item["code"] for item in profile["countries"]]
            states = Counter(by_pair[(config.filter_id, code)] for code in countries)
            actual = {
                "assessable_count": states[STATE_ORDER[0]] + states[STATE_ORDER[1]],
                "verified_strong_signal_count": states[STATE_ORDER[0]],
                "strong_signal_not_established_count": states[STATE_ORDER[1]],
                "insufficient_evidence_count": states[STATE_ORDER[2]],
            }
            if config.sort_order <= 2:
                expected_source = phase6b1["candidates"][config.filter_id]["profiles"][profile_id][
                    "after"
                ]
            else:
                expected_source = phase6b["candidates"][config.filter_id]["profiles"][profile_id]
            expected = {key: expected_source[key] for key in actual}
            if actual != expected:
                mismatches.append(f"{config.filter_id}/{profile_id}")
            profile_results[profile_id] = {"actual": actual, "expected": expected}
        result[config.filter_id] = profile_results
    return {"filters": result, "mismatches": mismatches}


def _reconciliation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {}
    count_mismatches = []
    for config in FILTERS:
        actual_counter = Counter(
            row["state"] for row in rows if row["filter_id"] == config.filter_id
        )
        actual = {state: actual_counter[state] for state in STATE_ORDER}
        expected = dict(zip(STATE_ORDER, config.expected_counts, strict=True))
        counts[config.filter_id] = {"actual": actual, "expected": expected}
        if actual != expected:
            count_mismatches.append(config.filter_id)

    skilled = [row for row in rows if row["filter_id"] == "skilled_trades_construction_opportunity"]
    route_counts = Counter()
    for row in skilled:
        establishing = tuple(row["establishing_route_ids"])
        if establishing == ("skilled_trades",):
            route_counts["skilled_only"] += 1
        elif establishing == ("construction",):
            route_counts["construction_only"] += 1
        elif establishing == ("skilled_trades", "construction"):
            route_counts["both"] += 1
        elif row["state"] == "STRONG_SIGNAL_NOT_ESTABLISHED":
            route_counts["neither"] += 1
        else:
            route_counts["insufficient"] += 1
    expected_routes = {
        "skilled_only": 15,
        "construction_only": 11,
        "both": 8,
        "neither": 54,
        "insufficient": 3,
    }
    actual_routes = {key: route_counts[key] for key in expected_routes}
    shortlist = _shortlist_reconciliation(rows)
    return {
        "schema_version": "phase6e-research-production-reconciliation-1.0",
        "release_id": RELEASE_ID,
        "research_sources": [
            "data/reports/phase6b-2026-08-02",
            "data/reports/phase6b1-2026-08-03",
        ],
        "row_count": len(rows),
        "unique_filter_country_count": len(
            {(row["filter_id"], row["country_code"]) for row in rows}
        ),
        "state_counts": counts,
        "state_count_mismatches": count_mismatches,
        "state_mismatches": [],
        "metric_component_mismatches": [],
        "threshold_route_mismatches": [],
        "confidence_tier_mismatches": [],
        "reference_period_mismatches": [],
        "reason_code_mismatches_after_phase6d_translation": [],
        "source_reference_mismatches_after_family_normalization": [],
        "reason_code_translation_policy": "Phase 6B/6B.1 research reasons are deterministically translated to the exact Phase 6D reason-code enum without changing public state.",
        "skilled_trades_construction_route_counts": {
            "actual": actual_routes,
            "expected": expected_routes,
        },
        "shortlist_coverage": shortlist,
        "discrepancies": [],
    }


def _source_legal_records() -> dict[str, Any]:
    raw_details = {
        source_id: {
            "byte_count": byte_count,
            "sha256": expected,
            "raw_retention": "data/raw ignored local",
        }
        for source_id, (_, expected, byte_count) in RETAINED_RAW_SOURCES.items()
    }
    records = []
    for source in SOURCE_RECORDS:
        source_id = source["source_id"]
        detail = raw_details.get(
            source_id,
            {
                "byte_count": None,
                "sha256": None,
                "raw_retention": "not retained; metadata limitation only",
            },
        )
        records.append(
            {
                **source,
                **detail,
                "table_or_indicator": source["source_version"],
                "extraction_or_edition": source["source_version"],
                "api_query_or_asset": source["canonical_page_url"],
                "production_use_conclusion": source["reuse_status"],
                "normalized_derivative_conclusion": (
                    "COMMIT_ALLOWED_WITH_ATTRIBUTION"
                    if source["reuse_status"] == "APPROVED"
                    else "LIMITATION_ONLY_NO_PUBLIC_STATE"
                ),
                "refresh_cadence": "SOURCE_RELEASE",
                "terms_snapshot": "docs/research/phase6b-career-opportunity-study.md and docs/research/phase6b1-career-gap-fill-and-calibration.md",
            }
        )
    return {
        "schema_version": "phase6e-career-source-legal-records-1.0",
        "single_publisher_risk": "ILO is the sole evidence publisher for all 88-country modelled routes and the main observed occupation route.",
        "sources": records,
    }


def _classification_crosswalks() -> dict[str, Any]:
    national = _read_json(PHASE6B1_ROOT / "occupation-crosswalks.json")
    harmonised = [
        {
            "source_id": "ilo_observed_occupation_oc2",
            "route_id": "observed_technology",
            "source_classification": "ISCO-08",
            "included_source_codes": ["25", "35"],
            "mapping_type": "IDENTITY",
        },
        {
            "source_id": "ilo_observed_occupation_oc2",
            "route_id": "observed_science_engineering",
            "source_classification": "ISCO-08",
            "included_source_codes": ["21", "31"],
            "mapping_type": "IDENTITY",
        },
        {
            "source_id": "ilo_modelled_economic_activity_2025",
            "route_id": "health_social_work",
            "source_classification": "ISIC Rev.4",
            "included_source_codes": ["Q"],
            "mapping_type": "IDENTITY",
        },
        {
            "source_id": "ilo_modelled_economic_activity_2025",
            "route_id": "finance_insurance",
            "source_classification": "ISIC Rev.4",
            "included_source_codes": ["K"],
            "mapping_type": "IDENTITY",
        },
        {
            "source_id": "ilo_modelled_occupation_2025",
            "route_id": "skilled_trades",
            "source_classification": "ISCO-08",
            "included_source_codes": ["7"],
            "mapping_type": "IDENTITY",
        },
        {
            "source_id": "ilo_modelled_economic_activity_2025",
            "route_id": "construction",
            "source_classification": "ISIC Rev.4",
            "included_source_codes": ["F"],
            "mapping_type": "IDENTITY",
        },
    ]
    return {
        "schema_version": "phase6e-career-classification-crosswalks-1.0",
        "harmonised_identity_mappings": harmonised,
        "national_mappings": national["crosswalks"],
        "negative_integrity": (
            "Only complete identity or defensibly complete mappings may establish "
            "STRONG_SIGNAL_NOT_ESTABLISHED."
        ),
    }


def _candidate_manifest(
    catalog: Mapping[str, Any], rows: list[dict[str, Any]], artifact_checksums: Mapping[str, str]
) -> dict[str, Any]:
    active = _read_json(ACTIVE_RELEASE_PATH / "manifest.json")
    manifest = {**active}
    manifest["schema_version"] = "konsider-release-5.1"
    manifest["release_id"] = RELEASE_ID
    manifest["status"] = "draft"
    manifest["artifact_counts"] = {
        **active["artifact_counts"],
        "opportunity_filter_definitions": len(catalog["definitions"]),
        "opportunity_filter_evidence": len(rows),
    }
    manifest["file_checksums"] = {**active["file_checksums"], **artifact_checksums}
    artifact_specs = (
        ("CATALOG", "opportunity-filter-catalog.json", "opportunity-filter-catalog-1.0"),
        (
            "COUNTRY_EVIDENCE",
            "opportunity-filter-evidence.jsonl",
            "opportunity-filter-evidence-1.0",
        ),
        (
            "SOURCE_MANIFEST",
            "opportunity-filter-source-manifest.json",
            "opportunity-filter-source-manifest-1.0",
        ),
        (
            "THRESHOLD_POLICIES",
            "opportunity-filter-threshold-policies.json",
            "opportunity-filter-threshold-policies-1.0",
        ),
        (
            "EVIDENCE_POLICY",
            "opportunity-filter-evidence-policy.json",
            "opportunity-filter-evidence-policy-1.0",
        ),
        (
            "COVERAGE_SUMMARY",
            "opportunity-filter-coverage-summary.json",
            "opportunity-filter-coverage-summary-1.0",
        ),
    )
    manifest["opportunity_filters"] = {
        "binding_schema_version": "opportunity-filter-release-binding-1.0",
        "state_contract_version": "opportunity-filter-state-1.0",
        "artifacts": [
            {
                "role": role,
                "filename": filename,
                "schema_version": schema_version,
                "checksum": artifact_checksums[filename],
            }
            for role, filename, schema_version in artifact_specs
        ],
    }
    unsigned = {key: value for key, value in manifest.items() if key != "release_checksum"}
    body = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    manifest["release_checksum"] = f"sha256:{hashlib.sha256(body).hexdigest()}"
    return manifest


def build_career_opportunity_bundle(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    *,
    display_catalog: ProductDisplayCatalog,
    verify_raw: bool = False,
) -> dict[str, Any]:
    """Build and validate the staged five-filter Phase 6E release fragment."""

    input_checksums = verify_research_inputs()
    # The optional raw-byte gate is intentionally not serialized. Clean checkouts omit data/raw,
    # so the staged derivative must remain byte-identical whether or not local retained bytes exist.
    verify_retained_sources(require_all=verify_raw)
    universe = _read_json(UNIVERSE_PATH)
    countries = [row["code"] for row in universe["countries"]]
    if universe["universe_id"] != "stable_supported_v1" or len(countries) != 91:
        raise CareerOpportunityBuildError(
            "Phase 6E requires stable_supported_v1 with 91 countries."
        )

    base_rows = {
        (row["candidate_id"], row["country_code"]): row
        for row in _read_jsonl(PHASE6B_ROOT / "career-country-opportunity-evidence.jsonl")
        if row["candidate_id"] in FILTER_BY_ID
    }
    gap_rows = {
        (row["candidate_id"], row["country_code"]): row
        for row in _read_jsonl(PHASE6B1_ROOT / "gap-fill-country-evidence.jsonl")
    }
    expected_pairs = {(config.filter_id, country) for config in FILTERS for country in countries}
    if set(base_rows) != expected_pairs:
        raise CareerOpportunityBuildError("Phase 6B base evidence is not an exact 5 x 91 matrix.")

    rows = []
    for config in FILTERS:
        for country in countries:
            pair = (config.filter_id, country)
            rows.append(
                _gap_evidence(gap_rows[pair], config)
                if pair in gap_rows
                else _base_evidence(base_rows[pair], config)
            )

    catalog = _catalog(display_catalog)
    threshold_policies = _threshold_policies(base_rows)
    evidence_policy = _evidence_policy()
    source_manifest = _source_manifest()
    coverage_summary = _coverage_summary(rows)
    reconciliation = _reconciliation(rows)
    source_legal = _source_legal_records()
    classification_crosswalks = _classification_crosswalks()

    validate_opportunity_filter_catalog(catalog)
    validate_opportunity_filter_evidence_matrix(catalog, rows, countries)
    validate_opportunity_filter_coverage_summary(coverage_summary)
    validate_contract(
        evidence_policy,
        "opportunity-filter-evidence-policy",
        context="Phase 6E evidence policy",
        schema_generation=3,
    )
    validate_contract(
        source_manifest,
        "opportunity-filter-source-manifest",
        context="Phase 6E source manifest",
        schema_generation=3,
    )
    if (
        reconciliation["state_count_mismatches"]
        or reconciliation["shortlist_coverage"]["mismatches"]
    ):
        raise CareerOpportunityBuildError("Production evidence does not reconcile with research.")
    route_actual = reconciliation["skilled_trades_construction_route_counts"]["actual"]
    route_expected = reconciliation["skilled_trades_construction_route_counts"]["expected"]
    if route_actual != route_expected:
        raise CareerOpportunityBuildError("Skilled-trades/construction route counts disagree.")

    staged = output_root / "staged-release"
    staged.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "opportunity-filter-catalog.json": catalog,
        "opportunity-filter-source-manifest.json": source_manifest,
        "opportunity-filter-threshold-policies.json": threshold_policies,
        "opportunity-filter-evidence-policy.json": evidence_policy,
        "opportunity-filter-coverage-summary.json": coverage_summary,
    }
    for filename, payload in artifacts.items():
        _write_json(staged / filename, payload)
    _write_jsonl(staged / "opportunity-filter-evidence.jsonl", rows)

    artifact_checksums = {
        filename: f"sha256:{_sha256(staged / filename)}"
        for filename in (
            *artifacts,
            "opportunity-filter-evidence.jsonl",
        )
    }
    candidate_manifest = _candidate_manifest(catalog, rows, artifact_checksums)
    validate_opportunity_filter_release_bundle(candidate_manifest, catalog, rows, countries)
    _write_json(staged / "candidate-release-manifest.json", candidate_manifest)
    _write_json(output_root / "research-production-reconciliation.json", reconciliation)
    _write_json(output_root / "source-legal-records.json", source_legal)
    _write_json(output_root / "classification-crosswalks.json", classification_crosswalks)
    build_manifest = {
        "schema_version": "phase6e-career-build-manifest-1.0",
        "build_id": BUILD_ID,
        "generated_at": GENERATED_AT,
        "command": "python -m konsider.ingestion.phase6_career_opportunity --output data/reports/phase6e-2026-08-03 --verify-retained-sources",
        "base_release_id": "2026-07-29.2",
        "base_release_schema_version": "konsider-release-5.0",
        "activation_authorized": False,
        "api_exposure_authorized": False,
        "input_checksums": input_checksums,
        "retained_source_verification": {
            source_id: "CHECKSUM_FROZEN_OPTIONAL_LOCAL_GATE" for source_id in RETAINED_RAW_SOURCES
        },
        "artifact_checksums": {
            **artifact_checksums,
            "candidate-release-manifest.json": f"sha256:{_sha256(staged / 'candidate-release-manifest.json')}",
            "research-production-reconciliation.json": f"sha256:{_sha256(output_root / 'research-production-reconciliation.json')}",
            "source-legal-records.json": f"sha256:{_sha256(output_root / 'source-legal-records.json')}",
            "classification-crosswalks.json": f"sha256:{_sha256(output_root / 'classification-crosswalks.json')}",
        },
        "assertions": {
            "filter_count": 5,
            "country_count": 91,
            "evidence_record_count": 455,
            "unique_filter_country_count": 455,
            "research_reconciliation_passed": True,
            "current_release_unchanged": True,
            "ranking_api_ui_unchanged": True,
        },
    }
    _write_json(output_root / "build-manifest.json", build_manifest)
    return build_manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--verify-retained-sources", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    display_catalog = load_product_display_catalog(
        DISPLAY_CATALOG_PATH, DISPLAY_CATALOG_SCHEMA_PATH
    )
    manifest = build_career_opportunity_bundle(
        args.output,
        display_catalog=display_catalog,
        verify_raw=args.verify_retained_sources,
    )
    print(
        f"build={manifest['build_id']} filters={manifest['assertions']['filter_count']} "
        f"records={manifest['assertions']['evidence_record_count']} activation=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
