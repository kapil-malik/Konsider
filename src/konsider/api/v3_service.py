"""API v3 adapter over the release-backed recommendation service."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from konsider.api.v2_service import RecommendationService
from konsider.ingestion.current_release import CurrentReleaseError

API_CONTRACT_VERSION = "konsider-api-3.0"


def _uniform_display(definition: Mapping[str, Any]) -> dict[str, Any]:
    required = ("id", "displayName", "compactName", "sectionId", "sectionName", "sortOrder")
    missing = [field for field in required if field not in definition]
    if missing:
        raise CurrentReleaseError(
            f"API v3 requires a uniform display snapshot; missing fields: {missing}."
        )
    return {field: definition[field] for field in required}


def _v3_tree(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if key == "api_contract_version":
                result[key] = API_CONTRACT_VERSION
            elif key == "criterion_name":
                result["displayName"] = _v3_tree(child)
            else:
                result[key] = _v3_tree(child)
        return result
    if isinstance(value, list):
        return [_v3_tree(child) for child in value]
    return value


class RecommendationServiceV3:
    """Expose only uniform catalog display fields while reusing ranking semantics."""

    def __init__(self, delegate: RecommendationService) -> None:
        self.delegate = delegate

    def health(self) -> dict[str, Any]:
        return _v3_tree(self.delegate.health())

    def catalog(self) -> dict[str, Any]:
        payload = copy.deepcopy(self.delegate.catalog())
        raw = {
            row["id"]: row for row in self.delegate.release.artifacts.consumer_catalog["criteria"]
        }
        for definition in payload["criteria"]:
            definition.pop("display_name", None)
            definition.pop("category", None)
            definition.update(_uniform_display(raw[definition["id"]]))
        return _v3_tree(payload)

    def opportunity_filter_catalog(self) -> dict[str, Any]:
        payload = copy.deepcopy(self.delegate.opportunity_filter_catalog())
        catalog = self.delegate.opportunity_filters.catalog
        raw = {row["id"]: row for row in catalog.get("definitions", [])}
        for definition in payload["definitions"]:
            for field in ("display_name", "compact_label", "category"):
                definition.pop(field, None)
            definition.update(_uniform_display(raw[definition["id"]]))
        payload["sections"] = copy.deepcopy(catalog.get("sections", []))
        return _v3_tree(payload)

    def tfc_catalog(self) -> dict[str, Any]:
        payload = copy.deepcopy(self.delegate.tfc_catalog())
        release = self.delegate.tfc_service.release
        if release is None:
            raise CurrentReleaseError("API v3 requires an active TFC overlay.")
        raw = {row["id"]: row for row in release.artifacts.catalog["definitions"]}
        for definition in payload["definitions"]:
            definition.pop("display_name", None)
            definition.pop("sort_order", None)
            definition.update(_uniform_display(raw[definition["id"]]))
        return _v3_tree(payload)

    def rank(self, *args, **kwargs) -> dict[str, Any]:
        payload = self.delegate.rank(*args, **kwargs)
        for row in payload["rankings"]:
            row["contributions"] = [
                {
                    "criterion_id": contribution["criterion_id"],
                    "criterion_name": contribution["criterion_name"],
                    "derivation": contribution["derivation"],
                    "score": contribution["score"],
                    "normalized_weight": contribution["normalized_weight"],
                    "contribution": contribution["contribution"],
                    "contributing_localities": contribution["contributing_localities"],
                }
                for contribution in row["contributions"]
            ]
        return _v3_tree(payload)

    def compare(self, *args, **kwargs) -> dict[str, Any]:
        return _v3_tree(self.delegate.compare(*args, **kwargs))

    def country_details(self, *args, **kwargs) -> dict[str, Any]:
        payload = _v3_tree(self.delegate.country_details(*args, **kwargs))
        raw = {
            row["id"]: row for row in self.delegate.release.artifacts.consumer_catalog["criteria"]
        }
        for detail in payload["criteria"]:
            definition = detail["criterion"]
            definition.pop("display_name", None)
            definition.pop("category", None)
            definition.update(_uniform_display(raw[definition["id"]]))
        return payload
