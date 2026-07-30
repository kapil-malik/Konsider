# Phase 6A career and education source study

Status: source gates complete; implementation gate closed

Study date: 2026-07-30

## Decision

Phase 6A approves **zero** of the seven candidates for public implementation. This is not a
recommendation to weaken the coverage policy. It is the evidence required by the Phase 6 rule for
stopping when four approvals are impossible:

- the four occupation-family measures have meaningful diagnostic signal, but only 61-66 of the
  stable 91 countries have acceptable observations from 2021 or later;
- the exact UIS archive has field-of-study graduate shares, not compatible graduate counts, and
  reaches only 75-76 countries at the freshness floor;
- the academic-ecosystem candidate has no pinned OpenAlex capture and cannot be mapped
  deterministically to Konsider's locality universe from the current committed geography artifact;
  and
- every candidate fails either the 82-country PCC minimum, the nine-country combined missing-union
  limit, or both.

No active release, catalog, runtime behavior, preset, score, or public criterion changes in this
study. Phase 6 must stop before 6B unless an exact new source clears the existing gates or the owner
explicitly changes product policy in a separate decision.

## Product framing

The candidates describe destination-side opportunity evidence:

- employment-market depth;
- higher-education capacity; and
- an academic and research ecosystem.

They do **not** estimate job openings, hiring probability, job quality, qualification recognition,
professional licensing, admission probability, accreditation, language suitability, visa
eligibility, household fit, or an individual's prospects. Those remain structured applicant and
household-context questions.

The engineering employment candidate is renamed **Science and engineering employment-market
depth** because the available two-digit ISCO-08 groups include natural-science occupations.
The business stretch candidate is narrowed to **Business and administration employment-market
depth** because the official source does not support a clean "business and finance" family without
an arbitrary mix of other occupations.

## Gates and method

The study uses the immutable `stable_supported_v1` universe of 91 countries and the active
`2026-07-29.2` release. A fresh observation has reference year 2021 or later. A publishable PCC must
have at least 82 valid countries, and its non-valid countries combined with all current active PCC
non-valid countries must not exceed nine.

The five active complete-case criteria currently have eight distinct non-valid countries:
`ATG`, `BHS`, `BOL`, `FJI`, `GRD`, `GUY`, `HTI`, and `UKR`.

Every country is explicitly classified as `valid`, `missing`, `stale`, `invalid`, or `rejected` for
each candidate. The replay uses retained, ignored source captures and writes only normalized
research evidence. The machine-readable bundle is
[`data/reports/phase6a-2026-07-30`](../../data/reports/phase6a-2026-07-30/).

## Workstream A: occupation data

### Exact source and granularity

