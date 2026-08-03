# Phase 6B.1 — Career opportunity gap fill and threshold calibration

Date: 2026-08-03
Release baseline: 2026-07-29.2
Status: **RESEARCH COMPLETE — NO PRODUCTION CHANGE**

## Outcome

Phase 6B.1 closes enough of the targeted evidence gap to move the frozen technology/software and science/engineering constructs into implementation design without changing ranking, ordering, runtime schemas, presets, APIs, UI, workers, or releases.

- **Technology/software:** `APPROVE_FOR_IMPLEMENTATION_DESIGN`. Malta supplies high-confidence harmonised ISCO evidence and Canada supplies medium-confidence national evidence under a transparent, tightly aligned NOC mapping. Assessability rises from 61/91 to 63/91. Four benchmark lists rise from 15/20 to 17/20; the family/education list rises from 17/20 to 18/20.
- **Science/engineering:** `APPROVE_FOR_IMPLEMENTATION_DESIGN`. Malta supplies exact harmonised ISCO evidence. Assessability rises from 66/91 to 67/91. Four benchmark lists rise from 15/20 to the hard floor of 16/20; the family/education list remains 17/20. Canada is retained as supplemental evidence only because no official NOC 2021 to ISCO-08 concordance was located and its result would otherwise be a negative.
- **Japan, South Korea, and New Zealand:** remain explicit source or granularity holds for these two constructs. No proxy was used to manufacture coverage.
- **Threshold:** retain the global P60 scale/share rule. P55 and P65 demonstrate expected movement around the boundary; P50 and P70 are materially permissive/restrictive. The rule remains global and no country-specific threshold is introduced.

## Frozen constructs and public meaning

Technology/software remains employment in ISCO-08 groups 25 and 35. Science/engineering remains employment in ISCO-08 groups 21 and 31. The public statement for either is “a substantial and established employment ecosystem.” It does not mean live vacancies, job quality, licence recognition, immigration eligibility, applicant success probability, or absence of jobs when the state is not established.

## National source results

| Country | Disposition | Classification | Finding |
|---|---|---|---|
| CAN | PARTIAL_GAP_FILL_TECHNOLOGY_ONLY | NOC 2021 Version 1.0 | No official NOC 2021 to ISCO-08 concordance was located; technology is a tight semantic mapping, science remains supplemental-only for a negative result. |
| JPN | HOLD_CROSSWALK_GAP | Japan Standard Occupational Classification, December 2009 revision | The retained annual workbook publishes only major groups; professional and engineering workers cannot be split into the frozen technology and science constructs. |
| KOR | HOLD_SOURCE_GAP | Korean Standard Classification of Occupations, 8th revision | One-digit occupation groups cannot isolate ISCO-08 25+35 or 21+31. |
| MLT | COMPLETE_GAP_FILL_BOTH_CONSTRUCTS | ISCO-08 two-digit | Small-country estimates remain below the global scale floor; result is a defensible not-established state, not no jobs. |
| NZL | HOLD_SOURCE_GAP | ANZSCO v1.3, public national table at major level 1 | The located full-population table exposes occupation only at major level; a concordance alone cannot create detailed employment counts. |

Official sources and reuse terms frozen in the source matrix include Eurostat dataset `lfsa_egai2d`, Statistics Canada table 98-10-0594-01, Japan e-Stat Labour Force Survey historical table 6, KOSIS table DT_1DA7E27S and its official 1-digit dissemination clarification, and Stats NZ 2023 Census dataset CEN23_WRK_009.

## Crosswalk decisions

Malta needs no crosswalk: the source is already ISCO-08 at two digits. Canada technology uses NOC 2122, 2123, and 2222 because their published labels align tightly with ISCO-08 groups 25 and 35. Canada science uses a documented research mapping only as supplemental evidence; mixed NOC groups 2112 and 2223 are excluded, and the aggregate cannot establish a public negative without an official concordance.

Japan publishes only a combined professional/engineering group in the retained annual workbook. Korea officially states that public occupation-by-sex data are disseminated only at 1 digit. The full-population New Zealand Census table located in Data Explorer exposes occupation at major-group level; an official classification concordance exists separately, but no matching detailed national employment stock was located. These are gaps, not zeroes.

## Gap-fill evidence

| Country | Construct | State | Scale (thousand) | Share (%) | Confidence |
|---|---|---|---:|---:|---|
| CAN | Technology | VERIFIED_STRONG_SIGNAL | 613.685 | 3.542868 | MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK |
| CAN | Science/engineering | INSUFFICIENT_EVIDENCE | 715.635 | 4.131436 | LOW_CONFIDENCE_SUPPLEMENTAL |
| JPN | Technology | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |
| JPN | Science/engineering | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |
| KOR | Technology | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |
| KOR | Science/engineering | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |
| MLT | Technology | STRONG_SIGNAL_NOT_ESTABLISHED | 11 | 3.349574 | HIGH_CONFIDENCE_OBSERVED_HARMONISED |
| MLT | Science/engineering | STRONG_SIGNAL_NOT_ESTABLISHED | 21.7 | 6.607795 | HIGH_CONFIDENCE_OBSERVED_HARMONISED |
| NZL | Technology | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |
| NZL | Science/engineering | INSUFFICIENT_EVIDENCE | — | — | LOW_CONFIDENCE_SUPPLEMENTAL |

Malta 2025 technology is 11.0 thousand (3.3496%) and science/engineering is 21.7 thousand (6.6078%). Both remain below the global scale floor and therefore produce a defensible `STRONG_SIGNAL_NOT_ESTABLISHED` state. Canada technology is 613.685 thousand (3.5429%) and crosses the P80-scale/P40-share route. The narrower Canada science aggregate is 715.635 thousand (4.1314%) but is supplemental-only and cannot publish a negative.

