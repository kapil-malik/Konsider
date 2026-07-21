# API component pointer

The implemented FastAPI application factory is `konsider.api.app.create_app`; the ASGI application
is `konsider.api.app:app`. Authoritative setup, configuration, lifecycle, routes, examples, and error
contracts are in [API operations](../../docs/operations/api.md). Architecture boundaries are in
[ADR 003](../../docs/architecture/decisions/003-fastapi-api-engine.md).
