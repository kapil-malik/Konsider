# Konsider Phase 5A — Criteria Research Framework and Prioritisation

**Status:** Phase 5A framework complete
**Version:** 1.0
**Date:** 24 July 2026
**Scope:** Criteria expansion, source feasibility, research prioritisation, publishing benchmarks, and hand-off schemas
**Out of scope:** API, UI, production adapters, source-specific implementation, and final guardrail relaxation decisions

---

## 1. Executive decision

Phase 5 should not treat the 84-item search space as 84 equally expensive investigations.

The approved research strategy is:

1. **Classify and order all 84 candidates now.**
2. **Lightly screen all 84 in Phase 5B.**
3. **Deeply research candidates in balanced batches of 12–15 in Phase 5C.**
4. **Use a 90% expected-coverage threshold—at least 82 of the stable 91 countries—as a normal eligibility threshold for deterministic probing, not as automatic permission to publish.**
5. **Keep the current production baseline unchanged during Phase 5A:** an enabled ranking criterion should, by default, be complete and ready for all 91 currently supported countries.
6. **Allow strategically important candidates below the 90% screening threshold to receive a bounded exception study**, but do not treat that as a guardrail relaxation.
7. **Do not deeply source-search profile composites.** Items 79–84 should eventually be calculated from approved component criteria.
8. **Do not mix city-level measures into the national ranking.** City-sensitive candidates should either use a defensible national baseline or wait for a later city/region layer.
9. **Select the final portfolio for decision coverage, not category quotas or the first datasets that are easy to fetch.**

The desired Phase 5 outcome remains approximately **10–15 total enabled criteria**, including the existing five, plus a small reserve set.

---

## 2. Source basis and current constraints

This framework is grounded in:

- the attached 84-item criteria search space;
- `docs/data/source-audit.md`;
- `docs/data/scoring-methodology.md`;
- `docs/data/country-coverage-phase-2d.md`;
- `docs/operations/worker.md`;
- active universe `stable_supported_v1`;
- active release `2026-07-24.1`.

The current repository establishes these baseline principles:

- a public endpoint is not evidence of a usable licence;
- sources must preserve version, methodology, attribution, licence evidence, limitations, and exact provenance;
- criterion readiness is separate from structural validity and aggregate product readiness;
- missing, stale, rejected, incomparable, or unlicensed values are not repaired by scoring;
- no fixture fallback, silent imputation, or partial-country scoring is used;
- fixed or domain-based transformations are preferred when sample-relative scoring would exaggerate small differences;
- experimental status describes methodological uncertainty, not permission to ignore licensing, provenance, replay, or completeness;
- the stable 91-country universe should not be silently reduced merely to admit a new criterion.

Phase 5A does **not** change these principles.

---

## 3. Product decision pillars

The final portfolio should answer seven practical relocation questions.

| Pillar | User question | Existing coverage | Phase 5 priority |
| --- | --- | --- | --- |
| Legal mobility | Can I legally move, work, remain, and bring family? | Major gap | Very high |
| Work and study | Can I find suitable work or education? | Major gap | Very high |
| Financial viability | Can I afford a good life after taxes and housing? | Partial: broad affordability | Very high |
| Safety and health | Will my family be safe and receive good care? | Partial: homicide and pollution | High |
| Integration | Can we function in the language and society? | Partial: women's legal equality | High |
| Daily reliability | Are power, water, internet, transport and government services dependable? | Partial: experimental infrastructure | High |
| Environment and lifestyle | Does the place fit our climate and lifestyle preferences? | Partial: pollution | Medium-high |

This is a **portfolio balance test**, not a rigid quota. A final portfolio should cover every pillar, but some pillars may justifiably contain more criteria than others.

---

## 4. Standard evaluation rubric

No weighted score can override a hard blocker. The rubric supports consistent research; it does not turn weak evidence into readiness.

### 4.1 Criterion identity and decision value

| Field | Required assessment |
| --- | --- |
| `criterion_id` | Stable source-controlled ID. |
| `name` | Clear user-facing name. |
| `relocation_question` | One sentence describing the decision it informs. |
| `definition` | Exact construct, numerator, denominator, population, geography and reference period. |
| `decision_value` | 1–5: marginal to essential for a relocation decision. |
| `decision_pillars` | One or more of the seven pillars above. |
| `target_profiles` | General, worker, student, family, professional, entrepreneur, retiree, or origin-specific. |
| `profile_dependence` | None, moderate, high, or profile-only. |

A criterion should not proceed merely because data exists. It must answer a comprehensible relocation question without implying more than the source measures.

### 4.2 Granularity

Allowed values:

- `NATIONAL`
- `NATIONAL_WITH_CITY_CAVEAT`
- `CITY_OR_REGIONAL`
- `PREFERENCE_MODEL`
- `PROFILE_ONLY`

Assessment questions:

- Would a national value describe the experience of likely migrants?
- Is variation within large countries material?
- Is the underlying decision about a country, a destination city, or an individual profile?
- Would a national score systematically favour small city-states over diverse countries?
- Can the limitation be communicated honestly, or does it invalidate the criterion?

**Default rule:** `CITY_OR_REGIONAL` candidates do not enter the national ranking until a city layer and a transparent destination-city selection policy exist.

### 4.3 Source authority

Use an authority grade:

| Grade | Meaning |
| --- | --- |
| `A4` | Official international or national statistical/legal source with dataset-specific methodology and accountable publisher. |
| `A3` | Strong authoritative research consortium or regulated body with transparent methods and provenance. |
| `A2` | Reputable secondary aggregation of named primary sources; suitable mainly for discovery or cross-checking. |
| `A1` | Commercial ranking, crowdsourced site, blog, opaque index, or undocumented aggregation. |
| `A0` | No identifiable authoritative source. |

Production preference is `A4`. `A3` needs explicit justification. `A2` and below should not be primary production sources without a later approved exception.

### 4.4 Candidate dataset specificity

Each source candidate should record:

- publisher;
- exact dataset, table, series or legal corpus;
- access URL or endpoint;
- edition/version;
- methodology URL;
- unit and population;
- update cadence;
- record locator;
- original upstream source, if redistributed;
- known flags, estimates or imputations.

