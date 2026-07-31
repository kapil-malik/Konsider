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
