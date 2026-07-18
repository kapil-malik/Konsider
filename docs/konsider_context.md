# Konsider - Historical Context Pack

> **Status: superseded.** This file preserves the original Phase 1 brief and sprint assumptions.
> Its 10-country, 10-metric fixture dataset is legacy test/demo data and is separate from the
> 20-country real-data releases. It must not be used to fill missing real observations.
> The accepted system design is now in [architecture.md](architecture.md), with the current delivery
> sequence in [roadmap.md](roadmap.md). Component details live under [components/](components/).
> References below to early vector search, LangGraph, MCP, or heavier AWS infrastructure are
> historical; the current plan starts with release artifacts, Lambda, S3, and metadata evidence
> lookup.

## Project Summary

Konsider is an AI-powered country suitability and relocation advisor. The goal is to help individuals and families evaluate countries for education, career growth, relocation, long-term settlement, entrepreneurship, and quality of life.

The product should not behave like a generic "best countries" ranking website. It should generate personalized recommendations based on each user's priorities, constraints, and preferences, and it should explain the reasoning, tradeoffs, evidence, and scoring behind each recommendation.

## Current Phase

We are building Phase 1 only.

Phase 1 should be a working, GitHub-demoable MVP that demonstrates:

* 10 countries
* 10 comparison parameters
* Custom weight tuning
* Explainable country rankings
* Structured data retrieval
* Qualitative evidence retrieval
* RAG
* LangGraph-style agentic workflow
* MCP tools
* Simple web interface
* AWS-deployable architecture later, but local-first for now

## Phase 1 Countries

1. India
2. Singapore
3. Canada
4. Australia
5. Germany
6. Netherlands
7. Switzerland
8. United States
9. United Kingdom
10. UAE

## Phase 1 Parameters

Career:

* Tech jobs
* Finance jobs

Safety:

* Crime rate
* Female safety

Quality of Life:

* Healthcare
* Air quality
* Infrastructure

Economics:

* Tax burden
* Cost of living

Education:

* University quality

## Suggested Phase 1 Goal

Build a clean, small, complete product rather than a large dataset project.

Definition of success:

* Streamlit app runs locally
* User enters or selects a profile
* App creates/editable parameter weights
* App ranks the 10 countries
* App shows score breakdown per country
* App explains recommendations with caveats
* App retrieves qualitative evidence snippets
* App includes a critic step that challenges the top recommendation
* Repo has clear README and sample data
* Architecture leaves room for FastAPI, LangGraph, MCP, and AWS deployment later

## Recommended Architecture

Start simple and modular.

### Initial stack

* Python 3.11 or 3.12
* Streamlit for UI
* SQLite for structured country metrics
* Chroma or local FAISS for vector retrieval
* sentence-transformers / BGE-small / OpenAI embeddings depending on availability
* LangGraph for agent orchestration, but do not overcomplicate first pass
* FastMCP for MCP tools after the core scoring app works
* pytest for unit tests
* ruff/black for formatting

### Suggested repo structure

```text
Konsider/
  README.md
  pyproject.toml
  .env.example
  app/
    streamlit\_app.py
  src/
    konsider/
      \_\_init\_\_.py
      config.py
      models.py
      data\_loader.py
      scoring.py
      retrieval.py
      prompts.py
      agents/
        \_\_init\_\_.py
        profile\_agent.py
        weight\_builder\_agent.py
        retrieval\_agent.py
        scoring\_agent.py
        critic\_agent.py
        recommendation\_agent.py
      mcp/
        server.py
        tools.py
  data/
    countries.yml
    parameter\_definitions.yml
    country\_metrics.csv
    evidence/
      canada.md
      singapore.md
      germany.md
      australia.md
      india.md
      netherlands.md
      switzerland.md
      united\_states.md
      united\_kingdom.md
      uae.md
  tests/
    test\_scoring.py
    test\_data\_loader.py
    test\_weights.py
```

## Core Data Model

Structured metric example:

```json
{
  "country": "Singapore",
  "parameter": "crime\_rate",
  "score": 9.2,
  "source": "MVP-estimate or actual source URL",
  "last\_updated": "2026-01-01",
  "notes": "Higher score means safer / better outcome"
}
```

Qualitative evidence example:

```json
{
  "country": "Canada",
  "topic": "housing",
  "text": "Canada has strong education and quality of life, but housing affordability is a common concern in major cities.",
  "source": "MVP-note or actual source URL"
}
```

## Scoring Rules

* Each parameter score should be normalized to 1-10 where 10 is better for the user.
* For negative metrics such as crime rate, tax burden, and cost of living, invert the score so that higher is still better.
* Weighted score = sum(parameter\_score \* parameter\_weight).
* Weights should sum to 1.0.
* Show both total score and parameter-level contribution.
* Always display caveats that MVP scores are approximate unless backed by hard sources.

