# Konsider Phase 7 — Typed Feasibility Checks and Guest Profile Context

## Purpose

This prompt pack is intended to be given to Codex / ChatGPT on the local Konsider repository, one phase at a time.

Phase 7 explores and, only if the evidence gates pass, implements **Typed Feasibility Checks (TFCs)** using explicit applicant, household, and exploration-scenario context.

Do not execute the entire pack as one task. Complete, test, document, commit, and obtain owner approval for each phase before beginning the next one.

## Terminology decision

Use:

- **Typed Feasibility Check**
- internal shorthand: **TFC**
- user-facing language: **Feasibility check**, **Your situation**, or **Your feasibility**, depending on the UI surface

Do not use “Typed Feasibility Criterion” in the implementation unless repository evidence justifies reversing this decision.

The word **check** is preferred because a TFC may return:

- a route or requirements match;
- a conditional match;
- missing required inputs;
- insufficient destination evidence;
- a calculated scenario metric;
- a contextual advisory result.

A TFC is not necessarily a score and must not be treated as an ordering criterion.

## Phase 7 product goal

Konsider must remain fully useful to a guest.

A user may optionally provide structured context describing:

1. the applicant;
2. the household;
3. the current relocation, work, or education scenario.

Konsider then evaluates selected or applicable TFCs against immutable, versioned destination evidence and policies.

The result must remain separate from:

- affinity score;
- ordering criteria;
- FCC/PCC coverage behavior;
- LSC aggregation and locality compatibility;
- Opportunity Filter states;
- preference presets.

## Approved product direction

Treat these as approved unless current repository evidence exposes a direct contradiction.

### Guest first

Phase 7 must not require authentication.

Profile and scenario data are:

- held in browser memory by default;
- optionally retained for the browser session;
- optionally remembered on the device only after explicit user action;
- never silently persisted server-side;
- never written to immutable public releases, source artifacts, analytics, URLs, or application logs.

### Profile is not the same as an account

Model separately:

- `ApplicantProfile`: reusable facts about an applicant;
- `HouseholdProfile`: reusable household composition and relevant facts;
- `ExplorationScenario`: temporary assumptions for a particular decision;
- `EffectiveProfileContext`: the immutable request snapshot actually evaluated.

A future account may own several saved profiles and several scenarios. Do not design one account as exactly one applicant.

### Explicit request snapshot

Even after future login exists, evaluation must use an explicit profile/scenario snapshot supplied with or resolved for the request.

Do not let assessment logic silently read a mutable “latest account profile.”

### No login implementation in Phase 7

Design clean persistence boundaries, but do not implement:

- authentication;
- account recovery;
- server-side saved profiles;
- cross-device sync;
- chat history;
- conversational memory;
- notifications.

### No hidden personalization

Do not infer sensitive or consequential profile facts.

Unknown means unknown. Missing profile fields must remain explicit.

## Phase 7 research gate

Implementation after Phase 7B may proceed only if at least **three TFCs** qualify for production.

Prefer a first wave of **three to five TFCs**.

If more than five qualify, the owner must select a coherent first wave rather than onboarding all of them automatically.

If fewer than three qualify:

- stop Phase 7 after the research and owner-decision report;
- do not create a generic runtime framework merely to claim implementation progress;
- document the blockers and next-best source research;
- leave the active release, API, and UI unchanged.

### Diversity preference

Prefer the qualified first wave to exercise at least two TFC result families, for example:

- rule/route matching; and
- calculated scenario metrics.

Do not weaken source, legal, coverage, construct, privacy, or replay gates merely to obtain type diversity.

## Candidate research universe

Phase 7A must revisit every Phase 3 criterion classified as profile-dependent.

At minimum include:

- C01 Overall higher-education opportunity
- C06 International-student accessibility
- C08 School education quality
- C12 Software and technology jobs
- C13 Medical and healthcare jobs
- C14 Business, finance, and professional-services jobs
- C15 Engineering and skilled technical jobs
- C17 Average earning potential
- C21 Personal income-tax burden
- C22 Social-security and mandatory contribution burden
- C25 Housing affordability
- C26 Healthcare affordability
- C32 Skilled-work visa accessibility
- C33 Permanent-residency accessibility
- C34 Citizenship accessibility
- C35 Post-study migration pathway
- C36 Family reunification support
- C38 Professional-licensing accessibility for immigrants
- C40 English usability
- C45 LGBTQ+ legal and social inclusion
- C76 Social protection and welfare support

The first deep-probe slate should normally be no more than eight candidates.

The default priority slate to validate, not blindly accept, is:

1. skilled-work route feasibility;
2. family accompaniment/reunification feasibility;
3. post-study work pathway;
4. permanent-residence pathway;
5. professional-licensing requirement/access check;
6. employment tax and mandatory-contribution scenario;
7. housing-affordability scenario;
8. healthcare-affordability scenario.