A publisher name alone is not a source candidate.

### 4.5 Comparability

Use a 0–4 comparability grade:

| Grade | Meaning |
| --- | --- |
| `C4` | Common definition, unit, population and method across countries. |
| `C3` | Mostly harmonised with documented, manageable differences. |
| `C2` | Material definitional or reporting differences; experimental at best. |
| `C1` | Comparisons likely misleading. |
| `C0` | No defensible cross-country construct. |

Record separately:

- legal versus lived outcome;
- administrative versus survey versus modelled observation;
- national versus urban population;
- stock versus flow;
- gross versus net measure;
- estimate/imputation status;
- methodology breaks between editions.

### 4.6 Coverage

Coverage is always measured against an explicit universe and denominator.

For Phase 5:

- default universe: `stable_supported_v1`;
- denominator: 91 countries;
- expected screening threshold: **82/91**;
- record `found`, `fresh`, `parsed`, `validated`, `missing`, `stale`, `invalid`, `rejected`, and `unmapped`;
- preserve country-level reason codes;
- report regional concentration of missingness.

Coverage bands:

| Band | Validated countries | Phase 5 interpretation |
| --- | ---: | --- |
| `FULL` | 91 | Eligible for production consideration, subject to all other gates. |
| `HIGH` | 82–90 | Normal threshold for measured feasibility work; not automatic production approval. |
| `MEDIUM` | 64–81 | Probe only through an explicit strategic exception. |
| `LOW` | Below 64 | Normally reject or defer to a regional/city product. |

A criterion must not pass by recomputing a smaller country universe unless Phase 5F explicitly approves that product change.

### 4.7 Freshness and update cadence

Freshness must be criterion-specific.

| Freshness class | Typical use | Initial research benchmark |
| --- | --- | --- |
| `CURRENT_POLICY` | Visa, PR, tax, citizenship, legal rights | Current as-of snapshot with retrieval date and scheduled re-check. |
| `FAST_MOVING` | Jobs, wages, inflation, housing | Normally latest 0–2 years. |
| `STANDARD_SOCIOECONOMIC` | Health, education, infrastructure | Normally latest 0–3 years. |
| `SLOW_STRUCTURAL` | Institutional or benchmark indicators | Up to 5 years only with stable methodology and explicit justification. |
| `CLIMATE_NORMAL` | Temperature and long-run climate | Published climatological normal or model period; annual age is not the correct test. |
| `EVENT_RISK_MODEL` | Disaster and climate risk | Current model edition, scenario, exposure year and methodology version. |
| `STATIC_OR_LEGAL_ASOF` | Formal legal rules | Current as-of date; no generic multi-year tolerance. |

These are research defaults, not final production rules. Phase 5F must approve any criterion-specific freshness rule.

### 4.8 Licensing clarity

Use a 0–4 licence grade:

| Grade | Meaning |
| --- | --- |
| `L4` | Dataset-specific terms clearly allow required commercial use, copying, transformation, public display and redistribution of derived artifacts, with stated conditions. |
| `L3` | Permissive licence with manageable attribution, share-alike or notice requirements; legal fit must be documented. |
| `L2` | Public access but incomplete or ambiguous reuse rights. |
| `L1` | Restricted, non-commercial, no-derivatives, contractual or redistribution-prohibited. |
| `L0` | No usable evidence. |

`L2` and below are production blockers. Generic website terms, privacy policies, and public APIs do not substitute for dataset-specific permission.

### 4.9 Country mapping and provenance

Assess:

- ISO alpha-3 or stable country identifier availability;
- aggregates, territories and disputed entities;
- historical country changes;
- economy-versus-country definitions;
- deterministic aliases;
- source-controlled exclusions;
- exact row, cell, API record or legal provision locator;
- raw artifact retention and checksum;
- online retrieval and offline replay.

Mapping grade:

- `M3`: deterministic direct mapping;
- `M2`: deterministic maintained crosswalk;
- `M1`: significant manual ambiguity;
- `M0`: not reproducibly mappable.

### 4.10 Scoring feasibility

Allowed scoring modes:

- `HIGHER_BETTER`
- `LOWER_BETTER`
- `TARGET_RANGE`
- `PREFERENCE_MATCH`
- `PROFILE_DERIVED`
- `INFORMATIONAL_ONLY`

Scoring grade:

| Grade | Meaning |
| --- | --- |
| `S4` | Clear direction and defensible domain thresholds. |
| `S3` | Clear direction; empirical transformation needs sensitivity review. |
| `S2` | Composite, survey or policy coding with material judgement; experimental only. |
| `S1` | Direction is ambiguous or masks incompatible dimensions. |
| `S0` | No defensible scalar score. |

A score cannot cure missing, stale, incomparable, or unlicensed observations. Preference-fit criteria should not be forced into universal rankings.

### 4.11 Redundancy and composites

Record:

- overlap with existing criteria;
- overlap with other Phase 5 candidates;
- shared source inputs;
- conceptual dependence;
- expected correlation;
- risk of double weighting.

A composite requires:

- transparent components;
- explicit weights;
- component-level provenance;
- no hidden substitution;
- sensitivity analysis;
- pairwise correlation review;
- a clear explanation of what the composite omits.

### 4.12 Maintainability and research priority

Operational assessment:

- structured download/API versus manual legal review;
- change detection;
- edition/version stability;
- parser complexity;
- update frequency;
- source fragility;
- expected human review;
- replayability.

After Phase 5B, calculate a **research priority score** only for ordering work:

- decision value: 30%;
- portfolio-gap contribution: 15%;
- source plausibility: 15%;
- expected coverage: 10%;
- comparability: 10%;
- preliminary licence confidence: 5%;
- freshness: 5%;
- scoring feasibility: 5%;
- maintainability: 5%.

Hard blockers remain hard blockers regardless of the score.

---

## 5. Stage gates and publishing benchmarks

### Gate A — Lightweight screening

Required:

- clear relocation question;
- initial classification and granularity;
- likely source families;
- expected coverage band;
- initial source, licence and comparability risks.

