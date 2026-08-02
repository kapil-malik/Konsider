# Phase 6B career-opportunity source study

Date: 2026-08-02

Status: research complete; implementation deliberately not started

Authoritative prompt: `project-history/phases/phase-6/Konsider Phase 6B Career Opportunity Criteria.pdf`

## Executive decision

The study approves three transparent, non-ranking employment-ecosystem criteria for implementation design, holds three candidates on source coverage, and approves no runtime change. “Approved” here means the construct, evidence route, tri-state semantics and frozen study threshold are sufficiently defined for a later owner decision; it does not authorize schema, worker, ranking, API, release, preset or UI work.

Approved portfolio:

- **Health and social-work employment ecosystem** — `APPROVE_WITH_NAMING_OR_SCOPE_CHANGE`; ISIC Rev.4 section Q cannot be labelled healthcare alone.
- **Finance and insurance employment ecosystem** — `APPROVE_WITH_NAMING_OR_SCOPE_CHANGE`; ISIC section K cannot represent all business and administration careers.
- **Skilled-trades or construction employment ecosystem** — `APPROVE_FOR_IMPLEMENTATION_DESIGN`; either the major-group-7 occupation route or section-F construction route may establish a positive signal.

Held:

- Technology/software and science/engineering have exact observed occupation constructs and clear the 60-country hard floor, but only 15/20 countries are assessable in four benchmark lists. Canada, Japan, Korea, Malta and New Zealand are material gaps.
- Research/academia has only 54 fresh, field-relevant M72 employment rows and the measure is business R&D rather than academia. Research output or institution counts may support a positive case but cannot safely establish a negative opportunity state.

## Semantics and frozen decision rule

This phase defines a filter, never a ranking input:

- `VERIFIED_STRONG_SIGNAL`: at least one reproducible route crosses a frozen strong-ecosystem threshold.
- `STRONG_SIGNAL_NOT_ESTABLISHED`: comparable evidence had a reasonable opportunity to detect the signal, but no route crosses it. This does **not** mean there are no jobs.
- `INSUFFICIENT_EVIDENCE`: missing, stale, incomplete, incomparable or construct-mismatched evidence. It is never a negative conclusion.

For each single employment route the base rule is: (scale ≥ P60 and share ≥ P60), or (scale ≥ P80 and share ≥ P40), or (share ≥ P80 and scale ≥ P40). Percentiles are converted to frozen raw thresholds in the artifacts. This avoids an opaque score, admits either exceptional scale or specialization only with a minimum on the other dimension, and keeps the positive/negative evidence asymmetry explicit. P50 and P70 variants are sensitivity tests, not alternative policy defaults.

Modelled ILO estimates are treated as medium-confidence comparable evidence. ILO describes the series as a balanced internationally comparable panel combining nationally reported and imputed observations and cautions that estimates for countries with limited information have higher uncertainty. Antigua and Barbuda, Grenada and Ukraine are absent from the November 2025 modelled captures and therefore remain `INSUFFICIENT_EVIDENCE`.

## Candidate results

| Candidate | Strong | Not established | Insufficient | Decision |
|---|---:|---:|---:|---|
| Technology and software employment ecosystem | 19 | 42 | 30 | HOLD_SOURCE_GAP |
| Science and engineering employment ecosystem | 20 | 46 | 25 | HOLD_SOURCE_GAP |
| Health and social-work employment ecosystem | 27 | 61 | 3 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Finance and insurance employment ecosystem | 22 | 66 | 3 | APPROVE_WITH_NAMING_OR_SCOPE_CHANGE |
| Research and academia opportunity | 16 | 38 | 37 | HOLD_SOURCE_GAP |
| Skilled-trades or construction employment ecosystem | 34 | 54 | 3 | APPROVE_FOR_IMPLEMENTATION_DESIGN |

The smaller assessed state class is at least eight for every approved candidate at the base threshold. No approved candidate is a near-universal toggle.

## Benchmark shortlist coverage

The five lists are regenerated solely from current release 2026-07-29.2 criteria and the existing complete-case ranking rules. Opportunity evidence is not used to create or reorder a list.

