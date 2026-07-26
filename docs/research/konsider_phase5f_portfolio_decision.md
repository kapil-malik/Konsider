# Konsider Phase 5F — Criteria Portfolio and Guardrail Decision

**Status:** Approved by user for Phase 5G execution
**Evidence cutoff:** `main@5215a28`
**Date:** 26 July 2026
**Scope:** Criteria portfolio, publication/readiness guardrails, fallback policy, and Phase 5G implementation order
**Out of scope:** Production code, release publication, API/UI implementation, and legal advice

---

## 1. Executive decision

Phase 5 has produced enough evidence to expand Konsider meaningfully, but not enough to force every important relocation question into a single national score.

The recommended outcome is:

1. Preserve a stable catalog of **91 supported countries**.
2. Replace the current broad experimental infrastructure composite with a narrower and more defensible **Digital connectivity** criterion using its already-published internet-use and fixed-broadband components.
3. Add three globally complete production candidates:
   - **C48 — Political stability**
   - **C49 — Rule of law**
   - **C30 — Established immigrant presence**
4. Add **C29 — Macroeconomic stability** as experimental after its scoring and currency-break rules are fixed.
5. Introduce a tightly controlled **conditional complete-case** mode for high-value criteria with at least 82/91 valid observations:
   - **C11 — Overall job-market opportunity**: 88/91
   - **C08 — School education quality**: 87/91, experimental
6. Run one final bounded probe round before implementing:
   - **C26 — Financial protection from health costs**
   - **C66 — Extreme-weather risk**
   - **C71 — Working-time burden**
   - **C34 — Naturalisation accessibility**, as context/experimental rather than a proxy for visa or permanent-residence eligibility
7. Target **13 enabled criteria** for the mature Phase 5 portfolio, with a possible fourteenth if C71 proves sufficiently discriminating.
8. Do not represent skilled-work visa, permanent residence, family reunification, professional licensing, tax burden, housing, English usability, or occupation-specific jobs as universal country scores. These require a later profile, legal-route, or city layer.
9. Keep source authority, licensing, provenance, replay, and no-Konsider-imputation guardrails unchanged.
10. Do not start full Phase 5G implementation for unprobed candidates. Complete the final four probes first, then implement in the order defined in Section 12.

The central product conclusion is:

> Konsider can become a materially stronger country-comparison product with 11–13 honest criteria, but it cannot responsibly answer “Can I legally move there?” through a single country score. Legal eligibility must remain profile- and route-aware.

---

## 2. Evidence reviewed

This decision is based on the repository state through commit `5215a28`:

- Phase 5A research framework and 84-criterion classification
- Phase 5B screening of all 84 candidates
- Phase 5C deep-research batches 1–3
- Phase 5D deterministic feasibility-probe framework
- Phase 5E exact-source online probes and offline replay
- Current source/licence audit
- Current scoring methodology
- Stable 91-country policy and release rules

Primary repository evidence:

- [`konsider_phase5a/phase5a_framework.md`](../../konsider_phase5a/phase5a_framework.md)
- [`konsider_phase5b/phase5b_screening.md`](../../konsider_phase5b/phase5b_screening.md)
- [`konsider_phase5c_batch1/phase5c_batch1.md`](../../konsider_phase5c_batch1/phase5c_batch1.md)
- [`konsider_phase5c_batch2/phase5c_batch2.md`](../../konsider_phase5c_batch2/phase5c_batch2.md)
- [`konsider_phase5c_batch3/phase5c_batch3.md`](../../konsider_phase5c_batch3/phase5c_batch3.md)
- [`docs/research/phase5d-feasibility-probes.md`](phase5d-feasibility-probes.md)
- [`docs/research/phase5e-deterministic-probes.md`](phase5e-deterministic-probes.md)
- [`data/reports/feasibility-probes/phase5e-deterministic-2026-07-26/report.md`](../../data/reports/feasibility-probes/phase5e-deterministic-2026-07-26/report.md)
- [`docs/data/source-audit.md`](../data/source-audit.md)
- [`docs/data/scoring-methodology.md`](../data/scoring-methodology.md)
- [`docs/data/country-coverage-phase-2d.md`](../data/country-coverage-phase-2d.md)

