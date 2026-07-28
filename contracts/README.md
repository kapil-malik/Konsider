# Konsider contracts

`contracts/schemas/v1` contains the immutable release-3/catalog-1 Draft 2020-12 contracts.
`contracts/schemas/v2` adds release-4/catalog-2 mixed-coverage envelopes and explicit
criterion-country outcomes. Unchanged source, observation, and score rows continue to validate
against v1. Producers own valid output; consumers negotiate compatible majors before joining or
serving records. Published schemas are not silently weakened to accept invalid historical data.

FastAPI-generated `/openapi.json` is authoritative for HTTP request, response, and error shapes. It
is generated from the Pydantic transport models rather than hand-maintained here. Future frontend
types must be generated from or runtime-validated against OpenAPI.

- [Release format](../docs/data/release-format.md)
- [API contract and examples](../docs/operations/api.md)
- [Immutable release decision](../docs/architecture/decisions/001-immutable-release-artifacts.md)
