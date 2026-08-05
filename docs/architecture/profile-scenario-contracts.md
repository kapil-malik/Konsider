# Applicant, household and scenario contracts

Status: Phase 7C target contract

## Model

The profile context is three separate objects:

- `ApplicantProfile`: relatively stable facts such as citizenship, residence, occupation,
  experience, qualifications, registrations and language evidence;
- `HouseholdProfile`: partner status and participation, partner intent and anonymous dependent
  roles/age bands; and
- `ExplorationScenario`: destination, target date, purpose, offer, intended occupation or study,
  target region, relocation composition and selected TFCs.

A preference preset remains only a set of ranking weights. An account, saved profile or mutable UI
form is not an evaluation object.

## Unknowns and provenance

Every object has explicit `unknown_fields`. Unknown never means absent, false or failed. Supplied
fields carry field-level provenance: `USER_SUPPLIED`, `IMPORTED` or `DERIVED`, with capture time and
optional source-field references.

Occupation, field and institution references preserve user text and mapping state. A taxonomy code
is present only when a versioned mapping succeeds. Unresolved identity produces required-input or
insufficient-evidence behavior rather than a guessed mapping.

## Age decision

`age_years` evaluated at the scenario snapshot date is the standard input. Exact `date_of_birth` is
allowed only when a supported dated rule cannot be evaluated from age in years. Both cannot be
supplied together. Date of birth is never retained by default, never device-stored and omitted from
the default export.

Dependent age bands are preferred. Exact child ages are requested only for a supported rule that
cannot use the band. Names and document identifiers are outside the contract.

## EffectiveProfileContext

Before evaluation, normalized applicant, household and scenario values become an immutable
`EffectiveProfileContext`. It contains:

- all component schema versions;
- selected TFCs;
- resolved taxonomy versions;
- evaluation timestamp;
- retention/consent state; and
- a canonical SHA-256 snapshot hash.

The hash includes normalized values and taxonomy/schema versions. It excludes mutable client IDs,
the evaluation timestamp and retention choice. Identical effective facts therefore produce the same
snapshot identity. Editing an evaluated fact produces a new hash.

The request supplies this snapshot. No server persistence ID or account lookup is allowed.

## Future saved profiles

A later persistence adapter may save multiple applicants, households and scenarios with revisions,
ownership and import/export. It must resolve one explicit revision of each object into an effective
context before evaluation. Phase 7C adds no repository, database, authentication or CRUD service.
