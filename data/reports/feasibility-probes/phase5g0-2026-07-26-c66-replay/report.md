# Feasibility probe: C66 — Extreme-weather risk

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase5g0-2026-07-26-c66-replay`
- Source candidate: `C66-INFORM-RISK-2026-V072`
- Publisher/dataset: INFORM / European Commission Joint Research Centre — INFORM Risk Index 2026
- Source version: `31 March 2026 workbook`
- Retrieval/replay time: `2026-07-26T17:39:53.936659+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2026

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 91 | 91 | 91 | 91 | 91 | 0 | 0 | 0 | 0 | 0 | 100 |

## Decision gates

- Phase 5 probe threshold (82): **PASS**
- Full stable-universe coverage: **PASS**
- Candidate blockers: LIC_COMPONENT_SOURCE_CHAIN, SCO_WEIGHTS_REQUIRED, CMP_LOCAL_VARIATION
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
