# Konsider

Konsider is an evidence-backed country suitability and relocation project. The repository currently
implements the local data-refresh worker, the framework-independent recommendation engine, and the
Phase 2B typed FastAPI transport. React, retrieval, and LLM/chat layers remain deferred.

## Current status

Active release `2026-07-21.1` is a packaging-only correction of `2026-07-20.2` for portable LF
checksums. It contains the same six real-data criteria, observations, scores, and readiness
decisions for the fixed 20-country experiment set. Five criteria pass every
criterion-level product-readiness check:

- World Bank WDI population-weighted PM2.5 exposure;
- UNODC intentional homicide distributed through WDI;
- World Bank ICP-derived broad relative-cost bands;
- World Bank Women, Business and the Law legal-framework index; and
- an experimental three-component WDI infrastructure composite.

World Bank HNP UHC coverage has complete 20-country coverage but is not ready: its latest official
observation is 2021 and exceeds the configured three-year freshness limit. Passing the five-of-six
data gate does not mean every criterion is ready. The Phase 2A consumer excludes UHC automatically.

`RecommendationService` resolves and validates the active pointer, verifies every declared file
checksum, joins scores to observations and sources, and deterministically ranks all 20 countries.
It exposes catalog, ranking, comparison, and country-breakdown operations without a web framework.
The FastAPI adapter exposes those operations under `/api/v1` without duplicating their business
logic and reuses one validated immutable release snapshot for the process lifetime.

The repository also retains a separate legacy ten-country fixture dataset. Those approximate scores
exist only for domain tests and examples; they are not substituted into real releases.

See [the active release report](docs/release-2026-07-21.1.md), [source audit](docs/data-source-feasibility.md),
[scoring experiments](docs/scoring-methodology.md), and [roadmap](docs/roadmap.md).

## Worker guarantees

- Content-addressed raw bytes remain local under ignored `data/raw/`; committed release metadata
  retains exact URLs, HTTP metadata, timestamps, source versions, and SHA-256 checksums.
- Every observation points to the exact artifact and JSON record or workbook cell that produced it.
- Every expected source/country/criterion combination has a `success`, `no_data`, `failed`, or
  `rejected` attempt.
- Draft publication requires structural validity and at least five product-ready criteria.
- Published releases are immutable; corrections receive new IDs and earlier releases remain intact.

## Setup and verification

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -p "test_*.py"
python -m pytest -q
python -m konsider.ingestion.worker replay data\releases\2026-07-21.1
```

GitHub Actions runs the same backend gates on Ubuntu for every push and pull request:

```powershell
pytest
ruff check .
black --check .
python -m compileall -q src tests
```

Start the local API from any working directory after setting explicit paths when the checkout data
is not at its default location:

```powershell
$env:KONSIDER_RELEASE_ROOT = "C:\path\to\Konsider\data\releases"
$env:KONSIDER_ACTIVE_RELEASE_PATH = "$env:KONSIDER_RELEASE_ROOT\active.json"
$env:KONSIDER_CATALOG_PATH = "C:\path\to\Konsider\data\catalogs\consumer-catalog-1.0.json"
python -m uvicorn konsider.api.app:app --reload
```

The local source-checkout defaults are absolute and independent of the caller's working directory.
A process restart is deliberately required after changing `active.json`; Phase 2B does not poll or
hot-reload releases. See [the API reference](docs/api.md).

Minimal ranking example:

```python
from konsider.application import RecommendationService

service = RecommendationService()
result = service.rank({
    "ambient_pm25_population_weighted": 2,
    "intentional_homicide_rate": 3,
})
print(result["release_id"], result["rankings"][0])
```

Rebuilding a candidate performs network downloads from registered official sources:

```powershell
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N \
  --source-version world_bank_pm25=... # repeat for every registered source
```

## Repository layout

```text
apps/worker/                  worker deployment notes
data/fixtures/                legacy 10-country test/demo fixtures
data/raw/                     ignored local third-party bytes
data/releases/                immutable published releases and active pointer
data/catalogs/                versioned release-consumer catalog
contracts/schemas/v1/         machine-readable consumer JSON Schemas
docs/                         architecture, source, method, and release records
src/konsider/application.py   framework-independent recommendation services
src/konsider/api/             FastAPI factory, typed models, mappings, errors, settings
src/konsider/ingestion/       source registry, capture, parsers, scoring, validation
src/konsider/repositories/    release publication and read-only consumer adapters
tests/                        unit, integration, failure, publication, and replay tests
```

The legacy fixture scorer remains isolated for backward-compatible tests. It never fills, maps, or
relabels published-release data.
