# Phase 6D Opportunity Filter contracts and architecture

Status: complete (contracts only)  
Completed: 2026-08-03  
Implementation commit: pending final commit

## Outcome

Phase 6D establishes versioned, machine-validated Opportunity Filter contracts without onboarding
production evidence, activating filters, changing country affinity scores or ordering, extending API
v2, or adding UI. The public product name is **Opportunity Filters**. `OFC` remains an internal
shorthand only.

Opportunity Filters are a sibling product capability, not ordering criteria. They have no weight,
direction, normalization, score contribution, PCC/LSC activation, imputation rule or ranking
coefficient. Selecting multiple filters is strict `AND`; only `VERIFIED_STRONG_SIGNAL` passes. With
no filter selected, country membership, score and order are unchanged. A valid filtered result may
be empty.

## Architecture decision

[ADR 010](../architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md) records the
decision to keep Opportunity Filters in a separate catalog and release-artifact family. The detailed
[contract guide](../architecture/opportunity-filter-contracts.md) defines artifact ownership,
validation, state semantics, release binding, fixtures and the procedure for adding a future filter.

The contract versions introduced are:

- `opportunity-filter-definition-1.0`
- `opportunity-filter-catalog-1.0`
- `opportunity-filter-evidence-1.0`
- `opportunity-filter-assessment-1.0`
- `opportunity-filter-source-manifest-1.0`
- `opportunity-filter-evidence-policy-1.0`
- `opportunity-filter-threshold-policy-1.0`
- `opportunity-filter-coverage-summary-1.0`
- optional Opportunity Filter binding in `konsider-release-5.1`

The consumer catalog remains `consumer-catalog-3.0`. Release schema `konsider-release-5.0` remains
valid without Opportunity Filter fields.

## Exact enums

### Public states

- `VERIFIED_STRONG_SIGNAL`
- `STRONG_SIGNAL_NOT_ESTABLISHED`
- `INSUFFICIENT_EVIDENCE`

`INSUFFICIENT_EVIDENCE` is never a negative conclusion. Only complete evidence can support
`STRONG_SIGNAL_NOT_ESTABLISHED`.

### Categories and confidence

- categories: `CAREER`, `EDUCATION`
- bands: `HIGH`, `MEDIUM`, `LOW`
- tiers: `HIGH_CONFIDENCE_OBSERVED_HARMONISED`, `HIGH_CONFIDENCE_OBSERVED_NATIONAL`,
  `HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET`, `MEDIUM_CONFIDENCE_MODELLED_HARMONISED`,
  `MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK`, `LOW_CONFIDENCE_SUPPLEMENTAL`

The frozen-research-dataset tier is the source-aligned education tier required by the committed
Phase 6C evidence. It does not invent a finer confidence distinction.

### Reason codes

Positive:

- `SCALE_AND_SHARE_ROUTE_PASSED`
- `EXCEPTIONAL_SCALE_ROUTE_PASSED`
- `EXCEPTIONAL_SPECIALIZATION_ROUTE_PASSED`
- `SKILLED_TRADES_ROUTE_PASSED`
- `CONSTRUCTION_ROUTE_PASSED`
- `SKILLED_TRADES_AND_CONSTRUCTION_ROUTES_PASSED`
- `TOP_100_INSTITUTION_ROUTE_PASSED`
- `TOP_300_BREADTH_ROUTE_PASSED`
- `OUTPUT_AND_BREADTH_ROUTE_PASSED`

Strong signal not established:

- `COMPLETE_EVIDENCE_BELOW_STRONG_THRESHOLD`
- `SCALE_FLOOR_NOT_MET`
- `BREADTH_THRESHOLD_NOT_MET`
- `NO_APPROVED_STRONG_ROUTE_PASSED`

Insufficient evidence:

- `SOURCE_MISSING`
- `EVIDENCE_STALE`
- `UNSUPPORTED_TAXONOMY`
- `INSUFFICIENT_GRANULARITY`
- `CROSSWALK_INCOMPLETE`
- `INCOMPATIBLE_NUMERATOR_DENOMINATOR`
- `SOURCE_LEGALLY_BLOCKED`
- `COUNTRY_ABSENT_FROM_SOURCE_UNIVERSE`
- `INSTITUTION_IDENTITY_UNRESOLVED`
- `SOURCE_DEPENDENCY_UNAVAILABLE`
- `CONFLICTING_EVIDENCE_UNRESOLVED`

