# Prompt — Phase 4E: API Contract and Integration

## Intended for
Codex in the local Konsider repository.

## Inputs
- Phase 4C contract support.
- Phase 4D domain/service implementation.
- Existing FastAPI v1 routes and typed error envelope.

## Objective

Expose uncertainty-aware ranking through the thin typed API without duplicating ranking, coverage, readiness, or robustness logic.

## Catalog changes

For each criterion expose:

- criterion ID and label;
- enabled/readiness status;
- coverage mode;
- valid-country count and stable denominator;
- coverage percentage;
- PCC activation threshold;
- experimental flag;
- concise caveat;
- optionally missing-country count, with full details available in ranking output.

## Ranking request

Keep the existing weight request semantics where possible.

- `top_k` defaults to 10.
- User weights continue to use the existing raw scale.
- Do not require the client to identify FCC/PCC.
- Do not let the client choose excluded countries.
- Consider an optional `include_baseline` flag only if the domain result is otherwise too large; default behavior must still provide enough metadata to explain uncertainty.

## Ranking response

Add typed fields for:

- stable universe size;
- eligible universe size;
- ranking coverage mode;
- active/ignored PCC;
- excluded countries;
- missing criteria and reason codes;
- uncertainty status;
- robustness K;
- Kth eligible score;
- potential excluded entrants;
- baseline top-K membership;
- policy version;
- warning/message code.

Keep ranked countries separate from excluded/unranked countries.

## Error behavior

Use stable structured codes, including:

- `coverage_limit_exceeded` only when the API contract chooses to represent the fallback as an error;
- preferably return a successful FCC baseline with structured coverage status rather than a transport error;
- preserve existing 422, 404, 503, and 500 behavior for unrelated failures.

## Compatibility

- Update API models and OpenAPI.
- Keep routes thin.
- Update generated or checked-in frontend types.
- Add integration and contract tests.
- Ensure old FCC-only requests produce semantically identical rankings plus additive uncertainty metadata.

## Deliverables

- API models/routes integration;
- OpenAPI update;
- contract tests;
- documentation examples for all uncertainty states;
- no source ingestion or UI implementation.
