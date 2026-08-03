# Phase 6C — Higher-education opportunity exploration

Date: 2026-08-03
Status: **RESEARCH COMPLETE — OWNER DECISIONS REQUIRED — NO PRODUCTION CHANGE**

## Outcome

Four of the six Phase 6C directions have a defensible research-only route, but only after narrowing their public names to the official evidence taxonomy. Business/finance remains on hold because the available field is too broad. Broad university excellence is rejected as an opportunity criterion because scientific performance is neither generic excellence nor a complete applicant opportunity measure and would overlap the existing research/innovation criterion.

The four recommended constructs describe a country's **research-intensive university ecosystem**. They do not measure admissions, teaching quality, affordability, accreditation, qualification recognition, visa eligibility, campus access, or an applicant's chance of success.

- **Physical sciences and engineering research-university ecosystem:** APPROVE_WITH_NAMING_OR_SCOPE_CHANGE.
- **Mathematics and computer science research-university ecosystem:** APPROVE_WITH_NAMING_OR_SCOPE_CHANGE.
- **Biomedical and health sciences research-university ecosystem:** APPROVE_WITH_NAMING_OR_SCOPE_CHANGE.
- **Life and earth sciences research-university ecosystem:** APPROVE_WITH_NAMING_OR_SCOPE_CHANGE.

Research/academia, moved from Phase 6B, is resolved through these field-specific education research ecosystems rather than revived as an employment proxy.

## Method inherited from Phase 6B.1

The Phase 6C prompt remains controlling. The augmented protocol pre-registers constructs, evidence routes, source precedence, negative capability, global thresholds, P50–P70 sensitivity, dependency removal, benchmark coverage, deterministic fixtures, and owner dispositions before outcomes are interpreted. Complete narrow evidence may establish either a positive or a carefully worded not-established state. Missing countries and taxonomy mismatches remain insufficient; no zero is invented.

## Primary source and rights

The retained route is CWTS Leiden Ranking Open Edition 2025 (DOI 10.5281/zenodo.17473224), using its frozen August 2025 OpenAlex snapshot and 2020–2023 publication window. It contains 2,831 universities in 120 countries and five broad fields. Its result and underlying data are CC0; the official workbook provides ROR identities. The source's own responsible-use boundary is decisive: this is scientific performance, not a generic best-university or teaching-quality measure.

The direct OpenAlex API is not needed for this release-specific route. UIS OPRI remains a possible specialization supplement but is held outside the primary signal pending a separate legal/coverage decision. No GeoNames or inferred campus coordinates are used.

## Institution identity and accessibility boundary

The mapping contains 2831 institutions and 2825 exact name/country matches. Six quoted names truncated in HTML tooltips use explicit high-confidence manual disambiguations. Every row has a unique ROR ID. Country is the only location signal retained. Locality, campus distribution, multi-campus status, cross-border provision, online availability, and applicant accessibility remain unknown and must be resolved before any institution-level experience is designed.

## Candidate decisions

P60 cells show verified / not-established / insufficient across the fixed 91-country universe.

| Prompt direction | Evidence-aligned public name | P60 states | Disposition |
|---|---|---:|---|
| Engineering and technology | Physical sciences and engineering research-university ecosystem | 27/48/16 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Computer science and ICT | Mathematics and computer science research-university ecosystem | 30/45/16 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Medicine and health sciences | Biomedical and health sciences research-university ecosystem | 30/45/16 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Business and finance | Business and finance higher-education opportunity | 0/0/91 | HOLD_SOURCE_GAP |
| Natural sciences | Life and earth sciences research-university ecosystem | 31/44/16 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Broad university excellence | Broad scientific research-university ecosystem | 29/46/16 | REJECT_AS_OPPORTUNITY_CRITERION |

The four approvals pass the 60/91 assessability gate, every frozen-list 16/20 gate, and the eight-country smaller-class discrimination gate. Their approvals remain naming/scope changes because the official fields are not identical to the prompt shorthand.

Business/finance has 91 insufficient states. The broad social-sciences field cannot safely stand in for business and finance. Broad scientific research has full diagnostic classifications but is rejected as a public opportunity criterion; a good source does not rescue an invalid product construct.

## Classification routes and P60 thresholds

