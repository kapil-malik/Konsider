# Konsider Phase 5 — Locality-Aware Criteria and Structured Assessment Prompt Pack

## Purpose

This prompt pack is intended to be given to Codex / ChatGPT on the local Konsider repository, one phase at a time.

Phase 5 will add a clean, extensible foundation for locality-specific criteria without weakening the Phase 4 complete-case and uncertainty guarantees. It will explore which of the original 45 deeply researched criteria are genuinely locality-specific, design the data and API contracts, implement locality-derived country scoring, expose transparent locality evidence in the API and UI, onboard only criteria that clear source and licensing gates, and finish with a clean structured contract.

Do not execute all prompts as one task. Complete, test, document, and commit each phase before beginning the next one.

---

# Agreed product and architecture decisions

Treat the following as approved unless repository evidence reveals a direct contradiction that must be raised before implementation.

## 1. Criterion attributes are orthogonal

A criterion has four independent attribute groups:

1. **Core definition**
   - Existing identity, meaning, scoring, caveat, readiness, and experimental attributes.
   - These may remain at the criterion root.

2. **Coverage**
   - Whether the country result is `GLOBAL_CORE`, `CONDITIONAL_COMPLETE_CASE`, or `DIAGNOSTIC_ONLY`.
   - Country outcome counts, stable universe, thresholds, source versions, and score range.
   - Coverage answers: **Can Konsider produce a valid country result?**

3. **Scope**
   - Whether evidence is naturally national, locality-level, or otherwise geographically scoped.
   - How locality evidence is aggregated into a country result.
   - Scope answers: **Where did the country result come from?**

4. **Applicability / profile**
   - Whether the criterion is universal or depends on applicant, occupation, household, visa, licensing, or other future profile inputs.
   - Phase 5 must define clean metadata and response boundaries, but must not implement a full applicant or household profile engine.

Coverage and scope must not be encoded in the same enum or status.

A locality-derived criterion may be an FCC if every country has a valid derived country score. A national criterion may be a PCC if some countries lack usable national data.

## 2. Preserve Phase 4 guarantees

Phase 5 must retain these principles:

- no imputation of missing, stale, invalid, or rejected observations;
- no country-specific weight renormalization;
- every ranked country has every criterion required by that ranking;
- excluded countries retain inspectable evidence but receive no fabricated final score;
- source lineage, scoring versions, checksums, immutable releases, and replay remain mandatory;
- the UI never reimplements ranking, coverage, locality aggregation, or assessment logic.

## 3. Locality-specific criterion behavior

Use the term **Locality-Specific Criterion**, abbreviated `LSC`, in internal design documents unless a better name is justified and consistently adopted.

A locality-derived country score may use the best qualifying locality options under a frozen, versioned aggregation policy. The eligible locality universe must be defined independently and transparently; it must not be selected after observing which cities maximize a desired score.

The default country interpretation is **independent country opportunity**:

> The country contains strong locality options for each selected criterion, even when different criteria are strongest in different localities.

Therefore, when multiple active LSCs point to different localities:

- keep the independently derived country scores;
- do not apply an automatic score penalty;
- calculate and expose locality coherence separately;
- clearly warn when the leading locality evidence does not overlap.

Do not pretend that independently selected localities form one combined destination.

## 4. Locality analysis threshold

Use raw weight `0.6` — Medium — as the default threshold for prominent locality-coherence analysis.

- An FCC LSC with any positive weight may contribute to the aggregate score.
- An LSC below `0.6` must still retain locality provenance in API evidence and detailed UI views.
- An LSC at or above `0.6` participates in prominent locality compatibility analysis.
- PCC activation remains an independent coverage decision. If an LSC is also a PCC, the existing PCC activation and exclusion rules still apply independently.

Do not conflate `pcc_activation_threshold` with `locality_analysis_threshold`, even if both initially equal `0.6`.

## 5. Multiple LSCs

When two or more LSCs are active for locality analysis:

- inspect the full valid locality evidence for those criteria, not only each criterion’s top one or two displayed localities;
- determine whether a common qualifying locality exists;
- expose the best common locality when one exists;
- expose partial overlap or no overlap when appropriate;
- do not alter the country aggregate merely because no common locality exists.

A future profile/household phase may add `PREFERRED` or `REQUIRED` co-location constraints. Phase 5 must leave a clean extension point but must not simulate or infer such constraints.

## 6. Final API shape

Temporary additive compatibility fields are acceptable during intermediate Phase 5 commits only.

By the end of Phase 5:

