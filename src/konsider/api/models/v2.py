"""Strict transport contracts for the Konsider API v2 public surface."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from konsider.api.models.common import ApiModel


def _validate_weights(value):
    if value is None:
        return value
    if not isinstance(value, dict):
        raise ValueError("weights must be an object")
    for criterion_id, weight in value.items():
        if not isinstance(criterion_id, str) or not criterion_id:
            raise ValueError("weight keys must be non-empty criterion IDs")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError("weights must contain numeric values")
    return value


CoverageMode = Literal[
    "GLOBAL_CORE",
    "CONDITIONAL_COMPLETE_CASE",
    "DIAGNOSTIC_ONLY",
]
Outcome = Literal["valid", "missing", "stale", "invalid", "rejected"]
LocalityStatus = Literal[
    "NO_ACTIVE_LOCALITY_CRITERIA",
    "BELOW_ANALYSIS_THRESHOLD",
    "ONE_ACTIVE_LOCALITY_CRITERION",
    "COMMON_LOCALITY_AVAILABLE",
    "PARTIAL_OVERLAP",
    "NO_COMMON_LOCALITY",
    "INSUFFICIENT_LOCALITY_EVIDENCE",
    "MIXED_COUNTRY_RESULTS",
]


class V2VersionedResponse(ApiModel):
    api_contract_version: Literal["konsider-api-2.0"] = "konsider-api-2.0"
    release_id: str
    release_schema_version: str
    catalog_schema_version: str
    scoring_method_versions: list[str]


class V2WeightSelection(ApiModel):
    weights: dict[str, float] | None = None
    preference_preset_id: str | None = Field(default=None, min_length=1)

    _strict_weights = field_validator("weights", mode="before")(_validate_weights)

    @model_validator(mode="after")
    def one_weight_source(self) -> V2WeightSelection:
        if self.weights is not None and self.preference_preset_id is not None:
            raise ValueError("Provide either weights or preference_preset_id, not both.")
        return self


class V2RankingRequest(V2WeightSelection):
    top_k: int = Field(default=10, strict=True, ge=1)


class V2ComparisonRequest(V2WeightSelection):
    country_codes: list[str] = Field(min_length=2, max_length=10)

    @field_validator("country_codes")
    @classmethod
    def normalize_countries(cls, value: list[str]) -> list[str]:
        normalized = [item.upper() for item in value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Comparison country codes must be unique.")
        return normalized


class EntityReferenceResponse(ApiModel):
    entity_id: str
    entity_type: Literal["COUNTRY", "CITY", "METRO", "REGION", "SERVICE_AREA"]


class GeographicEntityResponse(EntityReferenceResponse):
    display_name: str
    country_codes: list[str]
    region: str | None = None


class ScoreRangeResponse(ApiModel):
    minimum: float
    maximum: float


class OutcomeCountsResponse(ApiModel):
    valid: int = Field(ge=0)
    missing: int = Field(ge=0)
    stale: int = Field(ge=0)
    invalid: int = Field(ge=0)
    rejected: int = Field(ge=0)


class CriterionCoverageResponse(ApiModel):
    mode: CoverageMode
    stable_universe_id: str
    stable_country_count: int = Field(ge=1)
    valid_country_count: int = Field(ge=0)
    minimum_valid_country_count: int = Field(ge=0)
    outcome_counts: OutcomeCountsResponse
    activation_threshold: float | None = Field(default=None, ge=0, le=1)
    score_range: ScoreRangeResponse
    source_lineage_ids: list[str]


class CriterionScopeResponse(ApiModel):
    evidence_level: Literal["COUNTRY", "LOCALITY"]
    result_level: Literal["COUNTRY"]
    locality_type: Literal["CITY", "METRO", "REGION", "SERVICE_AREA"] | None
    derivation: Literal["DIRECT", "AGGREGATED_FROM_LOCALITIES"]
    locality_universe_id: str | None
    aggregation_policy_id: str | None
    locality_analysis_threshold: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def valid_derivation(self) -> CriterionScopeResponse:
        locality_fields = (
            self.locality_type,
            self.locality_universe_id,
            self.aggregation_policy_id,
            self.locality_analysis_threshold,
        )
        if self.derivation == "DIRECT":
            if self.evidence_level != "COUNTRY" or any(
                item is not None for item in locality_fields
            ):
                raise ValueError("Direct criteria cannot carry locality-only fields.")
        elif self.evidence_level != "LOCALITY" or any(item is None for item in locality_fields):
            raise ValueError("Locality-derived criteria require complete locality policy identity.")
        return self


class CriterionApplicabilityResponse(ApiModel):
    mode: Literal["UNIVERSAL", "PARAMETERIZED", "FUTURE_PROFILE_REQUIRED"]
    dimensions: list[str]


class SourceMetadataResponse(ApiModel):
    source_id: str
    role: (
        Literal[
            "PRIMARY_OBSERVATION",
            "ENTITY_UNIVERSE",
            "BOUNDARY",
            "AUXILIARY",
            "SCORING_INPUT",
        ]
        | None
    ) = None
    publisher: str | None = None
    source_version: str
    dataset_version: str | None = None
    asset_uri: str | None = None
    checksum: str | None = None
    licence_id: str | None = None
    canonical_page_url: str | None = None
    attribution: str | None = None
    reference_period: str | None = None


class CatalogCriterionV2Response(ApiModel):
    id: str
    display_name: str
    historical_names: list[str]
    category: str
    description: str
    direction: Literal["higher_is_better", "lower_is_better"]
    raw_unit: str
    interpretation: str
    caveats: list[str]
    quality_limitations: list[str]
    ready: bool
    default_enabled: bool
    experimental: bool
    scoring_method_version: str
    coverage: CriterionCoverageResponse
    scope: CriterionScopeResponse
    applicability: CriterionApplicabilityResponse
    sources: list[SourceMetadataResponse]


class PreferencePresetResponse(ApiModel):
    id: str
    name: str
    description: str
    weights: dict[str, float]


class CatalogV2Response(V2VersionedResponse):
    coverage_policy_version: str
    stable_universe_id: str
    countries: list[GeographicEntityResponse]
    criteria: list[CatalogCriterionV2Response]
    preference_presets: list[PreferencePresetResponse]


class HealthV2Response(V2VersionedResponse):
    status: Literal["ok"]
    country_count: int
    enabled_criterion_count: int
    ready_for_rankings: bool


class AssessmentReasonResponse(ApiModel):
    code: str
    severity: Literal["INFO", "WARNING", "BLOCKER"]
    effect: Literal[
        "NONE",
        "ADVISORY",
        "COUNTRY_EXCLUDED",
        "RANKING_FALLBACK",
        "NOT_EVALUATED",
    ]


class CriterionLocalityEvidenceResponse(ApiModel):
    criterion_id: str
    eligible_locality_entity_ids: list[str]
    valid_locality_entity_ids: list[str]
    contributing_locality_entity_ids: list[str]


class CountryLocalityAssessmentResponse(ApiModel):
    status: LocalityStatus
    eligible_locality_entity_ids: list[str]
    valid_locality_entity_ids: list[str]
    contributing_locality_entity_ids: list[str]
    common_locality_entity_ids: list[str]
    best_common_locality_entity_id: str | None
    criterion_evidence: list[CriterionLocalityEvidenceResponse]
    reasons: list[AssessmentReasonResponse]


class ProfileAssessmentResponse(ApiModel):
    status: Literal["NO_PROFILE_CONTEXT"]
    evaluated_dimensions: list[str]
    reasons: list[AssessmentReasonResponse]

    @model_validator(mode="after")
    def explicitly_unevaluated(self) -> ProfileAssessmentResponse:
        if self.evaluated_dimensions:
            raise ValueError("Profile dimensions cannot be evaluated without profile input.")
        if not any(reason.effect == "NOT_EVALUATED" for reason in self.reasons):
            raise ValueError("Profile assessment must explicitly report non-evaluation.")
        return self


class LocalityUniverseReferenceResponse(ApiModel):
    locality_universe_id: str
    locality_universe_version: str


class AggregationPolicyReferenceResponse(ApiModel):
    policy_id: str
    policy_version: str
    method: Literal["TOP_N_MEAN", "BOTTOM_N_MEAN", "ALL_VALID_MEAN"]
    n: int | None


class ObservationEvidenceResponse(ApiModel):
    observation_id: str
    subject: EntityReferenceResponse
    value: float
    unit: str
    reference_start: str
    reference_end: str
    source_lineage_id: str
    observation_method_version: str | None = None
    parser_version: str | None = None
    quality_flags: list[str]


class ContributingLocalityResponse(ApiModel):
    locality: GeographicEntityResponse
    input_score: float
    observation_id: str
    score_id: str


class ContributionV2Response(ApiModel):
    criterion_id: str
    criterion_name: str
    source_scope: Literal["COUNTRY", "LOCALITY"]
    result_scope: Literal["COUNTRY"]
    derivation: Literal["DIRECT", "AGGREGATED_FROM_LOCALITIES"]
    score: float
    normalized_weight: float
    contribution: float
    score_id: str
    derived_evidence_id: str | None
    aggregation_policy: AggregationPolicyReferenceResponse | None
    locality_universe: LocalityUniverseReferenceResponse | None
    contributing_localities: list[ContributingLocalityResponse]
    observations: list[ObservationEvidenceResponse]
    source_lineage_ids: list[str]
    sources: list[SourceMetadataResponse]
    scoring_method_version: str
    observation_method_versions: list[str]
    quality_flags: list[str]

    @model_validator(mode="after")
    def valid_scope_payload(self) -> ContributionV2Response:
        if self.derivation == "DIRECT":
            if (
                self.source_scope != "COUNTRY"
                or self.derived_evidence_id is not None
                or self.aggregation_policy is not None
                or self.locality_universe is not None
                or self.contributing_localities
            ):
                raise ValueError("Direct contributions cannot carry locality derivation evidence.")
        elif (
            self.source_scope != "LOCALITY"
            or self.derived_evidence_id is None
            or self.aggregation_policy is None
            or self.locality_universe is None
            or not self.contributing_localities
        ):
            raise ValueError("Locality-derived contributions require complete locality provenance.")
        return self


class CriterionOutcomeEvidenceResponse(ApiModel):
    criterion_id: str
    outcome: Outcome
    active_for_ranking: bool
    reason_codes: list[str]
    source_lineage_ids: list[str]
    observation_id: str | None
    score_id: str | None
    contribution: ContributionV2Response | None

    @model_validator(mode="after")
    def no_unavailable_contribution(self) -> CriterionOutcomeEvidenceResponse:
        if self.outcome == "valid" and self.active_for_ranking and self.contribution is None:
            raise ValueError("Valid active evidence requires a contribution.")
        if self.outcome != "valid" and self.contribution is not None:
            raise ValueError("Unavailable evidence cannot carry a contribution.")
        return self


class ExcludedCountryV2Response(ApiModel):
    country: GeographicEntityResponse
    final_aggregate: None = None
    criterion_evidence: list[CriterionOutcomeEvidenceResponse]
    locality_assessment: CountryLocalityAssessmentResponse
    reasons: list[AssessmentReasonResponse]


class CoverageAssessmentV2Response(ApiModel):
    status: Literal[
        "NO_PARTIAL_CRITERIA_ACTIVE",
        "FULL_COVERAGE",
        "PARTIAL_COMPLETE_CASE",
        "COVERAGE_LIMIT_FALLBACK",
    ]
    policy_version: str
    active_global_core_criterion_ids: list[str]
    active_conditional_criterion_ids: list[str]
    excluded_countries: list[ExcludedCountryV2Response]
    reasons: list[AssessmentReasonResponse]


class ResponseLocalityAssessmentV2Response(ApiModel):
    status: LocalityStatus
    policy_version: str
    contributing_criterion_ids: list[str]
    analysis_triggered_criterion_ids: list[str]
    below_threshold_criterion_ids: list[str]
    analysis_thresholds: dict[str, float]
    aggregation_policy_ids: list[str]
    reasons: list[AssessmentReasonResponse]


class AssessmentsV2Response(ApiModel):
    coverage: CoverageAssessmentV2Response
    locality: ResponseLocalityAssessmentV2Response
    profile: ProfileAssessmentResponse


class CountryAssessmentsV2Response(ApiModel):
    locality: CountryLocalityAssessmentResponse
    profile: ProfileAssessmentResponse


class RankedCountryV2Response(ApiModel):
    rank: int = Field(ge=1)
    country: GeographicEntityResponse
    total_score: float
    contributions: list[ContributionV2Response]
    assessments: CountryAssessmentsV2Response


class RankingV2Response(V2VersionedResponse):
    resolved_preference_preset_id: str | None
    normalized_weights: dict[str, float]
    assessments: AssessmentsV2Response
    rankings: list[RankedCountryV2Response]


class ComparisonCellV2Response(CriterionOutcomeEvidenceResponse):
    country: GeographicEntityResponse


class ComparisonCriterionRowV2Response(ApiModel):
    criterion_id: str
    criterion_name: str
    coverage: CriterionCoverageResponse
    scope: CriterionScopeResponse
    cells: list[ComparisonCellV2Response]


class ComparedCountryV2Response(ApiModel):
    country: GeographicEntityResponse
    rank: int | None
    final_aggregate: float | None
    coverage_excluded: bool
    assessments: CountryAssessmentsV2Response

    @model_validator(mode="after")
    def excluded_has_no_aggregate(self) -> ComparedCountryV2Response:
        if self.coverage_excluded and (self.rank is not None or self.final_aggregate is not None):
            raise ValueError("Coverage-excluded countries cannot carry a final aggregate.")
        return self


class ComparisonV2Response(V2VersionedResponse):
    resolved_preference_preset_id: str | None
    normalized_weights: dict[str, float]
    assessments: AssessmentsV2Response
    requested_country_entity_ids: list[str]
    countries: list[ComparedCountryV2Response]
    criterion_rows: list[ComparisonCriterionRowV2Response]


class CountryCriterionDetailV2Response(ApiModel):
    criterion: CatalogCriterionV2Response
    evidence: CriterionOutcomeEvidenceResponse


class CountryDetailsV2Response(V2VersionedResponse):
    resolved_preference_preset_id: str | None
    normalized_weights: dict[str, float]
    assessments: AssessmentsV2Response
    country: GeographicEntityResponse
    criteria: list[CountryCriterionDetailV2Response]
