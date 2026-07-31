---

# FILE: 00_README.md

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


---

# FILE: 01_PHASE_6A_PORTFOLIO_AND_SOURCE_GATES.md

# Phase 6A Prompt — Portfolio Definition and Exact Source Gates

## Role

Work as the lead data/product engineer for the Konsider repository.

## Objective

Research the complete Phase 6 career-and-education portfolio as one coordinated exercise. Freeze truthful constructs, exact source candidates, legal/reuse conclusions, coverage estimates, and production recommendations before implementing runtime changes.

Do not add public criteria or modify the active release in this phase.

## Required target portfolio

Evaluate all seven candidates together:

### Core

1. Technology employment-market depth.
2. Engineering employment-market depth.
3. Engineering higher-education capacity.
4. Engineering academic and research ecosystem.

### Stretch

5. Healthcare employment-market depth.
6. Business and finance employment-market depth.
7. ICT higher-education capacity.

The goal is to approve at least four candidates for implementation. Prefer approving more where the same evidence supports them honestly.

## Repository orientation

Read at minimum:

- `docs/history/phase5-closure-report.md`
- `docs/product/roadmap.md`
- `docs/research/phase5a-locality-criteria-discovery.md`
- `docs/research/phase3-closure-report.md`
- retained Phase 3 records for C01, C05, C06, C11-C17, C35, and C38;
- active release report;
- current source registry;
- current criterion catalog;
- coverage policy;
- scope/applicability contracts;
- locality-universe and aggregation policies;
- current preference presets.

Locate exact current paths rather than relying on historical paths.

## Correct the product framing

Phase 5 classified occupation-specific and institution-specific questions as profile-dependent because personal accessibility requires qualifications, licensing, admissions, language, household, and visa context.

Phase 6 must preserve that warning while testing narrower profile-neutral constructs:

- destination employment-market depth;
- destination education capacity;
- destination academic ecosystem.

Do not research “likelihood that Kapil gets a job” or “likelihood that a student gets admission.” Research objective destination opportunity evidence.

## Workstream A — occupation data probe

### Source candidates

Start with official ILOSTAT bulk data and ISCO documentation. Identify the exact downloadable indicator/table, not merely the website.

Test:

- annual employment by occupation;
- the finest occupation-code level available with acceptable coverage;
- both-sex totals;
- current and recent reference years;
- observed versus modelled values;
- breaks in classification;
- national source comparability;
- whether total employment denominators are available from the same compatible source.

### Candidate occupation families

Do not freeze these mappings until the source granularity is proven.

#### Technology

Preferred concept:

- ICT professionals;
- ICT technicians;
- other codes only if their inclusion is explicit and defensible.

At ISCO-08 two-digit level, likely starting groups are 25 and 35. Verify exact source categories and definitions.

#### Engineering

Prefer engineering-specific three-digit groups if coverage supports them.

If only broad two-digit groups such as 21 and 31 are available, decide whether the truthful criterion must be named:

- `Science and engineering employment-market depth`

rather than:

- `Engineering employment-market depth`.

Do not hide natural-science occupations under an engineering label.

#### Healthcare stretch

Likely broad groups include health professionals and health associate professionals. Verify exact categories.

#### Business and finance stretch

Define a narrow reproducible family. Avoid an arbitrary mixture of management, legal, sales, clerical, marketing, and finance occupations.

A plausible starting family is business and administration professionals and associate professionals, but exact codes and names must be frozen.

### Candidate measures

Evaluate at least:

1. occupation-family share of total employment;
2. occupation-family employment per working-age population or labour force;
3. absolute employment scale with a defensible size adjustment;
4. recent direction/trend where a comparable series exists.

Prefer a simple score with understandable meaning.

Do not use current employee count alone because it mechanically rewards large countries. Do not use share alone if it makes tiny markets appear equivalent to large ecosystems. Evaluate a transparent blend of depth and specialization only if both components materially improve the construct.

### Coverage report

For each candidate family report:

- countries with any data;
- countries with acceptable recent data;
- exact latest year per country;
- classification version;
- observed/modelled/estimated flags;
- missing/stale/invalid/rejected countries;
- country coverage against the stable 91;
- combined missing-country unions with all currently active PCCs;
- expected FCC/PCC/diagnostic status.

Do not assume the same countries are available for each occupation family.

## Workstream B — education-capacity probe

### Source candidates

Start with UIS official API/bulk data.

Find exact indicators and dimensions for:

- tertiary graduates by field of education;
- tertiary enrolment by field of education;
- total tertiary graduates/enrolment denominators;
- engineering, manufacturing and construction;
- information and communication technologies;
- ISCED level and sex dimensions where relevant;
- current and archived data availability.

Freeze exact indicator IDs, files, metadata, units, update date, licence, and attribution.

### Candidate constructs

For Engineering higher-education capacity, evaluate:

1. engineering graduates per relevant population;
2. engineering graduates as share of tertiary graduates;
3. engineering enrolment per relevant population;
4. engineering enrolment share;
5. a simple two-component blend of absolute capacity and specialization.

Avoid treating graduate share alone as capacity. A country can have a high share but very few graduates.

Avoid a complex composite if one or two measures clearly tell the story.

For ICT higher-education capacity, repeat the same analysis as a stretch candidate.

### Coverage report

For each education candidate report:

