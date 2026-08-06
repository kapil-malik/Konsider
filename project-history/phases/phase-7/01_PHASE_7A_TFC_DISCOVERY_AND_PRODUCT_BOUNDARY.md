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