- remove duplicate and transitional top-level assessment fields;
- keep coverage, locality, and profile/applicability assessments structurally separate;
- expose a clean structure conceptually similar to:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {}
  }
}
```

The exact schema may distinguish response-level and country-level assessments, but it must avoid duplicated sources of truth.

Coverage assessment is primarily ranking-universe-wide. Locality assessment is partly request-wide and partly country-specific. Profile assessment may remain explicitly unevaluated when no applicant profile is supplied.

## 7. Rename current “profiles”

The current catalog “profiles” are weight presets, not applicant profiles.

During Phase 5, migrate them to terminology such as:

- `preference_presets`
- `preference_preset_id`
- `resolved_preference_preset_id`

Reserve `profile` for future applicant or household attributes.

Temporary aliases are allowed only during staged migration and must be removed before Phase 5 closes.

## 8. Historical releases

Do not mutate or delete historical immutable releases or their release-scoped catalog snapshots.

Supporting historical schema loading for replay or audit is different from exposing legacy fields in the active API. Historical compatibility may remain internally where required, but the active release and public API must use the clean Phase 5 contract by closure.

---

# Global execution rules for every Phase 5 prompt

Apply these rules to every phase below:

1. Start from the latest `main` branch and inspect the repository before changing anything.
2. Read the prior phase’s report, ADRs, contracts, and tests.
3. Do not silently reinterpret historical releases.
4. Do not activate a release based on synthetic fixtures.
5. Do not use unlicensed, ambiguously licensed, user-contributed, scraped commercial, or non-reproducible data in production.
6. Prefer official or demonstrably independent sources with explicit production and redistribution support.
7. Keep source feasibility, construct suitability, coverage, freshness, scoring, and licensing as separate gates.
8. No fixtures may fill production data gaps.
9. Preserve deterministic replay and LF-stable serialized artifacts.
10. Keep backend business logic out of FastAPI routes and React components.
11. Add tests at the layer where each rule is owned.
12. Update documentation in the same phase as the behavior it describes.
13. Do not begin the next phase automatically.
14. Finish each phase with:
    - a concise implementation report;
    - all relevant validation commands and results;
    - a clean, reviewable commit;
    - a short list of unresolved decisions or blockers.
15. Do not create one monolithic “Phase 5” commit.

---

# Proposed commit sequence

Use at least the following staggered commits. Large phases may use more than one commit when separation improves reviewability.

| Phase | Expected commit intent |
|---|---|
| 5A | Research and locality-criterion disposition only |
| 5B | ADRs, schemas, contracts, and synthetic contract fixtures |
| 5C | Generic worker/release and geographic-entity foundation |
| 5D | Locality aggregation and deterministic assessment engine |
| 5E | Structured API contract and transport migration |
| 5F | Locality-aware UI and generated client migration |
| 5G-n | One production criterion onboarding per commit and preferably per immutable additive release |
| 5H | Final contract cleanup and removal of transitional fields |
| 5I | Verification, closure report, roadmap, and documentation |

If a production criterion fails a gate, commit its documented disposition separately without adding runtime code.

---
# Phase 5A Prompt — Discovery, classification, and first-wave recommendation

## Objective

Revisit the original 45 deeply researched Phase 3 criteria and determine which ones are:

- inherently locality-specific;
- occupation-specific and locality-sensitive;
- national criteria that would materially improve through locality evidence;
- profile-specific rather than locality-specific;
- unsuitable for locality-derived country scoring.

Explore the source and product feasibility of the locality candidates. Produce an evidence-backed first-wave recommendation. Do not implement runtime behavior.

## Required repository reading

Read at minimum:

- `docs/research/phase3-closure-report.md`
- all Phase 3 batch research documents and their retained historical locations;
- `docs/research/konsider_phase3f_portfolio_decision.md` or its current historical path;
- `docs/history/phase4-closure-report.md`
- `docs/product/roadmap.md`
- current criterion catalog and source registrations;
- current release and API/UI documentation.

Verify exact current paths rather than assuming historical paths have remained unchanged.

## Starting hypotheses to verify, not blindly accept

The previous review identified these likely locality or occupation/locality candidates among the 45:

- C25 Housing affordability
- C40 English usability
- C12 Software and technology jobs
- C13 Medical and healthcare jobs
- C14 Business, finance, and professional-services jobs
- C15 Engineering and skilled technical jobs
- C57 Water-supply reliability
- C17 Average earning potential

Re-evaluate all 45 criteria. Add or remove candidates based on evidence.

## Required analysis

Create a complete 45-row disposition matrix with at least:

- criterion ID and exact name;
- original Phase 3 disposition;
- natural evidence level: country, region/state, metro, city, utility/service area, institution, applicant/profile;
- whether locality materially changes relocation usefulness;
- whether a locality-derived country proxy is semantically defensible;
- whether the criterion is occupation-specific;
- whether it requires applicant or household data;
- recommended locality unit;
- candidate official or independent sources;
- exact source asset or API;
- source publisher and distributor;
- access method;
- licensing and redistribution evidence;
- freshness;
- estimated country coverage;
- estimated locality coverage within covered countries;
- cross-country comparability;
- major construct risks;
- possible aggregation method;
- recommendation:
  - `FIRST_WAVE`
  - `SECOND_WAVE`
  - `RESEARCH_ONLY`
  - `PROFILE_PHASE`
  - `REJECT_LOCALITY_PROXY`
- precise blockers.

## Locality unit study

Compare at least:

- administrative city;
- metropolitan area;
- state/province/region;
- utility/service area where relevant.

Recommend a default locality type per criterion family. Jobs, housing, commuting, and earnings should not automatically use municipal boundaries if metro data is more meaningful.

## Locality universe policy

Propose a versioned locality-universe policy that avoids cherry-picking and excessive large-country advantage.

Evaluate approaches such as:

- fixed number of major metros per country;
- population/economic-threshold inclusion;
- independent relocation-relevance selection;
- a bounded hybrid;
- single-locality treatment for city-states and small countries.

The universe must be chosen independently of final metric scores.

Define:

- inclusion criteria;
- maximum or expected localities per country;
- how small countries are handled;
- how metro aliases and cross-border metros are handled;
- how countries with no qualifying locality are represented;
- how changes to the universe are versioned.

## Source exploration depth

For each serious candidate, distinguish:

1. Conceptually useful source.
2. Technically fetchable source.
3. Reproducible exact source.
4. Legally suitable production source.
5. Sufficiently comparable and fresh source.

Do not promote a criterion because a website or ranking list exists.

## First-wave recommendation

Recommend no more than three first-wave LSCs.

For each recommended criterion provide:

- exact construct;
- exact locality unit;
- candidate source;
- licensing conclusion;
- estimated coverage;
- aggregation proposal;
- expected limitations;
- expected implementation complexity;
- why it adds decision value beyond existing criteria.

Prefer a coherent first wave over maximizing count.

## Required outputs

Create:

- `docs/research/phase5a-locality-criteria-discovery.md`
- a machine-readable matrix under `data/reports/phase5a-*/`
- a short decision summary suitable for later ADRs;
- an update to `docs/product/roadmap.md` that redefines Phase 5 as locality-aware criteria and moves conversational exploration to a later future phase.

Do not change runtime code, contracts, API behavior, UI behavior, or the active release.

## Verification

- Confirm all 45 criteria appear exactly once in the disposition matrix.
- Confirm every first-wave recommendation has explicit source and licensing evidence.
- Confirm profile-dependent criteria are not disguised as locality criteria.
- Confirm no source is described as production-ready without exact-asset verification.

## Commit

Use a focused commit such as:

`docs: complete Phase 5A locality criteria discovery`

Stop after reporting findings and questions.

---
# Phase 5B Prompt — Orthogonal domain model, ADRs, and target contracts

## Dependency

Proceed only after Phase 5A has an approved first-wave recommendation and locality-universe direction.

## Objective

Define the clean Phase 5 target architecture for:

- criterion definition;
- coverage;
- geographic scope;
- applicability/profile metadata;
- locality entities;
- locality observations and scores;
- locality-to-country derivation;
- structured ranking assessments;
- preference presets.

Implement versioned schemas and synthetic contract fixtures, but do not onboard production locality data or activate a new release.

## Architectural requirements

### Criterion representation

Keep existing core criterion fields at the root unless a migration provides clear value.

Add orthogonal objects conceptually equivalent to:

```yaml
coverage:
  mode: GLOBAL_CORE | CONDITIONAL_COMPLETE_CASE | DIAGNOSTIC_ONLY
  ...

