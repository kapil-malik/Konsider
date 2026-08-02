# Konsider Phase 6 history

## Purpose

Phase 6 explores career-opportunity evidence without estimating an individual's probability of finding a job, obtaining a credential, securing admission, or qualifying for immigration.

The phase began as a career and engineering-education implementation plan. Phase 6A tested the proposed occupation, education and academic-ecosystem source families and demonstrated material coverage, construct and licensing blockers. Its authoritative prompt and results remain:

- [`01_PHASE_6A_PORTFOLIO_AND_SOURCE_GATES.md`](01_PHASE_6A_PORTFOLIO_AND_SOURCE_GATES.md)
- [`../../../docs/research/phase6a-career-education-source-study.md`](../../../docs/research/phase6a-career-education-source-study.md)
- [`../../../data/reports/phase6a-2026-07-30`](../../../data/reports/phase6a-2026-07-30)

## Phase 6B pivot

After Phase 6A, the original Phase 6B–6G prompt sequence was withdrawn. Those prompt files were deleted and must not be treated as active instructions.

The replacement Phase 6B prompt is:

- [`Konsider Phase 6B Career Opportunity Criteria.pdf`](Konsider%20Phase%206B%20Career%20Opportunity%20Criteria.pdf)

It defines a research-only, non-ranking opportunity filter with three states:

1. `VERIFIED_STRONG_SIGNAL`
2. `STRONG_SIGNAL_NOT_ESTABLISHED`
3. `INSUFFICIENT_EVIDENCE`

`INSUFFICIENT_EVIDENCE` is never a negative conclusion, and none of these states changes affinity scores or country ordering.

Phase 6B stops after product-definition research. It does not authorize changes to runtime schemas, workers, ranking logic, APIs, releases, preference presets or UI.

## Phase 6B outputs

- [`../../../docs/research/phase6b-career-opportunity-study.md`](../../../docs/research/phase6b-career-opportunity-study.md)
- [`../../../data/reports/phase6b-2026-08-02`](../../../data/reports/phase6b-2026-08-02)
- [`research/run_phase6b_opportunity_probe.mjs`](research/run_phase6b_opportunity_probe.mjs)

Any implementation must begin under a separately approved prompt after the owner resolves the decisions recorded in the Phase 6B report.
