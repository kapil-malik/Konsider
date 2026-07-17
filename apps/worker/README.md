# Data Refresh Worker Application

This directory is the deployment root for scheduled and manually triggered data refresh jobs. The
first local worker vertical slice is implemented under `src/konsider/ingestion`.

The worker should start as a normal Python executable that can run locally against a release
directory. Production can wrap the same code in a Lambda handler scheduled by EventBridge; scheduled
ECS Fargate is reserved for long-running or browser-heavy refreshes.

Run a replay of the first real-data release:

```powershell
$env:PYTHONPATH = "src"
python -m konsider.ingestion.worker replay data\releases\2026-07-17.1
```

Build a new local release from registered public sources:

```powershell
$env:PYTHONPATH = "src"
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N
```

The worker currently covers WHO air quality, UNODC-lineage homicide via WDI, WHO UHC, World Bank ICP,
and WPS. See `docs/data-source-feasibility.md`, `docs/scoring-methodology.md`, and
`docs/release-2026-07-17.1.md`.
