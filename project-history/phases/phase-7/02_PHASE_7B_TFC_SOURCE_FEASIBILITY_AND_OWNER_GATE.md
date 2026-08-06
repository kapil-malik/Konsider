# Konsider Phase 7B — Exact-Source Feasibility Probes and Minimum-Three Owner Gate

## Dependency

Proceed only after Phase 7A is accepted.

## Role

Work as the lead source-research, legal/reuse, policy-modelling, deterministic-probe and product-feasibility engineer for Konsider.

This phase is research and non-publishing feasibility work.

Do not implement production TFC contracts, workers, API fields, UI or release activation.

## Objective

Perform exact-source feasibility research for the approved Phase 7A deep-probe slate.

Determine which TFCs can be productionized without:

- inventing profile outcomes;
- using a giant profile × country score matrix;
- relying on live runtime browsing;
- making legal or eligibility guarantees;
- weakening source, licensing, freshness, coverage, comparability or replay standards.

At least three TFCs must qualify before Phase 7C may proceed.

## Required reading

Read:

- Phase 7A report and machine-readable artifacts;
- all linked Phase 3/5 research for each candidate;
- current source audit and licence policy;
- current country mapping and stable 91-country universe;
- immutable release and source-lineage contracts;
- Phase 3 deterministic probe patterns;
- Phase 6 source-gap, calibration and research-to-production reconciliation methods;
- current roadmap and system architecture.

## Research rules

For each candidate, distinguish:

1. useful product question;
2. exact construct;
3. exact official or independent source;
4. technical access;
5. reproducible extraction;
6. legal production use;
7. legal redistribution of normalized facts/rules;
8. supported country coverage;
9. effective-date and refresh handling;
10. deterministic offline replay;
11. applicant-input sufficiency;
12. safe public interpretation.

A public website existing is not evidence that a TFC is production-ready.

## Required deep-probe areas

Use the approved Phase 7A slate. Unless Phase 7A changed it, probe:

- skilled-work route feasibility;
- family accompaniment/reunification feasibility;
- post-study work pathway;
- permanent-residence pathway;
- professional-licensing access/requirements;
- employment tax and mandatory-contribution scenario;
- housing-affordability scenario;
- healthcare-affordability scenario.

## Route/pathway probes

For legal or policy routes, study:

- exact route IDs/names;
- official authority;
- nationality applicability;
- age rules;
- occupation/skill rules;
- qualification rules;
- job-offer rules;
- salary/income thresholds;
- language requirements;
- quota or invitation dependence;
- dependant eligibility;
- partner work rights;
- temporary-to-permanent transitions;
- route closure/suspension;
- effective-from/effective-to dates;
- national versus regional authority;
- whether “no route matched” can be concluded from complete supported evidence;
- whether only positive/conditional matches are safe.

Do not reduce multiple routes to one opaque country score.

## Scenario-metric probes

For tax, contributions, housing or healthcare, study:

- exact calculation unit;
- household model;
- tax year;
- gross/net treatment;
- statutory versus effective burden;
- employee and employer contributions;
- deductions and allowances;
- residence assumptions;
- currency conversion policy;
- locality requirement;
- occupation/salary requirement;
- coverage and freshness;
- calculator/source licensing;
- whether a reproducible formula can be stored;
- whether the result must be a range rather than a point estimate.

Do not use consumer comparison websites or crowd-sourced values as production truth without explicit approved evidence and legal reuse.

## Professional licensing probe

Do not attempt all professions through one generic flag.

Test whether a bounded first version can support one or more precise families, for example:

- physicians;
- nurses;
- selected engineering professions;
- skilled trades.

Record:

- regulator;
- jurisdiction;
- protected title/activity;
- qualification-recognition route;
- examinations;
- supervised practice;
- language requirement;
- fees/timelines only if official and stable;
- region/state variation;
- source and effective date.

A destination workforce shortage is not licensing accessibility.

## Country support and explicit states

For every candidate and each of the 91 countries, classify research support as one of:

- source route assessable;
- source route partially assessable;
- destination unsupported;
- source missing;
- legally blocked;
- construct blocked;
- stale;
- conflicting/unresolved.

Do not silently omit countries.

This is research coverage classification, not the final public TFC outcome enum.

## Production qualification rubric

A TFC qualifies only when all required gates pass.

### Product gate

- precise user question;
- materially useful decision;
- does not duplicate ordering criteria or OFCs;
- output type is understandable;
- limitations are explainable.

### Construct gate

- exact input dimensions;
- exact destination facts/rules;
- deterministic evaluation;
- no unsupported generalization;
- no country-specific exception hidden in code.

### Source gate

