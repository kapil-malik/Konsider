# Phase 6C augmented research protocol

Date frozen: 2026-08-03
Status: research protocol only; no production or ranking change is authorised

## Purpose and precedence

The controlling brief is `Konsider Phase 6C Higher-Education Opportunity Criteria.pdf`. This document keeps its six candidate directions, evidence questions, 91-country universe, benchmark-list checks, implementation boundary, and required deliverables. It adds the methodological discipline introduced in Phase 6B.1: pre-registration, explicit source capability, asymmetric negatives, global threshold sensitivity, dependency tests, deterministic replay, and owner-facing dispositions.

If wording here conflicts with the Phase 6C PDF, the PDF controls unless this protocol explicitly narrows a claim to match what the retained evidence can support.

## Frozen research boundary

- Explore country-level higher-education opportunity signals for the 91-country stable universe.
- Do not alter schemas, workers, criteria, ranking, presets, APIs, UI, admissions logic, or releases.
- Do not imply applicant eligibility, admission probability, teaching quality, affordability, accreditation, qualification recognition, visa eligibility, campus safety, or graduate outcomes unless separately evidenced.
- Treat an institution's country as an ecosystem signal, not as an applicant-specific recommendation.
- Preserve the Phase 6C requirement for exactly one tri-state outcome per country and candidate, including held or rejected candidates.

## Pre-registered candidates

| Candidate ID | Intended exploration | Retained evidence route | Claim discipline |
|---|---|---|---|
| `engineering_technology_education_opportunity` | Engineering and technology | CWTS field `Physical sciences and engineering` | Must use the broader source-aligned name; cannot isolate engineering or technology alone. |
| `computer_science_ict_education_opportunity` | Computer science and ICT | CWTS field `Mathematics and computer science` | Must use the broader source-aligned name; cannot claim ICT programme availability. |
| `medicine_health_sciences_education_opportunity` | Medicine and health sciences | CWTS field `Biomedical and health sciences` | Research ecosystem only; no clinical-training or licence-recognition claim. |
| `business_finance_education_opportunity` | Business and finance | No sufficiently specific route retained | `Social sciences and humanities` is too broad; all country states remain insufficient. |
| `natural_sciences_education_opportunity` | Natural sciences | CWTS field `Life and earth sciences` | Must use the narrower source-aligned name; physical sciences are not included in this route. |
| `broad_university_excellence_opportunity` | Broad university excellence | CWTS `All sciences`, for diagnostic analysis only | Scientific performance is not generic university excellence; analyze but do not approve as a criterion. |

## Evidence source and construct limits

Primary source: CWTS Leiden Ranking Open Edition 2025, DOI `10.5281/zenodo.17473224`, based on an August 2025 OpenAlex snapshot. The retained release covers 2,831 universities from 120 countries and uses five broad fields. Result and underlying data are released under CC0; the source code is MIT licensed. The official university identity workbook supplies ROR IDs.

The source universe includes universities with at least 1,500 qualifying publications in 2020–2023. It therefore supports a research-intensive university ecosystem construct. Absence from the release does not mean a country has no universities, no programmes, or poor education.

The frozen field metric is fractional publication output `P`. Institution prominence uses within-field global ranks derived from the same frozen query and output metric. The supporting `P>=50` and `PP>=50` values are retained in the fixture for audit, but are not mixed into the country classification rule.

## Source capability and precedence

1. A complete, frozen, reusable field result plus canonical institution mapping may establish either a positive or a negative within the narrow research-ecosystem construct.
2. A complete result without a canonical institution mapping may establish neither state for publication.
3. A partial, ambiguous, broader, or supplemental source may support context or a positive only when the match is defensible; it cannot establish a negative.
4. Source absence, publisher redaction, taxonomy mismatch, or missing country coverage produces `INSUFFICIENT_EVIDENCE`, never a synthetic zero.
5. Conflicting evidence is preserved for review; lower-precedence evidence never silently overwrites higher-precedence evidence.

The UNESCO UIS Observatory of Public Research and Innovation remains a possible specialization supplement, but its current ShareAlike/legal and coverage route is not used for the primary country signal. Direct current OpenAlex API acquisition is not required because the CWTS release pins the snapshot and publishes reusable results; a future direct route would need its own access, freeze, and replay review.

