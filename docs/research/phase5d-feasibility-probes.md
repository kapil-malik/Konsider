# Phase 5D feasibility probes

Phase 5D introduces a small, deterministic framework for testing whether a
candidate criterion can be supported by a named source. It is a research
instrument, not a production ingestion path. Probe outputs never update the
active release, application API, scoring logic, or user interface.

The first two framework proofs are:

| Criterion | Adapter | Fixture outcome | Purpose |
|---|---|---:|---|
| C30 International migrant stock | World Bank indicator JSON | 91/91 valid | Clean full-universe path |
| C11 Labour-market strength | ILOSTAT bulk CSV composite | 88/91 valid; ATG, GRD, and UKR explicitly missing | Partial-coverage and missing-country path |

These outcomes use schema-faithful synthetic fixtures. They prove framework
behaviour and do not establish real-world source coverage. An online probe or
separate Phase 5C evidence review is required before making a coverage claim.

## Design and boundaries

Each probe definition records the criterion, adapter, publisher and dataset,
source identifiers and URLs, access method, methodology and licence evidence,
version or edition, retrieval date, observation type and scope, freshness
rule, validation rules, and known blockers.

Source-specific adapters translate publisher files into a common observation
model. The shared runner then:

1. captures source bytes through the existing content-addressed raw-artifact
   repository;
2. maps source country identifiers to the stable 91-country registry;
3. evaluates presence, freshness, parsing, and validation independently;
4. assigns explicit country-level outcomes and reason codes;
5. emits deterministic Markdown and machine-readable reports; and
6. verifies that the active release pointer did not change.

Raw artifacts are stored below `data/raw/feasibility-probes/`, which is ignored
by Git. The reports retain their SHA-256 checksums and repository-relative
paths so the exact captured artifacts can be replayed offline.

## Running the examples

From the repository root:

```powershell
python -m konsider.research.feasibility_probe `
  --definition data/research/phase5d/c30-world-bank.json `
  --run-id phase5d-c30-fixture `
  --mode fixture `
  --fixture tests/fixtures/phase5d/c30-world-bank.json
```

```powershell
python -m konsider.research.feasibility_probe `
  --definition data/research/phase5d/c11-ilostat.json `
  --run-id phase5d-c11-fixture `
  --mode fixture `
  --fixture tests/fixtures/phase5d/c11-unemployment.csv `
  --fixture tests/fixtures/phase5d/c11-employment.csv `
  --fixture tests/fixtures/phase5d/c11-participation.csv
```

To rebuild the deterministic synthetic fixtures:

```powershell
python scripts/build_phase5d_fixtures.py
```

To fetch the URLs declared in a definition instead of using fixtures, use
`--mode online`. This captures the received bytes but does not imply that
licensing, methodology, or coverage has been approved.

```powershell
python -m konsider.research.feasibility_probe `
  --definition data/research/phase5d/c30-world-bank.json `
  --run-id c30-online-YYYY-MM-DD `
  --mode online
```

For offline replay, pass a prior run's raw-artifact manifest:

```powershell
python -m konsider.research.feasibility_probe `
  --definition data/research/phase5d/c30-world-bank.json `
  --run-id c30-offline-replay `
  --mode offline `
  --artifacts data/reports/feasibility-probes/phase5d-c30-fixture/raw-artifacts.json
```

## Report files

Every run is written to
`data/reports/feasibility-probes/<run-id>/`:

| File | Contents |
|---|---|
| `definition.json` | Normalized probe definition |
| `sources.json` | Source and evidence metadata |
| `raw-artifacts.json` | Checksums and paths for captured inputs |
| `country-results.jsonl` | One result per stable-universe country |
| `unmapped-records.jsonl` | Source records that could not be mapped |
| `summary.json` | Counts, thresholds, blockers, and pass/fail findings |
| `report.md` | Human-readable result |
| `manifest.json` | SHA-256 checksum for every report file |

The summary reports counts for `found`, `fresh`, `parsed`, `validated`,
`valid`, `missing`, `stale`, `parse_failed`, `invalid`, `rejected`, and
`unmapped`. These are related dimensions rather than a single mutually
exclusive funnel. Each country also receives a final status and explicit
reason codes.

`probe_threshold_passed` answers whether the definition's research threshold
was reached. `full_91_passed` separately records whether all 91 stable
countries produced valid observations. A threshold pass therefore cannot be
mistaken for full coverage.

## Adding a probe

1. Add a definition under `data/research/phase5d/`.
2. Implement a publisher-specific adapter in
   `src/konsider/research/probe_adapters.py` and register its adapter name.
3. Add the smallest schema-faithful fixture needed to exercise the relevant
   path.
4. Add tests for country mapping, freshness boundaries, validation, counts,
   reason codes, determinism, offline replay, and active-release isolation.
5. Run the fixture probe and review both `report.md` and the machine-readable
   outputs.

Production ingestion remains a separate decision. A successful feasibility
probe does not select an indicator, approve a licence, authorize publication,
define scoring transformations, or modify a release.
