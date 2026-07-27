# Konsider Phase 3E — deterministic measured probes

> Research output only. No production scoring, imputation, release publication, or source substitution was performed.

## Executive result

All seven probes passed the Phase 3 coverage threshold of 82/91. Offline replay passed for 7/7.

| ID | Valid | Missing | Stale | Invalid | Phase 3C delta | Full 91 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| C08 | 87/91 | 2 | 1 | 1 | -1 | FAIL | EXPERIMENTAL_CANDIDATE |
| C11 | 88/91 | 2 | 1 | 0 | +0 | FAIL | PRODUCTION_CANDIDATE |
| C30 | 91/91 | 0 | 0 | 0 | +0 | PASS | PRODUCTION_CANDIDATE |
| C29 | 91/91 | 0 | 0 | 0 | +0 | PASS | EXPERIMENTAL_CANDIDATE |
| C48 | 91/91 | 0 | 0 | 0 | +0 | PASS | PRODUCTION_CANDIDATE |
| C49 | 91/91 | 0 | 0 | 0 | +0 | PASS | PRODUCTION_CANDIDATE |
| C53 | 86/91 | 2 | 0 | 3 | +0 | FAIL | RESERVE_CANDIDATE |

## Aggregate recommendations

- **Production candidates:** C11, C30, C48, C49
- **Experimental candidates:** C08, C29
- **Reserve candidates:** C53
- **Rejected:** none.

## Evidence interpretation

- `valid` requires presence, parsing, the candidate-specific freshness rule, and all declared component checks.
- `unmapped` counts source records outside the stable 91-country registry, including excluded countries/economies; it is not a count of missing stable countries.
- Raw source bytes are retained in the ignored content-addressed repository. The inventory records exact checksums, URLs, HTTP metadata and versions.
- The first C08 diagnostic run was discarded from committed artifacts after it incorrectly treated the published schooling component as a 0-100 percentage. The corrected v2 run removes that unsupported maximum and is the result used below.

## C08

- **Run:** `phase3e-2026-07-26-c08-online-v2`
- **Phase 3C expectation:** 89 countries with HLO/LAYS, of which 88 had a 2024+ label; BHS and BOL missing.
- **Measured:** 87/91 valid; 2 missing; 1 stale; 1 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C -1.
- **Licence:** PASS_CC_BY_4_0_WITH_ATTRIBUTION.
- **Recommendation:** **EXPERIMENTAL_CANDIDATE** — Coverage passes, but ATG lacks the schooling component, GUY is stale, the published schooling component is not a 0-100 percentage, and the primary HLO/LAYS/component choice must be settled before production scoring.
- **Non-valid countries:** ATG=invalid (VAL_COMPONENT_MISSING:hci_plus_schooling_component); BHS=missing (COV_SOURCE_RECORD_MISSING); BOL=missing (COV_SOURCE_RECORD_MISSING); GUY=stale (FRS_STALE)
- **Only-blocker countries across this seven-probe batch:** BOL, GUY
- **Offline replay:** PASS.

## C11

- **Run:** `phase3e-2026-07-26-c11-online`
- **Phase 3C expectation:** 88/91 current intersection; ATG, GRD and UKR previously absent.
- **Measured:** 88/91 valid; 2 missing; 1 stale; 0 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_WITH_ATTRIBUTION.
- **Recommendation:** **PRODUCTION_CANDIDATE** — The exact three-component ILOSTAT source passes at 88/91 with deterministic mapping and favourable reuse. Production consideration requires an explicit missing/stale policy and scoring sensitivity review.
- **Non-valid countries:** ATG=missing (COV_SOURCE_RECORD_MISSING); GRD=missing (COV_SOURCE_RECORD_MISSING); UKR=stale (FRS_STALE)
- **Only-blocker countries across this seven-probe batch:** UKR
- **Offline replay:** PASS.

## C30

