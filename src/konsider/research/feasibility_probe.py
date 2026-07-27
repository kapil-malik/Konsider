"""Generic deterministic source-feasibility probes for Phase 3 research."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from konsider.ingestion.countries import COUNTRY_ALIASES
from konsider.ingestion.models import RawArtifact, SourceRegistration
from konsider.repositories.raw_artifact_repository import RawArtifactRepository
from konsider.research.probe_adapters import ADAPTERS
from konsider.research.probe_models import (
    ArtifactInput,
    CountryProbeResult,
    ParsedProbeRecord,
    ProbeDefinition,
)
from konsider.text_io import write_text_lf

PROBE_SCHEMA_VERSION = "feasibility-probe-report-1.0"
DEFAULT_UNIVERSE_PATH = Path("data/country-universes/stable-supported-v1.json")


def load_definition(path: Path | str) -> ProbeDefinition:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Probe definition must be a JSON object.")
    return ProbeDefinition.from_dict(value)


def _source_registration(definition: ProbeDefinition) -> SourceRegistration:
    source = definition.source
    return SourceRegistration(
        source_id=source.source_candidate_id,
        criterion_id=definition.criterion_id,
        publisher=source.publisher,
        distributor=None,
        canonical_page_url=source.canonical_page_url,
        download_urls=source.access_urls,
        access_method="Phase 3 deterministic research probe",
        pagination="adapter-specific",
        dataset_version=source.dataset_version,
        source_version=source.source_version,
        reference_period=f"fresh when observation year >= {definition.freshness_min_year}",
        update_frequency=source.update_frequency,
        methodology_url=source.methodology_url,
        license_name=source.licence_name,
        license_url=source.licence_url,
        redistribution=source.redistribution,
        permitted_usage="Non-publishing source-feasibility research only.",
        attribution=source.attribution,
        license_evidence=source.licence_evidence,
        parser=definition.adapter_id,
        parser_version=source.parser_version,
        official_or_independent="official",
        notes="Research probe registration; not an approved production source registration.",
    )


def _active_pointer_bytes(release_root: Path) -> bytes | None:
    path = release_root / "active.json"
    return path.read_bytes() if path.exists() else None


def _write_json(path: Path, value: object) -> None:
    write_text_lf(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    encoded = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    write_text_lf(path, "\n".join(encoded) + ("\n" if encoded else ""))


def _load_universe(path: Path) -> tuple[str, list[dict[str, object]]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("canonical_identifier") != "ISO 3166-1 alpha-3":
        raise ValueError("Probe universe must use ISO 3166-1 alpha-3.")
    countries = value.get("countries")
    if not isinstance(countries, list) or int(value.get("country_count", -1)) != len(countries):
        raise ValueError("Probe universe country count is inconsistent.")
    return str(value["universe_id"]), countries


def _map_record(
    record: ParsedProbeRecord,
    countries_by_code: dict[str, dict[str, object]],
    aliases: dict[str, str],
) -> tuple[str | None, str | None]:
    source_code = (record.source_country_id or "").upper()
    if source_code in countries_by_code:
        return source_code, "SOURCE_ISO3"
    if record.source_country_name and record.source_country_name in aliases:
        code = aliases[record.source_country_name]
        if code in countries_by_code:
            return code, "NAME_ALIAS"
    return None, None


def _validate_values(
    definition: ProbeDefinition, record: ParsedProbeRecord
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    for rule in definition.component_rules:
        if rule.component_id not in record.values:
            reasons.append(f"VAL_COMPONENT_MISSING:{rule.component_id}")
            continue
        value = record.values[rule.component_id]
        if rule.minimum is not None and value < rule.minimum:
            reasons.append(f"VAL_VALUE_OUT_OF_RANGE:{rule.component_id}")
        if rule.maximum is not None and value > rule.maximum:
            reasons.append(f"VAL_VALUE_OUT_OF_RANGE:{rule.component_id}")
    return not reasons, tuple(sorted(set(reasons)))


def _country_result(
    definition: ProbeDefinition,
    country: dict[str, object],
    record: ParsedProbeRecord | None,
    mapped_by: str | None,
) -> CountryProbeResult:
    base = {
        "criterion_id": definition.criterion_id,
        "source_candidate_id": definition.source.source_candidate_id,
        "country_code": str(country["code"]),
        "display_name": str(country["display_name"]),
        "blocker_codes": definition.blocker_codes,
    }
    if record is None:
        return CountryProbeResult(
            **base,
            source_country_id=None,
            source_country_name=None,
            mapped_by=None,
            status="missing",
            presence_state="MISSING",
            freshness_state="NOT_APPLICABLE",
            parse_state="NOT_APPLICABLE",
            validation_state="NOT_APPLICABLE",
            values={},
            reference_start=None,
            reference_end=None,
            artifact_ids=(),
            record_locators=(),
            reason_codes=("COV_SOURCE_RECORD_MISSING",),
        )
    if not record.parse_succeeded:
        return CountryProbeResult(
            **base,
            source_country_id=record.source_country_id,
            source_country_name=record.source_country_name,
            mapped_by=mapped_by,
            status="parse_failed",
            presence_state="PRESENT",
            freshness_state="NOT_APPLICABLE",
            parse_state="PARSE_FAILED",
            validation_state="NOT_APPLICABLE",
            values={},
            reference_start=record.reference_start,
            reference_end=record.reference_end,
            artifact_ids=record.artifact_ids,
            record_locators=record.record_locators,
            reason_codes=record.parse_reason_codes or ("PRS_PARSE_FAILED",),
        )
    valid, validation_reasons = _validate_values(definition, record)
    year = int(record.reference_end) if record.reference_end else 0
    fresh = year >= definition.freshness_min_year
    if not valid:
        status = "invalid"
        reasons = validation_reasons
    elif not fresh:
        status = "stale"
        reasons = ("FRS_STALE",)
    elif definition.rejection_reason_codes:
        status = "rejected"
        reasons = definition.rejection_reason_codes
    else:
        status = "valid"
        reasons = ()
    return CountryProbeResult(
        **base,
        source_country_id=record.source_country_id,
        source_country_name=record.source_country_name,
        mapped_by=mapped_by,
        status=status,
        presence_state="PRESENT",
        freshness_state="FRESH" if fresh else "STALE",
        parse_state="PARSED",
        validation_state="VALID" if valid else "INVALID",
        values=dict(sorted(record.values.items())),
        reference_start=record.reference_start,
        reference_end=record.reference_end,
        artifact_ids=record.artifact_ids,
        record_locators=record.record_locators,
        reason_codes=reasons,
    )


def _summarize(
    definition: ProbeDefinition,
    run_id: str,
    mode: str,
    timestamp: str,
    universe_id: str,
    results: list[CountryProbeResult],
    unmapped: list[dict[str, object]],
    artifacts: list[RawArtifact],
) -> dict[str, object]:
    status_counts = Counter(item.status for item in results)
    found = sum(item.presence_state == "PRESENT" for item in results)
    fresh = sum(item.freshness_state == "FRESH" for item in results)
    parsed = sum(item.parse_state == "PARSED" for item in results)
    validated = sum(item.validation_state == "VALID" for item in results)
    return {
        "schema_version": PROBE_SCHEMA_VERSION,
        "run_id": run_id,
        "criterion_id": definition.criterion_id,
        "criterion_name": definition.name,
        "source_candidate_id": definition.source.source_candidate_id,
        "publisher": definition.source.publisher,
        "dataset": definition.source.dataset,
        "mode": mode,
        "retrieval_time": timestamp,
        "source_version": definition.source.source_version,
        "dataset_version": definition.source.dataset_version,
        "universe_id": universe_id,
        "denominator": len(results),
        "freshness_min_year": definition.freshness_min_year,
        "minimum_probe_coverage_count": definition.minimum_coverage_count,
        "found": found,
        "fresh": fresh,
        "parsed": parsed,
        "validated": validated,
        "valid": status_counts["valid"],
        "missing": status_counts["missing"],
        "stale": status_counts["stale"],
        "parse_failed": status_counts["parse_failed"],
        "invalid": status_counts["invalid"],
        "rejected": status_counts["rejected"],
        "unmapped": len(unmapped),
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_codes": list(definition.blocker_codes),
        "rejection_reason_codes": list(definition.rejection_reason_codes),
        "probe_threshold_passed": (
            status_counts["valid"] >= definition.minimum_coverage_count
            and not definition.rejection_reason_codes
        ),
        "full_91_passed": status_counts["valid"] == len(results),
        "raw_artifact_checksums": {
            item.requested_url: f"sha256:{item.sha256}" for item in artifacts
        },
    }


def _render_report(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# Feasibility probe: {summary['criterion_id']} — {summary['criterion_name']}",
            "",
            "> Research output only. This is not production ingestion and cannot activate a release.",
            "",
            f"- Run: `{summary['run_id']}`",
            f"- Source candidate: `{summary['source_candidate_id']}`",
            f"- Publisher/dataset: {summary['publisher']} — {summary['dataset']}",
            f"- Source version: `{summary['source_version']}`",
            f"- Retrieval/replay time: `{summary['retrieval_time']}`",
            f"- Universe: `{summary['universe_id']}` ({summary['denominator']} countries)",
            f"- Freshness rule: reference year >= {summary['freshness_min_year']}",
            "",
            "## Coverage",
            "",
            "| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {summary['found']} | {summary['fresh']} | {summary['parsed']} | "
                f"{summary['validated']} | {summary['valid']} | {summary['missing']} | "
                f"{summary['stale']} | {summary['parse_failed']} | {summary['invalid']} | "
                f"{summary['rejected']} | {summary['unmapped']} |"
            ),
            "",
            "## Decision gates",
            "",
            (
                f"- Phase 3 probe threshold ({summary['minimum_probe_coverage_count']}): "
                f"**{'PASS' if summary['probe_threshold_passed'] else 'FAIL'}**"
            ),
            (
                f"- Full stable-universe coverage: "
                f"**{'PASS' if summary['full_91_passed'] else 'FAIL'}**"
            ),
            f"- Candidate blockers: {', '.join(summary['blocker_codes']) or 'none'}",
            (
                f"- Candidate rejection reasons: "
                f"{', '.join(summary['rejection_reason_codes']) or 'none'}"
            ),
            "",
            (
                "See `country-results.jsonl` for one explicit outcome per stable country, "
                "`unmapped-records.jsonl` for source identities outside the registry, and "
                "`raw-artifacts.json` for content-addressed provenance."
            ),
            "",
        ]
    )


def _capture_payloads(
    definition: ProbeDefinition,
    payloads: list[tuple[bytes, str, str, dict[str, object]]],
    raw_repository: RawArtifactRepository,
    timestamp: str,
) -> list[RawArtifact]:
    registration = _source_registration(definition)
    if len(payloads) != len(definition.source.access_urls):
        raise ValueError("Artifact count must equal the definition's access URL count.")
    artifacts = []
    for requested_url, payload in zip(definition.source.access_urls, payloads, strict=True):
        body, final_url, media_type, metadata = payload
        artifacts.append(
            raw_repository.capture(
                registration,
                body,
                requested_url=requested_url,
                final_url=final_url,
                retrieved_at=timestamp,
                media_type=media_type,
                **metadata,
            )
        )
    return artifacts


def _load_artifacts(
    manifest_path: Path, raw_repository: RawArtifactRepository
) -> list[RawArtifact]:
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise TypeError("Raw artifact manifest must be a JSON array.")
    artifacts = [RawArtifact(**item) for item in value]
    for artifact in artifacts:
        raw_repository.load(artifact)
    return artifacts


def run_probe(
    definition: ProbeDefinition,
    run_id: str,
    *,
    mode: str,
    output_root: Path | str = "data/reports/feasibility-probes",
    raw_root: Path | str = "data/raw/feasibility-probes",
    universe_path: Path | str = DEFAULT_UNIVERSE_PATH,
    release_root: Path | str = "data/releases",
    fixture_paths: tuple[Path, ...] = (),
    artifact_manifest: Path | None = None,
    fetcher: Callable | None = None,
    clock: Callable[[], datetime] | None = None,
) -> tuple[Path, dict[str, object]]:
    """Run a fixture, online, or offline probe without touching release state."""

    if mode not in {"fixture", "online", "offline"}:
        raise ValueError("Probe mode must be fixture, online, or offline.")
    if definition.adapter_id not in ADAPTERS:
        raise ValueError(f"Unknown probe adapter: {definition.adapter_id}")
    release_path = Path(release_root)
    active_before = _active_pointer_bytes(release_path)
    raw_repository = RawArtifactRepository(raw_root)
    now = (clock or (lambda: datetime.now(UTC)))()
    timestamp = now.isoformat()
    if mode == "fixture":
        if len(fixture_paths) != len(definition.source.access_urls):
            raise ValueError("Fixture count must equal the definition's access URL count.")
        payloads = [
            (
                path.read_bytes(),
                definition.source.access_urls[index],
                "application/json" if path.suffix == ".json" else "text/csv",
                {"http_status": 200},
            )
            for index, path in enumerate(fixture_paths)
        ]
        artifacts = _capture_payloads(definition, payloads, raw_repository, timestamp)
    elif mode == "online":
        if fetcher is None:
            from konsider.ingestion.worker import fetch_url

            fetcher = fetch_url
        payloads = []
        for url in definition.source.access_urls:
            fetched = fetcher(url)
            if len(fetched) == 3:
                body, final_url, media_type = fetched
                metadata = {"http_status": 200}
            else:
                body, final_url, media_type, metadata = fetched
            payloads.append((body, final_url, media_type, metadata))
        artifacts = _capture_payloads(definition, payloads, raw_repository, timestamp)
    else:
        if artifact_manifest is None:
            raise ValueError("Offline probe mode requires an artifact manifest.")
        artifacts = _load_artifacts(artifact_manifest, raw_repository)
        if artifacts:
            timestamp = max(item.retrieved_at for item in artifacts)

    artifact_inputs = tuple(
        ArtifactInput(
            artifact_id=item.artifact_id,
            requested_url=item.requested_url,
            body=raw_repository.load(item),
        )
        for item in artifacts
    )
    parsed = ADAPTERS[definition.adapter_id].parse(artifact_inputs, definition.adapter_options)
    universe_id, countries = _load_universe(Path(universe_path))
    countries_by_code = {str(item["code"]): item for item in countries}
    aliases = dict(COUNTRY_ALIASES)
    aliases.update({str(item["display_name"]): str(item["code"]) for item in countries})
    mapped: dict[str, tuple[ParsedProbeRecord, str]] = {}
    duplicate_codes: set[str] = set()
    unmapped = []
    for record in parsed.records:
        code, mapped_by = _map_record(record, countries_by_code, aliases)
        if code is None:
            unmapped.append(
                {
                    "source_country_id": record.source_country_id,
                    "source_country_name": record.source_country_name,
                    "record_locators": list(record.record_locators),
                    "reason_codes": ["MAP_NO_STABLE_COUNTRY_ID"],
                }
            )
            continue
        if code in mapped:
            duplicate_codes.add(code)
            continue
        mapped[code] = (record, str(mapped_by))
    results = []
    for code in sorted(countries_by_code):
        record_and_method = mapped.get(code)
        result = _country_result(
            definition,
            countries_by_code[code],
            record_and_method[0] if record_and_method else None,
            record_and_method[1] if record_and_method else None,
        )
        if code in duplicate_codes:
            result = replace(
                result,
                status="invalid",
                validation_state="INVALID",
                reason_codes=tuple(sorted(set(result.reason_codes) | {"MAP_DUPLICATE_COUNTRY"})),
            )
        results.append(result)
    summary = _summarize(
        definition, run_id, mode, timestamp, universe_id, results, unmapped, artifacts
    )
    output = Path(output_root) / run_id
    output.mkdir(parents=True, exist_ok=False)
    _write_json(output / "definition.json", definition.to_dict())
    _write_json(output / "sources.json", [_source_registration(definition).to_dict()])
    _write_json(output / "raw-artifacts.json", [item.to_dict() for item in artifacts])
    _write_jsonl(output / "country-results.jsonl", [item.to_dict() for item in results])
    _write_jsonl(output / "unmapped-records.jsonl", unmapped)
    _write_json(output / "summary.json", summary)
    write_text_lf(output / "report.md", _render_report(summary))
    payload_names = (
        "definition.json",
        "sources.json",
        "raw-artifacts.json",
        "country-results.jsonl",
        "unmapped-records.jsonl",
        "summary.json",
        "report.md",
    )
    checksums = {
        name: f"sha256:{hashlib.sha256((output / name).read_bytes()).hexdigest()}"
        for name in payload_names
    }
    _write_json(
        output / "manifest.json",
        {
            "schema_version": "feasibility-probe-manifest-1.0",
            "run_id": run_id,
            "files": checksums,
            "non_publishing": True,
        },
    )
    if _active_pointer_bytes(release_path) != active_before:
        raise RuntimeError("Feasibility probe changed the active release pointer.")
    return output, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a non-publishing feasibility probe")
    parser.add_argument("--definition", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("fixture", "online", "offline"), required=True)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--artifacts")
    parser.add_argument("--output-root", default="data/reports/feasibility-probes")
    parser.add_argument("--raw-root", default="data/raw/feasibility-probes")
    parser.add_argument("--universe", default=str(DEFAULT_UNIVERSE_PATH))
    args = parser.parse_args()
    output, summary = run_probe(
        load_definition(args.definition),
        args.run_id,
        mode=args.mode,
        output_root=args.output_root,
        raw_root=args.raw_root,
        universe_path=args.universe,
        fixture_paths=tuple(Path(item) for item in args.fixture),
        artifact_manifest=Path(args.artifacts) if args.artifacts else None,
    )
    print(f"Criterion: {summary['criterion_id']}")
    print(f"Valid: {summary['valid']}/{summary['denominator']}")
    print(f"Probe threshold: {'PASS' if summary['probe_threshold_passed'] else 'FAIL'}")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
