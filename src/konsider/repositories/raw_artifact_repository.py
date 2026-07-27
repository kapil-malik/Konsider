"""Content-addressed immutable raw artifact storage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from konsider.ingestion.models import RawArtifact, SourceRegistration
from konsider.text_io import write_text_lf


class RawArtifactRepository:
    def __init__(self, root: Path | str = "data/raw") -> None:
        self.root = Path(root)

    def capture(
        self,
        registration: SourceRegistration,
        body: bytes,
        *,
        requested_url: str,
        final_url: str,
        retrieved_at: str,
        media_type: str,
        http_status: int = 200,
        etag: str | None = None,
        last_modified: str | None = None,
        content_length_header: str | None = None,
    ) -> RawArtifact:
        digest = hashlib.sha256(body).hexdigest()
        artifact_id = f"sha256:{digest}"
        source_dir = self.root / registration.source_id
        source_dir.mkdir(parents=True, exist_ok=True)
        body_path = source_dir / f"{digest}.bin"
        metadata_path = source_dir / f"{digest}.json"
        if body_path.exists() and body_path.read_bytes() != body:
            raise ValueError(f"Immutable artifact collision: {artifact_id}")
        if not body_path.exists():
            body_path.write_bytes(body)
        artifact = RawArtifact(
            artifact_id=artifact_id,
            source_id=registration.source_id,
            requested_url=requested_url,
            final_url=final_url,
            retrieved_at=retrieved_at,
            media_type=media_type,
            byte_length=len(body),
            sha256=digest,
            dataset_version=registration.dataset_version,
            parser_version=registration.parser_version,
            path=body_path.as_posix(),
            http_status=http_status,
            etag=etag,
            last_modified=last_modified,
            content_length_header=content_length_header,
        )
        encoded = json.dumps(artifact.to_dict(), indent=2, sort_keys=True) + "\n"
        if (
            metadata_path.exists()
            and json.loads(metadata_path.read_text(encoding="utf-8"))["sha256"] != digest
        ):
            raise ValueError(f"Immutable artifact metadata collision: {artifact_id}")
        if not metadata_path.exists():
            write_text_lf(metadata_path, encoded)
        return artifact

    def load(self, artifact: RawArtifact) -> bytes:
        body = Path(artifact.path).read_bytes()
        if hashlib.sha256(body).hexdigest() != artifact.sha256:
            raise ValueError(f"Checksum mismatch for {artifact.artifact_id}")
        return body
