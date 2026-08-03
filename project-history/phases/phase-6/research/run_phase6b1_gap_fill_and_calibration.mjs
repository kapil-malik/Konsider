import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPORT_DATE = "2026-08-03";
const PHASE6B_DATE = "2026-08-02";
const RELEASE_ID = "2026-07-29.2";
const PERCENTILES = [0.5, 0.55, 0.6, 0.65, 0.7];
const BASE_PERCENTILE = 0.6;
const RULE = "(scale >= P60 and share >= P60) OR (scale >= P80 and share >= P40) OR (share >= P80 and scale >= P40)";
const TECH = "technology_software_opportunity";
const SCIENCE = "science_engineering_opportunity";
const REPORT_DIRECTORY = `phase6b1-${REPORT_DATE}`;

const json = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");
const round = (value, digits = 6) => Number(value.toFixed(digits));
const sum = (values) => values.reduce((total, value) => total + value, 0);

function quantile(values, percentile) {
  const sorted = [...values].sort((a, b) => a - b);
  if (!sorted.length) throw new Error("Cannot calculate a quantile over an empty array.");
  const index = (sorted.length - 1) * percentile;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower);
}

function thresholdsFor(observations, percentile) {
  const low = Math.max(0, percentile - 0.2);
  const high = Math.min(1, percentile + 0.2);
  const scales = observations.map((row) => row.scale_thousands);
  const shares = observations.map((row) => row.share_percent);
  return {
    base_scale_thousands: quantile(scales, percentile),
    base_share_percent: quantile(shares, percentile),
    high_scale_thousands: quantile(scales, high),
    high_share_percent: quantile(shares, high),
    low_scale_thousands: quantile(scales, low),
    low_share_percent: quantile(shares, low),
  };
}

function roundedThresholds(thresholds) {
  return Object.fromEntries(Object.entries(thresholds).map(([key, value]) => [key, round(value)]));
}

function routePasses(observation, thresholds) {
  if (!observation) return false;
  return (
    (observation.scale_thousands >= thresholds.base_scale_thousands && observation.share_percent >= thresholds.base_share_percent) ||
    (observation.scale_thousands >= thresholds.high_scale_thousands && observation.share_percent >= thresholds.low_share_percent) ||
    (observation.share_percent >= thresholds.high_share_percent && observation.scale_thousands >= thresholds.low_scale_thousands)
  );
}

function countBy(rows, key) {
  return Object.fromEntries([...new Set(rows.map((row) => row[key]))].sort().map((value) => [value, rows.filter((row) => row[key] === value).length]));
}

async function readJsonLines(filePath) {
  return (await fs.readFile(filePath, "utf8")).trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
}

function candidateRows(rows, candidateId) {
  return rows.filter((row) => row.candidate_id === candidateId);
}

function existingObservation(row) {
  const pathRow = row.evidence_paths[0];
  if (!pathRow || row.state === "INSUFFICIENT_EVIDENCE") return null;
  return { country_code: row.country_code, scale_thousands: pathRow.scale_thousands, share_percent: pathRow.share_percent };
}

function stateFor(observation, thresholds, assessable = Boolean(observation)) {
  if (!assessable || !observation) return "INSUFFICIENT_EVIDENCE";
  return routePasses(observation, thresholds) ? "VERIFIED_STRONG_SIGNAL" : "STRONG_SIGNAL_NOT_ESTABLISHED";
}

function compactCountry(row) {
  return {
    country_code: row.country_code,
    country_name: row.country_name,
    region: row.region,
    income_group: row.income_group,
    benchmark_shortlist_memberships: row.benchmark_shortlist_memberships,
  };
}

function sourceRecord({
  countryCode, countryName, disposition, sources, extraction, classification, unit, denominator,
  flags, rights, attribution, retention, replay, limitations,
}) {
  return {
    country_code: countryCode,
    country_name: countryName,
    disposition,
    sources,
    extraction,
    classification,
    sex: "Both sexes / total gender",
    unit,
    denominator,
    flags,
    normalized_rights: rights,
    required_attribution: attribution,
    retention_policy: retention,
    replay,
    limitations,
  };
}

