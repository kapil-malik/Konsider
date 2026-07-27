# Phase 3E deterministic measured probes

Phase 3E ran the Phase 3D research framework against the exact approved live sources for C08, C11,
C30, C29, C48, C49, and C53. These are non-publishing feasibility results: no source was added to
production ingestion, no score was published, no value was imputed, and the active release remained
unchanged.

The complete aggregate report is at
`data/reports/feasibility-probes/phase3e-deterministic-2026-07-26/report.md`. Its adjacent JSON, CSV,
country-status matrix, artifact inventory, replay evidence, and manifest are the authoritative
machine-readable outputs.

## Measured results

| Criterion | Valid | Missing | Stale | Invalid | Threshold | Phase 3E recommendation |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| C08 | 87/91 | 2 | 1 | 1 | pass | experimental candidate |
| C11 | 88/91 | 2 | 1 | 0 | pass | production candidate |
| C30 | 91/91 | 0 | 0 | 0 | pass | production candidate |
| C29 | 91/91 | 0 | 0 | 0 | pass | experimental candidate |
| C48 | 91/91 | 0 | 0 | 0 | pass | production candidate |
| C49 | 91/91 | 0 | 0 | 0 | pass | production candidate |
| C53 | 86/91 | 2 | 0 | 3 | pass | reserve candidate |

All seven offline replays reproduced the exact country-result bytes and normalized summaries from
their captured content-addressed artifacts.

## Interpretation

- C08 passes the coverage gate but remains experimental until the HLO, LAYS, or published schooling
  component is selected. The live file also showed that the schooling component is not a 0–100
  percentage.
- C11 passes with ATG and GRD missing and UKR stale under the 2025 freshness rule.
- C30, C48, and C49 have complete current coverage. C30 still needs a scoring-direction decision;
  both WGI candidates need uncertainty treatment.
- C29 has complete source coverage but remains experimental until currency regimes, breaks,
  transformations, and component weighting are specified.
- C53 reproduces the expected 86 valid countries, but basic-service access is a weak proxy for
  drinking-water safety and continuity and may offer little discrimination among likely
  destinations.

Raw source bytes remain below the ignored `data/raw/feasibility-probes/` path. Exact URLs,
checksums, HTTP metadata, versions, licence evidence, and attribution are retained in each run's
committed report artifacts.