- valid countries;
- latest reference year per country;
- age/level/field consistency;
- missing/stale/invalid/rejected outcomes;
- whether counts and shares can be reconstructed from compatible observations;
- country coverage against 91;
- expected FCC/PCC/diagnostic status;
- combined PCC missing-union implications.

## Workstream C — engineering academic ecosystem probe

### Source candidates

Use official OpenAlex and ROR only unless a clearly better open global source is found.

Determine a reproducible acquisition approach:

- pinned full snapshot;
- official filtered download;
- deterministic paginated API capture with frozen query, response hashes, and capture timestamp.

Do not use live API results at ranking time.

### Institution identity

Freeze:

- ROR release;
- OpenAlex institution snapshot/capture;
- mapping between OpenAlex institution IDs and ROR IDs;
- institution country;
- institution coordinates;
- mapping to the current Konsider locality universe;
- handling of multi-campus institutions;
- handling of missing or conflicting coordinates;
- unmapped institutions.

No fuzzy institution-to-locality mapping may silently publish.

### Field definition

Define “engineering” using a frozen OpenAlex field/topic mapping.

Report:

- selected topics/fields;
- excluded adjacent fields;
- taxonomy version;
- sensitivity to alternative field mappings.

Do not assume the current OpenAlex taxonomy is immutable.

### Time window and metric

Evaluate a recent multi-year window, for example five years, to reduce annual noise.

Test simple, interpretable institution/locality measures such as:

- field-specific scholarly output;
- fractional output by institution;
- citation-normalized impact;
- number of active engineering institutions;
- combination of scale and breadth.

Avoid ranking by raw citations alone.

### Relation to existing C05

Quantify correlation and conceptual overlap with the current national Research and innovation ecosystem criterion.

The new criterion must add field specificity and locality/institution evidence. If it is merely a noisy duplicate, do not publish it under a different name.

### Operational feasibility

Report:

- expected raw/download size;
- filtered capture size;
- local disk and run-time requirements;
- update/replay workflow;
- clean-checkout behavior where raw bytes are not committed;
- licensing and redistribution.

## Legal and source gate

For every exact asset record:

- publisher;
- distributor;
- asset/API/file;
- version;
- URL;
- access date;
- licence;
- commercial use;
- redistribution;
- attribution;
- third-party component restrictions;
- raw-byte retention plan;
- whether normalized derived release data can be committed.

Do not infer licence rights from the publisher's general reputation.

## Criterion decision matrix

Create one row per seven candidates with:

- proposed public ID;
- display name;
- Phase 3 lineage;
- exact construct;
- what it does not mean;
- scope;
- source;
- taxonomy;
- metric;
- scoring idea;
- reference period;
- valid-country estimate;
- expected coverage mode;
- correlation risks;
- licensing conclusion;
- replay feasibility;
- implementation effort;
- decision:
  - `APPROVE_CORE`
  - `APPROVE_STRETCH`
  - `APPROVE_RENAMED`
  - `DIAGNOSTIC_ONLY`
  - `HOLD_CRITICAL_BLOCKER`
  - `REJECT_CONSTRUCT`
- precise blocker or approval conditions.

## Portfolio decision rules

1. Approve the four core criteria when their exact constructs clear the gates.
2. If a core criterion is blocked, approve a stretch replacement only when it independently clears all gates.
3. If healthcare, business/finance, or ICT education reuse the same approved evidence with limited extra work, include them in Phase 6.
4. Do not lower the PCC coverage minimum or hard union limit.
5. Do not activate all new PCCs in default presets without testing their combined missing union.
6. Do not continue to implementation unless at least four candidates are approved or the report proves why that is impossible.

## Required outputs

Create:

- `docs/research/phase6a-career-education-source-study.md`
- a machine-readable decision matrix under `data/reports/phase6a-<date>/`
- exact coverage extracts/reports;
- source/legal evidence;
- proposed occupation and education mappings;
- proposed research-field mapping;
- proposed score candidates and sensitivity results;
- a short approved implementation portfolio;
- an update to `docs/product/roadmap.md` marking Phase 6 as in progress and placing structured applicant/context work after it.

Do not change active runtime behavior.

## Tests and verification

- Re-run every probe offline from retained captures.
- Confirm all 91 stable countries are explicitly classified for every proposed criterion.
- Confirm exact source versions and checksums.
- Confirm no candidate is called “job availability” when it only measures employment stock.
- Confirm no education criterion implies admissions or accreditation.
- Confirm approved criteria have meaningful score dispersion.

## Commit

Commit only the research and roadmap changes.

Suggested commit:

`docs: define Phase 6 career and education portfolio`

Stop and present:

- approved core criteria;
- approved stretch criteria;
- blocked criteria;
- exact source and coverage conclusions;
- critical decisions requiring owner approval.


---

# FILE: 02_PHASE_6B_SHARED_TAXONOMY_AND_EVIDENCE_FOUNDATION.md

# Phase 6B Prompt — Minimum Shared Taxonomy and Evidence Foundation

## Dependency

Proceed only after Phase 6A approves at least four criteria and the owner accepts the exact constructs and names.

## Objective

Implement the smallest shared foundation required to produce the approved career and education criteria reproducibly.

Do not build a generic ontology platform. Every abstraction added must be used by at least two approved criteria or be required for source lineage and replay.

Do not publish a new active release yet.

## Required design principles

### One taxonomy, two uses

The taxonomy IDs introduced here must be suitable for:

1. current destination-level criteria; and
2. future typed applicant/context inputs.

