# Live API Application

This directory is the deployment root for the future FastAPI live engine. It will compose the
shared domain, application services, and repository adapters; expose the versioned REST and chat
contracts; and own server-side LLM orchestration.

The initial local runtime should be FastAPI/Uvicorn reading a local active release. The initial AWS
runtime should be API Gateway plus Python Lambda reading S3 release artifacts, with App Runner or
ECS considered only if Lambda constraints show up in measured usage.

No API runtime is implemented yet. See `docs/components/live-engine.md` and `docs/roadmap.md`.