- **Run:** `phase3e-2026-07-26-c30-online`
- **Phase 3C expectation:** 91/91 current WDI observations.
- **Measured:** 91/91 valid; 0 missing; 0 stale; 0 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_WITH_ATTRIBUTION.
- **Recommendation:** **PRODUCTION_CANDIDATE** — The exact source is fresh, valid and complete for 91/91. Keep the construct label narrow and resolve whether immigrant share is scored higher-better or treated as preference/context.
- **Non-valid countries:** none
- **Only-blocker countries across this seven-probe batch:** none
- **Offline replay:** PASS.

## C29

- **Run:** `phase3e-2026-07-26-c29-online`
- **Phase 3C expectation:** 91/91 with at least three 2020-2024 observations in both components and a 2023+ latest year.
- **Measured:** 91/91 valid; 0 missing; 0 stale; 0 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_WITH_ATTRIBUTION.
- **Recommendation:** **EXPERIMENTAL_CANDIDATE** — Both exact time series pass for 91/91, but exchange-rate regime flags, currency breaks, log-return construction and component weighting remain criterion-level methodology decisions.
- **Non-valid countries:** none
- **Only-blocker countries across this seven-probe batch:** none
- **Offline replay:** PASS.

## C48

- **Run:** `phase3e-2026-07-26-c48-online`
- **Phase 3C expectation:** 91/91 for GOV_WGI_PV_EST in 2024.
- **Measured:** 91/91 valid; 0 missing; 0 stale; 0 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_FOR_PUBLISHED_AGGREGATES.
- **Recommendation:** **PRODUCTION_CANDIDATE** — The published aggregate estimate is fresh and valid for 91/91. A production implementation must retain or separately capture WGI uncertainty and avoid treating small rank differences as precise.
- **Non-valid countries:** none
- **Only-blocker countries across this seven-probe batch:** none
- **Offline replay:** PASS.

## C49

- **Run:** `phase3e-2026-07-26-c49-online`
- **Phase 3C expectation:** 91/91 for GOV_WGI_RL_EST in 2024.
- **Measured:** 91/91 valid; 0 missing; 0 stale; 0 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_FOR_PUBLISHED_AGGREGATES.
- **Recommendation:** **PRODUCTION_CANDIDATE** — The narrowed Rule of law source is fresh and valid for 91/91. Production consideration requires uncertainty handling and an overlap decision against other governance criteria.
- **Non-valid countries:** none
- **Only-blocker countries across this seven-probe batch:** none
- **Offline replay:** PASS.

## C53

- **Run:** `phase3e-2026-07-26-c53-online`
- **Phase 3C expectation:** 86/91 had both basic-water and basic-sanitation observations from 2022-2024.
- **Measured:** 86/91 valid; 2 missing; 0 stale; 3 invalid; 0 parse-failed.
- **Comparison:** valid-count delta versus Phase 3C +0.
- **Licence:** PASS_CC_BY_4_0_WITH_WHO_UNICEF_ATTRIBUTION.
- **Recommendation:** **RESERVE_CANDIDATE** — The exact pair reproduces 86 valid countries and passes the threshold, but basic service access is not water safety or continuity and is highly saturated across many likely destinations. Retain as a reserve/foundation indicator unless Phase 3F shows meaningful ranking discrimination.
- **Non-valid countries:** BHS=missing (COV_SOURCE_RECORD_MISSING); BIH=invalid (VAL_COMPONENT_MISSING:basic_sanitation_access); GRD=invalid (VAL_COMPONENT_MISSING:basic_drinking_water_access); HRV=invalid (VAL_COMPONENT_MISSING:basic_sanitation_access); NIC=missing (COV_SOURCE_RECORD_MISSING)
- **Only-blocker countries across this seven-probe batch:** BIH, HRV, NIC
- **Offline replay:** PASS.

## Output inventory

- `aggregate.json` and `aggregate.csv`: measured comparison and recommendations.
- `country-status-matrix.json` and `.csv`: all seven statuses for each stable country.
- `raw-artifact-inventory.json`: exact content-addressed inputs.
- `offline-replay-verification.json`: replay checks for every candidate.
- Each candidate run directory contains `country-results.jsonl`, `summary.json`, `sources.json`, `raw-artifacts.json`, `report.md`, and a manifest.