Example:

- a current criterion can bind to `occupation_family_id = technology`;
- a future applicant can declare `occupation_family_id = technology`.

This creates compatibility without implementing applicant scoring now.

### Taxonomy is not a score

Taxonomy files define membership and meaning. They must not contain hidden ranking weights unless those weights belong to a separately versioned criterion policy.

### Evidence remains source-specific

Do not force ILO, UIS, OpenAlex, and ROR records into one vague universal record if that loses semantics. Reuse the current Phase 5 entity-neutral observation/score foundation where appropriate, while retaining source-specific parsing models and typed dimensions.

## Required shared taxonomies

Implement only the taxonomies approved in Phase 6A.

### Occupation family taxonomy

Create a versioned registry, for example:

- `occupation-families-1.0`

Each family must include:

- stable family ID;
- display name;
- description;
- classification system and version;
- included source codes;
- excluded adjacent codes;
- mapping rationale;
- limitations;
- regulated-profession flag where relevant;
- Phase 3 lineage.

Expected initial families:

- technology;
- engineering or science-and-engineering, using the approved truthful name;
- healthcare if approved;
- business-and-finance if approved.

Reject overlapping mappings unless overlap is deliberate, documented, and tested.

### Education field taxonomy

Create a versioned registry, for example:

- `education-fields-1.0`

Each field must include:

- stable field ID;
- display name;
- ISCED-F version;
- included codes;
- excluded adjacent codes;
- degree/level applicability where relevant;
- mapping rationale;
- limitations.

Expected initial fields:

- engineering-manufacturing-construction;
- information-communication-technologies if approved.

### Research field taxonomy

If Engineering academic and research ecosystem is approved, create a frozen mapping from the chosen OpenAlex taxonomy version to a stable Konsider field ID.

Include:

- stable field ID;
- OpenAlex taxonomy version/capture;
- included fields/topics;
- excluded adjacent fields/topics;
- mapping provenance;
- sensitivity notes.

Do not reuse UIS field codes as though they were OpenAlex topics. They may share a Konsider semantic parent but must retain separate source mappings.

## Criterion family metadata

Add a minimal, typed way to identify related criteria, only if the current contract lacks it and it is useful in the API/UI.

Possible concepts:

- `domain`: CAREER or EDUCATION;
- `family`: TECHNOLOGY, ENGINEERING, HEALTHCARE, BUSINESS_FINANCE;
- `evidence_kind`: EMPLOYMENT_MARKET, EDUCATION_CAPACITY, ACADEMIC_ECOSYSTEM;
- `taxonomy_binding`.

Do not introduce a deep hierarchy or subcriterion engine in Phase 6.

## Source adapters and frozen captures

Implement reusable acquisition/parsing foundations for every approved source family.

### ILOSTAT foundation

Support:

- exact approved indicator/table;
- source dimensions;
- classification version;
- country mapping;
- observation status;
- reference year;
- estimate/method flags;
- denominator alignment;
- offline replay;
- exact raw checksums.

The adapter should allow multiple approved occupation families to be derived in one pass.

### UIS foundation

Support:

- exact approved bulk/API asset;
- indicator and dimension metadata;
- ISCED field mapping;
- level mapping;
- counts/shares;
- country mapping;
- reference year;
- offline replay;
- exact raw checksums.

The adapter should allow engineering and ICT education criteria to be derived in one pass.

### OpenAlex/ROR foundation

Only if approved:

- freeze the approved OpenAlex acquisition;
- freeze the ROR release;
- map institution identity;
- map institution country and locality;
- retain unmapped/rejected records;
- retain query or snapshot metadata;
- retain hashes;
- support deterministic replay.

Do not download the complete OpenAlex snapshot if a reproducible official filtered capture is sufficient. Do not use ad-hoc web scraping.

## Future context boundary

Do not add applicant input to ranking requests.

Do add a short ADR or design note that freezes how future context will reference Phase 6 taxonomy IDs.

At minimum discuss future fields such as:

```text
occupation_family_id
education_field_id
degree_level
qualification_country
regulated_profession
household_member_id
```

These are future extension points, not Phase 6 runtime inputs.

Do not add guessed default applicant values.

## Generic criterion orchestration

Use the Phase 5 generic worker/release path.

Avoid new modules named after Phase 6 if the behavior belongs in:

- source adapters;
- taxonomy registry;
- scoring policy;
- criterion registry;
- release builder.

A thin Phase 6 orchestration command is acceptable for repeatable portfolio builds, but publication logic must remain generic.

## Validation rules

Add validation that proves:

- every criterion taxonomy binding resolves;
- source codes exist in the frozen source metadata;
- no occupation or education code is silently dropped;
- source classification version matches the mapping;
- taxonomies are versioned and immutable after publication;
- derived observations retain exact source codes;
- country outcomes reconcile with scores;
- source lineages are complete;
- future-profile metadata does not imply that a profile was evaluated.

## Tests

Add:

- taxonomy schema tests;
- duplicate/overlap tests;
- unknown code tests;
- wrong classification-version tests;
- parser fixtures for all approved families;
- observed/missing/stale/invalid/rejected cases;
- offline capture replay tests;
- source-lineage tests;
- Windows path/newline tests;
- historical release regression tests.

## Required outputs

Create or update:

