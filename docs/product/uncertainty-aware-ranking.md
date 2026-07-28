# Phase 4A: uncertainty-aware ranking policy and mathematical contract

Status: approved product and mathematical specification

Policy version: `uncertainty-aware-ranking-policy-1.0`

Approved: 2026-07-27

Scope: Phase 4A specification only. This document does not approve a partial-coverage criterion,
change production code or data, or activate a release.

## 1. Purpose

Konsider has a stable catalog of 91 countries and eight enabled criteria with valid scores for
every country. Phase 4 permits a narrowly controlled second coverage mode for valuable criteria
that are otherwise production-suitable but lack a ready observation for a small number of
countries.

The model preserves four guarantees:

1. The stable country catalog remains 91.
2. Every country in a ranking is scored with the same active criteria and the same normalized
   weights.
3. Konsider never imputes a missing value or renormalizes weights by country.
4. Countries without every active criterion are explicitly excluded and unranked, never placed at
   the bottom.

The product therefore separates the stable catalog from a query-specific eligible ranking
universe. It also reports whether excluded countries could plausibly affect the user's requested
top K.

The policy is based on the [Phase 3 closure report](../research/phase3-closure-report.md), the
[Phase 3F portfolio decision](../research/konsider_phase3f_portfolio_decision.md), the
[Phase 3E measured probes](../research/phase3e-deterministic-probes.md), the
[Phase 3G-0 final probes](../research/phase3g0-final-probes.md), the current
[scoring methodology](../data/scoring-methodology.md), and active release `2026-07-27.1`.

## 2. Normative language and ownership

The words **must**, **must not**, **should**, and **may** are normative.

- Immutable release artifacts own canonical observations, readiness outcomes, canonical 1-10
  scores, source lineage, and criterion coverage metadata.
- The recommendation domain/service layer owns criterion activation, weight normalization,
  complete-case selection, scoring, robustness analysis, status selection, and reason codes.
- The API exposes typed domain results without reproducing those decisions.
- The UI renders API-owned states and explanations without calculating rankings or robustness.

## 3. Terminology

| Term | Symbol | Definition |
| --- | --- | --- |
| Stable country catalog | \(S\) | The versioned set of countries supported by Konsider independently of one query. Under this policy, \(|S|=91\). |
| Full-coverage criterion | FCC | An enabled, ranking-ready criterion with a valid canonical score for every country in \(S\). |
| Partial-coverage criterion | PCC | An enabled `CONDITIONAL_COMPLETE_CASE` criterion with valid canonical scores for at least 82 countries in \(S\), explicit outcomes for all 91, and no contractual requirement to remain 91/91. A particular release may incidentally have 91 valid outcomes without changing the criterion's coverage mode. |
| User-active PCC | PCC-u, \(P_u\) | A PCC whose raw user weight is at least the policy activation threshold of 0.6. |
| Baseline ranking | \(R_0\) | The complete 91-country ranking calculated only from the user's FCC weights. It is the full-coverage comparison baseline. |
| User-specific missing-country union | \(M_u\) | The union of countries having any non-ready outcome for any criterion in \(P_u\). |
| Eligible ranking universe | \(E_u\) | The query-specific complete-case set \(S \setminus M_u\). |
| Final complete-case ranking | \(R_1\) | The PCC-inclusive ranking over \(E_u\), using one normalized weight vector across every active FCC and PCC-u. |
| Optimistic excluded-country upper bound | \(U(x)\) | A diagnostic maximum for an excluded country \(x\), using its real scores where ready and score 10 for every non-ready active PCC outcome. It is not a published country score or rank. |
| Robustness K | \(K\) | The request's `top_k`; it defaults to 10. All countries tied at the Kth-score boundary count as top K. |
| Top-K robustness status | — | One stable status describing whether PCC activation caused exclusions and whether those exclusions could affect the score-bounded top K. |
| Non-ready outcome | — | Any missing, stale, invalid, rejected, parse-failed, mapping-failed, or otherwise explicitly non-ranking-ready outcome for a country in \(S\). Unmapped source records outside \(S\) do not enter \(M_u\). |

“Missing country” may be used informally for a member of \(M_u\), but product contracts should say
**excluded** or **unranked** and preserve the exact outcome. A country excluded from \(R_1\) is not
low-ranked.

