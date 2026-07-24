"""Local-first refresh, stabilization, and replay entry points."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from konsider.ingestion.countries import COUNTRY_CODES
from konsider.ingestion.country_coverage import audit_coverage
from konsider.ingestion.models import RawArtifact, SourceAttempt, SourceRegistration
from konsider.ingestion.parsers import PARSERS
from konsider.ingestion.registry import SOURCES
from konsider.ingestion.scoring import score_observations, sensitivity_experiments
from konsider.ingestion.validation import RELEASE_SCHEMA_VERSION, validate_release
from konsider.repositories.raw_artifact_repository import RawArtifactRepository
from konsider.repositories.release_repository import ReleaseRepository


def fetch_url(url: str) -> tuple[bytes, str, str, dict[str, object]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Konsider-data-worker/0.3",
            "Referer": "https://wbl.worldbank.org/en/data/download-data",
            "Accept": "application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*",
        },
    )
    with urllib.request.urlopen(
        request, timeout=120
    ) as response:  # noqa: S310 - registered URLs only
        return (
            response.read(),
            response.geturl(),
            response.headers.get_content_type(),
            {
                "http_status": response.status,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "content_length_header": response.headers.get("Content-Length"),
            },
        )


def _fetch_result(fetcher, url: str):
    result = fetcher(url)
    if len(result) == 3:
        body, final_url, media_type = result
        return body, final_url, media_type, {"http_status": 200}
    return result


def _next_odata_url(url: str, skip: int) -> str:
    if re.search(r"(?:%24skip=|\$skip=)\d+", url):
        return re.sub(r"(%24skip=|\$skip=)\d+", rf"\g<1>{skip}", url)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}%24skip={skip}"


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
            registration,
            body,
            requested_url=url,
            final_url=final_url,
            retrieved_at=retrieved_at,
            media_type=media_type,
            **metadata,
        )
        artifacts.append(artifact)
        bodies.append(body)
        if registration.pagination == "odata_skip_until_empty":
            next_url = payload.get("@odata.nextLink") or payload.get("odata.nextLink")
            if next_url:
                if next_url in urls:
                    raise RuntimeError(f"Repeated continuation URL for {registration.source_id}")
                urls.append(next_url)
                index += 1
                continue
            top_match = re.search(r"(?:%24top=|\$top=)(\d+)", url)
            if top_match and len(rows) < int(top_match.group(1)):
                break
            skip_match = re.search(r"(?:%24skip=|\$skip=)(\d+)", url)
            skip = int(skip_match.group(1)) + len(rows) if skip_match else len(rows)
            next_url = _next_odata_url(url, skip)
            if next_url in urls:
                raise RuntimeError(f"Pagination made no progress for {registration.source_id}")
            urls.append(next_url)
            if len(urls) > 10000:
                raise RuntimeError(f"Pagination safety limit exceeded for {registration.source_id}")
        index += 1
    return artifacts, bodies


def _artifact_order(registration, artifacts: list[RawArtifact]) -> list[RawArtifact]:
    if registration.pagination == "odata_skip_until_empty":

        def skip_value(item):
            match = re.search(r"(?:%24skip=|\$skip=)(\d+)", item.requested_url)
            return int(match.group(1)) if match else 0

        return sorted(artifacts, key=skip_value)
    order = {url: index for index, url in enumerate(registration.download_urls)}
    return sorted(artifacts, key=lambda item: order.get(item.requested_url, 9999))


def _attempts_for(
    registration,
    observations,
    attempted_at,
    fallback_artifacts=(),
    failure=None,
    country_codes=COUNTRY_CODES,
):
    by_country = {item.country_code: item for item in observations}
    attempts = []
    for code in country_codes:
        observation = by_country.get(code)
        if failure:
            attempts.append(
                SourceAttempt(
                    registration.source_id,
                    registration.criterion_id,
                    code,
                    "failed",
                    attempted_at,
                    registration.parser_version,
                    tuple(item.artifact_id for item in fallback_artifacts),
                    reason=failure,
                )
            )
        elif observation:
            attempts.append(
                SourceAttempt(
                    registration.source_id,
                    registration.criterion_id,
                    code,
                    "success",
                    attempted_at,
                    registration.parser_version,
                    observation.raw_artifact_ids,
                    observation.observation_id,
                )
            )
        else:
            attempts.append(
                SourceAttempt(
                    registration.source_id,
                    registration.criterion_id,
                    code,
                    "no_data",
                    attempted_at,
                    registration.parser_version,
                    tuple(item.artifact_id for item in fallback_artifacts),
                    reason="No eligible source record for the expected country/criterion.",
                )
            )
    return attempts


def _parse_artifacts(
    artifacts: list[RawArtifact],
    raw_repository: RawArtifactRepository,
    registrations: list[SourceRegistration] | None = None,
    country_codes: tuple[str, ...] | None = None,
):
    observations, attempts = [], []
    attempted_at = max(
        (item.retrieved_at for item in artifacts), default=datetime.now(UTC).isoformat()
    )
    for registration in registrations or list(SOURCES.values()):
        ordered = _artifact_order(
            registration, [item for item in artifacts if item.source_id == registration.source_id]
        )
        try:
            parsed = PARSERS[registration.parser](
                ordered, [raw_repository.load(item) for item in ordered]
            )
            if country_codes is not None:
                allowed_country_codes = set(country_codes)
                parsed = [
                    observation
                    for observation in parsed
                    if observation.country_code in allowed_country_codes
                ]
            observations.extend(parsed)
            attempts.extend(
                _attempts_for(
                    registration,
                    parsed,
                    attempted_at,
                    ordered,
                    country_codes=country_codes or COUNTRY_CODES,
                )
            )
        except Exception as exc:
            attempts.extend(
                _attempts_for(
                    registration,
                    [],
                    attempted_at,
                    ordered,
                    f"{type(exc).__name__}: {exc}",
                    country_codes=country_codes or COUNTRY_CODES,
                )
            )
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    return observations, attempts


def _write_release(
    release_id,
    artifacts,
    observations,
    attempts,
    release_root,
    previous_release_id=None,
    previous_observations=None,
):
    scores = score_observations(observations, profile="current")
    sensitivity = sensitivity_experiments(observations)
    validation = validate_release(
        observations,
        scores,
        artifacts,
        attempts,
        list(SOURCES.values()),
        schema_version=RELEASE_SCHEMA_VERSION,
        previous_observations=previous_observations,
    )
    repository = ReleaseRepository(release_root)
    repository.write_draft(
        release_id,
        observations,
        scores,
        artifacts,
        [source.to_dict() for source in SOURCES.values()],
        validation,
        attempts,
        sensitivity,
        previous_release_id=previous_release_id,
    )
    return repository.publish(release_id, require_product_ready=True), validation


def refresh(
    release_id: str,
    *,
    raw_root: Path | str = "data/raw",
    release_root: Path | str = "data/releases",
    fetcher=fetch_url,
    publish: bool = True,
    source_versions: Mapping[str, str] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> Path:
    """Refresh sources after explicitly acknowledging every registered source version."""

    expected_versions = {item.source_id: item.source_version for item in SOURCES.values()}
    if dict(source_versions or {}) != expected_versions:
        raise ValueError(
            "Refresh requires an explicit source_versions mapping matching every audited "
            "registration. Update the registration first when an upstream dataset changes."
        )
    raw_repository = RawArtifactRepository(raw_root)
    artifacts, observations, attempts = [], [], []
    refreshed_at = (clock or (lambda: datetime.now(UTC)))()
    retrieved_at = refreshed_at.isoformat()
    for registration in SOURCES.values():
        source_artifacts = []
        try:
            source_artifacts, bodies = _fetch_registration(
                registration, raw_repository, fetcher, retrieved_at
            )
            artifacts.extend(source_artifacts)
            parsed = PARSERS[registration.parser](source_artifacts, bodies)
            observations.extend(parsed)
            attempts.extend(_attempts_for(registration, parsed, retrieved_at, source_artifacts))
        except Exception as exc:
            attempts.extend(
                _attempts_for(
                    registration,
                    [],
                    retrieved_at,
                    source_artifacts,
                    failure=f"{type(exc).__name__}: {exc}",
                )
            )
    observations.sort(key=lambda item: (item.metric_id, item.country_code, item.reference_end))
    scores = score_observations(observations, profile="current")
    sensitivity = sensitivity_experiments(observations)
    release_root_path = Path(release_root)
    active_path = release_root_path / "active.json"
    previous_release_id = None
    previous_observations = None
    if active_path.exists():
        previous_release_id = json.loads(active_path.read_text(encoding="utf-8"))["release_id"]
        previous_path = release_root_path / previous_release_id / "observations.jsonl"
        if previous_path.exists():
            previous_observations = [
                SimpleNamespace(**json.loads(line))
                for line in previous_path.read_text(encoding="utf-8").splitlines()
            ]
    validation = validate_release(
        observations,
        scores,
        artifacts,
        attempts,
        list(SOURCES.values()),
        previous_observations=previous_observations,
        as_of_year=refreshed_at.year,
    )
    repository = ReleaseRepository(release_root)
    path = repository.write_draft(
        release_id,
        observations,
        scores,
        artifacts,
        [s.to_dict() for s in SOURCES.values()],
        validation,
        attempts,
        sensitivity,
        previous_release_id=previous_release_id,
    )
    return repository.publish(release_id, require_product_ready=True) if publish else path


def stabilize_baseline(
    previous_path: Path | str, release_id: str, release_root: Path | str = "data/releases"
) -> Path:
    previous = Path(previous_path)
    artifacts = [
        RawArtifact(**item)
        for item in json.loads((previous / "raw-artifacts.json").read_text(encoding="utf-8"))
    ]
    observations, attempts = _parse_artifacts(artifacts, RawArtifactRepository())
    previous_rows = [
        json.loads(line)
        for line in (previous / "observations.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    previous_observations = [SimpleNamespace(**row) for row in previous_rows]
    path, _ = _write_release(
        release_id,
        artifacts,
        observations,
        attempts,
        release_root,
        previous.name,
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
    schema_version = manifest.get("schema_version")
    if not schema_version:
        return manifest.get("observation_count") == len(
            (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()
        )
    for name, expected in manifest["file_checksums"].items():
        if "sha256:" + hashlib.sha256((release / name).read_bytes()).hexdigest() != expected:
            return False
    expected_release_checksum = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest["file_checksums"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    if manifest.get("release_checksum") != expected_release_checksum:
        return False
    source_items = json.loads((release / "sources.json").read_text(encoding="utf-8"))
    registrations = [SourceRegistration(**item) for item in source_items]
    expected_observations = [
        json.loads(line)
        for line in (release / "observations.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    expected_scores = [
        json.loads(line)
        for line in (release / "scores.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    expected_attempts = [
        json.loads(line)
        for line in (release / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    release_country_codes = tuple(
        dict.fromkeys(
            str(item["country_code"]) for item in (expected_attempts or expected_observations)
        )
    )
    observations, attempts = _parse_artifacts(
        artifacts,
        raw_repository,
        registrations,
        country_codes=release_country_codes,
    )
    score_profile = "legacy" if schema_version == "konsider-release-2.0" else "current"
    scores = score_observations(observations, profile=score_profile)
    return (
        [item.to_dict() for item in observations] == expected_observations
        and [item.to_dict() for item in scores] == expected_scores
        and [item.to_dict() for item in attempts] == expected_attempts
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build, stabilize, or replay a Konsider dataset release"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "list-sources",
        help="Print the registered source-version acknowledgements required by refresh.",
    )
    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--release-id", required=True)
    refresh_parser.add_argument(
        "--source-version",
        action="append",
        default=[],
        metavar="SOURCE_ID=VERSION",
        help="Acknowledge each audited source version; repeat once per registered source.",
    )
    stabilize_parser = subparsers.add_parser("stabilize-baseline")
    stabilize_parser.add_argument("previous_path")
    stabilize_parser.add_argument("--release-id", required=True)
    replay_parser = subparsers.add_parser("replay")
    replay_parser.add_argument("release_path")
    audit_parser = subparsers.add_parser(
        "audit-coverage",
        help="Build or replay a country coverage audit without activating a release.",
    )
    audit_parser.add_argument("--universe", required=True)
    audit_parser.add_argument("--audit-id", required=True)
    audit_parser.add_argument("--mode", required=True, choices=("online", "offline"))
    audit_parser.add_argument("--output-root", default="data/reports/country-coverage")
    audit_parser.add_argument("--raw-root", default="data/raw")
    audit_parser.add_argument("--artifacts")
    audit_parser.add_argument("--candidate-limit", type=int)
    args = parser.parse_args()
    if args.command == "list-sources":
        for source_id in sorted(SOURCES):
            print(f"{source_id}={SOURCES[source_id].source_version}")
        return 0
    if args.command == "refresh":
        versions = dict(item.split("=", 1) for item in args.source_version)
        print(refresh(args.release_id, source_versions=versions))
        return 0
    if args.command == "stabilize-baseline":
        print(stabilize_baseline(args.previous_path, args.release_id))
        return 0
    if args.command == "audit-coverage":
        path, summary = audit_coverage(
            args.universe,
            args.audit_id,
            mode=args.mode,
            output_root=args.output_root,
            raw_root=args.raw_root,
            artifact_manifest=args.artifacts,
            candidate_limit=args.candidate_limit,
        )
        print(f"Universe: {summary['universe_id']}")
        print(f"Candidate countries: {summary['candidate_country_count']}")
        print(f"Enabled criteria: {len(summary['enabled_criteria'])}")
        print("Complete publishable countries: " f"{summary['complete_publishable_country_count']}")
        print(f"Minimum required: {summary['minimum_required_country_count']}")
        print(f"Status: {summary['status']}")
        print(path)
        return 0 if summary["status"] == "PASS" else 2
    passed = replay(args.release_path)
    print("replay passed" if passed else "replay failed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
