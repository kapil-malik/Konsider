"""Read-only adapter for validated, immutable published releases."""

from __future__ import annotations

import hashlib
import json
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
        self.catalog_path = Path(
            catalog_path or PROJECT_ROOT / "data" / "catalogs" / "consumer-catalog-1.0.json"
        ).resolve()
        self.active_release_path = (
            Path(active_release_path)
            if active_release_path is not None
            else self.release_root / "active.json"
        )

    def load_active(self, *, diagnostic_read_only: bool = False) -> PublishedRelease:
        try:
            pointer = _read_json(self.active_release_path)
            require_supported_version(pointer.get("schema_version"), "konsider-release")
            validate_contract(pointer, "active-release-pointer", context="active release pointer")
            release_path = self.release_root / pointer["release_id"]
            manifest = _read_json(release_path / "manifest.json")
            require_supported_version(manifest.get("schema_version"), "konsider-release")
            validate_contract(manifest, "release-manifest", context="release manifest")
            if manifest["release_id"] != pointer["release_id"]:
                raise PublishedReleaseError("Active pointer and manifest release IDs disagree.")
            if manifest["status"] != "published":
                raise PublishedReleaseError("The active release is not published.")
            if not manifest["validation_summary"]["structural_passed"]:
                raise PublishedReleaseError("The active release failed structural validation.")
            self._verify_checksums(release_path, manifest)

            validation = _read_json(release_path / "validation.json")
            require_supported_version(validation.get("schema_version"), "validation")
            validate_contract(validation, "validation-report", context="validation report")
            sources = _read_json(release_path / "sources.json")
            observations = _read_jsonl(release_path / "observations.jsonl")
            scores = _read_jsonl(release_path / "scores.jsonl")
            for index, source in enumerate(sources):
                validate_contract(
                    source, "source-registration", context=f"source registration {index}"
                )
            for index, observation in enumerate(observations):
                validate_contract(observation, "metric-observation", context=f"observation {index}")
            for index, score in enumerate(scores):
                validate_contract(score, "metric-score", context=f"score {index}")

            catalog = _read_json(self.catalog_path)
            require_supported_version(catalog.get("schema_version"), "consumer-catalog")
            validate_contract(catalog, "consumer-catalog", context="consumer catalog")
            records = self._join(manifest, validation, catalog, sources, observations, scores)
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
    def _join(manifest, validation, catalog, sources, observations, scores):
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
        if pair_keys != expected_pairs:
            missing = sorted(expected_pairs - pair_keys)
            raise PublishedReleaseError(
                f"Published score matrix is incomplete; missing {missing[:3]}."
            )
        return tuple(sorted(records, key=lambda item: (item.country["code"], item.criterion["id"])))