## Current-release compatibility

The active release remains `2026-07-29.2`, using `konsider-release-5.0` and
`consumer-catalog-3.0`. It loads and replays without Opportunity Filter artifacts. No active pointer,
release artifact, source evidence, ranking behavior, API schema or web artifact changed.

The additive `konsider-release-5.1` contract may bind six checksummed sibling artifacts: catalog,
country evidence, source manifest, threshold policies, evidence policy and coverage summary. Their
presence and counts are cross-validated. Phase 6D provides only synthetic fixtures; it does not
publish a 5.1 release.

## Changed paths

Contract schemas and indexes:

- `contracts/README.md`
- `contracts/schemas/v3/README.md`
- `contracts/schemas/v3/release-manifest.schema.json`
- `contracts/schemas/v3/opportunity-filter-definition.schema.json`
- `contracts/schemas/v3/opportunity-filter-catalog.schema.json`
- `contracts/schemas/v3/opportunity-filter-evidence.schema.json`
- `contracts/schemas/v3/opportunity-filter-assessment.schema.json`
- `contracts/schemas/v3/opportunity-filter-source-manifest.schema.json`
- `contracts/schemas/v3/opportunity-filter-evidence-policy.schema.json`
- `contracts/schemas/v3/opportunity-filter-threshold-policy.schema.json`
- `contracts/schemas/v3/opportunity-filter-coverage-summary.schema.json`

Typed validation and tests:

- `src/konsider/domain/__init__.py`
- `src/konsider/domain/opportunity_filters.py`
- `tests/unit/test_phase5b_contracts.py`
- `tests/unit/test_phase6d_opportunity_filter_contracts.py`
- `tests/fixtures/phase6d/README.md`
- `tests/fixtures/phase6d/valid/*`

Architecture, product and history documentation:

- `docs/README.md`
- `docs/architecture/system-architecture.md`
- `docs/architecture/opportunity-filter-contracts.md`
- `docs/architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md`
- `docs/data/release-format.md`
- `docs/product/roadmap.md`
- `docs/product/terminology-glossary.md`
- `docs/history/phase6d-opportunity-filter-contracts.md`
- `project-history/phases/phase-6/00_README.md`
- `project-history/phases/phase-6/03_README_EXECUTION_GUIDE.txt`
- `project-history/phases/phase-6/04_PHASE_6D_OFC_PRODUCT_CONTRACTS_AND_ARCHITECTURE.txt`
- `project-history/phases/phase-6/05_PHASE_6E_CAREER_OFC_EVIDENCE_ONBOARDING.txt`
- `project-history/phases/phase-6/06_PHASE_6F_EDUCATION_OFC_EVIDENCE_ONBOARDING.txt`
- `project-history/phases/phase-6/07_PHASE_6G_OFC_FILTER_ENGINE_AND_API.txt`
- `project-history/phases/phase-6/08_PHASE_6H_OFC_UI_AND_EXPLANATIONS.txt`
- `project-history/phases/phase-6/09_PHASE_6I_RELEASE_VERIFICATION_AND_CLOSURE.txt`

The prompt pack is recorded as planning history. Prompts 05–09 are not executed by this phase.

## Verification

Local verification on 2026-08-03:

- targeted Phase 6D and Phase 5B contracts: `70 passed`
- full backend suite: `312 passed` (one non-functional pytest cache warning caused by managed
  Windows directory permissions)
- Ruff: passed
- Black check: 105 files unchanged
- Python compileall for `src` and `tests`: passed
- retained-source replay for active release `2026-07-29.2`: `replay=PASSED`
- regenerated OpenAPI JSON and TypeScript declarations: no Git diff
- current API model/OpenAPI surface regression assertions: passed

## Owner decisions before Phase 6E

Phase 6E must not begin until the owner explicitly accepts or revises all of the following:

1. Keep Opportunity Filters as a separate sibling catalog with filter-only semantics and the exact
   three-state model above.
2. Accept `konsider-release-5.1` as an additive optional binding while retaining
   `consumer-catalog-3.0`.
3. Accept the exact confidence tiers, including
   `HIGH_CONFIDENCE_FROZEN_RESEARCH_DATASET` for the Phase 6C source model.
4. Accept the reason-code vocabulary and the explicit skilled-trades/construction route attribution
   rules.
5. Authorize Phase 6E to onboard the five committed career filters and their production evidence.

No Phase 6E work has started.
