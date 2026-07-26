# Feasibility probe: C11 — Overall job-market opportunity

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase5e-2026-07-26-c11-online`
- Source candidate: `C11-ILO-MODEL-2025`
- Publisher/dataset: International Labour Organization (ILOSTAT) — ILOSTAT bulk download — modelled labour estimates
- Source version: `ILOSTAT catalogue updated 2025-12-02`
- Retrieval/replay time: `2026-07-26T16:40:55.615165+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2025

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 89 | 88 | 89 | 89 | 88 | 2 | 1 | 0 | 0 | 0 | 187 |

## Decision gates

- Phase 5 probe threshold (82): **PASS**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: COV_NOT_FULL_91, RED_SHARED_COMPONENTS, CMP_MODELLED_ESTIMATES
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