The retained source is ILOSTAT indicator
[`EMP_TEMP_SEX_OC2_NB_A`](https://rplumber.ilo.org/data/indicator/?id=EMP_TEMP_SEX_OC2_NB_A&format=csv),
Employment by sex and occupation (thousands), annual. The probe uses:

- both sexes: `SEX_T`;
- ISCO-08 two-digit classifications;
- an occupation-family numerator and total employment denominator from the same country, year, and
  national source;
- the latest acceptable combination, preferring a clean observation over an observation flagged
  with a break; and
- unreliable (`U`) observations only to classify an `invalid` outcome, never as a score input.

The exact three-digit candidate `EMP_TEMP_SEX_OC3_NB_A` returned HTTP 400 on the current official
endpoint. Engineering-specific three-digit groups therefore could not be tested. ILOSTAT rows are
published national survey or administrative observations rather than modelled estimates, but
national sources and survey designs differ. A break flag can be accepted for a level observation
with a quality flag; it is not acceptable for a trend calculation.

The proposed, not-frozen mappings are:

| Candidate | ISCO-08 groups | Truthful interpretation |
| --- | --- | --- |
| Technology | 25 ICT professionals; 35 Information and communications technicians | ICT occupation stock |
| Science and engineering | 21 Science and engineering professionals; 31 Science and engineering associate professionals | Broad science-and-engineering occupation stock |
| Healthcare | 22 Health professionals; 32 Health associate professionals | Health occupation stock |
| Business and administration | 24 Business and administration professionals; 33 Business and administration associate professionals | Business-and-administration occupation stock |

Technology deliberately excludes managers, electrotechnology engineers, and installers outside
groups 25 and 35. Business and administration deliberately excludes an arbitrary mixture of
management, legal, sales, clerical, and marketing groups.

### Measure and scoring probe

Two dimensions are available from the compatible table:

1. occupation-family share of total employment, measuring specialization; and
2. log occupation-family employment, measuring ecosystem scale without allowing the largest
   countries to dominate linearly.

Working-age-population or labour-force normalization would require a second table and additional
source-period alignment. Current employee count alone is mechanically size-driven, while share
alone equates small specialized markets with large ecosystems. The diagnostic score therefore
tests an equal blend of percentile-ranked share and log scale.

The components are not duplicates: their Spearman correlations are 0.171 for technology, 0.241 for
science and engineering, 0.333 for healthcare, and 0.151 for business and administration. The
equal-blend score has standard deviation 2.22-2.39 on a 0-10 scale, so dispersion is meaningful.
This does not cure the coverage failure. Trend is not proposed because comparable multi-year
series cannot be guaranteed across classification and national-source breaks.

### Coverage

| Candidate | Any acceptable | Fresh valid | Stale | Invalid | Missing | Combined missing union | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Technology employment-market depth | 64 | 61 | 3 | 2 | 25 | 32 | `DIAGNOSTIC_ONLY` |
| Science and engineering employment-market depth | 68 | 66 | 2 | 0 | 23 | 30 | `DIAGNOSTIC_ONLY` |
| Healthcare employment-market depth | 68 | 66 | 2 | 0 | 23 | 30 | `DIAGNOSTIC_ONLY` |
| Business and administration employment-market depth | 68 | 66 | 2 | 0 | 23 | 30 | `DIAGNOSTIC_ONLY` |

Technology has two additional countries with only unreliable observations; they remain invalid and
are not included in "any acceptable." None reaches the 82-country PCC minimum. The exact latest
year, source, observation flags, and reason codes for every country are in
[`country-coverage.jsonl`](../../data/reports/phase6a-2026-07-30/country-coverage.jsonl).

## Workstream B: higher-education capacity

### Exact source and construct result

The retained official UIS asset is the February 2026
[`OPRI.zip`](https://download.uis.unesco.org/bdds/202602/OPRI.zip) archive, extracted by the
publisher on 2026-02-12. It provides:

- `FOSGP.5T8.F700`: percentage of tertiary graduates from ISCED 5-8 Engineering, manufacturing and
  construction programmes, both sexes; and
- `FOSGP.5T8.F600`: percentage of tertiary graduates from ISCED 5-8 Information and Communication
  Technologies programmes, both sexes.

These are graduate **shares**. The archive does not contain a compatible total-graduate count from
which field graduate counts can be reconstructed. It contains total tertiary enrolment indicator
`25053`, but multiplying graduate share by enrolment would mix different populations and produce a
false measure.

Consequently the source supports specialization, not capacity. It cannot construct engineering or
ICT graduates per relevant population, absolute graduate scale, or a truthful scale-and-share
blend. The observed share distributions are non-degenerate, but that is insufficient for
publication.

### Coverage

| Candidate | Any observation | Fresh valid | Stale | Missing | Combined missing union | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Engineering higher-education capacity | 84 | 76 | 8 | 7 | 16 | `HOLD_CRITICAL_BLOCKER` |
| ICT higher-education capacity | 84 | 75 | 9 | 7 | 17 | `HOLD_CRITICAL_BLOCKER` |

Both candidates fail the 82-country minimum at the 2021 freshness floor and fail the combined-union
limit. Even if coverage improved, they remain blocked until a compatible field count and total
count are available.

The archive README applies Creative Commons Attribution-ShareAlike 3.0 IGO. The current UIS site
terms state BY-SA 4.0. The exact archive notice controls this captured asset for this study. Raw
bytes remain ignored, and committing normalized derivatives requires owner/legal acceptance of
ShareAlike and a compatible repository licensing/attribution plan.

No criterion should imply admissions access, institutional quality, accreditation, or an
applicant's chance of acceptance.

## Workstream C: engineering academic and research ecosystem

The proposed primary OpenAlex mapping is field 22, Engineering. A sensitivity mapping would add
fields 15 Chemical Engineering, 21 Energy, and 25 Materials Science. Computer Science (17),
Chemistry (16), and Physics and Astronomy (31) are excluded from the primary mapping. This mapping
is not frozen because no exact taxonomy capture was retained.

A defensible future metric would use a recent five-year window, fractional field output, and active
institution breadth. Citation-normalized impact may be a sensitivity component, but raw citations
must not be the score.

The candidate is held for four independent reasons:

1. No pinned OpenAlex snapshot or deterministic paginated API capture was retained. The full
   snapshot is approximately 330 GB compressed and 1.6 TB decompressed; the API/CLI route needs a
   frozen query, key, response hashes, and timestamp.
2. ROR v2.10 is identified, but was not downloaded after the OpenAlex acquisition gate failed.
3. Current committed Konsider geographic entities do not contain the coordinates or boundaries
   needed for deterministic institution-coordinate-to-locality mapping. Retained GHSL geometry,
   point-in-polygon rules, multi-campus rules, conflict handling, and an unmapped-institution audit
   are prerequisites.
4. Without a capture and mapping, coverage, score dispersion, and correlation with active C05
   Research and innovation ecosystem cannot be measured.

OpenAlex documents its data as CC0, while current API service terms contain broader service-use
language requiring review for the selected acquisition route. ROR data are CC0, with GeoNames
location components requiring CC BY 4.0 attribution.

Decision: `HOLD_CRITICAL_BLOCKER`, with all 91 countries explicitly classified `rejected` for this
probe rather than inventing coverage.

## Source and legal evidence

| Exact asset | Frozen identity | Rights conclusion | Retention / normalized commit |
| --- | --- | --- | --- |
| ILOSTAT `EMP_TEMP_SEX_OC2_NB_A` | 19,708,182 bytes; SHA-256 `aaadd9ad52c88af5b00edce9c78821481d352251fe1ee944bb9bff299bdd04d4` | ILO aggregate data under CC BY 4.0; attribution required; restricted partner microdata excluded | Raw ignored; normalized derivative permitted with attribution |
| ILOSTAT guidelines PDF | 301,571 bytes; SHA-256 `aab6b086254c594cead72d0bf769783b01c80ef6723ba424de80452a642ad929` | Research evidence only | Raw ignored |
| UIS OPRI February 2026 | 68,300,100 bytes; SHA-256 `7e35482e817d63b0cf638fb695f8a9fd2df9139ae830c0d13f2eba4706d50eca` | Exact archive: CC BY-SA 3.0 IGO; attribution and ShareAlike | Raw ignored; normalized commit needs owner/legal review |
| UIS terms capture | 40,012 bytes; SHA-256 `91843e81e17ce6cf9f3a99022f7676a28290b6f0202c79c609a9e2a010af2f8d` | Site text says BY-SA 4.0; does not replace the archive's exact notice | Raw ignored |
| OpenAlex works/institutions/taxonomy | No frozen asset or checksum | Data documentation says CC0; selected API route still needs service-terms review | Blocked |
| [ROR v2.10](https://zenodo.org/records/21458494), 2026-07-20 | Identified release; 132,537 organizations; no local capture/checksum | CC0 plus GeoNames CC BY 4.0 attribution | Blocked pending capture and mapping |

The complete structured record, including URLs, access dates, publishers, distributors, third-party
restrictions, and commit conclusions, is
[`sources.json`](../../data/reports/phase6a-2026-07-30/sources.json).

## Decision matrix

| Candidate | Lineage | Valid estimate | Expected mode | Decision | Precise condition |
| --- | --- | ---: | --- | --- | --- |
| Technology employment-market depth | C12 | 61 | Diagnostic only | `DIAGNOSTIC_ONLY` | New official edition/source must reach policy without imputation |
| Science and engineering employment-market depth | C11 | 66 | Diagnostic only | `DIAGNOSTIC_ONLY` | Same; retain the renamed broad construct |
| Engineering higher-education capacity | C35 | 76 | Hold | `HOLD_CRITICAL_BLOCKER` | Compatible counts plus coverage and ShareAlike approval |
| Engineering academic and research ecosystem | C05 | 0 | Hold | `HOLD_CRITICAL_BLOCKER` | Pinned capture, legal review, locality mapping, coverage, and C05 overlap test |
| Healthcare employment-market depth | C13/C14 | 66 | Diagnostic only | `DIAGNOSTIC_ONLY` | New official edition/source must reach policy without imputation |
| Business and administration employment-market depth | C15-C17 | 66 | Diagnostic only | `DIAGNOSTIC_ONLY` | Same; do not relabel it business and finance |
| ICT higher-education capacity | C38 | 75 | Hold | `HOLD_CRITICAL_BLOCKER` | Compatible counts plus coverage and ShareAlike approval |

The full field-by-field matrix is
[`decision-matrix.json`](../../data/reports/phase6a-2026-07-30/decision-matrix.json).
The short implementation portfolio is
[`approved-implementation-portfolio.json`](../../data/reports/phase6a-2026-07-30/approved-implementation-portfolio.json).

## Reproducibility and verification

Run the exported `runPhase6A({ repoRoot })` function in
[`run_phase6a_probe.mjs`](../../project-history/phases/phase-6/research/run_phase6a_probe.mjs)
with the four retained raw captures present under ignored `data/raw/phase6a/`.

The replay:

- validates source byte counts and SHA-256 identities;
- rebuilds all seven coverage classifications from the retained captures or explicit blocked state;
- confirms 637 country-candidate rows: 91 countries times seven candidates;
- recomputes fresh coverage, current-PCC overlap unions, mappings, and score sensitivity;
- emits deterministic JSON/JSONL outputs; and
- records output checksums in
  [`replay-manifest.json`](../../data/reports/phase6a-2026-07-30/replay-manifest.json).

All proposed public names describe employment stock or education capacity. None says job
availability, promises employment, or implies admission or accreditation.

## Owner decisions

No decision is required to preserve the current product: stop Phase 6 before runtime work.

Resuming this portfolio would require one or more explicit owner actions:

1. authorize a search for a different official occupation or education source that clears the
   existing coverage gates;
2. accept and document UIS ShareAlike obligations before any normalized derivative is committed;
3. choose and resource the OpenAlex acquisition route, including storage/API-key policy and terms
   review; and
4. authorize a separate geography change that retains deterministic locality geometry and defines
   institution-to-locality mapping.

Lowering the 82-country PCC minimum, increasing the nine-country hard union limit, imputing missing
countries, or calling a share-only UIS measure "capacity" is not recommended.
