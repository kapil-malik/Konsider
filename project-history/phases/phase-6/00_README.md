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

- `Konsider Phase 6B Career Opportunity Criteria.pdf`

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

## Phase 6B.1 gap fill and calibration

Phase 6B.1 tightened source precedence, negative integrity, threshold sensitivity, frozen-shortlist coverage, dependency testing and deterministic replay. It completed the targeted career-evidence follow-up without authorising production work.

- `Konsider Phase 6B.1 Prompt.pdf`
- [`../../../docs/research/phase6b1-career-gap-fill-and-calibration.md`](../../../docs/research/phase6b1-career-gap-fill-and-calibration.md)
- [`../../../data/reports/phase6b1-2026-08-03`](../../../data/reports/phase6b1-2026-08-03)
- [`research/run_phase6b1_gap_fill_and_calibration.mjs`](research/run_phase6b1_gap_fill_and_calibration.mjs)

## Phase 6C education exploration

Phase 6C applies the same evidence discipline to field-specific higher-education research ecosystems while retaining the directions and implementation boundary in the Phase 6C PDF. Its augmented protocol records how Phase 6B.1's methodology is adapted without importing its career criteria.

- `Konsider Phase 6C Higher-Education Opportunity Criteria.pdf`
- [`02_PHASE_6C_AUGMENTED_RESEARCH_PROTOCOL.md`](02_PHASE_6C_AUGMENTED_RESEARCH_PROTOCOL.md)
- [`../../../docs/research/phase6c-education-opportunity-study.md`](../../../docs/research/phase6c-education-opportunity-study.md)
- [`../../../data/reports/phase6c-2026-08-03`](../../../data/reports/phase6c-2026-08-03)
- [`research/run_phase6c_education_opportunity_study.mjs`](research/run_phase6c_education_opportunity_study.mjs)

Phase 6C stops at research and owner decisions. It does not add an education criterion or change any ranking, schema, worker, preset, API, release or UI.

## Phase 6D–6I execution pack

The accepted implementation sequence is indexed by [`03_README_EXECUTION_GUIDE.txt`](03_README_EXECUTION_GUIDE.txt). Phase 6D begins with contracts and architecture only:

- [`04_PHASE_6D_OFC_PRODUCT_CONTRACTS_AND_ARCHITECTURE.txt`](04_PHASE_6D_OFC_PRODUCT_CONTRACTS_AND_ARCHITECTURE.txt)
- [`../../../docs/architecture/opportunity-filter-contracts.md`](../../../docs/architecture/opportunity-filter-contracts.md)
- [`../../../docs/architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md`](../../../docs/architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md)
- [`../../../docs/history/phase6d-opportunity-filter-contracts.md`](../../../docs/history/phase6d-opportunity-filter-contracts.md)

Phase 6D does not onboard evidence, expose API fields, add UI or activate a release.

## Phase 6E career evidence onboarding

Phase 6E promotes the five approved career filters into checksum-bound, deterministic staged
artifacts without activating a release or changing ranking, API or UI behavior:

- [`05_PHASE_6E_CAREER_OFC_EVIDENCE_ONBOARDING.txt`](05_PHASE_6E_CAREER_OFC_EVIDENCE_ONBOARDING.txt)
- [`../../../docs/data/career-opportunity-evidence.md`](../../../docs/data/career-opportunity-evidence.md)
- [`../../../docs/history/phase6e-career-opportunity-evidence.md`](../../../docs/history/phase6e-career-opportunity-evidence.md)
- [`../../../data/reports/phase6e-2026-08-03`](../../../data/reports/phase6e-2026-08-03)

Prompts `06`–`09` remain sequential future instructions. Phase 6F has not started.
