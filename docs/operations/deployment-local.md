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
5. Require `GET http://127.0.0.1:8000/api/v2/health` to return `200`.

Phase 2C adds:

```text
Vite React UI :5173 -> http://127.0.0.1:8000/api/v2
```

Use `http://localhost:5173` consistently or allow both `localhost` and `127.0.0.1` in
`KONSIDER_CORS_ORIGINS`. The UI tolerates temporary API unavailability and provides a retry action.

PowerShell, terminal 1:

```powershell
.venv\Scripts\Activate.ps1
$env:KONSIDER_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
python -m uvicorn konsider.api.app:app --reload
```

PowerShell, terminal 2:

```powershell
Set-Location web
pnpm install
pnpm run generate:api
pnpm run dev
```

Bash, terminal 1:

```bash
source .venv/bin/activate
KONSIDER_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173" \
  python -m uvicorn konsider.api.app:app --reload
```

Bash, terminal 2:

```bash
cd web
pnpm install
pnpm run generate:api
pnpm run dev
```

Vite defaults to `127.0.0.1:5173`; FastAPI defaults to `127.0.0.1:8000`. Configure another browser-
safe API base with `VITE_KONSIDER_API_BASE_URL`. See [web/README.md](../../web/README.md) for Node,
generation, test, build, and troubleshooting details.

### Windows background commands

After completing the Python installation and running `pnpm install` in `web`, these commands can be
run from the repository root:

```powershell
.\start-local.cmd
.\stop-local.cmd
.\restart-local.cmd
```

`start-local.cmd` starts Uvicorn on port 8000 and Vite on port 5173, enables CORS for both local UI
origins, waits up to 30 seconds for the API and UI, and then prints their URLs. `stop-local.cmd`
stops only processes whose PID and start time match the state recorded by the start command.
`restart-local.cmd` performs those operations in sequence.

The scripts use `.venv\Scripts\python.exe` and executables on `PATH` when available, verify that the
selected Python has Konsider and Uvicorn installed, and can use the Codex bundled runtime as a local
fallback. Executable paths can be overridden for a particular shell session:

```powershell
$env:KONSIDER_PYTHON = "C:\path\to\python.exe"
$env:KONSIDER_NODE = "C:\path\to\node.exe"
.\start-local.cmd
```

Runtime state and diagnostic output are kept under the ignored `.konsider-run` directory. Inspect
`api.err.log` or `ui.err.log` there if startup fails. These helpers intentionally do not install
dependencies, generate API types, run the ingestion worker, or modify the active release.

The API loads one release snapshot. After any intentional `active.json` change, restart Uvicorn and
recheck health. The worker and API must never write the same published release directory.

## Packaged local demo

A packaged demo is not implemented. Native Python and future Vite processes are the normal
development path. Docker Compose may later bundle those processes as a convenience, but Docker is
not required and must not introduce a second publication or scoring implementation.