scope:
  evidence_level: COUNTRY | LOCALITY
  result_level: COUNTRY
  locality_type: METRO | CITY | REGION | SERVICE_AREA | null
  derivation: DIRECT | AGGREGATED_FROM_LOCALITIES
  locality_universe_id: string | null
  aggregation_policy_id: string | null
  locality_analysis_threshold: number | null

applicability:
  mode: UNIVERSAL | PARAMETERIZED | FUTURE_PROFILE_REQUIRED
  dimensions: []
```

The exact naming may differ, but the dimensions must remain separate.

### Geographic entities

Do not represent localities as unvalidated free-text labels.

Define a canonical geographic entity contract with stable IDs, country parentage, type, display name, and aliases or source mappings as needed.

Evaluate and document whether to:

- generalize observations to an entity-neutral geographic reference; or
- retain separate country and locality observation types.

Choose one through an ADR. Do not overload `country_code` with locality IDs.

### Locality aggregation policy

Define a versioned policy object that can express:

- eligible locality universe;
- source criterion;
- result criterion;
- top-N or other aggregation;
- `N`;
- minimum valid localities;
- score range;
- tie handling;
- treatment of one-locality countries;
- provenance and source lineage;
- policy version.

Do not hard-code `TOP_2_AVERAGE` across domain logic without a policy contract.

### Derived country evidence

A locality-derived country observation or contribution must expose:

- derivation method;
- aggregation policy version;
- contributing localities;
- locality-level input scores or observation references;
- enough lineage to replay the result;
- quality or coverage flags;
- criterion source lineage.

### Multiple source lineage

The current Phase 4 outcome construction assumes one registered source per criterion. Design a clean replacement or extension that supports derived criteria with multiple source inputs without breaking provenance.

Do not collapse multiple inputs into an opaque synthetic source string.

### Preference presets

Rename current weight-only “profiles” in the target contract to `preference_presets`.

Reserve profile terminology for future applicant and household context.

### Assessments

Define the final target response model with no duplicated sources of truth.

At minimum, model:

- response-level coverage assessment;
- response-level locality assessment summary and policy;
- response-level profile assessment;
- country-level locality assessment;
- future country-level profile assessment;
- structured reason codes and severity/effect.

The final target should conceptually resemble:

```json
{
  "assessments": {
    "coverage": {},
    "locality": {},
    "profile": {}
  },
  "rankings": [
    {
      "assessments": {
        "locality": {},
        "profile": {}
      }
    }
  ]
}
```

Decide precisely which fields belong globally and which belong per country.

### Locality statuses

Define stable locality assessment statuses. They should cover at least:

- no active locality criteria;
- analysis not triggered because all LSC weights are below threshold;
- one active LSC;
- common locality available;
- partial overlap;
- no common locality;
- insufficient locality evidence.

Avoid embedding coverage status into locality status names.

### Profile status in Phase 5

Phase 5 does not implement applicant profiles.

The contract must be able to state explicitly that profile suitability was not evaluated, for example through a typed status such as `NO_PROFILE_CONTEXT` or `NOT_EVALUATED`.

Do not add fake user-profile defaults.

## Versioning and migration design

Recommend explicit target versions for:

- release schema;
- consumer catalog;
- API/OpenAPI contract;
- generated TypeScript types.

A new major version is expected because geographic subject modeling and response restructuring are materially different.

Historical release loading may remain internally, but the active target contract must be clean.

Define:

- temporary migration fields, if any;
- exact phase in which each temporary field is removed;
- how old release snapshots remain inspectable;
- how the active release migrates.

## Required implementation

- Add ADRs under `docs/architecture/decisions/`.
- Add versioned JSON schemas or equivalent typed contracts.
- Add synthetic valid and invalid contract fixtures.
- Add schema tests for:
  - orthogonality of coverage and scope;
  - canonical locality references;
  - locality-derived evidence;
  - multiple-source lineage;
  - preference preset naming;
  - structured assessment envelopes;
  - rejection of duplicated or contradictory fields.
- Add a Phase 5B design report.

Do not change active production API behavior yet unless a strictly additive contract export is needed for tests. Do not activate a new release.

## Commit

Use a focused commit such as:

`feat: define Phase 5 locality and assessment contracts`

Stop after presenting the ADR decisions, target schemas, migration plan, and open questions.

---
# Phase 5C Prompt — Generic worker, release, and geographic-entity foundation

## Dependency

Proceed only after Phase 5B contracts and ADRs are approved.

## Objective

Refactor the ingestion and immutable-release pipeline so future national and locality-derived criteria can use one generic, policy-driven path.

Remove the need to create a bespoke Phase-specific release builder for every additional PCC or LSC.

Do not yet implement the full ranking locality-coherence engine or onboard production LSC sources.

## Required worker changes

### Generic schema-current refresh

The normal refresh/build path must support:

- global-core criteria;
- conditional complete-case criteria;
- diagnostic-only criteria;
- country observations;
- locality observations;
- derived country observations;
- explicit outcomes;
- criterion coverage metadata;
- scope and applicability metadata;
- immutable release and catalog snapshots.

The current generic refresh path must no longer fall back to older complete-matrix semantics for active schema-current releases.

### Policy-driven criterion registry

Move criterion behavior out of Phase-specific onboarding modules and into versioned registry/configuration where practical.

The registry or policy model must make it possible to declare:

- criterion ID;
- source registrations;
- parser;
- scoring method;
- coverage policy;
- scope policy;
- derivation policy;
- applicability metadata;
- readiness and experimental status.

Do not force every source or parser into generic configuration when hard-coded parsing is clearer. The goal is generic orchestration and contracts, not eliminating criterion-specific transformation code.

### Geographic entity registry

Implement the approved locality/entity registry and validation.

Require:

- stable entity IDs;
- entity type;
- display name;
- parent country;
- canonical source mappings where required;
- versioned locality universe membership.

### Observation and outcome model

Implement the approved geographic observation model.

Ensure:

- locality observations cannot masquerade as country observations;
- derived country observations reference locality inputs;
- exact source lineage is retained;
- non-valid outcomes have normalized reason codes;
- result entities are explicit;
- score existence reconciles with valid result outcomes.

Decide whether explicit outcomes are required at both locality and country-result levels. Implement the ADR decision and test it.

### Multiple-source support

Remove the one-source-per-criterion restriction from the generic outcome/derivation path.

Require deterministic source lineage for every output.

### Release validation

Extend structural validation to prove:

- criterion coverage and scope are independent;
- every declared geographic entity exists;
- locality observations belong to the declared universe;
- derived country results reference valid locality inputs;
- aggregation policy versions match;
- score ranges and methods match;
- coverage counts reconcile;
- catalog, validation, and manifest metadata agree;
- historical releases remain immutable.

### Replay

Replay must regenerate:

- locality observations;
- derived country observations;
- country outcomes;
- scores;
- derivation evidence;

and compare them deterministically with the published release.

## Migration of Phase 4 specialized builders

Do not delete historical reports.

Where safe:

- refactor reusable logic from `phase4f.py` and `phase4_wave2.py` into the generic pipeline;
- preserve tests that prove existing release semantics;
- mark or remove obsolete builder code only when equivalent generic tests exist.

Do not rewrite historical release bytes.

## Required tests

Add:

- unit tests for entity validation and lineage;
- schema-current worker tests with synthetic national FCC, national PCC, locality FCC, and locality PCC criteria;
- invalid fixtures for broken locality parentage, undeclared locality, broken aggregation lineage, contradictory scope/coverage, and multiple-source mismatch;
- deterministic replay tests;
- historical release load tests;
- clean-checkout behavior tests that respect intentionally uncommitted licensed bytes.

## Documentation

Update worker and release-format documentation.

Create a Phase 5C implementation report explaining:

- generic orchestration;
- entity model;
- release contents;
- outcome semantics;
- source lineage;
- replay;
- migration from special onboarding modules.

## Commit

Use a focused commit such as:

`refactor: generalize releases for locality-aware criteria`

Stop after tests and report. Do not proceed to ranking behavior.

---
# Phase 5D Prompt — Locality aggregation and deterministic assessment engine

## Dependency

Proceed only after Phase 5C can build and load synthetic locality-aware releases.

## Objective

Implement deterministic locality-to-country scoring and locality-coherence assessments in the domain/service layer using synthetic fixtures.

Do not change production sources or activate a production locality release.

## Country score derivation

For each locality-derived criterion:

1. Load every valid locality score in the criterion’s declared locality universe.
2. Apply the versioned aggregation policy.
3. Produce a country result with complete derivation evidence.
4. Produce no country score if the policy’s minimum-valid-locality requirement is not met.
5. Emit a normalized country outcome and reason codes.

Support at least the approved first policy, expected to be a top-N average, without making the engine specific to one criterion.

Define deterministic handling for:

- one qualifying locality;
- fewer localities than configured `N` but at least the declared minimum;
- ties;
- no qualifying locality;
- invalid or stale locality input;
- locality outside the frozen universe;
- score precision.

## Independent country opportunity

The normal country affinity calculation must use each LSC’s derived country score independently.

Example:

- software criterion may derive from Seattle and San Francisco;
- medical criterion may derive from Phoenix and Boston;
- the United States remains eligible and receives both criterion contributions if both country results are valid.

Do not penalize or exclude the country solely because the contributing localities differ.

## Locality analysis activation

Define:

```text
active locality criterion =
  ready locality-derived criterion
  AND raw weight >= locality_analysis_threshold
  AND active under its independent coverage policy