Phase 7A may replace items when evidence supports a better slate.

## Relationship with Opportunity Filters

Opportunity Filters remain destination-side ecosystem signals.

TFCs may combine with OFCs in explanations, but must not mutate OFC evidence or reinterpret OFC states.

Examples:

- strong technology ecosystem + supported skilled-work route match;
- strong care-sector ecosystem + professional licensing requirements not yet met;
- strong biomedical research-university ecosystem + student route requires additional inputs.

A non-verified OFC is not proof that a personal opportunity is absent.

A failed or unsupported TFC is not proof that the destination itself is poor.

## Proposed execution sequence

| Phase | Intent |
|---|---|
| 7A | Product discovery, complete profile-dependent criterion disposition, context model, first deep-probe slate |
| 7B | Exact-source feasibility probes, production qualification, minimum-three owner gate |
| 7C | Profile, scenario, privacy, TFC and assessment contracts; ADRs and synthetic fixtures only |
| 7D | Generic rule/evidence worker and immutable release foundation |
| 7E | Typed assessment engine, input sufficiency, scenario snapshots and optional explicit feasibility filtering |
| 7F | Production onboarding of the approved first-wave TFCs into staged immutable artifacts |
| 7G | Stateless API v2 profile/TFC transport and generated client contract |
| 7H | Guest-first profile/scenario UI and explicit local/session retention |
| 7I | OFC/locality/TFC integration, scenario comparison and end-to-end verification |
| 7J | Immutable release activation, regression/privacy verification, closure and roadmap |

## Proposed commit sequence

Use focused commits. Do not create one monolithic Phase 7 commit.

| Phase | Expected commit intent |
|---|---|
| 7A | Research and product-boundary documentation only |
| 7B | Source probes, qualification matrix and owner gate only |
| 7C | ADRs, schemas, contracts and synthetic fixtures |
| 7D | Generic worker/release foundation |
| 7E | Assessment engine and scenario snapshot domain logic |
| 7F-n | Prefer one qualified TFC or one inseparable source family per commit |
| 7G | API/OpenAPI/generated-client changes |
| 7H | Guest profile UI and browser retention |
| 7I | Integration and end-to-end scenarios |
| 7J | Release, closure, cleanup and roadmap |

## Global execution rules

Apply these rules to every prompt:

1. Start from the latest `main` branch.
2. Inspect current repository paths and active contracts before making assumptions.
3. Read the previous phase report, ADRs, schemas, fixtures and tests.
4. Preserve immutable historical releases.
5. Do not weaken no-imputation or complete-case ranking guarantees.
6. Do not change affinity scores because of a TFC.
7. Do not put TFCs into criterion weights or preference presets.
8. Do not put TFCs into the OFC catalog.
9. Do not infer profile values from country, browser, name, email or other indirect signals.
10. Keep destination evidence and applicant input separate.
11. Store destination evidence and policies, not precomputed profile × country matrices.
12. Keep runtime assessment deterministic and explainable.
13. Use exact official or demonstrably independent sources with explicit licensing conclusions.
14. Preserve effective dates, policy versions, source snapshots/checksums and replay.
15. Missing evidence is not a negative conclusion.
16. Missing profile input is not destination failure.
17. Do not make legal, immigration, tax, admissions or licensing guarantees.
18. Every public result must disclose scope, effective date, limitations and source.
19. API runtime must never fetch external sources.
20. UI must not implement eligibility, route, tax or scoring rules.
21. Do not log profile request bodies or place profile values in URLs.
22. Do not persist profile context server-side in Phase 7.
23. Add tests at the layer that owns each rule.
24. Update documentation in the same phase as behavior.
25. Do not begin the next phase automatically.
26. End each phase with a concise report, commands/results, changed paths, commit SHA and unresolved owner decisions.

## Current baseline

Begin from the current active release and contracts found in the repository.

At the time this pack was written, the expected baseline was:

- active release `2026-08-04.1`;
- schema-5.1 release with 91 countries;
- ordering criteria, FCC/PCC, LSC and OFC behavior already active;
- `assessments.profile` reserved but unevaluated;
- authentication, saved profiles and persistent sessions deferred.

Repository truth takes precedence if the baseline has changed.

## How to use this pack

Run:

1. `01_PHASE_7A_TFC_DISCOVERY_AND_PRODUCT_BOUNDARY.md`
2. `02_PHASE_7B_TFC_SOURCE_FEASIBILITY_AND_OWNER_GATE.md`

Stop for explicit owner review.

Only if at least three TFCs are approved, continue in order through Phase 7J.

The combined file `KONSIDER_PHASE_7_PROMPT_PACK.md` is provided for reference. Prefer the modular files during execution.
