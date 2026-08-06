# Worker operations

The active display-metadata migration is overlay `2026-08-07.2`, bound to base `2026-08-07.1`.
Its checksum-backed evidence and rollback record are under
`data/reports/catalog-display-metadata-2026-08-07/`.

The local Python worker downloads registered official data, captures exact raw bytes, parses
source-neutral observations, computes versioned canonical scores, validates a candidate, and
publishes a new immutable release. It does not serve API requests, modify published releases, fill
missing data from fixtures, deploy to AWS, or run on a schedule.

Phase 5C adds `GenericReleaseWorker` and `CurrentReleaseRepository` as the schema-5/catalog-3 build
path. It accepts versioned criterion processors and snapshotted policies for national or locality
evidence. Phase 5G's `phase5_locality_onboarding` command uses this path to migrate the immutable
schema-4 baseline and onboard approved GHSL locality criteria. Schema-5 replay returns a distinct
`SOURCE_BYTES_UNAVAILABLE` status when ignored licensed bytes are absent.

The first production invocation was:

```powershell
python -m konsider.ingestion.phase5_locality_onboarding `
  --release-id 2026-07-29.2 `
  --criterion C66 `
  --criterion C67 `
  --activate
```

The command verifies the retained archive checksum, builds through the generic worker, publishes
without activation, replays every payload from retained inputs, and only then updates
`active.json`.

Replay the active locality release with:

```powershell
python -m konsider.ingestion.phase5_locality_onboarding `
  --replay data\releases\2026-07-29.2
```

## `audit-coverage`

Coverage auditing is separate from refresh and can never activate a release.

```text
python -m konsider.ingestion.worker audit-coverage \
  --universe UNIVERSE_JSON \
  --audit-id AUDIT_ID \
  --mode online|offline \
  [--artifacts RAW_ARTIFACT_MANIFEST] \
  [--candidate-limit N]
```

Online example:

```bash
python -m konsider.ingestion.worker audit-coverage \
  --universe data/country-universes/popular-relocation-v1.json \
  --audit-id coverage-YYYY-MM-DD.N \
  --mode online
```

Offline replay:

```bash
python -m konsider.ingestion.worker audit-coverage \
  --universe data/country-universes/popular-relocation-v1.json \
  --audit-id coverage-YYYY-MM-DD.N-replay \
  --mode offline \
  --artifacts data/reports/country-coverage/coverage-YYYY-MM-DD.N/raw-artifacts.json
```

Online mode fetches official UN M49, UN migrant-stock, World Bank country metadata, the current WBL
workbook, and official CSV ZIP representations of the registered WDI indicators. Offline mode makes
no network calls and requires the retained content-addressed bytes. Both modes produce candidate,
registry, per-criterion, per-country, exclusion, source, artifact, summary, and Markdown reports.
Exit is `0` for PASS and `2` when the complete intersection is below the universe policy minimum,
currently 91. A FAIL is a diagnostic result, not permission to publish. The command compares
`active.json` before and after and raises if it changes.

The Phase 2D.4 `audit-homicide-sources` command was intentionally removed after the final licensing
decision. Its Direct UNODC, UNSD, Eurostat, and OECD adapters were study-only runtime paths. The
committed [Phase 2D.4 findings](../data/homicide-source-feasibility-phase-2d4.md) and machine-readable
reports preserve the investigation.

## Prerequisites

- Python 3.11 or newer and the installation in [local setup](local-setup.md).
- Run CLI commands from the repository root so `data/raw` and `data/releases` resolve correctly.
- A refresh needs outbound HTTPS access. Replay needs the original ignored bytes in `data/raw`.
- Use a new release ID in `YYYY-MM-DD.N` form. The CLI accepts any non-empty string today, but this
  is the operational convention and published IDs must never be reused.

PowerShell and Bash use the same commands except for line continuation (` instead of `\`).

## Discover registered source versions

Refresh requires explicit acknowledgement of every audited source version. This prevents new
upstream bytes from being published under stale registration metadata. Print the exact required
values with the read-only command:

```bash
python -m konsider.ingestion.worker list-sources
```

Current output:

```text
unodc_homicide=VC.IHR.PSRC.P5@WDI-2026-07-13
world_bank_icp=PA.NUS.PRVT.PP+PA.NUS.FCRF@WDI-2026-07-13
world_bank_infrastructure=INFRA-3@WDI-2026-07-13
world_bank_pm25=EN.ATM.PM25.MC.M3@WDI-2026-07-13
world_bank_uhc=SH.UHC.SRVS.CV.XD@HNP-2026-07-01
world_bank_wbl=WBL26_FINAL_ALL@2026-02-23
```

If upstream content or its version changes, audit and update the source registration, parser
fixtures, licence evidence, and expected layout before using the new value. Never acknowledge a
version merely to bypass the guard.

## `refresh`

Syntax:

```text
python -m konsider.ingestion.worker refresh --release-id RELEASE_ID \
  --source-version SOURCE_ID=VERSION [--source-version SOURCE_ID=VERSION ...]
