// Research-only coverage measurement for Phase 5C Batch 3.
// Captures exact World Bank API responses under ignored data/raw and emits an evidence ledger.
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const RAW = path.join(ROOT, "data", "raw", "phase5c-batch3");
const universe = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data", "country-universes", "stable-supported-v1.json"), "utf8"),
);
const stable = new Set(universe.countries.map((item) => item.code));

const candidates = [
  { id: "C53-BASIC-WATER", indicator: "SH.H2O.BASW.ZS", start: 2022, end: 2024, minYear: 2022 },
  { id: "C53-BASIC-SANITATION", indicator: "SH.STA.BASS.ZS", start: 2022, end: 2024, minYear: 2022 },
  { id: "C53-SAFELY-MANAGED-WATER", indicator: "SH.H2O.SMDW.ZS", start: 2022, end: 2024, minYear: 2022 },
  { id: "C53-SAFELY-MANAGED-SANITATION", indicator: "SH.STA.SMSS.ZS", start: 2022, end: 2024, minYear: 2022 },
];

async function main() {
  const results = [];
  fs.mkdirSync(RAW, { recursive: true });

  for (const candidate of candidates) {
    const url = `https://api.worldbank.org/v2/country/all/indicator/${candidate.indicator}?date=${candidate.start}:${candidate.end}&format=json&per_page=20000`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${candidate.indicator}: HTTP ${response.status}`);
    const body = Buffer.from(await response.arrayBuffer());
    const checksum = crypto.createHash("sha256").update(body).digest("hex");
    const rawPath = path.join(RAW, `${candidate.indicator}-${checksum}.json`);
    fs.writeFileSync(rawPath, body);
    const payload = JSON.parse(body.toString("utf8"));
    if (!Array.isArray(payload) || !Array.isArray(payload[1])) {
      throw new Error(`${candidate.indicator}: unexpected World Bank response`);
    }

    const latestByCountry = new Map();
    for (const row of payload[1]) {
      const code = row.countryiso3code;
      if (!stable.has(code) || row.value === null) continue;
      const year = Number(row.date);
      if (!Number.isInteger(year)) continue;
      latestByCountry.set(code, Math.max(year, latestByCountry.get(code) ?? 0));
    }
    const freshCodes = new Set(
      [...latestByCountry].filter(([, year]) => year >= candidate.minYear).map(([code]) => code),
    );
    results.push({
      criterion_id: candidate.id,
      indicator: candidate.indicator,
      universe_id: universe.universe_id,
      denominator: stable.size,
      measured: true,
      found: latestByCountry.size,
      fresh: freshCodes.size,
      missing_or_stale: [...stable].filter((code) => !freshCodes.has(code)).sort(),
      freshness_min_year: candidate.minYear,
      query_url: url,
      retrieved_at: new Date().toISOString(),
      sha256: `sha256:${checksum}`,
      raw_path: path.relative(ROOT, rawPath).replaceAll("\\", "/"),
    });
  }

  for (const pair of [
    ["C53-BASIC-COMPOSITE", "C53-BASIC-WATER", "C53-BASIC-SANITATION"],
    ["C53-SAFELY-MANAGED-COMPOSITE", "C53-SAFELY-MANAGED-WATER", "C53-SAFELY-MANAGED-SANITATION"],
  ]) {
    const [, leftId, rightId] = pair;
    const left = results.find((item) => item.criterion_id === leftId);
    const right = results.find((item) => item.criterion_id === rightId);
    const valid = [...stable].filter(
      (code) => !left.missing_or_stale.includes(code) && !right.missing_or_stale.includes(code),
    );
    results.push({
      criterion_id: pair[0],
      universe_id: universe.universe_id,
      denominator: stable.size,
      measured: true,
      fresh_component_intersection: valid.length,
      missing_or_stale: [...stable].filter((code) => !valid.includes(code)).sort(),
      rule: `Both ${left.indicator} and ${right.indicator} have a non-null observation from 2022-2024.`,
    });
  }

  fs.writeFileSync(
    path.join(__dirname, "world_bank_coverage_measurements.json"),
    `${JSON.stringify({ schema_version: "phase5c-coverage-measurement-1.0", results }, null, 2)}\n`,
  );
  console.log(JSON.stringify(results, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
