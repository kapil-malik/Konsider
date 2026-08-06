"""Transport contracts for the uniform-display-metadata API v3 surface."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from konsider.api.models.common import ApiModel
from konsider.api.models.v2 import (
    AssessmentsV2Response,
    CatalogCriterionV2Response,
    CatalogV2Response,
    ComparedCountryV2Response,
    ComparisonCellV2Response,
    ComparisonCriterionRowV2Response,
    ComparisonV2Response,
    ContributionV2Response,
    CountryAssessmentsV2Response,
    CountryCriterionDetailV2Response,
    CountryDetailsV2Response,
    CoverageAssessmentV2Response,
    CriterionOutcomeEvidenceResponse,
    ExcludedCountryV2Response,
    HealthV2Response,
    OpportunityFilterCatalogV2Response,
    OpportunityFilterDefinitionV2Response,
    RankedCountryV2Response,
    RankingV2Response,
    TfcCatalogV2Response,
    TfcDefinitionV2Response,
)


class V3ContractMixin(ApiModel):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"


class CatalogCriterionV3Response(CatalogCriterionV2Response):
    display_name: str = Field(alias="displayName")
    compact_name: str | None = Field(alias="compactName")
    section_id: str | None = Field(alias="sectionId")
    category: str | None = Field(alias="sectionName")
    sort_order: int = Field(alias="sortOrder", ge=0)


class CatalogV3Response(CatalogV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    criteria: list[CatalogCriterionV3Response]


class DisplaySectionV3Response(ApiModel):
    section_id: str = Field(alias="sectionId")
    section_name: str = Field(alias="sectionName")
    sort_order: int = Field(alias="sortOrder", ge=0)


class OpportunityFilterDefinitionV3Response(OpportunityFilterDefinitionV2Response):
    display_name: str = Field(alias="displayName")
    compact_label: str | None = Field(alias="compactName")
    section_id: str | None = Field(alias="sectionId")
    category: str | None = Field(alias="sectionName")
    sort_order: int = Field(alias="sortOrder", ge=0)


class OpportunityFilterCatalogV3Response(OpportunityFilterCatalogV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    sections: list[DisplaySectionV3Response]
    definitions: list[OpportunityFilterDefinitionV3Response]


class TfcDefinitionV3Response(TfcDefinitionV2Response):
    display_name: str = Field(alias="displayName")
    compact_name: str | None = Field(alias="compactName")
    section_id: str | None = Field(alias="sectionId")
    section_name: str | None = Field(alias="sectionName")
    sort_order: int = Field(alias="sortOrder", ge=0)


class TfcCatalogV3Response(TfcCatalogV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    definitions: list[TfcDefinitionV3Response]


class HealthV3Response(HealthV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"


class ContributionV3Response(ContributionV2Response):
    criterion_name: str = Field(alias="displayName")


class CriterionOutcomeEvidenceV3Response(CriterionOutcomeEvidenceResponse):
    contribution: ContributionV3Response | None


class ExcludedCountryV3Response(ExcludedCountryV2Response):
    criterion_evidence: list[CriterionOutcomeEvidenceV3Response]


class CoverageAssessmentV3Response(CoverageAssessmentV2Response):
    excluded_countries: list[ExcludedCountryV3Response]


class AssessmentsV3Response(AssessmentsV2Response):
    coverage: CoverageAssessmentV3Response


class RankedCountryV3Response(RankedCountryV2Response):
    contributions: list[ContributionV3Response]
    assessments: CountryAssessmentsV2Response


class RankingV3Response(RankingV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    assessments: AssessmentsV3Response
    rankings: list[RankedCountryV3Response]


class ComparisonCellV3Response(ComparisonCellV2Response):
    contribution: ContributionV3Response | None


class ComparisonCriterionRowV3Response(ComparisonCriterionRowV2Response):
    criterion_name: str = Field(alias="displayName")
    cells: list[ComparisonCellV3Response]


class ComparedCountryV3Response(ComparedCountryV2Response):
    assessments: CountryAssessmentsV2Response


class ComparisonV3Response(ComparisonV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    assessments: AssessmentsV3Response
    countries: list[ComparedCountryV3Response]
    criterion_rows: list[ComparisonCriterionRowV3Response]


class CountryCriterionDetailV3Response(CountryCriterionDetailV2Response):
    criterion: CatalogCriterionV3Response
    evidence: CriterionOutcomeEvidenceV3Response


class CountryDetailsV3Response(CountryDetailsV2Response):
    api_contract_version: Literal["konsider-api-3.0"] = "konsider-api-3.0"
    assessments: AssessmentsV3Response
    criteria: list[CountryCriterionDetailV3Response]