## 4. Versioned policy defaults

Every value in this table must live in one versioned policy object or contract. Implementations
must not scatter equivalent magic constants.

| Policy field | Default | Rationale |
| --- | ---: | --- |
| `policy_version` | `uncertainty-aware-ranking-policy-1.0` | Makes ranking behavior auditable and permits deliberate future change. |
| `stable_universe_id` | `stable_supported_v1` | Pins the policy to the approved country registry. |
| `stable_country_count` | 91 | Preserves the Phase 2D and Phase 3 supported catalog. |
| `pcc_min_valid_country_count` | 82 | Retains at least 90% of 91 countries and matches the Phase 3 research gate. |
| `preferred_missing_union_max` | 5 | Keeps ordinary PCC queries close to the complete catalog. Exceeding it is disclosed but not blocked. |
| `hard_missing_union_max` | 9 | Prevents a PCC-inclusive ranking when more than 10% of the catalog would be excluded. |
| `min_eligible_country_count` | 82 | Equivalent safety gate to the hard union limit while the stable catalog has 91 countries; both must still be checked and reported. |
| `pcc_activation_raw_weight_min` | 0.6 | Corresponds to the existing Medium priority. The raw, not normalized, weight controls activation. |
| `default_top_k` | 10 | Provides a consistent default recommendation and robustness boundary. |
| `diagnostic_score_max` | 10 | Matches the canonical score ceiling and makes the excluded-country bound deliberately optimistic. |
| `canonical_score_min` | 1 | Current default canonical score floor. It does not replace criterion-specific allowed-range validation. |
| `canonical_score_max` | 10 | Current default canonical score ceiling. |
| `country_tie_breaker` | ascending ISO-3 | Preserves deterministic display order without changing score-boundary membership. |
| `rounding_tolerance` | \(10^{-8}\) | Preserves the current contribution reconciliation tolerance and defines score-boundary equality. |

The preferred band is:

- **preferred** when \(|M_u| \leq 5\);
- **elevated** when \(6 \leq |M_u| \leq 9\); and
- **blocked** when \(|M_u| > 9\) or \(|E_u| < 82\).

The band supplements the robustness status. It does not replace it.

## 5. Criterion and outcome contract

Every enabled ranking criterion must declare a versioned coverage mode:

- `GLOBAL_CORE` for FCC;
- `CONDITIONAL_COMPLETE_CASE` for PCC; or
- `DIAGNOSTIC_ONLY` for visible evidence that never contributes to ranking.

An FCC must have 91 valid observations and 91 canonical scores.

A PCC must:

- have at least 82 valid observations and corresponding canonical scores, with no requirement that
  it have fewer than 91;
- have exactly one explicit attempt/outcome for each of the 91 stable countries;
- have no score for a non-ready observation;
- retain exact outcome and reason codes for each non-valid country;
- declare its activation threshold, allowed score range, source/scoring versions, freshness rule,
  and experimental state; and
- pass every non-coverage production gate, including authority, licensing, semantics,
  deterministic parsing, provenance, replay, scoring, and maintenance review.

Coverage is necessary but not sufficient for PCC approval. Phase 4A creates a capability; Phase 4B
selects candidates, and Phase 4F separately approves source onboarding and release activation.

An old release must never be silently reinterpreted. A new coverage contract requires a new schema
version, while schema-3 releases remain immutable and loadable with their original FCC-only
semantics.

## 6. Weight semantics

Let \(w_c\) be the raw user weight for criterion \(c\). An omitted enabled criterion has raw weight
zero. Weights must remain finite and non-negative.

The existing product priority scale is:

| Priority | Raw weight |
| --- | ---: |
| No | 0.0 |
| Very Low | 0.2 |
| Low | 0.4 |
| Medium | 0.6 |
| High | 0.8 |
| Very High | 1.0 |

The service may continue accepting other valid non-negative numeric weights for compatibility. PCC
activation still compares the raw numeric value to 0.6.

### 6.1 FCC weights

An FCC contributes when \(w_f>0\). FCC weights are not activation-thresholded.

For \(R_0\), normalize the raw FCC vector once:

\[
\alpha_f^{(0)} = \frac{w_f}{\sum_{j\in F}w_j}.
\]

