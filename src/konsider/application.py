"""Framework-independent deterministic recommendation application services."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from konsider.domain.scoring import ScoringError, normalize_weights
from konsider.domain.uncertainty_comparison import (
    compare_release_with_uncertainty,
)
from konsider.domain.uncertainty_models import (
    UncertaintyComparisonResult,
    UncertaintyRankingResult,
)
from konsider.domain.uncertainty_ranking import rank_release_with_uncertainty
from konsider.exceptions import (
    CountryNotFoundError,
    CriterionNotReadyError,
    InvalidComparisonError,
    InvalidProfileSelectionError,
    InvalidTopKError,
    InvalidWeightError,
    ProfileNotFoundError,
    UnknownCriterionError,
)
from konsider.repositories.published_release_repository import PublishedReleaseRepository


class RecommendationService:
    """Catalog, ranking, comparison, and breakdown operations pinned to one release."""

    def __init__(self, repository: PublishedReleaseRepository) -> None:
        """Construct the historical service from an explicitly selected legacy repository."""

        self.release = repository.load_active()

    def get_catalog(self) -> dict[str, Any]:
        sources_by_criterion: dict[str, list[dict[str, Any]]] = {}
        for source in self.release.sources:
            sources_by_criterion.setdefault(source["criterion_id"], []).append(
                {
                    "source_id": source["source_id"],
                    "publisher": source["publisher"],
                    "source_version": source["source_version"],
                    "dataset_version": source["dataset_version"],
                    "canonical_page_url": source["canonical_page_url"],
                    "attribution": source["attribution"],
                    "reference_period": source["reference_period"],
                }
            )
        return {
            "release_id": self.release.release_id,
            "release_schema_version": self.release.manifest["schema_version"],
            "catalog_schema_version": self.release.catalog["schema_version"],
            "scoring_method_versions": sorted(
                item["scoring_method_version"] for item in self.release.catalog["criteria"]
            ),
            "countries": self.release.catalog["countries"],
            "criteria": [
                self._catalog_criterion(criterion, sources_by_criterion)
                for criterion in self.release.catalog["criteria"]
            ],
            "profiles": self.release.catalog["profiles"],
        }

    def _catalog_criterion(
        self,
        criterion: dict[str, Any],
        sources_by_criterion: dict[str, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        stable_count = len(self.release.catalog["countries"])
        coverage = criterion.get("coverage")
        if coverage is None:
            valid_count = self.release.validation["criterion_coverage"].get(criterion["id"], 0)
            coverage_mode = "GLOBAL_CORE" if criterion["ready"] else "DIAGNOSTIC_ONLY"
            activation_threshold = None
        else:
            valid_count = coverage["valid_country_count"]
            stable_count = coverage["stable_country_count"]
            coverage_mode = coverage["mode"]
            activation_threshold = coverage["activation_threshold"]
        public = {key: value for key, value in criterion.items() if key != "coverage"}
        public.update(
            {
                "enabled": criterion["ready"],
                "coverage_mode": coverage_mode,
                "valid_country_count": valid_count,
                "stable_country_count": stable_count,
                "coverage_percentage": round(valid_count / stable_count * 100, 2),
                "pcc_activation_threshold": activation_threshold,
                "missing_country_count": stable_count - valid_count,
                "concise_caveat": (criterion["caveats"][0] if criterion["caveats"] else None),
                "sources": sorted(
                    sources_by_criterion.get(criterion["id"], []),
                    key=lambda item: item["source_id"],
                ),
            }
        )
        return public

    def _resolve_weights(
        self,
        weights: Mapping[str, float] | None,
        profile_id: str | None,
    ) -> tuple[dict[str, float], str | None]:
        if weights is not None and profile_id is not None:
            raise InvalidProfileSelectionError("Provide either weights or profile_id, not both.")
        if weights is not None:
            return dict(weights), None
        selected_profile = profile_id or "equal_weight_mvp"
        profiles = {item["id"]: item for item in self.release.catalog["profiles"]}
        try:
            profile = profiles[selected_profile]
        except KeyError as exc:
            raise ProfileNotFoundError(selected_profile) from exc
        return dict(profile["weights"]), selected_profile

    def rank(
        self,
        weights: Mapping[str, float] | None = None,
        *,
        profile_id: str | None = None,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        resolved_weights, resolved_profile_id = self._resolve_weights(weights, profile_id)
        enabled = self.release.enabled_criterion_ids
        available = set(self.release.available_criterion_ids)
        supplied = set(resolved_weights)
        non_ready = sorted(supplied & (available - set(enabled)))
        if non_ready:
            raise CriterionNotReadyError(non_ready)
        unknown = sorted(supplied - available)
        if unknown:
            raise UnknownCriterionError(unknown)
        try:
            normalized_nonzero = normalize_weights(resolved_weights, enabled)
        except (ScoringError, TypeError, ValueError) as exc:
            raise InvalidWeightError(str(exc)) from exc
        normalized = {
            criterion_id: normalized_nonzero.get(criterion_id, 0.0) for criterion_id in enabled
        }

        by_country: dict[str, list[Any]] = {}
        for record in self.release.records:
            by_country.setdefault(record.country["code"], []).append(record)
        rankings = []
        for country_code, records in sorted(by_country.items()):
            contributions = []
            for record in sorted(records, key=lambda item: item.criterion["id"]):
                criterion_id = record.criterion["id"]
                weight = normalized[criterion_id]
                contribution = round(record.score["score"] * weight, 8)
                observation = record.observations[0]
                contributions.append(
                    {
                        "criterion_id": criterion_id,
                        "criterion_name": record.criterion["display_name"],
                        "score": record.score["score"],
                        "normalized_weight": weight,
                        "contribution": contribution,
                        "raw_observation": observation["value"],
                        "raw_unit": observation["unit"],
                        "reference_start": observation["reference_start"],
                        "reference_end": observation["reference_end"],
                        "observation_id": observation["observation_id"],
                        "observation_method_version": observation["method_version"],
                        "parser_version": observation["parser_version"],
                        "scoring_method_version": record.score["method_version"],
                        "source": {
                            "source_id": record.source["source_id"],
                            "publisher": record.source["publisher"],
                            "source_version": record.source["source_version"],
                            "dataset_version": record.source["dataset_version"],
                            "canonical_page_url": record.source["canonical_page_url"],
                            "attribution": record.source["attribution"],
                        },
                        "caveats": record.criterion["caveats"],
                        "quality_limitations": record.criterion["quality_limitations"],
                        "experimental": record.criterion["experimental"],
                        "input_observations": list(record.observations),
                    }
                )
            total = round(sum(item["contribution"] for item in contributions), 8)
            weighted = [item for item in contributions if item["normalized_weight"] > 0]
            strengths = [
                item["criterion_id"]
                for item in sorted(
                    weighted, key=lambda item: (-item["score"], item["criterion_id"])
                )[:3]
            ]
            tradeoffs = [
                item["criterion_id"]
                for item in sorted(
                    weighted, key=lambda item: (item["score"], item["criterion_id"])
                )[:3]
            ]
            rankings.append(
                {
                    "country_code": country_code,
                    "country_name": records[0].country["display_name"],
                    "region": records[0].country["region"],
                    "total_score": total,
                    "contributions": contributions,
                    "strengths": strengths,
                    "tradeoffs": tradeoffs,
                }
            )
        rankings.sort(key=lambda item: (-item["total_score"], item["country_code"]))
        for rank, item in enumerate(rankings, 1):
            item["rank"] = rank
        eligible_count = len(rankings)
        if top_k is not None and (
            isinstance(top_k, bool)
            or not isinstance(top_k, int)
            or not 1 <= top_k <= eligible_count
        ):
            raise InvalidTopKError(top_k, eligible_count)
        rankings = rankings[:top_k]
        return {
            "release_id": self.release.release_id,
            "release_schema_version": self.release.manifest["schema_version"],
            "catalog_schema_version": self.release.catalog["schema_version"],
            "scoring_method_versions": sorted(
                item["scoring_method_version"]
                for item in self.release.catalog["criteria"]
                if item["ready"]
            ),
            "resolved_profile_id": resolved_profile_id,
            "normalized_weights": normalized,
            "all_zero_behavior": "equal_weights_across_all_enabled_criteria",
            "country_tie_breaker": "ascending_iso3_country_code",
            "rounding_tolerance": 1e-8,
            "total_eligible_country_count": eligible_count,
            "returned_result_count": len(rankings),
            "rankings": rankings,
        }

    def rank_with_uncertainty(
        self,
        weights: Mapping[str, float] | None = None,
        *,
        profile_id: str | None = None,
        top_k: int | None = None,
    ) -> UncertaintyRankingResult:
        """Return the typed Phase 4 ranking result without changing the HTTP contract."""

        resolved_weights, resolved_profile_id = self._resolve_weights(weights, profile_id)
        return rank_release_with_uncertainty(
            self.release,
            resolved_weights,
            resolved_profile_id=resolved_profile_id,
            top_k=top_k,
        )

    def compare_with_uncertainty(
        self,
        country_codes: Sequence[str],
        weights: Mapping[str, float] | None = None,
        *,
        profile_id: str | None = None,
    ) -> UncertaintyComparisonResult:
        """Compare available evidence while suppressing invalid partial totals."""

        requested = tuple(country_codes)
        if len(requested) < 2 or len(requested) > 10:
            raise InvalidComparisonError("Comparisons require between 2 and 10 countries.")
        if len(requested) != len(set(requested)):
            raise InvalidComparisonError("Comparison country codes must be unique.")
        ranking = self.rank_with_uncertainty(
            weights,
            profile_id=profile_id,
        )
        known = {item["code"] for item in self.release.catalog["countries"]}
        unknown = sorted(set(requested) - known)
        if unknown:
            raise CountryNotFoundError(unknown)
        return compare_release_with_uncertainty(
            self.release,
            ranking,
            requested,
        )

    def compare(
        self,
        country_codes: Sequence[str],
        weights: Mapping[str, float] | None = None,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        requested = list(country_codes)
        if len(requested) < 2 or len(requested) > 10:
            raise InvalidComparisonError("Comparisons require between 2 and 10 countries.")
        if len(requested) != len(set(requested)):
            raise InvalidComparisonError("Comparison country codes must be unique.")
        result = self.rank(weights, profile_id=profile_id)
        known = {item["code"] for item in self.release.catalog["countries"]}
        unknown = sorted(set(requested) - known)
        if unknown:
            raise CountryNotFoundError(unknown)
        rows = {item["country_code"]: item for item in result["rankings"]}
        result["countries"] = [rows[code] for code in requested]
        result.pop("rankings")
        result["returned_result_count"] = len(result["countries"])
        return result

    def country_breakdown(self, country_code: str) -> dict[str, Any]:
        records = [
            record for record in self.release.records if record.country["code"] == country_code
        ]
        if not records:
            raise CountryNotFoundError([country_code])
        return {
            "release_id": self.release.release_id,
            "release_schema_version": self.release.manifest["schema_version"],
            "catalog_schema_version": self.release.catalog["schema_version"],
            "scoring_method_versions": sorted(
                item["scoring_method_version"]
                for item in self.release.catalog["criteria"]
                if item["ready"]
            ),
            "country": records[0].country,
            "criteria": [
                {
                    "criterion": record.criterion,
                    "score": record.score,
                    "observations": list(record.observations),
                    "source": record.source,
                }
                for record in sorted(records, key=lambda item: item.criterion["id"])
            ],
        }
