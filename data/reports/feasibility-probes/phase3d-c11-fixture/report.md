# Feasibility probe: C11 — Overall job-market opportunity

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase3d-c11-fixture`
- Source candidate: `C11-ILO-MODEL-2025`
- Publisher/dataset: International Labour Organization (ILOSTAT) — ILOSTAT bulk download — modelled labour estimates
- Source version: `ILOSTAT catalogue updated 2025-12-02`
- Retrieval/replay time: `2026-07-26T15:49:40.963334+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2025

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 88 | 88 | 88 | 88 | 88 | 3 | 0 | 0 | 0 | 0 | 0 |

## Decision gates

- Phase 3 probe threshold (82): **PASS**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: COV_NOT_FULL_91
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
