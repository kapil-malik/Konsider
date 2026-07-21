# Data refresh worker

Status: six-criterion local worker and five-criterion publication gate implemented

Last updated: 2026-07-20

## Responsibility

The worker converts registered official source data into an immutable, reproducible local release.
It does not serve user requests or mutate a published release. Raw third-party payloads remain in the
ignored, content-addressed local store.

```powershell
$env:PYTHONPATH = "src"
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N \
  --source-version SOURCE_ID=VERSION  # repeat for every registered source
python -m konsider.ingestion.worker replay data\releases\2026-07-20.2
```

## Pipeline

1. Freeze source registration, URLs, methodology, licence/redistribution evidence, attribution,
   source version, parser, and expected country/criterion scope.
2. Fetch with bounded retries and capture exact bytes, final URL, status, retrieval timestamp,
   response headers, byte count, and SHA-256. Paginated connectors follow continuation metadata or
   stop at an empty page and do not retain an unnecessary terminal empty artifact.
3. Parse source-specific records and write normalized observations with exact artifact plus JSON
   record/workbook-cell provenance, parser/method version, type, unit, period, scope, quality flags,
   and component lineage for derived values.
4. Record one attempt for every expected source/country/criterion combination as `success`,
   `no_data`, `failed`, or `rejected`.
5. Apply versioned provisional scoring and run winsorized min-max, percentile, fixed-threshold,
   country-set, and tight-cluster sensitivity experiments.
6. Validate structural contracts separately from criterion product readiness: schema compatibility,
   checksums, HTTP metadata, registration, provenance, attempts, type/unit/range/flags, coverage,
   freshness, score lineage, and material changes from the previous active release.
7. Write a draft and publish atomically only if structural validation passes and at least five
   criteria are ready. Published directories and previous releases are never edited.

## Current sources

- WDI PM2.5 `EN.ATM.PM25.MC.M3`;
- WDI homicide `VC.IHR.PSRC.P5`, with UNODC lineage;
- World Bank HNP UHC `SH.UHC.SRVS.CV.XD` (captured but non-ready due to 2021 freshness);
- WDI ICP PPP/exchange inputs, emitted only as broad cost bands;
- WBL 2026 Legal Framework economy index; and
- experimental WDI infrastructure components for internet, fixed broadband, and LPI infrastructure.

## Release handshake

`manifest.json` declares schema, source/scoring/parser/method versions, creation/publication times,
artifact and payload checksums, aggregate release checksum, previous release, validation summary, and
replay metadata. `observations.jsonl`, `scores.jsonl`, `attempts.jsonl`, `raw-artifacts.json`,
`sources.json`, `validation.json`, and `scoring-sensitivity.json` are checksum-covered payloads.

Replay validates those checksums, loads the release-embedded registrations, reparses local raw bytes,
and regenerates observations and scores using the release's schema/scoring profile. Historic version-2
releases retain their legacy parsers and scoring behavior.

## Failure policy and tests

- Network/schema/parser failures become explicit attempts and cannot erase the active release.
- Missing or stale data is never filled from fixtures.
- A structurally valid candidate with fewer than five ready criteria cannot be promoted.
- Tests cover source parsing, provenance, dynamic pagination, scoring sensitivity, validation
  failures, immutable publication, readiness-gate refusal, manifest checksums, replay, and tampering.

AWS scheduling/storage adapters remain deferred. They must wrap the same pipeline rather than create a
second scoring or publication implementation.

## Controlled annual and future refreshes

Freshness is evaluated against the injected refresh clock/year; tests do not depend on the machine's
calendar. World Bank discovery ranges end at the current refresh year instead of 2026. Every refresh
requires explicit acknowledgement of every registered `source_version`; if upstream content or
version changes, update and audit the registration before fetching so new bytes cannot carry an old
frozen label.

WBL workbook URLs are year-specific. For each annual WBL update, review the official download page,
licence and methodology; update the URL, `dataset_version`, `source_version`, reference period,
parser fixture, and expected workbook layout together; run parser, validation, replay, and material-
change review; then publish under a new release ID. Never replace the WBL URL or data inside an
existing published release.
