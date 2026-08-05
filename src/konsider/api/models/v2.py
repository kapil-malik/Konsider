"""Strict transport contracts for the Konsider API v2 public surface."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

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


class OpportunityFilterSelection(ApiModel):
    mode: Literal["ALL_REQUIRED"] = "ALL_REQUIRED"
    required_filter_ids: list[str] = Field(default_factory=list)

    @field_validator("required_filter_ids")
    @classmethod
    def unique_canonical_filter_ids(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Opportunity Filter IDs must be unique.")
        if any(not item for item in value):
            raise ValueError("Opportunity Filter IDs must be non-empty.")
        return sorted(value)


class TfcTaxonomyReferenceRequest(ApiModel):
    user_text: str = Field(min_length=1, max_length=200)
    taxonomy_id: str | None = Field(default=None, min_length=1, max_length=80)
    taxonomy_version: str | None = Field(default=None, min_length=1, max_length=40)
    code: str | None = Field(default=None, min_length=1, max_length=80)
    mapping_state: Literal["MAPPED", "UNRESOLVED", "UNKNOWN"]


class TfcMoneyRequest(ApiModel):
    amount: float = Field(ge=0)
    currency: str = Field(pattern=r"^[A-Za-z]{3}$")
    period: Literal["HOURLY", "MONTHLY", "ANNUAL"]

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TfcQualificationRequest(ApiModel):
    level: Literal[
        "SECONDARY",
        "VOCATIONAL",
        "BACHELORS",
        "MASTERS",
        "DOCTORATE",
        "OTHER",
        "UNKNOWN",
    ]
    field: TfcTaxonomyReferenceRequest | None = None
    awarding_country: str | None = Field(default=None, pattern=r"^[A-Za-z]{3}$")
    institution: str | None = Field(default=None, max_length=200)
    completion_year: int | None = Field(default=None, ge=1900, le=2200)
    recognition_state: Literal["NOT_ASSESSED", "RECOGNIZED_BY_SOURCE", "UNRESOLVED"] | None = None

    @field_validator("awarding_country")
    @classmethod
    def normalize_awarding_country(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None


class TfcApplicantContextRequest(ApiModel):
    citizenships: list[str] = Field(default_factory=list, max_length=4)
    country_of_residence: str | None = Field(default=None, pattern=r"^[A-Za-z]{3}$")
    age_years: int | None = Field(default=None, ge=0, le=120)
    occupation: TfcTaxonomyReferenceRequest | None = None
    experience_years: float | None = Field(default=None, ge=0, le=80, multiple_of=0.5)
    qualifications: list[TfcQualificationRequest] = Field(default_factory=list)
    unknown_fields: list[str] = Field(default_factory=list)

    @field_validator("citizenships")
    @classmethod
    def normalize_citizenships(cls, value: list[str]) -> list[str]:
        normalized = [item.upper() for item in value]
        if any(len(item) != 3 or not item.isalpha() for item in normalized):
            raise ValueError("Citizenships must use ISO3 country codes.")
        if len(normalized) != len(set(normalized)):
            raise ValueError("Citizenships must be unique.")
        return sorted(normalized)

    @field_validator("country_of_residence")
    @classmethod
    def normalize_residence(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None


class TfcDependantRequest(ApiModel):
    role: Literal["DEPENDENT_CHILD", "STEPCHILD", "OTHER_DEPENDANT"]
    relocating: bool | None = None
    age_band: Literal[
        "UNDER_18",
        "AGE_18_TO_20",
        "AGE_21_TO_22",
        "AGE_23_TO_25",
        "OVER_25",
        "UNKNOWN",
    ]
    age_years: int | None = Field(default=None, ge=0, le=120)


class TfcHouseholdContextRequest(ApiModel):
    partner_status: Literal["NONE", "SPOUSE", "CIVIL_PARTNER", "UNMARRIED_PARTNER", "UNKNOWN"] = (
        "UNKNOWN"
    )
    partner_accompanying: bool | None = None
    partner_work_intent: Literal["WORK", "STUDY", "NEITHER", "UNKNOWN"] = "UNKNOWN"
    dependants: list[TfcDependantRequest] = Field(default_factory=list, max_length=19)
    unknown_fields: list[str] = Field(default_factory=list)


class TfcJobOfferRequest(ApiModel):
    state: Literal["PRESENT", "ABSENT", "UNKNOWN"]
    role: str | None = Field(default=None, max_length=200)
    employer_region_id: str | None = Field(default=None, max_length=120)
    sponsorship_state: Literal["CONFIRMED", "NOT_CONFIRMED", "NOT_APPLICABLE", "UNKNOWN"] = (
        "UNKNOWN"
    )
    salary: TfcMoneyRequest | None = None


class TfcIntendedStudyRequest(ApiModel):
    institution: TfcTaxonomyReferenceRequest
    qualification_level: Literal[
        "VOCATIONAL", "BACHELORS", "MASTERS", "DOCTORATE", "OTHER", "UNKNOWN"
    ]
    field: TfcTaxonomyReferenceRequest
    duration_months: int = Field(ge=1, le=120)
    mode: Literal["IN_PERSON", "HYBRID", "ONLINE", "UNKNOWN"]
    completion_date: date
    completion_state: Literal["COMPLETED", "CURRENT", "PLANNED"]


class TfcScenarioContextRequest(ApiModel):
    purpose: Literal["WORK", "STUDY", "FAMILY", "EXPLORATION"] = "EXPLORATION"
    target_date: date | None = None
    target_country_codes: list[str] = Field(default_factory=list, max_length=91)
    target_region_ids: list[str] = Field(default_factory=list)
    target_locality_ids: list[str] = Field(default_factory=list)
    job_offer: TfcJobOfferRequest | None = None
    intended_occupation: TfcTaxonomyReferenceRequest | None = None
    intended_study: TfcIntendedStudyRequest | None = None
    primary_route_id: str | None = Field(default=None, max_length=160)
    relocation_composition: Literal[
        "APPLICANT_ONLY",
        "WITH_PARTNER",
        "WITH_DEPENDANTS",
        "WITH_PARTNER_AND_DEPENDANTS",
        "UNKNOWN",
    ] = "UNKNOWN"
    unknown_fields: list[str] = Field(default_factory=list)

    @field_validator("target_country_codes")
    @classmethod
    def normalize_target_countries(cls, value: list[str]) -> list[str]:
        normalized = [item.upper() for item in value]
        if any(len(item) != 3 or not item.isalpha() for item in normalized):
            raise ValueError("Target destinations must use ISO3 country codes.")
        if len(normalized) != len(set(normalized)):
            raise ValueError("Target destinations must be unique.")
        return sorted(normalized)


class TfcAssessmentSelectionRequest(ApiModel):
    tfc_ids: list[str] = Field(default_factory=list, max_length=3)
    mode: Literal["ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH"] = "ASSESS_ONLY"
    profile_context: TfcApplicantContextRequest | None = None
    household_context: TfcHouseholdContextRequest | None = None
    scenario_context: TfcScenarioContextRequest | None = None

    @field_validator("tfc_ids")
    @classmethod
    def unique_tfc_ids(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("TFC IDs must be unique.")
        if any(not item for item in value):
            raise ValueError("TFC IDs must be non-empty.")
        return sorted(value)


class V2WeightSelection(ApiModel):
    weights: dict[str, float] | None = None
    preference_preset_id: str | None = Field(default=None, min_length=1)
    opportunity_filters: OpportunityFilterSelection | None = None
    feasibility: TfcAssessmentSelectionRequest | None = None

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


class OpportunitySourceVintageResponse(ApiModel):
    source_id: str
    source_version: str
    publisher: str
    attribution: str


class OpportunityFilterStateCountsResponse(ApiModel):
    VERIFIED_STRONG_SIGNAL: int = Field(ge=0)
    STRONG_SIGNAL_NOT_ESTABLISHED: int = Field(ge=0)
    INSUFFICIENT_EVIDENCE: int = Field(ge=0)


class OpportunityFilterCoverageResponse(ApiModel):
    assessable_count: int = Field(ge=0)
    state_counts: OpportunityFilterStateCountsResponse
    source_dependency_status: Literal["AVAILABLE", "DEGRADED", "UNAVAILABLE"]


class OpportunityFilterDefinitionV2Response(ApiModel):
    id: str
    display_name: str
    compact_label: str | None
    category: Literal["CAREER", "EDUCATION"]
    meaning: str
    limitations: list[str]
    documentation_ref: str
    coverage: OpportunityFilterCoverageResponse
    source_vintage: list[OpportunitySourceVintageResponse]
    active: bool
    availability: Literal["STAGED", "AVAILABLE", "WITHDRAWN"]
    mode: Literal["ALL_REQUIRED"]
    eligibility_state: Literal["VERIFIED_STRONG_SIGNAL"]
    no_score_impact: Literal[True]


class OpportunityFilterCatalogV2Response(V2VersionedResponse):
    opportunity_release_id: str | None
    state_contract_version: str | None
    evidence_policy_version: str | None
    source_bundle_version: str | None
    mode: Literal["ALL_REQUIRED"]
    no_score_impact: Literal[True]
    definitions: list[OpportunityFilterDefinitionV2Response]


class TfcFieldDefinitionV2Response(ApiModel):
    field_id: str
    data_type: str
    validation: str
    sensitivity: Literal[
        "LOW", "MODERATE_PERSONAL", "MODERATE_CONSEQUENTIAL", "HIGH_PERSONAL", "HIGH_CONSEQUENTIAL"
    ]
    default_retention: Literal["TAB_MEMORY_ONLY", "NEVER_RETAIN_BY_DEFAULT"]
    consumer_tfc_ids: list[str]
    prompt: str
    help_text: str
    may_be_omitted: bool
    may_be_stored_locally: bool


class TfcInputRequirementV2Response(ApiModel):
    field_id: str
    requirement: Literal["ALWAYS_REQUIRED", "CONDITIONALLY_REQUIRED", "OPTIONAL_EXPLANATORY"]
    when_field_id: str | None
    when_equals: str | float | bool | None


class TfcSourceSummaryV2Response(ApiModel):
    source_id: str
    publisher: str
    verified_at: date
    effective_from: date
    effective_to: date | None
    attribution: str


class TfcDefinitionV2Response(ApiModel):
    id: str
    display_name: str
    original_criterion_ids: list[str]
    user_question: str
    check_kind: Literal["RULE_ROUTE_MATCH", "SCENARIO_METRIC"]
    supported_profile_boundary: str
    supported_destination_codes: list[str]
    input_requirements: list[TfcInputRequirementV2Response]
    limitations: list[str]
    filter_capability: Literal["ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH_ALLOWED"]
    applicable_purposes: list[Literal["WORK", "STUDY", "FAMILY", "EXPLORATION"]]
    refresh_cadence: str
    policy_id: str
    policy_version: str
    source_summary: list[TfcSourceSummaryV2Response]
    effective_from: date
    stale_after: date
    sort_order: int = Field(ge=1)
    no_score_impact: Literal[True]


class TfcCatalogV2Response(V2VersionedResponse):
    tfc_release_id: str
    tfc_release_schema_version: str
    candidate_status: Literal["draft"]
    activation_authorized: Literal[False]
    available_modes: list[Literal["ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH"]]
    default_mode: Literal["ASSESS_ONLY"]
    selection_is_explicit: Literal[True]
    persisted_server_side: Literal[False]
    no_score_impact: Literal[True]
    definitions: list[TfcDefinitionV2Response]
    field_registry: list[TfcFieldDefinitionV2Response]


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


class OpportunityFilterEvidenceSummaryResponse(ApiModel):
    filter_id: str
    state: Literal[
        "VERIFIED_STRONG_SIGNAL",
        "STRONG_SIGNAL_NOT_ESTABLISHED",
        "INSUFFICIENT_EVIDENCE",
    ]
    passes: bool
    confidence_band: Literal["HIGH", "MEDIUM", "LOW"]
    establishing_route_ids: list[str]
    reason_codes: list[str]
    reference_period: str | None
    source_ids: list[str]
    limitations: list[str]
    documentation_ref: str


class CountryOpportunityAssessmentV2Response(ApiModel):
    evaluated: bool
    passes: bool | None
    filter_evidence: list[OpportunityFilterEvidenceSummaryResponse]

    @model_validator(mode="after")
    def evaluation_state_is_explicit(self) -> CountryOpportunityAssessmentV2Response:
        if self.evaluated and self.passes is None:
            raise ValueError("Evaluated Opportunity Filters require an explicit pass state.")
        if not self.evaluated and (self.passes is not None or self.filter_evidence):
            raise ValueError(
                "Unevaluated Opportunity Filters cannot carry evidence or a pass state."
            )
        return self


class OpportunityPerFilterAssessmentV2Response(ApiModel):
    filter_id: str
    input_country_count: int = Field(ge=0)
    passing_country_count: int = Field(ge=0)
    state_counts: OpportunityFilterStateCountsResponse


class OpportunityExcludedCountsResponse(ApiModel):
    STRONG_SIGNAL_NOT_ESTABLISHED: int = Field(ge=0)
    INSUFFICIENT_EVIDENCE: int = Field(ge=0)


class OpportunityExcludedCountryV2Response(ApiModel):
    country_code: str = Field(pattern=r"^[A-Z]{3}$")
    base_rank: int = Field(ge=1)
    exclusion_category: Literal["STRONG_SIGNAL_NOT_ESTABLISHED", "INSUFFICIENT_EVIDENCE"]
    failing_filter_evidence: list[OpportunityFilterEvidenceSummaryResponse]


class OpportunityAssessmentV2Response(ApiModel):
    status: Literal["NO_FILTERS_ACTIVE", "FILTERS_APPLIED", "NO_COUNTRIES_MATCH"]
    mode: Literal["ALL_REQUIRED"]
    active_filter_ids: list[str]
    input_ranked_country_count: int = Field(ge=0)
    passing_country_count: int = Field(ge=0)
    excluded_country_count: int = Field(ge=0)
    excluded_counts_by_state: OpportunityExcludedCountsResponse
    per_filter: list[OpportunityPerFilterAssessmentV2Response]
    excluded_countries: list[OpportunityExcludedCountryV2Response]
    opportunity_release_id: str | None
    evidence_policy_version: str | None
    source_bundle_version: str | None
    strict_filter_explanation: str
    no_score_impact: Literal[True]


class ResponseLocalityAssessmentV2Response(ApiModel):
    status: LocalityStatus
    policy_version: str
    contributing_criterion_ids: list[str]
    analysis_triggered_criterion_ids: list[str]
    below_threshold_criterion_ids: list[str]
    analysis_thresholds: dict[str, float]
    aggregation_policy_ids: list[str]
    reasons: list[AssessmentReasonResponse]


class TfcWarningV2Response(ApiModel):
    code: str
    tfc_id: str | None
    country_code: str | None
    record_ids: list[str]


class TfcConditionEvaluationV2Response(ApiModel):
    condition_id: str
    field_ids: list[str]
    status: Literal["MET", "UNMET", "UNKNOWN", "NOT_APPLICABLE"]
    blocking: bool


class TfcRouteEvaluationV2Response(ApiModel):
    route_id: str
    route_name: str
    jurisdiction_id: str
    classification: Literal["MATCH", "CONDITIONAL", "NO_MATCH"]
    conditions: list[TfcConditionEvaluationV2Response]
    source_ids: list[str]
    effective_from: date
    effective_to: date | None
    evidence_quality: Literal["HIGH", "MEDIUM", "LOW"]


class TfcRouteResultV2Response(ApiModel):
    result_type: Literal["ROUTE_RULE"]
    match_classification: Literal[
        "SUPPORTED_ROUTE_MATCH", "CONDITIONAL_ROUTE_MATCH", "NO_SUPPORTED_ROUTE_MATCH"
    ]
    routes: list[TfcRouteEvaluationV2Response]
    matched_route_ids: list[str]
    route_inventory_complete: bool
    legal_impossibility_disclaimer: str


class TfcMetricComponentV2Response(ApiModel):
    component_id: str
    field_id: str
    status: Literal["EVALUATED", "MISSING", "INCOMPATIBLE_UNIT"]
    contribution_minimum: float | None
    contribution_maximum: float | None
    unit: str


class TfcMetricResultV2Response(ApiModel):
    result_type: Literal["SCENARIO_METRIC"]
    metric_id: str
    formula_type: str
    value: float | None
    minimum: float
    maximum: float
    unit: str
    currency: str | None
    period: Literal["NONE", "HOURLY", "MONTHLY", "ANNUAL"]
    components: list[TfcMetricComponentV2Response]
    assumptions: list[str]
    rounding: dict[str, Any]
    locality_id: str | None
    source_ids: list[str]
    effective_from: date
    effective_to: date | None
    evidence_quality: Literal["HIGH", "MEDIUM", "LOW"]


class TfcOutcomeV2Response(ApiModel):
    tfc_id: str
    country_code: str = Field(pattern=r"^[A-Z]{3}$")
    common_status: Literal[
        "EVALUATED",
        "INPUT_REQUIRED",
        "DESTINATION_EVIDENCE_INSUFFICIENT",
        "UNSUPPORTED",
        "NOT_APPLICABLE",
        "EVALUATION_ERROR",
    ]
    reason_codes: list[str]
    input_required_fields: list[str]
    result: TfcRouteResultV2Response | TfcMetricResultV2Response | None
    warnings: list[TfcWarningV2Response]


class TfcCountryAssessmentV2Response(ApiModel):
    country_code: str = Field(pattern=r"^[A-Z]{3}$")
    base_rank: int = Field(ge=1)
    filtered_rank: int | None = Field(default=None, ge=1)
    affinity_score_before: float
    affinity_score_after: float
    no_change_affinity: Literal[True]
    outcomes: list[TfcOutcomeV2Response]


class TfcProfileContextSummaryV2Response(ApiModel):
    provided_layers: list[Literal["applicant", "household", "scenario"]]
    unknown_field_ids: list[str]
    returned_profile_values: Literal[False]
    persisted_server_side: Literal[False]


class TfcBaseRankingReferenceV2Response(ApiModel):
    release_id: str
    country_count: int = Field(ge=0)
    ordering_checksum: str


class TfcSnapshotMetadataV2Response(ApiModel):
    snapshot_id: str
    tfc_release_id: str
    policy_versions: dict[str, str]
    source_versions: dict[str, str]
    effective_profile_context_hash: str
    evaluation_date: date
    base_ranking_reference: TfcBaseRankingReferenceV2Response
    persisted_server_side: Literal[False]


class TfcStatusCountsV2Response(ApiModel):
    EVALUATED: int = Field(ge=0)
    INPUT_REQUIRED: int = Field(ge=0)
    DESTINATION_EVIDENCE_INSUFFICIENT: int = Field(ge=0)
    UNSUPPORTED: int = Field(ge=0)
    NOT_APPLICABLE: int = Field(ge=0)
    EVALUATION_ERROR: int = Field(ge=0)


class TfcAssessmentV2Response(ApiModel):
    schema_version: Literal["tfc-engine-assessment-1.0"]
    profile_context_status: Literal[
        "NO_PROFILE_CONTEXT", "PARTIAL_PROFILE_CONTEXT", "COMPLETE_PROFILE_CONTEXT"
    ]
    execution_status: Literal["NO_TFC_SELECTED", "NOT_EXECUTED_NO_CONTEXT", "EXECUTED"]
    filter_mode: Literal["ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH"]
    selected_tfc_ids: list[str]
    input_required_fields: list[str]
    status_counts: TfcStatusCountsV2Response
    matched_route_count: int = Field(ge=0)
    metric_result_count: int = Field(ge=0)
    no_change_affinity: Literal[True]
    warnings: list[TfcWarningV2Response]
    countries: list[TfcCountryAssessmentV2Response]
    profile_context_summary: TfcProfileContextSummaryV2Response
    snapshot: TfcSnapshotMetadataV2Response | None


class AssessmentsV2Response(ApiModel):
    coverage: CoverageAssessmentV2Response
    locality: ResponseLocalityAssessmentV2Response
    profile: ProfileAssessmentResponse
    opportunity: OpportunityAssessmentV2Response
    feasibility: TfcAssessmentV2Response | None = None


class CountryAssessmentsV2Response(ApiModel):
    locality: CountryLocalityAssessmentResponse
    profile: ProfileAssessmentResponse
    opportunity: CountryOpportunityAssessmentV2Response
    feasibility: TfcCountryAssessmentV2Response | None = None


class RankedCountryV2Response(ApiModel):
    rank: int = Field(ge=1)
    base_rank: int = Field(ge=1)
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
    base_rank: int | None
    final_aggregate: float | None
    coverage_excluded: bool
    opportunity_excluded: bool
    assessments: CountryAssessmentsV2Response

    @model_validator(mode="after")
    def excluded_has_no_aggregate(self) -> ComparedCountryV2Response:
        if self.coverage_excluded and (
            self.rank is not None
            or self.base_rank is not None
            or self.final_aggregate is not None
            or self.opportunity_excluded
        ):
            raise ValueError("Coverage-excluded countries cannot carry a final aggregate.")
        if self.opportunity_excluded and (
            self.coverage_excluded
            or self.rank is not None
            or self.base_rank is None
            or self.final_aggregate is None
        ):
            raise ValueError(
                "Opportunity-excluded countries retain base rank and score but no filtered rank."
            )
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
    opportunity_filters: list[OpportunityFilterEvidenceSummaryResponse]
    feasibility: TfcCountryAssessmentV2Response | None = None