```

An FCC LSC below the locality threshold still contributes when its weight is positive.

A PCC LSC obeys both the coverage activation policy and the locality threshold independently.

Expose:

- all locality-derived criteria contributing to the score;
- active LSCs participating in locality analysis;
- below-threshold locality criteria;
- threshold and reason codes.

## Multiple active LSC assessment

When two or more LSCs are active:

- inspect all valid localities for each criterion;
- do not intersect only the displayed top-N contributing locality list;
- determine complete common locality availability;
- determine partial overlap where useful;
- calculate the best common locality using a documented deterministic method;
- retain independent country scoring regardless of overlap status.

The best common locality calculation must use the same relevant criterion weights for that locality comparison and must not replace the country aggregate.

## Required locality statuses

Implement the approved typed statuses from Phase 5B, covering at least:

- no active locality criteria;
- analysis not triggered;
- single active LSC;
- common locality available;
- partial locality overlap;
- no common locality;
- insufficient evidence.

Each status must have stable reason codes and an effect classification such as:

- `NONE`
- `INFORMATIONAL`
- `ADVISORY`
- `WARNING`

Do not classify no overlap as a coverage exclusion.

## Profile assessment

Return a typed profile assessment indicating that no applicant or household profile was evaluated.

Do not accept occupation, spouse, visa, age, citizenship, licensing, or co-location requirement fields in Phase 5D.

Document how a future profile engine could introduce `PREFERRED` and `REQUIRED` co-location constraints without changing locality evidence.

## Interaction with coverage assessment

Coverage remains responsible for:

- PCC activation;
- country exclusion;
- eligible universe;
- robustness;
- coverage-limit fallback.

Locality remains responsible for:

- contributing locality provenance;
- common-locality analysis;
- advisory interpretation.

Add invariant tests that prove one assessment cannot silently alter the other.

## Synthetic golden scenarios

Cover at least:

1. National FCC only.
2. One FCC LSC at Low.
3. One FCC LSC at Medium.
4. One PCC LSC below its coverage threshold.
5. One PCC LSC active with missing countries.
6. Two active LSCs with the same leading locality.
7. Two active LSCs with a common locality outside one criterion’s displayed top-N.
8. Two active LSCs with partial overlap.
9. Two active LSCs with no overlap.
10. Three active LSCs with one common locality.
11. Three active LSCs with pairwise but no three-way overlap.
12. Country with one qualifying locality.
13. Country with insufficient locality evidence.
14. Coverage exclusion plus independent locality warning.
15. Tie and precision scenarios.

Prove:

- country aggregate is unchanged by advisory overlap status;
- all country results use one normalized criterion-weight vector;
- no partial country aggregate is fabricated;
- locality assessment uses the full valid locality universe;
- provenance reconciles with the release;
- deterministic order and replay.

## Documentation

Create:

- locality scoring policy documentation;
- locality assessment policy documentation;
- Phase 5D verification report.

## Commit

Use a focused commit such as:

`feat: add deterministic locality aggregation and assessment`

Stop after synthetic engine verification.

---
# Phase 5E Prompt — Structured API contract and transport migration

## Dependency

Proceed only after Phase 5D domain outputs are stable and fully typed.

## Objective

Expose coverage, locality, and profile assessments through a clean versioned API contract.

A temporary migration layer may exist during this phase, but all temporary aliases must be explicitly listed for removal in Phase 5H.

## API versioning

Implement the Phase 5B versioning decision.

Because this is a material contract change, prefer a clear major-version boundary over silently changing semantics.

Do not maintain two indefinitely supported public contracts.

## Catalog response

Each criterion must expose:

- existing core attributes;
- `coverage`;
- `scope`;
- `applicability`;
- source metadata;
- readiness and experimental state;
- locality analysis threshold where applicable;
- aggregation policy identity where applicable.

Do not flatten coverage and locality fields into one collection.

Rename:

- `profiles` to `preference_presets`;
- `profile_id` to `preference_preset_id`;
- `resolved_profile_id` to `resolved_preference_preset_id`.

Any temporary aliases must be deprecated and scheduled for Phase 5H removal.

## Ranking response

Design a single authoritative structure.

At response level expose:

```json
{
  "assessments": {
    "coverage": {
      "...": "ranking-universe-wide coverage state"
    },
    "locality": {
      "...": "request-wide locality policy and summary"
    },
    "profile": {
      "status": "NO_PROFILE_CONTEXT"
    }
  }
}
```

At country row level expose:

- country-specific locality assessment;
- contributing localities for each locality-derived contribution;
- best common locality where available;
- reason codes;
- advisory effect;
- no applicant-profile inference.

Do not duplicate the same status both at the root and in `assessments`.

## Contribution response

A locality-derived contribution must expose:

- source/result scope;
- derivation type;
- aggregation policy;
- locality universe;
- contributing localities;
- locality input scores or references;
- source lineage;
- scoring and observation versions.

A national contribution should use the same general contract without fake locality arrays.

## Excluded-country response

Coverage-excluded countries must continue to expose:

- baseline evidence;
- unavailable criteria;
- exact outcomes and reason codes;
- no final aggregate.

Where available, retain locality evidence for non-excluded criteria.

Do not label a country coverage-excluded merely because its locality criteria have no common city if independent country results are valid.

## Comparison response

Support:

- available and unavailable criterion cells;
- locality-derived criterion provenance;
- per-country locality assessment;
- common-locality evidence;
- no fabricated partial aggregate;
- no client-side intersection logic.

## Country-details response

Extend country details so that locality-derived criteria clearly show:

- contributing localities;
- aggregation method;
- locality observations;
- common-locality advisory context where relevant.

Also expose unavailable active criterion outcomes and reason codes directly rather than requiring the UI to recover them from a separate ranking response.

## OpenAPI and generated client

- Export authoritative OpenAPI.
- Regenerate TypeScript types.
- Add contract tests proving generated types match.
- Reject undocumented fields through strict models.
- Test every locality status and coverage status combination that is valid.
- Test invalid cross-domain combinations.

## Transitional fields

Produce an explicit table in the Phase 5E report:

| Temporary field/route | Replacement | Removal phase |
|---|---|---|
| ... | ... | 5H |

No temporary field may survive Phase 5H.

## Commit

Use a focused commit such as:

`feat: expose structured coverage and locality assessments`

Stop after API tests, generated types, and migration report.

---
# Phase 5F Prompt — Locality-aware React UI

## Dependency

Proceed only after Phase 5E OpenAPI and generated TypeScript contracts are stable.

## Objective

Update the React UI to present locality-derived criteria and structured assessments without reproducing business logic.

## Criterion controls

For each criterion display API-driven indicators for:

- complete or limited coverage;
- national or locality-derived scope;
- experimental state;
- locality coverage count where meaningful;
- locality analysis threshold;
- whether the current draft weight will trigger locality analysis.

At Low or Very Low:

- do not show a prominent locality-coherence warning;
- keep a subtle “Locality-derived” marker;
- retain provenance in details.

At Medium or above:

- clearly state that locality compatibility will be assessed when applied.

Do not infer this from category names.

## Ranking summary

Render the separate assessment domains:

1. Coverage status.
2. Locality status summary.
3. Profile status.

Avoid a single combined warning string.

Coverage warnings must retain their current prominence and meaning.

Locality warnings must not imply that countries were excluded unless coverage actually excluded them.

## Ranked country rows/cards

For a country with active LSCs, show:

- a concise locality status;
- contributing locality names where space permits;
- a link or expansion for full locality evidence;
- best common locality if available;
- a clear advisory when strong criteria come from different localities.

Example product wording:

> Strong options exist across the selected criteria, but the leading evidence comes from different metropolitan areas.

Do not reduce the affinity score solely because this advisory exists.

## Detailed score view

For each locality-derived contribution show:

- country-level criterion score;
- derivation label;
- contributing localities;
- locality-level scores;
- aggregation policy;
- source and period;
- caveats.

## Country details

Display:

- direct national metrics;
- locality-derived metrics;
- unavailable criteria and reason codes;
- locality assessment;
- best common locality or no-overlap explanation.

Do not show “Not ranked” for a locality advisory unless coverage or a future required profile constraint actually removes ranking eligibility.

## Comparison UI

Support side-by-side display of:

- country aggregate;
- criterion scores;
- contributing localities;
- locality status;
- common-locality evidence;
- unavailable cells;
- coverage exclusions.

Keep mobile and desktop behavior accessible and responsive.

## Data and sources view

Include:

- scope;
- locality universe;
- aggregation method;
- source lineage;
- coverage;
- applicability;
- experimental status.

## Accessibility and testing

Add component and browser scenarios for:

- no LSC;
- one Low LSC;
- one active LSC;
- common locality;
- partial overlap;
- no common locality;
- insufficient locality evidence;
- simultaneous coverage warning and locality advisory;
- excluded country details;
- mobile layouts;
- generated-type contract failures.

Use icons and text, not color alone.

## No browser business logic

The browser must not:

- select top localities;
- calculate intersections;
- calculate best common locality;
- determine statuses;
- adjust affinity scores;
- infer profile constraints.

## Commit

Use a focused commit such as:

`feat: render locality-aware rankings and evidence`

Stop after UI verification and screenshots/test evidence in the Phase 5F report.

---
# Phase 5G Prompt — Production onboarding of C66 Extreme heat exposure

## Usage

Run this prompt for the Phase 5A-approved first-wave criterion C66.

Do not onboard multiple new LSCs in one commit.

Prefer one additive immutable release per successfully onboarded criterion so coverage, ranking movement, locality behavior, and rollback remain attributable.

Instantiated values:

- Criterion ID: `C66`
- Criterion name: `Extreme heat exposure`
- Phase 5A decision reference:
  `docs/research/phase5a-locality-criteria-discovery.md#first-wave-recommendation-c66-narrowed-to-extreme-heat-exposure`