A represented country passes when it has at least one global top-100 institution, at least three global top-300 institutions, or crosses one of three global output/breadth combinations. Otherwise complete evidence produces not-established. Countries absent from the research-intensive release are insufficient. Thresholds are global; there are no country exceptions.

| Official field | Base output | Base breadth | High output | High breadth | Low output | Low breadth |
|---|---:|---:|---:|---:|---:|---:|
| Physical sciences and engineering | 7834.8 | 12.8 | 30774.2 | 39.2 | 2623.2 | 6 |
| Mathematics and computer science | 6337 | 12.8 | 17870.8 | 39.2 | 2215.6 | 6 |
| Biomedical and health sciences | 12502.8 | 12.8 | 39464.8 | 39.2 | 2761.6 | 6 |
| Life and earth sciences | 4560.2 | 12.8 | 13754.6 | 39.2 | 1397.8 | 6 |
| All sciences | 42074.8 | 12.8 | 145519.4 | 39.2 | 12178.2 | 6 |

Top-100 and top-300 routes prevent a small country with a genuinely prominent institution from being erased by national scale. Output/breadth routes prevent the measure from collapsing into a single league-table position. The result remains a research ecosystem indicator, not a university ranking copied into Konsider.

## Threshold sensitivity

Verified-country counts move monotonically as the percentile becomes more demanding:

| Candidate | P50 | P55 | P60 | P65 | P70 |
|---|---:|---:|---:|---:|---:|
| Engineering and technology | 37 | 32 | 27 | 24 | 23 |
| Computer science and ICT | 38 | 35 | 30 | 27 | 23 |
| Medicine and health sciences | 39 | 34 | 30 | 27 | 25 |
| Business and finance | 0 | 0 | 0 | 0 | 0 |
| Natural sciences | 39 | 34 | 31 | 29 | 28 |
| Broad university excellence | 38 | 33 | 29 | 27 | 26 |

P60 is retained for design discussion because it discriminates without making the fixed prominence routes irrelevant. P50 is noticeably more permissive; P70 is more restrictive. The exact country lists and thresholds are in the sensitivity artifact. Only one release/window is retained, so this study makes no false stability or time-trend claim.

Removing the CWTS result source makes every supported candidate 0/91 assessable. Removing canonical ROR identity also suppresses every state under the pre-registered publication rule. This single-source dependency must be accepted explicitly or reduced in a future research phase; it is not hidden by a weak substitute.

## Frozen benchmark-list coverage

Evidence is joined after the five Phase 6B top-20 lists are generated. It never changes rank or ordering.

| Candidate | Frozen profile | Assessable | ≥16 floor |
|---|---|---:|---|
| Engineering and technology | general_balanced | 20/20 | pass |
| Engineering and technology | affordability_sensitive | 20/20 | pass |
| Engineering and technology | safety_governance_oriented | 20/20 | pass |
| Engineering and technology | career_prioritised | 20/20 | pass |
| Engineering and technology | family_education_oriented | 20/20 | pass |
| Computer science and ICT | general_balanced | 20/20 | pass |
| Computer science and ICT | affordability_sensitive | 20/20 | pass |
| Computer science and ICT | safety_governance_oriented | 20/20 | pass |
| Computer science and ICT | career_prioritised | 20/20 | pass |
| Computer science and ICT | family_education_oriented | 20/20 | pass |
| Medicine and health sciences | general_balanced | 20/20 | pass |
| Medicine and health sciences | affordability_sensitive | 20/20 | pass |
| Medicine and health sciences | safety_governance_oriented | 20/20 | pass |
| Medicine and health sciences | career_prioritised | 20/20 | pass |
| Medicine and health sciences | family_education_oriented | 20/20 | pass |
| Business and finance | general_balanced | 0/20 | fail |
| Business and finance | affordability_sensitive | 0/20 | fail |
| Business and finance | safety_governance_oriented | 0/20 | fail |
| Business and finance | career_prioritised | 0/20 | fail |
| Business and finance | family_education_oriented | 0/20 | fail |
| Natural sciences | general_balanced | 20/20 | pass |
| Natural sciences | affordability_sensitive | 20/20 | pass |
| Natural sciences | safety_governance_oriented | 20/20 | pass |
| Natural sciences | career_prioritised | 20/20 | pass |
| Natural sciences | family_education_oriented | 20/20 | pass |
| Broad university excellence | general_balanced | 20/20 | pass |
| Broad university excellence | affordability_sensitive | 20/20 | pass |
| Broad university excellence | safety_governance_oriented | 20/20 | pass |
| Broad university excellence | career_prioritised | 20/20 | pass |
| Broad university excellence | family_education_oriented | 20/20 | pass |