- versioned taxonomy files;
- source adapters;
- registry/policy definitions;
- validation;
- synthetic and small exact-source fixtures;
- ADR for taxonomy/context boundary;
- `docs/architecture/phase6b-career-education-foundation.md`;
- worker/source documentation.

Do not activate a release.

## Efficiency checkpoint

Before committing, list every new abstraction and which approved criteria use it.

Remove or defer any abstraction with no immediate consumer.

## Commit

Suggested commit:

`feat: add career and education evidence foundation`

Stop and report:

- taxonomy IDs;
- approved source captures;
- reusable components;
- tests;
- remaining criterion-specific work;
- any Phase 6A assumption invalidated by implementation.


---

# FILE: 03_PHASE_6C_OCCUPATION_MARKET_WAVE.md

# Phase 6C Prompt — Occupation-Market Criterion Wave

## Dependency

Proceed only after Phase 6B is complete and the Phase 6A occupation constructs remain approved.

## Objective

Implement and publish all approved occupation-market criteria as one coherent career wave.

The minimum intended set is:

1. Technology employment-market depth.
2. Engineering employment-market depth, or the approved truthful renamed form.

Also include, in the same wave, if approved:

3. Healthcare employment-market depth.
4. Business and finance employment-market depth.

Do not artificially defer approved stretch criteria that use the same source, parser, taxonomy, and scoring framework.

## Product meaning

Every criterion must answer:

> How deep and established is this occupation-family employment market in the country?

It must not answer or imply:

- current vacancy count;
- personal hiring probability;
- salary;
- visa availability;
- language fit;
- recognition of qualifications;
- licensing eligibility;
- seniority fit;
- locality-specific demand unless locality evidence exists.

Use visible caveats in catalog, API evidence, UI details, and documentation.

## Scope decision

Use national direct scope unless Phase 6A found a globally reproducible locality source that clears the same gates.

Do not manufacture an LSC by assigning national occupation data to cities.

A national PCC is acceptable and expected.

## Input selection

For each country and occupation family:

- choose observations using an explicit freshness and source-priority policy;
- require compatible classification;
- prefer both-sex totals;
- avoid summing incompatible national estimates;
- preserve observation method flags;
- reject duplicate/conflicting records deterministically;
- classify missing/stale/invalid/rejected outcomes explicitly.

## Metric and scoring

Implement the approved simple metric.

If Phase 6A approved a blend of scale and specialization, define each component and weight explicitly.

Requirements:

- score range remains consistent with Konsider;
- transform is monotonic;
- reference population/denominator is compatible;
- no large-country domination;
- no tiny-market inflation;
- outlier handling is explicit;
- scoring version is frozen;
- sensitivity analysis supports the selected transform.

Do not use different score formulas for different countries.

## Naming gate

Before publication verify:

- technology codes genuinely represent ICT work;
- engineering name matches the actual code granularity;
- healthcare name does not imply foreign licensing access;
- business/finance name matches included codes.

If the data only supports broader groups, rename truthfully before publication.

## Coverage and portfolio analysis

For each new criterion report:

- valid countries;
- missing countries;
- stale countries;
- invalid/rejected countries;
- selected coverage mode;
- activation threshold;
- eligible-country count when active alone;
- missing-country union with each existing PCC;
- missing-country union with the other career criteria;
- missing-country union under proposed presets.

Do not alter the global coverage policy.

If an approved criterion falls below the existing PCC publication minimum during implementation, hold it with evidence or use an already approved replacement. Do not invent values.

## Interaction with existing Overall job-market opportunity

Quantify:

- Pearson/Spearman correlation;
- rank changes;
- countries with strong overall market but weak occupation-family depth;
- countries with weak overall market but strong occupation-family specialization;
- conceptual overlap.

The new criteria must remain independently useful.

Do not remove Overall job-market opportunity merely because occupation criteria exist.

## Readiness and experimental state

New criteria should normally begin as experimental unless all construct, coverage, and interpretation risks are unusually mature.

Experimental criteria may still be ready and weightable if the current product contract permits it.

## Preference presets

Do not simply add every new PCC at Medium to every existing preset.

Create or update presets deliberately, for example:

- Technology career;
- Engineering career;
- Career opportunity.

A preset must be validated against the PCC missing-union hard limit.

The equal/general preset should remain broadly useful and should not silently trigger coverage fallback because several specialized criteria were added.

Keep weights transparent.

## Release

Publish all approved occupation criteria in one additive immutable release.

Required:

- source registrations and lineages;
- taxonomy snapshots;
- criterion policies;
- scoring methods;
- exact outcomes for all 91 countries;
- observations and scores;
- catalog snapshot;
- checksums;
- replay;
- active pointer update only after all gates pass.

Do not mutate the Phase 5 release.

## API and UI

The current catalog-driven API/UI should render new criteria automatically.

Make only minimal changes required for:

- career domain labels;
- taxonomy/evidence details;
- caveats;
- new presets;
- unavailable outcomes;
- mobile display.

Do not introduce applicant controls in this phase.

## Tests

Cover:

- each occupation family;
- multiple families derived from one source capture;
- missing/stale data;
- classification mismatch;
- scoring boundaries;
- combined PCC activation;
- default and specialized presets;
- comparison and country details;
- active release load;
- offline replay;
- generated API types;
- UI rendering.

## Required report

Create a Phase 6C report including:

- exact public criteria;
- code mappings;
- source/version/licence;
- coverage;
- scoring;
- sensitivity;
- correlations;
- ranking movement;
- default-preset behavior;
- limitations;
- release ID and checksums.