Output: screen all 84.

### Gate B — Deep-research eligibility

Proceed when either:

- the criterion has high decision value and plausible authoritative sources; or
- it fills an important portfolio gap even though feasibility is uncertain.

Output: approximately 35–45 candidates across all Phase 5C batches.

### Gate C — Deterministic-probe eligibility

Normal route:

- at least one dataset-specific source candidate;
- `A3` or `A4` source plausibility;
- likely licence `L3` or `L4`;
- expected validated coverage at least 82/91;
- plausible country mapping and replay;
- no fatal comparability issue.

Strategic exception:

- a criterion may be probed below 82/91 when it is central to legal mobility, jobs, education, healthcare or housing and the study could identify a defensible fallback.
- the exception must be explicit and does not imply production approval.

### Gate D — Production-candidate eligibility

Default Phase 5A baseline:

- explicit acceptable licence;
- measured 91/91 validated coverage for the fixed stable universe;
- approved criterion-specific freshness;
- deterministic country mapping;
- complete attempts and provenance;
- replay and checksums;
- defensible scoring;
- no unresolved source substitution;
- no unapproved imputation;
- acceptable redundancy and sensitivity.

### Gate E — Experimental-candidate eligibility

Experimental criteria must still pass licensing, provenance, replay, mapping and current completeness requirements. Experimental status may cover:

- a derived composite;
- survey/model uncertainty;
- provisional weights;
- limitations in interpretation;
- a scoring method needing future validation.

It must not mean “lower evidence quality is acceptable.”

### Gate F — Informational or profile layer

Candidates may be retained outside ranking when they are:

- profile-derived;
- preference-fit;
- city/regional;
- partially covered;
- valuable but not scalar;
- legally or methodologically unsuitable for production scoring.

Any future informational partial-coverage mode requires a separate product decision. It is not approved by this document.

---

## 6. Classification taxonomy

| Tag | Meaning |
| --- | --- |
| IC | Independent criterion: can potentially be evaluated and scored on its own. |
| SC | Sub-criterion: naturally belongs under a broader domain and may later be grouped. |
| PC | Profile composite: calculated from approved component criteria; not a separate source search. |
| DO | Duplicate or overlapping: overlaps an existing criterion or another candidate. |
| CR | City/regional-sensitive: a national average may materially mislead. |
| PF | Preference-fit: no universal higher-is-better direction. |
| LF | Low-feasibility: likely difficult because of source, comparability, licensing, granularity, or maintenance. |

Tags are not verdicts. For example, skilled-work visa accessibility is both highly valuable and `LF` because current policy is difficult to encode and maintain. That makes it a high-priority research problem, not an early rejection.

---

## 7. Ordered master research list

The order below is a **research order**, not a final recommendation or claim of source feasibility.

