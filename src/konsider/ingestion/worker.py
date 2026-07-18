"""Local-first refresh, stabilization, and replay entry points."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.models import RawArtifact, SourceAttempt
from konsider.ingestion.parsers import PARSERS
from konsider.ingestion.registry import SOURCES
from konsider.ingestion.scoring import score_observations, sensitivity_experiments
from konsider.ingestion.validation import RELEASE_SCHEMA_VERSION, validate_release
from konsider.repositories.raw_artifact_repository import RawArtifactRepository
from konsider.repositories.release_repository import ReleaseRepository


def fetch_url(url: str) -> tuple[bytes, str, str, dict[str, object]]:
    request = urllib.request.Request(url, headers={"User-Agent": "Konsider-data-worker/0.2"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - registered URLs only
        return response.read(), response.geturl(), response.headers.get_content_type(), {
            "http_status": response.status, "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "content_length_header": response.headers.get("Content-Length"),
        }


def _fetch_result(fetcher, url: str):
    result = fetcher(url)
    if len(result) == 3:
        body, final_url, media_type = result
        return body, final_url, media_type, {"http_status": 200}
    return result


def _next_odata_url(url: str, skip: int) -> str:
    return re.sub(r"(%24skip=|\$skip=)\d+", rf"\g<1>{skip}", url)


def _fetch_registration(registration, raw_repository, fetcher, retrieved_at):
    artifacts, bodies = [], []
    urls = list(registration.download_urls)
    index = 0
    while index < len(urls):
        url = urls[index]
        body, final_url, media_type, metadata = _fetch_result(fetcher, url)
        if registration.pagination == "odata_skip_until_empty":
            payload = json.loads(body.decode("utf-8-sig"))
            rows = payload.get("value", [])
            if not rows:
                break  # Empty termination probes are deliberately not persisted.
        artifact = raw_repository.capture(
            registration, body, requested_url=url, final_url=final_url,
            retrieved_at=retrieved_at, media_type=media_type, **metadata,
        )
        artifacts.append(artifact)
        bodies.append(body)
        if registration.pagination == "odata_skip_until_empty":
            if len(rows) < 1000:
                break
            skip_match = re.search(r"(?:%24skip=|\$skip=)(\d+)", url)
            skip = int(skip_match.group(1)) + 1000 if skip_match else len(rows)
            urls.append(_next_odata_url(url, skip))
            if len(urls) > 10000:
                raise RuntimeError(f"Pagination safety limit exceeded for {registration.source_id}")
        index += 1
    return artifacts, bodies


def _artifact_order(registration, artifacts: list[RawArtifact]) -> list[RawArtifact]:
    if registration.pagination == "odata_skip_until_empty":
        return sorted(artifacts, key=lambda item: int(re.search(r"(?:%24skip=|\$skip=)(\d+)", item.requested_url).group(1)))
    order = {url: index for index, url in enumerate(registration.download_urls)}
    return sorted(artifacts, key=lambda item: order.get(item.requested_url, 9999))


def _attempts_for(registration, observations, attempted_at, fallback_artifacts=(), failure=None):
    by_country = {item.country_code: item for item in observations}
    attempts = []
    for code in COUNTRY_CODES:
        observation = by_country.get(code)
        if failure:
            attempts.append(SourceAttempt(
                registration.source_id, registration.criterion_id, code, "failed", attempted_at,
                registration.parser_version, tuple(item.artifact_id for item in fallback_artifacts),
                reason=failure,
            ))
        elif observation:
            attempts.append(SourceAttempt(
                registration.source_id, registration.criterion_id, code, "success", attempted_at,
                registration.parser_version, observation.raw_artifact_ids, observation.observation_id,
            ))
        else:
            attempts.append(SourceAttempt(
                registration.source_id, registration.criterion_id, code, "no_data", attempted_at,
                registration.parser_version, tuple(item.artifact_id for item in fallback_artifacts),
                reason="No eligible source record for the expected country/criterion.",
            ))
    return attempts


def _parse_artifacts(artifacts: list[RawArtifact], raw_repository: RawArtifactRepository):
    observations, attempts = [], []
    attempted_at = max((item.retrieved_at for item in artifacts), default=datetime.now(UTC).isoformat())
    for registration in SOURCES.values():
        ordered = _artifact_order(registration, [item for item in artifacts if item.source_id == registration.source_id])
        try:
            parsed = PARSERS[registration.parser](ordered, [raw_repository.load(item) for item in ordered])
            observations.extend(parsed)
            attempts.extend(_attempts_for(registration, parsed, attempted_at, ordered))
        except Exception as exc:
            attempts.extend(_attempts_for(registration, [], attempted_at, ordered, f"{type(exc).__name__}: {exc}"))
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    return observations, attempts


def _write_release(
    release_id, artifacts, observations, attempts, release_root, previous_release_id=None,
    previous_observations=None,
):
    scores = score_observations(observations)
    sensitivity = sensitivity_experiments(observations)
    validation = validate_release(
        observations, scores, artifacts, attempts, list(SOURCES.values()),
        schema_version=RELEASE_SCHEMA_VERSION, previous_observations=previous_observations,
    )
    repository = ReleaseRepository(release_root)
    path = repository.write_draft(
        release_id, observations, scores, artifacts, [source.to_dict() for source in SOURCES.values()],
        validation, attempts, sensitivity, previous_release_id=previous_release_id,
    )
    return repository.publish(release_id), validation


def refresh(
    release_id: str, *, raw_root: Path | str = "data/raw", release_root: Path | str = "data/releases",
    fetcher=fetch_url, publish: bool = True,
) -> Path:
    raw_repository = RawArtifactRepository(raw_root)
    artifacts, observations, attempts = [], [], []
    retrieved_at = datetime.now(UTC).isoformat()
    for registration in SOURCES.values():
        source_artifacts = []
        try:
            source_artifacts, bodies = _fetch_registration(registration, raw_repository, fetcher, retrieved_at)
            artifacts.extend(source_artifacts)
            parsed = PARSERS[registration.parser](source_artifacts, bodies)
            observations.extend(parsed)
            attempts.extend(_attempts_for(registration, parsed, retrieved_at, source_artifacts))
        except Exception as exc:
            attempts.extend(_attempts_for(
                registration, [], retrieved_at, source_artifacts,
                failure=f"{type(exc).__name__}: {exc}",
            ))
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    scores = score_observations(observations)
    sensitivity = sensitivity_experiments(observations)
    validation = validate_release(observations, scores, artifacts, attempts, list(SOURCES.values()))
    repository = ReleaseRepository(release_root)
    path = repository.write_draft(release_id, observations, scores, artifacts, [s.to_dict() for s in SOURCES.values()], validation, attempts, sensitivity)
    return repository.publish(release_id) if publish else path


def stabilize_baseline(previous_path: Path | str, release_id: str, release_root: Path | str = "data/releases") -> Path:
    previous = Path(previous_path)
    artifacts = [RawArtifact(**item) for item in json.loads((previous / "raw-artifacts.json").read_text(encoding="utf-8"))]
    observations, attempts = _parse_artifacts(artifacts, RawArtifactRepository())
    previous_rows = [json.loads(line) for line in (previous / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
    previous_observations = [SimpleNamespace(**row) for row in previous_rows]
    path, _ = _write_release(
        release_id, artifacts, observations, attempts, release_root, previous.name,
        previous_observations,
    )
    return path


def replay(release_path: Path | str) -> bool:
    release = Path(release_path)
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    raw_items = json.loads((release / "raw-artifacts.json").read_text(encoding="utf-8"))
    artifacts = [RawArtifact(**item) for item in raw_items]
    raw_repository = RawArtifactRepository()
    for artifact in artifacts:
        try:
            body = raw_repository.load(artifact)
        except (FileNotFoundError, ValueError):
            return False
        if hashlib.sha256(body).hexdigest() != artifact.sha256:
            return False
    if manifest.get("schema_version") != RELEASE_SCHEMA_VERSION:
        return manifest.get("observation_count") == len((release / "observations.jsonl").read_text(encoding="utf-8").splitlines())
    for name, expected in manifest["file_checksums"].items():
        if "sha256:" + hashlib.sha256((release / name).read_bytes()).hexdigest() != expected:
            return False
    expected_release_checksum = "sha256:" + hashlib.sha256(
        json.dumps(manifest["file_checksums"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if manifest.get("release_checksum") != expected_release_checksum:
        return False
    observations, attempts = _parse_artifacts(artifacts, raw_repository)
    scores = score_observations(observations)
    expected_observations = [json.loads(line) for line in (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
    expected_scores = [json.loads(line) for line in (release / "scores.jsonl").read_text(encoding="utf-8").splitlines()]
    expected_attempts = [json.loads(line) for line in (release / "attempts.jsonl").read_text(encoding="utf-8").splitlines()]
    return ([item.to_dict() for item in observations] == expected_observations
            and [item.to_dict() for item in scores] == expected_scores
            and [item.to_dict() for item in attempts] == expected_attempts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build, stabilize, or replay a Konsider dataset release")
    subparsers = parser.add_subparsers(dest="command", required=True)
    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--release-id", required=True)
    stabilize_parser = subparsers.add_parser("stabilize-baseline")
    stabilize_parser.add_argument("previous_path")
    stabilize_parser.add_argument("--release-id", required=True)
    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument("release_path")
    args = parser.parse_args()
    if args.command == "refresh":
        print(refresh(args.release_id)); return 0
    if args.command == "stabilize-baseline":
        print(stabilize_baseline(args.previous_path, args.release_id)); return 0
    passed = replay(args.release_path)
    print("replay passed" if passed else "replay failed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