## Objective

Onboard `Extreme heat exposure` (`C66`) through the generic Phase 5 pipeline only if it independently clears source, licensing, construct, coverage, freshness, scoring, locality-universe, replay, and product-value gates.

## Precondition

Read:

- `docs/research/phase5a-locality-criteria-discovery.md#first-wave-recommendation-c66-narrowed-to-extreme-heat-exposure`
- Phase 5B ADRs;
- Phase 5C worker contract;
- Phase 5D scoring and locality assessment policy;
- Phase 5E API contract;
- current active release.

Revalidate the exact source asset and terms. Do not rely solely on the earlier research date.

## Required source freeze

Freeze and document:

- publisher;
- distributor;
- exact asset/API;
- URL;
- access method;
- dataset version;
- source version;
- reference period;
- update frequency;
- methodology;
- licence name and URL;
- commercial use;
- redistribution;
- attribution;
- third-party component boundary;
- raw-byte retention policy;
- parser version.

If any legal or exact-asset condition remains ambiguous, do not production-onboard. Produce a held disposition report and a docs-only commit.

## Construct freeze

Define precisely:

- what the criterion measures;
- what it does not measure;
- locality type;
- locality universe version;
- occupation mapping if applicable;
- raw unit;
- direction;
- freshness threshold;
- valid/missing/stale/invalid/rejected rules;
- locality scoring method;
- country aggregation method;
- minimum qualifying localities;
- score bands or transform;
- experimental status;
- expected caveats.

