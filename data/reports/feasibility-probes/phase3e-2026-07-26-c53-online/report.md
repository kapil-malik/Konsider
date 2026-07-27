# Feasibility probe: C53 — Basic water and sanitation service access

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase3e-2026-07-26-c53-online`
- Source candidate: `C53-JMP-WDI-BASIC`
- Publisher/dataset: WHO/UNICEF JMP via World Bank WDI — World Development Indicators — basic drinking water and sanitation
- Source version: `JMP 2025 release; observations queried for 2022-2024`
- Retrieval/replay time: `2026-07-26T16:41:09.278199+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2022

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 89 | 89 | 89 | 86 | 86 | 2 | 0 | 0 | 3 | 0 | 159 |

## Decision gates

- Phase 3 probe threshold (82): **PASS**
- Full stable-universe coverage: **FAIL**
- Candidate blockers: CMP_BASIC_NOT_SAFELY_MANAGED, GRA_LOCAL_VARIATION, COV_NOT_FULL_91
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
