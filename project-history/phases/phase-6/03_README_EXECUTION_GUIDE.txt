KONSIDER PHASE 6D–6I IMPLEMENTATION PROMPT PACK
Opportunity Filters: contracts, evidence, API, UI, release and closure

GUIDE FILE

`03_README_EXECUTION_GUIDE.txt`

PURPOSE

This prompt pack implements the nine career and education Opportunity Filters approved by the
Phase 6B.1 and Phase 6C research.

Run the prompts sequentially. Review and accept the output of each prompt before starting the next.

The prompts deliberately separate:

1. product and data contracts;
2. career evidence onboarding;
3. education evidence onboarding;
4. filtering engine and API;
5. UI and user explanations; and
6. final release publication, verification and closure.

This keeps the implementation consistent with the staged approach used in Phases 4 and 5 and
prevents source onboarding, ranking behavior, API contracts and UI behavior from being changed in
one unreviewable step.

NAMING DECISION

Use the public/product name:

    Opportunity Filters

Do not present these to users as “criteria,” because users already understand criteria as weighted
inputs that change affinity score and ordering.

Use these internal names:

- `OpportunityFilterDefinition`
- `OpportunityFilterEvidence`
- `OpportunityFilterState`
- `OpportunityFilterAssessment`
- shorthand: `OFC`

“Opportunity Filter Criterion” may appear in architecture documentation when expanding OFC, but
runtime and UI names should prefer “Opportunity Filter.”

IMPORTANT TAXONOMY RULE

OFC is not the same kind of classification as FCC, PCC or LSC.

- FCC/PCC describe coverage behavior for ordering criteria.
- LSC describes locality-derived scope.
- OFC describes product behavior: filter-only, never score-bearing.

Model these dimensions orthogonally. Do not add OFC as another value to a single enum that currently
mixes coverage and scope concepts.

PUBLIC STATE ENUM

Use exactly these three public states:

- `VERIFIED_STRONG_SIGNAL`
- `STRONG_SIGNAL_NOT_ESTABLISHED`
- `INSUFFICIENT_EVIDENCE`

Do not add `STRONG_NEGATIVE_EVIDENCE`, `NO_OPPORTUNITY`, `WEAK_OPPORTUNITY`, or equivalent states.

Meaning:

- `VERIFIED_STRONG_SIGNAL`: reproducible evidence crosses the frozen strong-ecosystem rule.
- `STRONG_SIGNAL_NOT_ESTABLISHED`: sufficiently complete evidence was assessed, but the strong
  threshold was not crossed. This does not mean that no opportunity exists.
- `INSUFFICIENT_EVIDENCE`: evidence is absent, stale, incomplete, too broad, incompatible,
  legally unusable, or otherwise insufficient to make either conclusion.

INITIAL FILTER SEMANTICS

Implement one simple mode only:

- selected filters are all required;
- a country passes a selected filter only when its state is `VERIFIED_STRONG_SIGNAL`;
- `STRONG_SIGNAL_NOT_ESTABLISHED` and `INSUFFICIENT_EVIDENCE` both exclude the country under a
  strict filter;
- the exclusion explanation must distinguish those two states;
- multiple selected filters use AND semantics;
- no selected filter preserves current behavior exactly;
- filters never change affinity score;
- filters never change ordering among countries that remain;
- filters never participate in PCC missing-union calculations;
- filters never cause imputation;
- an empty result set is valid and must not silently fall back to unfiltered results.

APPROVED PORTFOLIO

Career:

1. Technology and software employment ecosystem
   - assessable: 63/91
   - P60 states: 20 verified, 43 not established, 28 insufficient

2. Science and engineering employment ecosystem
   - assessable: 67/91
   - P60 states: 20 verified, 47 not established, 24 insufficient

3. Care-sector employment ecosystem
   - assessable: 88/91
   - P60 states: 27 verified, 61 not established, 3 insufficient

4. Finance and insurance employment ecosystem
   - assessable: 88/91
   - P60 states: 22 verified, 66 not established, 3 insufficient

5. Skilled-trades or construction employment ecosystem
   - assessable: 88/91
   - P60 states: 34 verified, 54 not established, 3 insufficient
   - the evidence must retain whether the country passed through skilled trades, construction, or
     both.

Education/research-university ecosystems:

6. Physical sciences and engineering research-university ecosystem
   - assessable: 75/91
   - P60 states: 27 verified, 48 not established, 16 insufficient

7. Mathematics and computer science research-university ecosystem
   - assessable: 75/91
   - P60 states: 30 verified, 45 not established, 16 insufficient

8. Biomedical and health sciences research-university ecosystem
   - assessable: 75/91
   - P60 states: 30 verified, 45 not established, 16 insufficient

9. Life and earth sciences research-university ecosystem
   - assessable: 75/91
   - P60 states: 31 verified, 44 not established, 16 insufficient

EXECUTION ORDER

1. `04_PHASE_6D_OFC_PRODUCT_CONTRACTS_AND_ARCHITECTURE.txt`
2. `05_PHASE_6E_CAREER_OFC_EVIDENCE_ONBOARDING.txt`
3. `06_PHASE_6F_EDUCATION_OFC_EVIDENCE_ONBOARDING.txt`
4. `07_PHASE_6G_OFC_FILTER_ENGINE_AND_API.txt`
5. `08_PHASE_6H_OFC_UI_AND_EXPLANATIONS.txt`
6. `09_PHASE_6I_RELEASE_VERIFICATION_AND_CLOSURE.txt`

GLOBAL RULES FOR EVERY PROMPT

- Start from the latest `main`.
- Inspect the working tree before editing.
- Treat current repository contracts as authoritative where they have moved beyond research docs.
- Preserve the stable 91-country universe.
- Preserve all existing ordering criteria, weights, scores and ranking policies.
- Preserve Phase 4 complete-case/PCC behavior.
- Preserve Phase 5 coverage/locality/profile assessment separation.
- Do not revive `/api/v1`.
- Do not create backward-compatibility aliases unless an active supported client requires them and
  the owner approves them explicitly.
- Do not use research-history scripts directly as production runtime dependencies.
- Extract reusable production logic where appropriate while retaining deterministic research replay.
- Use immutable versioned releases.
- Retain source identity, licensing, hashes, thresholds, reason codes and explicit missingness.
- Never claim vacancies, hiring probability, admission probability, teaching quality, licensing,
  qualification recognition, visa access, salary, affordability or applicant success.
- Commit after each accepted phase with a clear commit message.
- Stop at the stated stop condition for each prompt.