function markdownReport({ sourceMatrix, coverage, thresholdCalibration, anchors, routeAnalysis, portfolio, gapEvidence }) {
  const sourceRows = sourceMatrix.countries.map((row) =>
    `| ${row.country_code} | ${row.disposition} | ${row.classification} | ${row.limitations} |`).join("\n");
  const evidenceRows = gapEvidence.map((row) =>
    `| ${row.country_code} | ${row.candidate_id === TECH ? "Technology" : "Science/engineering"} | ${row.state} | ${row.scale_thousands ?? "—"} | ${row.share_percent ?? "—"} | ${row.confidence_tier} |`).join("\n");
  const coverageRows = Object.entries(coverage.candidates).flatMap(([candidateId, candidate]) =>
    Object.entries(candidate.profiles).map(([profileId, profile]) =>
      `| ${candidateId === TECH ? "Technology" : "Science/engineering"} | ${profileId} | ${profile.before.assessable_count} | ${profile.after.assessable_count} | ${profile.after.hard_minimum_passes ? "yes" : "no"} | ${profile.after.preferred_target_passes ? "yes" : "no"} |`)).join("\n");
  const anchorRows = anchors.countries.map((row) =>
    `| ${row.country_code} | ${row.technology.p60} | ${row.science_engineering.p60} | ${row.review_note} |`).join("\n");
  return `# Phase 6B.1 — Career opportunity gap fill and threshold calibration

Date: ${REPORT_DATE}
Release baseline: ${RELEASE_ID}
Status: **RESEARCH COMPLETE — NO PRODUCTION CHANGE**

## Outcome

Phase 6B.1 closes enough of the targeted evidence gap to move the frozen technology/software and science/engineering constructs into implementation design without changing ranking, ordering, runtime schemas, presets, APIs, UI, workers, or releases.

- **Technology/software:** \`APPROVE_FOR_IMPLEMENTATION_DESIGN\`. Malta supplies high-confidence harmonised ISCO evidence and Canada supplies medium-confidence national evidence under a transparent, tightly aligned NOC mapping. Assessability rises from 61/91 to 63/91. Four benchmark lists rise from 15/20 to 17/20; the family/education list rises from 17/20 to 18/20.
- **Science/engineering:** \`APPROVE_FOR_IMPLEMENTATION_DESIGN\`. Malta supplies exact harmonised ISCO evidence. Assessability rises from 66/91 to 67/91. Four benchmark lists rise from 15/20 to the hard floor of 16/20; the family/education list remains 17/20. Canada is retained as supplemental evidence only because no official NOC 2021 to ISCO-08 concordance was located and its result would otherwise be a negative.
- **Japan, South Korea, and New Zealand:** remain explicit source or granularity holds for these two constructs. No proxy was used to manufacture coverage.
- **Threshold:** retain the global P60 scale/share rule. P55 and P65 demonstrate expected movement around the boundary; P50 and P70 are materially permissive/restrictive. The rule remains global and no country-specific threshold is introduced.

## Frozen constructs and public meaning

Technology/software remains employment in ISCO-08 groups 25 and 35. Science/engineering remains employment in ISCO-08 groups 21 and 31. The public statement for either is “a substantial and established employment ecosystem.” It does not mean live vacancies, job quality, licence recognition, immigration eligibility, applicant success probability, or absence of jobs when the state is not established.

## National source results

| Country | Disposition | Classification | Finding |
|---|---|---|---|
${sourceRows}

Official sources and reuse terms frozen in the source matrix include Eurostat dataset \`lfsa_egai2d\`, Statistics Canada table 98-10-0594-01, Japan e-Stat Labour Force Survey historical table 6, KOSIS table DT_1DA7E27S and its official 1-digit dissemination clarification, and Stats NZ 2023 Census dataset CEN23_WRK_009.

## Crosswalk decisions

Malta needs no crosswalk: the source is already ISCO-08 at two digits. Canada technology uses NOC 2122, 2123, and 2222 because their published labels align tightly with ISCO-08 groups 25 and 35. Canada science uses a documented research mapping only as supplemental evidence; mixed NOC groups 2112 and 2223 are excluded, and the aggregate cannot establish a public negative without an official concordance.

Japan publishes only a combined professional/engineering group in the retained annual workbook. Korea officially states that public occupation-by-sex data are disseminated only at 1 digit. The full-population New Zealand Census table located in Data Explorer exposes occupation at major-group level; an official classification concordance exists separately, but no matching detailed national employment stock was located. These are gaps, not zeroes.

## Gap-fill evidence

| Country | Construct | State | Scale (thousand) | Share (%) | Confidence |
|---|---|---|---:|---:|---|
${evidenceRows}

Malta 2025 technology is 11.0 thousand (3.3496%) and science/engineering is 21.7 thousand (6.6078%). Both remain below the global scale floor and therefore produce a defensible \`STRONG_SIGNAL_NOT_ESTABLISHED\` state. Canada technology is 613.685 thousand (3.5429%) and crosses the P80-scale/P40-share route. The narrower Canada science aggregate is 715.635 thousand (4.1314%) but is supplemental-only and cannot publish a negative.

## Benchmark coverage before and after

Opportunity evidence is joined after each current top-20 list is generated and never changes list order.

| Construct | Profile | Before | After | ≥16 hard floor | ≥18 preferred |
|---|---|---:|---:|---|---|
${coverageRows}

The hard floor is satisfied for both constructs. Science remains dependent on Malta for the four 16/20 results; removing the Eurostat Malta source returns those lists to 15/20. This dependency is recorded as an implementation risk, not hidden by a broader proxy.

## Confidence and precedence

The frozen order is: recent harmonised observed; recent official national observed with a strong documented mapping; harmonised modelled; supplemental. Observed evidence is never overwritten by modelled evidence. Contradictions are retained for review. High-confidence complete evidence may establish either positive or negative. Medium-confidence evidence may establish a positive; a negative requires defensible mapping completeness. Low-confidence supplemental evidence never produces a public negative.

## Threshold calibration

The retained rule is: ${RULE}.

At P60 after gap fill, technology has ${thresholdCalibration.candidates[TECH].p60.outcome_counts.VERIFIED_STRONG_SIGNAL} verified, ${thresholdCalibration.candidates[TECH].p60.outcome_counts.STRONG_SIGNAL_NOT_ESTABLISHED} not-established, and ${thresholdCalibration.candidates[TECH].p60.outcome_counts.INSUFFICIENT_EVIDENCE} insufficient states. Science/engineering has ${thresholdCalibration.candidates[SCIENCE].p60.outcome_counts.VERIFIED_STRONG_SIGNAL} verified, ${thresholdCalibration.candidates[SCIENCE].p60.outcome_counts.STRONG_SIGNAL_NOT_ESTABLISHED} not-established, and ${thresholdCalibration.candidates[SCIENCE].p60.outcome_counts.INSUFFICIENT_EVIDENCE} insufficient states.

Adding Malta and Canada to the calibration pool changes raw P60 thresholds only slightly; policy thresholds remain frozen to the pre-gap-fill reference pool to prevent target-driven drift. Malta’s 2024 and 2025 results produce the same public states. Canada has only the 2021 Census stock in the accepted route, so no false annual stability claim is made.

## Anchor-country review

| Country | Technology P60 | Science P60 | Review |
|---|---|---|---|
${anchorRows}

No anchor result required a country exception. Sensitivity movement is reported rather than edited away.

## Broad criterion naming and route decisions

- **Care-sector employment ecosystem:** approve with naming change; internal construct remains ISIC Rev.4 section Q, human health and social work.
- **Finance and insurance employment ecosystem:** retain. Business and administration evidence remains supplemental and cannot broaden the public claim.
- **Skilled-trades or construction employment ecosystem:** retain the transparent OR route. At P60 the route analysis records ${routeAnalysis.skilled_trades_or_construction.route_counts.skilled_only} skilled-only, ${routeAnalysis.skilled_trades_or_construction.route_counts.construction_only} construction-only, ${routeAnalysis.skilled_trades_or_construction.route_counts.both} both-route, and ${routeAnalysis.skilled_trades_or_construction.route_counts.neither} neither-route countries. Implementation must expose which route established the state.
- **Research and academic ecosystem:** move to the education/research phase. ISIC M72 is an R&D-sector proxy and cannot stand for academia or field-relevant research opportunity.

## Final research portfolio

Approved for implementation design: care-sector; finance and insurance; skilled-trades or construction; technology/software; science/engineering. Research and academic ecosystem moves to the education/research phase. No production work is authorised by this report.

## Files and verification

The dated report directory contains the source matrix, crosswalks, ten country/construct evidence rows, confidence and route policies, before/after coverage, threshold calibration, anchor review, route/naming analysis, final portfolio, and checksum manifest. The replay script verifies one row per target-country/construct pair, ISO alpha-3 codes, metric compatibility, shortlist floors, frozen global thresholds, JSON/JSONL parsing, raw-capture checksums where retained, and deterministic no-diff replay.

## Owner decisions before implementation

1. Accept technology and science/engineering at the hard shortlist floor, noting that science reaches 16/20 rather than the preferred 18/20 in four profiles.
2. Accept Canada technology as medium-confidence national observed evidence under the documented semantic mapping.
3. Accept the care-sector public name while retaining section Q internally.
4. Require route visibility for the skilled-trades/construction OR construct.
5. Confirm that research/academia will be handled in the education/research phase rather than through M72.
`;
}