The latest Phase 5E run measured seven exact candidates:

| Criterion | Valid | Full 91 | Licence | Replay | Phase 5E recommendation |
| --- | ---: | --- | --- | --- | --- |
| C08 School education quality | 87/91 | No | Pass | Pass | Experimental |
| C11 Overall job-market opportunity | 88/91 | No | Pass | Pass | Production candidate |
| C30 Existing immigrant share | 91/91 | Yes | Pass | Pass | Production candidate |
| C29 Currency and macroeconomic stability | 91/91 | Yes | Pass | Pass | Experimental |
| C48 Political stability | 91/91 | Yes | Pass | Pass | Production candidate |
| C49 Rule of law | 91/91 | Yes | Pass | Pass | Production candidate |
| C53 Water quality and sanitation | 86/91 | No | Pass | Pass | Reserve |

These are feasibility results, not production publication approvals.

---

## 3. Decision principles

### 3.1 Decision value is necessary but not sufficient

A criterion should enter ranking only when:

- it answers a clear relocation question;
- its source and licence support production use;
- its construct is cross-country comparable;
- its coverage and freshness are known;
- its scoring direction is defensible;
- it does not duplicate other criteria excessively;
- its limitations can be explained without changing its meaning.

### 3.2 Measured evidence outranks expected feasibility

Phase 5C estimates are useful for selecting probes. Phase 5E measured results govern production decisions where they exist.

Unprobed candidates may be approved for a final probe, but not for production implementation.

### 3.3 The country catalog and the ranking universe are different concepts

The stable catalog should remain 91 countries.

For globally complete criteria, all 91 are ranked.

For explicitly approved conditional criteria, the ranking universe may be the complete-case subset for that query, provided:

- at least 82 countries remain;
- exclusions are shown before and after ranking;
- no missing score is imputed;
- weights are not renormalised differently by country;
- the result reports the exact criterion-specific universe.

### 3.4 A narrow honest label is better than a broad impressive label

Examples:

- `Established immigrant presence`, not `Government support for immigrants`
- `Digital connectivity`, not `Infrastructure readiness`
- `Financial protection from health costs`, not `Healthcare affordability`
- `Working-time burden`, not `Work-life balance`
- `Naturalisation accessibility`, not `Ease of moving and settling`
- `Basic water and sanitation access`, not `Water quality and reliability`

### 3.5 Profile and city questions should remain profile and city questions

The following cannot be made trustworthy merely by finding a convenient global table:

- skilled-work visa eligibility;
- permanent residence;
- family reunification;
- professional licensing;
- effective personal tax;
- housing affordability;
- occupation-specific jobs;
- English usability;
- public transport;
- water continuity.

They should be designed later as route-aware, household-aware, profession-aware, origin-aware, or city-aware tools.

---

## 4. Recommended portfolio

### 4.1 Retain, but narrow, the existing criteria

| Criterion | Decision |
| --- | --- |
| Population-weighted PM2.5 | Retain as production-ready. |
| Household-consumption relative cost | Retain as production-ready broad cost bands. |
| Intentional homicide | Retain as production-ready with comparability caveats. |
| Women’s legal and economic equality | Retain as production-ready; preserve the de jure label. |
| Infrastructure readiness composite | Replace rather than expand. Create a narrower `Digital connectivity` criterion from internet use and fixed broadband. Keep LPI/logistics as metadata or a separate future study. |
| UHC service coverage | Keep diagnostic/non-ready until a fresh, reusable source representation satisfies its rule. Do not count it as enabled. |

The current infrastructure composite mixes digital access and trade/logistics, uses different component years, and has provisional equal weights. Splitting or narrowing it improves meaning without weakening source quality.

### 4.2 Approve for Phase 5G production implementation

#### C48 — Political stability

**Decision:** Approve as a production addition.

- Measured 91/91
- 2024 observation in the WGI 2025 revision
- CC BY 4.0 published aggregates
- Annual update
- Clear higher-is-better direction
- Low retrieval and mapping cost
- High decision value for safety and continuity

