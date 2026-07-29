"""Read-only adapter for validated, immutable published releases."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from konsider.contracts import (
    ContractError,
    UnsupportedContractError,
    require_supported_version,
    validate_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class PublishedReleaseError(ValueError):
    """Raised when a published release cannot safely be consumed."""


class UnsupportedReleaseContractError(PublishedReleaseError):
    """Raised when a release or catalog uses an unsupported contract major."""


@dataclass(frozen=True)
class PublishedMetricRecord:
    country: dict[str, Any]
    criterion: dict[str, Any]
    score: dict[str, Any]
    observations: tuple[dict[str, Any], ...]
    source: dict[str, Any]


@dataclass(frozen=True)
class PublishedRelease:
    release_id: str
    manifest: dict[str, Any]
    validation: dict[str, Any]
    catalog: dict[str, Any]
    sources: tuple[dict[str, Any], ...]
    outcomes: tuple[dict[str, Any], ...]
    records: tuple[PublishedMetricRecord, ...]
    diagnostic_read_only: bool = False

    @property
    def enabled_criterion_ids(self) -> tuple[str, ...]:
        return tuple(sorted(item["id"] for item in self.catalog["criteria"] if item["ready"]))

    @property
    def available_criterion_ids(self) -> tuple[str, ...]:
        return tuple(sorted(item["id"] for item in self.catalog["criteria"]))


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublishedReleaseError(f"Required published-release file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublishedReleaseError(f"Malformed JSON in {path}: {exc}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise PublishedReleaseError(f"Required published-release file is missing: {path}") from exc
    rows = []
    for line_number, line in enumerate(lines, 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise PublishedReleaseError(f"Malformed JSONL in {path}:{line_number}: {exc}") from exc
    return rows


class PublishedReleaseRepository:
    """Load one active release without calling any upstream data source."""

    def __init__(
        self,
        release_root: Path | str | None = None,
        catalog_path: Path | str | None = None,
        active_release_path: Path | str | None = None,
    ) -> None:
        self.release_root = Path(release_root or PROJECT_ROOT / "data" / "releases").resolve()
        self.catalog_path = Path(catalog_path).resolve() if catalog_path is not None else None
        if active_release_path is not None:
            self.active_release_path = Path(active_release_path)
        else:
            legacy_pointer = self.release_root / "legacy-active.json"
            self.active_release_path = (
                legacy_pointer if legacy_pointer.exists() else self.release_root / "active.json"
            )

    def load_active(self, *, diagnostic_read_only: bool = False) -> PublishedRelease:
        try:
            pointer = _read_json(self.active_release_path)
            release_major = require_supported_version(
                pointer.get("schema_version"), "konsider-release"
            )
            release_catalog_snapshot = (
                PROJECT_ROOT / "data" / "catalogs" / "releases" / f"{pointer['release_id']}.json"
            ).resolve()
            catalog_path = self.catalog_path or (
                release_catalog_snapshot
                if release_catalog_snapshot.exists()
                else (
                    PROJECT_ROOT
                    / "data"
                    / "catalogs"
                    / f"consumer-catalog-{2 if release_major == 4 else 1}.0.json"
                ).resolve()
            )
            schema_generation = 2 if release_major == 4 else 1
            validate_contract(
                pointer,
                "active-release-pointer",
                context="active release pointer",
                schema_generation=schema_generation,
            )
            release_path = self.release_root / pointer["release_id"]
            manifest = _read_json(release_path / "manifest.json")
            manifest_major = require_supported_version(
                manifest.get("schema_version"), "konsider-release"
            )
            if manifest_major != release_major:
                raise PublishedReleaseError("Active pointer and manifest schema majors disagree.")
            validate_contract(
                manifest,
                "release-manifest",
                context="release manifest",
                schema_generation=schema_generation,
            )
            if manifest["release_id"] != pointer["release_id"]:
                raise PublishedReleaseError("Active pointer and manifest release IDs disagree.")
            if manifest["status"] != "published":
                raise PublishedReleaseError("The active release is not published.")
            if not manifest["validation_summary"]["structural_passed"]:
                raise PublishedReleaseError("The active release failed structural validation.")
            self._verify_checksums(release_path, manifest)

            validation = _read_json(release_path / "validation.json")
            validation_major = require_supported_version(
                validation.get("schema_version"), "validation"
            )
            if validation_major != release_major:
                raise PublishedReleaseError("Release and validation schema majors disagree.")
            validate_contract(
                validation,
                "validation-report",
                context="validation report",
                schema_generation=schema_generation,
            )
            sources = _read_json(release_path / "sources.json")
            observations = _read_jsonl(release_path / "observations.jsonl")
            scores = _read_jsonl(release_path / "scores.jsonl")
            outcomes = _read_jsonl(release_path / "attempts.jsonl") if release_major == 4 else []
            for index, source in enumerate(sources):
                validate_contract(
                    source, "source-registration", context=f"source registration {index}"
                )
            for index, observation in enumerate(observations):
                validate_contract(observation, "metric-observation", context=f"observation {index}")
            for index, score in enumerate(scores):
                validate_contract(score, "metric-score", context=f"score {index}")
            for index, outcome in enumerate(outcomes):
                validate_contract(
                    outcome,
                    "criterion-outcome",
                    context=f"criterion outcome {index}",
                    schema_generation=2,
                )

            catalog = _read_json(catalog_path)
            catalog_major = require_supported_version(
                catalog.get("schema_version"), "consumer-catalog"
            )
            expected_catalog_major = 2 if release_major == 4 else 1
            if catalog_major != expected_catalog_major:
                raise PublishedReleaseError(
                    "Consumer catalog and release schema generations disagree."
                )
            validate_contract(
                catalog,
                "consumer-catalog",
                context="consumer catalog",
                schema_generation=schema_generation,
            )
            records = self._join(
                manifest,
                validation,
                catalog,
                sources,
                observations,
                scores,
                outcomes,
                release_major,
            )
        except UnsupportedContractError as exc:
            raise UnsupportedReleaseContractError(str(exc)) from exc
        except ContractError as exc:
            raise PublishedReleaseError(str(exc)) from exc

        if not diagnostic_read_only:
            records = tuple(record for record in records if record.criterion["ready"])
        return PublishedRelease(
            release_id=manifest["release_id"],
            manifest=manifest,
            validation=validation,
            catalog=catalog,
            sources=tuple(sources),
            outcomes=tuple(outcomes),
            records=records,
            diagnostic_read_only=diagnostic_read_only,
        )

    @staticmethod
    def _verify_checksums(release_path: Path, manifest: dict[str, Any]) -> None:
        for filename, expected in manifest["file_checksums"].items():
            path = release_path / filename
            try:
                actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            except FileNotFoundError as exc:
                raise PublishedReleaseError(f"Checksummed file is missing: {path}") from exc
            if actual != expected:
                raise PublishedReleaseError(
                    f"Checksum mismatch for {filename}: expected {expected}, got {actual}."
                )
        release_checksum = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(
                    manifest["file_checksums"], sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest()
        )
        if release_checksum != manifest["release_checksum"]:
            raise PublishedReleaseError("Manifest release checksum does not match file checksums.")

    @staticmethod
    def _join(
        manifest,
        validation,
        catalog,
        sources,
        observations,
        scores,
        outcomes,
        release_major,
    ):
        if (
            len(observations) != manifest["observation_count"]
            or len(scores) != manifest["score_count"]
        ):
            raise PublishedReleaseError("Manifest counts do not match consumer payload counts.")
        if validation["observation_count"] != len(observations) or validation["score_count"] != len(
            scores
        ):
            raise PublishedReleaseError("Validation counts do not match consumer payload counts.")

        countries = {item["code"]: item for item in catalog["countries"]}
        criteria = {item["id"]: item for item in catalog["criteria"]}
        if len(countries) != len(catalog["countries"]) or len(criteria) != len(catalog["criteria"]):
            raise PublishedReleaseError(
                "Consumer catalog contains duplicate country or criterion IDs."
            )
        if set(manifest["criteria"]) != set(criteria):
            raise PublishedReleaseError(
                "Consumer catalog criteria do not match the published release."
            )
        if catalog["compatible_release_schema_major"] != release_major:
            raise PublishedReleaseError(
                "Consumer catalog declares an incompatible release schema major."
            )
        readiness = validation["criterion_readiness"]
        catalog_readiness = {key: value["ready"] for key, value in criteria.items()}
        if (
            readiness != manifest["validation_summary"]["criterion_readiness"]
            or readiness != catalog_readiness
        ):
            raise PublishedReleaseError(
                "Criterion readiness is inconsistent across release artifacts."
            )
        if any(item["default_enabled"] != item["ready"] for item in criteria.values()):
            raise PublishedReleaseError(
                "Catalog default-enabled state must exactly follow readiness."
            )
        valid_pairs = None
        if release_major == 4:
            manifest_coverage = manifest["criterion_coverage"]
            validation_coverage = validation["criterion_coverage_details"]
            catalog_coverage = {
                criterion_id: item["coverage"] for criterion_id, item in criteria.items()
            }
            if not (
                manifest_coverage == validation_coverage == catalog_coverage
                and manifest["coverage_policy_version"]
                == validation["coverage_policy_version"]
                == catalog["coverage_policy_version"]
            ):
                raise PublishedReleaseError(
                    "Criterion coverage metadata is inconsistent across release artifacts."
                )
            for criterion_id, item in manifest_coverage.items():
                if item["criterion_id"] != criterion_id:
                    raise PublishedReleaseError(
                        f"Coverage criterion ID disagrees for {criterion_id}."
                    )
                declared_versions = {
                    source_id: manifest["source_versions"].get(source_id)
                    for source_id in item["source_versions"]
                }
                if item["source_versions"] != declared_versions:
                    raise PublishedReleaseError(
                        f"Coverage source versions disagree for {criterion_id}."
                    )
            if (
                manifest["country_count"] != len(countries)
                or set(manifest["country_codes"]) != set(countries)
                or validation["stable_country_count"] != len(countries)
                or validation["stable_universe_id"] != catalog["stable_universe_id"]
            ):
                raise PublishedReleaseError(
                    "Stable country universe is inconsistent across release artifacts."
                )
            if (
                len(outcomes) != manifest["attempt_count"]
                or len(outcomes) != validation["attempt_count"]
            ):
                raise PublishedReleaseError("Attempt counts do not match the criterion outcomes.")
            outcome_by_pair = {}
            for outcome in outcomes:
                pair = (outcome["country_code"], outcome["criterion_id"])
                if pair in outcome_by_pair:
                    raise PublishedReleaseError(f"Duplicate criterion outcome: {pair[0]}/{pair[1]}")
                outcome_coverage = manifest_coverage.get(outcome["criterion_id"])
                if (
                    outcome_coverage is None
                    or outcome["source_id"] not in outcome_coverage["source_versions"]
                ):
                    raise PublishedReleaseError(f"Criterion outcome source disagrees for {pair}.")
                outcome_by_pair[pair] = outcome
            expected_outcomes = {
                (country, criterion) for country in countries for criterion in criteria
            }
            if set(outcome_by_pair) != expected_outcomes:
                missing = sorted(expected_outcomes - set(outcome_by_pair))
                raise PublishedReleaseError(
                    f"Published outcome matrix is incomplete; missing {missing[:3]}."
                )
            valid_pairs = {
                pair for pair, outcome in outcome_by_pair.items() if outcome["outcome"] == "valid"
            }
            derived_counts = {}
            for criterion_id, criterion in criteria.items():
                coverage = manifest_coverage[criterion_id]
                outcome_counts = Counter(
                    outcome["outcome"]
                    for pair, outcome in outcome_by_pair.items()
                    if pair[1] == criterion_id
                )
                derived = {
                    outcome: outcome_counts.get(outcome, 0)
                    for outcome in ("invalid", "missing", "rejected", "stale", "valid")
                }
                derived_counts[criterion_id] = derived["valid"]
                if coverage["outcome_counts"] != derived:
                    raise PublishedReleaseError(
                        f"Country outcome counts disagree for {criterion_id}."
                    )
                if (
                    coverage["stable_universe_id"] != catalog["stable_universe_id"]
                    or coverage["stable_country_count"] != len(countries)
                    or coverage["valid_country_count"] != derived["valid"]
                    or sum(derived.values()) != len(countries)
                    or coverage["score_min"] > coverage["score_max"]
                    or criterion["experimental"] != coverage["experimental"]
                ):
                    raise PublishedReleaseError(
                        f"Coverage policy metadata disagrees for {criterion_id}."
                    )
                mode = coverage["mode"]
                threshold = coverage["activation_threshold"]
                minimum = coverage["minimum_valid_country_count"]
                ready = criterion["ready"]
                if mode == "GLOBAL_CORE" and (
                    derived["valid"] != len(countries)
                    or minimum != len(countries)
                    or threshold is not None
                ):
                    raise PublishedReleaseError(
                        f"GLOBAL_CORE policy is invalid for {criterion_id}."
                    )
                if mode == "CONDITIONAL_COMPLETE_CASE" and (
                    minimum < 82
                    or derived["valid"] < minimum
                    or threshold is None
                    or not 0 <= threshold <= 1
                ):
                    raise PublishedReleaseError(f"PCC policy is invalid for {criterion_id}.")
                if mode == "DIAGNOSTIC_ONLY" and ready:
                    raise PublishedReleaseError(
                        f"DIAGNOSTIC_ONLY criterion {criterion_id} cannot be ready."
                    )
            if derived_counts != validation["criterion_coverage"]:
                raise PublishedReleaseError(
                    "Valid outcome counts do not match validation coverage."
                )
        catalog_methods = {item["scoring_method_version"] for item in criteria.values()}
        if catalog_methods != set(manifest["scoring_method_versions"]):
            raise PublishedReleaseError(
                "Catalog scoring methods do not match the release manifest."
            )

        source_by_id = {}
        for source in sources:
            if source["source_id"] in source_by_id:
                raise PublishedReleaseError(f"Duplicate source ID: {source['source_id']}")
            if source["criterion_id"] not in criteria:
                raise PublishedReleaseError(
                    f"Unknown source criterion ID: {source['criterion_id']}"
                )
            if manifest["source_versions"].get(source["source_id"]) != source["source_version"]:
                raise PublishedReleaseError(
                    f"Source version for {source['source_id']} disagrees with the manifest."
                )
            source_by_id[source["source_id"]] = source
        if release_major == 4:
            if set(source_by_id) != set(manifest["source_versions"]):
                raise PublishedReleaseError(
                    "Registered sources do not match manifest source versions."
                )
            for pair, outcome in outcome_by_pair.items():
                source = source_by_id.get(outcome["source_id"])
                if source is None or source["criterion_id"] != pair[1]:
                    raise PublishedReleaseError(
                        f"Broken source lineage for criterion outcome {pair}."
                    )

        observation_by_id = {}
        for observation in observations:
            observation_id = observation["observation_id"]
            if observation_id in observation_by_id:
                raise PublishedReleaseError(f"Duplicate observation ID: {observation_id}")
            if (
                observation["country_code"] not in countries
                or observation["metric_id"] not in criteria
            ):
                raise PublishedReleaseError(
                    f"Unknown country/criterion in observation {observation_id}."
                )
            source = source_by_id.get(observation["source_id"])
            if not source or source["criterion_id"] != observation["metric_id"]:
                raise PublishedReleaseError(
                    f"Broken source lineage for observation {observation_id}."
                )
            if not observation["source_records"] or any(
                not row.get("artifact_id") or not row.get("locator") or not row.get("record_id")
                for row in observation["source_records"]
            ):
                raise PublishedReleaseError(
                    f"Malformed record lineage for observation {observation_id}."
                )
            record_artifacts = {item["artifact_id"] for item in observation["source_records"]}
            if record_artifacts != set(observation["raw_artifact_ids"]):
                raise PublishedReleaseError(
                    f"Artifact lineage disagrees for observation {observation_id}."
                )
            observation_by_id[observation_id] = observation

        pair_keys = set()
        records = []
        for score in scores:
            pair = (score["country_code"], score["criterion_id"])
            if pair in pair_keys:
                raise PublishedReleaseError(f"Duplicate score pair: {pair[0]}/{pair[1]}")
            pair_keys.add(pair)
            if pair[0] not in countries or pair[1] not in criteria:
                raise PublishedReleaseError(
                    f"Unknown country/criterion in score {pair[0]}/{pair[1]}."
                )
            if score["method_version"] != criteria[pair[1]]["scoring_method_version"]:
                raise PublishedReleaseError(f"Scoring method disagrees for {pair[0]}/{pair[1]}.")
            if score["direction"] != criteria[pair[1]]["direction"]:
                raise PublishedReleaseError(f"Scoring direction disagrees for {pair[0]}/{pair[1]}.")
            if valid_pairs is not None:
                coverage = manifest["criterion_coverage"][pair[1]]
                if not coverage["score_min"] <= score["score"] <= coverage["score_max"]:
                    raise PublishedReleaseError(
                        f"Score is outside the allowed range for {pair[0]}/{pair[1]}."
                    )
            linked = []
            for observation_id in score["input_observation_ids"]:
                observation = observation_by_id.get(observation_id)
                if not observation:
                    raise PublishedReleaseError(
                        f"Missing input observation {observation_id} for score {pair}."
                    )
                if (observation["country_code"], observation["metric_id"]) != pair:
                    raise PublishedReleaseError(
                        f"Inconsistent input observation {observation_id} for score {pair}."
                    )
                linked.append(observation)
            source_ids = {item["source_id"] for item in linked}
            if len(source_ids) != 1:
                raise PublishedReleaseError(f"Score {pair} has ambiguous source lineage.")
            if valid_pairs is not None:
                outcome = outcome_by_pair[pair]
                if outcome["observation_id"] not in score["input_observation_ids"]:
                    raise PublishedReleaseError(
                        f"Criterion outcome observation disagrees for {pair}."
                    )
                if outcome["source_id"] not in source_ids:
                    raise PublishedReleaseError(f"Criterion outcome source disagrees for {pair}.")
            records.append(
                PublishedMetricRecord(
                    countries[pair[0]],
                    criteria[pair[1]],
                    score,
                    tuple(linked),
                    source_by_id[source_ids.pop()],
                )
            )

        expected_pairs = {(country, criterion) for country in countries for criterion in criteria}
        if valid_pairs is not None:
            expected_pairs = valid_pairs
        if pair_keys != expected_pairs:
            missing = sorted(expected_pairs - pair_keys)
            raise PublishedReleaseError(
                f"Published score matrix is incomplete; missing {missing[:3]}."
            )
        return tuple(sorted(records, key=lambda item: (item.country["code"], item.criterion["id"])))
