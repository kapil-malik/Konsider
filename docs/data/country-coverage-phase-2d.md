# Phase 2D country coverage audit

Status: Phase 2D complete; stable 91-country release published

Audit date: 2026-07-23; final decision and publication: 2026-07-24

The discovery audit found 79 complete countries in the initial 150-country universe and 91 after
expanding to all 195 entities eligible under the public-country policy. The original 100-country
target was a discovery gate, not a defensible product-quality boundary. Phase 2D now uses this
statement:

> Konsider supports the countries for which complete and sufficiently fresh data is available
> across every enabled ranking criterion under the approved source and licensing policy.

The validated 91-country complete-case intersection is universe `stable_supported_v1`. Immutable
release `2026-07-26.3` is active; previous releases remain recoverable.

## Candidate selection

Universe `popular_relocation_v1` is defined by
`data/country-universes/popular-relocation-v1.json`.

The primary selection signal is United Nations DESA Population Division, *International Migrant
Stock 2024*, Table 1, international migrant stock at mid-year by destination, both sexes combined,
2024. The official page was checked on 2026-07-23 and 2024 was the current edition. The workbook
covers 233 countries and areas.

Country identity and regions are reconciled through:

- the English UN M49 country-or-area table, including M49, ISO alpha-2/alpha-3, region, and
  subregion;
- non-aggregate World Bank Country API metadata; and
- explicit source-controlled exclusions for non-sovereign territories and special areas.

All 20 countries in the previous active release remained candidates. Remaining slots were filled
in descending official migrant-stock order. Popularity selects candidates only; it never enters
scoring or ranking. The initial pool contains 150 countries. The expanded diagnostic uses every one
of the 195 eligible countries available through the same policy and retained source bytes.

Exact source bytes are retained content-addressed under ignored `data/raw/`. Checksums, versions,
record locators, candidate ranks, the canonical registry, and coverage outputs are preserved in:

- `data/reports/country-coverage/coverage-2026-07-23.6/`
- `data/reports/country-coverage/coverage-2026-07-23.6-all-eligible/`

## Coverage results

Initial 150-country audit:

| Criterion | Found | Fresh | Parsed | Validated/scored | Missing or unusable | Only blocker |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Population-weighted PM2.5 | 150 | 150 | 150 | 150 | 0 | 0 |
| Intentional homicide rate | 135 | 94 | 135 | 94 | 56 | 26 |
| Household-consumption relative cost | 148 | 130 | 147 | 129 | 21 | 4 |
| Women's legal and economic equality | 148 | 148 | 148 | 148 | 2 | 0 |
| Infrastructure readiness composite | 145 | 116 | 145 | 116 | 34 | 9 |

Historical discovery result: **79 of 150** against the original 100-country target (**FAIL**).

Expanded 195-country diagnostic:

| Criterion | Found | Fresh | Parsed | Validated/scored | Missing or unusable | Only blocker |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Population-weighted PM2.5 | 193 | 193 | 193 | 193 | 2 | 0 |
| Intentional homicide rate | 177 | 114 | 177 | 114 | 81 | 30 |
| Household-consumption relative cost | 190 | 161 | 189 | 160 | 35 | 4 |
| Women's legal and economic equality | 186 | 186 | 186 | 186 | 9 | 0 |
| Infrastructure readiness composite | 168 | 134 | 168 | 134 | 61 | 13 |

Validated complete intersection: **91 of 195**. This became the final supported universe after the
licensing decision.

`Only blocker` counts an otherwise-complete country excluded solely by that criterion.

## Exclusions

The expanded audit excludes 104 candidates. Reasons are non-exclusive because one country can fail
more than one criterion.

| Reason | Countries |
| --- | ---: |
| Intentional homicide stale | 63 |
| Infrastructure composite stale | 34 |
| Infrastructure component missing | 27 |
| Relative-cost common year stale | 26 |
| Intentional homicide missing | 18 |
| WBL legal-framework index missing | 9 |
| Relative-cost input missing | 5 |
| Relative-cost input invalid | 4 |
| PM2.5 missing | 2 |

The complete machine-readable country/criterion status includes source-code resolution, raw-record
presence, non-null and finite checks, reference years, freshness, parsing, validation, scoring, and
reason codes. No excluded country is silently discarded.

