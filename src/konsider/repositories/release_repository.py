"""Immutable draft and published local dataset releases."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from konsider.ingestion.models import MetricObservation, MetricScore, RawArtifact, ValidationReport


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, values: Iterable[dict[str, object]]) -> None:
    rows = [json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values]
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


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
    ) -> Path:
        draft = self.root / ".draft" / release_id
        published = self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        if draft.exists():
            raise FileExistsError(f"Draft release already exists: {release_id}")
        draft.mkdir(parents=True)
        _write_jsonl(draft / "observations.jsonl", (item.to_dict() for item in observations))
        _write_jsonl(draft / "scores.jsonl", (item.to_dict() for item in scores))
        _write_json(draft / "raw-artifacts.json", [item.to_dict() for item in artifacts])
        _write_json(draft / "sources.json", sources)
        _write_json(draft / "validation.json", validation.to_dict())
        _write_json(draft / "manifest.json", {
            "release_id": release_id, "status": "draft",
            "observation_count": len(observations), "score_count": len(scores),
            "criteria": sorted(validation.criterion_coverage),
            "raw_artifact_ids": sorted({a.artifact_id for a in artifacts}),
        })
        return draft

    def publish(self, release_id: str) -> Path:
        draft = self.root / ".draft" / release_id
        validation = json.loads((draft / "validation.json").read_text(encoding="utf-8"))
        if not validation["passed"]:
            raise ValueError("A release with validation errors cannot be published.")
        published = self.root / release_id
        if published.exists():
            raise FileExistsError(f"Published release is immutable: {release_id}")
        manifest_path = draft / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["status"] = "published"
        _write_json(manifest_path, manifest)
        published.parent.mkdir(parents=True, exist_ok=True)
        draft.replace(published)
        pointer_tmp = self.root / "active.json.tmp"
        _write_json(pointer_tmp, {"release_id": release_id})
        os.replace(pointer_tmp, self.root / "active.json")
        return published
