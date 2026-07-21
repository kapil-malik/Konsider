# Local deployment

## Developer mode

The implemented local backend is:

```text
worker CLI -> data/raw + data/releases + active.json
Uvicorn FastAPI :8000 -> validated active local release
```

Start order:

1. Install the repository using [local setup](local-setup.md).
2. Use the existing active release or run the [worker](worker.md) with a new release ID.
3. Set `KONSIDER_CORS_ORIGINS` if a browser runs on another origin.
4. Start Uvicorn: `python -m uvicorn konsider.api.app:app --reload`.
5. Require `GET http://127.0.0.1:8000/api/v1/health` to return `200`.

Phase 2C will add:

```text
Vite React UI :5173 -> http://127.0.0.1:8000/api/v1
```

Use `http://localhost:5173` consistently or allow both `localhost` and `127.0.0.1` in
`KONSIDER_CORS_ORIGINS`. Vite's exact command will be documented after its package exists. The UI
must start after or tolerate temporary API unavailability.

The API loads one release snapshot. After any intentional `active.json` change, restart Uvicorn and
recheck health. The worker and API must never write the same published release directory.

## Packaged local demo

A packaged demo is not implemented. Native Python and future Vite processes are the normal
development path. Docker Compose may later bundle those processes as a convenience, but Docker is
not required and must not introduce a second publication or scoring implementation.
