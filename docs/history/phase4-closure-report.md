# Phase 4 closure report

Status: complete; remote clean-checkout CI design corrected after the first matrix observation

Closed: 2026-07-28

Active release: `2026-07-28.2`

Policy: `uncertainty-aware-ranking-policy-1.0`

## Outcome

Phase 4 adds partial-coverage criteria without changing the stable 91-country catalog, imputing
missing values, or scoring countries with different criterion sets. A request with an active
partial-coverage criterion ranks only its complete-case eligible universe and reports excluded
countries separately with robustness diagnostics.

Phase 4 does not solve city-level, occupation-level, household-level, or applicant-specific
suitability. Its scores remain national indicators.

## Approved policy

| Policy | Value |
| --- | ---: |
| Stable catalog | 91 countries |
| Minimum valid PCC coverage | 82 countries |
| Preferred missing-union maximum | 5 |
| Hard missing-union maximum | 9 |
| Minimum eligible ranking universe | 82 |
| PCC activation threshold | Raw weight 0.6 |
| Default robustness K | 10 |
| Optimistic non-ready PCC substitution | 10 |
| Tie breaker | Ascending ISO-3 for display |
| Top-K membership | Score boundary, including every Kth-score tie |

When no PCC reaches 0.6, the result is always `NO_PARTIAL_CRITERIA_ACTIVE`. A missing union above
9 returns the 91-country FCC-only baseline and `COVERAGE_LIMIT_EXCEEDED`; no R1 threshold or
potential-entry conclusion is produced.

## Release inventory

Release `2026-07-28.2` has 12 available criteria, 11 ranking-ready criteria, 1,080 observations,
1,080 scores, and 1,092 explicit criterion-country outcomes.

### Global-core criteria

All eight FCCs are valid for 91/91 countries:

- Ambient PM2.5 exposure (`ambient_pm25_population_weighted`)
- Established immigrant presence (`established_immigrant_presence`)
- Household consumption price level (`household_consumption_price_level_us_100`)
- Infrastructure readiness (`infrastructure_readiness_composite`, experimental)
- Intentional homicide rate (`intentional_homicide_rate`)
- Political stability (`political_stability`)
- Rule of law (`rule_of_law`)
- Women's legal and economic equality (`women_legal_economic_equality`)

### Conditional complete-case criteria

| Criterion | Valid | Non-ready countries |
| --- | ---: | --- |
| Overall job-market opportunity (`overall_job_market_opportunity`) | 88/91 | ATG, GRD, UKR |
| School education quality (`school_education_quality`, experimental) | 88/91 | BHS, BOL, GUY |
| Research and innovation ecosystem (`research_innovation_ecosystem`, experimental) | 85/91 | ATG, BHS, FJI, GRD, GUY, HTI |

UHC service coverage remains diagnostic-only and cannot be weighted.

## Actual missing-country unions

| Active PCC set | Excluded | Eligible | Band |
| --- | ---: | ---: | --- |
| Job market | 3 | 88 | Preferred |
| School education | 3 | 88 | Preferred |
| Research and innovation | 6 | 85 | Elevated |
| Job market + school education | 6 | 85 | Elevated |
| Job market + research and innovation | 7 | 84 | Elevated |
| School education + research and innovation | 7 | 84 | Elevated |
| All three | 8 | 83 | Elevated |

The all-three union is ATG, BHS, BOL, FJI, GRD, GUY, HTI, and UKR. No currently published PCC
combination exceeds the hard limit. The blocked 10-country behavior is nevertheless covered by
fixture-backed golden tests.

## Verification results

The active equal-weight profile activates all three PCCs. At K=5, 10, and 20 it returns
`ROBUST_TOP_K`, ranks 83 eligible countries, and keeps all eight excluded countries unranked.
Research and innovation alone is `POTENTIALLY_AFFECTED` at K=20, proving that the active release
can surface a non-robust boundary rather than always producing the benign state.

Synthetic golden scenarios prove:

- missing unions of 0, 3, 5, 6, 9, and 10;
- every robustness status;
- omitted, explicit-zero, 0.2, 0.4, and exactly-0.6 PCC weights;
- optimistic bounds below, equal to, and above the R1 Kth score;
- R0 and R1 Kth-score ties;
- K values 5, 10, and 20;
- baseline-top-K exclusion; and
- coverage-limit output with no R1 fields or potential-entry decision.

Structural and runtime tests prove:

- exactly 91 outcomes per criterion;
- FCC coverage of 91/91 and PCC coverage of at least 82/91;
- a score exists exactly when the corresponding outcome is valid;
- every displayed R1 row has every active criterion;
- every R1 row uses the same normalized vector;
- contributions reconcile to the total;
- non-ready outcomes are not imputed or renormalized per country;
- excluded countries receive no R1 row or final rank; and
- optimistic bounds remain response diagnostics, not published scores.

API routes and mappers delegate ranking and comparison decisions to the service/domain layer. The
React UI renders typed API metadata and requests a separate FCC baseline; it does not reproduce
activation, union, scoring, tie, or robustness logic.

## UI states

The UI covers all six statuses, FCC/PCC coverage badges, the Medium activation threshold,
eligible-of-91 rank scope, exclusion details, score-boundary warnings, API-fetched baseline
toggle, and comparisons with unavailable cells. An excluded country retains accessible FCC
evidence but displays no partial aggregate score or final rank.

## Reproducibility and history

Release payload checksums and offline replay pass for `2026-07-28.2`. Release-scoped catalog
snapshots make `2026-07-27.1`, `2026-07-28.1`, and `2026-07-28.2` loadable without reinterpreting
their criterion sets. The first remote matrix run exposed two production-rebuild test modules that
did not apply the repository's clean-checkout policy for intentionally uncommitted licensed raw
bytes. Those tests now run fully when their exact local artifacts exist and skip only when the raw
files are absent; committed release integrity, synthetic parser coverage, structural invariants,
and runtime behavior remain mandatory. CI runs the backend gates independently on clean Ubuntu and
Windows checkouts, without matrix fail-fast cancellation, while the frontend contract and browser
gates run from a clean Ubuntu checkout.

Historical Phase 3 and Phase 4 working directories now live under
[`project-history/phases`](../../project-history/phases), leaving the repository root for current
runtime, data, contracts, tests, and documentation.

## Limitations and remaining risks

- Financial protection from health costs remains blocked by conflicting exact-asset WHO GHED
  reuse terms.
- Social-protection system reach needs a frozen export and policy for reported versus modeled or
  imputed publisher values.
- Food-safety system capacity needs an exact licensed export and proof that the self-reported
  capacity construct is useful.
- Freedom of expression and religion needs explicit production redistribution terms, exact
  variables, weighting, and uncertainty treatment.
- School quality and innovation are experimental broad national proxies.
- Job-market scores use modeled national labor indicators and do not determine occupation,
  licensing, visa, salary, or applicant prospects.
- Manual refresh and local raw-artifact retention remain operational risks.

## Next phase

Phase 5 may add conversational exploration only over typed deterministic tools. Numerical and
source claims must continue to originate from the release and ranking engine, with non-LLM
fallbacks and explicit operating limits. Held criteria should be onboarded only through the same
source, licensing, construct, coverage, scoring, replay, and immutable-release gates.

Detailed local gate evidence is in the
[Phase 4H verification report](../../data/reports/phase4h-2026-07-28/report.md).
