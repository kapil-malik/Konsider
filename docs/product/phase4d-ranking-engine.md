# Phase 4D: uncertainty-aware ranking engine

Status: implemented in the domain/service layer with synthetic schema-4 fixtures

Policy: `uncertainty-aware-ranking-policy-1.0`

Phase 4D adds `RecommendationService.rank_with_uncertainty`. It returns a typed
`UncertaintyRankingResult`; current API routes continue using the existing `rank` method. Phase 4E
will own transport models and mapping. No UI or HTTP behavior changes in this phase.

## Activation and weights

- Enabled `GLOBAL_CORE` criteria are FCCs.
- An FCC contributes to the final ranking when its raw weight is positive.
- Enabled `CONDITIONAL_COMPLETE_CASE` criteria are PCCs.
- A PCC is active when its raw weight is at least `0.6`.
- `ignored_pcc` contains only PCCs with `0 < weight < 0.6`. Omitted and explicit-zero PCCs are
  inactive and are not listed.
- R0 normalizes FCC weights independently. When all FCC weights are zero, R0 uses equal FCC
  weights.
- When PCC is active, R1 normalizes once across positive-weight FCCs and active PCCs. That exact
  vector is reused for every eligible country and every optimistic bound.

Existing failures for unknown, disabled, non-ready, negative, non-numeric, and non-finite weights
remain application errors.

## Ranking sequence

1. Calculate R0 over all 91 countries using FCC scores.
2. Build the missing union from every non-valid outcome across active PCCs.
3. If the union exceeds nine or leaves fewer than 82 eligible countries, return the tie-inclusive
   R0 boundary with `COVERAGE_LIMIT_EXCEEDED`. R1, its Kth score, optimistic bounds, and
   `could_enter_top_k` are absent.
4. Otherwise calculate R1 over the complete-case universe. Every eligible row must contain every
   active criterion; absence is a release/engine integrity error.
5. For each excluded country, retain its R0 rank and score. Use real scores for known active
   criteria and score 10 for every non-ready active PCC only in the optimistic diagnostic.

Contributions and totals use eight-decimal precision. Each row records the same eligible-universe
count, normalized weights, observation/scoring versions, and source version.

## Tie-inclusive top K

K defaults to 10 and is validated against the returned ranking universe. The score of the Kth
deterministically ordered country is the boundary. Every score equal to that boundary within
`1e-8` belongs to top K, so the returned set may exceed K. ISO-3 remains the display tie-breaker
but does not decide warnings.

An excluded R0 country tied at the baseline boundary triggers `BASELINE_TOP_K_EXCLUDED`. An
optimistic bound equal to the R1 boundary sets `could_enter_top_k` and triggers
`POTENTIALLY_AFFECTED` when no baseline-top-K country was excluded.

## Status decision

Exactly one status is selected in this order:

1. no active PCC: `NO_PARTIAL_CRITERIA_ACTIVE`;
2. failed coverage gate: `COVERAGE_LIMIT_EXCEEDED`;
3. active PCC with no exclusions: `FULL_COVERAGE`;
4. excluded country in the tie-inclusive R0 boundary: `BASELINE_TOP_K_EXCLUDED`;
5. excluded optimistic bound meeting or exceeding the R1 boundary: `POTENTIALLY_AFFECTED`;
6. otherwise: `ROBUST_TOP_K`.

Stable reason codes independently describe ignored PCCs, preferred/elevated/blocked missing
unions, violated gates, baseline and optimistic warnings, boundary ties, and the all-zero FCC
fallback.

## Verification boundary

Golden tests cover missing unions of 0, 3, 5, 6, 9, and 10; omitted, zero, 0.2, 0.4, and 0.6 PCC
weights; multiple PCCs; R0 and R1 ties; bounds below, equal to, and above the Kth score; K values
5, 10, and 20; contribution reconciliation; deterministic replay; coverage-limit null fields; and
schema-3 FCC score/order compatibility.

All Phase 4D scenarios are synthetic and fixture-backed. Live source onboarding remains Phase 4F.
