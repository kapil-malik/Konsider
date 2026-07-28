# Prompt — Phase 4A: Product Policy and Mathematical Contract

## Intended for
ChatGPT Desktop Work on the Windows laptop.

## Inputs
- Current Konsider repository.
- Phase 3 closure report.
- Phase 3F portfolio decision.
- Phase 3 measured probe reports and country-status matrices.
- Current recommendation engine, API contract, UI documentation, and active release.

## Objective

Create the authoritative product and mathematical specification for **Phase 4 — Uncertainty-Aware Ranking Model**. Do not implement code.

## Required decisions

### 1. Terminology

Define:

- stable country catalog;
- full-coverage criterion (`FCC`);
- partial-coverage criterion (`PCC`);
- user-active PCC (`PCC-u`);
- baseline ranking (`R0`);
- eligible ranking universe (`Eu`);
- user-specific missing-country union (`Mu`);
- final complete-case ranking (`R1`);
- optimistic excluded-country upper bound;
- top-K robustness status.

Do not call missing countries low-ranked countries. They are excluded or unranked.

### 2. Policy defaults

Use these defaults unless repository evidence proves they conflict with an existing contract:

- stable catalog size: 91;
- PCC minimum criterion coverage: 82/91;
- preferred query-specific missing union: `Mu <= 5`;
- hard maximum missing union: `Mu <= 9`;
- minimum eligible query universe: 82;
- PCC activation threshold: raw user weight >= 0.6, corresponding to Medium;
- default top K: 10;
- actual robustness K: requested `top_k`;
- score maximum used for diagnostic upper bounds: 10.

Make every value versioned/configurable in policy rather than scattered magic constants.

### 3. Ranking algorithm

Specify precisely:

1. Use the user's FCC weights to calculate `R0` across all 91 countries.
2. An FCC with zero weight does not contribute. Preserve the existing all-zero fallback semantics.
3. A PCC contributes only when its raw weight is at least 0.6.
4. A PCC below 0.6 is fully ignored for `R1`, weight normalisation, missing-country analysis, and robustness analysis.
5. Build `Mu` from missing, stale, invalid, rejected, or otherwise non-ready observations for every criterion in `PCC-u`.
6. Rank only `Eu = stable_91 - Mu`.
7. Every country in `R1` must have every active criterion.
8. Normalise weights once over the active criteria and apply the same weights to all countries in `R1`.
9. Never impute values or renormalise weights per country.
10. If more than nine countries are excluded, return `R0` plus a structured coverage-limit result instead of `R1`.

### 4. Top-K robustness analysis

For each excluded country `x`, define:

`upper_bound(x) = sum(known active criterion contributions) + sum(normalised weight of each missing active PCC * 10)`

This is a diagnostic bound only.

Compare the upper bound with the actual Kth score in `R1`, respecting ties.

Define these statuses:

- `NO_PARTIAL_CRITERIA_ACTIVE`
- `FULL_COVERAGE`
- `ROBUST_TOP_K`
- `POTENTIALLY_AFFECTED`
- `BASELINE_TOP_K_EXCLUDED`
- `COVERAGE_LIMIT_EXCEEDED`

Specify deterministic precedence when more than one condition applies. Recommended precedence:

1. `COVERAGE_LIMIT_EXCEEDED`
2. `BASELINE_TOP_K_EXCLUDED`
3. `POTENTIALLY_AFFECTED`
4. `ROBUST_TOP_K`
5. `FULL_COVERAGE`
6. `NO_PARTIAL_CRITERIA_ACTIVE`

### 5. Warning semantics

Define user-facing meaning, not final UI copy:

- mild disclosure for `ROBUST_TOP_K`;
- prominent caution for `POTENTIALLY_AFFECTED`;
- strongest warning for `BASELINE_TOP_K_EXCLUDED`;
- no PCC-inclusive results for `COVERAGE_LIMIT_EXCEEDED`.

### 6. Non-goals

Keep outside Phase 4:

- imputation;
- probabilistic prediction of missing criterion values;
- LLM-generated scores;
- city-level rankings;
- applicant-specific visa/legal eligibility;
- profile-derived tax or housing calculations;
- silent source fallback;
- country-specific criterion sets;
- changing the stable catalog from 91.

## Deliverables

Produce:

1. `docs/product/uncertainty-aware-ranking.md`
2. A policy table with every default and rationale.
3. Mathematical examples using:
   - no active PCC;
   - one PCC with three missing countries;
   - several PCC with five, six, and nine unique missing countries;
   - a coverage-limit case;
   - robust and potentially affected top-10 examples.
4. Stable status and reason-code definitions.
5. Acceptance criteria for Phases 4C–4H.
6. A concise list of open decisions that truly require user approval.

Do not change repository code or production data.
