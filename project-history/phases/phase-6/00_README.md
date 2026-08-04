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

## Phase 6F education evidence onboarding

Phase 6F promotes the four approved research-university ecosystem filters and combines them with
Phase 6E into a deterministic inactive nine-filter candidate:

- [`06_PHASE_6F_EDUCATION_OFC_EVIDENCE_ONBOARDING.txt`](06_PHASE_6F_EDUCATION_OFC_EVIDENCE_ONBOARDING.txt)
- [`../../../docs/data/education-opportunity-evidence.md`](../../../docs/data/education-opportunity-evidence.md)
- [`../../../docs/history/phase6f-education-opportunity-evidence.md`](../../../docs/history/phase6f-education-opportunity-evidence.md)
- [`../../../data/reports/phase6f-2026-08-03`](../../../data/reports/phase6f-2026-08-03)

## Phase 6G filter engine and API

Phase 6G implements strict post-ranking `ALL_REQUIRED` evaluation and additive API v2 transport
against a deterministic nine-filter API candidate. It preserves canonical scores, weights,
contributions, base ranks and survivor order, and leaves the active release pointer and UI
unchanged:

- [`07_PHASE_6G_OFC_FILTER_ENGINE_AND_API.txt`](07_PHASE_6G_OFC_FILTER_ENGINE_AND_API.txt)
- [`../../../docs/product/opportunity-filter-engine.md`](../../../docs/product/opportunity-filter-engine.md)
- [`../../../docs/history/phase6g-opportunity-filter-api.md`](../../../docs/history/phase6g-opportunity-filter-api.md)
- [`../../../data/reports/phase6g-2026-08-03`](../../../data/reports/phase6g-2026-08-03)

## Phase 6H UI and explanations

Phase 6H implements grouped checkbox controls, strict-selection requests, removable active filters,
result and exclusion explanations, country evidence, comparison, responsive behavior and
accessibility over the staged Phase 6G API candidate. It does not calculate filter states, change
affinity, activate the candidate or modify the active release pointer:

- [`08_PHASE_6H_OFC_UI_AND_EXPLANATIONS.txt`](08_PHASE_6H_OFC_UI_AND_EXPLANATIONS.txt)
- [`../../../docs/product/ui.md`](../../../docs/product/ui.md)
- [`../../../docs/product/phase6h-opportunity-filter-ui-test-plan.md`](../../../docs/product/phase6h-opportunity-filter-ui-test-plan.md)
- [`../../../docs/history/phase6h-opportunity-filter-ui.md`](../../../docs/history/phase6h-opportunity-filter-ui.md)

## Phase 6I release verification and closure

Phase 6I published and atomically activated immutable release `2026-08-04.1`. It binds nine
Opportunity Filter definitions and 819 explicit country states under release schema 5.1 while
preserving the Phase 5 ranking payloads byte-for-byte:

- [`09_PHASE_6I_RELEASE_VERIFICATION_AND_CLOSURE.txt`](09_PHASE_6I_RELEASE_VERIFICATION_AND_CLOSURE.txt)
- [`../../../docs/history/phase6-closure-report.md`](../../../docs/history/phase6-closure-report.md)
- [`../../../docs/history/releases/2026-08-04.1.md`](../../../docs/history/releases/2026-08-04.1.md)
- [`../../../data/reports/phase6i-2026-08-04`](../../../data/reports/phase6i-2026-08-04)

Phase 6 is closed. Future work must begin under a separately approved phase prompt.