## Commits

Prefer two reviewable commits:

1. implementation and tests:
   - `feat: add occupation-market criteria`
2. immutable release and product integration:
   - `data: publish Phase 6 career criteria release`

If repository conventions strongly favor one commit per additive release, keep the wave coherent but do not mix unrelated education work.

Stop after the career release and report whether the minimum Phase 6 four-criterion target remains achievable.


---

# FILE: 04_PHASE_6D_ENGINEERING_EDUCATION_WAVE.md

# Phase 6D Prompt — Engineering-Education Criterion Wave

## Dependency

Proceed only after:

- Phase 6B shared foundation is complete;
- Phase 6A approved the education constructs;
- Phase 6C career wave is stable.

## Objective

Implement and publish the approved education criteria as one coherent wave.

The intended minimum set is:

1. Engineering higher-education capacity.
2. Engineering academic and research ecosystem.

Also include ICT higher-education capacity if approved and supported by the same UIS evidence.

Do not implement applicant admission probability, tuition affordability, accreditation accessibility, or post-study migration in Phase 6.

## Criterion 1 — Engineering higher-education capacity

### Meaning

Answer:

> How substantial and specialized is tertiary engineering education in this country?

Do not imply:

- that programmes are high quality;
- that programmes are accredited;
- that an international student can enter them;
- that tuition is affordable;
- that teaching is in English;
- that graduates obtain jobs.

### Evidence

Use the exact approved UIS indicators and dimensions.

Retain:

- field code;
- level;
- sex dimension;
- measure;
- unit;
- reference year;
- status/quality flags;
- country mapping;
- source metadata.

### Metric

Implement the Phase 6A-approved simple metric.

If capacity and specialization are blended:

- show both components;
- freeze their weights;
- test sensitivity;
- ensure a high field share with tiny absolute scale does not dominate;
- ensure very large countries do not dominate solely due to population.

If only one component has adequate coverage, use a truthful narrower construct rather than a fragile composite.

### Coverage

Classify all 91 countries explicitly.

Do not fill missing annual values from unrelated sources.

Use a clear freshness policy suitable for education statistics, which may update more slowly than labour statistics.

## Criterion 2 — Engineering academic and research ecosystem

### Meaning

Answer:

> How strong and geographically concentrated is this country's recent engineering academic and research ecosystem?

Do not imply:

- undergraduate teaching quality;
- admissions;
- programme accreditation;
- research employment access;
- innovation commercialization;
- personal university fit.

### Evidence acquisition

Use the approved pinned OpenAlex capture and ROR release.

The production release must not depend on live API calls.

Freeze:

- snapshot/capture date;
- queries or filters;
- data version;
- checksums;
- selected time window;
- field taxonomy mapping;
- institution identity mapping;
- source licence.

### Institution and locality mapping

Map institution evidence to canonical Konsider geographic entities.

Requirements:

- exact institution IDs;
- exact country;
- deterministic locality mapping;
- explicit multi-campus policy;
- explicit treatment of institutions outside the selected locality universe;
- rejected/unmapped records retained in reports;
- no silent nearest-city guess beyond an approved distance/boundary rule.

If institution is valid nationally but cannot be mapped to a selected locality, decide whether it contributes to a national-only component or is excluded. The decision must be consistent and documented.

### Locality aggregation

Use the Phase 5 policy-driven LSC foundation.

Do not automatically reuse the climate locality universe/policy without testing suitability.

Evaluate whether the existing major urban-centre universe is acceptable for academic institutions. If a new institution-oriented locality universe is required, version it and justify it.

The country result should expose:

- contributing institutions;
- contributing localities;
- locality scores;
- aggregation policy;
- full valid locality evidence;
- source lineage.

### Metric

Use a recent multi-year window.

Prefer a transparent combination of:

- engineering research scale;
- breadth/number of active institutions;
- field-normalized impact if robust.

Avoid raw citation totals alone.

Use fractional institutional attribution where needed to prevent multi-institution works from being counted fully multiple times.

### Overlap with existing C05

The new criterion must earn its place.

Report:

- correlation with existing Research and innovation ecosystem;
- correlation with country size;
- examples where field-specific/locality evidence changes interpretation;
- whether the new criterion should coexist, replace a component, or remain experimental.

Do not remove the broad criterion without a separate approved product decision.

## ICT higher-education capacity stretch

If approved, derive it from the same UIS capture and education-field taxonomy.

Apply the same construct discipline.

Do not conflate ICT education capacity with technology labour-market depth. They should be independently weightable and may diverge.

## Portfolio coverage

For every education criterion report:

- valid/missing/stale/invalid/rejected countries;
- coverage mode;
- individual activation effect;
- missing-country union with all existing PCCs and career-wave PCCs;
- behavior under general, technology, engineering-career, and engineering-education presets.

Do not weaken the coverage policy.

## Release strategy

Publish the approved education criteria in one additive immutable release after the career release.

Include:

- source captures and checksums;
- taxonomy snapshots;
- institution mappings;
- locality universe/policies where applicable;
- criterion policies;
- outcomes;
- observations;
- scores;
- derived country evidence;
- catalog snapshot;
- replay verification.

Do not activate the release until both national and locality-derived evidence pass validation.

## API and UI

Use current generic structures.

Make only minimal additions required for:

