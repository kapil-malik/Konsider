# Phase 5A locality criteria discovery

Status: complete

Date: 2026-07-28

Scope: research, classification, locality-universe direction, and first-wave recommendation only

Runtime, API, UI, contracts, and active release changed: no

## Executive decision

Phase 5 should proceed with a locality-aware foundation, but it should not begin by forcing the
most appealing city questions into weak global proxies.

The first wave should contain one criterion:

- **C66, narrowed and renamed to Extreme heat exposure**, using the European Commission JRC
  `GHS-UCDB R2024A v1.2` climate asset and the `CL_UTC_T32_2020` field.

The first-wave count is deliberately one. It is enough to exercise real locality ingestion and
country derivation while synthetic contracts cover multiple-LSC combinations. It also avoids
lowering source and construct standards merely to demonstrate overlap behavior.

Three candidates remain promising second-wave research:

- C05 Research and innovation ecosystem, using a pinned OpenAlex snapshot after a locality-mapping
  and bibliometric-construct probe;
- C67 Long-term climate-change exposure, after one scenario, horizon, hazard, and scoring
  interpretation are frozen; and
- C68 Natural-disaster risk, after replacing or refreshing the current 2015-ended event occurrence
  evidence with a defensible risk construct.

The original obvious locality candidates remain important, but none clears every gate:

- housing and earnings require household and occupation context;
- English usability requires an English-speaking user context and lacks a reproducible licensed
  locality dataset;
- occupation-specific jobs require occupation, qualification, licensing, and metro demand data;
- water and electricity reliability require validated utility/service-area data;
- internet speed has strong measured locality coverage, but the exact JRC asset and its upstream
  Ookla non-commercial licence create an unresolved component-rights boundary.

This is an evidence-quality decision, not a judgment that these product questions lack value.

## Evidence reviewed

Repository evidence:

- all 45 Phase 3C records in the three retained research batches;
- the Phase 3 closure report and approved Phase 3F portfolio decision;
- deterministic Phase 3E and 3G-0 probe reports;
- the Phase 4 closure report, coverage contract, active catalog, release format, API guide, UI
  guide, and active release `2026-07-28.2`;
- the current stable 91-country universe and release-scoped catalog.

Current source evidence was checked against exact or official source pages:

