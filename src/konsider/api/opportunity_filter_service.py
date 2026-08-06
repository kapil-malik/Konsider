"""Indexed, offline Opportunity Filter evaluation over one immutable bundle."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from konsider.contracts import validate_contract
from konsider.domain.opportunity_filters import (
    OpportunityFilterState,
    validate_opportunity_filter_catalog,
    validate_opportunity_filter_coverage_summary,
    validate_opportunity_filter_evidence_matrix,
    validate_opportunity_filter_release_binding,
)
from konsider.exceptions import (
    InvalidOpportunityFilterSelectionError,
    OpportunityFilterNotActiveError,
    UnknownOpportunityFilterError,
)

STATE_ORDER = (
    OpportunityFilterState.VERIFIED_STRONG_SIGNAL.value,
    OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value,
    OpportunityFilterState.INSUFFICIENT_EVIDENCE.value,
)


class OpportunityFilterBundleError(ValueError):
    """Raised when an immutable Opportunity Filter bundle is unavailable or inconsistent."""


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class OpportunityFilterService:
    """Validate once, index once, and evaluate strict-AND filters without source I/O."""

    def __init__(
        self,
        *,
        release_id: str | None,
        catalog: Mapping[str, Any] | None = None,
        evidence_rows: Sequence[Mapping[str, Any]] = (),
        source_manifest: Mapping[str, Any] | None = None,
        coverage_summary: Mapping[str, Any] | None = None,
        evidence_policy: Mapping[str, Any] | None = None,
    ) -> None:
        self.release_id = release_id
        self.catalog = dict(catalog or {})
        self.source_manifest = dict(source_manifest or {})
        self.coverage_summary = dict(coverage_summary or {})
        self.evidence_policy = dict(evidence_policy or {})
        self._definitions = {row["id"]: dict(row) for row in self.catalog.get("definitions", [])}
        self._evidence = {
            (row["filter_id"], row["country_code"]): dict(row) for row in evidence_rows
        }
        self._sources = {
            row["source_id"]: dict(row) for row in self.source_manifest.get("sources", [])
        }
        self._countries = tuple(sorted({country for _, country in self._evidence}))
        if self._definitions:
            validate_opportunity_filter_catalog(self.catalog)
            validate_opportunity_filter_evidence_matrix(
                self.catalog, list(self._evidence.values()), self._countries
            )
            validate_opportunity_filter_coverage_summary(self.coverage_summary)
            validate_contract(
                self.source_manifest,
                "opportunity-filter-source-manifest",
                context="Opportunity Filter API source manifest",
                schema_generation=3,
            )
            validate_contract(
                self.evidence_policy,
                "opportunity-filter-evidence-policy",
                context="Opportunity Filter API evidence policy",
                schema_generation=3,
            )
            if len(self._countries) != 91 or len(self._evidence) != len(self._definitions) * 91:
                raise OpportunityFilterBundleError(
                    "Opportunity Filter API bundle must contain one row per filter and stable country."
                )

    @classmethod
    def empty(cls) -> OpportunityFilterService:
        return cls(release_id=None)

    @classmethod
    def from_directory(cls, path: Path | str) -> OpportunityFilterService:
        root = Path(path)
        manifest = _read_json(root / "candidate-release-manifest.json")
        if manifest["status"] not in {"draft", "published"}:
            raise OpportunityFilterBundleError("Opportunity Filter release status is unsupported.")
        return cls._from_bound_release(root, manifest)

    @classmethod
    def from_release(
        cls, path: Path | str, manifest: Mapping[str, Any]
    ) -> OpportunityFilterService:
        """Load the checksummed Opportunity Filter artifacts bound to a published release."""

        if manifest.get("status") != "published":
            raise OpportunityFilterBundleError(
                "Only a published release can provide active Opportunity Filters."
            )
        return cls._from_bound_release(Path(path), manifest)

    @classmethod
    def _from_bound_release(
        cls, root: Path, manifest: Mapping[str, Any]
    ) -> OpportunityFilterService:
        validate_opportunity_filter_release_binding(manifest)
        binding = manifest.get("opportunity_filters")
        if binding is None:
            raise OpportunityFilterBundleError("The release has no Opportunity Filter binding.")
        for artifact in binding["artifacts"]:
            filename = artifact["filename"]
            actual = _checksum(root / filename)
            if actual != artifact["checksum"] or actual != manifest["file_checksums"][filename]:
                raise OpportunityFilterBundleError(
                    f"Opportunity Filter checksum mismatch for {filename}."
                )
        evidence_rows = _read_jsonl(root / "opportunity-filter-evidence.jsonl")
        coverage_summary = _read_json(root / "opportunity-filter-coverage-summary.json")
        expected_source_release_id = manifest["release_id"]
        if manifest.get("schema_version") == "konsider-release-5.2":
            expected_source_release_id = manifest["display_metadata_equivalence"][
                "source_release_id"
            ]
        if coverage_summary.get("release_id") != expected_source_release_id or any(
            row.get("release_id") != expected_source_release_id for row in evidence_rows
        ):
            raise OpportunityFilterBundleError(
                "Opportunity Filter API artifacts and release identity disagree."
            )
        return cls(
            release_id=manifest["release_id"],
            catalog=_read_json(root / "opportunity-filter-catalog.json"),
            evidence_rows=evidence_rows,
            source_manifest=_read_json(root / "opportunity-filter-source-manifest.json"),
            coverage_summary=coverage_summary,
            evidence_policy=_read_json(root / "opportunity-filter-evidence-policy.json"),
        )

    @property
    def filter_count(self) -> int:
        return len(self._definitions)

    @property
    def evidence_count(self) -> int:
        return len(self._evidence)

    def catalog_payload(self) -> dict[str, Any]:
        definitions = []
        coverage = self.coverage_summary.get("filters", {})
        modern = self.catalog.get("schema_version") == "opportunity-filter-catalog-2.0"
        order_key = "sortOrder" if modern else "sort_order"
        for filter_id, definition in sorted(
            self._definitions.items(), key=lambda item: item[1][order_key]
        ):
            source_ids = definition["source_dependency"]["required_source_ids"]
            sources = [self._sources[source_id] for source_id in source_ids]
            definitions.append(
                {
                    "id": filter_id,
                    "display_name": definition.get("displayName", definition.get("display_name")),
                    "compact_label": definition.get("compactName", definition.get("compact_label")),
                    "category": (
                        str(definition["sectionId"]).upper() if modern else definition["category"]
                    ),
                    "meaning": definition["meaning"],
                    "limitations": definition["does_not_mean"],
                    "documentation_ref": definition["documentation_ref"],
                    "coverage": coverage[filter_id],
                    "source_vintage": [
                        {
                            "source_id": source["source_id"],
                            "source_version": source["source_version"],
                            "publisher": source["publisher"],
                            "attribution": source["attribution"],
                        }
                        for source in sources
                    ],
                    "active": definition["active"],
                    "availability": definition["availability"],
                    "mode": "ALL_REQUIRED",
                    "eligibility_state": "VERIFIED_STRONG_SIGNAL",
                    "no_score_impact": True,
                }
            )
        return {
            "opportunity_release_id": self.release_id,
            "state_contract_version": self.catalog.get("state_contract_version"),
            "evidence_policy_version": self.evidence_policy.get("policy_version"),
            "source_bundle_version": self.source_manifest.get("bundle_version"),
            "mode": "ALL_REQUIRED",
            "no_score_impact": True,
            "definitions": definitions,
        }

    def _selected(self, filter_ids: Sequence[str]) -> tuple[str, ...]:
        if len(filter_ids) != len(set(filter_ids)):
            raise InvalidOpportunityFilterSelectionError("Opportunity Filter IDs must be unique.")
        selected = tuple(sorted(filter_ids))
        unknown = sorted(set(selected) - set(self._definitions))
        if unknown:
            raise UnknownOpportunityFilterError(unknown)
        inactive = sorted(
            filter_id
            for filter_id in selected
            if not self._definitions[filter_id]["active"]
            or self._definitions[filter_id]["availability"] != "AVAILABLE"
        )
        if inactive:
            raise OpportunityFilterNotActiveError(inactive)
        return selected

    def evidence_summary(self, filter_id: str, country_code: str) -> dict[str, Any]:
        row = self._evidence[(filter_id, country_code)]
        definition = self._definitions[filter_id]
        return {
            "filter_id": filter_id,
            "state": row["state"],
            "passes": row["state"] == OpportunityFilterState.VERIFIED_STRONG_SIGNAL.value,
            "confidence_band": row["confidence_band"],
            "establishing_route_ids": row["establishing_route_ids"],
            "reason_codes": row["reason_codes"],
            "reference_period": row["reference_period"],
            "source_ids": [item["source_id"] for item in row["source_references"]],
            "limitations": definition["does_not_mean"],
            "documentation_ref": definition["documentation_ref"],
        }

    def all_country_evidence(self, country_code: str) -> list[dict[str, Any]]:
        order_key = (
            "sortOrder"
            if self.catalog.get("schema_version") == "opportunity-filter-catalog-2.0"
            else "sort_order"
        )
        return [
            self.evidence_summary(filter_id, country_code)
            for filter_id in sorted(
                self._definitions, key=lambda item: self._definitions[item][order_key]
            )
        ]

    def assess_ranked_countries(
        self,
        ranked_countries: Sequence[Mapping[str, Any]],
        filter_ids: Sequence[str],
    ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        selected = self._selected(filter_ids)
        country_results: dict[str, dict[str, Any]] = {}
        filtered_rank = 0
        for ranked in ranked_countries:
            country_code = ranked["country"]["country_codes"][0]
            summaries = [self.evidence_summary(filter_id, country_code) for filter_id in selected]
            passes = all(item["passes"] for item in summaries)
            if passes:
                filtered_rank += 1
            country_results[country_code] = {
                "country_code": country_code,
                "base_rank": ranked["rank"],
                "filtered_rank": filtered_rank if passes else None,
                "passes": passes,
                "filter_evidence": summaries,
            }

        passing = sum(item["passes"] for item in country_results.values())
        exclusion_categories = Counter()
        excluded_countries = []
        for country_code, result in country_results.items():
            if result["passes"]:
                continue
            failing = [item for item in result["filter_evidence"] if not item["passes"]]
            category = (
                OpportunityFilterState.INSUFFICIENT_EVIDENCE.value
                if any(
                    item["state"] == OpportunityFilterState.INSUFFICIENT_EVIDENCE.value
                    for item in failing
                )
                else OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value
            )
            exclusion_categories[category] += 1
            excluded_countries.append(
                {
                    "country_code": country_code,
                    "base_rank": result["base_rank"],
                    "exclusion_category": category,
                    "failing_filter_evidence": failing,
                }
            )

        per_filter = []
        for filter_id in selected:
            counts = Counter(
                self._evidence[(filter_id, country_code)]["state"]
                for country_code in country_results
            )
            per_filter.append(
                {
                    "filter_id": filter_id,
                    "input_country_count": len(country_results),
                    "passing_country_count": counts[
                        OpportunityFilterState.VERIFIED_STRONG_SIGNAL.value
                    ],
                    "state_counts": {state: counts[state] for state in STATE_ORDER},
                }
            )

        status = "NO_FILTERS_ACTIVE"
        if selected:
            status = "NO_COUNTRIES_MATCH" if passing == 0 else "FILTERS_APPLIED"
        assessment = {
            "status": status,
            "mode": "ALL_REQUIRED",
            "active_filter_ids": list(selected),
            "input_ranked_country_count": len(country_results),
            "passing_country_count": passing,
            "excluded_country_count": len(country_results) - passing,
            "excluded_counts_by_state": {
                OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value: exclusion_categories[
                    OpportunityFilterState.STRONG_SIGNAL_NOT_ESTABLISHED.value
                ],
                OpportunityFilterState.INSUFFICIENT_EVIDENCE.value: exclusion_categories[
                    OpportunityFilterState.INSUFFICIENT_EVIDENCE.value
                ],
            },
            "per_filter": per_filter,
            "excluded_countries": excluded_countries,
            "opportunity_release_id": self.release_id,
            "evidence_policy_version": self.evidence_policy.get("policy_version"),
            "source_bundle_version": self.source_manifest.get("bundle_version"),
            "strict_filter_explanation": (
                "A country passes only when every selected Opportunity Filter is "
                "VERIFIED_STRONG_SIGNAL. Other states are exclusions, not negative evidence."
            ),
            "no_score_impact": True,
        }
        return assessment, country_results


__all__ = ["OpportunityFilterBundleError", "OpportunityFilterService"]
