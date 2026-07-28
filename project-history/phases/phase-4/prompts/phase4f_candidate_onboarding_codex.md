# Prompt — Phase 4F: Candidate Source Onboarding and Immutable Release

## Intended for
Codex in the local Konsider repository.

## Inputs
- Approved Phase 4B PCC list.
- Phase 4C–4E implementation.
- Exact Phase 3 probe artifacts, source records, licensing conclusions, and missing-country outcomes.
- Current active release and retained local raw artifacts.

## Objective

Implement only the user-approved initial PCC candidates as production or explicitly experimental criteria under the new Phase 4 contract, then publish a new immutable release if every gate passes.

## Candidate order

Use the Phase 4B decision. The working hypothesis is:

1. C11 Overall job-market opportunity
2. C26 Financial protection from health costs
3. C08 School education quality as a second-wave experimental candidate
4. C53 remains reserve unless explicitly approved

Do not automatically implement all four.

## For each approved criterion

1. Freeze the exact source, edition, series/components, methodology, licence, attribution, parser version, freshness rule, and scoring method.
2. Preserve 91 explicit attempt outcomes.
3. Produce observations and scores only for valid countries.
4. Preserve missing/stale/invalid reasons.
5. Set coverage mode to `CONDITIONAL_COMPLETE_CASE`.
6. Require at least 82 valid countries.
7. Add component and sensitivity diagnostics.
8. Avoid broad labels that overclaim the source.
9. Add online and offline replay.
10. Add parser, scoring, validation, release, repository, engine, and API tests.

## Candidate-specific cautions

### C11

- Measures harmonised national labour-market outcomes, not vacancies or occupation-specific opportunity.
- Freeze the unemployment, employment-to-population, and labour-force-participation construction.
- Test component redundancy and weights.
- Preserve known non-valid countries.

### C26

- Label as financial protection from health costs, not total healthcare affordability.
- Do not imply migrant eligibility, premiums, quality, or waiting times.
- Preserve Ukraine's stale outcome unless a newer approved source resolves it.

### C08

- Freeze the exact schooling/learning construct before implementation.
- Do not treat the published schooling component as a percentage.
- Keep experimental status and model/mixed-year caveats.
- Preserve known non-valid countries.

### C53

- Do not enable merely because it fits the coverage model.
- It measures basic access, not safety, taste, continuity, or utility reliability.
- Require explicit user approval and discrimination evidence.

## Publication

- Publish only with a new release ID and new schema version.
- Do not modify historical releases.
- Keep global core criteria at 91/91.
- Validate the query-specific missing unions for the approved PCC set.
- Verify cross-platform checksums from a clean Git checkout/worktree.
- Move `active.json` only after all tests, replay, and catalog reconciliation pass.

## Deliverables

- source registrations and ingestion;
- new immutable release if valid;
- updated catalog;
- exact coverage report;
- replay and checksums;
- documentation and release history;
- no UI implementation.
