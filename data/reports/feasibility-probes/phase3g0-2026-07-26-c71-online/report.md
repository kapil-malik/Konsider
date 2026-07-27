# Feasibility probe: C71 — Working-time burden

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase3g0-2026-07-26-c71-online`
- Source candidate: `C71-ILOSTAT-HOW-2026`
- Publisher/dataset: International Labour Organization (ILOSTAT) — Average weekly hours actually worked per employed person by sex
- Source version: `ILOSTAT table of contents updated 7 July 2026`
- Retrieval/replay time: `2026-07-26T17:40:00.087218+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2023

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 77 | 72 | 77 | 77 | 72 | 14 | 5 | 0 | 0 | 0 | 170 |

## Decision gates

- Phase 3 probe threshold (82): **FAIL**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: CMP_NATIONAL_SOURCE_HETEROGENEITY
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