| Candidate | Profile | Assessable | Strong | Preferred ≥16/20 |
|---|---|---:|---:|---|
| Technology and software employment ecosystem | general_balanced | 15/20 | 10 | fail |
| Technology and software employment ecosystem | affordability_sensitive | 15/20 | 7 | fail |
| Technology and software employment ecosystem | safety_governance_oriented | 15/20 | 9 | fail |
| Technology and software employment ecosystem | career_prioritised | 15/20 | 9 | fail |
| Technology and software employment ecosystem | family_education_oriented | 17/20 | 12 | pass |
| Science and engineering employment ecosystem | general_balanced | 15/20 | 10 | fail |
| Science and engineering employment ecosystem | affordability_sensitive | 15/20 | 8 | fail |
| Science and engineering employment ecosystem | safety_governance_oriented | 15/20 | 9 | fail |
| Science and engineering employment ecosystem | career_prioritised | 15/20 | 9 | fail |
| Science and engineering employment ecosystem | family_education_oriented | 17/20 | 10 | pass |
| Health and social-work employment ecosystem | general_balanced | 20/20 | 15 | pass |
| Health and social-work employment ecosystem | affordability_sensitive | 20/20 | 11 | pass |
| Health and social-work employment ecosystem | safety_governance_oriented | 20/20 | 14 | pass |
| Health and social-work employment ecosystem | career_prioritised | 20/20 | 13 | pass |
| Health and social-work employment ecosystem | family_education_oriented | 20/20 | 16 | pass |
| Finance and insurance employment ecosystem | general_balanced | 20/20 | 11 | pass |
| Finance and insurance employment ecosystem | affordability_sensitive | 20/20 | 10 | pass |
| Finance and insurance employment ecosystem | safety_governance_oriented | 20/20 | 10 | pass |
| Finance and insurance employment ecosystem | career_prioritised | 20/20 | 11 | pass |
| Finance and insurance employment ecosystem | family_education_oriented | 20/20 | 10 | pass |
| Research and academia opportunity | general_balanced | 16/20 | 9 | pass |
| Research and academia opportunity | affordability_sensitive | 16/20 | 7 | pass |
| Research and academia opportunity | safety_governance_oriented | 16/20 | 9 | pass |
| Research and academia opportunity | career_prioritised | 16/20 | 8 | pass |
| Research and academia opportunity | family_education_oriented | 18/20 | 11 | pass |
| Skilled-trades or construction employment ecosystem | general_balanced | 20/20 | 4 | pass |
| Skilled-trades or construction employment ecosystem | affordability_sensitive | 20/20 | 6 | pass |
| Skilled-trades or construction employment ecosystem | safety_governance_oriented | 20/20 | 5 | pass |
| Skilled-trades or construction employment ecosystem | career_prioritised | 20/20 | 5 | pass |
| Skilled-trades or construction employment ecosystem | family_education_oriented | 20/20 | 5 | pass |

All three approved candidates are assessable for 20/20 countries in every benchmark list. The exact technology and science/engineering routes reach 17/20 only for the family/education list and 15/20 for each other list.

## Geographic, economic and source-dependency findings

The 88-country modelled routes span every stable-universe region and every World Bank income group represented in the universe. The three absent countries are distributed across Latin America/Caribbean and Europe/Central Asia, so they are explicit evidence gaps rather than inferred negatives. Detailed region and income-state counts are retained in `career-candidate-matrix.json`.

The approved portfolio has a material single-publisher dependency: removing the ILO modelled-estimate family turns every approved assessment into insufficient evidence. That is acceptable for this implementation-design approval only because the source is authoritative, exact captures and hashes are frozen, reuse is compatible, and the state is non-ranking. An implementation owner should decide whether medium-confidence modelled country estimates are acceptable before any product work.

## Source findings

