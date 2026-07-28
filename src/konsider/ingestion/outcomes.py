"""Deterministic schema-4 criterion outcomes derived from retained source bytes."""

from __future__ import annotations

from collections.abc import Iterable

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.models import (
    CriterionOutcome,
    MetricObservation,
    RawArtifact,
    SourceRegistration,
)
from konsider.ingestion.parsers import (
    classify_hci_plus_schooling_outcomes,
    classify_ilostat_job_market_outcomes,
)
from konsider.repositories.raw_artifact_repository import RawArtifactRepository

OUTCOME_CLASSIFIERS = {
    "ilostat_job_market_opportunity": classify_ilostat_job_market_outcomes,
    "world_bank_hci_plus_schooling": classify_hci_plus_schooling_outcomes,
}


def build_criterion_outcomes(
    *,
    registrations: Iterable[SourceRegistration],
    artifacts: Iterable[RawArtifact],
    observations: Iterable[MetricObservation],
    raw_repository: RawArtifactRepository,
    criterion_ids: Iterable[str],
    country_codes: tuple[str, ...] = COUNTRY_CODES,
) -> list[CriterionOutcome]:
    """Build exactly one explicit outcome for every criterion-country pair."""

    registrations_by_criterion: dict[str, SourceRegistration] = {}
    for registration in registrations:
        if registration.criterion_id in registrations_by_criterion:
            raise ValueError(
                "Schema-4 outcome construction currently requires one registered source per "
                f"criterion: {registration.criterion_id}."
            )
        registrations_by_criterion[registration.criterion_id] = registration
    artifacts_by_source: dict[str, list[RawArtifact]] = {}
    for artifact in artifacts:
        artifacts_by_source.setdefault(artifact.source_id, []).append(artifact)
    observation_by_pair = {(item.metric_id, item.country_code): item for item in observations}

    outcomes = []
    for criterion_id in sorted(criterion_ids):
        registration = registrations_by_criterion[criterion_id]
        source_artifacts = artifacts_by_source.get(registration.source_id, [])
        attempted_at = max(
            (item.retrieved_at for item in source_artifacts),
            default="1970-01-01T00:00:00+00:00",
        )
        classifier = OUTCOME_CLASSIFIERS.get(registration.parser)
        classified = (
            classifier(
                source_artifacts,
                [raw_repository.load(item) for item in source_artifacts],
            )
            if classifier
            else {}
        )
        for country_code in country_codes:
            observation = observation_by_pair.get((criterion_id, country_code))
            if observation is not None:
                outcomes.append(
                    CriterionOutcome(
                        criterion_id=criterion_id,
                        country_code=country_code,
                        outcome="valid",
                        source_id=registration.source_id,
                        attempted_at=attempted_at,
                        observation_id=observation.observation_id,
                    )
                )
                continue
            outcome, reason_codes = classified.get(
                country_code,
                ("missing", ("COV_SOURCE_RECORD_MISSING",)),
            )
            outcomes.append(
                CriterionOutcome(
                    criterion_id=criterion_id,
                    country_code=country_code,
                    outcome=outcome,
                    source_id=registration.source_id,
                    attempted_at=attempted_at,
                    reason_codes=reason_codes,
                )
            )
    return outcomes
