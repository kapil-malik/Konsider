# Konsider Phase 7 — Complete Modular Prompt Pack

This combined file mirrors the modular files in this directory. Execute one phase at a time and use the individual files for Codex work.


---

# Konsider Phase 7 — Typed Feasibility Checks and Guest Profile Context

## Purpose

This prompt pack is intended to be given to Codex / ChatGPT on the local Konsider repository, one phase at a time.

Phase 7 explores and, only if the evidence gates pass, implements **Typed Feasibility Checks (TFCs)** using explicit applicant, household, and exploration-scenario context.

Do not execute the entire pack as one task. Complete, test, document, commit, and obtain owner approval for each phase before beginning the next one.

## Terminology decision

Use:

- **Typed Feasibility Check**
- internal shorthand: **TFC**
- user-facing language: **Feasibility check**, **Your situation**, or **Your feasibility**, depending on the UI surface

Do not use “Typed Feasibility Criterion” in the implementation unless repository evidence justifies reversing this decision.

The word **check** is preferred because a TFC may return:

- a route or requirements match;
- a conditional match;
- missing required inputs;
- insufficient destination evidence;
- a calculated scenario metric;
- a contextual advisory result.

A TFC is not necessarily a score and must not be treated as an ordering criterion.

## Phase 7 product goal

Konsider must remain fully useful to a guest.

A user may optionally provide structured context describing:

1. the applicant;
2. the household;
3. the current relocation, work, or education scenario.

Konsider then evaluates selected or applicable TFCs against immutable, versioned destination evidence and policies.

The result must remain separate from:

- affinity score;
- ordering criteria;
- FCC/PCC coverage behavior;
- LSC aggregation and locality compatibility;
- Opportunity Filter states;
- preference presets.

## Approved product direction

Treat these as approved unless current repository evidence exposes a direct contradiction.

### Guest first

Phase 7 must not require authentication.

Profile and scenario data are:

- held in browser memory by default;
- optionally retained for the browser session;
- optionally remembered on the device only after explicit user action;
- never silently persisted server-side;
- never written to immutable public releases, source artifacts, analytics, URLs, or application logs.

### Profile is not the same as an account

Model separately:

- `ApplicantProfile`: reusable facts about an applicant;
- `HouseholdProfile`: reusable household composition and relevant facts;
- `ExplorationScenario`: temporary assumptions for a particular decision;
- `EffectiveProfileContext`: the immutable request snapshot actually evaluated.

A future account may own several saved profiles and several scenarios. Do not design one account as exactly one applicant.

### Explicit request snapshot

Even after future login exists, evaluation must use an explicit profile/scenario snapshot supplied with or resolved for the request.

Do not let assessment logic silently read a mutable “latest account profile.”

### No login implementation in Phase 7

Design clean persistence boundaries, but do not implement:

- authentication;
- account recovery;
- server-side saved profiles;
- cross-device sync;
- chat history;
- conversational memory;
- notifications.

### No hidden personalization

Do not infer sensitive or consequential profile facts.

Unknown means unknown. Missing profile fields must remain explicit.

## Phase 7 research gate

Implementation after Phase 7B may proceed only if at least **three TFCs** qualify for production.

Prefer a first wave of **three to five TFCs**.

If more than five qualify, the owner must select a coherent first wave rather than onboarding all of them automatically.

If fewer than three qualify:

- stop Phase 7 after the research and owner-decision report;
- do not create a generic runtime framework merely to claim implementation progress;
- document the blockers and next-best source research;
- leave the active release, API, and UI unchanged.

### Diversity preference

Prefer the qualified first wave to exercise at least two TFC result families, for example:

- rule/route matching; and
- calculated scenario metrics.

Do not weaken source, legal, coverage, construct, privacy, or replay gates merely to obtain type diversity.

## Candidate research universe

Phase 7A must revisit every Phase 3 criterion classified as profile-dependent.

At minimum include:

- C01 Overall higher-education opportunity
- C06 International-student accessibility
- C08 School education quality
- C12 Software and technology jobs
- C13 Medical and healthcare jobs
- C14 Business, finance, and professional-services jobs
- C15 Engineering and skilled technical jobs
- C17 Average earning potential
- C21 Personal income-tax burden
- C22 Social-security and mandatory contribution burden
- C25 Housing affordability
- C26 Healthcare affordability
- C32 Skilled-work visa accessibility
- C33 Permanent-residency accessibility
- C34 Citizenship accessibility
- C35 Post-study migration pathway
- C36 Family reunification support
- C38 Professional-licensing accessibility for immigrants
- C40 English usability
- C45 LGBTQ+ legal and social inclusion
- C76 Social protection and welfare support

The first deep-probe slate should normally be no more than eight candidates.

The default priority slate to validate, not blindly accept, is:

1. skilled-work route feasibility;
2. family accompaniment/reunification feasibility;
3. post-study work pathway;
4. permanent-residence pathway;
5. professional-licensing requirement/access check;
6. employment tax and mandatory-contribution scenario;
7. housing-affordability scenario;
8. healthcare-affordability scenario.

Phase 7A may replace items when evidence supports a better slate.

## Relationship with Opportunity Filters

Opportunity Filters remain destination-side ecosystem signals.

TFCs may combine with OFCs in explanations, but must not mutate OFC evidence or reinterpret OFC states.

Examples:

- strong technology ecosystem + supported skilled-work route match;
- strong care-sector ecosystem + professional licensing requirements not yet met;
- strong biomedical research-university ecosystem + student route requires additional inputs.

A non-verified OFC is not proof that a personal opportunity is absent.

A failed or unsupported TFC is not proof that the destination itself is poor.

## Proposed execution sequence

| Phase | Intent |
|---|---|
| 7A | Product discovery, complete profile-dependent criterion disposition, context model, first deep-probe slate |
| 7B | Exact-source feasibility probes, production qualification, minimum-three owner gate |
| 7C | Profile, scenario, privacy, TFC and assessment contracts; ADRs and synthetic fixtures only |
| 7D | Generic rule/evidence worker and immutable release foundation |
| 7E | Typed assessment engine, input sufficiency, scenario snapshots and optional explicit feasibility filtering |
| 7F | Production onboarding of the approved first-wave TFCs into staged immutable artifacts |
| 7G | Stateless API v2 profile/TFC transport and generated client contract |
| 7H | Guest-first profile/scenario UI and explicit local/session retention |
| 7I | OFC/locality/TFC integration, scenario comparison and end-to-end verification |
| 7J | Immutable release activation, regression/privacy verification, closure and roadmap |

## Proposed commit sequence

Use focused commits. Do not create one monolithic Phase 7 commit.

| Phase | Expected commit intent |
|---|---|
| 7A | Research and product-boundary documentation only |
| 7B | Source probes, qualification matrix and owner gate only |
| 7C | ADRs, schemas, contracts and synthetic fixtures |
| 7D | Generic worker/release foundation |
| 7E | Assessment engine and scenario snapshot domain logic |
| 7F-n | Prefer one qualified TFC or one inseparable source family per commit |
| 7G | API/OpenAPI/generated-client changes |
| 7H | Guest profile UI and browser retention |
| 7I | Integration and end-to-end scenarios |
| 7J | Release, closure, cleanup and roadmap |

## Global execution rules

Apply these rules to every prompt:

1. Start from the latest `main` branch.
2. Inspect current repository paths and active contracts before making assumptions.
3. Read the previous phase report, ADRs, schemas, fixtures and tests.
4. Preserve immutable historical releases.
5. Do not weaken no-imputation or complete-case ranking guarantees.
6. Do not change affinity scores because of a TFC.
7. Do not put TFCs into criterion weights or preference presets.
8. Do not put TFCs into the OFC catalog.
9. Do not infer profile values from country, browser, name, email or other indirect signals.
10. Keep destination evidence and applicant input separate.
11. Store destination evidence and policies, not precomputed profile × country matrices.
12. Keep runtime assessment deterministic and explainable.
13. Use exact official or demonstrably independent sources with explicit licensing conclusions.
14. Preserve effective dates, policy versions, source snapshots/checksums and replay.
15. Missing evidence is not a negative conclusion.
16. Missing profile input is not destination failure.
17. Do not make legal, immigration, tax, admissions or licensing guarantees.
18. Every public result must disclose scope, effective date, limitations and source.
19. API runtime must never fetch external sources.
20. UI must not implement eligibility, route, tax or scoring rules.
21. Do not log profile request bodies or place profile values in URLs.
22. Do not persist profile context server-side in Phase 7.
23. Add tests at the layer that owns each rule.
24. Update documentation in the same phase as behavior.
25. Do not begin the next phase automatically.
26. End each phase with a concise report, commands/results, changed paths, commit SHA and unresolved owner decisions.