Required implementation conditions:

- retain WGI standard error or uncertainty metadata;
- use broad bands, not precise ranks;
- label it as perception-based;
- avoid claiming it directly measures crime, democracy, or immigration policy.

#### C49 — Rule of law

**Decision:** Approve as a production addition, subject to a redundancy gate.

- Measured 91/91
- 2024 observation
- CC BY 4.0 published aggregates
- Annual update
- Clear higher-is-better direction
- High decision value for institutional reliability

Required implementation conditions:

- retain uncertainty;
- narrow the label to `Rule of law`;
- run correlation and marginal-contribution analysis against C48 and existing safety/equality criteria;
- if C48 and C49 are extremely redundant in both values and ranking contribution, retain the more decision-useful one or reduce default weights.

Suggested redundancy gate:

- do not reject solely because correlation is high;
- require a documented decision if absolute Spearman correlation exceeds 0.90;
- compare top/bottom country changes and contribution differences, not correlation alone.

#### C30 — Established immigrant presence

**Decision:** Approve after a semantic and scoring-direction decision.

- Measured 91/91
- Current 2024 observations
- CC BY 4.0
- Annual
- Very low implementation cost
- Directly useful as evidence of an established immigrant population

Rename from `Existing immigrant share` to **Established immigrant presence**.

Do not describe it as:

- government support;
- social acceptance;
- visa accessibility;
- ease of integration;
- quality of immigrant life.

Recommended scoring:

- higher values mean “more established immigrant presence,” not universally “better”;
- enable a positive user weight for people who value an established migrant environment;
- keep the caveat that source definitions may mix country of birth and citizenship and may include publisher estimates.

If the engine cannot yet express “more of this property” without implying universal quality, publish it as experimental until that semantic distinction is supported.

### 4.3 Approve as a global experimental addition

#### C29 — Macroeconomic stability

**Decision:** Approve as experimental after methodology is frozen.

- Measured 91/91
- Current multi-year inflation and official-exchange-rate series
- CC BY 4.0
- Deterministic replay
- High value for financial viability
- Moderate implementation cost

Required methodology:

- rename to `Macroeconomic stability`; do not imply currency attractiveness;
- define inflation instability and exchange-rate volatility separately;
- use a rolling multi-year window;
- detect redenominations, currency changes, pegs and regime breaks;
- publish component contributions;
- test alternative component weights;
- avoid rewarding deflation or currency immobility mechanically;
- retain experimental status for at least one release.

### 4.4 Approve as conditional complete-case additions

#### C11 — Overall job-market opportunity

**Decision:** Approve as a conditional production criterion if the conditional-complete-case policy in Section 8 is adopted.

- Measured 88/91 valid
- Missing: Antigua and Barbuda, Grenada
- Stale: Ukraine
- CC BY 4.0
- Annual ILO modelled estimates
- Strong comparability and mapping
- Highest practical decision value among the new candidates

The three components are:

- employment-to-population ratio;
- labour-force participation;
- unemployment rate.

Required conditions:

- do not call it job vacancies or profession-specific opportunity;
- make component weights transparent;
- avoid double counting highly dependent labour indicators;
- run sensitivity and correlation analysis;
- rank 88 complete countries when this criterion is active;
- disclose the three excluded countries prominently;
- search for a pre-approved semantically equivalent official fallback before implementation, but do not delay indefinitely if none exists.

This criterion is worth a narrow coverage exception because it addresses a central relocation decision and excludes only 3 of 91 countries.

#### C08 — School education quality

**Decision:** Approve as a conditional experimental criterion.

- Measured 87/91 valid
- Non-valid: Antigua and Barbuda, Bahamas, Bolivia, Guyana
- CC BY 4.0
- Current official/modelled education source
- High family decision value
- Medium-high methodological cost

Required conditions:

- settle the primary construct: harmonised learning outcomes, learning-adjusted years of schooling, or another published component;
- do not treat the schooling component as a 0–100 percentage;
- keep model and mixed-reference-year caveats;
- rank only complete countries when active;
- label it experimental;
- do not imply school availability, private-school quality, international-school access, or city-level school fit.

