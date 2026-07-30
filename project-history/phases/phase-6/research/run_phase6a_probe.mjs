import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { inflateRaw } from "node:zlib";
import { promisify } from "node:util";

const inflateRawAsync = promisify(inflateRaw);
const REPORT_DATE = "2026-07-30";
const FRESHNESS_MIN_YEAR = 2021;
const MINIMUM_PCC_COUNT = 82;
const MAXIMUM_MISSING_UNION = 9;

const OCCUPATION_FAMILIES = {
  technology_employment_market_depth: {
    codes: ["25", "35"],
    label: "Technology employment-market depth",
  },
  science_engineering_employment_market_depth: {
    codes: ["21", "31"],
    label: "Science and engineering employment-market depth",
  },
  healthcare_employment_market_depth: {
    codes: ["22", "32"],
    label: "Healthcare employment-market depth",
  },
  business_administration_employment_market_depth: {
    codes: ["24", "33"],
    label: "Business and administration employment-market depth",
  },
};

const EDUCATION_CANDIDATES = {
  engineering_higher_education_capacity: {
    indicator_id: "FOSGP.5T8.F700",
    label: "Engineering higher-education capacity",
  },
  ict_higher_education_capacity: {
    indicator_id: "FOSGP.5T8.F600",
    label: "ICT higher-education capacity",
  },
};

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (quoted) {
      if (character === '"') {
        if (line[index + 1] === '"') {
          current += '"';
          index += 1;
        } else {
          quoted = false;
        }
      } else {
        current += character;
      }
    } else if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      values.push(current);
      current = "";
    } else {
      current += character;
    }
  }
  values.push(current);
  return values;
}

function listZipEntries(buffer) {
  const entries = [];
  for (let offset = 0; offset <= buffer.length - 46; offset += 1) {
    if (buffer.readUInt32LE(offset) !== 0x02014b50) {
      continue;
    }
    const nameLength = buffer.readUInt16LE(offset + 28);
    const extraLength = buffer.readUInt16LE(offset + 30);
    const commentLength = buffer.readUInt16LE(offset + 32);
    entries.push({
      name: buffer
        .subarray(offset + 46, offset + 46 + nameLength)
        .toString("utf8"),
      method: buffer.readUInt16LE(offset + 10),
      compressed_size: buffer.readUInt32LE(offset + 20),
      uncompressed_size: buffer.readUInt32LE(offset + 24),
      local_header_offset: buffer.readUInt32LE(offset + 42),
    });
    offset += 45 + nameLength + extraLength + commentLength;
  }
  return entries;
}

async function extractZipEntry(buffer, entry) {
  const offset = entry.local_header_offset;
  if (buffer.readUInt32LE(offset) !== 0x04034b50) {
    throw new Error(`Invalid ZIP local header for ${entry.name}.`);
  }
  const nameLength = buffer.readUInt16LE(offset + 26);
  const extraLength = buffer.readUInt16LE(offset + 28);
  const start = offset + 30 + nameLength + extraLength;
  const compressed = buffer.subarray(
    start,
    start + entry.compressed_size,
  );
  if (entry.method === 0) {
    return Buffer.from(compressed);
  }
  if (entry.method === 8) {
    return inflateRawAsync(compressed);
  }
  throw new Error(`Unsupported ZIP method ${entry.method} for ${entry.name}.`);
}

function selectLatest(rows, allowUnreliable = false) {
  const selected = new Map();
  for (const row of rows) {
    if (!allowUnreliable && row.unreliable) {
      continue;
    }
    const previous = selected.get(row.country_code);
    if (
      !previous ||
      row.year > previous.year ||
      (row.year === previous.year &&
        Number(row.break_flag) < Number(previous.break_flag)) ||
      (row.year === previous.year &&
        row.break_flag === previous.break_flag &&
        row.source_id < previous.source_id)
    ) {
      selected.set(row.country_code, row);
    }
  }
  return selected;
}

function averageRanks(values) {
  const ordered = values
    .map((value, index) => ({ value, index }))
    .sort((left, right) => left.value - right.value);
  const ranks = Array(values.length);
  for (let index = 0; index < ordered.length; ) {
    let next = index + 1;
    while (
      next < ordered.length &&
      ordered[next].value === ordered[index].value
    ) {
      next += 1;
    }
    const rank = (index + next - 1) / 2;
    for (let cursor = index; cursor < next; cursor += 1) {
      ranks[ordered[cursor].index] = rank;
    }
    index = next;
  }
  return ranks;
}

function percentileScores(values) {
  const ranks = averageRanks(values);
  if (values.length === 1) {
    return [5];
  }
  return ranks.map((rank) => (10 * rank) / (values.length - 1));
}

