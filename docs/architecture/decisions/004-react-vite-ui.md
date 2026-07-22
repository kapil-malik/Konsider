# ADR 004: React and Vite UI

Status: accepted and implemented in Phase 2C

## Context

The Phase 2B API is stable and the next phase needs a small catalog-driven comparison interface.

## Decision

Use React, TypeScript, Vite, TanStack Query for server state, React state for editable weights,
OpenAPI-derived or runtime-validated API types, Vitest with React Testing Library, and limited
Playwright end-to-end coverage.

The UI obtains countries, criteria, profiles, labels, readiness, experimental flags, caveats, and
source metadata from the API. It never implements scoring or readiness rules. Local deployment is a
Vite development server calling local FastAPI. AWS static hosting uses S3 plus CloudFront; Amplify
Hosting remains an optional convenience.

## Consequences

CORS must explicitly allow the local UI origin. Browser state is intentionally non-persistent in
Phase 2C, and API contract drift must be caught by generated or validated types and tests.

## Alternatives considered

Server-rendered UI, Streamlit, hard-coded catalog data, and Amplify-only hosting were rejected for
this phase.

## Revisit when

Product requirements demand server rendering, durable accounts, offline behavior, or a different
deployment model.
