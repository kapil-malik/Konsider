"""Immutable draft and published local dataset releases with reproducibility manifests."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from konsider.ingestion.countries import COUNTRY_UNIVERSE
from konsider.ingestion.models import (
    CriterionCoverage,
    CriterionOutcome,
    MetricObservation,
    MetricScore,
    RawArtifact,
    SourceAttempt,
    ValidationReport,
)
from konsider.ingestion.validation import RELEASE_SCHEMA_VERSION
from konsider.text_io import write_text_lf


def _write_json(path: Path, value: object) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, values: Iterable[dict[str, object]]) -> None:
    rows = [json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values]
    write_text_lf(path, "\n".join(rows) + ("\n" if rows else ""))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReleaseRepository:
    def __init__(
        self,
        root: Path | str = "data/releases",
        catalog_path: Path | str = "data/catalogs/consumer-catalog-1.0.json",
    ) -> None:
        self.root = Path(root)
        self.catalog_path = Path(catalog_path)

    def write_draft(
        self,
        release_id: str,
        observations: list[MetricObservation],
        scores: list[MetricScore],
        artifacts: list[RawArtifact],
        sources: list[dict[str, object]],
        validation: ValidationReport,
        attempts: list[SourceAttempt] | list[CriterionOutcome] | None = None,
        sensitivity: dict[str, object] | None = None,
        *,
        coverage: list[CriterionCoverage] | None = None,
        previous_release_id: str | None = None,
        created_at: str | None = None,
    ) -> Path:
        draft, published = self.root / ".draft" / release_id, self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        if draft.exists():
            raise FileExistsError(f"Draft release already exists: {release_id}")
        if coverage is not None and not validation.schema_version.startswith("validation-4."):
            raise ValueError("Schema-4 coverage requires a validation-4 report.")
        if coverage is None and validation.schema_version.startswith("validation-4."):
            raise ValueError("A validation-4 report requires schema-4 coverage metadata.")
        if coverage is not None and {item.criterion_id for item in coverage} != set(
            validation.criterion_coverage_details
        ):
            raise ValueError("Coverage metadata and validation criteria disagree.")
        draft.mkdir(parents=True)
        attempts = attempts or []
        created_at = created_at or datetime.now(UTC).isoformat()
        _write_jsonl(draft / "observations.jsonl", (item.to_dict() for item in observations))
        _write_jsonl(draft / "scores.jsonl", (item.to_dict() for item in scores))
        _write_jsonl(draft / "attempts.jsonl", (item.to_dict() for item in attempts))
        _write_json(draft / "raw-artifacts.json", [item.to_dict() for item in artifacts])
        _write_json(draft / "sources.json", sources)
        _write_json(draft / "validation.json", validation.to_dict())
        _write_json(draft / "scoring-sensitivity.json", sensitivity or {})
        payload_names = [
            "observations.jsonl",
            "scores.jsonl",
            "attempts.jsonl",
            "raw-artifacts.json",
            "sources.json",
            "validation.json",
            "scoring-sensitivity.json",
        ]
        file_checksums = {name: f"sha256:{_sha256(draft / name)}" for name in payload_names}
        release_checksum = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(file_checksums, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        method_versions = sorted({score.method_version for score in scores})
        source_versions = {
            str(source["source_id"]): str(source["source_version"]) for source in sources
        }
        schema_version = "konsider-release-4.0" if coverage is not None else RELEASE_SCHEMA_VERSION
        country_codes = sorted(
            {item.country_code for item in attempts}
            if coverage is not None
            else {score.country_code for score in scores}
        )
        manifest = {
            "schema_version": schema_version,
            "release_id": release_id,
            "status": "draft",
            "created_at": created_at,
            "published_at": None,
            "previous_release_id": previous_release_id,
            "observation_count": len(observations),
            "score_count": len(scores),
            "attempt_count": len(attempts),
            "country_count": len(country_codes),
            "country_codes": country_codes,
            "country_universe": {
                "universe_id": COUNTRY_UNIVERSE["universe_id"],
                "policy_version": COUNTRY_UNIVERSE["policy_version"],
                "source_coverage_audit_id": COUNTRY_UNIVERSE["source_coverage_audit_id"],
                "licensing_decision": COUNTRY_UNIVERSE["licensing_decision"],
            },
            "criteria": sorted(validation.criterion_coverage),
            "source_versions": source_versions,
            "scoring_method_versions": method_versions,
            "artifact_checksums": {a.artifact_id: f"sha256:{a.sha256}" for a in artifacts},
            "file_checksums": file_checksums,
            "release_checksum": release_checksum,
            "validation_summary": {
                "structural_passed": validation.structural_passed,
                "product_ready": validation.product_ready,
                "ready_criterion_count": validation.ready_criterion_count,
                "criterion_readiness": dict(sorted(validation.criterion_readiness.items())),
                "errors": sum(i.severity == "error" for i in validation.issues),
                "blockers": sum(i.severity == "blocker" for i in validation.issues),
                "warnings": sum(i.severity == "warning" for i in validation.issues),
            },
            "reproducibility": {
                "raw_storage": "local content-addressed files excluded from git",
                "parser_versions": sorted({item.parser_version for item in observations}),
                "observation_method_versions": sorted(
                    {item.method_version for item in observations}
                ),
                "worker_package": "konsider-0.1.0",
                "python_requires": ">=3.11",
                "replay_command": (
                    f"python -m konsider.ingestion.worker replay data/releases/{release_id}"
                ),
            },
        }
        if coverage is not None:
            manifest["coverage_policy_version"] = validation.coverage_policy_version
            manifest["criterion_coverage"] = {
                item.criterion_id: item.to_dict()
                for item in sorted(coverage, key=lambda item: item.criterion_id)
            }
            manifest["validation_summary"].update(
                {
                    "global_core_ready_count": validation.global_core_ready_count,
                    "minimum_global_core_count": validation.minimum_global_core_count,
                }
            )
        _write_json(
            draft / "manifest.json",
            manifest,
        )
        return draft

    def publish(self, release_id: str, *, require_product_ready: bool = True) -> Path:
        draft = self.root / ".draft" / release_id
        validation = json.loads((draft / "validation.json").read_text(encoding="utf-8"))
        if not validation["structural_passed"]:
            raise ValueError("A structurally invalid release cannot be published.")
        if require_product_ready and not validation["product_ready"]:
            raise ValueError(
                "A release with fewer than five product-ready criteria cannot be promoted."
            )
        catalog = None
        if require_product_ready:
            catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            required = {
                str(item["id"])
                for item in catalog["criteria"]
                if item.get("ready") and item.get("default_enabled")
            }
            readiness = validation["criterion_readiness"]
            failed = sorted(criterion for criterion in required if not readiness.get(criterion))
            if failed:
                raise ValueError(
                    "Catalog-ready criteria failed release validation: " + ", ".join(failed)
                )
        published = self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        catalog_snapshot = self.catalog_path.parent / "releases" / f"{release_id}.json"
        if require_product_ready and catalog_snapshot.exists():
            raise FileExistsError(f"Published catalog snapshot is immutable: {release_id}")
        manifest_path = draft / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "published"
        manifest["published_at"] = datetime.now(UTC).isoformat()
        _write_json(manifest_path, manifest)
        catalog_snapshot_tmp = None
        if require_product_ready:
            catalog_snapshot.parent.mkdir(parents=True, exist_ok=True)
            catalog_snapshot_tmp = catalog_snapshot.with_suffix(".json.tmp")
            _write_json(catalog_snapshot_tmp, catalog)
        published.parent.mkdir(parents=True, exist_ok=True)
        draft.replace(published)
        if catalog_snapshot_tmp is not None:
            os.replace(catalog_snapshot_tmp, catalog_snapshot)
        pointer_tmp = self.root / "active.json.tmp"
        _write_json(
            pointer_tmp,
            {"release_id": release_id, "schema_version": manifest["schema_version"]},
        )
        os.replace(pointer_tmp, self.root / "active.json")
        return published
