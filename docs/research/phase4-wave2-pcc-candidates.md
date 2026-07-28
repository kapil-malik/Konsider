# Phase 4 Wave 2 partial-coverage candidate shortlist

Status: two candidates onboarded experimentally in release `2026-07-28.2`; remaining candidates
retain explicit gates

Updated: 2026-07-28

Phase 4's conditional complete-case model makes a criterion technically representable when at
least 82 of the 91 stable countries have fresh, valid observations. Technical fit is not production
approval: source licensing, construct validity, scoring, discrimination, regional concentration,
replay, and maintenance must still pass independently.

## Strongest Wave 2 candidates

### School education quality (C08) — onboarded experimentally

- Production evidence: 88/91 valid after freezing LAYS alone.
- Exact non-valid outcomes: The Bahamas and Bolivia missing; Guyana stale.
- Why it is strong: high relocation value for families, authoritative reusable source, exact
  online/offline replay, and robust Phase 4B singleton and combination simulations.
- Frozen construct: learning-adjusted years of schooling.
- Required label boundary: national modelled learning conditions, not the quality of a particular
  school or city.
- Disposition: experimental conditional criterion in release `2026-07-28.2`.

### Financial protection from health costs (C26) — priority after licensing

- Current evidence: 90/91 valid; Ukraine is stale.
- Why it is strong: excellent coverage, high relocation relevance, simple maintenance, and robust
  singleton simulations.
- Required gate: resolve `LIC_REDISTRIBUTION_REVIEW` for production use and redistribution.
- Required construct: lower out-of-pocket spending share as a national financial-protection proxy.
- Required label boundary: it does not measure migrant eligibility, premiums, waiting times,
  healthcare quality, or a household's personal affordability.
- Intended disposition: conditional criterion after licensing and scoring approval.

## Strong re-probe candidates

These candidates have plausible Phase 4 coverage and useful national constructs, but they have not
yet passed the exact deterministic evidence required for onboarding.

### Research and innovation ecosystem (C05) — onboarded experimentally

- Exact coverage: 85/91 in the pinned WIPO GII 2025 workbook.
- Potential value: national research output and innovation capacity can inform researchers,
  founders, and highly skilled movers.
- Frozen construct: WIPO's published Innovation outputs sub-index. The overall GII and input
  pillars are excluded to reduce overlap with education, infrastructure, and governance.
- Disposition: experimental conditional criterion in release `2026-07-28.2`.

### Social-protection system reach (C76)

- Estimated coverage: at least 90% appears plausible.
- Potential value: adds a national welfare-system reach signal not currently represented.
- Required work: exact source probe, modelled-value treatment, scoring and discrimination, and a
  strict caveat that system reach does not establish a migrant's eligibility or likely benefit.

### Food-safety system capacity (C54)

- Estimated coverage: at least 82/91 appears plausible.
- Potential value: provides a narrower public-health protection signal without claiming individual
  food-safety outcomes.
- Required work: exact source join and licensing, treatment of self-reported capacity, scoring
  sensitivity, and proof that the measure discriminates meaningfully.

### Freedom of expression and religion (C75)

- Estimated coverage: at least 90% appears plausible.
- Potential value: directly relevant to personal liberty and relocation fit.
- Required work: production-compatible licence for the exact dataset, a narrow predeclared variable
  set, rater-count and uncertainty policy, and a decision on whether expression and religion should
  remain separate rather than forming a normatively weighted composite.

## Watchlist, not Wave 2-ready

| Criterion | Why it is not currently a strong Wave 2 candidate |
| --- | --- |
| Overall higher-education opportunity (C01) | 88 countries were found, but only 77 met the preferred freshness rule and only 81 had 2021+ data, below the 82-country minimum. Revisit after a newer edition. |
| Entrepreneurship and startup opportunity (C16) | Exact measured coverage was 79/91 and the source has partial-geography and outlier problems. |
| Basic water and sanitation access (C53) | 86/91 technically qualifies, but the measure is saturated, narrow, and weakly discriminating; retain as reserve/context. |
| Working-time burden (C71) | Exact fresh coverage was 72/91, below policy. |
| Overall life satisfaction (C78) | Exact coverage is unmeasured, production licensing is unresolved, and the umbrella outcome risks double-counting the entire portfolio. |
| Social inclusion and acceptance of immigrants (C42) | Available survey scope is below 82, field years are mixed, and production reuse is unresolved. |

## Deliberately outside the PCC Wave 2 list

Macroeconomic stability and extreme-weather risk both measured 91/91. They remain worthwhile global
experimental candidates, but they do not need Phase 4's partial-coverage mechanism. City,
occupation, household, and applicant-specific legal criteria also remain outside this list because
conditional country coverage does not correct the wrong unit of analysis.

## Required Wave 2 gate

Before any candidate leaves this shortlist:

1. freeze the exact source, edition, series, licence, parser, freshness and attribution;
2. preserve one explicit outcome for every stable country;
3. require at least 82 fresh, valid countries;
4. freeze a versioned scoring method and component sensitivity analysis;
5. review regional concentration and discrimination;
6. simulate every active-PCC missing-country union;
7. pass online capture, offline replay, release validation, repository loading and API tests; and
8. publish only through a new immutable release.