Combined C11 and C08 activation leaves 85/91 countries based on the measured non-valid-country union. This remains above the Phase 5 threshold.

### 4.5 Final probe candidates before the mature portfolio is closed

#### C26 — Financial protection from health costs

**Decision:** Highest-priority final probe.

Phase 5C found full coverage plausible from the WHO Global Health Expenditure Database, but exact stable-91 coverage and licence capture were not measured.

The criterion should be narrowed to:

> Financial protection from health costs

Possible components:

- out-of-pocket expenditure share;
- catastrophic health-spending incidence, if sufficiently current and covered.

Do not claim:

- healthcare quality;
- migrant eligibility;
- insurance premium affordability;
- waiting-time performance.

Target outcome: production or experimental global criterion, subject to 91/91 or approved conditional coverage.

#### C66 — Extreme-weather risk

**Decision:** High-priority final probe; experimental only initially.

Phase 5C measured 91/91 availability in INFORM for the proposed hazard subset. Phase 5E did not run the deterministic exact-source probe.

Required decisions:

- use hazard/exposure components, not broad vulnerability/governance components;
- avoid duplication with political stability, infrastructure and future climate-resilience criteria;
- preserve the exact workbook licence/source chain;
- test component weights;
- retain local-variation caveats;
- use broad risk bands.

Target outcome: global experimental criterion.

#### C71 — Working-time burden

**Decision:** Final probe and reserve-to-add candidate.

Rename from `Work-life balance`.

The narrow construct should use official working-time indicators and avoid mixing:

- commute;
- leave take-up;
- workplace culture;
- childcare;
- city lifestyle.

Target outcome: global criterion if measured coverage, freshness and discrimination pass. It can become the fourteenth enabled criterion if the first 13 are already balanced.

#### C34 — Naturalisation accessibility

**Decision:** Probe as context/experimental, not as a substitute for legal eligibility.

A narrow legal subset may include:

- ordinary residence period;
- dual-citizenship treatment;
- language/civics requirements;
- selected formal naturalisation barriers.

Required conditions:

- exact GLOBALCIT archive licence and stable-91 mapping;
- current law-as-of metadata;
- transparent legal coding;
- no claim that it answers skilled visa, PR, discretion, processing time, or an individual’s eligibility;
- normative weights must remain explicit.

This may become an experimental long-term settlement criterion or contextual evidence. It should not be required to reach the core criterion target.

---

## 5. Mature target portfolio

Assuming the recommended probes and scoring decisions pass, the target portfolio is:

### Globally complete core criteria

1. Population-weighted PM2.5
2. Relative cost
3. Intentional homicide
4. Women’s legal and economic equality
5. Digital connectivity — replacing the infrastructure composite
6. Political stability
7. Rule of law
8. Established immigrant presence

### Global experimental or newly validated criteria

9. Macroeconomic stability — experimental
10. Financial protection from health costs — status determined by final probe
11. Extreme-weather risk — experimental

### Conditional complete-case criteria

12. Overall job-market opportunity — 88/91
13. School education quality — 87/91, experimental

### Optional fourteenth

14. Working-time burden, if its final probe passes and shows useful discrimination

### Context/reserve rather than required enabled criterion

- Naturalisation accessibility
- Basic water and sanitation access
- Research and innovation ecosystem
- Social-protection system reach
- Entrepreneurship activity

This target gives Konsider a credible 13-criterion product without pretending that every relocation question is a globally comparable national statistic.

---

## 6. Decision-question coverage

