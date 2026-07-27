# Phase 3G-0 final source probes

Status: completed 2026-07-26; non-publishing research

These probes tested the four unresolved Phase 3F candidates against exact official distributions.
Online runs captured immutable raw artifacts; replay runs reused those bytes. Coverage and freshness
below are verified measurements. Product dispositions remain Konsider policy decisions.

| Candidate | Verified source and result | Replay | Decision |
| --- | --- | --- | --- |
| Health spending | WHO Global Health Expenditure Database, March 2026 workbook: 90/91 valid; Ukraine's latest value is 2021 and stale under the approved rule. | Exact online/offline agreement. | Keep conditional; do not add to the current production portfolio. |
| Disaster-risk resilience | INFORM Risk 2026 v0.7.2 workbook: 91/91 valid. | Exact online/offline agreement. | Keep experimental. Component-chain licensing, weighting, and national-versus-local interpretation require further review. |
| Normal working hours | ILOSTAT bulk CSV, `HOW_TEMP_SEX_NB_A`: 72/91 fresh and valid, 14 missing, 5 stale. | Exact online/offline agreement. | Reserve; current coverage is below the 90% gate. |
| Citizenship access | GLOBALCIT Citizenship Law Dataset v3: official 191-country coverage and licence evidence verified. | Not run: no stable, version-pinned machine-download URL could be resolved. | Defer as context/research until a reproducible archive is available. |

The evidence is stored under
`data/reports/feasibility-probes/phase3g0-2026-07-26-*-online/` and matching `*-replay/`
directories. Probe definitions are under `data/research/phase3g0/`. These outputs do not modify
`data/releases/active.json` and are not ranking inputs.

No fixture fallback, imputation, or proxy substitution was used. A source being authoritative does
not by itself establish readiness: exact distribution, stable retrieval, licensing, coverage,
freshness, semantic fit, and scoring all remain separate gates.