All five supported diagnostic fields cover all 20 countries in every frozen benchmark list. Business/finance covers none because its field route is held. This high shortlist coverage does not erase the 16 countries absent from the complete 91-country research-university universe.

## Geographic, income, and system-size review

### Physical sciences and engineering research-university ecosystem

- Assessable by region: East Asia & Pacific 8; Europe & Central Asia 40; Latin America & Caribbean 11; Middle East, North Africa, Afghanistan & Pakistan 7; North America 2; South Asia 1; Sub-Saharan Africa 6.
- Verified by region: East Asia & Pacific 6; Europe & Central Asia 15; Latin America & Caribbean 2; North America 2; South Asia 1; Sub-Saharan Africa 1.
- Assessable by income group: High income 47; Lower middle income 7; Upper middle income 21.
- Verified by income group: High income 20; Lower middle income 1; Upper middle income 6.

### Mathematics and computer science research-university ecosystem

- Assessable by region: East Asia & Pacific 8; Europe & Central Asia 40; Latin America & Caribbean 11; Middle East, North Africa, Afghanistan & Pakistan 7; North America 2; South Asia 1; Sub-Saharan Africa 6.
- Verified by region: East Asia & Pacific 6; Europe & Central Asia 17; Latin America & Caribbean 2; Middle East, North Africa, Afghanistan & Pakistan 1; North America 2; South Asia 1; Sub-Saharan Africa 1.
- Assessable by income group: High income 47; Lower middle income 7; Upper middle income 21.
- Verified by income group: High income 23; Lower middle income 1; Upper middle income 6.

### Biomedical and health sciences research-university ecosystem

- Assessable by region: East Asia & Pacific 8; Europe & Central Asia 40; Latin America & Caribbean 11; Middle East, North Africa, Afghanistan & Pakistan 7; North America 2; South Asia 1; Sub-Saharan Africa 6.
- Verified by region: East Asia & Pacific 6; Europe & Central Asia 16; Latin America & Caribbean 2; Middle East, North Africa, Afghanistan & Pakistan 1; North America 2; South Asia 1; Sub-Saharan Africa 2.
- Assessable by income group: High income 47; Lower middle income 7; Upper middle income 21.
- Verified by income group: High income 22; Lower middle income 2; Upper middle income 6.

### Life and earth sciences research-university ecosystem

- Assessable by region: East Asia & Pacific 8; Europe & Central Asia 40; Latin America & Caribbean 11; Middle East, North Africa, Afghanistan & Pakistan 7; North America 2; South Asia 1; Sub-Saharan Africa 6.
- Verified by region: East Asia & Pacific 5; Europe & Central Asia 18; Latin America & Caribbean 3; North America 2; South Asia 1; Sub-Saharan Africa 2.
- Assessable by income group: High income 47; Lower middle income 7; Upper middle income 21.
- Verified by income group: High income 22; Lower middle income 2; Upper middle income 7.

### Broad scientific research-university ecosystem

- Assessable by region: East Asia & Pacific 8; Europe & Central Asia 40; Latin America & Caribbean 11; Middle East, North Africa, Afghanistan & Pakistan 7; North America 2; South Asia 1; Sub-Saharan Africa 6.
- Verified by region: East Asia & Pacific 6; Europe & Central Asia 16; Latin America & Caribbean 2; North America 2; South Asia 1; Sub-Saharan Africa 2.
- Assessable by income group: High income 47; Lower middle income 7; Upper middle income 21.
- Verified by income group: High income 21; Lower middle income 2; Upper middle income 6.

The evidence spans every stable-universe region and multiple income groups among represented countries, but research-intensive inclusion structurally favors systems with sufficient publication scale. Exceptional/top-band routes help smaller systems when they contain prominent institutions. They cannot make countries absent from the release assessable. The report therefore keeps those countries insufficient rather than punishing small systems.

