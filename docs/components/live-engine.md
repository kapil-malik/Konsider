# Live Python Engine

## Responsibility

The live engine is the sole authority for user profiles, weight normalization, deterministic
rankings, evidence retrieval, and chat orchestration. It exposes versioned APIs to the website and
MCP tools later. It reads published releases only and never refreshes external sources during a
user request.

## Internal Layers

| Layer | Responsibility |
| --- | --- |
| Domain | Typed models, profile rules, weight normalization, scoring, contribution calculation |
| Services | Ranking, comparison, evidence retrieval, profile revision, conversation orchestration |
| Repositories | Interfaces and adapters for releases, metrics, evidence, profiles, and conversations |
| API | FastAPI routing, validation, authentication, serialization, streaming, and error mapping |
| Agents | LLM prompts and tool orchestration built on services; no independent scoring implementation |

The current `konsider.domain` package is intentionally framework-free and remains usable by tests,
the API, worker validation, CLI utilities, and future MCP adapters.

## REST API

All endpoints are rooted at `/api/v1`. FastAPI-generated OpenAPI is the canonical public contract.

### Catalog

`GET /api/v1/catalog` returns countries, metric definitions, default profiles, caveats, and the
active dataset release. The website uses it to construct controls and labels rather than embedding
the catalog in JavaScript.

### Ranking

`POST /api/v1/rankings` accepts editable non-negative weights, an optional profile template ID,
and `top_k`. The service:

1. Validates metric IDs and numeric bounds.
2. Completes omitted metrics with zero and normalizes the weights.
3. Pins the request to one active dataset release.
4. Computes totals and parameter contributions through the domain scorer.
5. Returns stable country IDs, display metadata, strengths, tradeoffs, versions, and evidence
   references.

Results may be cached by dataset version, scoring version, normalized-weight hash, and `top_k`.

### Evidence

`GET /api/v1/countries/{country_id}/evidence` supports metric/topic filters, pagination, and a
result limit. Each result includes an evidence ID, source label and URL when permitted, effective
and retrieval dates, excerpt, confidence, and dataset version.

## Chat API

`POST /api/v1/chat/sessions` creates a server-owned conversation and profile state. A message is
sent to `/api/v1/chat/sessions/{session_id}/messages` with the expected profile revision to prevent
lost updates.

The initial transport is SSE. Events have stable types such as:

```text
message.started
message.delta
tool.started
tool.completed
profile.proposed
profile.updated
ranking.updated
citation
message.completed
error
```

A profile event contains structured weights, the previous and new revision, and an explanation.
The React client updates sliders from this event; it never extracts weights from prose. Sensitive
or broad changes can be proposed for confirmation, while accepted changes create a new revision
that can be undone.

## Agent and Tool Boundary

The conversational layer may call these application tools:

- `get_profile`
- `propose_weights`
- `apply_weights`
- `rank_countries`
- `compare_countries`
- `search_evidence`
- `get_country_breakdown`
- `critique_recommendation`

Tools return typed results with release and scoring versions. LLM-generated text must cite returned
evidence IDs for factual claims. A template-based explanation remains available when no LLM is
configured or the provider fails.

## Technology

- Python 3.11 or newer and FastAPI.
- Pydantic API models separated from domain dataclasses where transport requirements differ.
- Uvicorn locally; a container deployed to App Runner or ECS Fargate initially.
- SSE for first chat streaming; API Gateway WebSockets only when bidirectional requirements justify
  the added connection-state machinery.
- LangGraph after the service/tool flow is stable, not as a prerequisite for ranking.
- OpenTelemetry-compatible tracing and structured logs.

## Security and Reliability

- LLM and storage credentials are server-side secrets.
- Authentication and authorization are enforced at API boundaries; anonymous sessions can be
  added as an explicit product policy.
- Rate, token, message-size, retrieval-count, and tool-call limits are applied per session.
- User text and retrieved web content are untrusted. Tools validate all arguments independently of
  model output.
- Request IDs, dataset versions, scoring versions, conversation IDs, and profile revisions appear
  in logs and responses.

## Testing Expectations

- Domain unit tests remain fast and have no network or framework dependency.
- Service tests use in-memory repositories.
- API contract tests validate status codes and schemas.
- Integration tests cover one published release and database adapters.
- Agent tests assert tool usage, citation presence, fallback behavior, and structured event order
  rather than exact prose.