## Benchmark coverage before and after

Opportunity evidence is joined after each current top-20 list is generated and never changes list order.

| Construct | Profile | Before | After | ≥16 hard floor | ≥18 preferred |
|---|---|---:|---:|---|---|
| Technology | general_balanced | 15 | 17 | yes | no |
| Technology | affordability_sensitive | 15 | 17 | yes | no |
| Technology | safety_governance_oriented | 15 | 17 | yes | no |
| Technology | career_prioritised | 15 | 17 | yes | no |
| Technology | family_education_oriented | 17 | 18 | yes | yes |
| Science/engineering | general_balanced | 15 | 16 | yes | no |
| Science/engineering | affordability_sensitive | 15 | 16 | yes | no |
| Science/engineering | safety_governance_oriented | 15 | 16 | yes | no |
| Science/engineering | career_prioritised | 15 | 16 | yes | no |
| Science/engineering | family_education_oriented | 17 | 17 | yes | no |

The hard floor is satisfied for both constructs. Science remains dependent on Malta for the four 16/20 results; removing the Eurostat Malta source returns those lists to 15/20. This dependency is recorded as an implementation risk, not hidden by a broader proxy.

## Confidence and precedence

The frozen order is: recent harmonised observed; recent official national observed with a strong documented mapping; harmonised modelled; supplemental. Observed evidence is never overwritten by modelled evidence. Contradictions are retained for review. High-confidence complete evidence may establish either positive or negative. Medium-confidence evidence may establish a positive; a negative requires defensible mapping completeness. Low-confidence supplemental evidence never produces a public negative.

## Threshold calibration

The retained rule is: (scale >= P60 and share >= P60) OR (scale >= P80 and share >= P40) OR (share >= P80 and scale >= P40).

At P60 after gap fill, technology has 20 verified, 43 not-established, and 28 insufficient states. Science/engineering has 20 verified, 47 not-established, and 24 insufficient states.

Adding Malta and Canada to the calibration pool changes raw P60 thresholds only slightly; policy thresholds remain frozen to the pre-gap-fill reference pool to prevent target-driven drift. Malta’s 2024 and 2025 results produce the same public states. Canada has only the 2021 Census stock in the accepted route, so no false annual stability claim is made.

## Anchor-country review

| Country | Technology P60 | Science P60 | Review |
|---|---|---|---|
| AUS | VERIFIED_STRONG_SIGNAL | STRONG_SIGNAL_NOT_ESTABLISHED | Existing Phase 6B evidence retained without exception. |
| CAN | VERIFIED_STRONG_SIGNAL | INSUFFICIENT_EVIDENCE | Technology accepted; science negative suppressed to insufficient. |
| DEU | VERIFIED_STRONG_SIGNAL | VERIFIED_STRONG_SIGNAL | Existing Phase 6B evidence retained without exception. |
| IND | STRONG_SIGNAL_NOT_ESTABLISHED | STRONG_SIGNAL_NOT_ESTABLISHED | Existing Phase 6B evidence retained without exception. |
| JPN | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | Granularity hold retained; no proxy state. |
| KOR | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | Granularity hold retained; no proxy state. |
| MLT | STRONG_SIGNAL_NOT_ESTABLISHED | STRONG_SIGNAL_NOT_ESTABLISHED | Exact harmonised evidence; scale floor prevents small-country false positive. |
| NZL | INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE | Granularity hold retained; no proxy state. |
| SGP | VERIFIED_STRONG_SIGNAL | VERIFIED_STRONG_SIGNAL | Existing Phase 6B evidence retained without exception. |
| USA | VERIFIED_STRONG_SIGNAL | VERIFIED_STRONG_SIGNAL | Existing Phase 6B evidence retained without exception. |

No anchor result required a country exception. Sensitivity movement is reported rather than edited away.

## Broad criterion naming and route decisions

- **Care-sector employment ecosystem:** approve with naming change; internal construct remains ISIC Rev.4 section Q, human health and social work.
- **Finance and insurance employment ecosystem:** retain. Business and administration evidence remains supplemental and cannot broaden the public claim.
- **Skilled-trades or construction employment ecosystem:** retain the transparent OR route. At P60 the route analysis records 15 skilled-only, 11 construction-only, 8 both-route, and 54 neither-route countries. Implementation must expose which route established the state.
- **Research and academic ecosystem:** move to the education/research phase. ISIC M72 is an R&D-sector proxy and cannot stand for academia or field-relevant research opportunity.

## Final research portfolio

Approved for implementation design: care-sector; finance and insurance; skilled-trades or construction; technology/software; science/engineering. Research and academic ecosystem moves to the education/research phase. No production work is authorised by this report.

## Files and verification

The dated report directory contains the source matrix, crosswalks, ten country/construct evidence rows, confidence and route policies, before/after coverage, threshold calibration, anchor review, route/naming analysis, final portfolio, and checksum manifest. The replay script verifies one row per target-country/construct pair, ISO alpha-3 codes, metric compatibility, shortlist floors, frozen global thresholds, JSON/JSONL parsing, raw-capture checksums where retained, and deterministic no-diff replay.

## Owner decisions before implementation

1. Accept technology and science/engineering at the hard shortlist floor, noting that science reaches 16/20 rather than the preferred 18/20 in four profiles.
2. Accept Canada technology as medium-confidence national observed evidence under the documented semantic mapping.
3. Accept the care-sector public name while retaining section Q internally.
4. Require route visibility for the skilled-trades/construction OR construct.
5. Confirm that research/academia will be handled in the education/research phase rather than through M72.