## Current baseline

Begin from the current active release and contracts found in the repository.

At the time this pack was written, the expected baseline was:

- active release `2026-08-04.1`;
- schema-5.1 release with 91 countries;
- ordering criteria, FCC/PCC, LSC and OFC behavior already active;
- `assessments.profile` reserved but unevaluated;
- authentication, saved profiles and persistent sessions deferred.

Repository truth takes precedence if the baseline has changed.

## How to use this pack

Run:

1. `01_PHASE_7A_TFC_DISCOVERY_AND_PRODUCT_BOUNDARY.md`
2. `02_PHASE_7B_TFC_SOURCE_FEASIBILITY_AND_OWNER_GATE.md`

Stop for explicit owner review.

Only if at least three TFCs are approved, continue in order through Phase 7J.

The combined file `KONSIDER_PHASE_7_PROMPT_PACK.md` is provided for reference. Prefer the modular files during execution.


---

# Konsider Phase 7A — TFC Discovery, Product Boundary and Candidate Portfolio

## Role

Work as the lead product researcher, decision-model architect, privacy-aware product owner and evidence-methodology reviewer for the Konsider repository.

This is a research and product-definition phase only.

Do not change runtime schemas, workers, releases, ranking, API behavior or UI behavior.

## Objective

Define what a Typed Feasibility Check is in Konsider and identify the strongest candidates for exact-source feasibility research.

Revisit every deeply researched criterion previously classified as profile-dependent.

Produce:

- a complete disposition;
- a typed applicant/household/scenario input model;
- candidate TFC result families;
- a bounded deep-probe slate for Phase 7B;
- a clear guest-first product flow;
- a source and privacy risk plan.

## Required repository reading

Read at minimum:

- `docs/research/phase3-closure-report.md`;
- all retained Phase 3 batch research records;
- `docs/research/phase5a-locality-criteria-discovery.md`;
- `docs/architecture/phase5b-target-contracts.md`;
- ADR 005 and ADR 007;
- `docs/history/phase5-closure-report.md`;
- Phase 6B, 6B.1 and 6C research reports;
- Opportunity Filter contracts, ADR and closure report;
- `docs/product/roadmap.md`;
- `docs/architecture/system-architecture.md`;
- current active catalog/release manifests;
- current API v2 ranking request/response and structured assessments;
- current browser-state behavior and UI documentation.

Find current paths rather than assuming these paths remain unchanged.

## Terminology

Use **Typed Feasibility Check**, abbreviated `TFC`.

Explain in the research report why “check” is safer than “criterion”:

- not all TFCs produce a score;
- some evaluate route requirements;
- some calculate scenario values;
- some require more input;
- some are not applicable;
- TFCs do not rank countries by default.

Propose user-facing language separately from internal types.

## Product boundary

Define TFCs as a sibling product role.

A TFC must not be represented as:

- an ordering criterion;
- a PCC;
- an LSC;
- an Opportunity Filter;
- a preference preset;
- an account setting.

A TFC evaluates explicit profile/scenario context against versioned destination evidence and policy.

## Complete disposition matrix

Create a complete matrix covering at least these 21 candidates exactly once:

- C01 Overall higher-education opportunity
- C06 International-student accessibility
- C08 School education quality
- C12 Software and technology jobs
- C13 Medical and healthcare jobs
- C14 Business, finance, and professional-services jobs
- C15 Engineering and skilled technical jobs
- C17 Average earning potential
- C21 Personal income-tax burden
- C22 Social-security and mandatory contribution burden
- C25 Housing affordability
- C26 Healthcare affordability
- C32 Skilled-work visa accessibility
- C33 Permanent-residency accessibility
- C34 Citizenship accessibility
- C35 Post-study migration pathway
- C36 Family reunification support
- C38 Professional-licensing accessibility for immigrants
- C40 English usability
- C45 LGBTQ+ legal and social inclusion
- C76 Social protection and welfare support

For each record include:

- original criterion ID and name;
- original Phase 3 and Phase 5 disposition;
- precise user decision answered;
- proposed TFC name;
- proposed check kind;
- stable applicant inputs;
- scenario-specific inputs;
- household inputs;
- sensitive/optional inputs;
- destination evidence required;
- natural geography: country, region, city, institution or route;
- relation to an existing OFC;
- relation to existing ordering criteria;
- whether a hard/conditional route exists;
- whether output is categorical, numeric, range or advisory;
- whether the result could safely support explicit post-ranking filtering;
- source families;
- freshness requirement;
- expected coverage;
- licensing/reuse risk;
- maintenance burden;
- legal/interpretation risk;
- expected product value;
- recommendation:
  - `DEEP_PROBE`
  - `SECOND_WAVE`
  - `PROFILE_MODEL_ONLY`
  - `RESEARCH_ONLY`
  - `REJECT_TFC`
- precise blockers.

## Typed result-family study

Do not force one result enum onto every TFC.

Study at least:

### Rule or route match

Examples:

- skilled-work route;
- post-study route;
- family route;
- permanent-residence route;
- professional licensing.

Possible structure:

- common evaluation status;
- zero or more matched routes;
- matched conditions;
- unmet conditions;
- unsupported or unknown conditions;
- source and effective date.

### Scenario metric

Examples:

- estimated employment tax burden;
- mandatory contributions;
- rent-to-net-income ratio;
- estimated healthcare cost.

Possible structure:

- numeric value or range;
- currency and period;
- assumptions;
- confidence/quality;
- missing components;
- optional derived comparison band.

### Contextual advisory

Examples:

- English usability for stated language needs;
- school-system fit;
- inclusion relevance.

Treat advisory language cautiously. Avoid unsupported “good/bad for this person” conclusions.

Recommend the minimum type system needed for the first wave. Do not design a universal rules language in Phase 7A.

## Profile and scenario study

Define a candidate field inventory.

Separate:

### Applicant profile

Examples:

- citizenships;
- age or date-of-birth representation;
- current residence;
- occupation taxonomy and specialization;
- years of experience;
- qualifications and qualification countries;
- professional registrations;
- languages and tested proficiency.

### Household profile

Examples:

- partner accompanying;
- partner work intent;
- dependants;
- child ages;
- household size.

### Exploration scenario

Examples:

- work, study or family-relocation purpose;
- target year;
- job-offer status;
- offered salary and currency;
- intended occupation;
- intended course/degree;
- target cities/regions;
- housing tenure and dwelling assumptions;
- budget;
- whether relocation is solo or household.

For every field record:

- which candidate TFCs need it;
- whether mandatory, conditional or optional;
- sensitivity classification;
- validation rules;
- whether it is stable or scenario-specific;
- whether it may be retained locally;
- whether it must never be retained by default.

Do not ask for data merely because it may be useful someday.

## Guest-first experience

Propose a product flow that allows:

1. ordinary anonymous ranking without profile context;
2. optional “Add your situation”;
3. progressive questions driven by selected/applicable TFCs;
4. an explicit summary of assumptions;
5. separate affinity, opportunity and feasibility explanations;
6. easy correction and clearing;
7. optional session/device retention;
8. future save-to-account without requiring login now.

Do not design a login wall.

## OFC interaction

For every career and education OFC, document:

- which TFCs may add access/feasibility context;
- which profile fields are needed;
- what must never be inferred from the OFC;
- how conflicting-looking evidence is explained.

Examples to test:

- strong technology ecosystem but no supported work-route match;
- strong care-sector ecosystem but licensing requirements unresolved;
- strong education ecosystem but admission/student-route inputs missing;
- no verified strong ecosystem but one specific route still matches.

## Deep-probe selection

Recommend no more than eight candidates for Phase 7B.

Start by evaluating this default slate:

1. skilled-work route feasibility;
2. family accompaniment/reunification feasibility;
3. post-study work pathway;
4. permanent-residence pathway;
5. professional-licensing access/requirements;
6. employment tax and mandatory-contribution scenario;
7. housing-affordability scenario;
8. healthcare-affordability scenario.

Replace candidates where the evidence shows a materially stronger option.

For each selected candidate specify:

- exact construct;
- target users;
- minimum input fields;
- result family;
- exact source questions;
- expected country support;
- highest-risk blocker;
- Phase 7B probe plan.

## Required outputs

Create:

- `docs/research/phase7a-tfc-discovery.md`;
- a machine-readable 21-row disposition under `data/reports/phase7a-*/`;
- a candidate profile/scenario field registry;
- a TFC-to-OFC crosswalk;
- a Phase 7B deep-probe protocol;
- a roadmap update stating that Phase 7 implementation is gated by at least three production-qualified TFCs.

Do not change the active release or runtime.

## Verification

Confirm:

- every profile-dependent Phase 3 candidate appears exactly once;
- no profile criterion is disguised as a universal country score;
- no TFC is placed into ordering criteria or OFCs;
- every proposed field has a named consumer;
- sensitive fields are optional and purpose-bound;
- the deep-probe slate contains no more than eight candidates;
- each deep-probe candidate has an exact user question and source plan.

## Commit

Use a focused commit such as:

`docs: complete Phase 7A TFC discovery`

## Stop condition

Stop after the Phase 7A report and artifacts are complete.

Report:

- recommended TFC definition;
- 21-candidate disposition counts;
- deep-probe slate;
- proposed result families;
- proposed profile/scenario boundaries;
- privacy concerns;
- files changed;
- checks run;
- commit SHA;
- owner questions before Phase 7B.


---

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


---

# Konsider Phase 7C — Profile Context, Privacy, TFC Contracts and ADRs

## Dependency

Proceed only after:

- Phase 7B is accepted;
- at least three first-wave TFCs are owner-approved;
- their source and product boundaries are frozen.

## Role

Work as the lead domain-contract, privacy-by-design, API-contract and architecture engineer for Konsider.

This phase implements contracts, ADRs, schemas and synthetic fixtures only.

Do not onboard production TFC evidence, activate a release, expose client API fields or add UI.

## Objective

Define the clean target contracts for:

- applicant profile;
- household profile;
- exploration scenario;
- effective profile snapshot;
- TFC definitions;
- required inputs;
- typed TFC outcomes;
- profile/TFC assessments;
- privacy and retention metadata;
- future saved-profile persistence boundaries.

## Architectural decisions

Create ADRs for at least:

1. TFCs as a sibling product role.
2. Applicant profile versus exploration scenario.
3. Explicit effective-context snapshots.
4. Guest-first, stateless-server evaluation.
5. Browser retention requiring explicit user choice.
6. Typed outcomes rather than one universal score/state.
7. TFC assessment independence from ranking, PCC, locality and OFC.
8. Future account persistence as an adapter, not a domain dependency.

## Core profile contracts

Define versioned types conceptually equivalent to:

### ApplicantProfile

- stable profile ID optional for future saved profiles;
- schema version;
- citizenships;
- residence country where required;
- age/date representation chosen through ADR;
- occupation taxonomy/version;
- specialization;
- experience;
- qualifications;
- professional registrations;
- languages/proficiency;
- explicit unknowns;
- field-level provenance/source: user supplied, imported or derived;
- no authentication fields.

### HouseholdProfile

- household ID optional;
- partner/dependant composition;
- child ages or age bands where needed;
- partner work/study intent;
- relocation participation;
- explicit unknowns.

### ExplorationScenario

- purpose;
- target date/year;
- job offer;
- salary and currency;
- intended occupation;
- intended study;
- target localities;
- housing assumptions;
- budget assumptions;
- relocation composition;
- selected TFC IDs;
- optional explicit feasibility-filter mode.

### EffectiveProfileContext

A request-scoped immutable snapshot containing:

- normalized applicant;
- normalized household;
- normalized scenario;
- schema versions;
- resolved taxonomy versions;
- selected TFCs;
- generated snapshot hash;
- evaluation timestamp;
- no server persistence identifier required.

Do not use a mutable account record as the evaluation object.

## Field requirement contracts

Each TFC definition must declare typed input requirements.

Support:

- always required;
- conditionally required;
- optional explanatory;
- not used.

Conditional requirements must be deterministic and inspectable.

Avoid a general-purpose expression language unless the approved first wave requires it.

A small typed condition vocabulary is preferable.

For every field include:

- stable field ID;
- data type;
- validation;
- sensitivity classification;
- retention recommendation;
- consumer TFCs;
- public prompt/help text;
- whether it may be omitted;
- whether it may be stored locally;
- redaction behavior.

## TFC definition contract

Required fields should include:

- stable TFC ID;
- public name;
- compact label;
- source criterion mapping;
- product role fixed to TFC;
- check kind;
- exact construct;
- user question answered;
- plain-language meaning;
- explicit limitations;
- required/conditional input definitions;
- destination evidence policy ID;
- evaluation policy ID;
- source bundle ID;
- result schema/type ID;
- scope;
- supported destination/profile boundary;
- effective-date policy;
- refresh policy;
- filter capability:
  - assessment only;
  - explicit supported-route filtering allowed;
- active/available flag;
- sort order;
- documentation reference.

Prohibit:

- criterion weight;
- affinity contribution;
- normalization direction;
- PCC activation threshold;
- OFC public state;
- LSC aggregation fields;
- hidden account lookup.

## Common evaluation status

Define a small common status applicable to every TFC.

The exact enum must follow Phase 7B evidence, but it should distinguish at least:

- evaluated;
- more profile input required;
- destination evidence insufficient;
- unsupported destination/profile;
- not applicable;
- evaluation error only for technical failure.

Do not encode the substantive route or metric result into the common status.

## Typed result payloads

Implement only the result families approved after Phase 7B.

### Route/rule result

Support:

- supported routes evaluated;
- matched routes;
- match classification;
- met conditions;
- unmet conditions;
- unknown conditions;
- blocking conditions;
- evidence/source/effective date;
- caveats;
- explicit wording that no supported-route match is not a permanent legal impossibility.

### Scenario metric result

Support:

- metric value or range;
- unit/currency;
- period;
- assumptions;
- components;
- confidence/quality;
- missing components;
- optional comparison band only when research approved;
- source/effective date;
- caveats.

### Advisory result

Add only if a first-wave TFC needs it.

Do not invent a vague universal favorable/unfavorable enum.

## Structured assessment placement

Extend the existing structure without overloading siblings.

