// Research-only coverage measurement for Phase 3C Batch 2.
// Captures exact API responses under ignored data/raw and emits a compact evidence ledger.
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..", "..", "..", "..");
const RAW = path.join(ROOT, "data", "raw", "phase3c-batch2");
const universe = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data", "country-universes", "stable-supported-v1.json"), "utf8"),
);
const stable = new Set(universe.countries.map((item) => item.code));

const candidates = [
  { id: "C16", indicator: "IC.BUS.NDNS.ZS", start: 2022, end: 2024, minYear: 2022, minObservations: 1 },
  { id: "C29-INFLATION", indicator: "FP.CPI.TOTL.ZG", start: 2020, end: 2024, minYear: 2023, minObservations: 3 },
  { id: "C29-FXRATE", indicator: "PA.NUS.FCRF", start: 2020, end: 2024, minYear: 2023, minObservations: 3 },
  { id: "C48", indicator: "GOV_WGI_PV_EST", start: 2024, end: 2024, minYear: 2024, minObservations: 1 },
  { id: "C49", indicator: "GOV_WGI_RL_EST", start: 2024, end: 2024, minYear: 2024, minObservations: 1 },
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

    const byCountry = new Map();
    for (const row of payload[1]) {
      const code = row.countryiso3code;
      if (!stable.has(code) || row.value === null) continue;
      const year = Number(row.date);
      if (!Number.isInteger(year)) continue;
      if (!byCountry.has(code)) byCountry.set(code, []);
      byCountry.get(code).push(year);
    }
    const found = [...byCountry].filter(([, years]) => years.length >= candidate.minObservations);
    const fresh = found.filter(([, years]) => Math.max(...years) >= candidate.minYear);
    const freshCodes = new Set(fresh.map(([code]) => code));
    results.push({
      criterion_id: candidate.id,
      indicator: candidate.indicator,
      universe_id: universe.universe_id,
      denominator: stable.size,
      measured: true,
      found_with_minimum_observations: found.length,
      fresh: fresh.length,
      missing_or_insufficient: [...stable].filter((code) => !freshCodes.has(code)).sort(),
      freshness_min_year: candidate.minYear,
      minimum_observations: candidate.minObservations,
      query_url: url,
      retrieved_at: new Date().toISOString(),
      sha256: `sha256:${checksum}`,
      raw_path: path.relative(ROOT, rawPath).replaceAll("\\", "/"),
    });
  }

  const inflation = results.find((item) => item.criterion_id === "C29-INFLATION");
  const fx = results.find((item) => item.criterion_id === "C29-FXRATE");
  const inflationCodes = new Set([...stable].filter((code) => !inflation.missing_or_insufficient.includes(code)));
  const fxCodes = new Set([...stable].filter((code) => !fx.missing_or_insufficient.includes(code)));
  const compositeCodes = [...stable].filter((code) => inflationCodes.has(code) && fxCodes.has(code));
  results.push({
    criterion_id: "C29",
    universe_id: universe.universe_id,
    denominator: stable.size,
    measured: true,
    valid_component_intersection: compositeCodes.length,
    missing_or_insufficient: [...stable].filter((code) => !compositeCodes.includes(code)).sort(),
    rule: "At least three non-null annual observations in 2020-2024 for both inflation and official exchange rate, with latest observation in 2023 or 2024.",
  });

  fs.writeFileSync(
    path.join(__dirname, "world_bank_coverage_measurements.json"),
    `${JSON.stringify({ schema_version: "phase3c-coverage-measurement-1.0", results }, null, 2)}\n`,
  );
  console.log(JSON.stringify(results, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
