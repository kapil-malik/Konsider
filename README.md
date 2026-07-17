# Konsider

Konsider is an evidence-backed country suitability and relocation advisor. It produces personalized,
explainable country rankings from user priorities and is designed to grow into a system that
refreshes public evidence, serves deterministic rankings, and supports conversational exploration.

The repository is currently past the original fixture-only Phase 1 foundation. It now includes a
local data-refresh worker that publishes and replays a validated real-data release. API, React,
retrieval, and LLM runtimes remain intentionally blocked until the worker-first dataset gate is
satisfied and reviewed.

## Architecture

Konsider is organized around three independently deployable applications:

- A Python data refresh worker that builds versioned, validated dataset releases.
- A Python live engine that owns profiles, scoring, retrieval, chat tools, and public APIs.
- A React + Vite website that accesses only the live engine.

The early production target is deliberately lean: Amplify Hosting for the website, API Gateway plus
Python Lambda for the live API, EventBridge Scheduler plus Python Lambda for weekly refreshes, and
S3 for immutable dataset releases and raw artifacts. DynamoDB, ECS/App Runner, Step Functions, SQL,
and vector search are escalation paths rather than starting assumptions.

Start with [docs/architecture.md](docs/architecture.md). The component documents, storage design,
and current sprint sequence are linked from there and from [docs/roadmap.md](docs/roadmap.md).

## Current Capabilities

- Published local release `2026-07-17.1` with five credible criteria across 20 countries.
- Immutable raw artifact capture, normalized observations, validation, scoring, publication, and
  replay for the first worker vertical slice.
- Ten countries and ten comparison metrics.
- Complete fixture validation.
- Editable and normalized user weights.
- Three default profile templates.
- Deterministic weighted rankings.
- Parameter-level contribution breakdowns, strengths, and tradeoffs.
- Qualitative evidence fixture loading.

Fixture scores remain approximate MVP fixtures and are not a source of truth for relocation
decisions. The real-data release is documented separately in
[docs/release-2026-07-17.1.md](docs/release-2026-07-17.1.md).

## Repository Layout

```text
apps/
  api/                         # future FastAPI/Lambda live engine root
  worker/                      # future refresh CLI/Lambda worker root
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