## Career–education comparison

The crosswalk compares ecosystem states without merging criteria or claiming that education supply causes labour-market opportunity.

| Career construct | Education construct | Relationship counts |
|---|---|---|
| science_engineering_opportunity | engineering_technology_education_opportunity | BOTH_STRONG: 14; CAREER_STRONG_EDUCATION_NOT_ESTABLISHED: 6; EDUCATION_STRONG_CAREER_NOT_ESTABLISHED: 8; NEITHER_STRONG_WITH_COMPLETE_EVIDENCE: 28; ONE_OR_BOTH_INSUFFICIENT: 35 |
| technology_software_opportunity | computer_science_ict_education_opportunity | BOTH_STRONG: 17; CAREER_STRONG_EDUCATION_NOT_ESTABLISHED: 3; EDUCATION_STRONG_CAREER_NOT_ESTABLISHED: 9; NEITHER_STRONG_WITH_COMPLETE_EVIDENCE: 26; ONE_OR_BOTH_INSUFFICIENT: 36 |
| health_social_work_opportunity | medicine_health_sciences_education_opportunity | BOTH_STRONG: 22; CAREER_STRONG_EDUCATION_NOT_ESTABLISHED: 5; EDUCATION_STRONG_CAREER_NOT_ESTABLISHED: 8; NEITHER_STRONG_WITH_COMPLETE_EVIDENCE: 38; ONE_OR_BOTH_INSUFFICIENT: 18 |

Life and earth sciences has no direct approved Phase 6B career pair and is left unpaired. Proposed shared taxonomy IDs are research notes only. Country-level combinations may help future explanation—for example, distinguishing a research ecosystem from an employment ecosystem—but cannot be interpreted as applicant outcomes.

## Final consolidated research portfolio

The consolidated portfolio contains the five career constructs approved in Phase 6B.1 plus four education research-ecosystem constructs approved here. Business/finance is held. Broad university excellence is rejected. The portfolio is a research/design recommendation only; no criterion, weight, preset, ranking, worker, schema, API, or UI change is authorised.

## Limitations and refresh policy

- Scientific publication output and prominence do not measure teaching, admissions, affordability, student support, institutional accreditation, recognition of a specific qualification, employment outcomes, or lived experience.
- The retained source selects research-intensive universities and may omit legitimate teaching-focused institutions and smaller systems.
- The official broad fields cannot isolate engineering, ICT, business, finance, medicine programmes, or all natural sciences exactly as phrased in the prompt.
- Country assignment is not campus-level accessibility; branch campuses, online programmes, language, visa, and geographic distance remain unresolved.
- A single 2025 release cannot establish temporal stability. Refresh annually only after pinning the new release, comparing coverage and taxonomy, rerunning every percentile, and reviewing state changes.
- A source/licence/access change must fail closed to insufficient rather than reuse stale or untraceable evidence.

## Deterministic artifacts and verification

The committed fixture freezes all 2,831 institution results for six official fields, 2,831 ROR mappings, 284 field-concept mappings, query parameters, source URLs, byte counts, and SHA-256 hashes. Ignored raw captures are verified when present; fixture-only replay remains possible. The generator enforces six × 91 = 546 unique outcomes, recognized states, unique institution identities, global threshold policy, benchmark-list non-interference, JSON/JSONL parseability, and stable output ordering. The replay manifest hashes every retained input and generated artifact. A second run must produce no diff.

The artifact commit SHA is supplied in the Git handoff because a commit cannot contain its own SHA.

## Owner decisions before implementation design

1. Accept that the public concept is a **research-university ecosystem**, not generic higher-education quality or applicant opportunity.
2. Accept all four official evidence-aligned names and reject broader shorthand in user-facing copy.
3. Accept P60 and the exceptional/top-band routes as the research baseline, subject to the recorded P50–P70 sensitivity.
4. Accept 75/91 assessability and the explicit insufficient state for countries absent from the research-intensive release.
5. Accept or require mitigation of the single-source and ROR-identity dependency.
6. Keep business/finance on hold and broad university excellence rejected.
7. Confirm that no production work begins until a separate implementation prompt and review.