| Rank | ID | Criterion | Category | Tags | Granularity | Research wave | Preliminary rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | C11 | Overall job-market opportunity | Employment, income and economic opportunity | IC | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Core relocation question with strong national labour indicators; vacancy depth and occupational matching need care. |
| 2 | C32 | Skilled-work visa accessibility | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_1 | One of the most important relocation gates, but policy rules are volatile, conditional and difficult to encode comparably. |
| 3 | C33 | Permanent-residency accessibility | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_1 | Core long-term settlement question; needs transparent scenario definitions and current official policy evidence. |
| 4 | C17 | Average earning potential | Employment, income and economic opportunity | IC, DO, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Core economic outcome, but national averages and gross wages can mislead without taxes, household type and city costs. |
| 5 | C21 | Personal income-tax burden | Tax, cost and financial conditions | IC | NATIONAL | BATCH_1 | Core relocation input; effective burden by household and income scenario is preferable to headline rates. |
| 6 | C25 | Housing affordability | Tax, cost and financial conditions | IC, SC, CR, LF | CITY_OR_REGIONAL | BATCH_1 | Extremely decision-relevant, but meaningful data is usually city-level and rent/home-price definitions differ. |
| 7 | C50 | Healthcare system capacity and quality | Safety, health and public services | IC, DO | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Core family decision area and natural successor to stale UHC; must separate capacity, outcomes, access and migrant eligibility. |
| 8 | C40 | English usability | Language, culture and integration | IC, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | High day-to-day and employment value; combine population proficiency carefully with actual service availability. |
| 9 | C01 | Overall higher-education opportunity | Education and human capital | IC | NATIONAL | BATCH_1 | Directly relevant to students and families; likely measurable, but quality and access should be kept separate. |
| 10 | C30 | Existing immigrant share | Migration, visa and settlement | IC | NATIONAL | BATCH_1 | Clear national structural measure and likely broad official coverage; interpretation should separate share from welcome or integration. |
| 11 | C12 | Software and technology jobs | Employment, income and economic opportunity | IC, SC, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Highly relevant for Konsider's likely early users, but jobs cluster in a few cities and occupation taxonomies vary. |
| 12 | C58 | Internet access, speed, and reliability | Infrastructure and daily-life reliability | IC, SC, DO | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Strong daily-life criterion with broad digital indicators; reliability and speed need more than subscription counts. |
| 13 | C56 | Electricity access and reliability | Infrastructure and daily-life reliability | IC, SC, DO | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Basic reliability is more useful than access alone; outage data may be less universal than electrification. |
| 14 | C08 | School education quality | Education and human capital | IC | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | High family relevance and plausible official outcomes, though national averages hide local and school-type variation. |
| 15 | C66 | Extreme-weather risk | Climate, environment and location | IC, SC, DO | NATIONAL_WITH_CITY_CAVEAT | BATCH_1 | Important environmental risk with plausible hazard data; define event frequency, exposure and resilience separately. |
| 16 | C38 | Professional-licensing accessibility for immigrants | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_2 | Critical for medical and other regulated professions, but origin, profession and credential dependence makes it a likely profile layer. |
| 17 | C35 | Post-study migration pathway | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_2 | Critical for students; should be researched as a policy pathway distinct from university quality. |
| 18 | C36 | Family reunification support | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_2 | High family value; dependant categories and sponsor rules vary and change frequently. |
| 19 | C34 | Citizenship accessibility | Migration, visa and settlement | IC, SC, LF | NATIONAL | BATCH_2 | Important for permanence, but time-to-citizenship and dual-citizenship rules need profile-specific qualification. |
| 20 | C05 | Research and innovation ecosystem | Education and human capital | IC | NATIONAL | BATCH_2 | Strong national innovation signal with plausible official inputs; avoid double counting education and tech jobs. |
| 21 | C15 | Engineering and skilled technical jobs | Employment, income and economic opportunity | IC, SC, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_2 | Useful profession branch with plausible occupation data, but shortages and credential rules vary. |
| 22 | C13 | Medical and healthcare jobs | Employment, income and economic opportunity | IC, SC, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_2 | Strong demand signal for a major profession, but professional licensing must be separated from vacancies. |
| 23 | C14 | Business, finance, and professional-services jobs | Employment, income and economic opportunity | IC, SC, CR | NATIONAL_WITH_CITY_CAVEAT | BATCH_2 | Useful profession branch; broad occupational definitions may blur finance, consulting and general services. |
| 24 | C16 | Entrepreneurship and startup opportunity | Employment, income and economic opportunity | IC | NATIONAL | BATCH_2 | High economic value with several official components; composite design and redundancy with innovation need control. |
| 25 | C19 | Employment protection and worker rights | Employment, income and economic opportunity | IC, SC | NATIONAL | BATCH_2 | Useful quality-of-work dimension with plausible legal indicators; law and enforcement should not be conflated. |
| 26 | C22 | Social-security and mandatory contribution burden | Tax, cost and financial conditions | IC, SC | NATIONAL | BATCH_2 | Necessary companion to income tax for take-home pay; country systems and benefit entitlements complicate comparison. |
| 27 | C26 | Healthcare affordability | Tax, cost and financial conditions | IC, SC | NATIONAL_WITH_CITY_CAVEAT | BATCH_2 | High family value; distinguish system financing, insurance requirements and migrant eligibility. |
| 28 | C28 | Savings and disposable-income potential | Tax, cost and financial conditions | IC, SC, DO, CR, LF | NATIONAL_WITH_CITY_CAVEAT | BATCH_2 | Best treated as a derived household-profile result from earnings, tax, housing and essentials rather than one raw criterion. |
| 29 | C29 | Currency and macroeconomic stability | Tax, cost and financial conditions | IC, SC | NATIONAL | BATCH_2 | Useful risk dimension with strong national data possibilities; avoid turning short-term volatility into a permanent country label. |
| 30 | C48 | Political stability and civil peace | Safety, health and public services | IC, SC | NATIONAL | BATCH_2 | High-level safety and continuity signal with plausible broad sources; distinguish conflict exposure from ordinary politics. |
| 31 | C49 | Rule of law and institutional trust | Safety, health and public services | IC, SC | NATIONAL | WAVE_3 | Strong institutional criterion with broad governance indicators; survey/model uncertainty and licensing need review. |
| 32 | C53 | Water quality and sanitation | Safety, health and public services | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Strong health/infrastructure dimension with plausible broad official indicators; access does not guarantee reliability or taste. |
| 33 | C57 | Water-supply reliability | Infrastructure and daily-life reliability | IC, SC, CR, LF | CITY_OR_REGIONAL | WAVE_3 | High practical value but continuity and scarcity are highly local and seasonally variable. |
| 34 | C70 | Climate resilience and adaptation readiness | Climate, environment and location | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Promising risk-management dimension, though many indices are modelled composites and may embed socioeconomic outcomes. |
| 35 | C67 | Long-term climate-change exposure | Climate, environment and location | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Long-horizon structural risk; model assumptions and scenarios require careful communication. |
| 36 | C68 | Natural-disaster risk | Climate, environment and location | IC, SC, DO | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Broad hazard exposure can complement extreme weather but overlaps it; geophysical and climate hazards may need separate components. |
| 37 | C06 | International-student accessibility | Education and human capital | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Decision-relevant for students, but combines admissions, language, visa and support policies that may require multiple sources. |
| 38 | C07 | Tuition affordability | Education and human capital | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Useful only when normalized by purchasing power or income; fees vary heavily by institution and residency status. |
| 39 | C10 | Recognition and portability of qualifications | Education and human capital | IC, SC, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Valuable for regulated careers and study, but qualification recognition is profession- and origin-specific. |
| 40 | C62 | Digital-government readiness | Infrastructure and daily-life reliability | IC, SC | NATIONAL | WAVE_3 | Promising institutional convenience measure with emerging official benchmarks; composite transparency is important. |
| 41 | C71 | Work-life balance | Family, lifestyle and long-term liveability | IC, SC, DO, CR, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Highly relevant but combines legal entitlements, actual hours, commute and culture; some components are city/profile dependent. |
| 42 | C72 | Family friendliness | Family, lifestyle and long-term liveability | IC, SC, DO, CR, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Broad profile-oriented composite overlapping school, childcare, safety, leave and migration rules. |
| 43 | C76 | Social protection and welfare support | Family, lifestyle and long-term liveability | IC, SC | NATIONAL | WAVE_3 | Important for long-term security, but immigrant eligibility and contribution history matter more than nominal generosity. |
| 44 | C42 | Social inclusion and acceptance of immigrants | Language, culture and integration | IC, SC, CR, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Important lived-outcome dimension, but survey comparability, bias and sparse country coverage may limit production use. |
| 45 | C37 | Government stance toward immigrants | Migration, visa and settlement | IC, SC, DO, LF | NATIONAL | WAVE_3 | Broad, partly subjective composite that overlaps visa, PR, rights and integration; use components rather than one opaque stance score. |
| 46 | C39 | Visa and immigration processing efficiency | Migration, visa and settlement | IC, SC, LF | NATIONAL | WAVE_3 | Useful administrative-quality measure, but comparable official processing-time and rejection-rate data may be incomplete. |
| 47 | C31 | Immigrant community depth | Migration, visa and settlement | IC, SC, CR, LF | CITY_OR_REGIONAL | WAVE_3 | Valuable for origin-specific users but bilateral and city-level; likely too sparse for one universal score. |
| 48 | C02 | Technology and engineering education | Education and human capital | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | High value for technical profiles, but institution-level rankings may be commercial or city-concentrated. |
| 49 | C03 | Medical and health-sciences education | Education and human capital | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | High value for medical students; programme recognition and licensing make simple country scoring difficult. |
| 50 | C04 | Business, commerce, and management education | Education and human capital | IC, SC | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Useful sector branch, but likely overlaps the broader higher-education criterion. |
| 51 | C20 | Remote-work suitability | Employment, income and economic opportunity | IC, DO, CR, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | User-relevant composite but overlaps internet, visas, taxes and jobs; city and time-zone dependence is substantial. |
| 52 | C18 | Income growth and career mobility | Employment, income and economic opportunity | IC, SC, CR, LF | NATIONAL_WITH_CITY_CAVEAT | WAVE_3 | Meaningful long-term outcome but difficult to measure comparably and likely slow or survey-dependent. |
| 53 | C23 | Consumption and indirect-tax burden | Tax, cost and financial conditions | IC, SC | NATIONAL | WAVE_3 | Useful cost input but partly reflected in observed price levels and varies by goods and exemptions. |
| 54 | C27 | Childcare and family-cost burden | Tax, cost and financial conditions | IC, SC, CR, LF | CITY_OR_REGIONAL | WAVE_3 | Important for families but city-, age-, household- and policy-specific, with weak global standardization. |
| 55 | C09 | International-school availability | Education and human capital | IC, SC, CR, LF | CITY_OR_REGIONAL | WAVE_3 | Important to globally mobile families but primarily city-level and likely dependent on non-government directories. |
| 56 | C61 | International connectivity | Infrastructure and daily-life reliability | IC, SC, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Relevant for migrants and travel, but airport/city concentration and commercial schedule data complicate national scoring. |
| 57 | C59 | Transport and logistics infrastructure | Infrastructure and daily-life reliability | IC, SC, DO | NATIONAL_WITH_CITY_CAVEAT | DEFER_OR_SPECIAL_STUDY | Useful national infrastructure component but overlaps the existing experimental composite and may favor trade over residents. |
| 58 | C60 | Urban public transport | Infrastructure and daily-life reliability | IC, SC, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Highly useful for actual movers, but inherently metropolitan and difficult to normalize globally. |
| 59 | C64 | Temperature comfort | Climate, environment and location | IC, SC, CR, PF, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Strong user relevance but primarily city/regional and preference-dependent; national annual averages are misleading. |
| 60 | C65 | Climate preference fit | Climate, environment and location | IC, SC, PF, LF | PREFERENCE_MODEL | DEFER_OR_SPECIAL_STUDY | Should be a user preference-match model, not a universal higher-is-better score. |
| 61 | C69 | Environmental quality beyond PM2.5 | Climate, environment and location | IC, SC, DO, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Too broad as one measure and overlaps pollution, water, waste, biodiversity and urban quality. |
| 62 | C43 | Cultural openness and diversity | Language, culture and integration | IC, SC, DO, CR, LF | NATIONAL_WITH_CITY_CAVEAT | DEFER_OR_SPECIAL_STUDY | Broad and subjective; likely overlaps immigrant inclusion, rights and diversity measures. |
| 63 | C75 | Religious freedom and freedom of expression | Family, lifestyle and long-term liveability | IC, SC | NATIONAL | DEFER_OR_SPECIAL_STUDY | Meaningful rights criterion with plausible legal measures; legal protections and lived practice should remain distinct. |
| 64 | C45 | LGBTQ+ legal and social inclusion | Language, culture and integration | IC, SC | NATIONAL | DEFER_OR_SPECIAL_STUDY | Potentially measurable through law and rights datasets, but lived safety and social acceptance should be separated. |
| 65 | C47 | Property-crime and everyday safety | Safety, health and public services | IC, SC, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | High practical value but reporting practices and victimization survey coverage are inconsistent; city effects are large. |
| 66 | C51 | Emergency-care readiness | Safety, health and public services | IC, SC, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Important but operational emergency metrics are rarely globally standardized and are often local. |
| 67 | C55 | Mental-health support | Safety, health and public services | IC, SC, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Important lived need, yet provider access, affordability and stigma are difficult to compare globally. |
| 68 | C54 | Food safety and public-health protection | Safety, health and public services | IC, SC, LF | NATIONAL | DEFER_OR_SPECIAL_STUDY | Useful in principle, but comparable inspection and outbreak-response measures are fragmented. |
| 69 | C78 | Overall life satisfaction | Family, lifestyle and long-term liveability | IC, SC, DO, CR, PF, LF | NATIONAL_WITH_CITY_CAVEAT | DEFER_OR_SPECIAL_STUDY | Useful outcome check, not a causal relocation criterion; survey culture and annual volatility require caution. |
| 70 | C74 | Recreation, culture, and leisure | Family, lifestyle and long-term liveability | IC, SC, CR, PF, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Useful for lifestyle exploration, but subjective, city-level and unlikely to justify early production effort. |
| 71 | C73 | Quality of urban life | Family, lifestyle and long-term liveability | IC, SC, DO, CR, LF | CITY_OR_REGIONAL | DEFER_OR_SPECIAL_STUDY | Attractive product concept but primarily city-level and highly composite. |
| 72 | C41 | Local-language difficulty and learning burden | Language, culture and integration | IC, SC, PF | PREFERENCE_MODEL | DEFER_OR_SPECIAL_STUDY | Inherently depends on the user's known languages and learning context; suited to preference/profile logic. |
| 73 | C77 | Retirement suitability | Family, lifestyle and long-term liveability | IC, SC, DO, PF, LF | NATIONAL_WITH_CITY_CAVEAT | DEFER_OR_SPECIAL_STUDY | Profile composite rather than universal country property; overlaps the dedicated retirement profile. |
| 74 | C24 | Overall affordability | Tax, cost and financial conditions | IC, DO | NATIONAL | EXISTING_MONITOR | Already represented by Konsider's broad household price-level criterion; retain as baseline, not new Phase 5 research. |
| 75 | C44 | Gender equality | Language, culture and integration | IC, DO | NATIONAL | EXISTING_MONITOR | Already represented by women's legal and economic equality; lived-outcome expansion may be researched separately later. |
| 76 | C46 | Violent-crime and homicide safety | Safety, health and public services | IC, DO | NATIONAL | EXISTING_MONITOR | Already represented by intentional homicide; broader violent crime is not automatically comparable. |
| 77 | C52 | Air pollution | Safety, health and public services | IC, DO | NATIONAL | EXISTING_MONITOR | Already represented by population-weighted PM2.5; city air-quality detail belongs to a future layer. |
| 78 | C63 | Infrastructure readiness composite | Infrastructure and daily-life reliability | IC, DO | NATIONAL | EXISTING_MONITOR | Existing experimental composite; Phase 5 should evaluate components and redundancy rather than treat it as a new criterion. |
| 79 | C79 | Suitability for a software professional | Profile-dependent composites | PC, DO | PROFILE_ONLY | PROFILE_LAYER | Explicit profile composite built from approved independent criteria; do not search for a separate source. |
| 80 | C80 | Suitability for a medical professional | Profile-dependent composites | PC, DO | PROFILE_ONLY | PROFILE_LAYER | Explicit profile composite with licensing and language dependencies; do not treat as standalone data. |
| 81 | C81 | Suitability for a student | Profile-dependent composites | PC, DO | PROFILE_ONLY | PROFILE_LAYER | Explicit profile composite combining education, affordability, safety and migration pathways. |
| 82 | C82 | Suitability for a family with school-age children | Profile-dependent composites | PC, DO | PROFILE_ONLY | PROFILE_LAYER | Explicit family profile composite; should be calculated after component criteria mature. |
| 83 | C83 | Suitability for an entrepreneur | Profile-dependent composites | PC, DO | PROFILE_ONLY | PROFILE_LAYER | Explicit entrepreneur profile composite; avoid duplicating its underlying business, tax and migration criteria. |
| 84 | C84 | Suitability for retirement | Profile-dependent composites | PC, DO, PF | PROFILE_ONLY | PROFILE_LAYER | Explicit retirement profile composite and near-duplicate of retirement suitability; calculate from components. |

