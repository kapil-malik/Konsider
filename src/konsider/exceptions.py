"""Typed application errors shared by non-HTTP and HTTP consumers."""

from __future__ import annotations

from konsider.domain.scoring import ScoringError


class RecommendationError(ValueError):
    """Base class for expected recommendation request failures."""


class WeightRequestError(RecommendationError, ScoringError):
    """Base class for expected weight-selection failures."""


class UnknownCriterionError(WeightRequestError):
    def __init__(self, criterion_ids: list[str]) -> None:
        self.criterion_ids = criterion_ids
        super().__init__(f"Unknown criterion ID(s): {criterion_ids}")


class CriterionNotReadyError(WeightRequestError):
    def __init__(self, criterion_ids: list[str]) -> None:
        self.criterion_ids = criterion_ids
        super().__init__(f"Non-ready criterion ID(s): {criterion_ids}")


class InvalidWeightError(WeightRequestError):
    pass


class InvalidTopKError(RecommendationError):
    def __init__(self, top_k: object, eligible_count: int) -> None:
        self.top_k = top_k
        self.eligible_count = eligible_count
        super().__init__(f"top_k must be between 1 and {eligible_count}.")


class InvalidProfileSelectionError(RecommendationError):
    pass


class ProfileNotFoundError(RecommendationError):
    def __init__(self, profile_id: str) -> None:
        self.profile_id = profile_id
        super().__init__(f"Unknown profile ID: {profile_id}")


class PreferencePresetNotFoundError(RecommendationError):
    def __init__(self, preference_preset_id: str) -> None:
        self.preference_preset_id = preference_preset_id
        super().__init__(f"Unknown preference preset ID: {preference_preset_id}")


class CountryNotFoundError(RecommendationError):
    def __init__(self, country_codes: list[str]) -> None:
        self.country_codes = country_codes
        super().__init__(f"Unknown country code(s): {country_codes}")


class InvalidComparisonError(RecommendationError):
    pass


class UnknownOpportunityFilterError(RecommendationError):
    def __init__(self, filter_ids: list[str]) -> None:
        self.filter_ids = filter_ids
        super().__init__(f"Unknown Opportunity Filter ID(s): {filter_ids}")


class OpportunityFilterNotActiveError(RecommendationError):
    def __init__(self, filter_ids: list[str]) -> None:
        self.filter_ids = filter_ids
        super().__init__(f"Inactive Opportunity Filter ID(s): {filter_ids}")


class InvalidOpportunityFilterSelectionError(RecommendationError):
    pass


class RankingIntegrityError(RecommendationError):
    """Raised when a validated release cannot satisfy one ranking invariant."""