| Relocation question | Recommended answer | Portfolio status |
| --- | --- | --- |
| Can I legally move and remain? | Not answerable by a universal country score. Build a later route/profile module. Naturalisation accessibility may provide long-term context only. | Explicit gap; deferred by design |
| Can I find work or education? | C11 job-market opportunity; C08 school quality; research/education reserves later. | Covered conditionally |
| Can I afford life there? | Relative cost; macroeconomic stability; health-cost financial protection. Tax and housing require profile/city layers. | Meaningfully covered, with known gaps |
| Will my family be safe and healthy? | Homicide, political stability, PM2.5, school quality, health-cost protection. UHC remains diagnostic. | Covered |
| Can we function and integrate? | Established immigrant presence and women’s legal equality. English usability and social acceptance remain city/survey gaps. | Partially covered |
| Is infrastructure dependable? | Digital connectivity. Electricity and water reliability remain unsupported at national global scale. | Partially covered honestly |
| Does the environment fit us? | PM2.5 and extreme-weather risk. Climate comfort remains a preference/city layer. | Covered for risk, not preference |

The table intentionally exposes gaps instead of masking them with weak proxies.

---

## 7. Candidate disposition summary

### 7.1 Production additions

- C48 Political stability
- C49 Rule of law, subject to redundancy review
- C30 Established immigrant presence, after scoring semantics
- C11 Job-market opportunity, conditional complete-case

### 7.2 Experimental additions

- C29 Macroeconomic stability
- C08 School education quality, conditional
- C66 Extreme-weather risk, after final probe
- C34 Naturalisation accessibility, context/experimental if approved

### 7.3 Production or experimental pending final probe

- C26 Financial protection from health costs
- C71 Working-time burden

### 7.4 Reserve candidates

- C53 Basic water and sanitation access
- C05 Research and innovation ecosystem
- C76 Social-protection system reach
- C16 Entrepreneurship activity
- C34 Naturalisation accessibility, if not enabled
- C71 Working-time burden, if not enabled

C53 remains reserve because its measured 86/91 coverage is weaker than the full-coverage candidates and the basic-service measure is saturated and does not represent water safety or continuity.

### 7.5 Deferred to profile/legal layers

- C32 Skilled-work visa accessibility
- C33 Permanent-residency accessibility
- C35 Post-study migration pathway
- C36 Family reunification support
- C38 Professional-licensing accessibility
- C21 Personal income-tax burden
- C22 Social-security contribution burden
- C72 Family friendliness
- C77 Retirement suitability
- C79–C84 profile composites

### 7.6 Deferred to city/occupation layers

- C25 Housing affordability
- C40 English usability
- C12 Software and technology jobs
- C13 Medical and healthcare jobs
- C14 Business/professional-services jobs
- C15 Engineering/skilled jobs
- C57 Water-supply reliability
- C60 Urban public transport
- C61 International connectivity
- C73 Urban quality of life
- C74 Recreation/culture

### 7.7 Rejected as current production criteria

- C19 Employment protection and worker rights — source warns against the required country comparison and the proposed score is indefensible.
- C45 LGBTQ+ legal/social inclusion — current selected source is non-commercial.
- C69 Environmental quality composite — non-commercial source and substantial redundancy/definition concerns.
- Direct EF EPI use for English usability — licensing, selection and city/domain validity problems.
- Direct proprietary or crowdsourced housing/cost/job rankings — licensing, reproducibility and comparability problems.

Rejected criteria may be revisited if a materially different source resolves the recorded blockers.

---

## 8. Guardrail decisions

### 8.1 Freshness

**Current rule:** Criterion-specific freshness exists, including three years for UHC and five years for homicide.

**Proposed rule:** Keep criterion-specific freshness; formalise freshness classes rather than adopting one global year limit.

Examples:

- current policy/legal rules: current as-of snapshot;
- jobs, inflation and housing: latest 0–2 years;
- standard socioeconomic measures: latest 0–3 years;
- slow structural measures: up to 5 years with justification;
- climate: current model edition/normal period, not simple observation age;
- rolling stability measures: latest year plus declared multi-year window.

**Quantified benefit:** Supports the correct interpretation of C29’s 2020–2024 window, WGI’s 2024 observation, and legal/climate editions without pretending they have identical freshness semantics.

**Quality cost:** Slightly more policy complexity.

**Visible caveat/fallback:** Show reference period and freshness class per criterion.

**Recommendation:** Accept. This is clarification, not weakening.

### 8.2 Complete-country coverage

**Current rule:** Enabled ranking criteria are complete for all 91 stable countries.

**Proposed rule:**

