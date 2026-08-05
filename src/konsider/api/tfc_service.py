"""Public, stateless API adapter for an immutable Phase 7 TFC release."""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from konsider.domain.tfc_assessment import TfcAssessmentEngine, TfcAssessmentError
from konsider.exceptions import (
    InvalidProfileContextError,
    TfcReleaseUnavailableError,
    TfcFilterNotAllowedError,
    UnknownTfcError,
    UnsupportedTaxonomyVersionError,
)
from konsider.ingestion.tfc_first_wave import FIRST_WAVE_TFC_IDS
from konsider.ingestion.tfc_release import (
    LoadedTfcRelease,
    TfcCandidateReleaseRepository,
    TfcReleaseError,
)

SUPPORTED_TAXONOMIES = {"isco08": {"2008"}}

FIELD_REGISTRY = {
    "applicant.citizenships": (
        "array<iso3-country-code>",
        "Up to four unique ISO 3166-1 alpha-3 country codes.",
        "HIGH_PERSONAL",
        "Citizenship(s)",
        "Used only where a route rule distinguishes citizenship.",
    ),
    "applicant.occupation": (
        "taxonomy-reference",
        "User text is required; optional mapped codes must use an advertised taxonomy version.",
        "MODERATE_CONSEQUENTIAL",
        "Current occupation",
        "Plain text may be supplied when no reliable taxonomy mapping is available.",
    ),
    "applicant.qualifications": (
        "array<qualification>",
        "Declared qualification level; recognition remains explicit and is never inferred.",
        "HIGH_CONSEQUENTIAL",
        "Qualifications",
        "List qualifications relevant to the selected route check.",
    ),
    "household.dependants": (
        "array<dependant>",
        "Declared dependant role and age band; relocating may be true, false, or unknown.",
        "HIGH_PERSONAL",
        "Dependants",
        "An empty list means no dependants were declared; omission means unknown.",
    ),
    "household.partner_status": (
        "enum",
        "NONE, SPOUSE, CIVIL_PARTNER, UNMARRIED_PARTNER, or UNKNOWN.",
        "HIGH_PERSONAL",
        "Partner status",
        "Used only for the family accompaniment check.",
    ),
    "scenario.job_offer": (
        "job-offer",
        "Offer state is PRESENT, ABSENT, or UNKNOWN; salary is optional.",
        "HIGH_CONSEQUENTIAL",
        "Job offer",
        "False or absent facts are not converted into unknown values.",
    ),
    "scenario.intended_study": (
        "intended-study",
        "Institution, qualification, field, duration, mode, completion date, and state.",
        "HIGH_CONSEQUENTIAL",
        "Intended study",
        "Planned study remains provisional and does not establish provider eligibility.",
    ),
    "scenario.primary_route_id": (
        "string",
        "A route ID from the frozen first-wave route inventory.",
        "MODERATE_CONSEQUENTIAL",
        "Primary route",
        "Required only to assess whether family members fit a supported primary route.",
    ),
    "scenario.target_country_codes": (
        "array<iso3-country-code>",
        "Unique ISO 3166-1 alpha-3 destination codes.",
        "LOW",
        "Target destinations",
        "Assessment output is still returned for every ranked destination.",
    ),
    "scenario.target_date": (
        "date",
        "ISO 8601 calendar date.",
        "LOW",
        "Target date",
        "Selects the rule version effective on the declared scenario date.",
    ),
}


