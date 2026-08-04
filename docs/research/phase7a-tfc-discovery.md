# Phase 7A Typed Feasibility Check discovery

Status: complete; ready for Phase 7B owner review

Date: 2026-08-05

This phase defines the product boundary for applicant-dependent feasibility without changing the
runtime. It revisits the 21 Phase 5 `PROFILE_PHASE` candidates, maps the useful questions to typed
results and explicit profile context, and recommends eight exact-source probes. It does not approve
any check for production. Phase 7B must qualify at least three checks before implementation can
proceed.

## Decision

A **Typed Feasibility Check (TFC)** is a deterministic, evidence-backed assessment of a named
applicant, household, or exploration scenario against destination rules or costs as of a stated
date. A check may return matched routes and conditions, missing inputs, unsupported evidence, a
scenario metric or a cautious contextual advisory. It never returns an affinity score and never
changes country quality, Opportunity Filter evidence, or canonical ordering.

"Check" is safer than "criterion" because it describes a question evaluated for an explicit
snapshot. "Criterion" in Konsider means destination evidence that can participate in ordering and
invites an invalid universal country score. A TFC is instead a sibling assessment product:

| Product concept | Question answered | May change affinity/order? | Context owner |
| --- | --- | --- | --- |
| Ordering criterion (FCC/PCC/LSC) | How well does the destination fit stated preferences? | Yes, through existing ranking rules | Immutable destination release |
| Opportunity Filter (OFC) | Is a strong destination-side ecosystem signal established? | Filters only; preserves survivor order | Immutable destination release |
| Typed Feasibility Check | What supported routes, requirements, or scenario values apply to this explicit situation? | No; future filtering requires a separate owner decision | Immutable destination rules plus request snapshot |
| Preference preset | Which ordering weights should be used? | Selects weights | Request/UI state |
| Account setting | How should a future account behave? | No product inference | Out of Phase 7 scope |

TFC output must be evaluated from an explicit `EffectiveProfileContext` snapshot assembled from
separate `ApplicantProfile`, `HouseholdProfile`, and `ExplorationScenario` inputs. Evaluation must
not read a mutable "latest profile", infer unknown facts, or write applicant facts into releases,
source artifacts, analytics, URLs, request logs, or server persistence.

## Current product position

Active release `2026-08-04.1` has 91 countries, schema 5.1, fourteen ordering criteria and nine
Opportunity Filters. The API already exposes structured coverage, locality, opportunity, and
reserved profile assessments; without applicant input, profile status is `NO_PROFILE_CONTEXT`.
The browser keeps current preferences in React memory, does not put them in URLs, and does not
persist them. Phase 7 should extend those boundaries guest-first rather than introduce accounts.

The Phase 3 and Phase 5 findings remain controlling:

- legal routes were deferred because nationality, occupation, qualification, household and policy
  date determine the answer;
- tax, contributions, housing and healthcare were deferred because a household/scenario value is
  more honest than a country scalar;
- career and research-university ecosystem signals now exist as destination-side OFCs and must not
  be reimplemented as applicant-success claims;
- school quality, English usability, citizenship, welfare and LGBTQ+ inclusion retain construct,
  locality, licensing, sensitivity or maintenance blockers that profile context alone does not fix.

## Candidate disposition

The machine-readable source of truth is
`data/reports/phase7a-2026-08-05/tfc-disposition-matrix.json`. Every one of the 21 Phase 5
`PROFILE_PHASE` candidates appears exactly once.

