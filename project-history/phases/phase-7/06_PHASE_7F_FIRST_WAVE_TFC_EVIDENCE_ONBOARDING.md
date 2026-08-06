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