function pearson(left, right) {
  const leftMean = left.reduce((sum, value) => sum + value, 0) / left.length;
  const rightMean =
    right.reduce((sum, value) => sum + value, 0) / right.length;
  let numerator = 0;
  let leftSquared = 0;
  let rightSquared = 0;
  for (let index = 0; index < left.length; index += 1) {
    const leftDelta = left[index] - leftMean;
    const rightDelta = right[index] - rightMean;
    numerator += leftDelta * rightDelta;
    leftSquared += leftDelta ** 2;
    rightSquared += rightDelta ** 2;
  }
  return numerator / Math.sqrt(leftSquared * rightSquared);
}

function spearman(left, right) {
  return pearson(averageRanks(left), averageRanks(right));
}

function quantile(sorted, proportion) {
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  return (
    sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower)
  );
}

function summarize(values) {
  const sorted = [...values].sort((left, right) => left - right);
  const mean = sorted.reduce((sum, value) => sum + value, 0) / sorted.length;
  return {
    count: sorted.length,
    minimum: sorted[0],
    p10: quantile(sorted, 0.1),
    median: quantile(sorted, 0.5),
    p90: quantile(sorted, 0.9),
    maximum: sorted.at(-1),
    mean,
    standard_deviation: Math.sqrt(
      sorted.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
        sorted.length,
    ),
    unique_count: new Set(sorted.map((value) => value.toFixed(8))).size,
  };
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function jsonBytes(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function outcomeCountry(outcome) {
  return outcome.subject.entity_id.replace(/^country:/, "");
}

function classifyOccupationCountry(
  countryCode,
  selectedAcceptable,
  selectedIncludingUnreliable,
) {
  const accepted = selectedAcceptable.get(countryCode);
  if (accepted && accepted.year >= FRESHNESS_MIN_YEAR) {
    return {
      outcome: "valid",
      reason_codes: ["VALID_RECENT_ISCO08_OC2"],
      latest_year: accepted.year,
      classification: "ISCO-08 two-digit",
      source_id: accepted.source_id,
      observation_statuses: accepted.statuses_used,
      family_employment_thousands: accepted.family_value,
      total_employment_thousands: accepted.total_value,
      family_share_percent: accepted.share * 100,
    };
  }
  if (accepted) {
    return {
      outcome: "stale",
      reason_codes: ["LATEST_YEAR_BEFORE_2021"],
      latest_year: accepted.year,
      classification: "ISCO-08 two-digit",
      source_id: accepted.source_id,
      observation_statuses: accepted.statuses_used,
    };
  }
  const unreliable = selectedIncludingUnreliable.get(countryCode);
  if (unreliable) {
    return {
      outcome: "invalid",
      reason_codes: ["ILO_UNRELIABLE_OBSERVATION_FLAG"],
      latest_year: unreliable.year,
      classification: "ISCO-08 two-digit",
      source_id: unreliable.source_id,
      observation_statuses: unreliable.statuses_used,
    };
  }
  return {
    outcome: "missing",
    reason_codes: ["NO_COMPLETE_ISCO08_OC2_FAMILY_AND_TOTAL"],
    latest_year: null,
    classification: "ISCO-08 two-digit",
    source_id: null,
    observation_statuses: [],
  };
}

function classifyEducationCountry(countryCode, selected) {
  const row = selected.get(countryCode);
  if (!row) {
    return {
      outcome: "missing",
      reason_codes: ["NO_UIS_FIELD_SHARE_OBSERVATION"],
      latest_year: null,
    };
  }
  if (row.year < FRESHNESS_MIN_YEAR) {
    return {
      outcome: "stale",
      reason_codes: ["LATEST_YEAR_BEFORE_2021"],
      latest_year: row.year,
      qualifier: row.qualifier || null,
    };
  }
  return {
    outcome: "valid",
    reason_codes: ["VALID_RECENT_UIS_FIELD_SHARE"],
    latest_year: row.year,
    value_percent: row.value,
    qualifier: row.qualifier || null,
  };
}

async function writeOutputs(outputDirectory, outputs) {
  await fs.mkdir(outputDirectory, { recursive: true });
  const checksums = {};
  for (const [fileName, content] of Object.entries(outputs)) {
    const buffer = Buffer.from(content, "utf8");
    await fs.writeFile(path.join(outputDirectory, fileName), buffer);
    checksums[fileName] = {
      bytes: buffer.length,
      sha256: sha256(buffer),
    };
  }
  const manifest = {
    schema_version: "konsider-phase6a-replay-manifest-1.0",
    report_date: REPORT_DATE,
    deterministic: true,
    files: checksums,
  };
  await fs.writeFile(
    path.join(outputDirectory, "replay-manifest.json"),
    jsonBytes(manifest),
  );
  return manifest;
}

export async function runPhase6A({ repoRoot }) {
  const rawDirectory = path.join(repoRoot, "data", "raw", "phase6a");
  const outputDirectory = path.join(
    repoRoot,
    "data",
    "reports",
    `phase6a-${REPORT_DATE}`,
  );
  const stableUniverse = JSON.parse(
    await fs.readFile(
      path.join(
        repoRoot,
        "data",
        "country-universes",
        "stable-supported-v1.json",
      ),
      "utf8",
    ),
  );
  const countryCodes = stableUniverse.countries.map(
    (country) => country.code,
  );
  const countrySet = new Set(countryCodes);

  const activeCatalog = JSON.parse(
    await fs.readFile(
      path.join(
        repoRoot,
        "data",
        "releases",
        "2026-07-29.2",
        "consumer-catalog.json",
      ),
      "utf8",
    ),
  );
  const activeOutcomes = (
    await fs.readFile(
      path.join(
        repoRoot,
        "data",
        "releases",
        "2026-07-29.2",
        "criterion-outcomes.jsonl",
      ),
      "utf8",
    )
  )
    .trim()
    .split(/\r?\n/)
    .map(JSON.parse);
  const activePccIds = activeCatalog.criteria
    .filter(
      (criterion) =>
        criterion.coverage.mode === "CONDITIONAL_COMPLETE_CASE",
    )
    .map((criterion) => criterion.id);
  const currentMissingUnion = new Set(
    activeOutcomes
      .filter(
        (outcome) =>
          activePccIds.includes(outcome.criterion_id) &&
          outcome.outcome !== "valid",
      )
      .map(outcomeCountry),
  );

  const iloPath = path.join(rawDirectory, "ilostat-emp-oc2.csv");
  const iloBuffer = await fs.readFile(iloPath);
  const iloLines = iloBuffer.toString("utf8").split(/\r?\n/);
  const iloHeaders = parseCsvLine(iloLines[0].replace(/^\uFEFF/, ""));
  const iloIndex = Object.fromEntries(
    iloHeaders.map((header, index) => [header, index]),
  );
  const requiredOccupationCodes = new Set([
    "TOTAL",
    ...Object.values(OCCUPATION_FAMILIES).flatMap(
      (family) => family.codes,
    ),
  ]);
  const combinations = new Map();
  for (const line of iloLines.slice(1)) {
    if (!line) {
      continue;
    }
    const row = parseCsvLine(line);
    const countryCode = row[iloIndex.ref_area];
    if (
      !countrySet.has(countryCode) ||
      row[iloIndex.sex] !== "SEX_T" ||
      !row[iloIndex.classif1].startsWith("OC2_ISCO08_")
    ) {
      continue;
    }
    const code = row[iloIndex.classif1].slice("OC2_ISCO08_".length);
    if (!requiredOccupationCodes.has(code)) {
      continue;
    }
    const key = [
      countryCode,
      row[iloIndex.source],
      row[iloIndex.time],
    ].join("|");
    const combination = combinations.get(key) ?? {
      country_code: countryCode,
      source_id: row[iloIndex.source],
      year: Number(row[iloIndex.time]),
      values: {},
      statuses: {},
    };
    combination.values[code] = Number(row[iloIndex.obs_value]);
    combination.statuses[code] = row[iloIndex.obs_status] || "";
    combinations.set(key, combination);
  }

  const occupationSelections = {};
  for (const [candidateId, definition] of Object.entries(
    OCCUPATION_FAMILIES,
  )) {
    const candidates = [];
    for (const combination of combinations.values()) {
      const requiredCodes = ["TOTAL", ...definition.codes];
      if (
        requiredCodes.every((code) =>
          Number.isFinite(combination.values[code]),
        ) &&
        combination.values.TOTAL > 0
      ) {
        const statuses = requiredCodes
          .map((code) => combination.statuses[code])
          .filter(Boolean);
        const familyValue = definition.codes.reduce(
          (sum, code) => sum + combination.values[code],
          0,
        );
        candidates.push({
          ...combination,
          family_value: familyValue,
          total_value: combination.values.TOTAL,
          share: familyValue / combination.values.TOTAL,
          statuses_used: statuses,
          unreliable: statuses.includes("U"),
          break_flag: statuses.includes("B"),
        });
      }
    }
    occupationSelections[candidateId] = {
      acceptable: selectLatest(candidates, false),
      including_unreliable: selectLatest(candidates, true),
    };
  }

  const uisPath = path.join(rawDirectory, "uis-opri-202602.zip");
  const uisBuffer = await fs.readFile(uisPath);
  const uisEntries = listZipEntries(uisBuffer);
  const nationalEntry = uisEntries.find(
    (entry) => entry.name === "OPRI_DATA_NATIONAL.csv",
  );
  const readmeEntry = uisEntries.find(
    (entry) => entry.name === "OPRI_README_RELEASE_2026_February.md",
  );
  if (!nationalEntry || !readmeEntry) {
    throw new Error("The UIS archive is missing required entries.");
  }
  const uisNationalLines = (
    await extractZipEntry(uisBuffer, nationalEntry)
  )
    .toString("utf8")
    .split(/\r?\n/);
  const uisReadme = (await extractZipEntry(uisBuffer, readmeEntry)).toString(
    "utf8",
  );
  if (
    !uisReadme.includes(
      "Creative Commons Attribution-ShareAlike 3.0 IGO License",
    )
  ) {
    throw new Error("The expected UIS embedded licence statement changed.");
  }
  const educationSelections = {};
  for (const [candidateId, definition] of Object.entries(
    EDUCATION_CANDIDATES,
  )) {
    const selected = new Map();
    for (const line of uisNationalLines) {
      if (
        !line.startsWith(`"${definition.indicator_id}"`) &&
        !line.startsWith(`${definition.indicator_id},`)
      ) {
        continue;
      }
      const row = parseCsvLine(line);
      if (!countrySet.has(row[1])) {
        continue;
      }
      const observation = {
        country_code: row[1],
        year: Number(row[2]),
        value: Number(row[3]),
        magnitude: row[4],
        qualifier: row[5],
      };
      const previous = selected.get(observation.country_code);
      if (
        Number.isFinite(observation.value) &&
        (!previous || observation.year > previous.year)
      ) {
        selected.set(observation.country_code, observation);
      }
    }
    educationSelections[candidateId] = selected;
  }

  const countryCoverage = [];
  for (const [candidateId, selections] of Object.entries(
    occupationSelections,
  )) {
    for (const countryCode of countryCodes) {
      countryCoverage.push({
        candidate_id: candidateId,
        country_code: countryCode,
        ...classifyOccupationCountry(
          countryCode,
          selections.acceptable,
          selections.including_unreliable,
        ),
      });
    }
  }
  for (const [candidateId, selected] of Object.entries(
    educationSelections,
  )) {
    for (const countryCode of countryCodes) {
      countryCoverage.push({
        candidate_id: candidateId,
        country_code: countryCode,
        indicator_id: EDUCATION_CANDIDATES[candidateId].indicator_id,
        ...classifyEducationCountry(countryCode, selected),
      });
    }
  }
  for (const countryCode of countryCodes) {
    countryCoverage.push({
      candidate_id: "engineering_academic_research_ecosystem",
      country_code: countryCode,
      outcome: "rejected",
      reason_codes: [
        "NO_PINNED_OPENALEX_CAPTURE",
        "NO_DETERMINISTIC_INSTITUTION_LOCALITY_MAPPING",
      ],
      latest_year: null,
    });
  }

  const coverageSummary = {
    schema_version: "konsider-phase6a-coverage-summary-1.0",
    report_date: REPORT_DATE,
    stable_universe_id: stableUniverse.universe_id,
    stable_country_count: countryCodes.length,
    freshness_min_year: FRESHNESS_MIN_YEAR,
    minimum_pcc_count: MINIMUM_PCC_COUNT,
    maximum_missing_union: MAXIMUM_MISSING_UNION,
    active_pcc_ids: activePccIds,
    current_active_pcc_missing_union: [...currentMissingUnion].sort(),
    current_active_pcc_missing_union_count: currentMissingUnion.size,
    candidates: {},
  };
  for (const candidateId of [
    ...Object.keys(OCCUPATION_FAMILIES),
    ...Object.keys(EDUCATION_CANDIDATES),
    "engineering_academic_research_ecosystem",
  ]) {
    const rows = countryCoverage.filter(
      (row) => row.candidate_id === candidateId,
    );
    const counts = {
      valid: 0,
      missing: 0,
      stale: 0,
      invalid: 0,
      rejected: 0,
    };
    for (const row of rows) {
      counts[row.outcome] += 1;
    }
    const nonvalid = rows
      .filter((row) => row.outcome !== "valid")
      .map((row) => row.country_code)
      .sort();
    const combinedUnion = new Set([...currentMissingUnion, ...nonvalid]);
    coverageSummary.candidates[candidateId] = {
      outcome_counts: counts,
      valid_country_count: counts.valid,
      expected_coverage_mode: "DIAGNOSTIC_ONLY",
      passes_pcc_minimum: counts.valid >= MINIMUM_PCC_COUNT,
      nonvalid_countries: nonvalid,
      combined_with_all_active_pcc_missing_union: [...combinedUnion].sort(),
      combined_missing_union_count: combinedUnion.size,
      passes_combined_missing_union_limit:
        combinedUnion.size <= MAXIMUM_MISSING_UNION,
      latest_year_by_country: Object.fromEntries(
        rows.map((row) => [row.country_code, row.latest_year]),
      ),
    };
  }

  const scoreSensitivity = {
    schema_version: "konsider-phase6a-score-sensitivity-1.0",
    report_date: REPORT_DATE,
    note: "Diagnostic calculations only; no candidate is approved for runtime scoring.",
    occupation: {},
    education: {},
    academic_ecosystem: {
      status: "NOT_MEASURED",
      reason:
        "No pinned OpenAlex capture and no deterministic institution-to-locality mapping.",
    },
  };
  for (const [candidateId, selections] of Object.entries(
    occupationSelections,
  )) {
    const rows = [...selections.acceptable.values()]
      .filter((row) => row.year >= FRESHNESS_MIN_YEAR)
      .sort((left, right) =>
        left.country_code.localeCompare(right.country_code),
      );
    const shares = rows.map((row) => row.share * 100);
    const logScale = rows.map((row) => Math.log1p(row.family_value));
    const shareScores = percentileScores(shares);
    const scaleScores = percentileScores(logScale);
    const blendScores = shareScores.map(
      (score, index) => (score + scaleScores[index]) / 2,
    );
    scoreSensitivity.occupation[candidateId] = {
      country_count: rows.length,
      score_candidates: {
        occupation_share_percentile: summarize(shareScores),
        log_employment_scale_percentile: summarize(scaleScores),
        equal_depth_specialization_blend: summarize(blendScores),
      },
      raw_dispersion: {
        occupation_share_percent: summarize(shares),
        occupation_employment_thousands: summarize(
          rows.map((row) => row.family_value),
        ),
      },
      spearman: {
        share_vs_log_scale: spearman(shares, logScale),
        share_vs_equal_blend: spearman(shares, blendScores),
        log_scale_vs_equal_blend: spearman(logScale, blendScores),
      },
    };
  }
  for (const [candidateId, selected] of Object.entries(
    educationSelections,
  )) {
    const rows = [...selected.values()]
      .filter((row) => row.year >= FRESHNESS_MIN_YEAR)
      .sort((left, right) =>
        left.country_code.localeCompare(right.country_code),
      );
    const shares = rows.map((row) => row.value);
    scoreSensitivity.education[candidateId] = {
      country_count: rows.length,
      raw_field_share_percent: summarize(shares),
      percentile_score: summarize(percentileScores(shares)),
      capacity_score_status: "NOT_CONSTRUCTIBLE",
      reason:
        "The exact current UIS archive has field shares but no compatible field graduate count.",
    };
  }

  const mappings = {
    schema_version: "konsider-phase6a-proposed-mappings-1.0",
    report_date: REPORT_DATE,
    status: "PROPOSED_NOT_FROZEN",
    occupation: {
      classification: "ISCO-08",
      available_granularity: "two-digit only",
      table: "EMP_TEMP_SEX_OC2_NB_A",
      sex: "SEX_T",
      total: "OC2_ISCO08_TOTAL",
      families: Object.fromEntries(
        Object.entries(OCCUPATION_FAMILIES).map(
          ([candidateId, definition]) => [
            candidateId,
            definition.codes.map((code) => `OC2_ISCO08_${code}`),
          ],
        ),
      ),
      excluded_examples: {
        technology: [
          "133 ICT services managers",
          "215 electrotechnology engineers",
          "742 electronics and telecommunications installers and repairers",
        ],
        science_engineering: [
          "ISCO-08 trades and production groups outside 21 and 31",
        ],
        business_administration: [
          "management, legal, sales, clerical and marketing groups outside 24 and 33",
        ],
      },
    },
    education: {
      classification: "ISCED-F 2013 broad fields; tertiary ISCED 5-8",
      sex: "both sexes",
      families: {
        engineering_higher_education_capacity: {
          indicator_id: "FOSGP.5T8.F700",
          field: "Engineering, manufacturing and construction",
        },
        ict_higher_education_capacity: {
          indicator_id: "FOSGP.5T8.F600",
          field: "Information and Communication Technologies",
        },
      },
    },
    research_field: {
      taxonomy: "OpenAlex domain > field > subfield > topic",
      primary_mapping: [
        {
          field_id: 22,
          name: "Engineering",
          inclusion: "primary mapping",
        },
      ],
      sensitivity_mapping: [
        { field_id: 15, name: "Chemical Engineering" },
        { field_id: 21, name: "Energy" },
        { field_id: 25, name: "Materials Science" },
      ],
      explicitly_excluded_from_primary: [
        { field_id: 17, name: "Computer Science" },
        { field_id: 16, name: "Chemistry" },
        { field_id: 31, name: "Physics and Astronomy" },
      ],
      freeze_status:
        "Not frozen because no exact taxonomy capture was retained.",
    },
  };

  const sources = {
    schema_version: "konsider-phase6a-source-legal-evidence-1.0",
    report_date: REPORT_DATE,
    assets: [
      {
        source_id: "ilostat-emp-temp-sex-oc2-nb-a-2026-07-29",
        publisher: "International Labour Organization",
        distributor: "ILOSTAT bulk data API",
        asset: "Employment by sex and occupation (thousands), annual",
        indicator_id: "EMP_TEMP_SEX_OC2_NB_A",
        url: "https://rplumber.ilo.org/data/indicator/?id=EMP_TEMP_SEX_OC2_NB_A&format=csv",
        access_date: "2026-07-29",
        version:
          "Mutable current capture; content frozen by SHA-256 for this study",
        local_file: "data/raw/phase6a/ilostat-emp-oc2.csv",
        bytes: iloBuffer.length,
        sha256: sha256(iloBuffer),
        licence: "Creative Commons Attribution 4.0 International",
        commercial_use: true,
        redistribution: true,
        attribution_required: true,
        third_party_restrictions:
          "Restricted partner microdata are excluded; this probe uses published aggregate data.",
        raw_retention: "Local ignored content-address candidate; not committed.",
        normalized_derived_release_commit: true,
      },
      {
        source_id: "uis-opri-2026-02",
        publisher: "UNESCO Institute for Statistics",
        distributor: "UIS Bulk Data Download Service",
        asset: "Education: Other Policy Relevant Indicators",
        url: "https://download.uis.unesco.org/bdds/202602/OPRI.zip",
        access_date: "2026-07-29",
        version: "February 2026; extracted 2026-02-12 11:15:13",
        local_file: "data/raw/phase6a/uis-opri-202602.zip",
        bytes: uisBuffer.length,
        sha256: sha256(uisBuffer),
        licence:
          "Creative Commons Attribution-ShareAlike 3.0 IGO (embedded archive README)",
        commercial_use: true,
        redistribution: true,
        attribution_required: true,
        third_party_restrictions:
          "ShareAlike applies; site terms currently state BY-SA 4.0 while the exact archive states BY-SA 3.0 IGO.",
        raw_retention: "Local ignored capture; not committed.",
        normalized_derived_release_commit:
          "OWNER_LEGAL_REVIEW_REQUIRED_FOR_SHAREALIKE",
      },
      {
        source_id: "openalex-public-data-unpinned",
        publisher: "OurResearch",
        distributor: "OpenAlex",
        asset: "Works, institutions and topic taxonomy",
        url: "https://developers.openalex.org/download/overview",
        access_date: "2026-07-30",
        version: "No exact snapshot or API capture retained",
        local_file: null,
        bytes: null,
        sha256: null,
        licence: "CC0 per OpenAlex data documentation",
        commercial_use: true,
        redistribution: true,
        attribution_required: false,
        third_party_restrictions:
          "Current service terms contain broader restrictions that require review if API capture is used.",
        raw_retention:
          "Blocked: choose a pinned ~330 GB quarterly snapshot or an API/CLI capture with a user-supplied key.",
        normalized_derived_release_commit:
          "BLOCKED_PENDING_CAPTURE_AND_TERMS_REVIEW",
      },
      {
        source_id: "ror-v2.10-2026-07-20",
        publisher: "Research Organization Registry",
        distributor: "Zenodo",
        asset: "v2.10-2026-07-20-ror-data.zip",
        url: "https://zenodo.org/records/21458494",
        access_date: "2026-07-30",
        version: "v2.10, schema v2, 132,537 organizations",
        local_file: null,
        bytes: 33700000,
        md5_publisher: null,
        sha256: null,
        licence: "CC0; GeoNames-derived location data CC BY 4.0",
        commercial_use: true,
        redistribution: true,
        attribution_required:
          "Required for GeoNames-derived location components",
        third_party_restrictions:
          "GeoNames location data requires CC BY 4.0 attribution.",
        raw_retention:
          "Not downloaded because OpenAlex acquisition failed first.",
        normalized_derived_release_commit:
          "BLOCKED_PENDING_CAPTURE_AND_MAPPING",
      },
    ],
  };

  const decisionMatrix = {
    schema_version: "konsider-phase6a-decision-matrix-1.0",
    report_date: REPORT_DATE,
    approved_count: 0,
    implementation_gate_passed: false,
    rows: [
      {
        proposed_public_id: "technology_employment_market_depth",
        display_name: "Technology employment-market depth",
        phase3_lineage: "C12",
        exact_construct:
          "ISCO-08 groups 25 and 35 employment stock, tested as share, log scale and equal blend.",
        does_not_mean:
          "Live vacancies, hiring demand, job quality or applicant probability.",
        scope: "national-direct",
        source: "ILOSTAT EMP_TEMP_SEX_OC2_NB_A",
        taxonomy: "ISCO-08 two-digit: 25 + 35",
        metric: "Diagnostic equal blend of share and log employment scale",
        scoring_idea: "Equal percentile blend; not approved",
        reference_period: "Latest acceptable 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates.technology_employment_market_depth
            .valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Scale component overlaps population and overall employment depth.",
        licensing_conclusion: "Passes under ILO CC BY 4.0",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "medium",
        decision: "DIAGNOSTIC_ONLY",
        conditions:
          "Fails 82-country minimum; a new official edition/source must reach the policy without imputation.",
      },
      {
        proposed_public_id: "science_engineering_employment_market_depth",
        display_name: "Science and engineering employment-market depth",
        phase3_lineage: "C15",
        exact_construct:
          "ISCO-08 groups 21 and 31 employment stock, including natural sciences.",
        does_not_mean:
          "Pure engineering, skilled trades, vacancies, licensing access or applicant probability.",
        scope: "national-direct",
        source: "ILOSTAT EMP_TEMP_SEX_OC2_NB_A",
        taxonomy: "ISCO-08 two-digit: 21 + 31",
        metric: "Diagnostic equal blend of share and log employment scale",
        scoring_idea: "Equal percentile blend; not approved",
        reference_period: "Latest acceptable 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates
            .science_engineering_employment_market_depth.valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Scale component overlaps population and overall employment depth.",
        licensing_conclusion: "Passes under ILO CC BY 4.0",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "medium",
        decision: "DIAGNOSTIC_ONLY",
        conditions:
          "Fails 82-country minimum; three-digit table is unavailable, so the public name must remain science and engineering.",
      },
      {
        proposed_public_id: "engineering_higher_education_capacity",
        display_name: "Engineering higher-education capacity",
        phase3_lineage: "C01 production component",
        exact_construct:
          "Target is scale plus specialization; exact current source supplies only graduate share for ISCED 5-8 field 700.",
        does_not_mean:
          "Admissions, accreditation, teaching quality, affordability or applicant access.",
        scope: "national-direct",
        source: "UIS OPRI February 2026",
        taxonomy: "ISCED-F field 700; ISCED levels 5-8; both sexes",
        metric: "Capacity metric not constructible; share-only diagnostic tested",
        scoring_idea: "No approved score",
        reference_period: "Latest 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates.engineering_higher_education_capacity
            .valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Share alone rewards specialization without proving scale.",
        licensing_conclusion:
          "ShareAlike-compatible use requires owner/legal acceptance",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "medium",
        decision: "HOLD_CRITICAL_BLOCKER",
        conditions:
          "Need compatible field counts or field share plus total graduates, at least 82 fresh countries, and ShareAlike disposition.",
      },
      {
        proposed_public_id: "engineering_academic_research_ecosystem",
        display_name: "Engineering academic and research ecosystem",
        phase3_lineage: "C05 and C01 field-specific extension",
        exact_construct:
          "Five-year engineering-primary-topic fractional output plus breadth of active institutions, locality-derived to country.",
        does_not_mean:
          "Teaching quality, admissions, accreditation or applicant access.",
        scope: "institution/locality-derived country result",
        source: "OpenAlex plus ROR v2.10",
        taxonomy:
          "OpenAlex field 22 primary; sensitivity fields 15, 21 and 25",
        metric:
          "Proposed log fractional output and active-institution breadth blend",
        scoring_idea: "Not tested",
        reference_period: "Proposed 2021-2025",
        valid_country_estimate: 0,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Correlation with active WIPO C05 not measurable without the capture.",
        licensing_conclusion:
          "Data licences broadly reusable; API terms and GeoNames attribution require review",
        replay_feasibility: "Blocked",
        implementation_effort: "high",
        decision: "HOLD_CRITICAL_BLOCKER",
        conditions:
          "Pin an OpenAlex capture, accept acquisition cost/key requirement, retain ROR, and build deterministic institution-to-GHSL mapping.",
      },
      {
        proposed_public_id: "healthcare_employment_market_depth",
        display_name: "Healthcare employment-market depth",
        phase3_lineage: "C13",
        exact_construct:
          "ISCO-08 groups 22 and 32 employment stock.",
        does_not_mean:
          "Shortage, vacancies, licensing access or applicant probability.",
        scope: "national-direct",
        source: "ILOSTAT EMP_TEMP_SEX_OC2_NB_A",
        taxonomy: "ISCO-08 two-digit: 22 + 32",
        metric: "Diagnostic equal blend of share and log employment scale",
        scoring_idea: "Equal percentile blend; not approved",
        reference_period: "Latest acceptable 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates.healthcare_employment_market_depth
            .valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Scale overlaps population and broad health-system capacity.",
        licensing_conclusion: "Passes under ILO CC BY 4.0",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "low after shared adapter",
        decision: "DIAGNOSTIC_ONLY",
        conditions: "Fails the 82-country minimum.",
      },
      {
        proposed_public_id:
          "business_administration_employment_market_depth",
        display_name: "Business and administration employment-market depth",
        phase3_lineage: "C14",
        exact_construct:
          "ISCO-08 groups 24 and 33 employment stock.",
        does_not_mean:
          "All business/finance jobs, management, sales, vacancies or applicant probability.",
        scope: "national-direct",
        source: "ILOSTAT EMP_TEMP_SEX_OC2_NB_A",
        taxonomy: "ISCO-08 two-digit: 24 + 33",
        metric: "Diagnostic equal blend of share and log employment scale",
        scoring_idea: "Equal percentile blend; not approved",
        reference_period: "Latest acceptable 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates
            .business_administration_employment_market_depth
            .valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Scale overlaps population and broad service-economy depth.",
        licensing_conclusion: "Passes under ILO CC BY 4.0",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "low after shared adapter",
        decision: "DIAGNOSTIC_ONLY",
        conditions:
          "Fails the 82-country minimum; truthful name is narrower than business and finance.",
      },
      {
        proposed_public_id: "ict_higher_education_capacity",
        display_name: "ICT higher-education capacity",
        phase3_lineage: "C01 field-specific component",
        exact_construct:
          "Target is scale plus specialization; exact current source supplies only graduate share for ISCED 5-8 field 600.",
        does_not_mean:
          "Admissions, accreditation, teaching quality, affordability or applicant access.",
        scope: "national-direct",
        source: "UIS OPRI February 2026",
        taxonomy: "ISCED-F field 600; ISCED levels 5-8; both sexes",
        metric: "Capacity metric not constructible; share-only diagnostic tested",
        scoring_idea: "No approved score",
        reference_period: "Latest 2021+ observation",
        valid_country_estimate:
          coverageSummary.candidates.ict_higher_education_capacity
            .valid_country_count,
        expected_coverage_mode: "DIAGNOSTIC_ONLY",
        correlation_risks:
          "Share alone rewards specialization without proving scale.",
        licensing_conclusion:
          "ShareAlike-compatible use requires owner/legal acceptance",
        replay_feasibility: "Passes from retained capture",
        implementation_effort: "low after education adapter",
        decision: "HOLD_CRITICAL_BLOCKER",
        conditions:
          "Need compatible field counts or field share plus total graduates, at least 82 fresh countries, and ShareAlike disposition.",
      },
    ],
  };

  const rawArtifacts = {
    schema_version: "konsider-phase6a-raw-artifacts-1.0",
    report_date: REPORT_DATE,
    artifacts: [
      {
        file: "data/raw/phase6a/ilostat-emp-oc2.csv",
        bytes: iloBuffer.length,
        sha256: sha256(iloBuffer),
      },
      {
        file: "data/raw/phase6a/uis-opri-202602.zip",
        bytes: uisBuffer.length,
        sha256: sha256(uisBuffer),
      },
      ...(
        await Promise.all(
          ["ilostat-guidelines.pdf", "uis-terms.html"].map(
            async (fileName) => {
              const buffer = await fs.readFile(
                path.join(rawDirectory, fileName),
              );
              return {
                file: `data/raw/phase6a/${fileName}`,
                bytes: buffer.length,
                sha256: sha256(buffer),
              };
            },
          ),
        )
      ),
    ],
  };

  const implementationPortfolio = {
    schema_version: "konsider-phase6a-implementation-portfolio-1.0",
    report_date: REPORT_DATE,
    approved_core: [],
    approved_stretch: [],
    diagnostic_only: [
      "technology_employment_market_depth",
      "science_engineering_employment_market_depth",
      "healthcare_employment_market_depth",
      "business_administration_employment_market_depth",
    ],
    blocked: [
      "engineering_higher_education_capacity",
      "engineering_academic_research_ecosystem",
      "ict_higher_education_capacity",
    ],
    implementation_gate_passed: false,
    next_prompt_authorized: false,
    reason:
      "Zero candidates are approved; the Phase 6 rule requires four or evidence that four are impossible. This study provides the latter and stops before runtime work.",
  };

  const outputs = {
    "approved-implementation-portfolio.json": jsonBytes(
      implementationPortfolio,
    ),
    "country-coverage.jsonl": `${countryCoverage
      .map((row) => JSON.stringify(row))
      .join("\n")}\n`,
    "coverage-summary.json": jsonBytes(coverageSummary),
    "decision-matrix.json": jsonBytes(decisionMatrix),
    "mappings.json": jsonBytes(mappings),
    "raw-artifacts.json": jsonBytes(rawArtifacts),
    "score-sensitivity.json": jsonBytes(scoreSensitivity),
    "sources.json": jsonBytes(sources),
  };
  const manifest = await writeOutputs(outputDirectory, outputs);
  return {
    output_directory: outputDirectory,
    manifest,
    decision_matrix: decisionMatrix,
    coverage_summary: coverageSummary,
  };
}
