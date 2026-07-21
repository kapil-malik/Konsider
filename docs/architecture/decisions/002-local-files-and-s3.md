# ADR 002: Local files and S3

Status: accepted design; S3 deployment not implemented

## Context

The current dataset is small, immutable, and read as a complete snapshot. Mutable application state
does not yet exist.

## Decision

Local development uses `data/raw`, `data/releases`, and `data/catalogs`. Third-party raw bytes remain
ignored locally. Initial AWS storage will use S3 for raw artifacts, releases, catalogs, manifests,
and the active pointer. Observations and scores do not currently require SQL or DynamoDB.

DynamoDB is reserved for future profiles, sessions, quotas, conversations, or operational run
records. Vector storage is deferred until evidence volume and measured retrieval quality justify it.

## Consequences

The API can validate and load one release into memory. Production S3 needs versioning, encryption,
least-privilege IAM, lifecycle policy, and tested pointer rollback.

## Alternatives considered

SQL, DynamoDB for immutable metrics, and a vector database were rejected as premature complexity.

## Revisit when

Release size, query volume, mutable-state requirements, or measured retrieval needs exceed the file
and in-memory model.
