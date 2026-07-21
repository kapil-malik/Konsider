# Konsider contracts

`contracts/schemas/v1` contains versioned Draft 2020-12 JSON Schemas for the active pointer, release
manifest, validation report, source registration, metric observation, metric score, and consumer
catalog. Producers own valid output; consumers reject incompatible major versions before joining or
serving records. Published schemas are not silently weakened to accept invalid historical data.

FastAPI-generated `/openapi.json` is authoritative for HTTP request, response, and error shapes. It
is generated from the Pydantic transport models rather than hand-maintained here. Future frontend
types must be generated from or runtime-validated against OpenAPI.

- [Release format](../docs/data/release-format.md)
- [API contract and examples](../docs/operations/api.md)
- [Immutable release decision](../docs/architecture/decisions/001-immutable-release-artifacts.md)