---

## 8. First balanced research batch

The first batch contains 15 criteria. It deliberately covers jobs, legal mobility, financial viability, education, integration, health, infrastructure and environmental risk.

| Order | ID | Criterion | Decision area | Primary research risk |
| --- | --- | --- | --- | --- |
| 1 | C11 | Overall job-market opportunity | Employment, income and economic opportunity | Definition, coverage and comparability |
| 2 | C32 | Skilled-work visa accessibility | Migration, visa and settlement | Policy volatility and comparability |
| 3 | C33 | Permanent-residency accessibility | Migration, visa and settlement | Policy volatility and comparability |
| 4 | C17 | Average earning potential | Employment, income and economic opportunity | Household scenarios and effective burden |
| 5 | C21 | Personal income-tax burden | Tax, cost and financial conditions | Household scenarios and effective burden |
| 6 | C25 | Housing affordability | Tax, cost and financial conditions | City-level prices and definitions |
| 7 | C50 | Healthcare system capacity and quality | Safety, health and public services | Capacity, outcomes, access and migrant eligibility |
| 8 | C40 | English usability | Language, culture and integration | Population proficiency versus practical service access |
| 9 | C01 | Overall higher-education opportunity | Education and human capital | National outcomes versus institution/local variation |
| 10 | C30 | Existing immigrant share | Migration, visa and settlement | Definition, coverage and comparability |
| 11 | C12 | Software and technology jobs | Employment, income and economic opportunity | City concentration and occupational taxonomy |
| 12 | C58 | Internet access, speed, and reliability | Infrastructure and daily-life reliability | Access versus reliability and consistent measurement |
| 13 | C56 | Electricity access and reliability | Infrastructure and daily-life reliability | Access versus reliability and consistent measurement |
| 14 | C08 | School education quality | Education and human capital | National outcomes versus institution/local variation |
| 15 | C66 | Extreme-weather risk | Climate, environment and location | Hazard, exposure and resilience must stay distinct |