- `GLOBAL_CORE`: 91/91 required.
- `CONDITIONAL_COMPLETE_CASE`: minimum 82/91; activated only when selected by the user; rank only countries with valid data for every active criterion.
- `CONTEXT_ONLY`: may show data without affecting ranking.

**Quantified benefit:**

- C11 becomes usable for 88/91, excluding 3.
- C08 becomes usable for 87/91, excluding 4.
- C53 could become usable for 86/91, excluding 5, though this document does not recommend enabling it.
- C11 + C08 together leave 85/91.
- C11 + C08 + C53 together leave 82/91.

**Quality cost:**

- ranking universe varies by selected criteria;
- exclusions may be regionally or developmentally biased;
- users may interpret a missing country as low-ranked rather than unranked.

**Visible caveat/fallback:**

- show `85 of 91 countries ranked`;
- list excluded countries and reasons before results;
- never show excluded countries at the bottom;
- keep stable catalog search separate from ranked-result count;
- enforce a minimum result universe of 82;
- require a regional-bias review for each conditional criterion.

**Recommendation:** Accept narrowly for C11 and C08. Do not use the exception merely to inflate criterion count.

### 8.3 Minimum ready criteria

**Current rule:** Publication requires at least five ready criteria.

**Proposed rule:** After the first successful Phase 5G release:

- require at least **eight GLOBAL_CORE criteria**;
- previously published core criteria cannot silently disappear;
- conditional and experimental criteria do not count toward the core minimum;
- removal or demotion of a core criterion requires an explicit policy/version decision.

**Quantified benefit:** The proposed core portfolio reaches eight after digital-connectivity refactoring plus C48, C49 and C30.

**Quality cost:** A failed core source can block refresh publication.

**Fallback:** Retain the previous immutable release until a valid new release exists.

**Recommendation:** Accept. This tightens quality.

### 8.4 Source authority

**Current rule:** Official or strongly authoritative sources are required.

**Proposed rule:** Keep A4 as default; allow A3 only through explicit review when no official comparable source exists.

**Benefit of relaxation:** None currently demonstrated.

**Quality cost:** Lower-accountability datasets can introduce opaque methodology or instability.

**Recommendation:** Do not broadly relax.

### 8.5 Licensing

**Current rule:** Dataset-specific production reuse and redistribution rights must be clear; ambiguity is rejection.

**Proposed rule:** No change.

**Quantified benefit of relaxation:** It could admit ILGA, some surveys, commercial rankings and alternate UN payloads.

**Quality cost:** Legal and operational risk directly conflicts with public product use.

**Recommendation:** Do not relax.

### 8.6 Imputation

**Current rule:** Konsider does not impute missing product data.

**Proposed clarification:**

- continue prohibiting Konsider-created imputation;
- permit publisher-provided modelled or estimated values when:
  - the source is authoritative;
  - the methodology is documented;
  - estimate flags are retained;
  - the licence permits use;
  - sensitivity is reviewed.

**Quantified benefit:** Supports existing PM2.5 and current candidates such as C11, C30 and C08 without inventing values.

**Quality cost:** Model assumptions may reduce interpretability.

**Visible caveat:** Mark modelled/estimated observations in details and provenance.

**Recommendation:** Accept as clarification; do not fill source gaps internally.

### 8.7 Partial-country scoring

**Current rule:** No partial-country scoring or country-specific weight renormalisation.

**Proposed rule:** Keep this prohibition.

Conditional complete-case ranking is allowed because every ranked country has all active criteria; countries lacking data are excluded rather than partially scored.

**Rejected fallbacks:**

- neutral score for missing data;
- worst score for missing data;
- mean/region imputation;
- per-country weight renormalisation;
- treating missing as zero;
- listing unranked countries at the bottom.

**Recommendation:** No relaxation.

### 8.8 National versus city granularity

**Current rule:** Current rankings use national observations.

**Proposed rule:** Keep the national ranking. A city-sensitive criterion may proceed only if:

- the national construct is independently meaningful;
- the label is narrowed;
- within-country variation is disclosed.

Housing, public transport, occupation-specific jobs, English usability and service continuity remain deferred.