## Parser and locality mapping

Implement:

- exact reproducible parser;
- source-locality to canonical-locality mapping;
- duplicate and ambiguous locality rejection;
- country parent validation;
- quality flags;
- source-record provenance;
- deterministic ordering.

No fuzzy mapping may silently publish. Ambiguous mappings must be explicit and reviewable.

## Coverage evaluation

Report separately:

- source locality count;
- mapped locality count;
- valid locality count;
- valid countries;
- countries with insufficient locality evidence;
- missing countries;
- stale countries;
- invalid/rejected countries;
- selected coverage mode.

Do not assume an LSC must be a PCC. Choose FCC or PCC solely from valid country-result coverage.

If PCC, apply the existing independent coverage gates.

## Scoring and aggregation validation

Validate:

- score distribution and discrimination;
- sensitivity to top-N choice;
- sensitivity to locality-universe composition;
- small-country treatment;
- large-country advantage;
- correlation with existing criteria;
- contribution and rank movement;
- locality provenance;
- common-locality behavior with already onboarded LSCs.

Reject or retain as diagnostic if the criterion is saturated, unstable, redundant, or semantically misleading.

## Release and activation

If all gates pass:

- build through the generic worker;
- publish a new immutable release;
- publish a release-scoped catalog snapshot;
- replay from retained raw bytes;
- verify checksums;
- verify API and UI against the new criterion;
- update active pointer only after all gates pass.