Conceptually:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {},
    "opportunity": {},
    "feasibility": {}
  }
}
```

Define:

- response-level profile-context summary;
- response-level TFC execution summary;
- country-level feasibility assessment;
- per-TFC country outcomes;
- input-required summary;
- source/effective-date summary;
- explicit base-rank versus optional feasibility-filtered position.

Do not place TFC results inside `assessments.profile` if doing so would make profile presence and TFC execution the same concept.

A clean split may be:

- `assessments.profile`: context supplied, dimensions evaluated and privacy/retention state;
- `assessments.feasibility`: selected checks and country outcomes.

Document the decision.

## Privacy contracts

Define:

- field sensitivity classes;
- default retention;
- redaction;
- exportability;
- clear/delete behavior;
- log prohibition;
- URL prohibition;
- analytics prohibition;
- server persistence fixed to none for Phase 7;
- device-storage consent marker;
- expiration/version invalidation.

No real profile fixtures.

All fixtures must be synthetic and visibly fictional.

## Future persistence boundary

Define repository interfaces or domain ports only where they materially protect architecture.

Support future concepts such as:

- saved applicant profiles;
- saved household profiles;
- saved scenarios;
- revisions;
- ownership;
- import/export;
- migration from local guest storage.

Do not implement a database, authentication or unused CRUD service.

## Release contract

Design an additive/major release extension for:

- TFC catalog;
- destination rule/evidence bundles;
- TFC policy bundles;
- source/legal manifests;
- coverage/support summaries.

Profile input and profile outcomes must not be stored in the immutable public release.

Old releases without TFCs must remain loadable through historical loaders.

Do not activate a release.

## Synthetic fixtures and tests

Add fixtures for:

- no profile context;
- partial profile;
- complete profile;
- route match;
- conditional route match;
- no supported route match;
- input required;
- unsupported destination;
- insufficient destination evidence;
- scenario metric;
- household-dependent result;
- region-dependent result;
- multiple TFC types;
- no TFC selected;
- optional explicit filtering capability;
- redaction/export;
- old release compatibility.

Add invalid fixtures rejecting:

- TFC weight fields;
- OFC states in TFC payloads;
- profile data in release artifacts;
- hidden account identifiers as required runtime inputs;
- missing source/effective-date metadata;
- route result without evaluated-route identity;
- numeric result without units/assumptions;
- sensitive fields marked for silent persistence.

## Required outputs

Create/update:

- TFC architecture document;
- profile/scenario contract document;
- privacy and retention document;
- ADRs and ADR index;
- versioned schemas;
- synthetic fixtures;
- contract tests;
- terminology glossary;
- Phase 7C implementation report.

## Explicit non-goals

Do not:

- onboard production TFC evidence;
- activate a release;
- implement login;
- persist profiles server-side;
- expose API fields to current clients;
- add UI;
- change ranking;
- change OFC evaluation;
- change PCC/LSC behavior;
- implement chat.

## Commit

Use a focused commit such as:

`feat: define Phase 7 TFC and profile contracts`

## Stop condition

Stop when contracts, ADRs, fixtures, validation and documentation pass.

Report:

- chosen terminology;
- approved first-wave TFCs;
- schema/release version decisions;
- exact common statuses and result types;
- privacy decisions;
- compatibility results;
- files changed;
- tests run;
- commit SHA;
- owner decisions before Phase 7D.


---

# Konsider Phase 7D — Generic TFC Rule, Evidence and Immutable Release Foundation

## Dependency

Proceed only after Phase 7C contracts are accepted and merged.

## Role

Work as the lead worker, immutable-release, source-lineage, rule-artifact and deterministic-replay engineer for Konsider.

## Objective

Implement the generic production path for destination-side TFC evidence and policies.

Do not onboard the final first-wave TFC source data yet.

Do not expose API behavior, add UI or activate a release.

## Core principle

Store:

- destination rules;
- destination evidence;
- effective dates;
- source identities;
- evaluation policies.

Do not store:

- precomputed profile × country outcomes;
- real applicant data;
- session data;
- account data.

## Generic source architecture

Extend the existing worker/source registry to support TFC source families such as:

- structured APIs;
- official tables;
- official policy documents;
- rule schedules;
- jurisdiction mappings;
- formula tables.

For each input retain:

- publisher;
- responsible authority;
- exact asset/endpoint/document;
- extraction date;
- effective period;
- checksum or immutable identity where lawful;
- access and licence;
- normalized derivative conclusion;
- attribution;
- refresh cadence;
- change-detection method;
- parser version;
- manual-review status where required.

Do not make research scripts production dependencies.

## Rule/evidence artifact model

Implement typed artifacts for:

- TFC definition;
- destination support record;
- jurisdiction;
- route/rule definition;
- condition;
- threshold;
- formula/component;
- source reference;
- effective period;
- conflict status;
- evidence quality;
- unsupported/missing reason;
- policy version.

Avoid one unbounded JSON blob.

Permit type-specific payloads behind versioned schemas.

## Jurisdiction and geography

Reuse canonical geography where possible.

Support explicit jurisdiction levels where approved:

- country;
- region/state/province;
- city/locality;
- institution;
- regulator/service authority.

Do not overload country codes with regulator or route IDs.

A country may have:

- national rule;
- regional override;
- unsupported region;
- conflicting authority evidence.

## Effective-date handling

Every mutable legal/policy/rate record must have:

- known effective-from;
- effective-to where known;
- extraction/verification date;
- source publication/update date where available;
- stale-after policy;
- supersession linkage;
- conflict resolution status.

Do not evaluate a future or expired rule silently.

## Release and catalog foundation

Extend the release writer/loader/validator to bind:

- TFC catalog;
- destination support matrix;
- rule/evidence bundles;
- evaluation-policy bundles;
- source/legal manifest;
- support/coverage summary;
- validation report.

The active release must remain unchanged.

Old releases must remain inspectable.

## Explicit country support

For each staged TFC, the future release must contain an explicit support record for every stable country, even when:

- unsupported;
- evidence insufficient;
- legally blocked;
- stale;
- not applicable at national level.

Runtime must not infer missing records.

## Deterministic build

Implement:

- online capture where allowed;
- offline replay from captured inputs;
- normalized output generation;
- stable ordering;
- LF-stable serialization;
- checksum validation;
- no-diff regeneration;
- candidate release assembly;
- validation before promotion.

Do not use live network calls in API runtime.

## Reviewable policy changes

A destination rule change must be visible as:

- source input changed;
- normalized rule changed;
- effective date changed;
- evaluation policy changed;
- support state changed.

Generate a semantic diff report.

Do not hide rule changes inside parser code.

## Synthetic foundation

Use synthetic, fictional rule/evidence bundles to prove:

- route/rule family;
- scenario metric family;
- national and regional rules;
- effective-date selection;
- source conflict;
- unsupported country;
- stale evidence;
- multiple routes;
- formula components;
- deterministic replay.

Synthetic data must never activate production.

## Validation and tests

Add tests for:

- source manifest validation;
- rule schema validation;
- effective-period overlap;
- duplicate route IDs;
- jurisdiction mapping;
- country support completeness;
- one support record per TFC-country pair;
- no profile data in releases;
- no ranking fields;
- no OFC state fields;
- legacy release compatibility;
- deterministic candidate build;
- semantic diff generation;
- source conflict handling;
- expired/future rule rejection;
- stable serialization.

## Documentation

Document:

- adding a TFC source;
- adding a route/rule;
- adding a metric formula;
- jurisdiction mapping;
- effective dates;
- refresh and change review;
- offline replay;
- source/legal review;
- research-to-production promotion;
- why applicant outcomes are computed at request time.

## Explicit non-goals

Do not:

- onboard approved production TFCs;
- activate a release;
- implement assessment logic beyond synthetic foundation needs;
- change API;
- change UI;
- implement profile storage;
- implement login;
- change ranking/OFC/PCC/LSC behavior.

## Required outputs

1. generic TFC source registry support;
2. typed rule/evidence artifacts;
3. release/catalog binding;
4. validation and semantic diff;
5. deterministic build/replay commands;
6. synthetic fixtures;
7. tests;
8. documentation;
9. Phase 7D implementation report.

## Commit

Use a focused commit such as:

`feat: add generic TFC release foundation`

## Stop condition

Stop when synthetic candidate releases build and replay deterministically while the active release remains unchanged.

Report:

- schema/release changes;
- artifact inventory;
- compatibility result;
- tests and replay results;
- changed paths;
- commit SHA;
- blockers before Phase 7E.


---

# Konsider Phase 7E — Typed Assessment Engine and Scenario Snapshots

## Dependency

Proceed only after Phase 7D is accepted.

## Role

Work as the lead domain-engine, policy-evaluation, deterministic-assessment and scenario-snapshot engineer for Konsider.

Use synthetic or staged test data only.

Do not activate production TFC data, expose final API behavior or add UI.

## Objective

Implement the generic TFC assessment engine that evaluates an explicit effective profile context against immutable destination rules/evidence.

Preserve canonical country ranking and all existing assessments.

## Domain ownership

The domain service owns:

- profile/scenario normalization;
- input sufficiency;
- TFC applicability;
- destination support;
- effective-date selection;
- route/rule evaluation;
- scenario metric calculation;
- reason codes;
- optional explicit feasibility filtering;
- assessment summaries.

FastAPI routes and React components must not own these rules.

## Effective context normalization

Normalize:

- country/citizenship codes;
- occupation taxonomy/version;
- qualifications;
- currencies;
- dates/years;
- household composition;
- scenario intent;
- target locality;
- selected TFCs.

Do not invent missing values.

Produce an immutable effective-context snapshot and hash.

The hash must avoid exposing raw personal values in logs.

## Input sufficiency

For each selected TFC:

1. resolve input requirements;
2. determine which are satisfied;
3. return structured missing-input requirements;
4. do not evaluate substantive outcome when blocking inputs are absent;
5. allow partial explanatory evaluation only when policy explicitly permits it.

A missing job offer must be represented as “no job offer” only if the user explicitly provided that value. Otherwise it is unknown.

## Evaluation order

A suggested deterministic order:

1. validate request and context;
2. resolve selected/applicable TFCs;
3. resolve destination support;
4. resolve jurisdiction and effective date;
5. evaluate input sufficiency;
6. evaluate type-specific policy;
7. assemble per-TFC outcome;
8. assemble country feasibility assessment;
9. optionally apply explicit permitted feasibility filtering;
10. preserve base ranking and survivor order.

Document and test the final order.

## Route/rule engine

Implement only the condition vocabulary required by approved first-wave TFCs.

Support deterministic conditions such as:

- equality/set membership;
- numeric minimum/maximum/range;
- boolean requirement;
- presence/absence;
- date/age range;
- occupation/taxonomy membership;
- qualification level;
- jurisdiction;
- AND/OR groups where required;
- conditional requirement.

Avoid a Turing-complete or arbitrary expression engine.

For each route return:

- evaluated conditions;
- met;
- unmet;
- unknown;
- blocking;
- route match classification;
- source/effective date.

## Multiple routes

A TFC may evaluate multiple routes.

Define deterministic aggregation:

- at least one clear match;
- one or more conditional matches;
- no supported route matched;
- input required;
- insufficient destination evidence;
- unsupported.

Do not discard route-level detail.

Do not describe “no supported route matched” as impossible immigration or permanent ineligibility.

## Scenario metric engine

For approved metric TFCs support:

- versioned formula;
- components;
- units;
- currency;
- period;
- ranges;
- rounding;
- missing components;
- assumptions;
- exchange-rate policy only if approved;
- locality selection;
- confidence/quality.

Do not convert a metric to a 1–10 score unless Phase 7B and owner approval explicitly froze the transform.

## Country and response assessments

Produce:

- profile context present/absent summary;
- selected TFCs;
- evaluated/input-required/unsupported counts;
- per-country TFC outcomes;
- matched-route counts;
- scenario metric summaries;
- source/effective-date warnings;
- base rank;
- optional filtered rank;
- explicit no-change affinity score.

## Optional feasibility filtering

Default behavior is assessment-only.

Permit post-ranking filtering only when:

- a TFC definition explicitly allows it;
- the user explicitly requests it;
- the TFC is a route/rule type with approved match semantics;
- survivor order is stable from base ranking;
- affinity scores and base ranks remain unchanged;
- input-required/insufficient/unsupported handling is visible and policy-defined.

Prefer modes such as:

- `ASSESS_ONLY`;
- `REQUIRE_SUPPORTED_MATCH`.

Do not allow metric thresholds as filters in Phase 7 unless explicitly approved.

## Interaction invariants

Test that:

- TFC evaluation does not change weights;
- TFC evaluation does not change contributions;
- TFC evaluation does not change affinity;
- TFC evaluation does not change PCC unions;
- TFC evaluation does not change LSC aggregation;
- TFC evaluation does not change OFC states;
- explicit feasibility filtering preserves survivor order;
- turning TFCs off returns canonical existing ranking payloads.

## Scenario snapshots

Define a result snapshot containing:

- active release ID;
- TFC policy/source versions;
- effective profile context hash;
- selected TFCs;
- evaluation date;
- base ranking reference;
- TFC outcomes;
- assumptions;
- warnings.

Snapshots are returned to the client but not persisted server-side.

Do not put raw profile fields into diagnostic IDs.

## Synthetic golden scenarios

Create golden tests for:

- no profile context;
- partial profile;
- complete work scenario;
- study scenario;
- family scenario;
- matched route;
- conditional route;
- no supported route;
- input required;
- unsupported country;
- stale rule;
- regional rule;
- metric range;
- two TFC kinds active;
- explicit feasibility filter;
- no matches;
- OFC selected alongside TFC;
- PCC and LSC active alongside TFC;
- tie-preserving filtered order.

## Performance and safety

Measure assessment cost across:

- 91 countries;
- approved first-wave TFC count;
- multiple routes;
- scenario metrics.

Avoid uncontrolled rule explosion.

No request body or profile field may be logged.

Error messages must identify field IDs, not echo sensitive values.

## Required outputs

- TFC assessment domain service;
- context normalization;
- input-sufficiency evaluator;
- approved typed evaluators;
- scenario snapshot;
- optional filtering engine;
- golden tests;
- invariance tests;
- performance report;
- product/domain documentation;
- Phase 7E implementation report.

## Explicit non-goals

Do not:

- onboard production source data;
- activate release;
- expose final API/UI;
- persist profiles;
- implement login;
- use LLM reasoning;
- introduce arbitrary rules DSL;
- change base ranking.

## Commit

Use a focused commit such as:

`feat: implement typed feasibility assessment engine`

## Stop condition

Stop when synthetic/staged golden scenarios pass and all ranking/OFC/locality invariants hold.

Report:

- evaluation order;
- result types;
- filtering behavior;
- performance;
- invariance results;
- files changed;
- tests run;
- commit SHA;
- blockers before Phase 7F.


---

# Konsider Phase 7F — First-Wave TFC Evidence and Policy Onboarding

## Dependency

Proceed only after:

- Phase 7E is accepted;
- the Phase 7B first-wave list remains approved;
- exact source, legal, coverage and public-interpretation decisions are frozen.

## Role

Work as the lead source-adapter, rule-normalization, evidence-policy, immutable-release and research-to-production reconciliation engineer for Konsider.

## Objective

Productionize the approved first-wave TFCs into staged immutable release artifacts.

Onboard at least three and no more than five TFCs unless the owner explicitly approves a different count.

Do not activate the release or expose API/UI behavior.

## First-wave scope

Read the Phase 7B owner decision. Do not substitute candidates.

For each approved TFC freeze:

- stable TFC ID;
- public name;
- original criterion mapping;
- check kind;
- supported profile boundary;
- supported destination boundary;
- required inputs;
- source route;
- evaluation policy;
- effective-date policy;
- public limitations;
- filter capability;
- refresh cadence.

If a previously approved TFC fails production reconciliation, hold it and re-evaluate the minimum-three gate.

Do not onboard a replacement automatically.

## Production source promotion

Convert approved research logic into production modules.

Reuse:

- exact source identities;
- captured lawful inputs;
- mappings;
- jurisdiction tables;
- route IDs;
- formulas;
- thresholds;
- effective dates;
- conflict policies;
- country support states.

Do not import research scripts as runtime dependencies.

## Evidence/rule completeness

For every first-wave TFC:

- include one explicit destination support record for each of 91 countries;
- include all supported routes/rules or formula components;
- include unsupported/insufficient/stale/legal-block reason;
- include source and effective date;
- include policy version;
- include refresh metadata.

Do not generate profile outcomes in the release.

## Source/legal manifest

Retain:

- authority/publisher;
- exact source;
- URL/API/document ID;
- edition/version;
- extraction/verification date;
- effective period;
- checksum where lawful;
- byte count where applicable;
- licence/terms;
- attribution;
- normalized derivative conclusion;
- raw retention policy;
- refresh cadence;
- change detection;
- manual-review requirements;
- production-use decision.

## Research-to-production reconciliation

For each TFC compare production artifacts with approved Phase 7B research:

- country support state;
- route/rule inventory;
- input requirements;
- effective dates;
- thresholds/formulas;
- jurisdiction mapping;
- public limitations;
- sample synthetic outcomes.

Any mismatch fails unless explicitly documented and owner-approved.

## Commit and release discipline

Prefer:

- one TFC per commit; or
- one inseparable source family per commit.

Create a staged candidate release only after each approved TFC independently passes.

Do not mutate active release files.

## Tests

At minimum:

- source checksum/identity;
- parser fixtures;
- jurisdiction/country mapping;
- route uniqueness;
- effective-date validity;
- support completeness across 91 countries;
- required input alignment;
- policy evaluation against synthetic profiles;
- expected research support counts;
- legal-block handling;
- stale handling;
- no profile data in artifacts;
- no ranking fields;
- no OFC fields;
- deterministic no-diff regeneration;
- research-production reconciliation;
- existing full regression suite.

## Documentation

For each TFC document:

- user question;
- exact construct;
- required inputs;
- supported profiles;
- supported destinations;
- source;
- evaluation policy;
- result interpretation;
- effective date;
- limitations;
- refresh;
- replay;
- examples using synthetic profiles.

## Failure handling

If onboarding leaves fewer than three production-valid TFCs:

- stop;
- do not continue to API/UI;
- do not activate a release;
- document why the gate failed;
- return to owner decision.

## Required outputs

1. production source manifests;
2. production parsers/mappers;
3. first-wave TFC catalog definitions;
4. destination support records;
5. rule/evidence/formula bundles;
6. evaluation policies;
7. source/legal manifest;
8. reconciliation report;
9. staged candidate release;
10. deterministic build/replay;
11. tests/documentation;
12. Phase 7F implementation report.

## Explicit non-goals

Do not:

- activate release;
- add API fields;
- add UI;
- persist profile data;
- implement login;
- expand beyond owner-approved TFCs;
- add unsupported nationality/occupation assumptions;
- change ranking/OFC/PCC/LSC behavior.

## Commit

Use focused commits such as:

- `data: onboard <TFC name>`
- `data: assemble Phase 7 TFC candidate release`

## Stop condition

Stop when at least three first-wave TFCs are staged, reconciled and deterministic.

Report:

- exact TFC list;
- source routes;
- destination support;
- policy versions;
- staged artifact IDs;
- discrepancies;
- tests/replay;
- files changed;
- commit SHAs;
- blockers before Phase 7G.


---

# Konsider Phase 7G — Stateless Profile Context and TFC API

## Dependency

Proceed only after Phase 7F has a valid staged candidate containing at least three production TFCs.

## Role

Work as the lead API-domain integration, OpenAPI, privacy-safe transport and generated-client engineer for Konsider.

## Objective

Expose additive, typed API v2 support for:

- profile context;
- household context;
- exploration scenario;
- selected TFCs;
- input requirements;
- TFC catalog;
- per-country feasibility outcomes;
- optional explicit supported-match filtering;
- scenario snapshot metadata.

Do not activate the final release or add UI.

## Compatibility principle

Existing clients that send no profile/TFC fields must receive semantically identical ranking, OFC, coverage and locality behavior.

Prefer additive API v2 evolution if clean and compatible.

Introduce a new major API only if current contracts cannot represent the change without ambiguity.

Document the decision.

## Request contract

Support explicit request fields conceptually equivalent to:

```json
{
  "preference_preset_id": null,
  "weights": {},
  "opportunity_filter_ids": [],
  "profile_context": {},
  "household_context": {},
  "scenario_context": {},
  "tfc_ids": [],
  "feasibility_mode": "ASSESS_ONLY"
}
```

Exact nesting may differ.

Rules:

- no hidden account lookup;
- omitted profile means no profile context;
- unknown values remain unknown;
- selected TFCs are explicit;
- scenario purpose may drive recommended TFCs but must not silently activate them unless the contract clearly reports resolved selection;
- no profile values in query strings.

Prefer POST for profile-bearing assessments.

## Catalog and input requirements

Expose:

- available TFCs;
- check kinds;
- public descriptions;
- limitations;
- supported profile/destination boundaries;
- required and conditional inputs;
- field definitions;
- sensitivity/retention hints;
- source/effective-date summary;
- filter capability;
- sort/group order.

The UI must derive forms and labels from the API/catalog where practical.

Do not expose internal legal notes or sensitive operational data.

## Response contract

Return:

- existing ranking payload;
- profile-context summary;
- selected/resolved TFCs;
- response-level feasibility assessment;
- per-country TFC outcomes;
- input-required details;
- matched route summaries;
- scenario metric results;
- source/effective dates;
- warnings/limitations;
- base rank;
- optional filtered rank;
- snapshot/policy versions.

Do not change affinity scores.

## Endpoints

Evaluate the smallest clean surface, such as:

- catalog endpoint includes TFC definitions and field registry;
- ranking endpoint accepts profile/TFC context;
- country details include TFC evidence/result for the current request;
- comparison endpoint accepts the same context;
- optional validation/requirements endpoint only if it materially improves progressive forms.

Avoid duplicating evaluation rules across endpoints.

## Privacy and logging

Ensure:

- request bodies are not logged;
- validation errors do not echo sensitive values;
- profile context is not included in URLs;
- caches do not cross-contaminate profile-specific responses;
- response cache policy is private/no-store where required;
- traces contain IDs and timings, not raw profile values;
- server does not persist profile requests;
- health/metrics do not expose profile content.

Review framework defaults and reverse-proxy behavior.

## Errors

Add stable typed errors for:

- invalid profile field;
- unsupported taxonomy version;
- selected TFC unavailable;
- input missing;
- unsupported feasibility mode;
- stale/unavailable TFC bundle;
- candidate release unavailable.

Input missing for a TFC should normally be a successful assessment outcome, not an HTTP failure.

## OpenAPI and generated client

Regenerate:

- OpenAPI;
- TypeScript client/types;
- fixtures;
- contract snapshots.

Do not hand-write duplicate frontend types.

## Tests

Add tests for:

- no-profile backward compatibility;
- profile request validation;
- unknown versus false/none;
- required input responses;
- route result serialization;
- metric result serialization;
- unsupported destination;
- multiple TFC kinds;
- explicit filter mode;
- base-rank invariance;
- OFC + TFC;
- PCC + LSC + TFC;
- country details/comparison consistency;
- no profile data in logs;
- no-store/private caching;
- generated client parity;
- staged candidate unavailable.

## Documentation

Update:

- API guide;
- OpenAPI examples using fictional profiles;
- privacy behavior;
- field registry;
- feasibility modes;
- result interpretation;
- migration/compatibility;
- no-login/no-persistence boundary.

## Explicit non-goals

Do not:

- activate release;
- add UI;
- persist profile data;
- add login;
- add saved profiles;
- add chat;
- change base ranking;
- infer TFC selection invisibly.

## Commit

Use a focused commit such as:

`feat: expose stateless TFC assessment API`

## Stop condition

Stop when API, OpenAPI, generated client and compatibility tests pass against the staged candidate.

Report:

- endpoint/request/response decisions;
- privacy controls;
- compatibility;
- tests;
- generated artifacts;
- files changed;
- commit SHA;
- blockers before Phase 7H.


---

# Konsider Phase 7H — Guest-First Profile and Feasibility UI

## Dependency

Proceed only after Phase 7G is accepted and generated client types are current.

## Role

Work as the lead product UX, React/TypeScript, accessibility and privacy-conscious browser-state engineer for Konsider.

## Objective

Add a guest-first “Your situation” experience that lets users:

- enter only relevant profile/scenario facts;
- select or confirm TFCs;
- see missing-input requests;
- view feasibility results separately from affinity and OFCs;
- retain context for the session;
- optionally remember it on the device;
- clear/export/import it;
- use Konsider without login.

Do not implement authentication or server persistence.

## Main-page information architecture

Keep the existing ranking usable without profile context.

Add compact summaries such as:

- **Priorities** — ordering weights;
- **Opportunity** — selected OFCs;
- **Your situation** — applicant/household/scenario summary;
- **Feasibility checks** — selected TFCs and status.

Do not display a permanent 20-field form beside ranking controls.

Use a guided drawer/modal/page flow.

## Progressive disclosure

The UI should:

1. ask the exploration purpose;
2. show relevant available TFCs;
3. ask only fields required by those TFCs;
4. distinguish required, optional and unknown;
5. show why a field is requested;
6. allow “I don’t know” where supported;
7. show an assumptions summary before or with results;
8. request additional data when a country/TFC needs it.

Do not infer omitted answers.

## Profile/scenario separation

Present stable facts separately from scenario assumptions.

Examples:

### Applicant

- citizenship;
- occupation;
- qualifications;
- experience;
- languages.

### Household

- accompanying partner;
- dependants;
- child ages where relevant.

### Scenario

- work/study/family purpose;
- job offer and salary;
- intended course;
- target year;
- cities;
- housing/budget assumptions.

Allow the same applicant profile to be reused with different local scenarios in browser state.

## TFC selection

Use API/catalog-driven labels and grouping.

The UI may recommend checks based on purpose, but must clearly show which checks will run.

Do not silently activate consequential checks.

Support:

- select/unselect;
- required-input indicator;
- source/effective-date indicator;
- assessment-only versus explicit filter capability.

## Results presentation

Keep separate visual concepts:

- affinity score and base rank;
- OFC evidence;
- TFC feasibility;
- locality compatibility.

Examples:

- “Strong technology ecosystem”
- “Supported skilled-work route match found”
- “More salary information required”
- “No supported route matched under the currently modelled routes”
- “Destination evidence unavailable”
- “Estimated employee tax and contribution range”

Never show:

- “You can immigrate”
- “Visa guaranteed”
- “You cannot move”
- “No jobs”
- “Admission likely”

## Country detail and comparison

Show:

- selected TFCs;
- match/condition details;
- missing inputs;
- assumptions;
- routes evaluated;
- source/effective date;
- limitations;
- metric components;
- base rank and optional filtered rank;
- relation to OFCs where useful.

Comparison must use one consistent effective profile/scenario snapshot.

## Explicit feasibility filtering

Default to assessment-only.

Where the API permits route-match filtering, provide an explicit control such as:

> Show only destinations with a supported route match

Explain:

- base affinity is unchanged;
- countries may be hidden due to the selected feasibility mode;
- input-required/unsupported handling;
- how to restore the base list.

Do not apply hidden filtering.

## Browser state and retention

### Default

- memory for current page/app session;
- session retention may be used where approved;
- no automatic persistent local storage.

### Remember on this device

Require explicit opt-in.

Show:

- what is stored;
- that it is stored on this device/browser;
- expiration/version behavior;
- clear action;
- shared-device caution.

Do not claim browser storage is equivalent to secure account storage.

### Clear/export/import

Provide:

- clear current situation;
- clear remembered data;
- export as versioned JSON;
- import with validation and preview.

Do not include assessment results in export unless explicitly designed.

Never include profile data in URLs.

## Multiple scenarios

Support a bounded local experience if practical:

- one active applicant/household context;
- a small number of named local scenarios;
- duplicate scenario;
- compare scenario summaries.

Do not build a full persistence platform.

## Accessibility

Ensure:

- keyboard flow;
- proper labels/descriptions;
- error association;
- screen-reader announcements;
- no color-only status;
- mobile responsiveness;
- focus management;
- accessible modal/drawer;
- understandable reason text.

## Analytics and privacy

Do not send raw field values to analytics.

If event analytics exist, allow only coarse events such as:

- profile flow opened;
- TFC selected;
- assessment requested;
- local retention enabled.

Review and document.

## UI tests

At minimum:

- ranking works without profile;
- open/cancel profile flow;
- progressive field requirements;
- unknown value behavior;
- selected TFC summary;
- input-required result;
- route result;
- metric result;
- OFC + TFC display;
- country detail;
- comparison;
- explicit filter/undo;
- session restoration;
- opt-in local retention;
- clear;
- export/import;
- schema-version mismatch;
- mobile;
- keyboard/screen reader semantics;
- API error;
- unavailable candidate/release.

No UI-side eligibility logic.

## Documentation

Update:

- UI guide;
- privacy/retention help;
- screenshots/test plan if repository convention supports them;
- user-facing limitations;
- developer state ownership.

## Explicit non-goals

Do not:

- add login;
- add account settings;
- add server persistence;
- add chat;
- add hidden profile inference;
- add UI-side TFC rules;
- change ranking.

## Commit

Use a focused commit such as:

`feat: add guest profile and TFC experience`

## Stop condition

Stop when the guest flow, local/session retention, details, comparison, accessibility and tests pass against the staged API.

Report:

- UX flow;
- retention behavior;
- privacy behavior;
- test results;
- screenshots/evidence where applicable;
- files changed;
- commit SHA;
- blockers before Phase 7I.


---

# Konsider Phase 7I — OFC, Locality and TFC Integration with End-to-End Scenarios

## Dependency

Proceed only after Phase 7H is accepted.

## Role

Work as the lead cross-feature domain verifier, product-explanation engineer and end-to-end test owner for Konsider.

## Objective

Prove that profile/TFC behavior composes correctly with:

- ordering criteria;
- PCC uncertainty;
- locality-derived criteria and locality compatibility;
- Opportunity Filters;
- country comparison;
- browser scenario state.

Do not activate the final release yet.

## Orthogonality matrix

Create and test a matrix covering:

| Dimension | Must remain independent |
|---|---|
| Affinity | TFCs do not change weights, contributions or scores |
| Coverage | TFCs do not change FCC/PCC missing unions |
| Locality | TFCs do not change locality aggregation |
| Opportunity | TFCs do not change OFC states |
| Profile | Context presence does not imply every TFC is evaluated |
| Feasibility | TFC results may explain or explicitly filter only under approved mode |

## Required combined scenarios

At minimum:

### Career ecosystem + work route

- technology OFC verified;
- work-route TFC matched;
- work-route TFC conditional;
- no supported route matched;
- input required;
- OFC insufficient but TFC route matches.

### Care ecosystem + licensing

- care-sector OFC verified;
- licensing TFC matched/conditional;
- licensing evidence unsupported;
- regional regulator;
- language/qualification input required.

### Education ecosystem + student/post-study route

- education OFC verified;
- student/post-study route match;
- admission inputs intentionally not evaluated;
- intended degree missing;
- source/effective-date warning.

### Locality + household

- active LSCs with common locality;
- no common locality;
- target city supplied;
- housing or cost metric uses the selected locality;
- target city unsupported;
- country result preserved while locality advice differs.

### PCC + TFC

- active PCC excludes countries from R1;
- TFC outcomes remain inspectable where evidence exists;
- no fabricated aggregate score;
- feasibility filtering does not revive countries excluded from complete-case ranking unless product policy explicitly defines a separate view;
- base R0/R1 semantics remain clear.

### Multiple scenarios

- same applicant, solo move;
- same applicant, family move;
- same applicant, study scenario;
- results use different scenario snapshots without mutating the applicant facts.

## Explanation policy

Create consistent explanation ordering:

1. country attractiveness/base rank;
2. coverage uncertainty;
3. locality compatibility;
4. opportunity ecosystem;
5. personal feasibility;
6. assumptions and missing inputs.

Avoid contradictory-looking statements.

Provide approved templates for:

- strong ecosystem but access conditions unmet;
- no broad ecosystem signal but a supported route exists;
- destination attractive but current supported route not matched;
- route matched but locality/housing trade-offs remain;
- evidence unavailable;
- more input required.

## Comparison semantics

Ensure country comparison:

- uses one effective context snapshot;
- exposes per-country TFC differences;
- shows source/effective dates;
- shows base rank;
- shows optional filtered rank;
- does not compare missing metrics as zero;
- preserves OFC and criterion evidence separately.

## Golden end-to-end fixtures

Use fictional profiles.

Cover at least:

- work applicant;
- regulated professional;
- international student;
- family relocation;
- missing input;
- unsupported destination;
- two TFC kinds;
- OFC strict AND;
- PCC active;
- two LSCs;
- explicit feasibility filter;
- mobile UI.

## Regression verification

Run:

- backend unit/integration;
- schema validation;
- release replay;
- OpenAPI generation;
- frontend unit/component;
- browser E2E;
- accessibility;
- clean-checkout;
- Windows/Linux CI where available.

Confirm no change to canonical ranking payloads for requests without profile/TFC context.

## Documentation

Create/update:

- cross-feature behavior guide;
- explanation glossary;
- end-to-end scenario matrix;
- UI test plan;
- Phase 7I verification report.

## Explicit non-goals

Do not:

- activate final release;
- add new TFCs;
- change first-wave policy;
- implement login/persistence/chat;
- change base ranking.

## Commit

Use a focused commit such as:

`test: verify TFC cross-feature integration`

## Stop condition

Stop when all combined scenarios and regression suites pass.

Report:

- invariance results;
- scenario matrix;
- explanation decisions;
- failures and fixes;
- tests/CI;
- files changed;
- commit SHA;
- owner decisions before Phase 7J.


---

# Konsider Phase 7J — Release Activation, Privacy Verification and Phase Closure

## Dependency

Proceed only after:

- Phase 7I is accepted;
- at least three production TFCs remain valid;
- staged release/replay passes;
- owner approves activation.

## Role

Work as the lead release, compatibility, privacy-verification, documentation and phase-closure engineer for Konsider.

## Objective

Publish and atomically activate the immutable Phase 7 release containing the approved first-wave TFC destination evidence and policies.

Close Phase 7 with complete verification, documentation, rollback and roadmap updates.

## Pre-activation checks

Verify:

- staged artifact checksums;
- catalog validity;
- one explicit support state per TFC-country pair;
- rule/evidence/formula validity;
- effective dates;
- source/legal manifests;
- research-production reconciliation;
- deterministic replay;
- active pointer unchanged during candidate verification;
- API/UI against candidate;
- minimum-three gate;
- owner-approved TFC list.

## Ranking and OFC invariance

For requests without profile/TFC context, prove:

- identical criterion catalog behavior;
- identical weights;
- identical affinity scores;
- identical base ranks;
- identical PCC behavior;
- identical locality behavior;
- identical OFC states and filtering;
- compatible API response semantics.

Where byte-for-byte identity is not possible due to additive release metadata, prove field-level semantic identity and document the difference.

## Profile/TFC verification

Verify:

- no login required;
- no server-side persistence;
- no profile data in release artifacts;
- no profile request-body logging;
- no profile values in URLs;
- no raw profile analytics;
- session/device retention is explicit;
- clear/export/import work;
- scenario snapshots identify release and policy versions;
- source/effective dates are visible;
- input-required and unsupported states are honest;
- no legal/visa/admission guarantee wording.

## Release process

Follow repository conventions:

1. build from clean checkout;
2. validate candidate;
3. replay offline;
4. run full tests;
5. generate release report;
6. publish immutable directory;
7. update active pointer atomically;
8. restart/reload runtime as required;
9. run smoke tests;
10. preserve rollback to prior release.

Do not mutate prior releases.

## Closure report

Create `docs/history/phase7-closure-report.md` covering:

- product decision;
- TFC terminology;
- research funnel;
- production-qualified and onboarded TFCs;
- supported profile/destination boundary;
- data model;
- privacy and retention;
- worker/release;
- engine;
- API;
- UI;
- OFC/locality integration;
- verification;
- limitations;
- risks;
- refresh/maintenance;
- next phase.

## Release report

Record:

- release ID;
- schema/catalog versions;
- TFC IDs and names;
- source/policy bundle versions;
- country support counts;
- checksums;
- replay command;
- compatibility;
- rollback;
- known limitations.

## Roadmap decision

Recommend the next phase based on evidence.

Authentication/persistent profiles should become the next phase only if Phase 7 demonstrates that:

- profile entry produces meaningful value;
- users would benefit from saving multiple profiles/scenarios;
- losing local data is a real product problem;
- privacy/security work is justified.

Otherwise prioritize:

- second-wave TFC research;
- deeper locality/occupation support;
- source refresh and maintenance;
- usability improvements.

Conversational exploration remains later and must consume structured deterministic tools.

## Cleanup

Remove:

- transitional contract aliases;
- unused staged-only paths;
- obsolete synthetic active-path switches;
- duplicate frontend types;
- dead research-to-runtime adapters.

Preserve:

- historical research;
- immutable releases;
- replay tools;
- source/legal evidence;
- migration documentation.

## Final verification

Run all repository-standard commands, including:

- backend tests;
- lint/format/type checks;
- schema validation;
- source/release replay;
- OpenAPI/type generation;
- frontend tests;
- browser E2E;
- accessibility;
- clean-checkout verification;
- CI status.

Document exact commands and results.

## Required outputs

1. immutable active release;
2. release report;
3. Phase 7 closure report;
4. updated roadmap/system architecture;
5. updated source/release/API/UI/privacy docs;
6. verification evidence;
7. rollback instructions;
8. clean commit history.

## Explicit non-goals

Do not add:

- authentication;
- server-side saved profiles;
- cross-device sync;
- chat;
- notifications;
- new unresearched TFCs.

## Commit

Use focused final commits such as:

- `release: publish Phase 7 TFC release`
- `docs: close Phase 7`

## Stop condition

Stop when the release is active, smoke-tested, rollback-capable and the closure report is complete.

Report:

- active release;
- exact TFC list;
- support coverage;
- compatibility/invariance;
- privacy verification;
- all commands/results;
- commit SHAs;
- remaining risks;
- recommended next phase.


---

# Phase 7 Owner Decision Checklist

Use this after Phase 7B and before Phase 7C.

## Terminology

- [ ] Approve **Typed Feasibility Check (TFC)**
- [ ] Approve user-facing language: Feasibility checks / Your situation / Your feasibility

## Minimum gate

- [ ] At least three TFCs are production-qualified
- [ ] No gate was weakened to reach three
- [ ] First wave contains no more than five unless explicitly justified

## First-wave scope

For each approved TFC:

- [ ] Stable ID
- [ ] Public name
- [ ] Original criterion mapping
- [ ] Exact user question
- [ ] Check kind
- [ ] Required profile inputs
- [ ] Scenario inputs
- [ ] Supported destination boundary
- [ ] Supported applicant boundary
- [ ] Source route
- [ ] Legal/reuse conclusion
- [ ] Effective-date/refresh policy
- [ ] Public limitation
- [ ] Assessment-only or explicit filtering capability

## Product behavior

- [ ] Guest use remains fully supported
- [ ] Profile context is optional
- [ ] No login in Phase 7
- [ ] No server-side profile persistence
- [ ] Browser memory/session is default
- [ ] Remember-on-device requires explicit consent
- [ ] TFCs do not change affinity
- [ ] TFCs do not change OFCs
- [ ] TFCs do not change PCC/LSC behavior
- [ ] Explicit feasibility filtering, if allowed, preserves base rank and score

## Privacy

- [ ] Only purpose-bound fields are requested
- [ ] Sensitive fields are optional
- [ ] Unknown values are not inferred
- [ ] No profile data in URLs
- [ ] No request-body logging
- [ ] No raw profile analytics
- [ ] Clear/export/import behavior approved
- [ ] Synthetic fixtures only

## Architecture

- [ ] Applicant profile, household and scenario are separate
- [ ] Evaluation uses an explicit immutable snapshot
- [ ] Destination rules/evidence are stored, not profile × country outcomes
- [ ] Future account persistence is an adapter, not a Phase 7 dependency
- [ ] Old releases remain immutable and inspectable

## Stop decision

- [ ] Proceed to Phase 7C
- [ ] Stop as research-only because fewer than three TFCs qualified
- [ ] Request targeted Phase 7B follow-up before deciding