## Institution and country identity

- Map every retained source institution to its official ROR ID from the CWTS workbook.
- Prefer exact source-name and country matches. Record the six deterministic manual disambiguations caused by quoted-name truncation in the HTML tooltip.
- Record source internal ID, source name, canonical institution name, ROR ID/URL, country, match method, and confidence.
- No locality or campus coordinates are inferred. Multi-campus and applicant-access implications remain unknown.
- Map source country names to the 91-country universe using explicit aliases and ISO alpha-3 codes. Countries outside the stable universe are ignored for product coverage but remain part of global institution ranks.

## Global classification rule

For each source-supported candidate and each represented stable country, calculate:

- fractional field publication output across retained universities;
- active-university breadth, defined as non-redacted universities with field `P > 0`;
- counts of universities in the field's global top 100, top 200, and top 300.

For a sensitivity percentile `p`, calculate global thresholds over represented stable countries:

- base output and breadth at `Pp`;
- high output and breadth at `P(p+20)`;
- low output and breadth at `P(p-20)`.

A represented country is `VERIFIED_STRONG_SIGNAL` if at least one route passes:

1. exceptional institution route: at least one global top-100 institution; or
2. prominent breadth route: at least three global top-300 institutions; or
3. scale/breadth route: `(output >= base AND breadth >= base) OR (output >= high AND breadth >= low) OR (breadth >= high AND output >= low)`.

Otherwise, complete evidence produces `STRONG_SIGNAL_NOT_ESTABLISHED`. A country not represented in the complete university release produces `INSUFFICIENT_EVIDENCE`. Business/finance is insufficient for every country because the retained field taxonomy cannot support the construct. No country-specific threshold is allowed.

The primary diagnostic uses P60. Recalculate P50, P55, P60, P65, and P70. Also report top-100/top-200/top-300 band counts, removal of the primary result source, and removal of canonical identity mapping. Do not manufacture a time trend from the single retained 2025 release.

## Candidate gates and dispositions

Before an education candidate can be recommended for implementation design, it must:

- have at least 60/91 assessable countries;
- preferably cover at least 16/20 countries in each frozen Phase 6B benchmark list when joined after list generation;
- retain geographic and income-group breadth;
- have at least eight countries in the smaller P60 assessed outcome class;
- use a reusable, attributable, frozen source route;
- pass deterministic replay and outcome-cardinality checks;
- have public naming no broader than the actual evidence.

Allowed dispositions are `APPROVE_FOR_IMPLEMENTATION_DESIGN`, `APPROVE_WITH_NAMING_OR_SCOPE_CHANGE`, `RESEARCH_SHORTLIST_ONLY`, `HOLD_SOURCE_GAP`, and `REJECT_AS_OPPORTUNITY_CRITERION`.

## Career–education crosswalk

Compare, but do not merge, these constructs:

- science/engineering employment ecosystem ↔ physical sciences and engineering research-university ecosystem;
- technology/software employment ecosystem ↔ mathematics and computer science research-university ecosystem;
- care-sector employment ecosystem ↔ biomedical and health sciences research-university ecosystem;
- life and earth sciences research-university ecosystem ↔ no direct approved Phase 6B employment construct.

Report both-strong, education-only strong, career-only strong, and insufficient combinations. These are ecosystem relationships, not causal claims. Propose future shared taxonomy IDs only; do not implement them.

## Reproducibility and acceptance checks

- Commit a compact source fixture with source URLs, query policy, captured-file byte counts, and SHA-256 hashes.
- If ignored raw captures are present, verify them before generation. Fixture-only replay remains possible from the committed source fixture.
- Generate all JSON and JSONL deterministically with stable ordering and newline policy.
- Produce exactly 546 country outcomes: six candidates × 91 countries, unique on `(candidate_id, country_code)`.
- Produce one institution-mapping row per source university and verify all 2,831 ROR mappings.
- Generate a manifest with input and output hashes, outcome counts, coverage assertions, and replay mode.
- Run a second generation and require a no-diff replay.

## Owner decisions after research

The study must stop after research and request explicit owner decisions on public names, implementation scope, the research-university boundary, hard versus preferred shortlist floors, single-source dependency, and the exclusion of held/rejected candidates. A research disposition never authorises production work.
