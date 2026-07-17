# Konsider

Konsider is an evidence-backed country suitability and relocation advisor. It produces personalized,
explainable country rankings from user priorities and is designed to grow into a system that
refreshes public evidence, serves deterministic rankings, and supports conversational exploration.

The repository is currently at the architecture-aligned Phase 1 foundation: fixture-backed country
data and a tested Python scoring domain. API, worker, React, retrieval, and LLM runtimes are planned
but intentionally not implemented in this structural change.

## Architecture

Konsider is organized around three independently deployable applications:

- A Python data refresh worker that builds versioned, validated dataset releases.
- A Python live engine that owns profiles, scoring, retrieval, chat tools, and public APIs.
- A React + Vite website that accesses only the live engine.

Start with [docs/architecture.md](docs/architecture.md). The component documents, storage design,
and current sprint sequence are linked from there and from [docs/roadmap.md](docs/roadmap.md).

## Current Capabilities

- Ten countries and ten comparison metrics.
- Complete fixture validation.
- Editable and normalized user weights.
- Three default profile templates.
- Deterministic weighted rankings.
- Parameter-level contribution breakdowns, strengths, and tradeoffs.
- Qualitative evidence fixture loading.

All current scores are approximate MVP fixtures and are not a source of truth for relocation
decisions.

## Repository Layout

```text
apps/
  api/                         # future FastAPI deployment root
  worker/                      # future data refresh deployment root
contracts/                     # future machine-readable shared contracts
data/
  fixtures/                    # local pre-published Phase 1 dataset
docs/
  architecture.md
  components/
  roadmap.md
  storage.md
src/konsider/
  domain/                      # framework-free models, profiles, scoring
  repositories/               # fixture and future storage adapters
tests/
  unit/domain/
  integration/repositories/
web/                           # future React + Vite deployment root
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## Run Tests

```powershell
python -m pytest
```

The tests also run without third-party test tooling:

```powershell
python -m unittest discover -s tests
```

## Example

```python
from konsider.domain.profiles import get_default_profile
from konsider.domain.scoring import build_ranking_table, rank_countries
from konsider.repositories.fixture_repository import FixtureProjectDataRepository

data = FixtureProjectDataRepository().load()
profile = get_default_profile("indian_tech_professional_with_teenage_child")
rankings = rank_countries(data.metrics, profile.weights)
table = build_ranking_table(rankings, data.countries)

print(table[0].rank, table[0].country_name, table[0].total_score)
```