- education/career domain organization;
- institution evidence;
- contributor localities;
- source and time-window explanation;
- new engineering-education preset;
- experimental labels and caveats.

Do not add applicant admission fields.

## Tests

Cover:

- UIS field parsing;
- count/share consistency;
- stale/missing education data;
- OpenAlex capture replay;
- ROR identity;
- institution/locality mapping;
- fractional attribution;
- field mapping;
- locality aggregation;
- one-locality and multiple-locality countries;
- unmapped institutions;
- overlap/correlation report generation;
- combined PCC coverage;
- API comparison/details;
- UI evidence display;
- full release replay.

## Critical-blocker and replacement rule

If Engineering academic and research ecosystem fails a genuine critical gate:

1. do not publish a weak proxy;
2. record the exact blocker;
3. publish ICT higher-education capacity or another Phase 6A-approved stretch criterion if it clears all gates;
4. keep Engineering academic ecosystem as a named held criterion with a concrete reopening condition.

The phase-level goal remains at least four new criteria, but not by lowering standards.

## Required report

Create a Phase 6D report including:

- final public names;
- Phase 3 lineage;
- exact assets;
- licensing;
- taxonomy;
- coverage;
- scoring;
- institution/locality mapping;
- overlap with C05;
- release inventory;
- limitations;
- held/replacement decisions.

## Commits

Prefer:

1. `feat: add engineering education criteria`
2. `data: publish Phase 6 education criteria release`

Stop after the education release.


---

# FILE: 05_PHASE_6E_PORTFOLIO_INTEGRATION_AND_PRODUCT_VALIDATION.md

# Phase 6E Prompt — Portfolio Integration and Product Validation

## Dependency

Proceed only after the career and education releases are published locally and replay successfully.

## Objective

Validate the new criteria as a coherent product portfolio, not merely as individually valid datasets.

Do not add unrelated new source families in this phase.

## Criterion inventory

Produce a definitive inventory of:

- all previously enabled criteria;
- all Phase 6 criteria;
- diagnostic-only criteria;
- held Phase 6 candidates;
- Phase 3 lineage;
- coverage mode;
- scope;
- experimental status;
- default-enabled status;
- preset membership.

Confirm that at least four new criteria are public unless a critical blocker is documented.

## Semantic separation

Validate and document these distinctions:

### Overall job market versus occupation market

- Overall job-market opportunity measures broad labour-market conditions.
- Technology/engineering/healthcare/business criteria measure occupation-family market depth.
- Neither measures applicant accessibility.

### Education capacity versus academic ecosystem

- Higher-education capacity measures education production/participation.
- Academic ecosystem measures institution/research strength and concentration.
- Neither measures admission probability or tuition affordability.

### Education versus employment

- Engineering education capacity and engineering employment depth are related but independent.
- Avoid combining them into one hidden composite.
- Allow users and presets to weight them separately.

## Redundancy and correlation analysis

For every new criterion compute:

- correlation with relevant existing criteria;
- correlation among Phase 6 criteria;
- rank contribution;
- countries most affected;
- sensitivity to weight 0.2, 0.4, 0.6, 0.8, and 1.0;
- score distribution;
- outliers.

Investigate at least:

- Technology employment versus Overall job market.
- Engineering employment versus Overall job market.
- Technology versus Engineering employment.
- Engineering education capacity versus School education quality.
- Engineering academic ecosystem versus Research and innovation ecosystem.
- Engineering education capacity versus academic ecosystem.
- ICT education versus Technology employment, if present.

High correlation is not automatic rejection, but the report must explain distinct decision value.

## Coverage-union analysis

This is a hard gate.

Adding many PCCs can make a request exceed the Phase 4/5 missing-union limit.

Test:

- each new criterion alone;
- career criteria together;
- education criteria together;
- all Phase 6 criteria together;
- all existing PCCs plus all Phase 6 PCCs;
- every public preference preset;
- representative custom weight combinations.

For each report:

- active PCCs;
- excluded-country union;
- eligible count;
- coverage status;
- fallback behavior;
- top-K robustness.

Do not modify the hard coverage limit merely because the portfolio grew.

## Preference-preset strategy

Create a small, useful preset portfolio.

Consider:

- General balanced;
- Technology career;
- Engineering career;
- Engineering education;
- Career and education.

Rules:

- do not create many near-duplicate presets;
- no preset may hide that it is specialized;
- validate every preset's PCC union;
- specialized criteria may default to zero outside relevant presets;
- preserve user ability to configure all criteria manually;
- do not call presets applicant profiles.

If a desired preset would trigger coverage-limit fallback, redesign its weights or clearly decide not to publish it.

## Product copy

Ensure criterion descriptions say exactly what is measured.

Required phrases or equivalent ideas:

- “employment-market depth, not live vacancies or personal hiring probability”;
- “education capacity, not admission likelihood or teaching quality”;
- “academic and research ecosystem, not programme accreditation or student fit”;
- “profile assessment remains unevaluated because no applicant context is supplied.”

Avoid overly defensive text in the main UI. Keep concise wording in controls and fuller caveats in details/Data & Sources.

## API/UI integration check

Do not redesign the API or UI unless evidence requires it.

Verify:

- catalog-driven rendering;
- structured coverage/locality/profile assessments;
- national and locality-derived contributions;
- institution/locality evidence;
- unavailable outcomes;
- comparisons;
- country details;
- mobile behavior;
- accessibility;
- source and methodology pages;
- preset behavior.