**Benefit of relaxation:** A national proxy could increase criterion count.

**Quality cost:** It would mislead users about actual migrant destinations.

**Recommendation:** Do not broadly relax.

### 8.9 Composites

**Current rule:** Transparent versioned composites may be experimental.

**Proposed rule:** Allow composites only when:

- every component is independently sourced and available;
- components have a coherent construct;
- weights are explicit;
- alternative weights are tested;
- pairwise correlations and redundancy are reviewed;
- component contributions are visible;
- no hidden fallback or imputation exists.

**Quantified benefit:** Supports C29 and C66, and a narrowed digital-connectivity measure.

**Quality cost:** Weight choices introduce policy judgement.

**Recommendation:** Accept criterion-specifically; experimental on first release.

### 8.10 Survey and perception indicators

**Current rule:** No blanket prohibition, but comparability and source quality are required.

**Proposed rule:** Permit authoritative harmonised survey/perception aggregates, including WGI, when:

- uncertainty is retained;
- scoring uses broad bands;
- small differences do not produce strong rank claims;
- methodology and editions are frozen;
- survey/legal/modelled nature is explicit.

**Benefit:** Enables C48 and C49 with 91/91 current coverage.

**Quality cost:** Perception bias and margins of error.

**Recommendation:** Accept with uncertainty-aware scoring.

---

## 9. Approved fallback hierarchy

When a candidate does not reach full coverage, apply this order:

1. **Exact same source, older observation within the approved freshness window**
   - acceptable only when the criterion’s policy permits it;
   - preserve the country-specific year.

2. **Pre-approved equivalent official representation**
   - same construct, definition, unit and population;
   - acceptable licence;
   - frozen source precedence;
   - deterministic discrepancy checks.

3. **Query-specific complete-case exclusion**
   - minimum 82 countries;
   - clear excluded-country disclosure;
   - no partial scoring.

4. **Context-only display**
   - useful evidence that does not alter ranking.

5. **Defer to a later city/profile/legal module**

Not approved:

- ad hoc web search at scoring time;
- manually copied values;
- unofficial rankings;
- silent source substitution;
- internal imputation;
- semantic proxies presented as the original criterion.

---

## 10. Maintenance and implementation-cost comparison

| Candidate | Maintenance cost | Main reason |
| --- | --- | --- |
| C30 immigrant presence | Low | One World Bank indicator; annual; direct mapping |
| C48 political stability | Low | One WGI indicator; annual |
| C49 rule of law | Low | One WGI indicator; annual |
| Digital connectivity | Low–medium | Existing production inputs; composite sensitivity |
| C29 macro stability | Medium | Multi-year time series, currency changes and regime handling |
| C11 job market | Medium | Three ILO files, annual model edition, conditional coverage |
| C08 school quality | Medium–high | Stata/panel parsing, component choice, model interpretation |
| C26 health-cost protection | Low–medium expected | Exact series and coverage still need probe |
| C66 extreme-weather risk | Medium–high | Workbook/version/source chain, component selection, local variation |
| C71 working-time burden | Medium | Exact join and discrimination still need probe |
| C34 naturalisation accessibility | High | Legal coding, as-of dates and normative choices |
| C53 water/sanitation | Low–medium | Easy source, but weak construct/discrimination |

Implementation priority should favour high decision value and evidence quality, not merely low maintenance.

---

## 11. Portfolio balance and redundancy rules

Before publication:

1. Compute Pearson and Spearman correlation across all globally complete numeric criteria.
2. Compare criterion contribution distributions under representative profiles.
3. Test rank changes after removing each new criterion.
4. Flag:
   - absolute correlation above 0.90;
   - near-zero contribution spread;
   - duplicated components;
   - repeated governance/economic constructs.
5. Do not automatically remove correlated criteria when their meanings differ.
6. Do not allow multiple criteria to repeatedly reward the same upstream component without clear user value.

Specific checks:

- C48 versus C49
- C29 inflation component versus existing relative cost
- Digital connectivity versus the former infrastructure composite
- C08 versus any future higher-education measure
- C66 versus future disaster/resilience measures
- C30 versus future social-inclusion measures

