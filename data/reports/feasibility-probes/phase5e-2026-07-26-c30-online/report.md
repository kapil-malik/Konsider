# Feasibility probe: C30 — Existing immigrant share

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase5e-2026-07-26-c30-online`
- Source candidate: `C30-WDI-MIGRANT`
- Publisher/dataset: World Bank distribution / UN Population Division upstream — World Development Indicators
- Source version: `2024 observations retrieved in July 2026`
- Retrieval/replay time: `2026-07-26T16:40:53.544054+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2024

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 91 | 91 | 91 | 91 | 91 | 0 | 0 | 0 | 0 | 0 | 168 |

## Decision gates

- Phase 5 probe threshold (82): **PASS**
- Full stable-universe coverage: **PASS**
- Candidate blockers: CMP_DEFINITION_AND_IMPUTATION_VARIATION, SCO_DIRECTION_PREFERENCE_UNRESOLVED
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
