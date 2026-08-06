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