| ID | Original name | Phase 7A disposition | Proposed role |
| --- | --- | --- | --- |
| C01 | Overall higher-education opportunity | `PROFILE_MODEL_ONLY` | Course/institution context for student checks; ecosystem remains OFC territory |
| C06 | International-student accessibility | `SECOND_WAVE` | Bounded student-entry/admission-requirements check after source decomposition |
| C08 | School education quality | `RESEARCH_ONLY` | Household context may explain relevance but does not turn national quality into feasibility |
| C12 | Software and technology jobs | `PROFILE_MODEL_ONLY` | Occupation context may select the technology OFC and feed route checks |
| C13 | Medical and healthcare jobs | `PROFILE_MODEL_ONLY` | Occupation context may select care OFC and licensing checks |
| C14 | Business, finance and professional-services jobs | `PROFILE_MODEL_ONLY` | Occupation context may select finance OFC; no applicant-success TFC |
| C15 | Engineering and skilled technical jobs | `PROFILE_MODEL_ONLY` | Occupation context may select engineering/trades OFCs and licensing checks |
| C17 | Average earning potential | `SECOND_WAVE` | Occupation/locality earnings range after a defensible source route exists |
| C21 | Personal income-tax burden | `DEEP_PROBE` | Employment deductions estimate, including C22 components |
| C22 | Social-security and mandatory contribution burden | `PROFILE_MODEL_ONLY` | Mandatory component of C21; not a separate check |
| C25 | Housing affordability | `DEEP_PROBE` | Locality and household housing-cost-to-budget scenario |
| C26 | Healthcare affordability | `DEEP_PROBE` | Status/household healthcare-cost scenario |
| C32 | Skilled-work visa accessibility | `DEEP_PROBE` | Supported skilled-work route and requirement match |
| C33 | Permanent-residency accessibility | `DEEP_PROBE` | Supported residence pathway and requirement match |
| C34 | Citizenship accessibility | `SECOND_WAVE` | Long-horizon naturalisation requirements after residence modelling |
| C35 | Post-study migration pathway | `DEEP_PROBE` | Supported post-study work/stay route match |
| C36 | Family reunification support | `DEEP_PROBE` | Accompaniment/reunification route and dependant-rights match |
| C38 | Professional-licensing accessibility | `DEEP_PROBE` | Bounded profession/jurisdiction requirements match |
| C40 | English usability | `PROFILE_MODEL_ONLY` | Language facts feed route/licensing checks; broad usability is not feasibility |
| C45 | LGBTQ+ legal and social inclusion | `REJECT_TFC` | Do not request/infer identity; current production-source licence also blocks reuse |
| C76 | Social protection and welfare support | `SECOND_WAVE` | Status/contribution-aware eligibility advisory only after legal-source research |

Counts are: eight `DEEP_PROBE`, four `SECOND_WAVE`, seven `PROFILE_MODEL_ONLY`, one
`RESEARCH_ONLY`, and one `REJECT_TFC`.

## Minimum result type system

Phase 7 should begin with a deliberately small discriminated result family rather than a universal
rules language.

### Rule or route match

Use for migration and licensing. A result identifies the check, destination, snapshot and evidence
effective date, then reports zero or more named routes with `MATCHED`, `CONDITIONAL`, or
`NOT_MATCHED` status. Every route carries satisfied conditions, unmet conditions, missing inputs,
source references and limitations. Check-level states must distinguish `INPUT_REQUIRED`,
`ASSESSED`, `DESTINATION_UNSUPPORTED`, and `INSUFFICIENT_EVIDENCE`.

"No supported route matched" is permitted only when the bounded route inventory is complete and
current. It must never be presented as permanent ineligibility or legal advice.

### Scenario metric

Use for tax/contributions, housing and healthcare. A result contains a point or range, unit,
currency, period, assumptions, included and missing components, source/effective date and quality.
Comparison bands may be derived only from like-for-like supported scenarios. A missing salary,
locality or household input returns `INPUT_REQUIRED`, not a default person.

### Contextual advisory

Reserve for later checks such as welfare eligibility where exact rules can support useful context
but not a route decision or complete numeric estimate. Advisories must state what is known,
unknown, conditional and unsupported. They must not label a destination "good" or "bad" for a
person. No contextual advisory is needed to prove the first wave if rule and metric families qualify.

## Profile and scenario boundary

The machine-readable field registry is
`data/reports/phase7a-2026-08-05/profile-context-field-registry.json`. Its governing rules are:

- applicant fields describe relatively stable facts such as citizenship, residence, occupation,
  qualifications, registrations and language proficiency;
- household fields describe the people whose rights and costs are part of the exploration;
- scenario fields describe a destination attempt: purpose, year, job/course, salary, localities,
  housing and budget assumptions;
- every field has named consuming checks, validation, sensitivity, requirement mode and default
  retention; fields with no consumer are prohibited;
- all profile disclosure is optional; "mandatory" means a selected check cannot evaluate without
  that fact and must return `INPUT_REQUIRED` when the guest declines;
- age in years is preferred. Exact date of birth is requested only when a supported rule requires
  date-bound calculation and is not retained by default;
- nationality/citizenship, residence status, salary, qualification details and household
  composition are consequential and purpose-bound. Unknown remains unknown;
- sexual orientation, gender identity, ethnicity, religion, health condition, inferred wealth and
  other unrelated sensitive attributes are not candidate fields for this phase.

Default lifetime is the active browser tab. Explicit user action may retain a named snapshot for
the session or on the device. A future account may own multiple profiles and scenarios, but account
persistence is an adapter outside Phase 7. One account must never imply one applicant.

## Guest-first experience

The ordinary anonymous ranking remains the first and complete experience. "Add your situation" is
optional and opens progressive questions only for the checks the guest selects. The UI should:

1. explain the purpose of each requested field at the point of collection;
2. show assumptions and missing inputs before evaluation;
3. keep affinity, opportunity and feasibility explanations visibly separate;
4. let the guest correct, clear, export or explicitly retain the snapshot;
5. clear tab-memory state on reload/close unless the guest chose session/device retention; and
6. never make login a prerequisite or silently send profile facts to persistence, analytics or URLs.

