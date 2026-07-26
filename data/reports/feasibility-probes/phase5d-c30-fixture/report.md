# Feasibility probe: C30 — Existing immigrant share

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase5d-c30-fixture`
- Source candidate: `C30-WDI-MIGRANT`
- Publisher/dataset: World Bank (distribution) / UN Population Division (upstream) — World Development Indicators
- Source version: `2024 observations retrieved from WDI in July 2026`
- Retrieval/replay time: `2026-07-26T15:49:40.470548+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2024

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 91 | 91 | 91 | 91 | 91 | 0 | 0 | 0 | 0 | 0 | 0 |

## Decision gates

- Phase 5 probe threshold (82): **PASS**
- Full stable-universe coverage: **PASS**
- Candidate blockers: none
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