class TfcApiService:
    """Load and assess one immutable release-6 overlay."""

    def __init__(
        self,
        release: LoadedTfcRelease | None,
        engine: TfcAssessmentEngine | None,
        unavailable_reason: str | None = None,
    ) -> None:
        self.release = release
        self.engine = engine
        self.unavailable_reason = unavailable_reason

    @classmethod
    def unavailable(cls, reason: str = "TFC candidate is not configured.") -> TfcApiService:
        return cls(None, None, reason)

    @classmethod
    def from_candidate(
        cls, candidate_path: Path | str, active_manifest: Mapping[str, Any]
    ) -> TfcApiService:
        path = Path(candidate_path)
        try:
            release = TfcCandidateReleaseRepository(path.parent).load(path)
        except (OSError, ValueError, TfcReleaseError) as exc:
            raise TfcReleaseUnavailableError("The staged TFC candidate is unavailable.") from exc
        manifest = release.manifest
        expected_base = {
            "release_id": active_manifest["release_id"],
            "schema_version": active_manifest["schema_version"],
            "release_checksum": active_manifest["release_checksum"],
        }
        definition_ids = tuple(row["tfc_id"] for row in release.artifacts.catalog["definitions"])
        if (
            manifest["status"] != "draft"
            or manifest["synthetic"]
            or manifest["activation_authorized"]
            or manifest["base_release"] != expected_base
            or set(definition_ids) != set(FIRST_WAVE_TFC_IDS)
        ):
            raise TfcReleaseUnavailableError(
                "The staged TFC candidate does not match the authorized API boundary."
            )
        engine = TfcAssessmentEngine(
            release.artifacts,
            active_release_id=active_manifest["release_id"],
            tfc_release_id=manifest["release_id"],
        )
        return cls(release, engine)

    @classmethod
    def from_published(
        cls, release: LoadedTfcRelease, active_manifest: Mapping[str, Any]
    ) -> TfcApiService:
        manifest = release.manifest
        expected_base = {
            "release_id": active_manifest["release_id"],
            "schema_version": active_manifest["schema_version"],
            "release_checksum": active_manifest["release_checksum"],
        }
        definition_ids = tuple(row["tfc_id"] for row in release.artifacts.catalog["definitions"])
        if (
            manifest["status"] != "published"
            or manifest["synthetic"]
            or not manifest["activation_authorized"]
            or manifest["base_release"] != expected_base
            or release.artifacts.catalog["activation_status"] != "ACTIVE"
            or set(definition_ids) != set(FIRST_WAVE_TFC_IDS)
        ):
            raise TfcReleaseUnavailableError(
                "The active TFC release does not match the authorized API boundary."
            )
        engine = TfcAssessmentEngine(
            release.artifacts,
            active_release_id=active_manifest["release_id"],
            tfc_release_id=manifest["release_id"],
        )
        return cls(release, engine)

    def _require_available(self) -> tuple[LoadedTfcRelease, TfcAssessmentEngine]:
        if self.release is None or self.engine is None:
            raise TfcReleaseUnavailableError("The active TFC release is unavailable.")
        return self.release, self.engine

    def catalog(self, version_fields: Mapping[str, Any]) -> dict[str, Any]:
        release, _ = self._require_available()
        artifacts = release.artifacts
        policies = {row["tfc_id"]: row for row in artifacts.policy_bundles["policies"]}
        sources = {row["source_id"]: row for row in artifacts.source_legal_manifest["sources"]}
        definitions = []
        consumers: dict[str, list[str]] = {field_id: [] for field_id in FIELD_REGISTRY}
        for order, definition in enumerate(artifacts.catalog["definitions"], start=1):
            tfc_id = definition["tfc_id"]
            for field_id in definition["input_field_ids"]:
                consumers.setdefault(field_id, []).append(tfc_id)
            records = [row for row in artifacts.rule_evidence if row.get("tfc_id") == tfc_id]
            rule_records = [
                row for row in records if row["record_type"] in {"ROUTE_RULE", "METRIC_FORMULA"}
            ]
            source_ids = sorted(
                {
                    ref["source_id"]
                    for row in rule_records
                    for ref in row.get("source_references", [])
                }
            )
            effective_dates = [row["effective_period"]["effective_from"] for row in rule_records]
            stale_dates = [row["effective_period"]["stale_after"] for row in rule_records]
            definitions.append(
                {
                    "id": tfc_id,
                    "display_name": definition["name"],
                    "original_criterion_ids": definition["original_criterion_ids"],
                    "user_question": definition["user_question"],
                    "check_kind": definition["result_family"],
                    "supported_profile_boundary": definition["supported_profile_boundary"],
                    "supported_destination_codes": definition["supported_destination_codes"],
                    "input_requirements": definition["input_requirements"],
                    "limitations": definition["public_limitations"],
                    "filter_capability": definition["filter_capability"],
                    "applicable_purposes": definition["applicable_purposes"],
                    "refresh_cadence": definition["refresh_cadence"],
                    "policy_id": definition["policy_id"],
                    "policy_version": policies[tfc_id]["policy_version"],
                    "source_summary": [
                        {
                            "source_id": source_id,
                            "publisher": sources[source_id]["publisher"],
                            "verified_at": sources[source_id]["verified_at"],
                            "effective_from": sources[source_id]["effective_from"],
                            "effective_to": sources[source_id]["effective_to"],
                            "attribution": sources[source_id]["attribution"],
                        }
                        for source_id in source_ids
                    ],
                    "effective_from": min(effective_dates),
                    "stale_after": min(stale_dates),
                    "sort_order": order * 10,
                    "no_score_impact": True,
                }
            )
        field_registry = []
        for field_id in sorted(consumers):
            data_type, validation, sensitivity, prompt, help_text = FIELD_REGISTRY[field_id]
            field_registry.append(
                {
                    "field_id": field_id,
                    "data_type": data_type,
                    "validation": validation,
                    "sensitivity": sensitivity,
                    "default_retention": "NEVER_RETAIN_BY_DEFAULT",
                    "consumer_tfc_ids": sorted(consumers[field_id]),
                    "prompt": prompt,
                    "help_text": help_text,
                    "may_be_omitted": True,
                    "may_be_stored_locally": True,
                }
            )
        return {
            **version_fields,
            "tfc_release_id": release.manifest["release_id"],
            "tfc_release_schema_version": release.manifest["schema_version"],
            "release_status": release.manifest["status"],
            "activation_authorized": release.manifest["activation_authorized"],
            "available_modes": ["ASSESS_ONLY", "REQUIRE_SUPPORTED_MATCH"],
            "default_mode": "ASSESS_ONLY",
            "selection_is_explicit": True,
            "persisted_server_side": False,
            "no_score_impact": True,
            "definitions": definitions,
            "field_registry": field_registry,
        }

    def _validate_taxonomies(self, context: Mapping[str, Any]) -> None:
        invalid: set[str] = set()

        def check(field_id: str, value: Any) -> None:
            if not isinstance(value, Mapping) or value.get("mapping_state") != "MAPPED":
                return
            taxonomy_id = value.get("taxonomy_id")
            taxonomy_version = value.get("taxonomy_version")
            if taxonomy_version not in SUPPORTED_TAXONOMIES.get(str(taxonomy_id), set()):
                invalid.add(field_id)

        applicant = context.get("applicant", {})
        scenario = context.get("scenario", {})
        check("applicant.occupation", applicant.get("occupation"))
        for index, qualification in enumerate(applicant.get("qualifications", [])):
            check(f"applicant.qualifications[{index}].field", qualification.get("field"))
        check("scenario.intended_occupation", scenario.get("intended_occupation"))
        study = scenario.get("intended_study")
        if isinstance(study, Mapping):
            check("scenario.intended_study.institution", study.get("institution"))
            check("scenario.intended_study.field", study.get("field"))
        if invalid:
            raise UnsupportedTaxonomyVersionError(sorted(invalid))

    def assess(
        self,
        payload: Mapping[str, Any],
        *,
        selected_tfc_ids: Sequence[str],
        mode: str,
        context: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        release, engine = self._require_available()
        unknown = sorted(set(selected_tfc_ids) - set(engine.definitions))
        if unknown:
            raise UnknownTfcError(unknown)
        non_filterable = sorted(
            tfc_id
            for tfc_id in selected_tfc_ids
            if engine.definitions[tfc_id]["filter_capability"] != "REQUIRE_SUPPORTED_MATCH_ALLOWED"
        )
        if mode == "REQUIRE_SUPPORTED_MATCH" and non_filterable:
            raise TfcFilterNotAllowedError(non_filterable)
        if context is not None:
            self._validate_taxonomies(context)
        evaluation_date = (
            str(context.get("scenario", {}).get("target_date"))
            if context is not None and context.get("scenario", {}).get("target_date") is not None
            else release.artifacts.validation["validated_as_of"]
        )
        try:
            run = engine.assess_ranking_payload(
                payload,
                context=context,
                selected_tfc_ids=selected_tfc_ids,
                evaluation_date=evaluation_date,
                filter_mode=mode,
            )
        except TfcAssessmentError as exc:
            raise InvalidProfileContextError("The supplied profile context is invalid.") from exc

        assessment = copy.deepcopy(run.assessment)
        provided_layers = (
            sorted(layer for layer in ("applicant", "household", "scenario") if layer in context)
            if context is not None
            else []
        )
        unknown_fields = sorted(
            {
                f"{layer}.{field_id}"
                for layer in provided_layers
                for field_id in context[layer].get("unknown_fields", [])
            }
        )
        assessment["profile_context_summary"] = {
            "provided_layers": provided_layers,
            "unknown_field_ids": unknown_fields,
            "returned_profile_values": False,
            "persisted_server_side": False,
        }
        snapshot = run.snapshot
        assessment["snapshot"] = (
            {
                "snapshot_id": snapshot["snapshot_id"],
                "tfc_release_id": snapshot["tfc_release_id"],
                "policy_versions": snapshot["policy_versions"],
                "source_versions": snapshot["source_versions"],
                "effective_profile_context_hash": snapshot["effective_profile_context_hash"],
                "evaluation_date": snapshot["evaluation_date"],
                "base_ranking_reference": snapshot["base_ranking_reference"],
                "persisted_server_side": False,
            }
            if snapshot is not None
            else None
        )
        result = copy.deepcopy(run.payload)
        result.setdefault("assessments", {})["feasibility"] = assessment
        by_country = {row["country_code"]: row for row in assessment["countries"]}
        for row in result.get("rankings", []):
            code = row["country"]["country_codes"][0]
            if code in by_country:
                row["assessments"]["feasibility"] = by_country[code]
        return result