### Why this batch is balanced

- It attacks the largest product gaps: jobs, visas, PR, tax, housing, healthcare and language.
- It includes both easy-looking national statistical indicators and hard policy criteria.
- It tests several source patterns without requiring a generic AI search framework.
- It contains two infrastructure components separately, allowing the existing composite to be reviewed rather than blindly expanded.
- It includes one climate-risk criterion without prematurely forcing climate preference into a universal score.
- It retains software jobs because this is highly relevant to the likely initial user base, while still researching the general job market first.

### Batch 1 success criterion

The batch is successful when it produces:

- at least one measured probe candidate in five or more decision pillars;
- explicit rejection evidence for failures;
- a clear determination of which policy criteria require structured legal snapshots rather than ordinary statistical APIs;
- enough repeated patterns to justify the minimal Phase 5D probe framework.

It does not need all 15 to succeed.

---

## 9. Recommended second batch

| Order | ID | Criterion | Why second |
| --- | --- | --- | --- |
| 1 | C38 | Professional-licensing accessibility for immigrants | Highly valuable but profession/origin-specific. |
| 2 | C35 | Post-study migration pathway | Important policy pathway; depends on current official rule evidence. |
| 3 | C36 | Family reunification support | Important policy pathway; depends on current official rule evidence. |
| 4 | C34 | Citizenship accessibility | Important policy pathway; depends on current official rule evidence. |
| 5 | C05 | Research and innovation ecosystem | Strong candidate but may overlap education, jobs or startup measures. |
| 6 | C15 | Engineering and skilled technical jobs | Sector branch best assessed after the general job-market model. |
| 7 | C13 | Medical and healthcare jobs | Sector branch best assessed after the general job-market model. |
| 8 | C14 | Business, finance, and professional-services jobs | Sector branch best assessed after the general job-market model. |
| 9 | C16 | Entrepreneurship and startup opportunity | Strong candidate but may overlap education, jobs or startup measures. |
| 10 | C19 | Employment protection and worker rights | Useful structural risk or rights measure after the core relocation gates. |
| 11 | C22 | Social-security and mandatory contribution burden | Complements earnings/tax research and needs scenario modelling. |
| 12 | C26 | Healthcare affordability | Complements earnings/tax research and needs scenario modelling. |
| 13 | C28 | Savings and disposable-income potential | Complements earnings/tax research and needs scenario modelling. |
| 14 | C29 | Currency and macroeconomic stability | Useful structural risk or rights measure after the core relocation gates. |
| 15 | C48 | Political stability and civil peace | Useful structural risk or rights measure after the core relocation gates. |

