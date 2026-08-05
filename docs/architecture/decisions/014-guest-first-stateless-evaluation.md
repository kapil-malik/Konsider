# ADR 014: Guest-first stateless evaluation

Status: accepted for Phase 7 contracts

Date: 2026-08-05

## Context

The first useful workflow does not require an account, while applicant and household facts are
consequential and create avoidable privacy obligations if retained by default.

## Decision

Phase 7 evaluation is guest-first and stateless on the server. The request supplies an effective
context; the response returns assessments; server profile persistence is `NONE`. Profile values are
prohibited in URLs, analytics and application logs. Authentication is outside Phase 7.

## Consequences

Refresh, retry and scaling do not depend on session state. Operational telemetry may record contract
versions and aggregate statuses, but never profile values or snapshot contents.

## Alternatives considered

Mandatory login and server sessions were rejected as unnecessary. A hidden account lookup was
rejected because it makes evaluation non-reproducible and violates explicit-context semantics.
