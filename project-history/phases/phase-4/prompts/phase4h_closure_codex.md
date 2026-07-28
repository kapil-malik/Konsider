# Prompt — Phase 4H: End-to-End Verification and Closure

## Intended for
Codex in the local Konsider repository, followed by review in ChatGPT Desktop Work or Web ChatGPT.

## Inputs
- Completed Phase 4A–4G outputs.
- New active release, if Phase 4F published one.
- Current backend, API, UI, CI, roadmap, and documentation.

## Objective

Verify and close **Phase 4 — Uncertainty-Aware Ranking Model** without weakening the evidence-first guarantees established in Phases 1–3.

## End-to-end scenarios

Test at minimum:

1. FCC-only profile: 91 countries, unchanged ranking semantics.
2. PCC present but below Medium: ignored completely.
3. One active PCC with three excluded countries.
4. Active PCC combination with five excluded countries.
5. Combination with six excluded countries and heightened disclosure.
6. Combination with nine excluded countries.
7. Ten excluded countries: PCC-inclusive ranking blocked and R0 returned.
8. `ROBUST_TOP_K`.
9. `POTENTIALLY_AFFECTED`.
10. `BASELINE_TOP_K_EXCLUDED`.
11. top_k 5, 10, and 20.
12. ties at the Kth score.
13. excluded country detail and FCC evidence access.
14. deterministic repeat requests.
15. clean Windows and Linux checkouts.

## Invariants

Prove:

- stable catalog remains 91;
- global core criteria remain 91/91;
- PCC has at least 82 valid countries;
- all 91 attempts exist for every criterion;
- no score exists for a non-valid PCC observation;
- every R1 country has every active criterion;
- one normalised weight vector is used for all R1 countries;
- no imputation;
- no per-country weight renormalisation;
- excluded countries are never assigned final ranks;
- optimistic bounds are diagnostic only;
- API and UI do not duplicate engine logic;
- historical releases remain immutable and loadable;
- offline replay and checksums pass.

## Documentation

Create/update:

- Phase 4 closure report;
- architecture;
- release schema and catalog docs;
- scoring methodology;
- API docs;
- UI docs;
- worker operations;
- implementation history;
- release report;
- roadmap;
- documentation index.

Document the distinction between:

- stable 91-country catalog;
- query-specific eligible ranking universe;
- full-coverage baseline R0;
- final complete-case R1;
- robustness status.

## Quality gates

Run:

- complete pytest suite;
- Ruff;
- Black formatting check;
- Python compileall;
- frontend typecheck;
- frontend unit/component tests;
- production frontend build;
- OpenAPI/documentation contract checks;
- clean-checkout release validation;
- offline replay.

## Closure report

Record:

- approved policy values;
- enabled FCC and PCC;
- actual missing-country unions;
- robustness test results;
- source and scoring limitations;
- final enabled criterion count;
- UI states;
- known gaps;
- future criteria that remain blocked for city/profile/legal/methodology reasons.

Do not claim that Phase 4 solves city-level, occupation-level, household, or applicant-specific ranking.

## Deliverables

- passing end-to-end system;
- Phase 4 closure report;
- roadmap update;
- quality-gate evidence;
- concise list of remaining risks and next phase.
