# Konsider

Konsider is an evidence-backed country suitability and relocation project. The repository currently
implements the local data-refresh worker; the recommendation engine, APIs, React UI, retrieval, and
LLM/chat layers remain deferred.

## Current status

Published release `2026-07-20.2` contains six real-data criteria for the fixed 20-country experiment
set. It passes structural validation and the project gate because five criteria pass every
criterion-level product-readiness check:

- World Bank WDI population-weighted PM2.5 exposure;
- UNODC intentional homicide distributed through WDI;
- World Bank ICP-derived broad relative-cost bands;
- World Bank Women, Business and the Law legal-framework index; and
- an experimental three-component WDI infrastructure composite.

World Bank HNP UHC coverage has complete 20-country coverage but is not ready: its latest official
observation is 2021 and exceeds the configured three-year freshness limit. Passing the five-of-six
data gate does not mean every criterion is ready or that the deferred product stack has started.

The repository also retains a separate legacy ten-country fixture dataset. Those approximate scores
exist only for domain tests and examples; they are not substituted into real releases.

See [the release report](docs/release-2026-07-20.2.md), [source audit](docs/data-source-feasibility.md),
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
python -m konsider.ingestion.worker replay data\releases\2026-07-20.2
```

Rebuilding a candidate performs network downloads from registered official sources:

```powershell
python -m konsider.ingestion.worker refresh --release-id YYYY-MM-DD.N
```

## Repository layout

```text
apps/worker/                  worker deployment notes
data/fixtures/                legacy 10-country test/demo fixtures
data/raw/                     ignored local third-party bytes
data/releases/                immutable published releases and active pointer
docs/                         architecture, source, method, and release records
src/konsider/ingestion/       source registry, capture, parsers, scoring, validation
src/konsider/repositories/    local release publication adapter
tests/                        unit, integration, failure, publication, and replay tests
```

The example scorer under `src/konsider/domain` still consumes legacy fixtures; it is not a live
product engine and must not be presented as using release `2026-07-20.2`.
