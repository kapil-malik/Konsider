# Konsider contracts

`contracts/schemas/v1` contains the immutable release-3/catalog-1 Draft 2020-12 contracts.
`contracts/schemas/v2` adds release-4/catalog-2 mixed-coverage envelopes and explicit
criterion-country outcomes. Unchanged source, observation, and score rows continue to validate
against v1. Producers own valid output; consumers negotiate compatible majors before joining or
serving records. Published schemas are not silently weakened to accept invalid historical data.

`contracts/schemas/v3` defines the Phase 5 domain/release target: release 5, catalog 3, canonical
geographic entities, entity-neutral observations/scores, versioned locality policies, replayable
multiple-source lineage, preference presets, and API v2 assessment envelopes. The release
contracts and synthetic fixtures do not change the active production release.

FastAPI-generated `/openapi.json` is authoritative for HTTP request, response, and error shapes. It
is generated from strict Pydantic transport models and exported at
`contracts/openapi/konsider-api-2.0.json`. Frontend types are generated from the same document.

- [Phase 5B target contracts](../docs/architecture/phase5b-target-contracts.md)
- [Release format](../docs/data/release-format.md)
- [API contract and examples](../docs/operations/api.md)
- [API v2 contract and migration](../docs/operations/api-v2.md)
- [Immutable release decision](../docs/architecture/decisions/001-immutable-release-artifacts.md)
