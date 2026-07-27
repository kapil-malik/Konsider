# Feasibility probe: C08 — School education quality

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase3e-2026-07-26-c08-online-v2`
- Source candidate: `C08-HCIPLUS-V3`
- Publisher/dataset: World Bank — Human Capital Index Plus
- Source version: `File updated 2026-02-11; panel labels through 2025`
- Retrieval/replay time: `2026-07-26T16:42:28.407644+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2024

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 89 | 88 | 89 | 88 | 87 | 2 | 1 | 0 | 1 | 0 | 96 |

## Decision gates

- Phase 3 probe threshold (82): **PASS**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: COV_NOT_FULL_91, FRS_FILE_CATALOGUE_YEAR_DISCREPANCY, GRA_LOCAL_SCHOOL_VARIATION
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