## Default User Profiles

### Profile 1: Indian tech professional with teenage child

Priorities:

* Tech jobs: high
* Female safety: high
* University quality: high
* Crime rate: high
* Healthcare: medium
* Cost of living: medium
* Tax burden: low-medium

### Profile 2: Student planning higher education

Priorities:

* University quality: high
* Safety: high
* Cost of living: high
* Public infrastructure: medium
* Tech jobs/finance jobs: medium

### Profile 3: Finance professional

Priorities:

* Finance jobs: high
* Tax burden: high
* Infrastructure: high
* Safety: medium
* Cost of living: medium
* Healthcare: medium

## Agent Workflow

Implement as simple functions first; wrap with LangGraph later.

1. Profile Agent

   * Extract user goals, constraints, family context, and priorities.
2. Weight Builder Agent

   * Convert priorities into weights.
   * Allow user to edit weights.
3. Retrieval Agent

   * Retrieve structured metrics and qualitative evidence.
4. Scoring Agent

   * Compute weighted rankings.
5. Critic Agent

   * Challenge top results and identify weaknesses.
6. Recommendation Agent

   * Produce final explanation with top countries, tradeoffs, and caveats.

## MCP Tools to Add After Core MVP

Expose the following tools:

* search\_country\_metrics(country, parameter)
* compare\_countries(countries)
* rank\_countries(weights)
* search\_evidence(country, topic)
* generate\_report(country)

Do not start with MCP. Add it after local Streamlit + scoring + retrieval works.

## Suggested Solo Sprint Plan

### Sprint 1: Repo + Data Skeleton

Goal:

* Create project repo, Python environment, data schemas, and first sample data.

Tasks:

* Create repo structure.
* Add README with Phase 1 scope.
* Add countries and parameter definitions.
* Add country\_metrics.csv with placeholder/rough scores for 10 countries x 10 parameters.
* Add evidence markdown files with 5-10 bullet points per country.
* Implement data\_loader.py.
* Add basic tests for loading and validation.

### Sprint 2: Scoring Engine

Goal:

* Make rankings deterministic and explainable.

Tasks:

* Implement weighted scoring.
* Implement weight normalization.
* Add default profiles.
* Add country ranking output.
* Add score breakdown.
* Add tests for scoring correctness.

### Sprint 3: Streamlit MVP

Goal:

* First usable app.

Tasks:

* Build Streamlit UI.
* Add profile selector.
* Add editable weight sliders.
* Show country ranking table.
* Show top 3 recommendations.
* Show per-country breakdown.
* Add caveat text about approximate MVP scoring.

### Sprint 4: Evidence Retrieval + Explanations

Goal:

* Add RAG-style qualitative context.

Tasks:

* Embed evidence docs.
* Retrieve relevant evidence by country/topic.
* Add simple recommendation prompt.
* Generate explanation with "Why this country?", "Tradeoffs", and "Who may not like it?"
* Keep the app robust if no API key is present by falling back to template-based explanations.

### Sprint 5: Critic + LangGraph Shape

Goal:

* Make it feel agentic and thoughtful.

Tasks:

* Add critic\_agent.py.
* Critic should challenge the top recommendation.
* Add "risks and caveats" section.
* Optional: introduce LangGraph nodes if the functional flow is stable.
* Add tests around critic output shape.

### Sprint 6: MCP + Demo Polish

Goal:

* Make it production-style and demo-ready.

Tasks:

* Add FastMCP server.
* Expose the five core tools.
* Add README demo script.
* Add screenshots or sample outputs.
* Add GitHub issues for Phase 2.
* Optional: deploy Streamlit locally or to a simple cloud target.

## Immediate First Codex Task

Ask Codex to do this first:

```text
Create the initial Konsider Phase 1 repo skeleton in Python.

Requirements:
- Use pyproject.toml.
- Create src/konsider package.
- Create data folder with countries.yml, parameter\_definitions.yml, country\_metrics.csv, and evidence/\*.md placeholders.
- Implement data\_loader.py to load and validate countries, parameter definitions, metrics, and evidence docs.
- Implement scoring.py with weighted scoring and normalized weights.
- Add tests for data loading and scoring.
- Add a README explaining Phase 1 scope.
- Do not add LangGraph, MCP, Chroma, or Streamlit yet. Keep this first PR small and clean.
```

## Important Product Principle

Do not optimize for perfect country data in Phase 1. Optimize for a complete, explainable AI/system-design demo.

The project should clearly demonstrate:

* structured metrics
* qualitative evidence
* RAG
* agent-style reasoning
* custom weights
* scoring
* critique
* explainable recommendation
* clean software architecture
