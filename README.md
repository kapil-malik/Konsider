# Konsider

Konsider is a Phase 1 MVP for an AI-powered country suitability and relocation advisor.

The project ranks countries against a user's priorities instead of presenting a generic "best countries" list. Phase 1 focuses on a small, explainable foundation that can later grow into a Streamlit app with retrieval, agent-style workflows, MCP tools, and deployment support.

## Phase 1 Scope

- 10 countries
- 10 comparison parameters
- Editable user weights
- Weighted, explainable country rankings
- Structured metric loading
- Qualitative evidence document loading
- Tested scoring and validation core

This first sprint intentionally does not include Streamlit, LangGraph, MCP, Chroma, or LLM calls.

## Countries

- India
- Singapore
- Canada
- Australia
- Germany
- Netherlands
- Switzerland
- United States
- United Kingdom
- UAE

## Parameters

- Tech jobs
- Finance jobs
- Crime rate
- Female safety
- Healthcare
- Air quality
- Infrastructure
- Tax burden
- Cost of living
- University quality

All parameter scores are normalized from 1 to 10, where 10 is better for the user. Negative metrics such as crime rate, tax burden, and cost of living are already inverted in the MVP data so higher remains better.

## Project Layout

```text
data/
  countries.yml
  parameter_definitions.yml
  country_metrics.csv
  evidence/
src/
  konsider/
    data_loader.py
    models.py
    scoring.py
tests/
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## Run Tests

```bash
python -m pytest
```

## Example

```python
from konsider.data_loader import load_project_data
from konsider.scoring import rank_countries

data = load_project_data()
weights = {
    "tech_jobs": 5,
    "female_safety": 5,
    "university_quality": 4,
    "cost_of_living": 2,
}

rankings = rank_countries(data.metrics, weights)
print(rankings[0].country_id, rankings[0].total_score)
```

## Data Caveat

The included country scores are placeholder MVP estimates for product and architecture development. They are not a source of truth for real relocation decisions.