If source bytes cannot be committed for licensing reasons, preserve the repository’s clean-checkout policy without weakening committed normalized release integrity tests.

## Required report

Create a criterion-specific onboarding report including:

- decision;
- exact source and licence;
- locality universe;
- construct;
- coverage;
- non-valid outcomes;
- scoring;
- sensitivity;
- ranking movement;
- locality assessment examples;
- replay;
- checksums;
- limitations.

## Commit

Successful example:

`feat: onboard Extreme heat exposure locality criterion`

Held example:

`docs: record Extreme heat exposure locality onboarding blockers`

Stop after this single criterion. Do not continue to another criterion automatically.

---
# Phase 5H Prompt — Final migration and removal of transitional compatibility

## Dependency

Proceed only after the approved first-wave locality criteria are either production-onboarded or explicitly held, and the Phase 5F UI works against the structured API.

## Objective

Complete the breaking migration to the clean Phase 5 contract.

Remove temporary aliases, duplicate fields, dual terminology, and old active-runtime paths. Preserve immutable historical releases and any internal historical loader support needed for audit.

## Required cleanup

### Criterion and catalog

Final active criterion representation must have:

- core root attributes;
- `coverage`;
- `scope`;
- `applicability`.

Remove flattened duplicate coverage/scope fields where the structured object is authoritative.

Remove `profiles` terminology for weight presets.

Retain only `preference_presets` and related field names.

### API

Remove all transitional top-level fields superseded by structured assessments, including the old root `uncertainty_status` pattern if its authoritative replacement is `assessments.coverage.status`.

Remove duplicated:

- coverage statuses;
- locality statuses;
- threshold fields;
- active criterion lists;
- reason-code containers;
- resolved preset identifiers.

Retain each concept in exactly one documented location.

Remove temporary legacy request aliases and deprecated routes unless the architecture explicitly requires an internal historical endpoint. Public active API documentation must expose only the clean contract.

### Domain and mapper layer

Remove transitional mapper shims.

Ensure the domain output natively matches the structured concepts rather than constructing both old and new formats.

### Frontend

Remove fallback reads of deprecated properties.

Regenerate types and prove the UI compiles only against the final contract.

### Current active release

Publish or migrate to a schema-current active release using:

- structured criterion metadata;
- locality scope metadata;
- preference presets;
- structured assessment-compatible catalog;
- release-scoped snapshot;
- deterministic replay.

Do not mutate historical release directories.

### Old Phase-specific code

Remove obsolete Phase 4/5 special onboarding runtime code only when:

- the generic worker fully replaces it;
- historical reports remain;
- regression tests prove equivalent historical semantics where required.

Do not delete useful research or closure evidence.

### Profile boundary

The final response must contain a structured profile assessment with an explicit unevaluated/no-context status.

Do not leave ambiguous fields named `profile_id` that still mean weight presets.

Do not implement applicant profile logic in this cleanup phase.

## Contract invariants

Add tests that fail if:

- a legacy and structured field coexist;
- `profile` is used to mean a weight preset;
- coverage and scope enums are mixed;
- locality advisory changes country eligibility;
- profile assessment claims evaluation without profile input;
- API and generated TypeScript disagree;
- UI accesses deprecated properties.

