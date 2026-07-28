# Phase 3 closure report

Status: complete

Closed: 2026-07-26

Phase 3 expanded Konsider's evidence base while preserving the stable 91-country universe,
deterministic scoring, immutable releases, explicit missing-data outcomes, and conservative source
and licensing rules. It began with an 84-item search space and ended with three new
production-ready criteria. Active release `2026-07-27.1` publishes nine criteria, eight of which
are enabled for ranking.

This report distinguishes measured results from policy decisions. Measured coverage, freshness,
parsing, validation, and replay outcomes come from committed probe or release artifacts. Portfolio
labels, scoring semantics, and implementation order are Konsider decisions.

## Research funnel

| Stage | Scope | Outcome |
| --- | ---: | --- |
| Phase 3A framework | 84 candidate criteria | Established authority, licensing, comparability, coverage, freshness, granularity, scoring, and operational gates. |
| Phase 3B lightweight screen | 84/84 | Retained 42 for prioritized deeper research; classified all 84 by feasibility, natural granularity, and priority. |
| Phase 3C deep research | 45 unique criteria in three 15-item batches | Seven deterministic probe candidates, 15 conditional/experimental candidates, 20 deferrals, and three rejections at the batch-decision stage. |
| Phase 3D framework proof | Two fixture-backed examples | Proved country mapping, explicit missing outcomes, raw capture, deterministic reporting, and offline replay without publication. |
| Phase 3E measured probes | Seven live candidates | All passed the 82/91 research threshold; four were production candidates, two experimental, and one reserve. |
| Phase 3F portfolio decision | Consolidated 3A–3E evidence | Approved the portfolio guardrails and a staged implementation order. |
| Phase 3G-0 final probes | Four unresolved candidates | Three exact live probes completed; one source lacked a stable machine archive. None was promoted in 3G-1. |
| Phase 3G-1 production | Three globally complete candidates | Added political stability, rule of law, and established immigrant presence at 91/91. |

The 45 deeply researched criteria were:

- Batch 1: C11, C32, C33, C17, C21, C25, C50, C40, C01, C30, C12, C58, C56,
  C08, and C66.
- Batch 2: C38, C35, C36, C34, C05, C15, C13, C14, C16, C19, C22, C26, C29,
  C48, and C49.
- Batch 3: C53, C71, C76, C54, C67, C62, C68, C06, C75, C70, C78, C42, C57,
  C45, and C69.

The other 39 candidates retain their Phase 3B screening rows. They were not silently rejected:
their preliminary feasibility, granularity, and priority evidence remains available for later
portfolio, city, occupation, or profile work.

## Screening and probe methodology

Phase 3A and 3B used a funnel rather than treating all 84 candidates as equally expensive:

1. Confirm the construct and the relocation decision it might support.
2. Identify authoritative publisher and dataset families.
3. Estimate cross-country comparability, stable-91 coverage, freshness, and licensing uncertainty.
4. Classify the natural unit as national, city/regional, preference-based, profile-derived, or
   unsuitable as an independent criterion.
5. Prioritize only candidates with sufficient decision value and a plausible evidence path.
6. Deeply research exact series, editions, access paths, reuse terms, country mapping, scoring
   direction, redundancy, maintenance burden, and known blockers.
7. Run deterministic live probes only after a source and narrow construct were approved.
8. Promote only candidates that passed production validation and semantic guardrails.

The normal research threshold was at least 82 valid countries out of 91. That threshold authorized
further research; it was not automatic production approval. The 3G-1 publication retained 91/91
coverage for every enabled criterion.

## Sources probed

Phase 3D used schema-faithful fixture examples for World Bank JSON and ILOSTAT CSV. These proved the
framework only and were never treated as live source evidence.

Ten candidates received exact live source probes:

| Candidate construct | Exact publisher/distribution family | Verified valid coverage | Final Phase 3 disposition |
| --- | --- | ---: | --- |
| School education quality | World Bank Human Capital Project/HCI Plus | 87/91 | Experimental, conditional complete-case candidate |
| Overall job-market opportunity | ILOSTAT bulk CSV | 88/91 | Conditional complete-case candidate |
| Established immigrant presence | World Bank WDI | 91/91 | Added to production |
| Macroeconomic stability | World Bank WDI | 91/91 | Experimental future candidate |
| Political stability | World Bank WGI | 91/91 | Added to production |
| Rule of law | World Bank WGI | 91/91 | Added to production |
| Basic water and sanitation access | WHO/UNICEF JMP via World Bank WDI | 86/91 | Reserve |
| Financial protection from health costs | WHO Global Health Expenditure Database | 90/91 | Conditional; Ukraine was stale |
| Extreme-weather risk | EU/JRC INFORM Risk 2026 | 91/91 | Experimental; source-chain and local-variation review remains |
| Working-time burden | ILOSTAT bulk CSV | 72/91 fresh | Reserve; below the research threshold |

Naturalisation accessibility was also investigated through GLOBALCIT. Publisher scope and licence
evidence were verified, but a stable version-pinned machine archive could not be resolved, so no
synthetic or substitute probe was reported.

## Final portfolio dispositions

### Production additions

- Political stability: World Bank WGI 2024 estimate, with standard error and 90% confidence bounds
  retained.
- Rule of law: World Bank WGI 2024 estimate, with the same uncertainty treatment and an explicit
  redundancy diagnostic against political stability.
- Established immigrant presence: international migrant stock as a share of population, presented
  as a user preference rather than universal country quality.

All three have 91/91 valid observations in active release `2026-07-27.1`.

### Experimental or conditional future candidates

- Macroeconomic stability: complete coverage, but component weighting, currency regimes, and break
  handling must be fixed before production.
- School education quality: 87/91; the exact schooling construct and model interpretation remain
  experimental.
- Overall job-market opportunity: 88/91; requires conditional complete-case product capability and
  a final composite-versus-components decision.
- Financial protection from health costs: 90/91; conditional because one country is stale.
- Extreme-weather risk: 91/91, but component-chain licensing, weighting, redundancy, and national
  versus local exposure require resolution.

### Reserve

- Basic water and sanitation access: 86/91 and weakly discriminating among likely destinations.
- Working-time burden: 72/91 fresh, below the normal research threshold.
- Research and innovation ecosystem, entrepreneurship activity, and social-protection reach:
  retained as researched reserves rather than promoted on estimated evidence.

### Deferred

- Profile/legal layer: skilled-work visas, permanent residence, post-study pathways, family
  reunification, professional licensing, tax and contribution burdens, family friendliness,
  retirement suitability, and profile composites.
- City/occupation layer: housing affordability, English usability, occupation-specific jobs,
  water-supply reliability, public transport, international connectivity, urban quality of life,
  and recreation/culture.
- Naturalisation accessibility: context/legal research until a stable reproducible archive and
  transparent current-law methodology are available.
- Other researched deferrals remain in the three Phase 3C batch reports; lack of promotion is not
  deletion of evidence.

### Rejected as current independent production criteria

- Employment protection and worker rights: the candidate source warns against the required country
  comparison and did not support a defensible scalar score.
- LGBTQ+ legal/social inclusion: the selected current source is non-commercial.
- Broad environmental-quality composite: the candidate source is non-commercial and the construct
  has substantial definition, redundancy, and local-variation problems.

Rejection is source-and-construct specific. A materially different, production-compatible source
may justify a future re-evaluation.

## Production result

Active release `2026-07-27.1` has:

- 91 countries;
- nine published criteria;
- eight enabled, product-ready ranking criteria;
- 819 observations and 819 canonical scores;
- 91 expected blockers, all belonging to the visible but stale UHC criterion;
- zero validation errors; and
- successful offline replay from retained content-addressed raw artifacts.