The browser must not calculate taxonomy membership, scores, coverage unions, or locality aggregation.

## Ranking scenarios

Create golden scenarios for:

1. Technology career only.
2. Engineering career only.
3. Engineering education only.
4. Combined engineering employment and education.
5. Strong education but weak employment country.
6. Strong employment but weak education country.
7. Common and non-common locality behavior where academic ecosystem is active with other LSCs.
8. Multiple active PCCs within limit.
9. Multiple active PCCs exceeding limit.
10. Excluded country retaining available evidence.
11. All specialized weights zero.
12. General preset.

Use both synthetic invariants and active-release evidence.

## Required corrections

Fix:

- misleading names;
- caveats;
- preset weights;
- duplicated criterion family metadata;
- catalog readiness;
- API/UI evidence omissions;
- test gaps;
- documentation inconsistencies.

Do not change source values or score methods merely to make rankings look intuitive. Any scoring correction requires evidence and a new immutable release.

## Required outputs

Create:

- `docs/product/phase6e-career-education-portfolio.md`
- a machine-readable correlation/sensitivity report;
- a PCC union/preset report;
- active release examples;
- final preset definitions;
- product wording and limitations.

## Commit

Suggested commit:

`feat: integrate Phase 6 career and education portfolio`

Stop and report:

- total enabled criteria;
- Phase 6 criteria;
- default and specialized presets;
- coverage-union findings;
- remaining product risks.


---

# FILE: 06_PHASE_6F_NEXT_UNLOCK_AND_CONTEXT_BOUNDARY.md

# Phase 6F Prompt — Next-Criterion Unlock Map and Applicant-Context Boundary

## Dependency

Proceed only after Phase 6E confirms the Phase 6 portfolio is coherent.

## Objective

Use actual Phase 6 evidence to state clearly what should be built next to unlock more Phase 3 criteria.

Do not implement a full applicant/profile scoring engine in this phase.

Do not avoid recommending applicant/context work merely because it is larger than another data-only criterion.

## Required analysis

Revisit all remaining unpublished Phase 3 criteria, especially:

- C01 Overall higher-education opportunity;
- C06 International-student accessibility;
- C12-C15 occupation-specific jobs;
- C17 Average earning potential;
- C21-C22 tax/contribution burden;
- C25 Housing affordability;
- C26 Healthcare affordability;
- C32-C36 migration pathways;
- C38 Professional licensing;
- C40 English usability;
- C50 Healthcare capacity;
- C76 Social protection.

Account for the narrowed Phase 6 criteria. Do not claim full C01/C12/C15 completion if Phase 6 only implemented one destination-level component.

## Unlock categories

Classify each remaining criterion into one of these groups:

### A. Immediate reuse

Can be added mostly through existing Phase 6 sources/taxonomies.

Examples may include:

- healthcare employment-market depth;
- business and finance employment-market depth;
- ICT education capacity;
- medical/health education capacity.

These should be recommended as fast follows only if they were not already onboarded.

### B. One additional evidence layer

Requires one substantial new source family but not a full profile engine.

Examples:

- occupation-specific earnings;
- university programme/accreditation inventory;
- tuition and scholarship evidence;
- live or recent vacancy evidence;
- programme teaching language.

For each, identify the exact missing evidence layer and source candidates.

### C. Typed applicant/context engine

Cannot be answered honestly without user-specific inputs.

Examples:

- personal job accessibility;
- professional licensing accessibility;
- university admission fit;
- housing affordability for a household;
- personal tax burden;
- visa and migration pathways;
- co-location of household careers.

For each, identify the minimum context fields.

### D. Still blocked by source/licensing/construct

Not ready even with profile context.

State precise blockers.

## Minimal future context vocabulary

Design a simple next-phase context model using Phase 6 taxonomy IDs.

The design should be minimal and practical.

At minimum consider:

### Applicant

- age band where legally/materially relevant;
- citizenship/current residence;
- occupation family;
- years/seniority;
- qualification field;
- qualification level;
- qualification country;
- languages;
- regulated-profession status.

### Student

- education field;
- intended degree level;
- current curriculum/qualification;
- academic result range;
- budget range;
- teaching language;
- international-student status.

### Household

- members;
- which career/education need belongs to which member;
- co-location preferred or required;
- household income/budget;
- dependants.

Do not turn this into an exhaustive immigration form.

## Separate ecosystem from accessibility

Propose a future scoring pattern:

```text
destination ecosystem score
+ applicant accessibility assessment
+ household/co-location assessment
```

The existing Phase 6 opportunity criteria should remain valid evidence and should not be replaced by opaque personalized scores.

A future applicant result may qualify or constrain the interpretation.

## Decide the next best phase honestly

Choose one of:

1. **Structured applicant and household context**
2. **Additional career/education data wave**
3. **Another source-limited criterion family**

Use evidence from Phase 6.

Decision guidance:

- If the shared source backbone has obvious high-value approved criteria not yet onboarded, a short data fast-follow may be justified.
- If further meaningful criteria require admissions, licensing, earnings, visa, tax, household, or qualification context, recommend the applicant/context phase directly.
- Do not keep adding broad proxies merely to avoid profile work.

## Next-phase candidate plan

Provide:

- recommended next phase title;
- top 5 criteria it could unlock;
- required context fields;
- required source layers;
- architecture changes;
- estimated sequencing;
- criteria that should remain deferred;
- what Phase 6 infrastructure will be reused.

