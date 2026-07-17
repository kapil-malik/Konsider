"""Local-first refresh worker and replay entry point."""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from konsider.ingestion.models import RawArtifact
from konsider.ingestion.parsers import PARSERS
from konsider.ingestion.registry import SOURCES
from konsider.ingestion.scoring import score_observations
from konsider.ingestion.validation import validate_release
from konsider.repositories.raw_artifact_repository import RawArtifactRepository
from konsider.repositories.release_repository import ReleaseRepository


def fetch_url(url: str) -> tuple[bytes, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "Konsider-data-worker/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - registered URLs only
        return response.read(), response.geturl(), response.headers.get_content_type()


def refresh(
    release_id: str, *, raw_root: Path | str = "data/raw", release_root: Path | str = "data/releases",
    fetcher=fetch_url, publish: bool = True,
) -> Path:
    raw_repository = RawArtifactRepository(raw_root)
    artifacts: list[RawArtifact] = []
    observations = []
    retrieved_at = datetime.now(UTC).isoformat()
    for registration in SOURCES.values():
        source_artifacts = []
        bodies = []
        for url in registration.download_urls:
            try:
                body, final_url, media_type = fetcher(url)
            except Exception as exc:  # pragma: no cover - exercised against live network
                raise RuntimeError(f"Failed to fetch {registration.source_id}: {url}") from exc
            artifact = raw_repository.capture(
                registration, body, requested_url=url, final_url=final_url,
                retrieved_at=retrieved_at, media_type=media_type,
            )
            source_artifacts.append(artifact)
            bodies.append(body)
        artifacts.extend(source_artifacts)
        observations.extend(PARSERS[registration.parser](source_artifacts, bodies))
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    scores = score_observations(observations)
    validation = validate_release(observations, scores, artifacts)
    repository = ReleaseRepository(release_root)
    path = repository.write_draft(
        release_id, observations, scores, artifacts,
        [source.to_dict() for source in SOURCES.values()], validation,
    )
    if publish:
        path = repository.publish(release_id)
    return path


def replay(release_path: Path | str) -> bool:
    release = Path(release_path)
    raw_items = json.loads((release / "raw-artifacts.json").read_text(encoding="utf-8"))
    artifacts = [RawArtifact(**item) for item in raw_items]
    raw_repository = RawArtifactRepository()
    observations = []
    for registration in SOURCES.values():
        source_artifacts = [item for item in artifacts if item.source_id == registration.source_id]
        ordered = sorted(source_artifacts, key=lambda item: registration.download_urls.index(item.requested_url))
        observations.extend(PARSERS[registration.parser](ordered, [raw_repository.load(item) for item in ordered]))
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    scores = score_observations(observations)
    expected_observations = [json.loads(line) for line in (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
    expected_scores = [json.loads(line) for line in (release / "scores.jsonl").read_text(encoding="utf-8").splitlines()]
    return [item.to_dict() for item in observations] == expected_observations and [item.to_dict() for item in scores] == expected_scores


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or replay a Konsider dataset release")
    subparsers = parser.add_subparsers(dest="command", required=True)
    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--release-id", required=True)
    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument("release_path")
    args = parser.parse_args()
    if args.command == "refresh":
        print(refresh(args.release_id))
        return 0
    passed = replay(args.release_path)
    print("replay passed" if passed else "replay failed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