The second batch should be revised after Phase 5B and the first Phase 5C findings.

---

## 10. Common lifecycle statuses

Use one of these as the primary status:

| Status | Meaning |
| --- | --- |
| `NOT_SCREENED` | No Phase 5 assessment yet. |
| `SCREENED_PROMISING` | Strong initial value and source plausibility. |
| `SCREENED_POSSIBLE` | Worth deeper research, with material uncertainty. |
| `SCREENED_LOW_FEASIBILITY` | Valuable or interesting, but likely blocked. |
| `DEEP_RESEARCH_APPROVED` | Included in a Phase 5C batch. |
| `PROBE_APPROVED` | Exact source candidate approved for deterministic measurement. |
| `PROBE_MEASURED_PASS` | Probe met its declared measured threshold; production gates still remain. |
| `PROBE_MEASURED_FAIL` | Probe failed coverage, freshness, mapping, validation, licensing or comparability. |
| `PRODUCTION_CANDIDATE` | Passed research and measured gates; awaits implementation approval. |
| `EXPERIMENTAL_CANDIDATE` | Structurally usable but methodology/scoring remains explicitly provisional. |
| `RESERVE_CANDIDATE` | Credible but not selected for the initial portfolio. |
| `DEFERRED_CITY_LAYER` | Valuable only with city/regional design. |
| `DEFERRED_PROFILE_LAYER` | Should be calculated from components for a specific user profile. |
| `DEFERRED` | Not currently worth further cost, but not rejected. |
| `REJECTED` | Evidence supports stopping work. |
| `IMPLEMENTED_READY` | Published and ranking-ready. |
| `IMPLEMENTED_EXPERIMENTAL` | Published under an explicit experimental label. |

A criterion may also carry multiple blocker and caveat codes.

---

## 11. Reason-code taxonomy

### 11.1 Source and access

- `SRC_NO_AUTHORITATIVE_SOURCE`
- `SRC_NOT_DATASET_SPECIFIC`
- `SRC_OPAQUE_AGGREGATION`
- `SRC_PRIMARY_UNAVAILABLE`
- `SRC_ACCESS_FRAGILE`
- `SRC_MANUAL_ONLY`
- `SRC_VERSION_UNSTABLE`

### 11.2 Licensing

- `LIC_NO_EVIDENCE`
- `LIC_AMBIGUOUS`
- `LIC_NONCOMMERCIAL_ONLY`
- `LIC_NO_DERIVATIVES`
- `LIC_REDISTRIBUTION_RESTRICTED`
- `LIC_ATTRIBUTION_UNRESOLVED`
- `LIC_SOURCE_CHAIN_UNCLEAR`

### 11.3 Coverage and mapping

- `COV_BELOW_90_PERCENT`
- `COV_NOT_FULL_91`
- `COV_REGIONALLY_BIASED`
- `COV_MISSING_KEY_DESTINATIONS`
- `MAP_NO_STABLE_COUNTRY_ID`
- `MAP_TERRITORY_AMBIGUITY`
- `MAP_ECONOMY_COUNTRY_MISMATCH`
- `MAP_MANUAL_NONDETERMINISTIC`

### 11.4 Freshness

- `FRS_STALE`
- `FRS_MIXED_REFERENCE_PERIODS`
- `FRS_UPDATE_CADENCE_UNKNOWN`
- `FRS_POLICY_SNAPSHOT_OUTDATED`
- `FRS_MODEL_EDITION_OUTDATED`

### 11.5 Methodology and comparability

- `CMP_DEFINITION_DIFFERS`
- `CMP_UNIT_DIFFERS`
- `CMP_POPULATION_DIFFERS`
- `CMP_REPORTING_CAPACITY_BIAS`
- `CMP_SURVEY_NOT_HARMONISED`
- `CMP_MODEL_ASSUMPTIONS_OPAQUE`
- `CMP_LEGAL_NOT_LIVED_OUTCOME`
- `CMP_STOCK_FLOW_MISMATCH`
- `CMP_GROSS_NET_MISMATCH`
- `CMP_METHODOLOGY_BREAK`
- `CMP_IMPUTED_VALUES_REQUIRED`

### 11.6 Product semantics and granularity

- `GRA_CITY_LEVEL_REQUIRED`
- `GRA_ORIGIN_SPECIFIC`
- `GRA_PROFESSION_SPECIFIC`
- `GRA_HOUSEHOLD_SCENARIO_REQUIRED`
- `PRF_PROFILE_ONLY`
- `PRF_PREFERENCE_MATCH_REQUIRED`
- `SEM_QUESTION_TOO_BROAD`
- `SEM_NOT_ACTIONABLE`
- `SEM_CAUSALITY_OVERCLAIM`

### 11.7 Scoring and redundancy

- `SCO_NO_CLEAR_DIRECTION`
- `SCO_NO_DEFENSIBLE_THRESHOLDS`
- `SCO_COMPOSITE_WEIGHTS_ARBITRARY`
- `SCO_SAMPLE_RELATIVE_DISTORTION`
- `SCO_UNCERTAINTY_TOO_HIGH`
- `RED_EXISTING_CRITERION`
- `RED_CANDIDATE_OVERLAP`
- `RED_SHARED_COMPONENTS`
- `RED_HIGH_CORRELATION`

### 11.8 Operations and reproducibility