If every FCC raw weight is zero, preserve the current fallback: assign equal weight to every
enabled FCC. This fallback applies independently to \(R_0\), so a meaningful 91-country baseline
always exists.

### 6.2 PCC activation

A PCC is user-active exactly when:

\[
P_u = \{p\in P \mid w_p \geq 0.6\}.
\]

A PCC below 0.6 is excluded entirely from:

- \(R_1\);
- weight normalization;
- \(M_u\);
- \(E_u\);
- optimistic bounds; and
- robustness analysis.

The response must identify each ignored PCC and its raw weight. The implementation must not
threshold a normalized weight, because normalization depends on the other selected criteria.

### 6.3 Final active weights

When \(P_u\) is non-empty and the coverage gate passes, the active set is:

\[
A=\{f\in F\mid w_f>0\}\cup P_u.
\]

Normalize once across \(A\):

\[
\alpha_c^{(1)} = \frac{w_c}{\sum_{j\in A}w_j}.
\]

The same \(\alpha^{(1)}\) vector must be used for every country in \(R_1\) and every optimistic
bound. Since each PCC-u has raw weight at least 0.6, the denominator is non-zero. If all FCC weights
are zero while a PCC is active, the active PCC weights alone determine \(R_1\); \(R_0\) still uses
the equal-FCC fallback.

If no PCC is active and all FCC weights are zero, equal FCC weights produce the ordinary FCC-only
result.

## 7. Ranking algorithm

### 7.1 Validate and resolve the request

1. Resolve a server-owned profile or explicit raw weights using the existing mutually exclusive
   selection rules.
2. Reject unknown, disabled, non-ranking-ready, negative, non-numeric, or non-finite inputs using
   existing structured behavior.
3. Resolve \(K\) from `top_k`, defaulting to 10. `top_k` remains a strict positive integer. As in
   the existing service, it must not exceed the ranking universe that will be returned.
4. Classify enabled criteria from release metadata; the client must not choose FCC/PCC labels.

### 7.2 Calculate the baseline \(R_0\)

For every \(x\in S\):

\[
R_0(x)=\sum_{f\in F}\alpha_f^{(0)}s_{x,f},
\]

where \(s_{x,f}\) is the canonical score for \(x\) on FCC \(f\).

Sort by descending published total and ascending ISO-3. Preserve the current contribution
calculation, score precision, rounding tolerance, strengths/trade-offs behavior, and provenance.

The display rank remains the deterministic ordinal position after ISO-3 tie-breaking. Top-K
membership does not use that tie-break: it uses the score boundary in Section 9.

### 7.3 Select active PCC and build the complete-case universe

1. Build \(P_u\) from raw weights.
2. If \(P_u=\varnothing\), return the FCC result with
   `NO_PARTIAL_CRITERIA_ACTIVE`. Do not perform PCC missing-data or robustness analysis.
3. For each \(p\in P_u\), read all 91 release outcomes.
4. Define:

\[
M_u=\bigcup_{p\in P_u}\{x\in S\mid outcome(x,p)\neq valid\}
\]

and:

\[
E_u=S\setminus M_u.
\]

5. Preserve, for every member of \(M_u\), every active PCC with a non-ready outcome plus its
   normalized outcome class, source reason codes, source/scoring versions, and record provenance
   where available.

### 7.4 Enforce the coverage gate

If either:

\[
|M_u|>9
\]

or:

\[
|E_u|<82,
\]

do not calculate or publish \(R_1\). Return \(R_0\) as the result ranking with
`COVERAGE_LIMIT_EXCEEDED`.

The result must still report the proposed \(M_u\), its exact countries and reasons, the proposed
eligible count, both violated thresholds, and the PCCs that caused the gate. These are
would-be exclusions from a PCC-inclusive ranking; they remain ranked in the returned FCC baseline.
An implementation may calculate diagnostic optimistic totals, but there is no \(R_1\) Kth score
and therefore no `could_enter_top_k` decision in this branch.

### 7.5 Calculate the final complete-case ranking \(R_1\)

When the gate passes, for every \(x\in E_u\):

\[
R_1(x)=\sum_{c\in A}\alpha_c^{(1)}s_{x,c}.
\]

Every \(x\in E_u\) must have a ready canonical score for every \(c\in A\). Any violation is a
release/engine integrity error, not permission to skip a contribution.