```

Arguments:

| Argument | Required | Meaning |
| --- | --- | --- |
| `--release-id` | yes | New immutable release ID; operational format `YYYY-MM-DD.N`. |
| `--source-version` | yes, repeated | Exact acknowledgement for every registered source. |

Complete Bash example:

```bash
python -m konsider.ingestion.worker refresh --release-id NEXT_RELEASE_ID \
  --source-version unodc_homicide=VC.IHR.PSRC.P5@WDI-2026-07-13 \
  --source-version world_bank_icp=PA.NUS.PRVT.PP+PA.NUS.FCRF@WDI-2026-07-13 \
  --source-version world_bank_infrastructure=INFRA-3@WDI-2026-07-13 \
  --source-version world_bank_pm25=EN.ATM.PM25.MC.M3@WDI-2026-07-13 \
  --source-version world_bank_uhc=SH.UHC.SRVS.CV.XD@HNP-2026-07-01 \
  --source-version world_bank_wbl=WBL26_FINAL_ALL@2026-02-23
```

Complete PowerShell example:

```powershell
python -m konsider.ingestion.worker refresh --release-id NEXT_RELEASE_ID `
  --source-version unodc_homicide=VC.IHR.PSRC.P5@WDI-2026-07-13 `
  --source-version world_bank_icp=PA.NUS.PRVT.PP+PA.NUS.FCRF@WDI-2026-07-13 `
  --source-version world_bank_infrastructure=INFRA-3@WDI-2026-07-13 `
  --source-version world_bank_pm25=EN.ATM.PM25.MC.M3@WDI-2026-07-13 `
  --source-version world_bank_uhc=SH.UHC.SRVS.CV.XD@HNP-2026-07-01 `
  --source-version world_bank_wbl=WBL26_FINAL_ALL@2026-02-23
```

The command prints the published path and exits `0` on success. Fetch or parser failures become
explicit failed attempts; validation then decides whether the candidate is structurally valid and
whether at least five criteria are ready. Publication refusal or invalid arguments raise an error
and return a non-zero process exit. A failed publication may leave `data/releases/.draft/RELEASE_ID`
for diagnosis; it never changes `active.json`. Do not use refresh merely to replay existing bytes.

## `stabilize-baseline`

```text
python -m konsider.ingestion.worker stabilize-baseline PREVIOUS_PATH --release-id RELEASE_ID
```

`PREVIOUS_PATH` is an existing release directory whose raw-artifact metadata will be reprocessed;
`--release-id` must be new. The command uses ignored raw bytes in the default `data/raw`, writes to
the default `data/releases`, prints the published path, and exits `0` on success. It exists for
controlled baseline reprocessing, not ordinary refreshes or in-place correction.

Example:

```bash
python -m konsider.ingestion.worker stabilize-baseline data/releases/2026-07-21.1 \
  --release-id 2026-07-22.2
```

## `replay`

```text
python -m konsider.ingestion.worker replay RELEASE_PATH
```

Replay validates local raw-artifact checksums, declared release payload checksums, the aggregate
release checksum, embedded source registrations, parsing, attempts, observations, and scores. It
prints `replay passed` and exits `0`, or prints `replay failed` and exits `1`. Missing ignored raw
bytes make replay fail even when the committed normalized release is valid for API consumption.

```bash
python -m konsider.ingestion.phase5_locality_onboarding --replay data/releases/2026-07-29.2
```

## Outputs and lineage

```text
source registration
  -> data/raw content-addressed artifact
  -> observation
  -> canonical score
  -> validation report
  -> manifest and immutable publication
