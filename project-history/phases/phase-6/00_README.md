# Konsider Phase 6 Prompt Pack

## Phase title

**Phase 6 — Career and Engineering-Education Opportunity**

## Why this phase exists

Phase 5 proved that Konsider can publish national or locality-derived criteria independently of whether they are full-coverage or partial-coverage. The next useful step is not another general architecture rewrite. It is to use that foundation to add a coherent group of career and education criteria.

The present active product already has broad national criteria for the overall job market, school education, and research and innovation. It does not yet answer:

- whether a destination has a substantial technology employment market;
- whether it has a substantial engineering employment market;
- whether it produces meaningful engineering higher-education capacity; or
- where its engineering academic and research clusters are located.

Phase 6 should answer those four questions without pretending to calculate an individual applicant's probability of getting a job or university admission.

## Required Phase 6 outcome

Phase 6 should end with **at least four new public, weightable criteria**, unless a critical blocker is demonstrated with evidence.

### Core target criteria

1. **Technology employment-market depth**
   - Intended Phase 3 lineage: narrowed, profile-neutral form of C12.
   - Expected scope: national.
   - Expected coverage: PCC unless the evidence proves FCC.
   - Meaning: scale and depth of internationally comparable ICT occupations.
   - Not personal job probability and not a live-vacancy count.

2. **Engineering employment-market depth**
   - Intended Phase 3 lineage: narrowed, profile-neutral form of C15.
   - Expected scope: national.
   - Expected coverage: PCC unless the evidence proves FCC.
   - Meaning: scale and depth of engineering or science-and-engineering occupations at the finest defensible internationally comparable level.
   - Do not call a two-digit science-and-engineering aggregate "pure engineering" if the source cannot isolate engineering.

3. **Engineering higher-education capacity**
   - Intended Phase 3 lineage: narrowed production component of C01.
   - Expected scope: national.
   - Expected coverage: FCC or PCC based on evidence.
   - Meaning: scale and specialization of tertiary engineering education.
   - Not admission probability, tuition affordability, accreditation, or teaching quality.

4. **Engineering academic and research ecosystem**
   - Intended lineage: field-specific extension related to C05 and C01.
   - Expected scope: institution/locality-derived country result.
   - Expected coverage: PCC unless evidence proves FCC.
   - Meaning: strength and concentration of engineering-active academic and research institutions, with contributing localities.
   - Must demonstrate useful distinction from the existing broad national Research and innovation ecosystem criterion.

### Stretch criteria

Phase 6 must probe these at the same time. If they reuse the approved source and taxonomy with limited incremental work and clear constructs, onboard them in the same phase rather than deferring them artificially:

5. **Healthcare employment-market depth** — narrowed profile-neutral form of C13.
6. **Business and finance employment-market depth** — narrowed profile-neutral form of C14.
7. **ICT higher-education capacity** — another field-specific component of C01.

The core target remains the four criteria listed first. Stretch criteria may substitute only when a core criterion has a documented critical blocker; substitution must be explicit in the phase report.

## What counts as a critical blocker

A criterion may be held only when at least one of these is demonstrated:

- exact source asset cannot be reproduced;
- production reuse or redistribution rights are unclear or incompatible;
- valid country coverage fails the approved Konsider publication policy;
- the source cannot isolate the stated construct and a truthful narrower name is not useful;
- the score is saturated, unstable, non-discriminating, or dominated by data artefacts;
- the criterion materially duplicates an existing public criterion;
- locality or institution mapping cannot be made deterministic and auditable;
- the result would imply applicant accessibility when only market or ecosystem evidence exists;
- deterministic replay cannot be achieved.

The following are not sufficient blockers by themselves:

- the criterion is not perfect;
- it is PCC rather than FCC;
- it is national rather than locality-specific;
- personal context could refine it later;
- the source requires a new parser;
- the source is large but a reproducible filtered capture is feasible.

## Phase 6 philosophy

### Be honest

Separate three questions:

1. **Does the opportunity ecosystem exist?**
2. **Where does it exist?**
3. **Can this particular applicant access it?**

Phase 6 answers the first two where evidence permits. A future applicant/context phase answers the third.

### Be simple

Do not build a generic ontology platform. Add only shared abstractions that are used by at least two approved criteria or that are necessary for deterministic evidence.

### Be efficient

Research all core and stretch criteria as one portfolio. Build shared source adapters and taxonomies once. Publish criteria in coherent waves rather than one criterion per mini-phase.

### Preserve existing guarantees

Do not weaken:

- the 91-country stable universe;
- explicit country outcomes;
- no-imputation rules;
- complete-case ranking;
- PCC activation and coverage-limit policy;
- locality provenance;
- immutable releases;
- source licensing gates;
- deterministic replay;
- API-owned business logic;
- structured coverage/locality/profile assessments.

## Current repository baseline to verify before starting

Inspect, do not assume:

- `docs/history/phase5-closure-report.md`
- `docs/product/roadmap.md`
- `docs/research/phase5a-locality-criteria-discovery.md`
- the Phase 3 closure and criterion research records;
- active release and release-scoped catalog;
- current taxonomy, coverage, scope, applicability, lineage, and locality schemas;
- current preference presets;
- current CI status and branch state.

The Phase 5 closure recorded release schema 5, catalog 3, API v2, 91 countries, 388 urban centres, 13 enabled criteria, two locality-derived criteria, and a `NO_PROFILE_CONTEXT` profile assessment. Treat the current repository as authoritative if it has moved forward.

## Candidate source families to verify

Do not rely on these names alone. Freeze exact assets, indicator IDs, versions, terms, and reference periods.

### Occupation evidence

- ILOSTAT bulk data and official ISCO classifications.
- Starting point: annual employment by occupation at the finest internationally comparable level with adequate coverage.
- Official starting pages:
  - https://ilostat.ilo.org/data/
  - https://ilostat.ilo.org/data/bulk/
  - https://ilostat.ilo.org/methods/concepts-and-definitions/classification-occupation/

### Education capacity evidence

- UNESCO Institute for Statistics Data Browser API and bulk downloads.
- Starting point: tertiary graduates and/or enrolment by ISCED field of education.
- Official starting pages:
  - https://databrowser.uis.unesco.org/
  - https://databrowser.uis.unesco.org/resources
  - https://databrowser.uis.unesco.org/resources/bulk
  - https://databrowser.uis.unesco.org/glossary

### Academic ecosystem evidence

- OpenAlex filtered reproducible capture or pinned snapshot.
- ROR frozen release for canonical institution identity and location.
- Official starting pages:
  - https://developers.openalex.org/
  - https://developers.openalex.org/download/overview
  - https://help.openalex.org/hc/en-us/articles/24397762024087-Pricing
  - https://ror.readme.io/docs/data-dump

## Execution order

Use the prompts in this order:

1. `01_PHASE_6A_PORTFOLIO_AND_SOURCE_GATES.md`
2. `02_PHASE_6B_SHARED_TAXONOMY_AND_EVIDENCE_FOUNDATION.md`
3. `03_PHASE_6C_OCCUPATION_MARKET_WAVE.md`
4. `04_PHASE_6D_ENGINEERING_EDUCATION_WAVE.md`
5. `05_PHASE_6E_PORTFOLIO_INTEGRATION_AND_PRODUCT_VALIDATION.md`
6. `06_PHASE_6F_NEXT_UNLOCK_AND_CONTEXT_BOUNDARY.md`
7. `07_PHASE_6G_FINAL_VERIFICATION_AND_CLOSURE.md`

Do not give all prompts to Codex at once. Run one prompt, review its findings and commit, then proceed.

## Expected commit pattern

Use multiple reviewable commits. A reasonable minimum sequence is:

1. Phase 6A research and decisions.
2. Phase 6B shared taxonomy/evidence foundation.
3. Phase 6C occupation-market implementation.
4. Phase 6C career-wave immutable release.
5. Phase 6D education evidence implementation.
6. Phase 6D education-wave immutable release.
7. Phase 6E product integration and portfolio validation.
8. Phase 6F next-unlock/context boundary documentation.
9. Phase 6G defect fixes, if any, in focused commits.
10. Phase 6G closure documentation.

Do not collapse Phase 6 into one monolithic commit.

## Global rules for every prompt

- Start from latest `main` and inspect the working tree.
- Read prior phase outputs before coding.
- Do not change historical release bytes.
- Do not add synthetic values to production releases.
- Do not lower coverage thresholds to force publication.
- Do not label employment stock as live job vacancies.
- Do not label education capacity as admission accessibility.
- Do not label research output as teaching quality.
- Do not infer applicant fit without applicant context.
- Keep every source, transform, mapping, score, and release reproducible.
- Keep exact unavailable outcomes explicit.
- Update documentation with behavior.
- Stop after each phase and report:
  - decisions;
  - files changed;
  - tests run;
  - commit SHA;
  - blockers;
  - what must be approved before the next prompt.
