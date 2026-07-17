# Konsider Roadmap

Status: current roadmap

Supersedes the sprint sequence in `konsider_context.md`.

## Product Direction

Konsider will become an evidence-backed, personalized country decision platform with three
deployable components: a data refresh worker, a Python live engine, and a React web application.
The deterministic scoring domain remains independent of LLMs. Retrieval and conversational agents
use that domain through typed tools and cite versioned evidence.

## Completed Foundation

### Sprint 1: Repository and Fixture Data

- Python package and project configuration.
- Ten-country, ten-metric fixture dataset.
- Fixture validation and qualitative evidence loading.
- Initial tests and README.

### Sprint 2: Deterministic Scoring

- Weight normalization and country ranking.
- Default profiles.
- Parameter-level contributions, strengths, and tradeoffs.
- Scoring and profile tests.

### Architecture Alignment

- Define the three deployable boundaries and their storage/API handshakes.
- Move existing behavior into domain and fixture-repository packages.
- Reserve application roots for the API, worker, and website.
- Keep this step behavior-preserving.

## Planned Delivery

### Sprint 3: API-backed React MVP

- Add a minimal FastAPI live engine using the fixture repository.
- Publish catalog and ranking endpoints with generated OpenAPI.
- Build the React + Vite + TypeScript website.
- Add profile selection, editable weights, top-K ranking, contribution breakdown, and caveats.
- Deploy the website locally first; keep it compatible with Amplify Hosting.

### Sprint 4: Evidence Model and Retrieval

- Introduce structured evidence IDs and provenance fields.
- Add evidence lookup endpoints and website evidence details.
- Add retrieval interfaces and a local retrieval implementation.
- Provide template-based explanations that work without an LLM key.

### Sprint 5: Conversational Profiles and Explanations

- Add chat sessions, profile revisions, typed stream events, and SSE.
- Integrate an LLM behind server-side tools and secrets.
- Allow chat to propose/apply weight changes and refresh rankings.
- Require evidence citations and retain a deterministic fallback.

### Sprint 6: First Production Data Connector

- Add source registrations, refresh runs, raw-artifact capture, and draft releases.
- Implement one approved public API connector end to end.
- Add normalization, validation, publication, and replay tests.
- Keep fixture releases available for demos and tests.

### Sprint 7: Critic, Agent Workflow, and MCP

- Add recommendation critique and explicit risk/caveat output.
- Introduce LangGraph only where durable orchestration improves the proven service flow.
- Expose stable ranking, comparison, evidence, and reporting tools through MCP.
- Test tool use, citation coverage, and failure fallbacks.

### Sprint 8: AWS Deployment and Operations

- Host the React application on Amplify Hosting.
- Deploy the FastAPI container to App Runner or ECS Fargate based on measured needs.
- Schedule refresh workflows with EventBridge and Step Functions.
- Add AWS-backed repositories, secrets, tracing, alerts, backup, and rollback procedures.
- Add authentication and user-data lifecycle controls when persistence is enabled.

## Delivery Rules

- Each sprint ends with a runnable vertical slice, tests, and updated contracts.
- Business logic is not duplicated between Python and TypeScript.
- New data is not published without provenance and validation.
- LLM availability is never required for deterministic ranking.
- Architecture choices listed as deferred in `architecture.md` remain reversible until load,
  latency, cost, or compliance requirements justify a decision.