Sort by descending total and ascending ISO-3. The returned ranking must state that each displayed
rank is among \(|E_u|\) eligible countries. Members of \(M_u\) have no \(R_1\) score or final rank.

## 8. Optimistic excluded-country upper bound

For each \(x\in M_u\), partition the active criteria into:

- \(K_x\): active criteria with a ready canonical score for \(x\); and
- \(N_x\): active PCCs with any non-ready outcome for \(x\).

Then:

\[
U(x)=
\sum_{c\in K_x}\alpha_c^{(1)}s_{x,c}
+
\sum_{p\in N_x}\alpha_p^{(1)}\times 10.
\]

This substitution applies to every non-ready active PCC outcome, including missing, stale,
invalid, rejected, parse-failed, or another explicit non-ready state. A stale raw value is not a
known ranking score and must not be used in the bound.

The bound:

- uses the same normalized vector as \(R_1\);
- retains real FCC and ready PCC scores;
- is calculated and displayed at the same precision as ranking totals;
- is never stored or exposed as the country's canonical or final score;
- never gives the country an \(R_1\) rank; and
- is deliberately one-sided: it asks whether exclusion could matter, not what the missing value
  is likely to be.

## 9. Score-boundary top K and ties

Let \(T_K(R)\) be the Kth ordered score in ranking \(R\). A country is in the score-bounded top K
when:

\[
score(x)\geq T_K(R),
\]

with equality interpreted using the versioned rounding tolerance.

Consequences:

- every country tied at the Kth score belongs to top K;
- the returned top-K set may contain more than K countries;
- ISO-3 still provides deterministic display order among tied countries;
- a baseline warning applies to every excluded country whose \(R_0\) score is at least
  \(T_K(R_0)\), including a tie at the boundary; and
- an excluded country could enter top K when \(U(x)\geq T_K(R_1)\), not only when it is strictly
  greater.

The domain result must report requested K, Kth score, boundary-tie count, and returned result count.
The ordinal `rank` field remains deterministic presentation metadata and must not decide top-K
membership.

For an active-PCC request, `top_k` is validated against \(|E_u|\) after the eligible universe is
known. This preserves the existing rule that K cannot exceed the returned ranking universe. In the
coverage-limit branch, the returned universe is \(R_0\), so validation uses 91.

## 10. Status decision procedure

Exactly one status is returned.

| Evaluation order | Condition | Status |
| ---: | --- | --- |
| 1 | \(P_u=\varnothing\) | `NO_PARTIAL_CRITERIA_ACTIVE` |
| 2 | \(P_u\neq\varnothing\) and the coverage gate fails | `COVERAGE_LIMIT_EXCEEDED` |
| 3 | The gate passes and \(M_u=\varnothing\) | `FULL_COVERAGE` |
| 4 | At least one \(x\in M_u\) is in the score-bounded \(R_0\) top K | `BASELINE_TOP_K_EXCLUDED` |
| 5 | No baseline-top-K country is excluded, and at least one \(U(x)\geq T_K(R_1)\) | `POTENTIALLY_AFFECTED` |
| 6 | Exclusions exist and every \(U(x)<T_K(R_1)\) | `ROBUST_TOP_K` |

This decision procedure incorporates the approved precedence while making two mutually exclusive
special cases explicit:

- no active PCC is always `NO_PARTIAL_CRITERIA_ACTIVE`; and
- active PCC with no exclusions is `FULL_COVERAGE`.

`BASELINE_TOP_K_EXCLUDED` is stronger than an optimistic-bound result because the excluded country
was already on the full-coverage top-K score boundary.

## 11. Stable reason codes

Statuses are coarse, stable classifications. Reason codes provide deterministic detail. A result
may have several reason codes.

### 11.1 Result reason codes