- `OPS_NO_REPLAY`
- `OPS_NO_RAW_ARTIFACT`
- `OPS_NO_RECORD_PROVENANCE`
- `OPS_EXCESSIVE_MANUAL_MAINTENANCE`
- `OPS_CHANGE_DETECTION_UNAVAILABLE`
- `OPS_PARSER_TOO_FRAGILE`
- `OPS_COST_DISPROPORTIONATE`

Reason codes should be preserved for rejected candidates. A later source edition may make a prior rejection worth revisiting.

---

## 12. Candidate source families for Phase 5B

These are **discovery families, not approved sources**.

| Domain | Source families to investigate |
| --- | --- |
| Education | UNESCO and other official education-statistics systems; OECD where coverage permits; World Bank representations; official qualification and student-mobility sources. |
| Employment | ILO statistical systems; World Bank representations; OECD where relevant; official occupational and vacancy statistics. |
| Tax and finance | Official tax authorities; OECD comparative tax systems; IMF and World Bank macroeconomic sources. |
| Migration | UN international-migrant datasets; OECD migration systems; official immigration, residence and citizenship authorities. |
| Language and integration | Official census/language data; recognised comparative surveys; legal anti-discrimination datasets. Commercial proficiency rankings should be discovery-only until licence and methodology pass. |
| Safety and health | WHO and official health systems; World Bank representations; official justice and governance datasets. |
| Infrastructure | ITU, World Bank, official energy systems, water/sanitation monitoring systems, transport and digital-government datasets. |
| Climate and hazards | Official meteorological, disaster-risk and climate-model publishers with transparent editions and scenarios. |
| Rights and liveability | ILO, official legal datasets, accountable governance systems, and harmonised surveys with clear licences. |

Phase 5B must replace these families with exact dataset candidates.

---

## 13. Standard Markdown report schema

Every Phase 5C criterion report should use this structure:

```markdown
# <Criterion ID> — <Criterion name>

## Decision summary
- Status:
- Recommendation:
- Decision pillar(s):
- Research owner:
- Evidence cutoff:
- Primary blocker codes:
- Caveat codes:

## 1. Relocation question
## 2. Precise definition
## 3. Classification and granularity
## 4. User profiles and decision value
## 5. Source candidates

### Source candidate <ID>
- Publisher:
- Dataset/series/table:
- Access:
- Version/edition:
- Methodology:
- Unit/population:
- Update cadence:
- Original upstream source:
- Licence evidence:
- Required attribution:
- Known limitations:

## 6. Comparability assessment
## 7. Expected or measured 91-country coverage
## 8. Freshness assessment
## 9. Country mapping and territory policy
## 10. Scoring options and sensitivity risks
## 11. Redundancy and composite risks
## 12. Retrieval, replay and maintenance
## 13. Blockers, caveats and reason codes
## 14. Recommendation
## 15. Open questions
## Evidence register
```

Rules:

- separate source facts from Konsider judgement;
- distinguish expected from measured coverage;
- quote licences sparingly and preserve exact links;
- do not claim “official” without identifying the accountable publisher;
- do not combine sources without documenting semantic equivalence and precedence;
- do not hide rejected source candidates.

---

## 14. Machine-readable record model

The companion JSON Schema file defines the authoritative shape. Core fields include:

```json
{
  "phase_id": "5A",
  "criterion_id": "C11",
  "name": "Overall job-market opportunity",
  "category": "Employment, income and economic opportunity",
  "classification_tags": ["IC"],
  "natural_granularity": "NATIONAL_WITH_CITY_CAVEAT",
  "decision_pillars": ["WORK_AND_STUDY"],
  "relocation_question": "...",
  "definition": "...",
  "research_rank": 1,
  "research_wave": "BATCH_1",
  "status": "DEEP_RESEARCH_APPROVED",
  "coverage": {
    "universe_id": "stable_supported_v1",
    "denominator": 91,
    "expected_band": "HIGH",
    "measured": false
  },
  "freshness_class": "FAST_MOVING",
  "source_candidates": [],
  "comparability": {},
  "licensing": {},
  "country_mapping": {},
  "scoring": {},
  "redundancy": {},
  "blocker_codes": [],
  "caveat_codes": [],
  "evidence": []
}
```

The schema permits several source candidates per criterion and requires evidence-level labels so estimates are not mistaken for measured facts.

---

## 15. Handoffs to later phases

### Phase 5B must deliver

- one completed screening record for every C01–C84;
- exact distinction between verified fact, informed estimate and unverified hypothesis;
- a revised ordered list;
- 35–45 deep-research candidates;
- revised first and second batches;
- initial source-candidate inventory;
- clear city/profile deferrals.

### Phase 5C must deliver

- dataset-specific evidence;
- licensing review;
- expected or measured coverage;
- source-specific limitations;
- explicit recommendation and reason codes;
- a shortlist for deterministic probes.

### Phase 5D must not begin as a generic platform project

It should begin only after Phase 5C reveals repeated technical patterns. The first implementation should support two or three representative source types and reuse the repository's existing raw artifact, attempt, mapping and report conventions.

### Phase 5F owns guardrail changes

Phase 5A deliberately leaves these questions open:

- whether any enabled criterion may have less than 91/91 coverage;
- whether informational partial coverage is useful;
- whether a criterion can use semantically equivalent multi-source fallbacks;
- whether policy criteria require a separate readiness model;
- whether survey indicators can be production-ready;
- whether any city-level data belongs in country scoring;
- whether the stable country universe may ever shrink or branch by profile.

No later implementation should assume an answer before Phase 5F.

---

## 16. Phase 5A completion criteria

Phase 5A is complete when:

- all 84 candidates have a classification and research order;
- the first batch is balanced across major relocation decisions;
- the 90% screening threshold is clearly separated from production completeness;
- lifecycle statuses and reason codes are standardised;
- Markdown and machine-readable report contracts exist;
- profile composites and city-layer candidates are explicitly separated;
- current publication guardrails remain unchanged;
- Desktop ChatGPT Work and Codex have an unambiguous handoff.

This document satisfies those criteria.