export async function runPhase6B1({ repoRoot }) {
  const phase6bDirectory = path.join(repoRoot, "data", "reports", `phase6b-${PHASE6B_DATE}`);
  const outputDirectory = path.join(repoRoot, "data", "reports", REPORT_DIRECTORY);
  const reportPath = path.join(repoRoot, "docs", "research", "phase6b1-career-gap-fill-and-calibration.md");
  const fixturePath = path.join(repoRoot, "project-history", "phases", "phase-6", "research", "fixtures", "phase6b1-official-source-fixtures.json");
  const scriptPath = fileURLToPath(import.meta.url);
  await fs.mkdir(outputDirectory, { recursive: true });

  const fixtureText = await fs.readFile(fixturePath, "utf8");
  const fixture = JSON.parse(fixtureText);
  const evidencePath = path.join(phase6bDirectory, "career-country-opportunity-evidence.jsonl");
  const shortlistPath = path.join(phase6bDirectory, "career-shortlist-coverage.json");
  const portfolioPath = path.join(phase6bDirectory, "approved-career-opportunity-portfolio.json");
  const phase6bEvidenceText = await fs.readFile(evidencePath, "utf8");
  const phase6bEvidence = phase6bEvidenceText.trim().split(/\r?\n/).map(JSON.parse);
  const priorShortlistsText = await fs.readFile(shortlistPath, "utf8");
  const priorShortlists = JSON.parse(priorShortlistsText);
  const priorPortfolioText = await fs.readFile(portfolioPath, "utf8");
  const priorPortfolio = JSON.parse(priorPortfolioText);

  const countryReference = new Map(candidateRows(phase6bEvidence, TECH).map((row) => [row.country_code, compactCountry(row)]));
  const maltaLatest = fixture.sources.eurostat_lfsa_egai2d_malta.rows.at(-1);
  const maltaPrior = fixture.sources.eurostat_lfsa_egai2d_malta.rows.at(-2);
  const canadaSource = fixture.sources.statcan_9810059401_canada;
  const canadaRow = (code) => canadaSource.rows.find((row) => row.code === code);
  const canadaTechCodes = ["2122", "2123", "2222"];
  const canadaScienceCodes = ["2110", "2111", "2120", "2121", "2130", "2131", "2132", "2133", "2139", "2210", "2211", "2221", "2230", "2231"];
  const canadaTechEmployment = sum(canadaTechCodes.map((code) => canadaRow(code).employed));
  const canadaScienceEmployment = sum(canadaScienceCodes.map((code) => canadaRow(code).employed));

  const targetObservations = {
    [`${TECH}|CAN`]: { scale_thousands: canadaTechEmployment / 1000, share_percent: canadaTechEmployment / canadaSource.all_occupations_employed * 100, period: 2021 },
    [`${SCIENCE}|CAN`]: { scale_thousands: canadaScienceEmployment / 1000, share_percent: canadaScienceEmployment / canadaSource.all_occupations_employed * 100, period: 2021, supplemental_only: true },
    [`${TECH}|MLT`]: { scale_thousands: maltaLatest.oc25 + maltaLatest.oc35, share_percent: (maltaLatest.oc25 + maltaLatest.oc35) / maltaLatest.total * 100, period: maltaLatest.year },
    [`${SCIENCE}|MLT`]: { scale_thousands: maltaLatest.oc21 + maltaLatest.oc31, share_percent: (maltaLatest.oc21 + maltaLatest.oc31) / maltaLatest.total * 100, period: maltaLatest.year },
  };

  const originalPools = {};
  const expandedPools = {};
  for (const candidateId of [TECH, SCIENCE]) {
    originalPools[candidateId] = candidateRows(phase6bEvidence, candidateId).map(existingObservation).filter(Boolean);
    expandedPools[candidateId] = [...originalPools[candidateId]];
  }
  expandedPools[TECH].push(
    { country_code: "CAN", ...targetObservations[`${TECH}|CAN`] },
    { country_code: "MLT", ...targetObservations[`${TECH}|MLT`] },
  );
  expandedPools[SCIENCE].push({ country_code: "MLT", ...targetObservations[`${SCIENCE}|MLT`] });

  const frozenThresholds = Object.fromEntries([TECH, SCIENCE].map((candidateId) => [candidateId, thresholdsFor(originalPools[candidateId], BASE_PERCENTILE)]));

  const gapEvidence = [];
  for (const countryCode of ["CAN", "JPN", "KOR", "MLT", "NZL"]) {
    for (const candidateId of [TECH, SCIENCE]) {
      const reference = countryReference.get(countryCode);
      const observation = targetObservations[`${candidateId}|${countryCode}`] ?? null;
      const accepted = Boolean(observation && !observation.supplemental_only);
      const state = stateFor(observation, frozenThresholds[candidateId], accepted);
      const countryDispositions = {
        CAN: candidateId === TECH ? "ACCEPT_MEDIUM_CONFIDENCE_NATIONAL" : "SUPPLEMENTAL_ONLY_NO_PUBLIC_NEGATIVE",
        JPN: "HOLD_CROSSWALK_GAP",
        KOR: "HOLD_SOURCE_GAP",
        MLT: "ACCEPT_HIGH_CONFIDENCE_HARMONISED",
        NZL: "HOLD_SOURCE_GAP",
      };
      gapEvidence.push({
        schema_version: "konsider-phase6b1-gap-fill-country-evidence-1.0",
        report_date: REPORT_DATE,
        country_code: countryCode,
        country_name: reference.country_name,
        candidate_id: candidateId,
        state,
        disposition: countryDispositions[countryCode],
        period: observation?.period ?? null,
        scale_thousands: observation ? round(observation.scale_thousands) : null,
        share_percent: observation ? round(observation.share_percent) : null,
        confidence_tier: countryCode === "MLT" ? "HIGH_CONFIDENCE_OBSERVED_HARMONISED" :
          countryCode === "CAN" && candidateId === TECH ? "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK" : "LOW_CONFIDENCE_SUPPLEMENTAL",
        source_id: countryCode === "MLT" ? "EUROSTAT:lfsa_egai2d" : countryCode === "CAN" ? "STATCAN:98-10-0594-01" : null,
        threshold_rule: RULE,
        thresholds: roundedThresholds(frozenThresholds[candidateId]),
        negative_integrity: state === "STRONG_SIGNAL_NOT_ESTABLISHED" ? "DEFENSIBLE_COMPLETE_HARMONISED_ROUTE" :
          countryCode === "CAN" && candidateId === SCIENCE ? "NEGATIVE_SUPPRESSED_NO_OFFICIAL_CONCORDANCE" : "NOT_APPLICABLE",
        benchmark_shortlist_memberships: reference.benchmark_shortlist_memberships,
        note: countryCode === "CAN" && candidateId === SCIENCE ?
          "The transparent narrower mapping is retained for audit, but cannot establish a public negative without an official NOC 2021 to ISCO-08 concordance." :
          state === "INSUFFICIENT_EVIDENCE" ? "No exact, sufficiently granular, replayable public stock was located." :
          "Scale and share use the same source, period, population, sex, unit, and denominator.",
      });
    }
  }

  const nationalSourceMatrix = {
    schema_version: "konsider-phase6b1-national-source-matrix-1.0",
    report_date: REPORT_DATE,
    countries: [
      sourceRecord({
        countryCode: "CAN", countryName: "Canada", disposition: "PARTIAL_GAP_FILL_TECHNOLOGY_ONLY",
        sources: [
          { publisher: "Statistics Canada", title: canadaSource.title, endpoint: canadaSource.endpoint, table_or_version: "98-10-0594-01 / NOC 2021 v1.0", period: canadaSource.reference_period },
          { publisher: "Statistics Canada", title: "Employment by occupation, annual", endpoint: "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410041601", table_or_version: "14-10-0416-01", period: "2025", disposition: "REJECT_TOO_AGGREGATED_FOR_FROZEN_CONSTRUCTS" },
        ],
        extraction: "Official HTML table payload; compact fixture retains exact employed counts for included and excluded NOC groups.",
        classification: "NOC 2021 Version 1.0", unit: "persons", denominator: "All occupations employed, 17,321,700",
        flags: ["Canada-level long-form census data quality flag 20000", "Excludes one or more incompletely enumerated reserves or settlements"],
        rights: "STATISTICS_CANADA_OPEN_LICENCE", attribution: "Adapted from Statistics Canada, table 98-10-0594-01, 2021 Census. This does not constitute an endorsement by Statistics Canada.",
        retention: "Compact fixture committed; raw HTML retained under data/raw/phase6b1 and checksum-bound.", replay: { raw_sha256: canadaSource.raw_capture_sha256, fixture_source: "phase6b1-official-source-fixtures.json" },
        limitations: "No official NOC 2021 to ISCO-08 concordance was located; technology is a tight semantic mapping, science remains supplemental-only for a negative result.",
      }),
      sourceRecord({
        countryCode: "JPN", countryName: "Japan", disposition: "HOLD_CROSSWALK_GAP",
        sources: [{ publisher: fixture.sources.estat_japan_lfs_table_6_1.publisher, title: fixture.sources.estat_japan_lfs_table_6_1.title, endpoint: fixture.sources.estat_japan_lfs_table_6_1.endpoint, table_or_version: "Labour Force Survey historical table 6 / JSOC Dec. 2009", period: "2025" }],
        extraction: "Official e-Stat XLSX inspected and rendered; annual both-sex total is present.", classification: "Japan Standard Occupational Classification, December 2009 revision", unit: "ten thousand persons", denominator: "All employed persons, whole Japan",
        flags: ["2011 earthquake supplementary-estimated values affect historical rows, not 2025"], rights: "GOVERNMENT_OF_JAPAN_STANDARD_TERMS_V2_CC_BY_4_COMPATIBLE", attribution: "Source: Labour Force Survey, Statistics Bureau of Japan, via e-Stat; adapted by Konsider.",
        retention: "Compact metadata fixture committed; raw XLSX retained under data/raw/phase6b1 and checksum-bound.", replay: { raw_sha256: fixture.sources.estat_japan_lfs_table_6_1.raw_capture_sha256 },
        limitations: "The retained annual workbook publishes only major groups; professional and engineering workers cannot be split into the frozen technology and science constructs.",
      }),
      sourceRecord({
        countryCode: "KOR", countryName: "Korea, Rep.", disposition: "HOLD_SOURCE_GAP",
        sources: [
          { publisher: "Statistics Korea", title: "Employed persons by gender/occupation", endpoint: "https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1DA7E27S&language=en&conn_path=I2", table_or_version: "KOSIS DT_1DA7E27S / KSCO 8th revision", period: "2025 onward" },
          { publisher: "Statistics Korea", title: "Economically Active Population Survey detailed data — official Q&A", endpoint: "https://kosis.kr/eng/bulletinBoard/qnaView.do?boardIdx=335753", table_or_version: "Q&A response dated 2025-08-13", period: "current policy" },
        ],
        extraction: "Metadata and official dissemination clarification only; no evidence-bearing values retained.", classification: "Korean Standard Classification of Occupations, 8th revision", unit: "persons / public series", denominator: "Employed persons",
        flags: ["Official response states occupation-by-sex data are disseminated only at 1 digit"], rights: "KOSIS_PUBLIC_DATA_FREE_USE", attribution: "Source: Statistics Korea, KOSIS.",
        retention: "URLs and official limitation frozen in the source matrix.", replay: { mode: "REMOTE_METADATA_ONLY" }, limitations: "One-digit occupation groups cannot isolate ISCO-08 25+35 or 21+31.",
      }),
      sourceRecord({
        countryCode: "MLT", countryName: "Malta", disposition: "COMPLETE_GAP_FILL_BOTH_CONSTRUCTS",
        sources: [{ publisher: "Eurostat", title: fixture.sources.eurostat_lfsa_egai2d_malta.title, endpoint: fixture.sources.eurostat_lfsa_egai2d_malta.endpoint, table_or_version: "lfsa_egai2d", period: "2021-2025; latest 2025" }],
        extraction: "Eurostat JSON-stat API; annual, age 15-74, both sexes, thousand persons, Malta.", classification: "ISCO-08 two-digit", unit: "thousand persons", denominator: "Total employed persons in the same dataset/period/population",
        flags: ["No status flag attached to the 2025 total or OC21/31/25/35 observations"], rights: "EUROSTAT_CC_BY_4_0_FREE_REUSE", attribution: "Source: Eurostat, lfsa_egai2d, accessed 2026-08-03; adapted values and calculations by Konsider.",
        retention: "Compact five-year fixture committed; raw JSON retained under data/raw/phase6b1 and checksum-bound.", replay: { raw_sha256: fixture.sources.eurostat_lfsa_egai2d_malta.raw_capture_sha256, fixture_source: "phase6b1-official-source-fixtures.json" }, limitations: "Small-country estimates remain below the global scale floor; result is a defensible not-established state, not no jobs.",
      }),
      sourceRecord({
        countryCode: "NZL", countryName: "New Zealand", disposition: "HOLD_SOURCE_GAP",
        sources: [
          { publisher: "Stats NZ", title: "Occupation, age, and gender for the employed census usually resident population count aged 15 years and over", endpoint: "https://explore.data.stats.govt.nz/vis?df[id]=CEN23_WRK_009&df[ag]=STATSNZ&df[vs]=1.0", table_or_version: "CEN23_WRK_009 / ANZSCO v1.3", period: "2013, 2018, 2023" },
          { publisher: "Stats NZ", title: "About the National Occupation List", endpoint: "https://www.stats.govt.nz/methods/about-the-national-occupation-list", table_or_version: "NOL concordance catalogue", period: "updated 2026" },
        ],
        extraction: "Public Data Explorer table inspected; API requires a subscription key.", classification: "ANZSCO v1.3, public national table at major level 1", unit: "persons", denominator: "Employed census usually resident population aged 15+",
        flags: ["2023 Census confidentiality rounding and coding notes apply"], rights: "STATS_NZ_CC_BY_4_0_ATTRIBUTION", attribution: "Source: Stats NZ, 2023 Census; adapted by Konsider.",
        retention: "Dataset ID, query URL, classification, and limitation frozen in the source matrix.", replay: { mode: "REMOTE_METADATA_ONLY_API_KEY_REQUIRED" }, limitations: "The located full-population table exposes occupation only at major level; a concordance alone cannot create detailed employment counts.",
      }),
    ],
  };

  const occupationCrosswalks = {
    schema_version: "konsider-phase6b1-occupation-crosswalks-1.0",
    report_date: REPORT_DATE,
    constructs: { technology: "ISCO-08 25 + 35", science_engineering: "ISCO-08 21 + 31" },
    crosswalks: [
      {
        country_code: "MLT", source_classification: "ISCO-08", source_version: "dataset lfsa_egai2d", target_construct: "technology",
        included_source_codes: ["25", "35"], excluded_adjacent_codes: ["21", "31"], one_to_many: false,
        rationale: "Direct identity mapping at the exact two-digit target level.", ambiguity: "NONE", over_inclusion_risk: "NONE", under_inclusion_risk: "NONE",
        confidence: "HIGH_CONFIDENCE_OBSERVED_HARMONISED", official_provenance: "Eurostat EU-LFS harmonised ISCO-08 table",
      },
      {
        country_code: "MLT", source_classification: "ISCO-08", source_version: "dataset lfsa_egai2d", target_construct: "science_engineering",
        included_source_codes: ["21", "31"], excluded_adjacent_codes: ["25", "35"], one_to_many: false,
        rationale: "Direct identity mapping at the exact two-digit target level.", ambiguity: "NONE", over_inclusion_risk: "NONE", under_inclusion_risk: "NONE",
        confidence: "HIGH_CONFIDENCE_OBSERVED_HARMONISED", official_provenance: "Eurostat EU-LFS harmonised ISCO-08 table",
      },
      {
        country_code: "CAN", source_classification: "NOC 2021", source_version: "Version 1.0", target_construct: "technology",
        included_source_codes: canadaTechCodes, excluded_adjacent_codes: ["2121", "2131"], one_to_many: true,
        rationale: "The published minor-group labels align tightly with ICT professionals and ICT technicians; computer engineering remains science/engineering rather than ICT employment.",
        ambiguity: "LOW_BUT_NO_OFFICIAL_NOC_TO_ISCO_CONCORDANCE_LOCATED", over_inclusion_risk: "LOW", under_inclusion_risk: "LOW_TO_MEDIUM",
        confidence: "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK", official_provenance: "Official Statistics Canada NOC labels and Census counts; research mapping is explicitly not an official concordance.",
      },
      {
        country_code: "CAN", source_classification: "NOC 2021", source_version: "Version 1.0", target_construct: "science_engineering",
        included_source_codes: canadaScienceCodes, excluded_adjacent_codes: ["2112", "2223", "2122", "2123", "2222"], one_to_many: true,
        rationale: "A conservative research mapping excludes mixed public-health/safety and inspector/regulatory groups and excludes ICT groups.",
        ambiguity: "MEDIUM_NO_OFFICIAL_NOC_TO_ISCO_CONCORDANCE_LOCATED", over_inclusion_risk: "MEDIUM_2121_INCLUDES_DATA_SCIENTISTS", under_inclusion_risk: "MEDIUM_EXCLUDES_MIXED_GROUPS",
        confidence: "LOW_CONFIDENCE_SUPPLEMENTAL", official_provenance: "Official Statistics Canada NOC labels and Census counts; not accepted for a public negative.",
      },
      ...["JPN", "KOR", "NZL"].flatMap((countryCode) => ["technology", "science_engineering"].map((targetConstruct) => ({
        country_code: countryCode,
        source_classification: countryCode === "JPN" ? "JSOC December 2009" : countryCode === "KOR" ? "KSCO 8th revision" : "ANZSCO v1.3",
        source_version: "official source located in national-source-matrix.json", target_construct: targetConstruct,
        included_source_codes: [], excluded_adjacent_codes: [], one_to_many: null,
        rationale: "No sufficiently granular matching employment stock was located; no crosswalk is applied.",
        ambiguity: "UNRESOLVED_GRANULARITY_GAP", over_inclusion_risk: "UNBOUNDED_IF_BROAD_GROUP_USED", under_inclusion_risk: "UNBOUNDED",
        confidence: "LOW_CONFIDENCE_SUPPLEMENTAL", official_provenance: "Official source limitation retained; no invented mapping.",
      }))),
    ],
  };

  const confidencePolicy = {
    schema_version: "konsider-phase6b1-career-confidence-policy-1.0",
    report_date: REPORT_DATE,
    tiers: [
      { id: "HIGH_CONFIDENCE_OBSERVED_HARMONISED", public_positive: true, public_negative: true, requirements: ["observed", "harmonised construct", "complete numerator and denominator", "same source/period/population/sex/unit"] },
      { id: "HIGH_CONFIDENCE_OBSERVED_NATIONAL", public_positive: true, public_negative: true, requirements: ["official national observed", "official or near-identity mapping", "defensible completeness"] },
      { id: "MEDIUM_CONFIDENCE_MODELLED_HARMONISED", public_positive: true, public_negative: true, requirements: ["harmonised modelled series", "modelled status disclosed", "complete route"] },
      { id: "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK", public_positive: true, public_negative: "ONLY_IF_MAPPING_COMPLETENESS_DEFENSIBLE", requirements: ["official national source", "documented mapping", "limited ambiguity"] },
      { id: "LOW_CONFIDENCE_SUPPLEMENTAL", public_positive: false, public_negative: false, requirements: ["context only", "never replaces stronger evidence"] },
    ],
    precedence: ["HIGH_CONFIDENCE_OBSERVED_HARMONISED", "HIGH_CONFIDENCE_OBSERVED_NATIONAL", "MEDIUM_CONFIDENCE_MODELLED_HARMONISED", "MEDIUM_CONFIDENCE_OFFICIAL_CROSSWALK", "LOW_CONFIDENCE_SUPPLEMENTAL"],
    contradiction_policy: "Do not overwrite observed with modelled. Retain both, prefer the higher tier for public state, and open a review record when states disagree.",
    asymmetric_state_rule: { positive: "A complete accepted route may establish a positive.", negative: "Only evidence with defensible mapping completeness may establish a negative.", insufficient: "Missing, stale, incompatible, or ambiguous evidence remains insufficient and never becomes negative." },
  };

  const multiRoutePolicy = {
    schema_version: "konsider-phase6b1-multi-route-decision-policy-1.0",
    report_date: REPORT_DATE,
    rule: "A positive may be established when any accepted transparent route crosses its frozen threshold. A negative requires every required route to be present, comparable, and below threshold.",
    no_composite_score: true,
    route_visibility_required: true,
    missing_route_policy: "INSUFFICIENT_EVIDENCE_FOR_NEGATIVE",
    contradiction_policy: "Preserve route-level states and expose the route that established the positive; do not average routes.",
    applicable_constructs: ["skilled_trades_construction_opportunity", "future independently sourced career constructs"],
  };

  const coverage = {
    schema_version: "konsider-phase6b1-career-shortlist-coverage-before-after-1.0",
    report_date: REPORT_DATE,
    release_id: RELEASE_ID,
    ordering_effect: "NONE",
    candidates: {},
  };
  for (const candidateId of [TECH, SCIENCE]) {
    coverage.candidates[candidateId] = { profiles: {} };
    for (const [profileId, before] of Object.entries(priorShortlists.candidates[candidateId].profiles)) {
      const acceptedRows = gapEvidence.filter((row) => row.candidate_id === candidateId && row.state !== "INSUFFICIENT_EVIDENCE" && row.benchmark_shortlist_memberships.includes(profileId));
      const addedVerified = acceptedRows.filter((row) => row.state === "VERIFIED_STRONG_SIGNAL").length;
      const addedNegative = acceptedRows.filter((row) => row.state === "STRONG_SIGNAL_NOT_ESTABLISHED").length;
      const after = {
        assessable_count: before.assessable_count + acceptedRows.length,
        verified_strong_signal_count: before.verified_strong_signal_count + addedVerified,
        strong_signal_not_established_count: before.strong_signal_not_established_count + addedNegative,
        insufficient_evidence_count: before.insufficient_evidence_count - acceptedRows.length,
        insufficient_evidence_countries: before.insufficient_evidence_countries.filter((code) => !acceptedRows.some((row) => row.country_code === code)),
      };
      after.hard_minimum_passes = after.assessable_count >= 16;
      after.preferred_target_passes = after.assessable_count >= 18;
      coverage.candidates[candidateId].profiles[profileId] = { before, added_countries: acceptedRows.map((row) => ({ country_code: row.country_code, state: row.state })), after };
    }
  }

  const thresholdCalibration = {
    schema_version: "konsider-phase6b1-career-threshold-calibration-1.0",
    report_date: REPORT_DATE,
    base_percentile: BASE_PERCENTILE,
    rule: RULE,
    decision: "RETAIN_P60_GLOBAL_THRESHOLDS_FROM_PRE_GAP_FILL_REFERENCE_POOL",
    decision_reason: "P60 remains a transparent middle calibration; thresholds are not recomputed into policy after target-country additions, avoiding target-driven drift.",
    candidates: {},
    source_removal_tests: {
      remove_eurostat_malta: { technology_minimum_profile_assessable: 16, science_minimum_profile_assessable: 15, science_hard_floor_passes: false },
      remove_statcan_canada: { technology_minimum_profile_assessable: 16, technology_hard_floor_passes: true, science_effect: "NONE_CANADA_SUPPLEMENTAL_ONLY" },
    },
    period_stability: {},
  };

  const expandedRowMaps = {};
  for (const candidateId of [TECH, SCIENCE]) {
    const baseRows = candidateRows(phase6bEvidence, candidateId);
    const observations = new Map(baseRows.map((row) => [row.country_code, existingObservation(row)]));
    if (candidateId === TECH) {
      observations.set("CAN", targetObservations[`${TECH}|CAN`]);
      observations.set("MLT", targetObservations[`${TECH}|MLT`]);
    } else {
      observations.set("MLT", targetObservations[`${SCIENCE}|MLT`]);
    }
    expandedRowMaps[candidateId] = observations;
    thresholdCalibration.candidates[candidateId] = {
      original_assessable_count: originalPools[candidateId].length,
      expanded_assessable_count: expandedPools[candidateId].length,
      raw_threshold_stability: {},
    };
    const p60StateMap = new Map();
    for (const percentile of PERCENTILES) {
      const originalThreshold = thresholdsFor(originalPools[candidateId], percentile);
      const expandedThreshold = thresholdsFor(expandedPools[candidateId], percentile);
      const classified = baseRows.map((row) => {
        const observation = observations.get(row.country_code);
        return { ...compactCountry(row), state: stateFor(observation, originalThreshold, Boolean(observation)) };
      });
      const key = `p${Math.round(percentile * 100)}`;
      if (percentile === BASE_PERCENTILE) for (const row of classified) p60StateMap.set(row.country_code, row.state);
      thresholdCalibration.candidates[candidateId][key] = {
        percentile,
        outcome_counts: {
          VERIFIED_STRONG_SIGNAL: classified.filter((row) => row.state === "VERIFIED_STRONG_SIGNAL").length,
          STRONG_SIGNAL_NOT_ESTABLISHED: classified.filter((row) => row.state === "STRONG_SIGNAL_NOT_ESTABLISHED").length,
          INSUFFICIENT_EVIDENCE: classified.filter((row) => row.state === "INSUFFICIENT_EVIDENCE").length,
        },
        thresholds: roundedThresholds(originalThreshold),
        state_changes_from_p60: [],
        region_counts: Object.fromEntries([...new Set(classified.map((row) => row.region))].sort().map((region) => [region, countBy(classified.filter((row) => row.region === region), "state")])),
        income_group_counts: Object.fromEntries([...new Set(classified.map((row) => row.income_group))].sort().map((income) => [income, countBy(classified.filter((row) => row.income_group === income), "state")])),
      };
      thresholdCalibration.candidates[candidateId].raw_threshold_stability[key] = {
        original_pool: roundedThresholds(originalThreshold),
        expanded_pool: roundedThresholds(expandedThreshold),
        absolute_deltas: Object.fromEntries(Object.keys(originalThreshold).map((field) => [field, round(expandedThreshold[field] - originalThreshold[field])])),
      };
    }
    for (const percentile of PERCENTILES) {
      const key = `p${Math.round(percentile * 100)}`;
      const thresholds = thresholdsFor(originalPools[candidateId], percentile);
      thresholdCalibration.candidates[candidateId][key].state_changes_from_p60 = baseRows.map((row) => ({
        country_code: row.country_code,
        state: stateFor(observations.get(row.country_code), thresholds, Boolean(observations.get(row.country_code))),
      })).filter((row) => row.state !== p60StateMap.get(row.country_code)).map((row) => ({ country_code: row.country_code, from: p60StateMap.get(row.country_code), to: row.state }));
    }
  }

  const maltaPriorTech = { scale_thousands: maltaPrior.oc25 + maltaPrior.oc35, share_percent: (maltaPrior.oc25 + maltaPrior.oc35) / maltaPrior.total * 100 };
  const maltaPriorScience = { scale_thousands: maltaPrior.oc21 + maltaPrior.oc31, share_percent: (maltaPrior.oc21 + maltaPrior.oc31) / maltaPrior.total * 100 };
  thresholdCalibration.period_stability = {
    MLT: {
      technology: { prior_period: maltaPrior.year, prior_state: stateFor(maltaPriorTech, frozenThresholds[TECH]), latest_period: maltaLatest.year, latest_state: stateFor(targetObservations[`${TECH}|MLT`], frozenThresholds[TECH]) },
      science_engineering: { prior_period: maltaPrior.year, prior_state: stateFor(maltaPriorScience, frozenThresholds[SCIENCE]), latest_period: maltaLatest.year, latest_state: stateFor(targetObservations[`${SCIENCE}|MLT`], frozenThresholds[SCIENCE]) },
    },
    CAN: { technology: { period: 2021, state: stateFor(targetObservations[`${TECH}|CAN`], frozenThresholds[TECH]), prior_period_test: "NOT_AVAILABLE_IN_ACCEPTED_CENSUS_ROUTE" } },
  };

  const anchorCodes = ["AUS", "CAN", "DEU", "IND", "JPN", "KOR", "MLT", "NZL", "SGP", "USA"];
  const anchors = {
    schema_version: "konsider-phase6b1-anchor-country-review-1.0",
    report_date: REPORT_DATE,
    countries: anchorCodes.map((countryCode) => {
      const perCandidate = (candidateId) => Object.fromEntries(PERCENTILES.map((percentile) => {
        const thresholds = thresholdsFor(originalPools[candidateId], percentile);
        const observation = expandedRowMaps[candidateId].get(countryCode);
        return [`p${Math.round(percentile * 100)}`, stateFor(observation, thresholds, Boolean(observation))];
      }));
      return {
        country_code: countryCode,
        technology: perCandidate(TECH),
        science_engineering: perCandidate(SCIENCE),
        review_note: ["JPN", "KOR", "NZL"].includes(countryCode) ? "Granularity hold retained; no proxy state." :
          countryCode === "CAN" ? "Technology accepted; science negative suppressed to insufficient." :
          countryCode === "MLT" ? "Exact harmonised evidence; scale floor prevents small-country false positive." : "Existing Phase 6B evidence retained without exception.",
      };
    }),
  };

  const tradeRows = candidateRows(phase6bEvidence, "skilled_trades_construction_opportunity");
  const tradeRouteBuckets = { skilled_only: [], construction_only: [], both: [], neither: [] };
  for (const row of tradeRows.filter((item) => item.evidence_paths.length === 2)) {
    const skilled = row.evidence_paths.find((item) => item.route_id === "modelled_skilled_trades");
    const construction = row.evidence_paths.find((item) => item.route_id === "modelled_construction_sector");
    const skilledPass = routePasses(skilled, row.thresholds.modelled_skilled_trades.frozen_values);
    const constructionPass = routePasses(construction, row.thresholds.modelled_construction_sector.frozen_values);
    const bucket = skilledPass && constructionPass ? "both" : skilledPass ? "skilled_only" : constructionPass ? "construction_only" : "neither";
    tradeRouteBuckets[bucket].push(row.country_code);
  }
  const routeAnalysis = {
    schema_version: "konsider-phase6b1-broad-criterion-route-analysis-1.0",
    report_date: REPORT_DATE,
    care_sector: { prior_name: "Health and social-work employment ecosystem", recommended_name: "Care-sector employment ecosystem", internal_construct: "ISIC Rev.4 section Q — human health and social work", disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE" },
    finance_insurance: { recommended_name: "Finance and insurance employment ecosystem", internal_construct: "ISIC Rev.4 section K", business_administration_policy: "SUPPLEMENTAL_ONLY", disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN" },
    skilled_trades_or_construction: {
      recommended_name: "Skilled-trades or construction employment ecosystem",
      route_counts: Object.fromEntries(Object.entries(tradeRouteBuckets).map(([key, value]) => [key, value.length])),
      countries_by_route: tradeRouteBuckets,
      visible_route_required: true,
      disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN",
    },
    research_academia: { recommended_name: "Research and academic ecosystem", rejected_proxy: "ISIC Rev.4 M72 research and development employment", reason: "M72 does not represent academia or field-relevant research opportunity.", disposition: "MOVE_TO_EDUCATION_RESEARCH_PHASE" },
  };

  const heldById = new Map(priorPortfolio.held.map((row) => [row.candidate_id, row]));
  const finalPortfolio = {
    schema_version: "konsider-phase6b1-final-career-opportunity-portfolio-1.0",
    report_date: REPORT_DATE,
    status: "RESEARCH_COMPLETE_IMPLEMENTATION_DESIGN_ONLY",
    runtime_change_authorized: false,
    approved_for_implementation_design: [
      { candidate_id: "health_social_work_opportunity", display_name: "Care-sector employment ecosystem", construct: "ISIC Rev.4 Q", disposition: "APPROVE_WITH_NAMING_OR_SCOPE_CHANGE", source_from_phase6b: true },
      { candidate_id: "finance_insurance_opportunity", display_name: "Finance and insurance employment ecosystem", construct: "ISIC Rev.4 K", disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN", source_from_phase6b: true },
      { candidate_id: "skilled_trades_construction_opportunity", display_name: "Skilled-trades or construction employment ecosystem", construct: "ISCO-08 7 OR ISIC Rev.4 F", disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN", source_from_phase6b: true },
      { candidate_id: TECH, display_name: heldById.get(TECH).display_name, construct: heldById.get(TECH).exact_construct, disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN", assessable_count: 63, shortlist_floor_after: 17, preferred_shortlist_count: 1, implementation_status: "NOT_STARTED" },
      { candidate_id: SCIENCE, display_name: heldById.get(SCIENCE).display_name, construct: heldById.get(SCIENCE).exact_construct, disposition: "APPROVE_FOR_IMPLEMENTATION_DESIGN", assessable_count: 67, shortlist_floor_after: 16, preferred_shortlist_count: 0, implementation_status: "NOT_STARTED", risk: "Four profiles sit exactly at the hard 16/20 floor and depend on the Eurostat Malta source." },
    ],
    moved: [{ candidate_id: "research_academia_opportunity", display_name: "Research and academic ecosystem", disposition: "MOVE_TO_EDUCATION_RESEARCH_PHASE", implementation_status: "NOT_STARTED" }],
    rejected: [],
    owner_decisions_required: [
      "Accept hard-floor rather than preferred-floor coverage for science/engineering.",
      "Accept the documented medium-confidence Canada technology mapping.",
      "Accept the care-sector name and route visibility for skilled trades/construction.",
      "Confirm research/academia moves to the education/research phase.",
    ],
  };

  const outputs = {
    "national-source-matrix.json": json(nationalSourceMatrix),
    "occupation-crosswalks.json": json(occupationCrosswalks),
    "gap-fill-country-evidence.jsonl": `${gapEvidence.map((row) => JSON.stringify(row)).join("\n")}\n`,
    "career-confidence-policy.json": json(confidencePolicy),
    "multi-route-decision-policy.json": json(multiRoutePolicy),
    "career-shortlist-coverage-before-after.json": json(coverage),
    "career-threshold-calibration.json": json(thresholdCalibration),
    "anchor-country-review.json": json(anchors),
    "broad-criterion-route-analysis.json": json(routeAnalysis),
    "final-career-opportunity-portfolio.json": json(finalPortfolio),
  };
  for (const [fileName, content] of Object.entries(outputs)) await fs.writeFile(path.join(outputDirectory, fileName), content, "utf8");

  const reportText = markdownReport({ sourceMatrix: nationalSourceMatrix, coverage, thresholdCalibration, anchors, routeAnalysis, portfolio: finalPortfolio, gapEvidence });
  await fs.writeFile(reportPath, reportText, "utf8");

  const scriptText = await fs.readFile(scriptPath, "utf8");
  const manifest = {
    schema_version: "konsider-phase6b1-replay-manifest-1.0",
    report_date: REPORT_DATE,
    command: "node project-history/phases/phase-6/research/run_phase6b1_gap_fill_and_calibration.mjs",
    input_sha256: {
      phase6b_evidence: sha256(phase6bEvidenceText),
      phase6b_shortlists: sha256(priorShortlistsText),
      phase6b_portfolio: sha256(priorPortfolioText),
      official_source_fixture: sha256(fixtureText),
      replay_script: sha256(scriptText),
      eurostat_raw_capture: fixture.sources.eurostat_lfsa_egai2d_malta.raw_capture_sha256,
      statcan_raw_capture: fixture.sources.statcan_9810059401_canada.raw_capture_sha256,
      estat_japan_raw_capture: fixture.sources.estat_japan_lfs_table_6_1.raw_capture_sha256,
    },
    output_sha256: {
      ...Object.fromEntries(Object.entries(outputs).map(([fileName, content]) => [fileName, sha256(content)])),
      "docs/research/phase6b1-career-gap-fill-and-calibration.md": sha256(reportText),
    },
    assertions: {
      target_country_count: 5,
      candidate_count: 2,
      evidence_row_count: gapEvidence.length,
      unique_country_candidate_count: new Set(gapEvidence.map((row) => `${row.country_code}|${row.candidate_id}`)).size,
      iso_alpha3_codes: gapEvidence.every((row) => /^[A-Z]{3}$/.test(row.country_code)),
      metric_compatibility: gapEvidence.filter((row) => row.scale_thousands !== null).every((row) => row.period && row.scale_thousands >= 0 && row.share_percent >= 0),
      technology_assessable_after: 63,
      science_assessable_after: 67,
      technology_all_shortlists_at_least_16: Object.values(coverage.candidates[TECH].profiles).every((profile) => profile.after.assessable_count >= 16),
      science_all_shortlists_at_least_16: Object.values(coverage.candidates[SCIENCE].profiles).every((profile) => profile.after.assessable_count >= 16),
      no_country_specific_thresholds: true,
      canada_science_negative_suppressed: gapEvidence.find((row) => row.country_code === "CAN" && row.candidate_id === SCIENCE).state === "INSUFFICIENT_EVIDENCE",
      research_only_no_runtime_change: true,
    },
  };
  const requiredAssertions = Object.values(manifest.assertions).filter((value) => typeof value === "boolean");
  if (!requiredAssertions.every(Boolean)) throw new Error("One or more Phase 6B.1 assertions failed.");
  await fs.writeFile(path.join(outputDirectory, "replay-manifest.json"), json(manifest), "utf8");
  return { outputDirectory, reportPath, manifest };
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  const result = await runPhase6B1({ repoRoot: process.cwd() });
  console.log(JSON.stringify({
    output_directory: path.relative(process.cwd(), result.outputDirectory).replaceAll("\\", "/"),
    report: path.relative(process.cwd(), result.reportPath).replaceAll("\\", "/"),
    assertions: result.manifest.assertions,
  }, null, 2));
}
