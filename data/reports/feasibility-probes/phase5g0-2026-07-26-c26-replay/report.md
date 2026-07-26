# Feasibility probe: C26 — Financial protection from health costs

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase5g0-2026-07-26-c26-replay`
- Source candidate: `C26-WHO-GHED-2026-03`
- Publisher/dataset: World Health Organization — Global Health Expenditure Database — all data
- Source version: `OOPS%CHE_SHA2011; observations through 2023`
- Retrieval/replay time: `2026-07-26T17:39:23.316444+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2023

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 91 | 90 | 91 | 91 | 90 | 0 | 1 | 0 | 0 | 0 | 104 |

## Decision gates

- Phase 5 probe threshold (82): **PASS**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: CMP_ESTIMATED_VALUES, LIC_REDISTRIBUTION_REVIEW
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