## Regional distribution

| Region | Initial candidates | Initial complete | All eligible | All-eligible complete |
| --- | ---: | ---: | ---: | ---: |
| East Asia & Pacific | 16 | 8 | 31 | 10 |
| Europe & Central Asia | 46 | 40 | 52 | 42 |
| Latin America & Caribbean | 20 | 15 | 33 | 22 |
| Middle East, North Africa, Afghanistan & Pakistan | 23 | 7 | 23 | 7 |
| North America | 2 | 2 | 2 | 2 |
| South Asia | 5 | 1 | 6 | 1 |
| Sub-Saharan Africa | 38 | 6 | 48 | 7 |

Regional breadth shapes candidate discovery only. It never overrides complete-case validity.

## Limiting criteria and source alternatives

### Intentional homicide

The current source remains World Bank WDI `VC.IHR.PSRC.P5`, an explicitly CC BY 4.0
representation of UNODC data. It is the binding constraint: 63 of 195 values are stale under the
five-year rule, 18 are missing, and 30 otherwise-complete countries fail only this criterion.

Phase 2D.4 subsequently evaluated Direct UNODC and the UNSD SDG API. Each provided the same four
fresh, equivalent additions—Bangladesh, Belarus, Kuwait, and Saudi Arabia—but neither provides a
clear production reuse grant covering retained, transformed, and redistributed artifacts. The
source was therefore not changed.

Extending homicide freshness from five to eight years would raise the all-eligible complete
intersection from 91 to exactly 100 by accepting values as old as 2018. That would weaken the
current validation policy and is not recommended or implemented.

### Infrastructure

The limiting component is predominantly Logistics Performance Index infrastructure coverage and
age. World Bank's 2023 LPI covers 139 countries, so using the direct 2023 LPI release does not solve
the structural coverage ceiling. Replacing LPI with electricity, roads, mobile connectivity, or
another broader indicator would materially change the experimental composite's meaning and requires
an explicit product decision. No component or weighting changed.

### Relative cost

The latest ICP benchmark is the 2021 cycle, covering 176 participating economies. Official ICP
materials identify imputed results for additional non-participating economies. Phase 2D forbids
imputation, so those estimates are not an acceptable way to increase coverage. The existing WDI
PPP/exchange-rate derivation remains unchanged.

## Final decision and publication

The final production homicide strategy is World Bank WDI `VC.IHR.PSRC.P5` only. Its representation
is explicitly CC BY 4.0. Direct UNODC and UNSD remain rejected for production because their reuse
rights are ambiguous; Eurostat adds none of the residual countries and OECD is not a national-total
equivalent series. Their investigation remains in the
[Phase 2D.4 report](homicide-source-feasibility-phase-2d4.md), while their runtime adapters and CLI
were removed.

The final list is generated from this audit and recorded at
`data/country-universes/stable-supported-v1.json`. It records:

- universe ID `stable_supported_v1` and policy `complete-case-approved-sources-v1`;
- 91 unique ISO alpha-3 country codes and regions;
- source audit `coverage-2026-07-23.6-all-eligible` and source versions;
- the complete-case inclusion rule and link to all 104 detailed exclusions; and
- the final licensing decision, including the four technically recoverable exclusions.

The five-year homicide freshness rule is unchanged. No imputation, manually copied value, partial
scoring, unsupported territory, or popularity signal enters affinity scoring. Each of the six
published criteria has 91/91 observations and scores; UHC remains non-ready because all 2021
observations fail its separate three-year readiness rule. The five enabled criteria are complete
and ready for all 91 countries.

## Reproducibility and limitations

The online audit completed in approximately 15 seconds after using the World Bank's documented
indicator-level CSV ZIP representation of the same registered WDI series; this avoided a temporary
JSON API 502/time-out condition without changing source data or semantics. Offline replay completed
in approximately two seconds. Candidate, registry, criterion, country, exclusion, artifact, and
source files were byte-identical between online processing and replay.

The audit does not claim that the supported or candidate countries are "best countries." It reports
the current supported country universe with complete data across enabled criteria. No data was
fabricated, manually entered, substituted, partially scored, or imputed.
