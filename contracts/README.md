# Konsider contracts

`contracts/schemas/v1` contains the immutable release-3/catalog-1 Draft 2020-12 contracts.
`contracts/schemas/v2` adds release-4/catalog-2 mixed-coverage envelopes and explicit
criterion-country outcomes. Unchanged source, observation, and score rows continue to validate
against v1. Producers own valid output; consumers negotiate compatible majors before joining or
serving records. Published schemas are not silently weakened to accept invalid historical data.

`contracts/schemas/v3` defines the active Phase 5/6 domain and release contract: release 5,
catalog 3,
canonical geographic entities, entity-neutral observations/scores, versioned locality policies,
replayable multiple-source lineage, preference presets, and API v2 assessment envelopes. Phase 6D
adds an optional release-5.1 Opportunity Filter binding plus standalone filter definition,
evidence, policy, source, coverage and future assessment contracts. The active release is
`2026-08-04.1` on release 5.1.

`contracts/schemas/v4` defines the inactive Phase 7 target contracts for applicant, household and
scenario context; immutable effective snapshots; field privacy metadata; the three-item first-wave
Typed Feasibility Check catalog; route/rule outcomes; and sibling profile/feasibility assessments.
Phase 7D adds bounded source/legal, jurisdiction, destination-support, route-rule, synthetic metric
formula, evaluation-policy, coverage, validation, semantic-diff and release-6 candidate contracts.
Phase 7E adds typed domain-assessment and non-persisted scenario-snapshot contracts. It does not
modify the active loader or OpenAPI surface, bind production evidence or activate a release. The
metric artifact and result family are proven with fictional data and are not a product-approved
metric TFC.

FastAPI-generated `/openapi.json` is authoritative for HTTP request, response, and error shapes. It
is generated from strict Pydantic transport models and exported at
`contracts/openapi/konsider-api-2.0.json`. Frontend types are generated from the same document.

- [Phase 5B target contracts](../docs/architecture/phase5b-target-contracts.md)
- [Release format](../docs/data/release-format.md)
- [API contract and examples](../docs/operations/api.md)
- [Phase 5H contract migration](../docs/product/phase5h-contract-migration.md)
- [Immutable release decision](../docs/architecture/decisions/001-immutable-release-artifacts.md)
- [Opportunity Filter contracts](../docs/architecture/opportunity-filter-contracts.md)
- [Opportunity Filter decision](../docs/architecture/decisions/010-opportunity-filters-as-filter-only-contracts.md)
- [Typed Feasibility Check contracts](../docs/architecture/tfc-contracts.md)
- [Profile and scenario contracts](../docs/architecture/profile-scenario-contracts.md)
- [TFC immutable release foundation](../docs/architecture/tfc-release-foundation.md)
- [TFC source workflow](../docs/operations/tfc-source-workflow.md)
- [TFC assessment engine](../docs/product/tfc-assessment-engine.md)
- [TFC assessment performance](../docs/product/tfc-assessment-performance.md)
