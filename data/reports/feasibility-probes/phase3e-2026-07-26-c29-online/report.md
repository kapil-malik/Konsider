# Feasibility probe: C29 — Currency and macroeconomic stability

> Research output only. This is not production ingestion and cannot activate a release.

- Run: `phase3e-2026-07-26-c29-online`
- Source candidate: `C29-WDI-INFLATION-FXRATE`
- Publisher/dataset: World Bank distribution / IMF IFS upstream — World Development Indicators — inflation and official exchange rate
- Source version: `Annual observations for 2020-2024 retrieved in July 2026`
- Retrieval/replay time: `2026-07-26T16:41:05.328194+00:00`
- Universe: `stable_supported_v1` (91 countries)
- Freshness rule: reference year >= 2023

## Coverage

| Found | Fresh | Parsed | Validated | Valid | Missing | Stale | Parse failed | Invalid | Rejected | Unmapped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 91 | 91 | 91 | 91 | 91 | 0 | 0 | 0 | 0 | 0 | 163 |

## Decision gates

- Phase 3 probe threshold (82): **PASS**
- Full stable-universe coverage: **PASS**
- Candidate blockers: CMP_CURRENCY_REGIME, SCO_COMPOSITE_SENSITIVITY_REQUIRED, OPS_CURRENCY_BREAK_HANDLING_REQUIRED
- Candidate rejection reasons: none

See `country-results.jsonl` for one explicit outcome per stable country, `unmapped-records.jsonl` for source identities outside the registry, and `raw-artifacts.json` for content-addressed provenance.
