# Data refresh worker application

The implemented local worker lives under `src/konsider/ingestion`. It captures registered World Bank
sources, writes source-neutral observations and attempts, runs structural and criterion-level
readiness validation, and atomically publishes only candidates with at least five ready criteria.

```powershell
$env:PYTHONPATH = "src"
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N
python -m konsider.ingestion.worker replay data\releases\2026-07-21.1
```

Active release `2026-07-21.1` is the LF packaging correction of `2026-07-20.2` and covers WDI PM2.5,
WDI/UNODC homicide, World Bank HNP UHC, ICP relative-cost
bands, WBL legal and economic equality, and an experimental WDI infrastructure composite. UHC is
present but non-ready because its latest official value is 2021. See
`docs/data-source-feasibility.md`, `docs/scoring-methodology.md`, and
`docs/release-2026-07-20.2.md`.

Raw third-party bytes remain local under ignored `data/raw/`; release history and metadata are
committed without the source payloads. No API, UI, retrieval, or chat runtime is implemented here.
