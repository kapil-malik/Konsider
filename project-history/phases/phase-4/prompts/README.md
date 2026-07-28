# Konsider Phase 4 — Uncertainty-Aware Ranking Model

## Why this is a separate phase

Phase 3 is closed. It researched 84 criteria, deeply reviewed 45, measured selected sources, and added three globally complete criteria. Phase 4 changes a different architectural assumption: ranking no longer has to reject every otherwise-valid criterion merely because a small number of stable countries lack fresh data.

Phase 4 must preserve the stable 91-country catalog and must not use imputation or country-specific weight renormalisation. It introduces query-specific complete-case ranking, explicit excluded-country reporting, and a mathematical top-K robustness analysis.

## Baseline

- Stable catalog: 91 countries.
- Current enabled full-coverage criteria: 8.
- Full-coverage criterion (FCC): valid and ranking-ready for all 91 countries.
- Partial-coverage criterion (PCC): otherwise production-suitable, but valid for at least 82 of 91 countries.
- Default score range: 1–10.
- Existing user priority scale:
  - No = 0.0
  - Very Low = 0.2
  - Low = 0.4
  - Medium = 0.6
  - High = 0.8
  - Very High = 1.0

## Approved policy defaults to encode and test

- PCC activation threshold: Medium or above, raw weight >= 0.6.
- Preferred active missing-country union: 5 or fewer.
- Hard active missing-country union: 9 or fewer.
- Equivalent minimum eligible-country universe: 82.
- Default top K: 10.
- Actual robustness K: the request's `top_k`, defaulting to 10.
- Missing values are never imputed.
- Countries are never scored with different active criterion sets.
- A PCC below the activation threshold is excluded from ranking entirely, not merely ignored during missing-data analysis.
- The stable catalog remains 91 even when a query ranks fewer countries.

## Core algorithm

Given user weights:

1. Classify enabled criteria as FCC or PCC.
2. Compute baseline `R0` over all 91 countries using the user's FCC weights.
3. Activate only PCC whose raw user weight is >= 0.6. Call these `PCC-u`.
4. Let `Mu` be the union of countries missing or stale for any criterion in `PCC-u`.
5. Let `Eu = stable_91 - Mu`.
6. If `|Mu| > 9` or `|Eu| < 82`, do not produce a PCC-inclusive ranking. Return the FCC-only baseline with a structured coverage-limit explanation.
7. Otherwise compute `R1` over `Eu` using the same active criterion set and the same normalised weights for every ranked country.
8. For each excluded country, calculate an optimistic upper bound:
   - use its real scores for known active criteria;
   - use score 10 only for each missing active PCC;
   - this is diagnostic only and is never published as the country's score.
9. Compare each optimistic bound with the actual Kth score in `R1`.
10. Classify uncertainty:
    - `FULL_COVERAGE`: no active PCC country exclusions.
    - `ROBUST_TOP_K`: exclusions exist, but no excluded country could enter top K even with perfect missing scores.
    - `POTENTIALLY_AFFECTED`: at least one excluded country's optimistic bound reaches or exceeds the Kth score.
    - `BASELINE_TOP_K_EXCLUDED`: at least one excluded country was already in the FCC-only `R0` top K.
    - `COVERAGE_LIMIT_EXCEEDED`: more than 9 countries would be excluded or fewer than 82 would remain.
11. Always report excluded countries, missing criteria, baseline ranks, optimistic bounds, and exact ranking-universe size.

`BASELINE_TOP_K_EXCLUDED` is the strongest warning. `POTENTIALLY_AFFECTED` is also a prominent caution. `ROBUST_TOP_K` supports a mild warning.

## Initial Phase 3 candidates to evaluate

These are candidates for Phase 4 review, not automatic approvals:

- C11 Overall job-market opportunity: 88/91.
- C26 Financial protection from health costs: 90/91.
- C08 School education quality: 87/91; experimental construct decision remains.
- C53 Basic water and sanitation access: 86/91; reserve because discrimination and semantic value are weak.

Suggested initial onboarding sequence:

1. C11 + C26
2. C08 after its scoring construct is frozen
3. Keep C53 as reserve unless it adds clear decision value

Known active missing-union examples from Phase 3 evidence:

- C11 + C26: 3 unique missing/stale countries.
- C08 + C26: 5.
- C11 + C08 + C26: 6.
- C11 + C08 + C26 + C53: 9.

Full-coverage candidates such as macroeconomic stability or extreme-weather risk are not PCC problems. They may be added later after their separate methodology blockers are resolved.

## Phase structure

- Phase 4A — Product policy and mathematical contract
  Intended for: Desktop ChatGPT Work

- Phase 4B — Candidate selection and coverage simulations
  Intended for: Desktop ChatGPT Work

- Phase 4C — Release, catalog, and validation contracts
  Intended for: Codex

- Phase 4D — Ranking engine and robustness analysis
  Intended for: Codex

- Phase 4E — API contract and integration
  Intended for: Codex

- Phase 4F — Candidate source onboarding and immutable release
  Intended for: Codex

- Phase 4G — UI and UX implementation
  Intended for: Codex

- Phase 4H — End-to-end verification, closure, and roadmap update
  Intended for: Codex, followed by ChatGPT review

## Recommended execution order

Run 4A and 4B before writing production code. Revise later prompts with the approved 4A policy and 4B candidate list. Phases 4C–4E can use fixture-backed PCC data. Phase 4F introduces exact sources and a new immutable release. Phase 4G renders API metadata without duplicating ranking logic. Phase 4H closes the phase.
