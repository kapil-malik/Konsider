# Phase 5G - C66 Extreme heat exposure onboarding

Date: 2026-07-29

Decision: **experimentally production-onboarded**

Release: `2026-07-29.1`

## Outcome

C66 is now the locality-derived criterion **Extreme heat exposure**. Its historical
`Extreme-weather risk` name is retained only as lineage. The criterion is PCC because 89/91
countries have valid country results, and LSC because those results are derived from city
observations. Those classifications remain independent.

The active release moved from schema 4/catalog 2 to schema 5/catalog 3 so the API and UI can consume
the structured locality evidence natively. The 12 existing criteria were migrated from immutable
release `2026-07-28.2` without changing their canonical scores or non-valid outcomes.

## Resolved construct decision and disclaimer

Konsider interprets `CL_UTC_T32_2020` as the annual mean number of days in the decade ending 2020
when daily maximum Universal Thermal Climate Index exceeded 32 degrees Celsius.

That interpretation is supported by:

- the JRC indicator name;
- the JRC unit, `Number of days`;
- the day-based upstream Copernicus variable; and
- the measured 0-357 range across the selected localities.

The product retains this visible disclaimer:

> JRC's indicator name and unit describe annual mean extreme-heat days, while one methodology
> sentence inconsistently refers to counting pixels. Konsider follows the day interpretation.

This is an explicit experimental product interpretation, not a claim that the publisher's
documentation is internally consistent.

## Source and licence freeze

| Item | Frozen value |
| --- | --- |
| Publisher | European Commission, Joint Research Centre |
| Dataset | GHS-UCDB R2024A V1.2 |
| Exact asset | `GHS_UCDB_THEME_CLIMATE_GLOBE_R2024A_V1_2.zip` |
| Exact field | `CL_UTC_T32_2020` |
| Reference period | 2011-2020 |
| Parser | `jrc-ghsl-urban-climate-csv@1.0` |
| Licence | CC BY 4.0; commercial use and redistribution permitted with attribution and change indication |
| Raw retention | Exact archive retained locally under ignored `data/raw/phase5g/` |
| Raw SHA-256 | `966b96ef701a8b0053467179a1231ddc24830ac2693aadd7d1388f281795c0bb` |

The release stores the JRC publisher, dataset version, canonical dataset page, attribution,
reference period, source URL, and checksum in structured source lineage.

## Locality universe and coverage

The criterion uses `ghsl-ucdb-top5-population-v1`:

- GHSL urban centres with 2025 population of at least 50,000;
- up to five most populous centres per supported country;
- population descending, then GHSL ID ascending;
- selected before observing the heat value.

Results:

| Measure | Result |
| --- | ---: |
| Source urban-centre records | 11,422 |
| Selected localities | 388 |
| Mapped localities | 388 |
| Valid locality values | 388 |
| Valid countries | 89/91 |
| Missing countries | Antigua and Barbuda and Grenada |
| Coverage mode | Conditional complete case |

Both missing countries have `NO_QUALIFYING_LOCALITY`; neither is silently mapped or imputed.

## Scoring and aggregation

Locality score:

`10 - 9 * clamp(annual_mean_days, 0, 365) / 365`

This gives 10 to zero extreme-heat days and 1 to a full 365 days. The observed source range is
0-357. Country results average the two highest-scoring localities, or use one where only one
qualifies. All valid locality evidence remains available even though only two values contribute.

The top-two choice is stable against the nearest alternatives:

| Comparison | Spearman rho | Mean absolute rank movement |
| --- | ---: | ---: |
| Top two versus top one | 0.971 | 4.10 |
| Top two versus top three | 0.986 | 2.58 |
| Top two versus all five | 0.909 | 6.40 |
| Top two versus population weighted | 0.910 | 7.12 |

The relationship between country score and number of eligible localities is effectively zero
(`rho = 0.011`), so the measured result does not show a simple large-country advantage.

The strongest correlation with an existing criterion is moderate (`rho = 0.608`, women's legal
and economic equality). C66 is retained because its source and construct are independent and it
adds direct heat-exposure evidence.

## Ranking movement and examples

Under the balanced preset:

- eligibility remains 83 countries because Antigua and Barbuda and Grenada were already excluded
  by other active PCC evidence;
- 65 countries change rank;
- mean absolute movement is 2.12 positions;
- maximum movement is 10 positions.

Example contributing localities:

| Country | Contributor 1 | Days | Contributor 2 | Days |
| --- | --- | ---: | --- | ---: |
| Canada | Vancouver | 8 | Edmonton | 11 |
| India | Bengaluru | 182 | New Delhi | 245 |
| Norway | Stavanger | 0 | Trondheim | 0 |

These contributors represent the two strongest heat-opportunity scores among the frozen major-city
universe. They do not represent average national exposure.

## Release, replay, API, and UI

Release `2026-07-29.1` is published, product-ready, and active:

- release schema: `konsider-release-5.0`;
- catalog schema: `consumer-catalog-3.0`;
- geographic entities: 479, comprising 91 countries and 388 cities;
- C66 derived country evidence rows: 89;
- release checksum:
  `sha256:d99cf9c6e266b6bf3a9f5d899ad2bad78e07a929ed13a42a2b42899c0856db4d`;
- retained-source replay: passed.

API v2 exposes the criterion's structured PCC coverage, locality-derived scope, publisher
metadata, disclaimer flags, country contribution, selected localities, all valid locality evidence,
and locality assessment. The Phase 5F UI consumes these API-owned fields without calculating them.

## Limitations

- The underlying decade ends in 2020.
- The publisher documentation inconsistency remains disclosed.
- Urban-centre averages hide neighbourhood variation.
- The linear score is a transparent product transform, not a health-impact function.
- The best-destination aggregation answers whether a country contains lower-exposure major
  destinations; it is not average resident exposure.
- It does not measure adaptation, cooling access, health vulnerability, or non-heat hazards.