- [JRC GHS-UCDB R2024A catalog](https://data.jrc.ec.europa.eu/dataset/1a338be6-7eaf-480c-9664-3a8ade88cbcd)
  and exact v1.2 downloadable theme archives;
- [GHSL urban-centre documentation](https://human-settlement.emergency.copernicus.eu/ghs_ucdb_2024.php);
- [GHSL-OECD global functional urban areas](https://data.jrc.ec.europa.eu/dataset/347f0337-f2da-4592-87b3-e25975ec2c95);
- [OpenAlex developer documentation](https://developers.openalex.org/) and
  [snapshot format](https://developers.openalex.org/download/snapshot-format);
- [OpenAlex data and pricing statement](https://help.openalex.org/hc/en-us/articles/24397762024087-Pricing);
- [OECD functional urban areas](https://www.oecd.org/en/data/datasets/oecd-definition-of-cities-and-functional-urban-areas.html),
  [FUA labour data](https://data-explorer.oecd.org/vis?df%5Bag%5D=OECD.CFE.EDS&df%5Bds%5D=dsDisseminateFinalDMZ&df%5Bid%5D=DSD_FUA_LAB%40DF_LABOUR),
  and [open-access policy](https://www.oecd.org/en/about/oecd-open-by-default-policy.html);
- [EF EPI methodology and raw-data statement](https://www.ef.com/wwen/epi/about-epi/);
- [ILOSTAT bulk-download facility](https://ilostat.ilo.org/data/bulk/);
- [Ookla open-data repository and licence](https://github.com/teamookla/ookla-open-data);
- [World Bank IBNET reproducibility catalog entry](https://reproducibility.worldbank.org/catalog/484);
- [Copernicus ERA5 documentation and licence](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=documentation).

The full row-level evidence, retained Phase 3 source candidates, exact assets, coverage estimates,
licensing conclusions, risks, aggregations, and blockers are in the
[machine-readable matrix](../../data/reports/phase5a-2026-07-28/criterion-disposition-matrix.json).

## Classification rules

| Label | Meaning |
| --- | --- |
| `FIRST_WAVE` | Best current production-onboarding candidate, subject to its named final gates. |
| `SECOND_WAVE` | Source family is promising, but an exact construct, coverage, mapping, or freshness probe must precede onboarding. |
| `RESEARCH_ONLY` | Locality matters, but no current path clears enough gates to schedule production work. |
| `PROFILE_PHASE` | The useful answer depends on applicant, occupation, qualification, institution, household, or preference inputs. |
| `REJECT_LOCALITY_PROXY` | Locality aggregation would change, duplicate, or misstate the researched criterion. |

`PROFILE_PHASE` does not mean that locality is irrelevant. It means an independently aggregated
country opportunity score would answer the wrong question without profile context.

## Complete 45-criterion disposition matrix

Every Phase 3C criterion appears exactly once.

| ID | Exact Phase 3 name | Natural evidence level | Locality materially helps | Independent locality proxy defensible | Profile data required | Default local unit | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Overall higher-education opportunity | Institution + applicant | Yes | No | Yes | Institution | `PROFILE_PHASE` |
| C05 | Research and innovation ecosystem | Metro + institution | Yes | Yes | No | Metro | `SECOND_WAVE` |
| C06 | International-student accessibility | Institution + applicant | Yes | No | Yes | Institution | `PROFILE_PHASE` |
| C08 | School education quality | Region/state + city + applicant | Yes | No | Yes | Region/state | `PROFILE_PHASE` |
| C11 | Overall job-market opportunity | Metro | Yes | Yes | No | Metro | `RESEARCH_ONLY` |
| C12 | Software and technology jobs | Metro + applicant | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C13 | Medical and healthcare jobs | Metro + region/state + applicant | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C14 | Business, finance, and professional-services jobs | Metro + applicant | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C15 | Engineering and skilled technical jobs | Metro + region/state + applicant | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C16 | Entrepreneurship and startup opportunity | Metro | Yes | Yes | No | Metro | `RESEARCH_ONLY` |
| C17 | Average earning potential | Metro + applicant | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C19 | Employment protection and worker rights | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C21 | Personal income-tax burden | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C22 | Social-security and mandatory contribution burden | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C25 | Housing affordability | Metro + household | Yes | No | Yes | Metro | `PROFILE_PHASE` |
| C26 | Healthcare affordability | Country + applicant | Yes | No | Yes | None | `PROFILE_PHASE` |
| C29 | Currency and macroeconomic stability | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C30 | Existing immigrant share | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C32 | Skilled-work visa accessibility | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C33 | Permanent-residency accessibility | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C34 | Citizenship accessibility | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C35 | Post-study migration pathway | Country + institution + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C36 | Family reunification support | Country + applicant | No | No | Yes | None | `PROFILE_PHASE` |
| C38 | Professional-licensing accessibility for immigrants | Region/state + institution + applicant | Yes | No | Yes | Region/state | `PROFILE_PHASE` |
| C40 | English usability | City + applicant preference | Yes | No | Yes | City | `PROFILE_PHASE` |
| C42 | Social inclusion and acceptance of immigrants | City + region/state | Yes | No | No | City | `RESEARCH_ONLY` |
| C45 | LGBTQ+ legal and social inclusion | Country + city + applicant | Yes | No | Yes | City | `PROFILE_PHASE` |
| C48 | Political stability and civil peace | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C49 | Rule of law and institutional trust | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C50 | Healthcare system capacity and quality | Region/state + metro | Yes | No | No | Metro | `RESEARCH_ONLY` |
| C53 | Water quality and sanitation | Country | Yes | No | No | None | `REJECT_LOCALITY_PROXY` |
| C54 | Food safety and public-health protection | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C56 | Electricity access and reliability | Utility/service area | Yes | Yes | No | Utility/service area | `RESEARCH_ONLY` |
| C57 | Water-supply reliability | Utility/service area | Yes | Yes | No | Utility/service area | `RESEARCH_ONLY` |
| C58 | Internet access, speed, and reliability | Metro + city | Yes | Yes | No | Metro | `RESEARCH_ONLY` |
| C62 | Digital-government readiness | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C66 | Extreme-weather risk | City | Yes | Yes, after narrowing | No | City | `FIRST_WAVE` |
| C67 | Long-term climate-change exposure | City | Yes | Yes, after construct freeze | No | City | `SECOND_WAVE` |
| C68 | Natural-disaster risk | City + region/state | Yes | Yes, after construct freeze | No | City | `SECOND_WAVE` |
| C69 | Environmental quality beyond PM2.5 | City + region/state | Yes | No as one composite | No | City | `REJECT_LOCALITY_PROXY` |
| C70 | Climate resilience and adaptation readiness | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C71 | Work-life balance | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C75 | Religious freedom and freedom of expression | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |
| C76 | Social protection and welfare support | Country + applicant | Yes | No | Yes | None | `PROFILE_PHASE` |
| C78 | Overall life satisfaction | Country | No | No | No | None | `REJECT_LOCALITY_PROXY` |

The machine-readable matrix contains the original Phase 3 disposition text rather than replacing
it with this new classification.

## Re-evaluation of the starting hypotheses

| Candidate | Phase 5A result | Reason |
| --- | --- | --- |
| C25 Housing affordability | `PROFILE_PHASE` | Metro evidence is necessary but not sufficient. A useful score requires tenure, dwelling, household income, and tax assumptions. OECD regional house-price indices measure price movement rather than comparable household affordability levels. |
| C40 English usability | `PROFILE_PHASE` | The question depends on the user's language needs. EF EPI is self-selected, excludes many native-English destinations from symmetric measurement, and does not provide reusable raw data. |
| C12 Software and technology jobs | `PROFILE_PHASE` | Metro demand matters, but two-digit ILO occupations do not identify software opportunity and national data cannot recover metro vacancies. |
| C13 Medical and healthcare jobs | `PROFILE_PHASE` | Qualification recognition and licensing are threshold conditions; provider shortage is not accessible job opportunity. |
| C14 Business, finance, and professional-services jobs | `PROFILE_PHASE` | The occupation family and qualification must be specified before locality evidence can be interpreted. |
| C15 Engineering and skilled technical jobs | `PROFILE_PHASE` | Occupation code, licence, trade recognition, and regional demand are inseparable from the applicant. |
| C57 Water-supply reliability | `RESEARCH_ONLY` | Utility area is the right unit, but current IBNET exact assets are temporally uneven and partly limited-access. |
| C17 Average earning potential | `PROFILE_PHASE` | Nominal or average metro earnings do not answer occupation-specific disposable earning potential. |

The review adds C66 to the first wave and C05, C67, and C68 to the second-wave queue. It also
identifies C58 as technically strong but legally unresolved.

## Locality unit study

| Unit | Best use | Strengths | Main failure mode | Phase 5 direction |
| --- | --- | --- | --- | --- |
| Administrative city | Urban climate, dense urban environment, some city services | Globally available through harmonised GHSL urban-centre geometry; stable source IDs | Municipal boundaries can omit commuting suburbs and may not match official city names | Use for heat and other truly urban-form/exposure constructs. |
| Functional urban area / metro | Jobs, housing, earnings, commuting, research clusters | Better represents labour and housing markets than a municipality | Global FUA boundaries are modelled outside countries with commuting-flow data; current global JRC edition is based on 2015 centres | Default for economic opportunity families, with source/method flags. |
| State/province/region | Regulated professions, school systems, healthcare administration, electricity markets | Often matches policy and licensing authority | Units vary greatly in scale and are not interchangeable across countries | Use only where the criterion's authority or data is explicitly regional. |
| Utility/service area | Water continuity, electricity reliability, network services | Matches the actual provider and infrastructure | Boundaries and identifiers are hard to obtain globally and change through mergers | Required for utility reliability; never substitute a city label for a service territory. |
| Institution | Universities, post-study paths, professional recognition | Matches the actual decision object | Does not naturally collapse into one universal country score | Reserve for the future profile/institution layer. |

Jobs, housing, commuting, and earnings must default to a functional urban area, not a municipal
boundary. The C66 first-wave construct is different: heat exposure is measured over harmonised
urban-centre geometry, so the urban centre is the appropriate first locality unit.

## Proposed locality-universe policy

Draft policy ID: `major-urban-opportunity-v1-draft`

Source entity set: `GHS-UCDB R2024A v1.2`, fixed 2025 boundaries.

### Inclusion and selection

1. Start with every quality-controlled GHSL urban centre in the country. The Degree of
   Urbanisation definition supplies a harmonised minimum urban-centre population of 50,000.
2. Sort by the source's frozen `GC_POP_TOT_2025` value descending, then stable `ID_UC_G0`
   ascending.
3. Select at most five urban centres per country.
4. Perform the selection before loading or inspecting any criterion values.
5. Retain every selected locality in evidence even when an aggregation uses fewer contributors.
6. For metro-family criteria, map a selected urban core to one validated FUA. Do not silently use
   the urban-centre boundary when the construct requires a labour-market area.
7. For service-area criteria, attach validated provider territories to the selected destination
   localities. Do not overload the locality ID with a utility ID.

This is a bounded hybrid: a global population/evidence threshold establishes eligibility and a
fixed per-country cap limits large-country advantage.

### Measured inventory

Using the 91-country stable universe and the top-five rule:

- 89 countries have at least one qualifying urban centre;
- 388 localities are selected;
- 69 countries contribute five localities;
- 4 contribute four;
- 1 contributes three;
- 9 contribute two;
- 6 contribute one; and
- Antigua and Barbuda and Grenada have no qualifying GHSL urban centre.

A country with no qualifying locality receives an explicit no-locality outcome. It is not assigned
its capital or a synthetic locality.

### Small countries and city-states

- If one to four urban centres qualify, retain all of them.
- A city-state is not forced to have multiple pseudo-localities.
- A single qualifying locality may produce a country result only when the criterion's aggregation
  policy declares `minimum_valid_localities: 1`.

### Aliases and cross-border areas

- The canonical ID is the frozen source entity ID; names are display labels and aliases only.
- Source names are mapped to ISO-3 parent countries through an explicit reviewed table.
- The v1 policy assigns an urban centre to its source parent country.
- Cross-border metros are not combined into one transnational destination in v1. A later policy
  may add a cross-border entity only with explicit multi-country parentage and evidence rules.
- Ambiguous or duplicate mappings are rejected, never fuzzy-published.

### Versioning

Increment the locality-universe version when the source/version, population epoch, eligibility
definition, per-country cap, tie-breaker, country mapping, FUA mapping, or small-country and
cross-border treatment changes. Published releases retain exact inventories and mapping checksums.

## Source gate results

| Candidate/source | Useful construct | Fetchable | Exact reproducible asset | Production reuse | Comparable and fresh | Result |
| --- | --- | --- | --- | --- | --- | --- |
| C66 JRC UCDB `CL_UTC_T32_2020` | Pass after narrowing to extreme heat | Pass | Pass: v1.2 ZIP and field | Pass: exact JRC asset is CC BY 4.0 | Conditional: globally modelled and complete in selected localities, but decade ends 2020 and fact-sheet methodology wording needs confirmation | `FIRST_WAVE` |
| C05 OpenAlex snapshot | Pass for research ecosystem, not all innovation | Pass | Not yet: no quarterly manifest pinned | Pass: CC0 | Unknown until institution-to-locality mapping and field-normalised scoring probe | `SECOND_WAVE` |
| C67 JRC UCDB climate projections | Conceptually useful | Pass | Pass | Pass: CC BY 4.0 | Fail for now: scenario, horizon, hazard, and direction are not frozen | `SECOND_WAVE` |
| C68 JRC UCDB multi-hazard events | Partly useful | Pass | Pass | Pass: CC BY 4.0 | Fail for now: occurrence fields stop at 2015 and do not measure severity or expected loss | `SECOND_WAVE` |
| C58 JRC UCDB / Ookla speed | Useful narrow speed construct | Pass | Pass; measured 388/388 selected localities | Fail pending clarification: JRC asset is labelled CC BY 4.0 while upstream tiles are CC BY-NC-SA 4.0 | Reference year 2023 is fast-moving and test participation is selective | `RESEARCH_ONLY` |
| C57 IBNET utility continuity | Useful narrow continuity construct | Partial | Partial; named workbooks exist, some bytes are limited-access | Fail for a complete production set | Reporting is voluntary and uneven | `RESEARCH_ONLY` |
| C25 OECD regional housing | Useful context | Pass | Pass for the dataflow | Unresolved for all upstream components | Fail construct: price indices are not household rent-to-income levels; coverage is OECD-heavy | `PROFILE_PHASE` |
| C40 EF EPI | Weak proxy | Website only | Fail: raw data unavailable | Fail: no production dataset licence | Fail representativeness and symmetric destination coverage | `PROFILE_PHASE` |
| C11 OECD FUA labour | Useful broad metro labour context | Pass | Exact API family, not yet pinned extract | Likely favourable; exact dataflow notice still required | OECD-heavy and partly modelled from regional population shares | `RESEARCH_ONLY` |
| C12-C15 occupation jobs | High decision value | National ILO data are fetchable | No comparable global metro occupation/vacancy asset found | National ILO licence is favourable but does not solve locality | Fail occupation, qualification, licensing, and metro coverage | `PROFILE_PHASE` |
| C17 earning potential | High decision value | Regional wage tables exist in some systems | No global occupation-by-metro disposable-earnings asset found | Not reached | Fail construct without applicant occupation and taxes | `PROFILE_PHASE` |

No candidate is described as production-ready merely because a website, ranking, or API exists.

## First-wave recommendation: C66 narrowed to Extreme heat exposure

### Exact construct

Annual mean number of days in the decade for which the daily maximum Universal Thermal Climate
Index exceeded 32 degrees Celsius in an eligible urban centre.

This should become a narrow product construct named **Extreme heat exposure**. The original
research identifier C66 remains its lineage; Phase 5B should decide whether the runtime criterion
receives a new semantic ID rather than reusing an ID previously labelled broad extreme-weather
risk.

### Locality and source

- locality type: GHSL urban centre;
- locality universe: `major-urban-opportunity-v1-draft`;
- publisher/distributor: European Commission JRC, with Copernicus Climate Change Service upstream;
- exact asset: `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip`;
- exact field: `CL_UTC_T32_2020`;
- access: anonymous HTTPS archive with CSV, XLSX, and GeoPackage representations;
- licence: CC BY 4.0 on the exact JRC catalog asset; attribution required.

### Measured coverage

- 388/388 selected localities have a non-negative field value;
- 89/91 supported countries have at least one selected locality;
- Antigua and Barbuda and Grenada have no qualifying GHSL urban centre;
- the resulting criterion is expected to be a conditional complete-case criterion unless a
  separately justified small-country locality policy changes the universe.

These are Phase 5A measurements from the exact downloaded asset, not a production release.

### Aggregation proposal

1. Score every valid eligible locality with a frozen lower-is-better heat-exposure transform.
2. Select the two lowest-exposure locality scores among the independently chosen locality universe.
3. Average them.
4. If the country has only one qualifying locality, use it only because the policy explicitly
   permits `minimum_valid_localities: 1`.
5. Preserve all eligible locality observations for provenance and future common-locality analysis.

The top-two choice needs sensitivity analysis against top-one, top-three, and population-weighted
alternatives before onboarding. It must not be selected because it produces preferred rankings.

### Decision value

The current C66 research evidence is a national multi-hazard composite. The locality construct
answers a different and clearer relocation question: whether the country contains major urban
destinations with lower extreme-heat exposure. It adds destination-level discrimination that a
national mean cannot provide.

### Limitations and pre-onboarding blockers

- It measures extreme heat, not floods, storms, drought, wildfire, or broad climate suitability.
- The decadal field ends in 2020.
- It does not resolve neighbourhood-scale heat islands or housing-level cooling access.
- The JRC fact sheet's indicator description is a count of days, while its methodology sentence
  refers to a zonal count of pixels. The observed 0-365-style values support the day interpretation,
  but exact semantics must be confirmed before production.
- The score transform, precision, and top-N sensitivity are not frozen in Phase 5A.

If the semantic clarification fails, the correct Phase 5G outcome is a held disposition, not a
substitute score.

### Expected implementation complexity

Medium:

- source parsing is simple tabular ingestion;
- country and locality coverage are strong;
- entity mapping, frozen universe publication, derived lineage, scoring sensitivity, and release
  replay are new platform work;
- no applicant-profile logic is needed.

## Decision summary for later ADRs

1. Adopt `LSC` as the Phase 5 working term.
2. Keep coverage, scope, and applicability orthogonal.
3. Use a frozen global source entity inventory with an independent top-five population cap.
4. Allow criterion families to choose urban centre, FUA/metro, region, or service area; do not
   collapse these types.
5. Implement one real first-wave criterion and use synthetic fixtures for multi-LSC engine states.
6. Treat independently best localities as country opportunity; locality overlap remains advisory.
7. Preserve full locality evidence below the Medium analysis threshold.
8. Reserve profile-dependent questions for a future typed profile engine.
9. Keep conversational exploration after the typed deterministic Phase 5 system.

The machine-readable ADR handoff is
[decision-summary.json](../../data/reports/phase5a-2026-07-28/decision-summary.json).

## Verification

- All 45 Phase 3C criteria appear exactly once in the machine-readable matrix.
- Recommendation labels are restricted to the five Phase 5A values.
- One criterion, not more than three, is recommended for the first wave.
- The first-wave source asset, field, licence, coverage estimate, locality unit, aggregation, and
  blockers are explicit.
- Profile-dependent criteria are not represented as independently valid locality scores.
- No source with an unresolved exact-asset or component licence is marked production-ready.
- No runtime code, schema, contract, API, UI, catalog, release, or active pointer changed.

## Open decisions and blockers

No product clarification or technical blocker prevents Phase 5A closure.

The following decisions belong to approval of this research or to Phase 5B:

- approve one criterion as a coherent first wave rather than forcing a second;
- confirm that the narrowed product criterion should be named `Extreme heat exposure`;
- decide whether its runtime ID is new while retaining C66 as research lineage;
- approve the draft top-five locality-universe direction; and
- require resolution of the JRC fact-sheet wording before any production onboarding.