---

## 12. Phase 5G implementation order

### 12.1 Phase 5G-0 — Complete the final evidence gap

Before production implementation, run deterministic Phase 5E-style probes for:

1. C26 Financial protection from health costs
2. C66 Extreme-weather risk
3. C71 Working-time burden
4. C34 Naturalisation accessibility

Exit criteria:

- exact source and licence captured;
- stable-91 country outcomes;
- freshness;
- replay;
- discrimination summary;
- production/experimental/reserve decision.

This should be a bounded extension of the existing probe framework, not a new platform.

### 12.2 Phase 5G-1 — Low-risk globally complete additions

Implement:

1. C48 Political stability
2. C49 Rule of law
3. C30 Established immigrant presence

Also:

- run C48/C49 redundancy analysis;
- settle C30 semantics;
- add broad fixed bands and uncertainty metadata;
- keep all 91 countries.

Publish only when all three pass production validation.

### 12.3 Phase 5G-2 — Infrastructure clarification

Replace the current infrastructure composite with:

- `Digital connectivity`, based on internet use and fixed broadband.

Retain:

- old release history;
- LPI/logistics provenance;
- a migration note explaining the semantic change.

Do not keep both the old composite and the new digital criterion enabled by default, because that would double count the same digital components.

### 12.4 Phase 5G-3 — Experimental global additions

Implement, in order:

1. C29 Macroeconomic stability
2. C26 Financial protection from health costs, if probe passes
3. C66 Extreme-weather risk, if probe passes

Requirements:

- component-level output;
- sensitivity tests;
- broad bands;
- experimental flag where methodology remains policy-dependent.

### 12.5 Phase 5G-4 — Conditional complete-case capability

Add the repository/service rule needed to represent:

- global core criteria;
- conditional criteria;
- exact eligible-country intersection;
- excluded-country reasons;
- minimum 82-country result gate.

Then implement:

1. C11 Job-market opportunity
2. C08 School education quality

Do not implement per-country weight renormalisation.

### 12.6 Phase 5G-5 — Optional final additions

After the portfolio is reviewed:

- add C71 Working-time burden if it passes;
- publish C34 Naturalisation accessibility as experimental/context only if its legal coding is sufficiently current and transparent;
- retain C53 and C05 as reserves.

### 12.7 Publication target

Recommended first mature Phase 5 release:

- 8 globally complete core criteria;
- 2–3 global experimental/new criteria;
- 2 conditional criteria;
- total: 12–13 enabled criteria.

Do not delay a high-quality 12-criterion release merely to reach 15.

---

## 13. Phase 5G acceptance criteria

Phase 5G is complete only when:

1. Every implemented source has dataset-specific licence evidence.
2. All raw artifacts, versions, checksums and record locators are preserved.
3. Online processing and offline replay agree.
4. Global core criteria have 91/91 valid observations.
5. Conditional criteria have at least 82/91 and explicit exclusion reports.
6. No country is partially scored.
7. Every score has a versioned method and sensitivity diagnostics.
8. Experimental criteria are visibly and structurally experimental.
9. Redundancy analysis is recorded.
10. The source audit, scoring methodology, coverage report, worker guide, roadmap and release report are updated.
11. The active release changes only through a new immutable release ID.
12. The default ranking can explain what each criterion does and does not measure.

---

## 14. Final recommendation

Proceed with Phase 5G, but in two evidence levels:

- immediately implement the globally complete, measured candidates;
- finish the four final probes before implementing the remainder.

The preferred mature portfolio is **13 criteria**, not 15 at any cost.

The recommended quality-preserving compromise is:

- keep the stable country catalog at 91;
- preserve 91/91 for core criteria;
- permit carefully labelled query-specific complete-case ranking for exceptionally valuable criteria with at least 82/91;
- never impute or partially score;
- defer legal eligibility, housing, tax, English and profession-specific questions to layers that can represent their real profile and city dependence.

This gives Konsider significantly more decision value without abandoning the evidence-first standard that distinguishes it from generic country-ranking sites.