## Documentation

Update:

- API guide;
- release format;
- worker guide;
- UI guide;
- architecture docs;
- migration report.

Include a final removed-field table.

## Commit

Use a focused commit such as:

`refactor: finalize structured Phase 5 contracts`

Stop after confirming no transitional public field remains.

---
# Phase 5I Prompt — End-to-end verification, closure, and roadmap

## Dependency

Proceed only after Phase 5H cleanup is complete and the working tree is clean.

## Objective

Verify Phase 5 end to end, fix defects in small isolated commits, and close the phase with authoritative documentation.

Do not combine unrelated defect fixes with the closure-document commit.

## Verification matrix

Cover the cross-product of:

### Coverage

- FCC only;
- PCC below threshold;
- PCC active with preferred exclusions;
- PCC active with elevated exclusions;
- coverage-limit fallback;
- diagnostic criterion.

### Scope

- national direct;
- locality-derived with one locality;
- locality-derived with top-N;
- insufficient locality evidence;
- one active LSC;
- multiple LSCs with common locality;
- partial overlap;
- no overlap.

### Weights

- zero;
- Very Low;
- Low;
- exactly Medium;
- High;
- Very High;
- all-zero FCC fallback;
- mixed FCC/PCC/LSC combinations.

### API/UI

- ranking;
- baseline;
- exclusions;
- country details;
- comparisons;
- sources view;
- mobile;
- accessibility;
- unavailable release;
- generated contract.

### Profile boundary

- no applicant profile;
- profile assessment explicitly unevaluated;
- no accidental interpretation of preference preset as applicant profile.

## Required invariants

Prove:

1. Coverage, locality, and profile assessments are structurally separate.
2. A criterion can independently be FCC/PCC and national/locality-derived.
3. Every ranked country has every active criterion required by coverage policy.
4. Locality no-overlap does not exclude or penalize a country by default.
5. Locality provenance exists even below the prominent-analysis threshold.
6. Medium activates locality analysis.
7. Common-locality search uses all valid locality evidence, not only displayed top-N contributors.
8. Country aggregate and locality advisory remain independent.
9. No applicant or household assumption is made.
10. No deprecated response field survives.
11. Preference preset terminology is clean.
12. Release, validation, catalog, API, and UI agree.
13. Replay is deterministic.
14. Historical releases remain immutable and inspectable.
15. Production source/licensing gates remain intact.

## CI and reproducibility

Run all repository gates, including:

- backend tests;
- formatting;
- lint/static checks;
- compile checks;
- OpenAPI export;
- generated TypeScript verification;
- frontend type/lint/component/build tests;
- browser tests;
- Windows and Linux clean-checkout CI;
- active release replay where local raw bytes are available;
- committed release integrity where licensed raw bytes are intentionally absent.

Record exact commands and results.

## Defect handling

If verification finds defects:

- fix each coherent defect in a small commit;
- rerun affected and full gates;
- do not conceal skips;
- do not weaken invariants merely to pass CI.

Only after all defects are resolved, create the closure commit.

## Closure documents

Create:

- `docs/history/phase5-closure-report.md`
- Phase 5 verification report under `data/reports/`
- updated `docs/product/roadmap.md`
- updated README/current-position text;
- updated documentation index.

Move conversational exploration to a later phase and state that it must consume the typed deterministic Phase 5 tools.

The closure report must include:

- architecture outcome;
- criterion dispositions from Phase 5A;
- onboarded and held criteria;
- active release inventory;
- coverage results;
- locality universe and policy;
- aggregation methods;
- API contract;
- UI behavior;
- assessment statuses;
- removed compatibility fields;
- tests and CI;
- limitations;
- future profile/household extension points;
- future conversational exploration boundary.

## Final commit

Use a focused closure commit such as:

`docs: close Phase 5 locality-aware criteria`

Report:

- all Phase 5 commits in order;
- active release;
- enabled criteria;
- any held locality criteria;
- final schema/API versions;
- test and CI status;
- remaining risks;
- recommended next phase.

Stop after closure.

---

# Phase 5 exit criteria

Phase 5 is complete only when all of the following are true:

1. All original 45 Phase 3 criteria have a documented locality disposition.
2. A frozen, versioned locality-universe policy exists.
3. Coverage, scope, and applicability are separate criterion dimensions.
4. Current weight “profiles” have been renamed to preference presets.
5. Locality observations and derived country results have deterministic lineage and replay.
6. The generic worker can publish national FCC/PCC and locality FCC/PCC criteria without bespoke Phase-specific release orchestration.
7. Independent country opportunity is implemented.
8. Multiple active LSCs receive common-locality analysis without default score penalty.
9. Medium is the prominent locality-analysis threshold.
10. Full locality provenance remains available below Medium.
11. API responses contain structured coverage, locality, and profile assessments.
12. Country-level locality assessments and contributing localities are available.
13. The UI renders API-owned locality evidence and warnings without calculating them.
14. At least one LSC is either production-onboarded or explicitly held after complete source and licensing exploration; criterion count alone is not an exit requirement.
15. Every temporary compatibility field introduced during Phase 5 has been removed.
16. Historical releases remain immutable.
17. The active release uses the clean Phase 5 contract.
18. Full backend, API, frontend, browser, replay, and clean-checkout verification passes.
19. Phase 5 has multiple reviewable commits rather than a monolithic commit.
20. The closure report clearly separates what Phase 5 solved from future applicant, household, visa, licensing, and conversational work.
