"""Application-facing API v2 service and the temporary schema-4 migration adapter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from konsider.api.mappers import ranking_response
from konsider.application import RecommendationService
from konsider.domain.locality_models import Phase5Contribution, Phase5RankingResult
from konsider.domain.phase5_ranking import Phase5RankingError, rank_schema5_release
from konsider.exceptions import (
    CountryNotFoundError,
    CriterionNotReadyError,
    InvalidTopKError,
    InvalidWeightError,
    PreferencePresetNotFoundError,
    UnknownCriterionError,
)
from konsider.ingestion.current_release import LoadedCurrentRelease

API_CONTRACT_VERSION = "konsider-api-2.0"
LEGACY_LOCALITY_POLICY_VERSION = "locality-assessment-policy-1.0"


def _reason(
    code: str,
    *,
    severity: str = "INFO",
    effect: str = "NONE",
) -> dict[str, str]:
    return {"code": code, "severity": severity, "effect": effect}


def _country_entity(code: str, *, name: str, region: str | None) -> dict[str, Any]:
    return {
        "entity_id": f"country:{code}",
        "entity_type": "COUNTRY",
        "display_name": name,
        "country_codes": [code],
        "region": region,
    }


def _no_profile() -> dict[str, Any]:
    return {
        "status": "NO_PROFILE_CONTEXT",
        "evaluated_dimensions": [],
        "reasons": [
            _reason(
                "PROFILE_CONTEXT_NOT_SUPPLIED",
                effect="NOT_EVALUATED",
            )
        ],
    }


def _no_locality_country() -> dict[str, Any]:
    return {
        "status": "NO_ACTIVE_LOCALITY_CRITERIA",
        "eligible_locality_entity_ids": [],
        "valid_locality_entity_ids": [],
        "contributing_locality_entity_ids": [],
        "common_locality_entity_ids": [],
        "best_common_locality_entity_id": None,
        "criterion_evidence": [],
        "reasons": [_reason("NO_LOCALITY_CRITERIA_CONTRIBUTING")],
    }


def _no_locality_response() -> dict[str, Any]:
    return {
        "status": "NO_ACTIVE_LOCALITY_CRITERIA",
        "policy_version": LEGACY_LOCALITY_POLICY_VERSION,
        "contributing_criterion_ids": [],
        "analysis_triggered_criterion_ids": [],
        "below_threshold_criterion_ids": [],
        "analysis_thresholds": {},
        "aggregation_policy_ids": [],
        "reasons": [_reason("NO_LOCALITY_CRITERIA_CONTRIBUTING")],
    }


def _source_from_legacy(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source["source_id"],
        "role": "PRIMARY_OBSERVATION",
        "publisher": source.get("publisher"),
        "source_version": source["source_version"],
        "dataset_version": source.get("dataset_version"),
        "asset_uri": None,
        "checksum": None,
        "licence_id": source.get("license_name"),
        "canonical_page_url": source.get("canonical_page_url"),
        "attribution": source.get("attribution"),
        "reference_period": source.get("reference_period"),
    }


def _source_from_current(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source["source_id"],
        "role": source["role"],
        "publisher": None,
        "source_version": source["source_version"],
        "dataset_version": None,
        "asset_uri": source["asset_uri"],
        "checksum": source["checksum"],
        "licence_id": source["licence_id"],
        "canonical_page_url": None,
        "attribution": None,
        "reference_period": None,
    }


class V2RecommendationService:
    """Expose one clean v2 contract over either the current or transitional release path."""

    def __init__(
        self,
        source: RecommendationService | LoadedCurrentRelease,
    ) -> None:
        self.legacy = source if isinstance(source, RecommendationService) else None
        self.current = source if isinstance(source, LoadedCurrentRelease) else None

    @property
    def release_id(self) -> str:
        if self.current is not None:
            return self.current.manifest["release_id"]
        assert self.legacy is not None
        return self.legacy.release.release_id

    def _version_fields(self) -> dict[str, Any]:
        if self.current is not None:
            catalog = self.current.artifacts.consumer_catalog
            return {
                "api_contract_version": API_CONTRACT_VERSION,
                "release_id": self.current.manifest["release_id"],
                "release_schema_version": self.current.manifest["schema_version"],
                "catalog_schema_version": catalog["schema_version"],
                "scoring_method_versions": list(self.current.manifest["scoring_method_versions"]),
            }
        assert self.legacy is not None
        release = self.legacy.release
        return {
            "api_contract_version": API_CONTRACT_VERSION,
            "release_id": release.release_id,
            "release_schema_version": release.manifest["schema_version"],
            "catalog_schema_version": release.catalog["schema_version"],
            "scoring_method_versions": sorted(
                criterion["scoring_method_version"]
                for criterion in release.catalog["criteria"]
                if criterion["ready"]
            ),
        }

    def health(self) -> dict[str, Any]:
        if self.current is not None:
            artifacts = self.current.artifacts
            return {
                **self._version_fields(),
                "status": "ok",
                "country_count": sum(
                    row["entity_type"] == "COUNTRY" for row in artifacts.geographic_entities
                ),
                "enabled_criterion_count": sum(
                    row["ready"] for row in artifacts.consumer_catalog["criteria"]
                ),
                "ready_for_rankings": bool(self.current.validation["product_ready"]),
            }
        assert self.legacy is not None
        release = self.legacy.release
        return {
            **self._version_fields(),
            "status": "ok",
            "country_count": len(release.catalog["countries"]),
            "enabled_criterion_count": len(release.enabled_criterion_ids),
            "ready_for_rankings": bool(release.validation["product_ready"]),
        }

    def _legacy_coverage(self, criterion: dict[str, Any]) -> dict[str, Any]:
        assert self.legacy is not None
        release = self.legacy.release
        detail = release.validation["criterion_coverage_details"][criterion["id"]]
        return {
            "mode": detail["mode"],
            "stable_universe_id": detail["stable_universe_id"],
            "stable_country_count": detail["stable_country_count"],
            "valid_country_count": detail["valid_country_count"],
            "minimum_valid_country_count": detail["minimum_valid_country_count"],
            "outcome_counts": detail["outcome_counts"],
            "activation_threshold": detail["activation_threshold"],
            "score_range": {
                "minimum": detail["score_min"],
                "maximum": detail["score_max"],
            },
            "source_lineage_ids": [
                f"legacy-source:{source_id}" for source_id in sorted(detail["source_versions"])
            ],
        }

    def _legacy_catalog_criterion(self, criterion: dict[str, Any]) -> dict[str, Any]:
        assert self.legacy is not None
        sources = [
            _source_from_legacy(source)
            for source in self.legacy.release.sources
            if source["criterion_id"] == criterion["id"]
        ]
        return {
            "id": criterion["id"],
            "display_name": criterion["display_name"],
            "historical_names": [],
            "category": criterion["category"],
            "description": criterion["description"],
            "direction": criterion["direction"],
            "raw_unit": criterion["raw_unit"],
            "interpretation": criterion["interpretation"],
            "caveats": criterion["caveats"],
            "quality_limitations": criterion["quality_limitations"],
            "ready": criterion["ready"],
            "default_enabled": criterion["default_enabled"],
            "experimental": criterion["experimental"],
            "scoring_method_version": criterion["scoring_method_version"],
            "coverage": self._legacy_coverage(criterion),
            "scope": {
                "evidence_level": "COUNTRY",
                "result_level": "COUNTRY",
                "locality_type": None,
                "derivation": "DIRECT",
                "locality_universe_id": None,
                "aggregation_policy_id": None,
                "locality_analysis_threshold": None,
            },
            "applicability": {"mode": "UNIVERSAL", "dimensions": []},
            "sources": sorted(sources, key=lambda item: item["source_id"]),
        }

    def _current_catalog_criterion(self, criterion: dict[str, Any]) -> dict[str, Any]:
        assert self.current is not None
        lineages = {row["lineage_id"]: row for row in self.current.artifacts.source_lineages}
        sources = [
            _source_from_current(source)
            for lineage_id in criterion["coverage"]["source_lineage_ids"]
            for source in lineages[lineage_id]["sources"]
        ]
        return {**criterion, "sources": sources}

    def catalog(self) -> dict[str, Any]:
        if self.current is not None:
            catalog = self.current.artifacts.consumer_catalog
            entities = {row["entity_id"]: row for row in self.current.artifacts.geographic_entities}
            countries = [
                {
                    "entity_id": row["entity_id"],
                    "entity_type": row["entity_type"],
                    "display_name": row["display_name"],
                    "country_codes": row["country_codes"],
                    "region": None,
                }
                for row in sorted(entities.values(), key=lambda item: item["entity_id"])
                if row["entity_type"] == "COUNTRY"
            ]
            return {
                **self._version_fields(),
                "coverage_policy_version": catalog["coverage_policy_version"],
                "stable_universe_id": catalog["stable_universe_id"],
                "countries": countries,
                "criteria": [
                    self._current_catalog_criterion(row)
                    for row in sorted(catalog["criteria"], key=lambda item: item["id"])
                ],
                "preference_presets": catalog["preference_presets"],
            }
        assert self.legacy is not None
        release = self.legacy.release
        return {
            **self._version_fields(),
            "coverage_policy_version": release.validation["coverage_policy_version"],
            "stable_universe_id": release.manifest["country_universe"]["universe_id"],
            "countries": [
                _country_entity(
                    row["code"],
                    name=row["display_name"],
                    region=row["region"],
                )
                for row in release.catalog["countries"]
            ],
            "criteria": [
                self._legacy_catalog_criterion(row)
                for row in sorted(release.catalog["criteria"], key=lambda item: item["id"])
            ],
            "preference_presets": release.catalog["profiles"],
        }

    def _resolve_weights(
        self,
        weights: Mapping[str, float] | None,
        preference_preset_id: str | None,
    ) -> tuple[dict[str, float], str | None]:
        catalog = self.catalog()
        criteria = {row["id"]: row for row in catalog["criteria"]}
        if weights is None:
            presets = {row["id"]: row for row in catalog["preference_presets"]}
            selected = preference_preset_id or (
                "equal_weight_mvp" if "equal_weight_mvp" in presets else sorted(presets)[0]
            )
            try:
                return dict(presets[selected]["weights"]), selected
            except KeyError as exc:
                raise PreferencePresetNotFoundError(selected) from exc
        unknown = sorted(set(weights) - set(criteria))
        if unknown:
            raise UnknownCriterionError(unknown)
        non_ready = sorted(
            criterion_id
            for criterion_id, value in weights.items()
            if value and not criteria[criterion_id]["ready"]
        )
        if non_ready:
            raise CriterionNotReadyError(non_ready)
        for criterion_id, value in weights.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value < 0
            ):
                raise InvalidWeightError(
                    f"Weight for {criterion_id} must be finite and non-negative."
                )
        return dict(weights), None

    def _entity_map(self) -> dict[str, dict[str, Any]]:
        return {row["entity_id"]: row for row in self.catalog()["countries"]}

    def _current_source_metadata(self, lineage_ids: Sequence[str]) -> list[dict[str, Any]]:
        assert self.current is not None
        lineages = {row["lineage_id"]: row for row in self.current.artifacts.source_lineages}
        return [
            _source_from_current(source)
            for lineage_id in lineage_ids
            for source in lineages[lineage_id]["sources"]
        ]

    def _current_observation(
        self,
        row: dict[str, Any],
        *,
        observation_method_version: str,
        parser_version: str,
    ) -> dict[str, Any]:
        return {
            "observation_id": row["observation_id"],
            "subject": row["subject"],
            "value": row["value"],
            "unit": row["unit"],
            "reference_start": row["reference_period"]["start"],
            "reference_end": row["reference_period"]["end"],
            "source_lineage_id": row["source_lineage_id"],
            "observation_method_version": observation_method_version,
            "parser_version": parser_version,
            "quality_flags": row["quality_flags"],
        }

    def _current_contribution(
        self,
        contribution: Phase5Contribution,
    ) -> dict[str, Any]:
        assert self.current is not None
        artifacts = self.current.artifacts
        criteria = {row["id"]: row for row in artifacts.consumer_catalog["criteria"]}
        criterion = criteria[contribution.criterion_id]
        criterion_policy = next(
            row
            for row in artifacts.criterion_policies
            if row["criterion_id"] == contribution.criterion_id
        )
        parser = criterion_policy["parser"]
        observation_method_version = f"{parser['id']}@{parser['version']}"
        scores = {row["score_id"]: row for row in artifacts.scores}
        observations = {row["observation_id"]: row for row in artifacts.observations}
        score = scores[contribution.score_id]
        outcome = next(
            row
            for row in artifacts.criterion_outcomes
            if row["criterion_id"] == contribution.criterion_id
            and row["score_id"] == contribution.score_id
        )
        evidence = (
            next(
                row
                for row in artifacts.derived_country_evidence
                if row["evidence_id"] == contribution.derived_evidence_id
            )
            if contribution.derived_evidence_id
            else None
        )
        policy = (
            next(
                row
                for row in artifacts.aggregation_policies
                if row["policy_id"] == criterion["scope"]["aggregation_policy_id"]
            )
            if evidence
            else None
        )
        entities = {row["entity_id"]: row for row in artifacts.geographic_entities}
        locality_inputs = []
        observation_ids = list(score["observation_ids"])
        if evidence:
            observation_ids = [
                observation_id
                for locality in evidence["contributing_localities"]
                for observation_id in locality["observation_ids"]
            ]
            for locality in evidence["contributing_localities"]:
                entity = entities[locality["locality"]["entity_id"]]
                locality_inputs.append(
                    {
                        "locality": {
                            "entity_id": entity["entity_id"],
                            "entity_type": entity["entity_type"],
                            "display_name": entity["display_name"],
                            "country_codes": entity["country_codes"],
                            "region": None,
                        },
                        "input_score": locality["score"],
                        "observation_id": locality["observation_ids"][0],
                        "score_id": locality["score_id"],
                    }
                )
        selected_observations = [observations[item] for item in observation_ids]
        lineage_ids = list(outcome["source_lineage_ids"])
        return {
            "criterion_id": contribution.criterion_id,
            "criterion_name": criterion["display_name"],
            "source_scope": criterion["scope"]["evidence_level"],
            "result_scope": "COUNTRY",
            "derivation": criterion["scope"]["derivation"],
            "score": contribution.score,
            "normalized_weight": contribution.normalized_weight,
            "contribution": contribution.contribution,
            "score_id": contribution.score_id,
            "derived_evidence_id": contribution.derived_evidence_id,
            "aggregation_policy": (
                {
                    "policy_id": policy["policy_id"],
                    "policy_version": policy["policy_version"],
                    "method": policy["selection"]["method"],
                    "n": policy["selection"]["n"],
                }
                if policy
                else None
            ),
            "locality_universe": (policy["eligible_locality_universe"] if policy else None),
            "contributing_localities": locality_inputs,
            "observations": [
                self._current_observation(
                    row,
                    observation_method_version=observation_method_version,
                    parser_version=parser["version"],
                )
                for row in selected_observations
            ],
            "source_lineage_ids": lineage_ids,
            "sources": self._current_source_metadata(lineage_ids),
            "scoring_method_version": score["scoring_method_version"],
            "observation_method_versions": [observation_method_version],
            "quality_flags": sorted(
                set(score["quality_flags"])
                | {
                    flag
                    for observation in selected_observations
                    for flag in observation["quality_flags"]
                }
                | set((evidence or {}).get("quality_flags", []))
            ),
        }

    def _legacy_contribution(self, value: dict[str, Any]) -> dict[str, Any]:
        observation_versions = sorted(
            {row["observation_method_version"] for row in value["observations"]}
        )
        source = _source_from_legacy(value["source"])
        return {
            "criterion_id": value["criterion_id"],
            "criterion_name": value["criterion_name"],
            "source_scope": "COUNTRY",
            "result_scope": "COUNTRY",
            "derivation": "DIRECT",
            "score": value["score"],
            "normalized_weight": value["normalized_weight"],
            "contribution": value["contribution"],
            "score_id": next(
                f"legacy-score:{record.criterion['id']}:{record.country['code']}"
                for record in self.legacy.release.records
                if record.criterion["id"] == value["criterion_id"]
                and record.observations[0]["observation_id"]
                == value["observations"][0]["observation_id"]
            ),
            "derived_evidence_id": None,
            "aggregation_policy": None,
            "locality_universe": None,
            "contributing_localities": [],
            "observations": [
                {
                    "observation_id": row["observation_id"],
                    "subject": {
                        "entity_id": "country:"
                        + next(
                            record.country["code"]
                            for record in self.legacy.release.records
                            if record.observations[0]["observation_id"] == row["observation_id"]
                        ),
                        "entity_type": "COUNTRY",
                    },
                    "value": row["value"],
                    "unit": row["unit"],
                    "reference_start": str(row["reference_start"]),
                    "reference_end": str(row["reference_end"]),
                    "source_lineage_id": f"legacy-source:{source['source_id']}",
                    "observation_method_version": row["observation_method_version"],
                    "parser_version": row["parser_version"],
                    "quality_flags": row["quality_flags"],
                }
                for row in value["observations"]
            ],
            "source_lineage_ids": [f"legacy-source:{source['source_id']}"],
            "sources": [source],
            "scoring_method_version": value["scoring_method_version"],
            "observation_method_versions": observation_versions,
            "quality_flags": sorted(
                {
                    flag
                    for observation in value["observations"]
                    for flag in observation["quality_flags"]
                }
            ),
        }

    @staticmethod
    def _coverage_status(legacy_status: str, active_pcc: Sequence[str]) -> str:
        if legacy_status == "COVERAGE_LIMIT_EXCEEDED":
            return "COVERAGE_LIMIT_FALLBACK"
        if not active_pcc:
            return "NO_PARTIAL_CRITERIA_ACTIVE"
        if legacy_status == "FULL_COVERAGE":
            return "FULL_COVERAGE"
        return "PARTIAL_COMPLETE_CASE"

    @staticmethod
    def _coverage_reason(code: str) -> dict[str, str]:
        if code == "COVERAGE_LIMIT_EXCEEDED":
            return _reason(code, severity="WARNING", effect="RANKING_FALLBACK")
        if code.startswith("COUNTRY_EXCLUDED"):
            return _reason(code, severity="WARNING", effect="COUNTRY_EXCLUDED")
        return _reason(code)

    def _current_evidence(
        self,
        *,
        criterion_id: str,
        country_id: str,
        active_ids: set[str],
        contributions: Mapping[str, dict[str, Any]],
    ) -> dict[str, Any]:
        assert self.current is not None
        outcome = next(
            row
            for row in self.current.artifacts.criterion_outcomes
            if row["criterion_id"] == criterion_id and row["subject"]["entity_id"] == country_id
        )
        return {
            "criterion_id": criterion_id,
            "outcome": outcome["outcome"],
            "active_for_ranking": criterion_id in active_ids,
            "reason_codes": outcome["reason_codes"],
            "source_lineage_ids": outcome["source_lineage_ids"],
            "observation_id": outcome["observation_id"],
            "score_id": outcome["score_id"],
            "contribution": contributions.get(criterion_id),
        }

    def _current_country_contributions(
        self,
        country_id: str,
        normalized_weights: Mapping[str, float],
    ) -> dict[str, dict[str, Any]]:
        assert self.current is not None
        outcomes = {
            row["criterion_id"]: row
            for row in self.current.artifacts.criterion_outcomes
            if row["subject"]["entity_id"] == country_id and row["outcome"] == "valid"
        }
        scores = {row["score_id"]: row for row in self.current.artifacts.scores}
        result = {}
        for criterion_id, weight in normalized_weights.items():
            outcome = outcomes.get(criterion_id)
            if outcome is None:
                continue
            score = scores[outcome["score_id"]]
            contribution = Phase5Contribution(
                criterion_id=criterion_id,
                score=score["score"],
                normalized_weight=weight,
                contribution=round(score["score"] * weight, 8),
                observation_id=outcome["observation_id"],
                score_id=outcome["score_id"],
                evidence_kind=outcome["evidence_kind"],
                derived_evidence_id=outcome["derived_evidence_id"],
            )
            result[criterion_id] = self._current_contribution(contribution)
        return result

    def _legacy_outcome(
        self,
        *,
        criterion_id: str,
        country_code: str,
        active_ids: set[str],
        contributions: Mapping[str, dict[str, Any]],
    ) -> dict[str, Any]:
        assert self.legacy is not None
        outcome = next(
            row
            for row in self.legacy.release.outcomes
            if row["criterion_id"] == criterion_id and row["country_code"] == country_code
        )
        source = next(
            (
                row
                for row in self.legacy.release.sources
                if row["source_id"] == outcome["source_id"]
            ),
            None,
        )
        score_id = next(
            (
                f"legacy-score:{criterion_id}:{country_code}"
                for row in self.legacy.release.records
                if row.country["code"] == country_code and row.criterion["id"] == criterion_id
            ),
            None,
        )
        return {
            "criterion_id": criterion_id,
            "outcome": outcome["outcome"],
            "active_for_ranking": criterion_id in active_ids,
            "reason_codes": outcome["reason_codes"],
            "source_lineage_ids": ([f"legacy-source:{source['source_id']}"] if source else []),
            "observation_id": outcome["observation_id"],
            "score_id": score_id,
            "contribution": contributions.get(criterion_id),
        }

    def _legacy_country_contributions(
        self,
        country_code: str,
        normalized_weights: Mapping[str, float],
    ) -> dict[str, dict[str, Any]]:
        assert self.legacy is not None
        result = {}
        for record in self.legacy.release.records:
            criterion_id = record.criterion["id"]
            if record.country["code"] != country_code or criterion_id not in normalized_weights:
                continue
            result[criterion_id] = self._legacy_contribution(
                {
                    "criterion_id": criterion_id,
                    "criterion_name": record.criterion["display_name"],
                    "score": record.score["score"],
                    "normalized_weight": normalized_weights[criterion_id],
                    "contribution": round(
                        record.score["score"] * normalized_weights[criterion_id], 8
                    ),
                    "scoring_method_version": record.score["method_version"],
                    "observations": [
                        {
                            "observation_id": observation["observation_id"],
                            "value": observation["value"],
                            "unit": observation["unit"],
                            "reference_start": observation["reference_start"],
                            "reference_end": observation["reference_end"],
                            "observation_method_version": observation["method_version"],
                            "parser_version": observation["parser_version"],
                            "quality_flags": observation["quality_flags"],
                        }
                        for observation in record.observations
                    ],
                    "source": record.source,
                }
            )
        return result

    def _current_ranking_payload(
        self,
        result: Phase5RankingResult,
    ) -> dict[str, Any]:
        assert self.current is not None
        entities = {row["entity_id"]: row for row in self.current.artifacts.geographic_entities}
        active_ids = set(result.normalized_weights)
        rows = []
        contributions_by_country: dict[str, dict[str, dict[str, Any]]] = {}
        for row in result.rankings:
            country_id = row.country["entity_id"]
            contributions = {
                item.criterion_id: self._current_contribution(item) for item in row.contributions
            }
            contributions_by_country[country_id] = contributions
            entity = entities[country_id]
            rows.append(
                {
                    "rank": row.rank,
                    "country": {
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "display_name": entity["display_name"],
                        "country_codes": entity["country_codes"],
                        "region": None,
                    },
                    "total_score": row.total_score,
                    "contributions": list(contributions.values()),
                    "assessments": {
                        "locality": row.locality_assessment.to_dict(),
                        "profile": row.profile_assessment.to_dict(),
                    },
                }
            )
        excluded = []
        for country_id in result.coverage_assessment.excluded_country_entity_ids:
            entity = entities[country_id]
            locality = result.country_locality_assessments[country_id]
            country_contributions = self._current_country_contributions(
                country_id, result.normalized_weights
            )
            evidence = [
                self._current_evidence(
                    criterion_id=criterion_id,
                    country_id=country_id,
                    active_ids=active_ids,
                    contributions=country_contributions,
                )
                for criterion_id in sorted(active_ids)
            ]
            excluded.append(
                {
                    "country": {
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "display_name": entity["display_name"],
                        "country_codes": entity["country_codes"],
                        "region": None,
                    },
                    "final_aggregate": None,
                    "criterion_evidence": evidence,
                    "locality_assessment": locality.to_dict(),
                    "reasons": [
                        _reason(
                            f"COUNTRY_EXCLUDED:{country_id.removeprefix('country:')}",
                            severity="WARNING",
                            effect="COUNTRY_EXCLUDED",
                        )
                    ],
                }
            )
        coverage = result.coverage_assessment.to_dict()
        coverage.pop("excluded_country_entity_ids")
        coverage["excluded_countries"] = excluded
        return {
            **self._version_fields(),
            "resolved_preference_preset_id": result.resolved_preference_preset_id,
            "normalized_weights": result.normalized_weights,
            "assessments": {
                "coverage": coverage,
                "locality": result.locality_assessment.to_dict(),
                "profile": result.profile_assessment.to_dict(),
            },
            "rankings": rows,
        }

    def _legacy_ranking_payload(
        self,
        result: Any,
        *,
        resolved_preference_preset_id: str | None,
    ) -> dict[str, Any]:
        assert self.legacy is not None
        mapped = ranking_response(result).model_dump(mode="json")
        entities = self._entity_map()
        active_ids = set(mapped["active_fcc_ids"]) | set(mapped["active_pcc_ids"])
        rows = []
        for row in mapped["rankings"]:
            contributions = [self._legacy_contribution(item) for item in row["contributions"]]
            rows.append(
                {
                    "rank": row["rank"],
                    "country": entities[f"country:{row['country_code']}"],
                    "total_score": row["total_score"],
                    "contributions": contributions,
                    "assessments": {
                        "locality": _no_locality_country(),
                        "profile": _no_profile(),
                    },
                }
            )
        excluded = []
        for row in mapped["excluded_countries"]:
            country_code = row["country_code"]
            country_contributions = self._legacy_country_contributions(
                country_code, mapped["normalized_weights"]
            )
            evidence = [
                self._legacy_outcome(
                    criterion_id=criterion_id,
                    country_code=country_code,
                    active_ids=active_ids,
                    contributions=country_contributions,
                )
                for criterion_id in sorted(active_ids)
            ]
            excluded.append(
                {
                    "country": entities[f"country:{country_code}"],
                    "final_aggregate": None,
                    "criterion_evidence": evidence,
                    "locality_assessment": _no_locality_country(),
                    "reasons": [
                        _reason(
                            f"COUNTRY_EXCLUDED:{country_code}",
                            severity="WARNING",
                            effect="COUNTRY_EXCLUDED",
                        )
                    ],
                }
            )
        return {
            **self._version_fields(),
            "resolved_preference_preset_id": resolved_preference_preset_id,
            "normalized_weights": mapped["normalized_weights"],
            "assessments": {
                "coverage": {
                    "status": self._coverage_status(
                        mapped["uncertainty_status"], mapped["active_pcc_ids"]
                    ),
                    "policy_version": mapped["policy_version"],
                    "active_global_core_criterion_ids": mapped["active_fcc_ids"],
                    "active_conditional_criterion_ids": mapped["active_pcc_ids"],
                    "excluded_countries": excluded,
                    "reasons": [self._coverage_reason(code) for code in mapped["reason_codes"]],
                },
                "locality": _no_locality_response(),
                "profile": _no_profile(),
            },
            "rankings": rows,
        }

    def rank(
        self,
        weights: Mapping[str, float] | None,
        *,
        preference_preset_id: str | None,
        top_k: int | None,
    ) -> dict[str, Any]:
        resolved_weights, resolved_preset = self._resolve_weights(weights, preference_preset_id)
        if self.current is not None:
            try:
                result = rank_schema5_release(
                    self.current,
                    resolved_weights,
                    resolved_preference_preset_id=resolved_preset,
                )
            except Phase5RankingError as exc:
                raise InvalidWeightError(str(exc)) from exc
            eligible = len(result.rankings)
            if top_k is not None:
                if top_k > eligible:
                    raise InvalidTopKError(top_k, eligible)
                result = rank_schema5_release(
                    self.current,
                    resolved_weights,
                    resolved_preference_preset_id=resolved_preset,
                    top_k=top_k,
                )
            return self._current_ranking_payload(result)
        assert self.legacy is not None
        if top_k is None:
            preview = self.legacy.rank_with_uncertainty(
                resolved_weights,
                profile_id=None,
            )
            top_k = preview.eligible_country_count
        result = self.legacy.rank_with_uncertainty(resolved_weights, profile_id=None, top_k=top_k)
        return self._legacy_ranking_payload(
            result,
            resolved_preference_preset_id=resolved_preset,
        )

    def _requested_country_ids(self, country_codes: Sequence[str]) -> list[str]:
        known = {row["country_codes"][0]: row["entity_id"] for row in self.catalog()["countries"]}
        unknown = sorted(set(country_codes) - set(known))
        if unknown:
            raise CountryNotFoundError(unknown)
        return [known[code] for code in country_codes]

    def compare(
        self,
        country_codes: Sequence[str],
        weights: Mapping[str, float] | None,
        *,
        preference_preset_id: str | None,
    ) -> dict[str, Any]:
        requested_ids = self._requested_country_ids(country_codes)
        ranking = self.rank(
            weights,
            preference_preset_id=preference_preset_id,
            top_k=None,
        )
        ranked = {row["country"]["entity_id"]: row for row in ranking["rankings"]}
        excluded = {
            row["country"]["entity_id"]: row
            for row in ranking["assessments"]["coverage"]["excluded_countries"]
        }
        countries = []
        for entity_id in requested_ids:
            if entity_id in ranked:
                row = ranked[entity_id]
                countries.append(
                    {
                        "country": row["country"],
                        "rank": row["rank"],
                        "final_aggregate": row["total_score"],
                        "coverage_excluded": False,
                        "assessments": row["assessments"],
                    }
                )
            else:
                row = excluded[entity_id]
                countries.append(
                    {
                        "country": row["country"],
                        "rank": None,
                        "final_aggregate": None,
                        "coverage_excluded": True,
                        "assessments": {
                            "locality": row["locality_assessment"],
                            "profile": ranking["assessments"]["profile"],
                        },
                    }
                )
        active_ids = set(ranking["normalized_weights"])
        criteria = {row["id"]: row for row in self.catalog()["criteria"]}
        contribution_maps = {
            entity_id: {row["criterion_id"]: row for row in ranked[entity_id]["contributions"]}
            for entity_id in ranked
        }
        contribution_maps.update(
            {
                entity_id: {
                    evidence["criterion_id"]: evidence["contribution"]
                    for evidence in excluded_row["criterion_evidence"]
                    if evidence["contribution"] is not None
                }
                for entity_id, excluded_row in excluded.items()
            }
        )
        rows = []
        for criterion_id in sorted(active_ids):
            cells = []
            for entity_id in requested_ids:
                code = entity_id.removeprefix("country:")
                contributions = contribution_maps.get(entity_id, {})
                if self.current is not None:
                    evidence = self._current_evidence(
                        criterion_id=criterion_id,
                        country_id=entity_id,
                        active_ids=active_ids,
                        contributions=contributions,
                    )
                else:
                    evidence = self._legacy_outcome(
                        criterion_id=criterion_id,
                        country_code=code,
                        active_ids=active_ids,
                        contributions=contributions,
                    )
                cells.append(
                    {
                        **evidence,
                        "country": self._entity_map()[entity_id],
                    }
                )
            rows.append(
                {
                    "criterion_id": criterion_id,
                    "criterion_name": criteria[criterion_id]["display_name"],
                    "coverage": criteria[criterion_id]["coverage"],
                    "scope": criteria[criterion_id]["scope"],
                    "cells": cells,
                }
            )
        return {
            **{
                key: ranking[key]
                for key in (
                    "api_contract_version",
                    "release_id",
                    "release_schema_version",
                    "catalog_schema_version",
                    "scoring_method_versions",
                    "resolved_preference_preset_id",
                    "normalized_weights",
                    "assessments",
                )
            },
            "requested_country_entity_ids": requested_ids,
            "countries": countries,
            "criterion_rows": rows,
        }

    def country_details(
        self,
        country_code: str,
        weights: Mapping[str, float] | None,
        *,
        preference_preset_id: str | None,
    ) -> dict[str, Any]:
        comparison = self.compare(
            [country_code, self._comparison_peer(country_code)],
            weights,
            preference_preset_id=preference_preset_id,
        )
        country_id = f"country:{country_code}"
        country = next(
            row for row in comparison["countries"] if row["country"]["entity_id"] == country_id
        )
        catalog = {row["id"]: row for row in self.catalog()["criteria"]}
        evidence = {
            row["criterion_id"]: next(
                cell for cell in row["cells"] if cell["country"]["entity_id"] == country_id
            )
            for row in comparison["criterion_rows"]
        }
        details = []
        for criterion_id in sorted(evidence):
            item = dict(evidence[criterion_id])
            item.pop("country")
            details.append({"criterion": catalog[criterion_id], "evidence": item})
        return {
            **{
                key: comparison[key]
                for key in (
                    "api_contract_version",
                    "release_id",
                    "release_schema_version",
                    "catalog_schema_version",
                    "scoring_method_versions",
                    "resolved_preference_preset_id",
                    "normalized_weights",
                    "assessments",
                )
            },
            "country": country["country"],
            "criteria": details,
        }

    def _comparison_peer(self, country_code: str) -> str:
        codes = [row["country_codes"][0] for row in self.catalog()["countries"]]
        if country_code not in codes:
            raise CountryNotFoundError([country_code])
        return next(code for code in codes if code != country_code)