- **ilo_observed_occupation_oc2** — USABLE_EXACT_ROUTE_WITH_COVERAGE_GAP. 61 fresh technology rows; 66 fresh science/engineering rows in the 91-country universe.
- **ilo_modelled_occupation_2025** — USABLE_WITH_MODELLED_CONFIDENCE_CAVEAT. 88 of 91 stable countries; Antigua and Barbuda, Grenada and Ukraine absent.
- **ilo_modelled_economic_activity_2025** — USABLE_WITH_SCOPE_AND_MODELLED_CONFIDENCE_CAVEATS. 88 of 91 stable countries; the same three absences as the occupation model.
- **ilo_observed_economic_activity_isic2** — SUPPORTING_ONLY_SOURCE_GAP. No tested detailed family reaches the 60-country hard floor; fresh M72 research employment reaches 54.
- **eurostat_job_vacancy_statistics** — SUPPLEMENTAL_ONLY_GEOGRAPHIC_GAP. European regional scope; cannot satisfy geographic breadth for the 91-country universe.
- **cedefop_skills_ovate** — SUPPLEMENTAL_ONLY_GEOGRAPHIC_AND_REPRESENTATION_GAP. EU, EFTA and United Kingdom only.
- **national_labour_force_and_shortage_sources** — NOT_USED_UNTIL_CROSSWALKS_AND_REPLAY_ARE_FROZEN. Prominent-country positives may be recoverable, but taxonomies, reference periods and machine interfaces are not yet normalized.
- **major_employer_ecosystem_route** — REJECTED_FOR_CURRENT_STUDY. No authoritative, harmonized, reproducible 91-country source with employment counts and acceptable reuse was found.
- **world_bank_country_metadata** — ANALYSIS_ONLY. Income-group breadth diagnostic only; never used to classify opportunity.

Current-demand evidence remains supplemental. Eurostat job-vacancy statistics are authoritative but geographically regional and occupational breakdown is voluntary/experimental. Cedefop Skills OVATE is valuable near-real-time European evidence but online-ad representation and geographic scope prevent a 91-country negative state. No qualifying harmonized major-employer dataset was found; office locations, search counts and crowdsourced lists are excluded.

## Legal, replay and quality gates

- ILO source use: pass under the publisher's CC BY 4.0 default, with attribution and source-specific notices retained.
- Exact captures: pass; SHA-256 checks are frozen in `replay-manifest.json` and rechecked by the replay script.
- World Bank metadata: analysis-only income grouping; it never changes a country state.
- Construct validity: pass only for the final names shown above. Broader labels are not approved.
- Shortlist gate: pass for the three approved candidates; material failure for technology/software and science/engineering.
- Discrimination: pass at P60; see P50/P70 state flips in `career-threshold-sensitivity.json`.
- Runtime boundary: pass; no production catalog, schema, worker, ranking, API, release, preset or UI artifact changed.

Raw capture checksums used in this run:

- `ilo_observed_occupation`: `aaadd9ad52c88af5b00edce9c78821481d352251fe1ee944bb9bff299bdd04d4`
- `ilo_modelled_occupation`: `00c76b161f5308f6655bac28ac3b6edeca25f4d262fc694e1aec5c310ef89986`
- `ilo_modelled_economy`: `ab1baf83fb7f3cd3646df98b129571c21651e65fe49237efc873bff7e832efef`
- `ilo_observed_economy`: `f66ac2ba0364f70a2ed1709d99d7e2c5786819fae703247f8cb3642e7895aa96`
- `world_bank_metadata`: `d29d57f8adf954c5e2a1520a02fb2c7b45575d8db3bd327a9dff47d66914231c`

## Files and verification

- `data/reports/phase6b-2026-08-02/career-candidate-matrix.json`
- `data/reports/phase6b-2026-08-02/career-country-opportunity-evidence.jsonl`
- `data/reports/phase6b-2026-08-02/career-source-matrix.json`
- `data/reports/phase6b-2026-08-02/career-shortlist-coverage.json`
- `data/reports/phase6b-2026-08-02/career-threshold-sensitivity.json`
- `data/reports/phase6b-2026-08-02/approved-career-opportunity-portfolio.json`
- `data/reports/phase6b-2026-08-02/replay-manifest.json`
- `project-history/phases/phase-6/research/run_phase6b_opportunity_probe.mjs`

The replay verifies input hashes, reconstructs 546 country-candidate rows (91 × 6), requires exactly one state per row, checks the hard coverage and shortlist counts, and writes deterministic artifacts. The introducing Git commit is intentionally reported in the task handoff rather than embedded here because a commit cannot contain its own final hash.

## Owner decisions required before implementation

1. Accept or reject medium-confidence ILO modelled country estimates for a non-ranking filter.
2. Accept the exact public names and the OR semantics for skilled trades/construction.
3. Choose whether held technology/science criteria should wait for frozen national crosswalks or proceed later with the documented prominent-country gaps.
4. Decide whether an independent second-source requirement is mandatory despite the current single-publisher dependency.

Phase 6B stops here. No implementation phase is started.
