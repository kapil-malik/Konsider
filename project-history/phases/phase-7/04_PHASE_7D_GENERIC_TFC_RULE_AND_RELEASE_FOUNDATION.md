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