## Required outputs

Create:

- `docs/product/phase6f-next-criterion-unlock-map.md`
- machine-readable remaining-criteria matrix;
- a concise ADR/design note for future context references;
- roadmap update with the honest next phase.

No active runtime change is required unless small metadata corrections are necessary.

## Commit

Suggested commit:

`docs: define post-Phase 6 criterion unlock path`

Stop and present the recommendation plainly.


---

# FILE: 07_PHASE_6G_FINAL_VERIFICATION_AND_CLOSURE.md

# Phase 6G Prompt — Final Verification and Closure

## Dependency

Proceed only after Phase 6A-F are complete and all intended releases are built locally.

## Objective

Verify Phase 6 end to end, fix defects in focused commits, and close the phase with an authoritative criterion-focused report.

## Required exit outcome

Phase 6 should close with at least four new public, ready, weightable criteria unless the closure report demonstrates a critical blocker.

The intended four are:

1. Technology employment-market depth.
2. Engineering employment-market depth or truthful renamed form.
3. Engineering higher-education capacity.
4. Engineering academic and research ecosystem.

If one is blocked, document:

- the exact blocker;
- why it is critical;
- why a weaker proxy was rejected;
- whether an approved stretch criterion replaced it;
- the reopening condition.

Do not describe the phase as fully successful if fewer than four criteria are public without clearly calling out the shortfall.

## Criterion verification

For every Phase 6 criterion verify:

- public ID and name;
- Phase 3 lineage;
- exact construct;
- non-claims;
- category/domain/family;
- coverage;
- scope;
- applicability;
- source/version/licence;
- taxonomy version;
- scoring version;
- readiness;
- experimental state;
- default/preset weights;
- country outcomes;
- source lineage;
- replay.

## Data invariants

Prove:

- all 91 countries have explicit outcomes;
- score exists exactly for valid country result;
- no imputation;
- no country-specific renormalization;
- source codes resolve to frozen taxonomy mappings;
- reference years obey policy;
- classification versions match;
- derived institution/locality evidence is valid;
- release/catalog/manifest/checksums reconcile;
- historical releases are unchanged.

## Ranking and portfolio invariants

Prove:

- each new PCC activates under existing policy;
- combined missing-country unions are correct;
- coverage-limit fallback remains correct;
- no default preset unexpectedly falls back;
- specialized presets are reproducible;
- contributions reconcile to totals;
- new criteria do not change eligibility through profile status;
- `NO_PROFILE_CONTEXT` remains truthful;
- LSC academic evidence does not change country aggregate through common-locality advice.

## Semantic tests

Ensure the public product never claims:

- live vacancies from employment stock;
- personal job probability;
- engineering specificity when data are broader;
- admission probability from education capacity;
- programme quality from graduate counts;
- accreditation from research output;
- applicant fit without context.

## Full test matrix

Run and record:

### Backend

- unit tests;
- integration tests;
- release validation;
- source capture replay;
- active release replay;
- format/lint/static checks;
- compile checks.

### API

- health;
- catalog;
- ranking;
- comparison;
- country details;
- OpenAPI regeneration;
- strict schema tests;
- generated TypeScript no-diff check.

### Frontend

- typecheck;
- lint;
- component tests;
- production build;
- desktop and mobile browser tests;
- accessibility checks.

### Clean checkout

- Windows;
- Linux;
- committed release integrity without licensed raw bytes;
- documented skips only where exact retained raw artifacts are intentionally absent.

### Portfolio

- correlation report;
- score sensitivity;
- PCC union matrix;
- all preference presets;
- ranking scenarios from Phase 6E.

## Defect handling

When a defect is found:

- fix it in a focused commit;
- rerun affected tests;
- rerun full closure gates;
- do not weaken assertions or source standards to pass.

Do not bundle unrelated defects into the closure documentation commit.

## Closure report

Create:

- `docs/history/phase6-closure-report.md`
- `data/reports/phase6g-<date>/report.md`
- updated roadmap;
- updated README/current-position text;
- updated release history;
- updated documentation index.

The closure report must focus on criteria and include:

1. Starting public criterion inventory.
2. Phase 6 target portfolio.
3. Final new criteria.
4. Exact source families.
5. Taxonomies.
6. Coverage and missing countries.
7. Scoring and limitations.
8. National versus locality-derived scope.
9. Relationship to original C01, C05, C12-C15.
10. Which original criteria remain only partially addressed.
11. Stretch criteria added or held.
12. Combined PCC behavior.
13. Preference presets.
14. Test and CI results.
15. Remaining source risks.
16. The next-unlock recommendation.
17. Whether structured applicant/context work is now the best next phase.

Be direct. If the next meaningful criteria require applicant context, say so plainly.

## Final criterion accounting

Provide a table covering all 45 Phase 3 criteria with:

- public;
- partially represented by narrowed criterion;
- immediate fast follow;
- needs one additional evidence layer;
- needs profile/context;
- source/construct blocked;
- rejected.

Do not count a narrowed component as the full original criterion.

## Commit history

List every Phase 6 commit in order.

A reasonable closure commit is:

`docs: close Phase 6 career and engineering education`

## Final report to owner

State:

- active release ID;
- total public criteria;
- new Phase 6 criteria;
- blocked/replaced criteria;
- coverage modes;
- replay/CI status;
- next recommended phase;
- the first five criteria that next phase can unlock.

Stop after closure.
