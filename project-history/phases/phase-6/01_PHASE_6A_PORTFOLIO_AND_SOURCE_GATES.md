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
