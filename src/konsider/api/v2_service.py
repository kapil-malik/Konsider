"""Application-facing service for the final structured API contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from konsider.api.opportunity_filter_service import OpportunityFilterService
from konsider.api.tfc_service import TfcApiService
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


def _display_name(definition: Mapping[str, Any]) -> str:
    return str(definition.get("displayName", definition.get("display_name")))


def _criterion_sort_key(definition: Mapping[str, Any]) -> tuple[int, str]:
    sort_order = definition.get("sortOrder", definition.get("sort_order"))
    return (
        int(sort_order) if sort_order is not None else 2**31 - 1,
        str(definition["id"]),
    )


def _reason(
    code: str,
    *,
    severity: str = "INFO",
    effect: str = "NONE",
) -> dict[str, str]:
    return {"code": code, "severity": severity, "effect": effect}


def _source_metadata(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source["source_id"],
        "role": source["role"],
        "publisher": source.get("publisher"),
        "source_version": source["source_version"],
        "dataset_version": source.get("dataset_version"),
        "asset_uri": source["asset_uri"],
        "checksum": source["checksum"],
        "licence_id": source["licence_id"],
        "canonical_page_url": source.get("canonical_page_url"),
        "attribution": source.get("attribution"),
        "reference_period": source.get("reference_period"),
    }


class RecommendationService:
    """Expose the structured contract from one validated schema-current release."""

    def __init__(
        self,
        release: LoadedCurrentRelease,
        opportunity_filters: OpportunityFilterService | None = None,
        tfc_service: TfcApiService | None = None,
    ) -> None:
        self.release = release
        self.opportunity_filters = opportunity_filters or OpportunityFilterService.empty()
        self.tfc_service = tfc_service or TfcApiService.unavailable()

    @property
    def release_id(self) -> str:
        return self.release.manifest["release_id"]

    def _version_fields(self) -> dict[str, Any]:
        catalog = self.release.artifacts.consumer_catalog
        return {
            "api_contract_version": API_CONTRACT_VERSION,
            "release_id": self.release.manifest["release_id"],
            "release_schema_version": self.release.manifest["schema_version"],
            "catalog_schema_version": catalog["schema_version"],
            "scoring_method_versions": list(self.release.manifest["scoring_method_versions"]),
        }

    def health(self) -> dict[str, Any]:
        artifacts = self.release.artifacts
        return {
            **self._version_fields(),
            "status": "ok",
            "country_count": sum(
                row["entity_type"] == "COUNTRY" for row in artifacts.geographic_entities
            ),
            "enabled_criterion_count": sum(
                row["ready"] for row in artifacts.consumer_catalog["criteria"]
            ),
            "ready_for_rankings": bool(self.release.validation["product_ready"]),
        }

    def tfc_catalog(self) -> dict[str, Any]:
        return self.tfc_service.catalog(self._version_fields())

    def _catalog_criterion(self, criterion: dict[str, Any]) -> dict[str, Any]:
        lineages = {row["lineage_id"]: row for row in self.release.artifacts.source_lineages}
        sources = [
            _source_metadata(source)
            for lineage_id in criterion["coverage"]["source_lineage_ids"]
            for source in lineages[lineage_id]["sources"]
        ]
        result = {**criterion, "sources": sources}
        if "displayName" in result:
            result["display_name"] = result.pop("displayName")
            result["category"] = result.pop("sectionName") or ""
            for field in ("compactName", "sectionId", "sortOrder"):
                result.pop(field, None)
        return result

    def catalog(self) -> dict[str, Any]:
        catalog = self.release.artifacts.consumer_catalog
        criteria_by_id = {row["id"]: row for row in catalog["criteria"]}
        entities = {row["entity_id"]: row for row in self.release.artifacts.geographic_entities}
        countries = [
            {
                "entity_id": row["entity_id"],
                "entity_type": row["entity_type"],
                "display_name": row["display_name"],
                "country_codes": row["country_codes"],
                "region": row.get("region"),
            }
            for row in sorted(entities.values(), key=lambda item: item["entity_id"])
            if row["entity_type"] == "COUNTRY"
        ]
        outcomes_by_country: dict[str, list[dict[str, Any]]] = {}
        for outcome in self.release.artifacts.criterion_outcomes:
            outcomes_by_country.setdefault(outcome["subject"]["entity_id"], []).append(
                {
                    "criterion_id": outcome["criterion_id"],
                    "outcome": outcome["outcome"],
                    "reason_codes": outcome["reason_codes"],
                }
            )
        return {
            **self._version_fields(),
            "coverage_policy_version": catalog["coverage_policy_version"],
            "stable_universe_id": catalog["stable_universe_id"],
            "countries": countries,
            "country_coverage": [
                {
                    "country": country,
                    "criteria": sorted(
                        outcomes_by_country.get(country["entity_id"], []),
                        key=lambda item: _criterion_sort_key(criteria_by_id[item["criterion_id"]]),
                    ),
                }
                for country in countries
            ],
            "criteria": [
                self._catalog_criterion(row)
                for row in sorted(catalog["criteria"], key=_criterion_sort_key)
            ],
            "preference_presets": catalog["preference_presets"],
        }

    def opportunity_filter_catalog(self) -> dict[str, Any]:
        return {**self._version_fields(), **self.opportunity_filters.catalog_payload()}

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

    def _source_metadata(self, lineage_ids: Sequence[str]) -> list[dict[str, Any]]:
        lineages = {row["lineage_id"]: row for row in self.release.artifacts.source_lineages}
        return [
            _source_metadata(source)
            for lineage_id in lineage_ids
            for source in lineages[lineage_id]["sources"]
        ]

    def _observation(
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

    def _contribution(
        self,
        contribution: Phase5Contribution,
    ) -> dict[str, Any]:
        artifacts = self.release.artifacts
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
                            "region": entity.get("region"),
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
            "criterion_name": _display_name(criterion),
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
                self._observation(
                    row,
                    observation_method_version=observation_method_version,
                    parser_version=parser["version"],
                )
                for row in selected_observations
            ],
            "source_lineage_ids": lineage_ids,
            "sources": self._source_metadata(lineage_ids),
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

    def _evidence(
        self,
        *,
        criterion_id: str,
        country_id: str,
        active_ids: set[str],
        contributions: Mapping[str, dict[str, Any]],
    ) -> dict[str, Any]:
        outcome = next(
            row
            for row in self.release.artifacts.criterion_outcomes
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

    def _country_contributions(
        self,
        country_id: str,
        normalized_weights: Mapping[str, float],
    ) -> dict[str, dict[str, Any]]:
        outcomes = {
            row["criterion_id"]: row
            for row in self.release.artifacts.criterion_outcomes
            if row["subject"]["entity_id"] == country_id and row["outcome"] == "valid"
        }
        scores = {row["score_id"]: row for row in self.release.artifacts.scores}
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
            result[criterion_id] = self._contribution(contribution)
        return result

    def _ranking_payload(
        self,
        result: Phase5RankingResult,
    ) -> dict[str, Any]:
        entities = {row["entity_id"]: row for row in self.release.artifacts.geographic_entities}
        active_ids = set(result.normalized_weights)
        raw_criteria = {
            row["id"]: row for row in self.release.artifacts.consumer_catalog["criteria"]
        }
        rows = []
        contributions_by_country: dict[str, dict[str, dict[str, Any]]] = {}
        for row in result.rankings:
            country_id = row.country["entity_id"]
            contributions = {
                item.criterion_id: self._contribution(item) for item in row.contributions
            }
            contributions_by_country[country_id] = contributions
            entity = entities[country_id]
            rows.append(
                {
                    "rank": row.rank,
                    "base_rank": row.rank,
                    "country": {
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "display_name": entity["display_name"],
                        "country_codes": entity["country_codes"],
                        "region": entity.get("region"),
                    },
                    "total_score": row.total_score,
                    "contributions": [
                        contributions[criterion_id]
                        for criterion_id in sorted(
                            contributions,
                            key=lambda item: _criterion_sort_key(raw_criteria[item]),
                        )
                    ],
                    "assessments": {
                        "locality": row.locality_assessment.to_dict(),
                        "profile": row.profile_assessment.to_dict(),
                        "opportunity": {
                            "evaluated": False,
                            "passes": None,
                            "filter_evidence": [],
                        },
                    },
                }
            )
        excluded = []
        for country_id in result.coverage_assessment.excluded_country_entity_ids:
            entity = entities[country_id]
            locality = result.country_locality_assessments[country_id]
            country_contributions = self._country_contributions(
                country_id, result.normalized_weights
            )
            evidence = [
                self._evidence(
                    criterion_id=criterion_id,
                    country_id=country_id,
                    active_ids=active_ids,
                    contributions=country_contributions,
                )
                for criterion_id in sorted(
                    active_ids,
                    key=lambda item: _criterion_sort_key(raw_criteria[item]),
                )
            ]
            excluded.append(
                {
                    "country": {
                        "entity_id": entity["entity_id"],
                        "entity_type": entity["entity_type"],
                        "display_name": entity["display_name"],
                        "country_codes": entity["country_codes"],
                        "region": entity.get("region"),
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

    def _apply_opportunity_filters(
        self,
        payload: dict[str, Any],
        filter_ids: Sequence[str],
        top_k: int | None,
    ) -> dict[str, Any]:
        canonical = payload["rankings"]
        assessment, country_results = self.opportunity_filters.assess_ranked_countries(
            canonical, filter_ids
        )
        selected = tuple(assessment["active_filter_ids"])
        survivors = []
        for row in canonical:
            country_code = row["country"]["country_codes"][0]
            result = country_results[country_code]
            row["base_rank"] = result["base_rank"]
            row["assessments"]["opportunity"] = {
                "evaluated": True,
                "passes": result["passes"],
                "filter_evidence": result["filter_evidence"],
            }
            if result["passes"]:
                row["rank"] = result["filtered_rank"]
                survivors.append(row)

        if top_k is not None:
            if top_k > len(canonical):
                raise InvalidTopKError(top_k, len(canonical))
            if not selected:
                survivors = survivors[:top_k]
            elif len(survivors) > top_k:
                boundary_score = survivors[top_k - 1]["total_score"]
                survivors = [row for row in survivors if row["total_score"] >= boundary_score]
        payload["rankings"] = survivors
        payload["assessments"]["opportunity"] = assessment
        return payload

    def rank(
        self,
        weights: Mapping[str, float] | None,
        *,
        preference_preset_id: str | None,
        top_k: int | None,
        opportunity_filter_ids: Sequence[str] = (),
        feasibility: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_weights, resolved_preset = self._resolve_weights(weights, preference_preset_id)
        try:
            result = rank_schema5_release(
                self.release,
                resolved_weights,
                resolved_preference_preset_id=resolved_preset,
            )
        except Phase5RankingError as exc:
            raise InvalidWeightError(str(exc)) from exc
        payload = self._apply_opportunity_filters(
            self._ranking_payload(result), opportunity_filter_ids, top_k
        )
        if feasibility is None or not feasibility["tfc_ids"]:
            return payload
        return self.tfc_service.assess(
            payload,
            selected_tfc_ids=feasibility["tfc_ids"],
            mode=feasibility["mode"],
            context=feasibility["context"],
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
        opportunity_filter_ids: Sequence[str] = (),
        feasibility: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        requested_ids = self._requested_country_ids(country_codes)
        ranking = self.rank(
            weights,
            preference_preset_id=preference_preset_id,
            top_k=None,
            opportunity_filter_ids=opportunity_filter_ids,
            feasibility=feasibility,
        )
        canonical = (
            ranking
            if not opportunity_filter_ids
            else self.rank(
                weights,
                preference_preset_id=preference_preset_id,
                top_k=None,
                opportunity_filter_ids=(),
                feasibility=feasibility,
            )
        )
        ranked = {row["country"]["entity_id"]: row for row in ranking["rankings"]}
        canonical_ranked = {row["country"]["entity_id"]: row for row in canonical["rankings"]}
        excluded = {
            row["country"]["entity_id"]: row
            for row in canonical["assessments"]["coverage"]["excluded_countries"]
        }
        countries = []
        for entity_id in requested_ids:
            if entity_id in ranked:
                row = ranked[entity_id]
                countries.append(
                    {
                        "country": row["country"],
                        "rank": row["rank"],
                        "base_rank": row["base_rank"],
                        "final_aggregate": row["total_score"],
                        "coverage_excluded": False,
                        "opportunity_excluded": False,
                        "assessments": row["assessments"],
                    }
                )
            elif entity_id in canonical_ranked:
                row = canonical_ranked[entity_id]
                country_code = row["country"]["country_codes"][0]
                summaries = [
                    self.opportunity_filters.evidence_summary(filter_id, country_code)
                    for filter_id in sorted(opportunity_filter_ids)
                ]
                countries.append(
                    {
                        "country": row["country"],
                        "rank": None,
                        "base_rank": row["base_rank"],
                        "final_aggregate": row["total_score"],
                        "coverage_excluded": False,
                        "opportunity_excluded": True,
                        "assessments": {
                            "locality": row["assessments"]["locality"],
                            "profile": row["assessments"]["profile"],
                            "opportunity": {
                                "evaluated": True,
                                "passes": False,
                                "filter_evidence": summaries,
                            },
                            **(
                                {"feasibility": row["assessments"]["feasibility"]}
                                if "feasibility" in row["assessments"]
                                else {}
                            ),
                        },
                    }
                )
            else:
                row = excluded[entity_id]
                countries.append(
                    {
                        "country": row["country"],
                        "rank": None,
                        "base_rank": None,
                        "final_aggregate": None,
                        "coverage_excluded": True,
                        "opportunity_excluded": False,
                        "assessments": {
                            "locality": row["locality_assessment"],
                            "profile": ranking["assessments"]["profile"],
                            "opportunity": {
                                "evaluated": False,
                                "passes": None,
                                "filter_evidence": [],
                            },
                        },
                    }
                )
        active_ids = set(ranking["normalized_weights"])
        criteria = {row["id"]: row for row in self.catalog()["criteria"]}
        contribution_maps = {
            entity_id: {row["criterion_id"]: row for row in country["contributions"]}
            for entity_id, country in canonical_ranked.items()
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
        raw_criteria = {
            row["id"]: row for row in self.release.artifacts.consumer_catalog["criteria"]
        }
        for criterion_id in sorted(
            active_ids,
            key=lambda item: _criterion_sort_key(raw_criteria[item]),
        ):
            cells = []
            for entity_id in requested_ids:
                contributions = contribution_maps.get(entity_id, {})
                evidence = self._evidence(
                    criterion_id=criterion_id,
                    country_id=entity_id,
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
                    "criterion_name": _display_name(criteria[criterion_id]),
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
        opportunity_filter_ids: Sequence[str] = (),
        feasibility: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        comparison = self.compare(
            [country_code, self._comparison_peer(country_code)],
            weights,
            preference_preset_id=preference_preset_id,
            opportunity_filter_ids=opportunity_filter_ids,
            feasibility=feasibility,
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
        raw_criteria = {
            row["id"]: row for row in self.release.artifacts.consumer_catalog["criteria"]
        }
        for criterion_id in sorted(
            evidence,
            key=lambda item: _criterion_sort_key(raw_criteria[item]),
        ):
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
            "opportunity_filters": country["assessments"]["opportunity"]["filter_evidence"],
            **(
                {"feasibility": country["assessments"]["feasibility"]}
                if "feasibility" in country["assessments"]
                else {}
            ),
        }

    def _comparison_peer(self, country_code: str) -> str:
        codes = [row["country_codes"][0] for row in self.catalog()["countries"]]
        if country_code not in codes:
            raise CountryNotFoundError([country_code])
        return next(code for code in codes if code != country_code)