| Code | Meaning |
| --- | --- |
| `NO_PCC_AT_OR_ABOVE_ACTIVATION_THRESHOLD` | No PCC raw weight reached 0.6. |
| `PCC_BELOW_ACTIVATION_THRESHOLD` | At least one weighted PCC was ignored because its raw weight was below 0.6. |
| `ACTIVE_PCC_HAS_NO_NON_READY_COUNTRIES` | PCC is active, but no stable country is excluded. |
| `ACTIVE_MISSING_UNION_WITHIN_PREFERRED_LIMIT` | \(1\leq |M_u|\leq5\). |
| `ACTIVE_MISSING_UNION_ABOVE_PREFERRED_LIMIT` | \(6\leq |M_u|\leq9\). |
| `ACTIVE_MISSING_UNION_EXCEEDS_HARD_LIMIT` | \(|M_u|>9\). |
| `ELIGIBLE_UNIVERSE_BELOW_MINIMUM` | \(|E_u|<82\). |
| `EXCLUDED_COUNTRY_IN_BASELINE_TOP_K` | At least one excluded country meets the \(R_0\) Kth-score boundary. |
| `EXCLUDED_COUNTRY_CAN_REACH_TOP_K_BOUNDARY` | At least one optimistic bound meets or exceeds the \(R_1\) Kth score. |
| `ALL_EXCLUDED_COUNTRIES_BELOW_TOP_K_BOUNDARY` | Every optimistic bound is below the \(R_1\) Kth score. |
| `TOP_K_BOUNDARY_INCLUDES_TIES` | The score-bounded result includes more than K countries. |
| `FCC_ALL_ZERO_EQUAL_WEIGHT_FALLBACK` | The FCC baseline used equal weights because all FCC raw weights were zero. |

### 11.2 Normalized country-outcome codes

The release must retain exact source reason codes. The engine additionally maps them to one stable
classification for cross-source product handling.