The browser may derive an `EffectiveProfileContext` for a request, but it must not implement legal,
metric or TFC state rules. Those remain in the deterministic server-side engine over immutable
evidence.

## Opportunity Filter interaction

The machine-readable crosswalk is
`data/reports/phase7a-2026-08-05/tfc-ofc-crosswalk.json`. The product sentence is:

> Opportunity evidence describes the destination; a feasibility check describes this explicit
> situation. One does not prove the other.

Occupation/course fields may help a guest select relevant OFCs, but no OFC may infer occupation,
qualification, licensing, visa or admission facts. TFCs may cite a selected OFC alongside their
own result, yet must not mutate OFC state, evidence, threshold or survivor order. Examples:

- a strong care-sector signal can coexist with an unsupported or conditional physician-licensing
  check;
- a strong technology ecosystem can coexist with no supported skilled-work route match;
- a strong research-university ecosystem does not establish programme availability, admission,
  affordability, visa access or post-study rights;
- a destination unsupported by an OFC may still have a matched route; missing ecosystem evidence
  is not applicant failure.

## Phase 7B deep-probe slate

The detailed protocol is
`data/reports/phase7a-2026-08-05/phase7b-deep-probe-protocol.json`. The eight probes are:

| Probe | Source criteria | Exact user question | Result family |
| --- | --- | --- | --- |
| Skilled-work route feasibility | C32 | Which supported skilled-work routes match this snapshot, and what is missing or unmet? | Rule/route match |
| Family accompaniment/reunification | C36 | Can the named household members accompany or reunify under a supported route, and what rights/conditions apply? | Rule/route match |
| Post-study work pathway | C35 | Does the study scenario match a supported post-study work/stay route? | Rule/route match |
| Permanent-residence pathway | C33 | Which supported residence pathways match now or conditionally, and which requirements remain? | Rule/route match |
| Professional-licensing requirements | C38 | For this bounded profession, qualification origin and jurisdiction, what recognition/licensing steps are supported? | Rule/route match |
| Employment deductions estimate | C21 + C22 | Under this employment and household scenario, what employee tax and mandatory deductions are estimated? | Scenario metric |
| Housing affordability scenario | C25 | For this locality and household housing assumption, what share/range of income or budget is required? | Scenario metric |
| Healthcare affordability scenario | C26 | Under this status and household scenario, what required healthcare costs can be estimated and what is excluded? | Scenario metric |

Phase 7B should audit support across all 91 stable destinations while using a predeclared anchor
set to test rule diversity and extraction: Australia, Canada, Germany, Netherlands, Singapore,
United Arab Emirates, United Kingdom and United States. Anchor selection is methodological, not a
supported-country promise. Candidate-specific coverage floors must be frozen before results are
measured; a bounded high-value destination subset is acceptable only when unsupported destinations
remain explicit.

Phase 7B must test exact official source identity, lawful production and normalized derivative use,
effective dates, conflicts, extraction/replay, minimum inputs, safe interpretation and realistic
refresh burden. It must use synthetic profiles only. Each candidate receives one of the Phase 7B
dispositions and every country receives an explicit research-support state.

## Implementation gate and owner questions

No production schema, worker, release, API or UI work is authorized by Phase 7A. Phase 7C may begin
only if at least three probes are `PRODUCTION_QUALIFIED_FIRST_WAVE` without weakening any gate.
Prefer three to five checks and at least two result families. If fewer than three qualify, Phase 7
closes as research-only.

Phase 7B must ask the owner to approve the exact first-wave names, supported applicant and
destination boundaries, result-family scope, whether explicit post-ranking feasibility filtering
is allowed, and browser session/device retention direction. Those are intentionally not decided in
Phase 7A because they depend on measured source feasibility.

## Evidence base and artifacts

This decision used the retained Phase 3 screening and all three deep-research batches, Phase 3
closure, Phase 5A matrix and report, Phase 5 contracts/ADRs/closure, Phase 6B/6B.1/6C studies, active
Opportunity Filter contracts and closure, current roadmap/system architecture, active release and
catalog, API v2 schemas, and current UI state documentation.

Artifacts:

- `data/reports/phase7a-2026-08-05/tfc-disposition-matrix.json`
- `data/reports/phase7a-2026-08-05/profile-context-field-registry.json`
- `data/reports/phase7a-2026-08-05/tfc-ofc-crosswalk.json`
- `data/reports/phase7a-2026-08-05/phase7b-deep-probe-protocol.json`
- `data/reports/phase7a-2026-08-05/decision-summary.json`
- `data/reports/phase7a-2026-08-05/manifest.json`
