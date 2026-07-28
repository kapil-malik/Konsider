# Prompt — Phase 4D: Ranking Engine and Robustness Analysis

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4A mathematical contract.
- Phase 4C release/catalog support.
- Phase 4B candidate missing-country matrices.
- Existing deterministic recommendation service.

## Objective

Implement uncertainty-aware complete-case ranking in the domain/service layer. Do not put ranking rules in API routes or UI code.

## Algorithm requirements

### Criterion activation

- FCC uses the existing user-weight semantics.
- PCC is active only when raw weight >= 0.6.
- PCC with raw weight below 0.6 is removed before weight normalisation and missing-union analysis.
- Preserve existing behavior for unknown criteria, disabled criteria, negative/non-finite weights, omitted weights, and all-zero weights.

### Baseline R0

- Calculate `R0` over all 91 stable countries using the user's active FCC weights.
- Use existing deterministic tie-breaking.
- Preserve contributions and explanation semantics.

### Final R1

- Build `Mu` from every non-valid country outcome across active PCC.
- Build `Eu = stable_91 - Mu`.
- If `|Mu| > 9` or `|Eu| < 82`, do not calculate a PCC-inclusive result. Return the FCC baseline plus `COVERAGE_LIMIT_EXCEEDED`.
- Otherwise normalise weights once across active FCC and PCC.
- Rank only `Eu`.
- Every ranked country must have every active criterion.
- Never impute and never renormalise by country.

### Robustness

For each excluded country:

- retain its `R0` rank and FCC score;
- use real known scores for active criteria;
- substitute score 10 only inside an optimistic diagnostic calculation for missing active PCC;
- compute the optimistic total using the same normalised weights as `R1`;
- compare against the Kth `R1` score;
- treat equality as potentially able to enter because of ties.

Status precedence:

1. `COVERAGE_LIMIT_EXCEEDED`
2. `BASELINE_TOP_K_EXCLUDED`
3. `POTENTIALLY_AFFECTED`
4. `ROBUST_TOP_K`
5. `FULL_COVERAGE`
6. `NO_PARTIAL_CRITERIA_ACTIVE`

`K` equals requested `top_k`, default 10.

## Domain output

Return structured data including:

- stable country count;
- eligible country count;
- excluded country count;
- active FCC IDs;
- active PCC IDs;
- ignored PCC IDs and their raw weights;
- excluded countries and exact missing criteria/reasons;
- R0 top K;
- R1 top K;
- Kth score;
- excluded-country R0 ranks;
- optimistic upper-bound scores;
- could-enter-top-K flags;
- uncertainty status and reason codes;
- policy version and thresholds.

Do not rely only on prewritten warning strings.

## Tests

Cover:

- no PCC active;
- PCC below 0.6;
- one active PCC;
- multiple active PCC;
- unions of 5, 6, 9, and 10;
- baseline-top-K exclusion;
- optimistic bound below, equal to, and above Kth score;
- ties;
- top_k 5, 10, and 20;
- all-zero weights;
- deterministic ordering;
- no partial scoring;
- contribution reconciliation;
- old FCC-only behavior unchanged.

## Deliverables

- domain/service implementation;
- typed result models;
- tests and golden scenarios;
- algorithm documentation;
- no API/UI implementation in this sub-phase.
