# Homicide source feasibility study: homicide-source-2026-07-23.4-online

- Baseline complete countries: 91
- Homicide-only exclusions evaluated: 30
- Required complete countries: 100
- Freshness rule: unchanged at 5 years
- Result: **FAIL**

## Primary sources

Direct UNODC recovered 4 countries
(BGD, BLR, KWT, SAU) and produced
95 complete countries.

UNSD recovered 4 countries
(BGD, BLR, KWT, SAU) and produced
95 complete countries.

Both channels represent intentional-homicide victims per 100,000 population. Direct UNODC was
filtered to national total, both sexes, all ages, and total category. UNSD was filtered to
`VC_IHR_PSRC`, country geography, `BOTHSEX`, global reporting type, `PER_100000_POP`, and observed
country/country-adjusted nature (`C` or `CA`). The UNSD record does not expose age explicitly.

## Conditional fallbacks

Fallback evaluation triggered: True. The residual set contained
26 countries. Eurostat recovered
0 countries; OECD recovered
0. The resulting complete count remained
95.

Eurostat publishes a semantically suitable ICCS 0101 victim-rate table, but its geographic coverage
does not include the residual countries. OECD's homicide-labelled dataset is regional rather than a
national-total series and was rejected as non-equivalent.

## Licensing and operational suitability

Direct UNODC provides an official downloadable workbook and UNSD provides a documented JSON API.
Exact bytes were retained for offline replay. Neither channel exposes a clear provisional/final flag.
The general UN terms do not establish production redistribution rights, so licensing remains a separate
adoption blocker. See `licensing.md`.

## Recommendation

Outcome D applies: the unchanged five-year observed-data policy cannot support 100 complete countries
through the evaluated authoritative channels. Do not migrate the production source, adopt mixed-source
precedence, weaken freshness, impute values, or activate a release. A product decision would be required
before changing the criterion policy or considering a different construct.

The production WDI registration and active release were not changed.