```

| Output | Role | Authority |
| --- | --- | --- |
| `data/raw/` | Exact third-party bytes and capture metadata; ignored by Git. | Source input for replay. |
| `data/releases/RELEASE_ID/manifest.json` | Release ID, schema, counts, versions, checksums, readiness summary, previous release, replay metadata. | Publication envelope. |
| `observations.jsonl` | Values, units, periods, quality flags, parser/method versions, and exact record provenance. | Source-of-truth normalized observations. |
| `scores.jsonl` | Versioned canonical 1-10 scores linked to observation IDs. | Source-of-truth canonical scores. |
| `attempts.jsonl` | One expected source/country/criterion result: `success`, `no_data`, `failed`, or `rejected`. | Completeness evidence. |
| `raw-artifacts.json` | URLs, HTTP metadata, local paths, source versions, sizes, and SHA-256 values. | Raw capture inventory. |
| `sources.json` | Frozen source registrations, licence evidence, attribution, methodology, parser, and source version. | Release-specific source contract. |
| `validation.json` | Structural issues, criterion readiness, coverage, blockers, warnings, and aggregate readiness. | Readiness decision. |
| `scoring-sensitivity.json` | Distribution and alternative-method diagnostics. | Diagnostic review record. |
| `data/releases/active.json` | Current release ID and schema major. | Mutable activation pointer only. |
| `data/reports/country-coverage/AUDIT_ID/` | Candidate universe, canonical registry, coverage dimensions, exclusions, sources, and raw checksums. | Non-publishing discovery evidence. |
| `data/reports/homicide-source-feasibility/STUDY_ID/` | Source equivalence, coverage, discrepancies, licensing, and replay evidence. | Non-publishing discovery evidence. |

See [release format](../data/release-format.md) for field and checksum relationships.

## Readiness and failure behavior

Structural validity, criterion readiness, and aggregate product readiness are distinct. A criterion
needs acceptable licence, coverage, freshness, type, unit, flags, provenance, attempts, schemas,
checksums, and versions. Publication requires structural validity and at least five ready criteria.
One failed source produces failed attempts and normally makes that criterion non-ready; if the
aggregate gate then fails, the draft remains inactive. Missing, stale, rejected, or incomparable
data is never imputed from fixtures.

## Inspect and verify a release

PowerShell:

```powershell
Get-Content data\releases\active.json
Get-Content data\releases\2026-07-29.2\manifest.json
Get-Content data\releases\2026-07-29.2\validation.json
python -m konsider.ingestion.phase5_locality_onboarding --replay data\releases\2026-07-29.2
```

Bash:

```bash
python -m json.tool data/releases/active.json
python -m json.tool data/releases/2026-07-29.2/manifest.json
python -m json.tool data/releases/2026-07-29.2/validation.json
python -m konsider.ingestion.phase5_locality_onboarding --replay data/releases/2026-07-29.2
```

API startup performs schema-5, catalog, relationship, and payload-checksum validation through
`CurrentReleaseRepository` even when retained source bytes are unavailable.

## Phase 6 Opportunity Filter publication

The final release was produced with three separately gated commands:

```text
python -m konsider.ingestion.phase6_release_publication build --release-id 2026-08-04.1
python -m konsider.ingestion.phase6_release_publication publish 2026-08-04.1
python -m konsider.ingestion.phase6_release_publication activate 2026-08-04.1
```

`build` verifies retained Phase 6E/F/G checksums, exact accepted state counts, product decisions,
and base-payload identity while leaving `active.json` unchanged. `publish` moves only a validated
draft into the immutable release namespace. `activate` strictly reloads the published release and
atomically writes the matching release/schema pointer. Existing IDs are never reused.

Run `python -m konsider.ingestion.phase6_release_verification` after activation to record active
load and API timings. Future evidence refreshes require a new reviewed prompt, new source captures,
new release ID, reconciliation against accepted thresholds, and the same build/publish/activate
separation. Historical research, source/legal records, and replay manifests must be retained.

## Manual local rollback

There is no rollback CLI. Use this manual procedure only for a compatible published release:

1. Run replay on the target and require exit `0` (or separately validate its schema and checksums if
   raw bytes are unavailable).
2. Back up `active.json` for operational records.
3. Replace only its `release_id` with the target and retain the compatible schema version.
4. Do not edit any file inside either release directory.
5. Restart the API and require healthy status with the intended release ID.

Do not activate `2026-07-20.2` on Linux: its historical CRLF-based manifest is intentionally
immutable and is why packaging-corrected `2026-07-21.1` exists.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Missing or mismatched source versions | Run `list-sources`; update registrations first if upstream versions changed. |
| Network failure | Inspect failed attempts/draft; retry under a new ID only after the cause is understood. |
| Missing raw bytes during replay | Restore the captured content-addressed files to `data/raw`; normalized files alone cannot replay. |
| Checksum mismatch | Treat the release as unavailable; never edit it. Create a corrected release ID. |
| Stale criterion | Review its freshness blocker; do not relabel or impute it. |
| Fewer than five ready criteria | Publication must remain blocked and `active.json` unchanged. |
| Existing release or draft ID | Choose a new `YYYY-MM-DD.N`; never overwrite or delete published history to reuse an ID. |
| Windows/Linux checksum difference | Release files are LF-enforced by `.gitattributes`; use `2026-07-21.1` or later. |

## Historical release inspection

Schema-3/4 releases and their release-scoped catalogs are immutable audit records. They are not
eligible targets for `active.json` and the public API has no compatibility path for them. Internal
audit code must explicitly construct `PublishedReleaseRepository(release_id="...")`; there is no
default or legacy active pointer. Never rewrite a historical release or catalog snapshot.

## Phase 7 TFC release workflow

The destination-rule worker is documented in the
[TFC source and rule workflow](tfc-source-workflow.md). The finalized lifecycle has separate build,
publish, replay, activate and rollback commands and no API-runtime source calls:

```powershell
python -m konsider.ingestion.phase7_release_publication build
python -m konsider.ingestion.phase7_release_publication publish
python -m konsider.ingestion.phase7_release_publication replay
python -m konsider.ingestion.phase7_release_publication activate
```

Build writes under `data/releases/.draft/` and must not change `active.json`. Publish validates the
owner gate and creates immutable `data/releases/2026-08-05.1/`. Activation validates the published
overlay and atomically changes the pointer. Restart the API after pointer changes.

Rollback preserves both immutable releases:

```powershell
python -m konsider.ingestion.phase7_release_publication rollback --release-id 2026-08-04.1
```
