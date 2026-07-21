# Live API application

The implemented Phase 2B API is a thin FastAPI transport over `RecommendationService`. Run it with:

```powershell
python -m uvicorn konsider.api.app:app --reload
```

The application factory is `konsider.api.app.create_app`. It accepts explicit settings, an existing
service, or a service factory for deterministic tests. One active release is validated and loaded
during the application lifespan and reused for every request. Restart the process to adopt a newly
activated release.

The API never fetches upstream sources, reads raw artifact bytes, or falls back to legacy fixtures.
S3/Lambda deployment, authentication, chat, and UI code remain deferred. See `docs/api.md` and
`docs/components/live-engine.md`.