- exact source route;
- authoritative or demonstrably independent publisher;
- stable identity;
- reproducible extraction;
- acceptable freshness;
- explicit conflict policy.

### Legal gate

- production access allowed;
- normalized derivative use allowed or explicitly justified;
- attribution captured;
- source snapshots/checksums handled lawfully;
- terms changes monitored.

### Coverage gate

Freeze a candidate-specific minimum before measuring final results.

Prefer:

- broad support across the stable 91-country universe; or
- an explicitly bounded, high-value supported destination subset with visible unsupported states.

Do not lower the threshold after observing poor coverage.

### Profile-input gate

- minimum input set is practical;
- no unnecessary sensitive inputs;
- missing inputs lead to `INPUT_REQUIRED`, not guessed outcomes;
- the same facts can be reused across destinations.

### Replay gate

- exact raw/snapshot identities;
- deterministic parser/mapping;
- offline replay;
- stable serialized research output;
- no LLM or browser search required at runtime.

### Safety/interpretation gate

- result wording avoids legal guarantees;
- effective date is visible;
- “no supported route matched” is not described as permanent impossibility;
- tax/cost values are estimates with assumptions;
- applicant failure is not inferred from destination missingness.

### Maintenance gate

- feasible refresh cadence;
- source-change detection;
- owner/reviewer burden is realistic;
- no fragile manual workflow across 91 destinations without an explicit plan.

## Minimum-three gate

At the end of Phase 7B classify each candidate:

- `PRODUCTION_QUALIFIED_FIRST_WAVE`
- `QUALIFIED_BUT_SECOND_WAVE`
- `NEEDS_TARGETED_FOLLOW_UP`
- `RESEARCH_ONLY`
- `REJECT`

Proceed to Phase 7C only if at least three are `PRODUCTION_QUALIFIED_FIRST_WAVE`.

Prefer three to five.

If more than five qualify, recommend a coherent first wave and hold the remainder.

If fewer than three qualify:

- close Phase 7 as research-only;
- do not create production contracts or runtime code;
- document the most promising follow-up;
- update the roadmap;
- stop.

## Result-family diversity

Prefer at least two result families in the first wave.

Do not fail otherwise-qualified TFCs merely to force diversity.

If all qualified TFCs use one family, explicitly narrow the first production contract to that family rather than pretending to have a generic multi-type engine.

## Research artifacts

Produce deterministic research artifacts containing:

- candidate definitions;
- source manifests;
- legal/reuse conclusions;
- country support matrix;
- required profile fields;
- route/rule examples;
- metric formula examples;
- effective-date handling;
- conflict cases;
- sample profile evaluations;
- state-count or support-count summaries;
- checksums and replay instructions.

Use synthetic applicant profiles for research tests. Do not store real user data.

## Sample scenarios

At minimum evaluate synthetic scenarios that test:

- applicant missing a required field;
- applicant with a job offer;
- applicant without a job offer;
- applicant relocating alone;
- applicant relocating with partner/child;
- student scenario;
- unsupported nationality/source case;
- regional licensing case;
- evidence changed after effective date;
- conflicting official evidence;
- scenario metric with missing salary or city.

## Owner decision package

Create a concise decision table containing:

- TFC ID and public name;
- original criterion mapping;
- check kind;
- required inputs;
- supported destination coverage;
- source route;
- legal conclusion;
- refresh burden;
- public limitations;
- first-wave recommendation;
- blocking decisions.

Explicitly ask the owner to approve:

- first-wave TFC list;
- exact user-facing names;
- supported profile boundaries;
- supported destination boundary;
- result-family scope;
- whether explicit post-ranking filtering is permitted for route-match checks;
- device/session retention direction.

## Required outputs

Create:

- `docs/research/phase7b-tfc-source-feasibility.md`;
- machine-readable candidate/source/support matrices under `data/reports/phase7b-*/`;
- deterministic probe scripts under the historical/research area;
- replay instructions;
- owner-decision summary;
- roadmap update.

Do not publish production artifacts.

## Verification

Confirm:

- each deep-probe candidate has an exact disposition;
- all 91 destinations have an explicit research support state;
- no unsupported country is inferred as negative;
- no real profile data is committed;
- all live research can replay from captured lawful inputs;
- exact source and legal conclusions are recorded;
- minimum-three result is explicit.

## Commit

Use a focused commit such as:

`research: complete Phase 7B TFC source gates`

## Stop condition

Stop for owner approval.

Report:

- production-qualified count;
- recommended first-wave list;
- supported country/profile boundaries;
- result families;
- source and legal risks;
- follow-up candidates;
- files changed;
- commands/results;
- commit SHA.

Do not begin Phase 7C automatically.
