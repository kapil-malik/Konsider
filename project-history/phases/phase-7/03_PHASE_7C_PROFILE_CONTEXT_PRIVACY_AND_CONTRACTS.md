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