Political stability and rule of law have an average-rank Spearman correlation of 0.7295. That is
material enough to disclose but below the pre-set 0.90 redundancy-review threshold.

## Guardrails retained

- Authoritative, exact source distributions are required; publisher reputation alone is
  insufficient.
- Dataset-specific production reuse evidence is required. Ambiguous licensing blocks promotion.
- Missing and stale observations remain explicit. Fixtures, proxies, and silent imputation never
  fill production gaps.
- Partial-country scoring remains prohibited. Any future conditional criterion must use a
  complete-case country set in which every ranked country has every active criterion.
- Freshness is criterion-specific and edition-aware; an old observation is not made current by a
  recent download date.
- National criteria cannot claim city, neighbourhood, occupation, household, or applicant-level
  precision.
- Preference properties are not universal quality measures.
- Composites require visible components, fixed versioned transformations, sensitivity checks, and
  redundancy review.
- Survey and perception indicators retain uncertainty and cannot support false precision.
- Every catalog-enabled criterion must pass release validation before the active pointer can move.

## Limitations

- The enabled portfolio is eight, below the aspirational mature target of roughly 10–15; Phase 3
  chose evidence quality over criterion count.
- UHC remains unavailable because 2021 observations fail freshness.
- Infrastructure remains experimental and contains mixed reference years.
- WGI measures are perception-based national composites.
- Immigrant presence does not measure acceptance, integration quality, government support, or visa
  accessibility.
- The product does not yet support conditional country universes, city/occupation layers, or
  applicant-specific legal pathways.
- Source refresh is manual, and raw third-party bytes remain local and intentionally excluded from
  Git.

## Refresh recommendations

1. Refresh the nine registered production sources on their documented edition cadence and publish
   only under a new immutable release ID.
2. Re-run full validation, replay, scoring-sensitivity, and WGI redundancy diagnostics on every
   refresh.
3. Revisit UHC when a newer official observation becomes available; do not relax freshness merely
   to enable it.
4. Watch for revised WGI workbooks and WDI migrant-stock editions, pinning the exact workbook,
   sheet, series, year, licence evidence, and attribution.
5. Re-probe conditional/reserve candidates only after a new edition or source materially changes a
   recorded blocker.
6. Require an explicit product design before enabling any criterion that reduces the 91-country
   complete-case set.
7. Keep rejected and deferred evidence intact so future reviews compare new facts against recorded
   blockers rather than restarting from memory.

## Evidence retained

- [Phase 3A framework](../../project-history/phases/phase-3/research/framework/phase3a_framework.md)
- [Phase 3B screening](../../project-history/phases/phase-3/research/screening/phase3b_screening.md)
- [Phase 3C Batch 1](../../project-history/phases/phase-3/research/candidate-batch-1/phase3c_batch1.md)
- [Phase 3C Batch 2](../../project-history/phases/phase-3/research/candidate-batch-2/phase3c_batch2.md)
- [Phase 3C Batch 3](../../project-history/phases/phase-3/research/candidate-batch-3/phase3c_batch3.md)
- [Phase 3D framework proof](phase3d-feasibility-probes.md)
- [Phase 3E measured probes](phase3e-deterministic-probes.md)
- [Approved Phase 3F decision](konsider_phase3f_portfolio_decision.md)
- [Phase 3G-0 final probes](phase3g0-final-probes.md)
- [Active release report](../history/releases/2026-07-27.1.md)

Machine-readable screening, batch, probe, source, country-outcome, checksum, and replay artifacts
remain beside those reports. No rejected evidence was removed during closure.

## Closure verification

The Phase 3H documentation update passed:

- all 123 Python tests, including five documentation/link/roadmap checks;
- `ruff check .`;
- `black --check .`; and
- Python bytecode compilation for `src` and `tests`.

The Ruff rule set is now explicit in `pyproject.toml` so the documented gate remains stable across
tool upgrades rather than inheriting a changing tool default.
