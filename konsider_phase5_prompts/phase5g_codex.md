# Phase 5G — Production Implementation of Approved Criteria

## Intended for
Codex in the local Konsider repository.

## Inputs
- user-approved Phase 5F decision
- exact approved sources, definitions, guardrails, and scoring rules

## Prompt

Implement only the approved Phase 5 criteria as production-grade Konsider criteria.

For each criterion:

1. Add an audited source registration with exact version, methodology, licence evidence, redistribution decision, attribution, limitations, and parser version.
2. Implement deterministic retrieval and parsing.
3. Produce source-neutral observations with exact provenance.
4. Implement the approved versioned scoring transformation.
5. Add criterion-specific readiness validation for coverage, freshness, units, types, flags, provenance, attempts, checksums, schemas, and versions.
6. Preserve missing, stale, rejected, and incomparable results explicitly.
7. Add sensitivity and redundancy diagnostics where required.
8. Add parser, mapping, scoring, readiness, failure, replay, publication, and catalog tests.
9. Publish a new immutable release only if all approved requirements pass.
10. Update source audit, scoring methodology, coverage report, release report, worker documentation, roadmap, and implementation history as needed.

Do not use fixture fallback, unapproved imputation, source substitution, silent partial scoring, duplicated API/UI business rules, or modification of historical releases.

Experimental criteria must remain visibly experimental, and non-ready criteria must remain excluded from ranking.