| Code | Meaning and optimistic treatment |
| --- | --- |
| `PCC_OBSERVATION_MISSING` | No approved source observation; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_STALE` | Observation fails its criterion freshness rule; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_INVALID` | Observation exists but fails validation; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_REJECTED` | Observation or source record is explicitly rejected; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_PARSE_FAILED` | Approved source record could not be parsed; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_MAPPING_FAILED` | A stable-country attempt could not be reconciled to its approved source record; substitute 10 only in \(U(x)\). |
| `PCC_OBSERVATION_OTHER_NON_READY` | Another explicit non-ready state; substitute 10 only in \(U(x)\). |

Reason-code meanings are append-only within a policy major version. A meaning change requires a new
policy version.

## 12. Required structured result

The domain result must expose enough typed data for the API and UI to explain the outcome without
recomputing it:

- policy version and all applied thresholds;
- stable universe ID and size;
- returned ranking mode: `FCC_BASELINE` or `PCC_COMPLETE_CASE`;
- requested and resolved K;
- active FCC IDs;
- active PCC IDs;
- ignored PCC IDs, raw weights, and activation reason;
- one normalized weight vector for the returned ranking;
- baseline normalized FCC weights;
- exact eligible and excluded/would-be-excluded counts;
- coverage band;
- excluded country codes and names;
- each excluded country's non-ready criteria, normalized outcome classes, exact source reason
  codes, and available provenance;
- each excluded country's deterministic ordinal \(R_0\) rank, \(R_0\) score, and score-boundary
  top-K membership;
- \(R_0\) top-K rows and boundary score;
- \(R_1\) top-K rows and boundary score when \(R_1\) exists;
- each optimistic upper bound and `could_enter_top_k` flag when \(R_1\) exists;
- uncertainty status and result reason codes;
- boundary-tie counts;
- stable catalog count, eligible count, and returned ranked-row count; and
- existing release, schema, scoring-method, contribution, observation, source, caveat, and
  experimental metadata.

Ranked countries and excluded countries must be separate collections. In the coverage-limit branch,
the returned ranked collection is \(R_0\); the exclusion collection describes the countries that
prevented a PCC-inclusive \(R_1\).

## 13. User-facing warning semantics

This section defines meaning and severity, not final UI copy.

| Status | Severity | Required meaning |
| --- | --- | --- |
| `NO_PARTIAL_CRITERIA_ACTIVE` | None | The result uses only full-coverage criteria and all 91 countries. PCC below Medium did not affect weights, exclusions, or robustness. |
| `FULL_COVERAGE` | Informational | At least one PCC is active, but every stable country has every active criterion, so all 91 are ranked. |
| `ROBUST_TOP_K` | Mild disclosure | Some countries are unranked, but even perfect substituted scores on their non-ready active PCCs would not reach the requested top-K score boundary. |
| `POTENTIALLY_AFFECTED` | Prominent caution | At least one excluded country could meet or exceed the requested top-K boundary under the optimistic diagnostic. The result is useful but incomplete. |
| `BASELINE_TOP_K_EXCLUDED` | Strongest warning | At least one excluded country was already in the full-coverage score-bounded top K. Its omission is especially material. |
| `COVERAGE_LIMIT_EXCEEDED` | Blocking PCC disclosure | No PCC-inclusive ranking was produced. The displayed result is the 91-country FCC baseline, and the active PCC combination must be identified as exceeding policy. |

All exclusion states must show the exact ranked-universe size and make excluded-country details
accessible. PCC alone is not an error and should not receive alarming styling.

## 14. Mathematical examples

The arithmetic examples are illustrative; they do not publish candidate scores or approve
candidates.

### 14.1 No active PCC

Suppose two FCCs have raw weights 0 and a PCC has raw weight 0.4.

- The PCC is below 0.6 and is ignored everywhere.
- The FCC vector is all zero, so \(R_0\) uses equal FCC weights \(0.5,0.5\).
- All 91 countries are ranked.
- Status: `NO_PARTIAL_CRITERIA_ACTIVE`.
- Reasons: `NO_PCC_AT_OR_ABOVE_ACTIVATION_THRESHOLD`,
  `PCC_BELOW_ACTIVATION_THRESHOLD`, and `FCC_ALL_ZERO_EQUAL_WEIGHT_FALLBACK`.

### 14.2 One PCC with three excluded countries

Use raw weights 0.4 for FCC Safety, 0.4 for FCC Cost, and 0.8 for PCC Job market. The normalized
\(R_1\) vector is \(0.25,0.25,0.50\).

If the PCC is non-ready for ATG, GRD, and UKR:

\[
M_u=\{ATG,GRD,UKR\},\qquad |E_u|=88.
\]

The combination is within the preferred band and passes the hard gate.

For an excluded country with Safety 3 and Cost 4:

\[
U(x)=0.25(3)+0.25(4)+0.50(10)=6.75.
\]

If the actual \(R_1\) tenth score is 7.20, the country cannot reach the boundary. If every other
excluded bound is also below 7.20 and none was in the \(R_0\) score-bounded top 10, status is
`ROBUST_TOP_K`.

### 14.3 Potentially affected top 10

Keep the same weights. For another excluded country with Safety 6.8 and Cost 6.8:

\[
U(x)=0.25(6.8)+0.25(6.8)+0.50(10)=8.40.
\]

If the actual \(R_1\) tenth score is 8.40, equality is sufficient. The country could enter the
score-bounded top 10 and status is `POTENTIALLY_AFFECTED`, unless the stronger baseline warning
applies.

### 14.4 Baseline top-10 tie

If \(T_{10}(R_0)=8.00\) and an excluded country has \(R_0(x)=8.00\), that country is a baseline
top-10 member even if ISO-3 ordering displays it after the tenth row. Status is
`BASELINE_TOP_K_EXCLUDED`.

### 14.5 Measured five-, six-, and nine-country unions

The committed Phase 3 evidence records:

| Candidate | Non-valid stable countries |
| --- | --- |
| C11 Job-market opportunity | ATG missing; GRD missing; UKR stale |
| C26 Financial protection from health costs | UKR stale |
| C08 School education quality | ATG invalid; BHS missing; BOL missing; GUY stale |
| C53 Basic water and sanitation access | BHS missing; BIH invalid; GRD invalid; HRV invalid; NIC missing |

Therefore:

| Active PCC combination | \(M_u\) | Count | Band |
| --- | --- | ---: | --- |
| C11 + C26 | ATG, GRD, UKR | 3 | preferred |
| C08 + C26 | ATG, BHS, BOL, GUY, UKR | 5 | preferred |
| C11 + C08 + C26 | ATG, BHS, BOL, GRD, GUY, UKR | 6 | elevated |
| C11 + C08 + C26 + C53 | ATG, BHS, BIH, BOL, GRD, GUY, HRV, NIC, UKR | 9 | elevated |

These examples verify coverage arithmetic only. Phase 4B must revalidate exact source versions,
freshness, licensing, scoring readiness, bias, and historical robustness before selecting any PCC.

### 14.6 Coverage-limit case

Suppose active PCCs have ten unique non-ready countries:

\[
|M_u|=10,\qquad |E_u|=91-10=81.
\]

Both hard checks fail. No \(R_1\) or \(R_1\) Kth score exists. Return the 91-country \(R_0\),
status `COVERAGE_LIMIT_EXCEEDED`, and both
`ACTIVE_MISSING_UNION_EXCEEDS_HARD_LIMIT` and
`ELIGIBLE_UNIVERSE_BELOW_MINIMUM`.

## 15. Non-goals

Phase 4 must not introduce:

- Konsider-created imputation;
- probabilistic prediction of missing criterion values;
- LLM-generated scores;
- per-country active criterion sets or weight normalization;
- silent source fallback or semantic proxy substitution;
- a change to the stable 91-country catalog;
- city, neighborhood, occupation, household, or applicant-specific rankings;
- applicant-specific visa, legal, licensing, tax, contribution, housing, or route eligibility;
- treatment of an excluded country as low-ranked; or
- publication of an optimistic bound as a real score.

Publisher-provided modeled or estimated observations may remain eligible only under the existing
Phase 3 guardrails: authoritative methodology, retained flags, acceptable licensing, frozen
versions, and sensitivity review. This is not Konsider imputation.

## 16. Acceptance criteria for Phase 4C through 4H

### 16.1 Phase 4C: release, catalog, and validation contracts

Phase 4C is accepted only when:

1. A new versioned schema represents `GLOBAL_CORE`, `CONDITIONAL_COMPLETE_CASE`, and
   `DIAGNOSTIC_ONLY` without rewriting schema 3.
2. Criterion metadata includes stable denominator, valid count, minimum count, activation
   threshold, allowed score range, outcome reasons, policy version, experimental state, and
   source/scoring versions.
3. Every published criterion has exactly 91 attempt outcomes.
4. FCC requires 91 valid scores; PCC requires at least 82 and has scores only for valid outcomes.
5. Missing, stale, invalid, rejected, and other outcomes remain distinguishable.
6. Release, catalog, attempts, observations, scores, readiness, and checksums reconcile exactly.
7. An 81/91 PCC, absent attempt, non-valid score, score/attempt mismatch, or FCC below 91 fails
   validation.
8. Fixture releases cover one FCC, one 88/91 PCC, and mixed outcomes.
9. Schema-3 historical releases remain immutable and loadable.
10. LF-normalized artifacts, checksums, offline replay, and Windows/Linux byte stability pass.
11. `active.json` is unchanged.

### 16.2 Phase 4D: ranking engine and robustness

Phase 4D is accepted only when:

1. All policy decisions in Sections 6-10 are owned by typed domain/service code.
2. \(R_0\), \(M_u\), \(E_u\), \(R_1\), \(U(x)\), tie-inclusive boundaries, status precedence, and
   reason codes match this document.
3. PCC below 0.6 is absent from normalization, coverage, and robustness.
4. The all-zero FCC fallback and existing validation semantics are preserved.
5. A single normalized vector is demonstrably reused for every \(R_1\) row and every bound.
6. No excluded country receives an \(R_1\) score or rank.
7. Coverage-limit requests return \(R_0\) and structured gate evidence, not a partial ranking.
8. Golden tests cover no active PCC, active PCC with no exclusion, unions of 3, 5, 6, 9, and 10,
   every status, upper bounds below/equal/above the boundary, baseline ties, K values 5/10/20,
   contribution reconciliation, and repeat determinism.
9. FCC-only scores and ordering remain identical; Phase 4's approved tie-inclusive top-K response
   may contain more than K rows.
10. No API or UI logic is introduced in this phase.

### 16.3 Phase 4E: API contract and integration

Phase 4E is accepted only when:

1. Typed catalog responses expose coverage mode, valid/stable counts, activation threshold,
   experimental state, and concise caveats.
2. `top_k` defaults to 10 and uses score-boundary membership.
3. Typed ranking responses expose every required field in Section 12 and keep ranked and excluded
   collections separate.
4. The FCC baseline is returned successfully with `COVERAGE_LIMIT_EXCEEDED`; coverage policy is not
   treated as an unrelated transport failure.
5. Existing 422, 404, 503, and 500 behavior remains stable for unrelated errors.
6. Routes and mappers remain thin and contain no activation, eligibility, scoring, or robustness
   rules.
7. OpenAPI, checked-in/generated frontend types, contract tests, and examples cover every status.
8. FCC-only requests retain identical scores and ordering plus additive uncertainty metadata and
   the approved default/tie-inclusive top-K behavior.
9. No source ingestion or UI implementation occurs.

### 16.4 Phase 4F: candidate onboarding and immutable release

Phase 4F is accepted only when:

1. Only the Phase 4B user-approved PCC IDs are onboarded.
2. Exact source edition, series/components, licence, attribution, parser, freshness, scoring, and
   experimental policy are frozen and versioned.
3. All 91 outcomes and every non-ready reason match approved evidence or a documented newer probe.
4. Observations and scores exist only for valid countries.
5. Every PCC has at least 82 valid countries; every FCC remains 91/91.
6. Candidate-specific construct, label, component, discrimination, bias, sensitivity, and
   redundancy reviews pass.
7. Online ingestion and offline replay agree.
8. A new immutable release and schema version are used; historical releases are untouched.
9. Catalog/release reconciliation, cross-platform checksums, tests, and clean-checkout validation
   pass before `active.json` moves.
10. No UI implementation occurs.

### 16.5 Phase 4G: UI and UX

Phase 4G is accepted only when:

1. Criterion controls show FCC/PCC coverage, experimental/readiness state, and the Medium activation
   rule from API metadata.
2. Below-threshold PCC is visibly inactive without client-side ranking logic.
3. Results always show eligible-of-91 count, active PCCs, exclusion count, status, K, and rank
   scope.
4. Warning prominence matches Section 13.
5. Excluded details show baseline ordinal rank/score-boundary membership, exact non-ready
   criteria/reasons, optimistic bound, and potential-entry flag.
6. Excluded countries never appear at the bottom of \(R_1\) or receive a fabricated score.
7. \(R_1\) is primary; a clearly labeled 91-country \(R_0\) view is available when PCC is active.
8. An excluded country can still expose available FCC evidence while clearly marked unranked for
   the active query.
9. The browser does not recompute activation, unions, normalization, scores, bounds, or statuses.
10. Desktop/mobile, one/many/no-exclusion, all-status, tie, baseline-toggle, badge, and accessible
    warning tests pass.

### 16.6 Phase 4H: end-to-end verification and closure

Phase 4H is accepted only when:

1. End-to-end scenarios prove FCC-only 91, PCC below threshold, unions of 3/5/6/9/10, all statuses,
   K values 5/10/20, boundary ties, evidence access, and repeat determinism.
2. Structural tests prove 91 stable countries, FCC 91/91, PCC at least 82, 91 attempts per
   criterion, and no score for any non-valid PCC outcome.
3. Runtime tests prove complete \(R_1\) rows, one normalized vector, no imputation, no country-level
   renormalization, no excluded final ranks, and diagnostic-only bounds.
4. Ownership tests/review prove engine logic is not duplicated in API or UI.
5. Historical releases load unchanged; new release validation, checksums, and replay pass from
   clean Windows and Linux checkouts.
6. Pytest, Ruff, Black check, compileall, frontend typecheck/tests/build, OpenAPI/documentation
   checks, clean-checkout validation, and offline replay all pass.
7. Architecture, schema/catalog, scoring, API, UI, worker, implementation history, release report,
   roadmap, documentation index, and a Phase 4 closure report are current.
8. Closure records policy values, FCC/PCC IDs, actual unions, robustness results, limitations,
   enabled count, UI states, remaining risks, and explicitly unsolved city/profile/legal questions.

## 17. Approval gates remaining after Phase 4A

No mathematical or product-policy decision in this document remains open.

The following later-phase choices still require evidence and explicit user approval:

1. Phase 4B's candidate dispositions were approved on 2026-07-27: C11 initial, C08 second wave,
   C53 reserve, and C26 deferred; Phase 4F production onboarding remains a separate gate.
2. The exact frozen scoring construct for any candidate that remains experimental, especially C08.
3. Any decision to enable C53 despite its weak discrimination and narrow semantics.
4. Phase 4F activation of a new immutable release after source, replay, validation, and
   cross-platform gates pass.

These are candidate and release approval gates, not permission to alter the Phase 4A algorithm.
