"""Immutable draft and published local dataset releases with reproducibility manifests."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from konsider.ingestion.countries import COUNTRY_UNIVERSE
from konsider.ingestion.models import (
    MetricObservation,
    MetricScore,
    RawArtifact,
    SourceAttempt,
    ValidationReport,
)
from konsider.ingestion.validation import RELEASE_SCHEMA_VERSION


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, values: Iterable[dict[str, object]]) -> None:
    rows = [json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values]
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReleaseRepository:
    def __init__(self, root: Path | str = "data/releases") -> None:
        self.root = Path(root)

    def write_draft(
        self,
        release_id: str,
        observations: list[MetricObservation],
        scores: list[MetricScore],
        artifacts: list[RawArtifact],
        sources: list[dict[str, object]],
        validation: ValidationReport,
        attempts: list[SourceAttempt] | None = None,
        sensitivity: dict[str, object] | None = None,
        *,
        previous_release_id: str | None = None,
        created_at: str | None = None,
    ) -> Path:
        draft, published = self.root / ".draft" / release_id, self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        if draft.exists():
            raise FileExistsError(f"Draft release already exists: {release_id}")
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
        country_codes = sorted({score.country_code for score in scores})
        _write_json(
            draft / "manifest.json",
            {
                "schema_version": RELEASE_SCHEMA_VERSION,
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
                    "replay_command": f"python -m konsider.ingestion.worker replay data/releases/{release_id}",
                },
            },
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
        published = self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        manifest_path = draft / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "published"
        manifest["published_at"] = datetime.now(UTC).isoformat()
        _write_json(manifest_path, manifest)
        published.parent.mkdir(parents=True, exist_ok=True)
        draft.replace(published)
        pointer_tmp = self.root / "active.json.tmp"
        _write_json(
            pointer_tmp, {"release_id": release_id, "schema_version": RELEASE_SCHEMA_VERSION}
        )
        os.replace(pointer_tmp, self.root / "active.json")
        return published
