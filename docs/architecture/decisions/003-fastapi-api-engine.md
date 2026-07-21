# ADR 003: FastAPI API engine

Status: accepted and implemented locally

## Context

The deterministic recommendation service must remain independent of web transport and deployment.

## Decision

`RecommendationService` is the business-logic authority. FastAPI and Pydantic own the HTTP
transport, and generated OpenAPI is the contract authority. Uvicorn runs locally. Each process
reuses one validated immutable release snapshot.

The initial AWS target is API Gateway plus Lambda through an appropriate ASGI adapter. App Runner
or ECS becomes preferable only if cold starts, streaming, larger releases, long-lived requests, or
persistent caches justify containers.

## Consequences

Routes remain thin, startup can report controlled release failure, and frontend types should be
generated from or validated against OpenAPI. Pointer changes require process restart.

## Alternatives considered

Embedding business rules in routes and starting with a container service were rejected.

## Revisit when

Runtime measurements show Lambda unsuitable or API semantics require streaming or long-lived state.
