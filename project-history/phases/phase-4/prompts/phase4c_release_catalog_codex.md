# Prompt — Phase 4C: Release, Catalog, and Validation Contracts

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4A policy.
- Approved Phase 4B candidate selection.
- Current release `2026-07-27.1`.
- Existing release repository, validation, consumer catalog, and immutable-release rules.

## Objective

Extend Konsider's release and catalog contracts so a release can contain both globally complete ranking criteria and approved partial-coverage criteria without weakening structural validation.

Use fixture-backed PCC data in this phase. Do not ingest live candidate sources yet.

## Required contract model

Add a versioned criterion coverage mode, for example:

- `GLOBAL_CORE`
- `CONDITIONAL_COMPLETE_CASE`
- `DIAGNOSTIC_ONLY`

For each enabled criterion store or derive:

- coverage mode;
- stable universe ID and denominator;
- valid country count;
- minimum valid count;
- missing/stale/invalid country outcomes;
- PCC activation threshold;
- experimental status;
- source/scoring versions;
- allowed score range.

## Release behavior

1. `GLOBAL_CORE` criteria require 91/91 valid scores.
2. `CONDITIONAL_COMPLETE_CASE` criteria require at least 82/91 valid scores.
3. All 91 attempt outcomes must still be present for every published criterion.
4. Scores exist only for valid observations.
5. Missing, stale, invalid, and rejected observations remain explicit.
6. No validation path may treat absent score rows as valid without consulting the attempt/outcome record.
7. Product readiness requires the configured minimum number of global core criteria.
8. Historical releases and schemas remain immutable and loadable.
9. Publish a new schema version rather than rewriting release schema 3.0 in place.
10. Catalog and release validation must reconcile exactly.

## Validation requirements

Add checks for:

- criterion coverage mode;
- conditional minimum coverage;
- exact attempt completeness for all 91 countries;
- valid-score count reconciliation;
- country outcome reason codes;
- no score for non-valid observations;
- no missing attempt;
- activation threshold range;
- stable policy version;
- no PCC enabled when its valid count is below 82;
- global core remains 91/91;
- deterministic checksums and LF-normalised artifacts.

## Compatibility

- Preserve loading of the active schema-3 release.
- Add explicit schema negotiation or migration logic for the new release schema.
- Do not silently reinterpret an old criterion as PCC.
- Keep the API and engine behavior unchanged until later sub-phases use the new metadata.

## Tests

Add unit and integration tests for:

- one 91/91 FCC;
- one 88/91 PCC;
- mixed outcomes;
- insufficient 81/91 PCC;
- score/attempt mismatch;
- stale versus missing reason preservation;
- old release compatibility;
- new release checksum/replay;
- Windows/Linux byte stability.

## Deliverables

- schema and model changes;
- fixture release using the new contract;
- validation and repository support;
- tests;
- documentation;
- no active release pointer change.
