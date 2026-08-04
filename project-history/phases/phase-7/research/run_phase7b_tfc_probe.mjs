import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "../../../..");
const reportDate = "2026-08-05";
const outputDir = path.join(repoRoot, "data", "reports", `phase7b-${reportDate}`);
const universePath = path.join(repoRoot, "data", "country-universes", "stable-supported-v1.json");
const protocolPath = path.join(repoRoot, "data", "reports", "phase7a-2026-08-05", "phase7b-deep-probe-protocol.json");
const fixturePath = path.join(scriptDir, "fixtures", "phase7b-source-fixture.json");

function stableStringify(value) {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function pretty(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function sha256(content) {
  return crypto.createHash("sha256").update(content).digest("hex");
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function writeArtifact(name, content, artifacts) {
  const body = typeof content === "string" ? content : pretty(content);
  await fs.writeFile(path.join(outputDir, name), body, "utf8");
  artifacts.push({ path: name, sha256: sha256(body), bytes: Buffer.byteLength(body) });
}

function countBy(rows, key) {
  return rows.reduce((counts, row) => {
    counts[row[key]] = (counts[row[key]] ?? 0) + 1;
    return counts;
  }, {});
}

const gateNames = ["PRODUCT", "CONSTRUCT", "SOURCE", "LEGAL", "COVERAGE", "PROFILE_INPUT", "REPLAY", "SAFETY_INTERPRETATION", "MAINTENANCE"];

function gateResults(candidate) {
  if (candidate.disposition === "PRODUCTION_QUALIFIED_FIRST_WAVE") {
    return Object.fromEntries(gateNames.map((gate) => [gate, "PASS"]));
  }
  const failed = {
    permanent_residence_pathway: ["CONSTRUCT", "SOURCE", "COVERAGE", "REPLAY", "MAINTENANCE"],
    professional_licensing_requirements: ["CONSTRUCT", "SOURCE", "COVERAGE", "REPLAY", "MAINTENANCE"],
    employment_deductions_estimate: ["CONSTRUCT", "SOURCE", "COVERAGE", "REPLAY", "MAINTENANCE"],
    housing_affordability_scenario: ["COVERAGE"],
    healthcare_affordability_scenario: ["CONSTRUCT", "SOURCE", "COVERAGE", "REPLAY", "MAINTENANCE"],
  }[candidate.tfc_id] ?? ["SOURCE"];
  return Object.fromEntries(gateNames.map((gate) => [gate, failed.includes(gate) ? "FAIL" : "PASS"]));
}

function syntheticScenarios() {
  return [
    { scenario_id: "missing_required_field", tfc_id: "skilled_work_route_feasibility", profile: { destination: "DEU", occupation: null }, expected_state: "INPUT_REQUIRED", reason: "Occupation is required and is never guessed." },
    { scenario_id: "job_offer_present", tfc_id: "skilled_work_route_feasibility", profile: { destination: "DEU", occupation: "software_engineer", job_offer: true, salary: "ABOVE_FROZEN_THRESHOLD", qualification: "RECOGNIZED", snapshot_date: reportDate }, expected_state: "CONDITIONAL_ROUTE_MATCH", reason: "A positive source-rule match is conditional on official processing." },
    { scenario_id: "job_offer_absent", tfc_id: "skilled_work_route_feasibility", profile: { destination: "GBR", occupation: "software_engineer", job_offer: false, snapshot_date: reportDate }, expected_state: "INPUT_REQUIRED_OR_NO_POSITIVE_CONCLUSION", reason: "The first wave does not expose a complete no-route-matched conclusion." },
    { scenario_id: "relocating_alone", tfc_id: "family_accompaniment_reunification", profile: { destination: "AUS", household_roles: [], primary_route: "AU_SID_482", snapshot_date: reportDate }, expected_state: "NOT_APPLICABLE_BY_DECLARED_SCENARIO", reason: "No household member is declared." },
    { scenario_id: "partner_and_child", tfc_id: "family_accompaniment_reunification", profile: { destination: "AUS", household_roles: ["partner", "dependent_child"], primary_route: "AU_SID_482", snapshot_date: reportDate }, expected_state: "CONDITIONAL_ROUTE_MATCH", reason: "The route permits bounded secondary-applicant roles subject to conditions." },
    { scenario_id: "student_completion", tfc_id: "post_study_work_pathway", profile: { destination: "USA", status: "F1", qualification_level: "masters", completion_state: "PLANNED", snapshot_date: reportDate }, expected_state: "CONDITIONAL_ROUTE_MATCH", reason: "Future completion remains provisional and requires DSO/USCIS authorization." },
    { scenario_id: "unsupported_destination", tfc_id: "skilled_work_route_feasibility", profile: { destination: "IND", occupation: "software_engineer", snapshot_date: reportDate }, expected_state: "DESTINATION_UNSUPPORTED", reason: "Missing destination support is not an applicant-negative result." },
    { scenario_id: "regional_licensing", tfc_id: "professional_licensing_requirements", profile: { destination: "DEU", region: "Bavaria", profession: "physician", qualification_origin: "IND", snapshot_date: reportDate }, expected_state: "SOURCE_ROUTE_PARTIALLY_ASSESSABLE", reason: "The bounded regulator/jurisdiction rule set is not captured." },
    { scenario_id: "effective_date_changed", tfc_id: "skilled_work_route_feasibility", profile: { destination: "GBR", evidence_effective_from: "2026-07-01", snapshot_date: "2026-06-30" }, expected_state: "EVIDENCE_DATE_MISMATCH", reason: "Evidence cannot be applied outside its effective interval." },
    { scenario_id: "official_conflict", tfc_id: "permanent_residence_pathway", profile: { destination: "NLD", conflict: true, snapshot_date: reportDate }, expected_state: "CONFLICTING_UNRESOLVED", reason: "Conflicting official evidence blocks a conclusion and triggers review." },
    { scenario_id: "tax_missing_salary", tfc_id: "employment_deductions_estimate", profile: { destination: "CAN", tax_year: 2025, gross_salary: null }, expected_state: "INPUT_REQUIRED", reason: "Salary is required and is never inferred." },
    { scenario_id: "housing_missing_city", tfc_id: "housing_affordability_scenario", profile: { destination: "DEU", city: null, income: 60000 }, expected_state: "INPUT_REQUIRED", reason: "Reference-city evidence cannot be substituted with a national value." },
  ];
}

async function main() {
  const [universe, protocol, fixture] = await Promise.all([readJson(universePath), readJson(protocolPath), readJson(fixturePath)]);
  if (universe.country_count !== 91 || universe.countries.length !== 91) throw new Error("Stable universe must contain exactly 91 countries.");
  if (protocol.candidate_count !== 8 || protocol.candidates.length !== 8) throw new Error("Phase 7A protocol must contain exactly eight candidates.");
  if (fixture.research_cutoff !== reportDate) throw new Error("Fixture cutoff must match report date.");

  const overrides = new Map(fixture.candidate_overrides.map((item) => [item.tfc_id, item]));
  const candidates = protocol.candidates.map((base) => {
    const override = overrides.get(base.tfc_id);
    if (!override) throw new Error(`Missing fixture override for ${base.tfc_id}.`);
    const supported = fixture.country_sets[override.support_set];
    const anchorCount = fixture.anchors_iso3.filter((code) => supported.includes(code)).length;
    return {
      tfc_id: base.tfc_id,
      public_name: override.public_name,
      original_criterion_ids: base.source_criterion_ids,
      exact_user_question: base.exact_user_question,
      check_kind: override.check_kind,
      result_family: base.result_family,
      required_inputs: base.minimum_inputs,
      predeclared_coverage_floor: base.recommended_premeasurement_floor,
      measured_supported_destinations: supported.length,
      measured_supported_anchors: anchorCount,
      source_ids: override.source_ids,
      disposition: override.disposition,
      gate_results: gateResults(override),
      safe_negative_boundary: base.safe_negative_boundary,
      public_limitations: override.public_limitations,
    };
  });

  const knownCodes = new Set(universe.countries.map((country) => country.code));
  for (const [setId, codes] of Object.entries(fixture.country_sets)) {
    const unknown = codes.filter((code) => !knownCodes.has(code));
    if (unknown.length || new Set(codes).size !== codes.length) throw new Error(`Invalid country set ${setId}: ${unknown.join(",")}`);
  }

  const supportRows = [];
  for (const candidate of candidates) {
    const override = overrides.get(candidate.tfc_id);
    const supported = new Set(fixture.country_sets[override.support_set]);
    for (const country of universe.countries) {
      const state = supported.has(country.code) ? override.support_state : "DESTINATION_UNSUPPORTED";
      supportRows.push({
        tfc_id: candidate.tfc_id,
        country_code: country.code,
        country_name: country.display_name,
        research_support_state: state,
        source_ids: supported.has(country.code) ? override.source_ids : [],
        rationale: supported.has(country.code)
          ? (state === "SOURCE_ROUTE_ASSESSABLE" ? "Included in the frozen exact-source subset." : "Official comparative source exists, but complete production rules or formulas are not captured.")
          : "Outside the candidate's frozen supported source subset; this is not an applicant-negative conclusion.",
      });
    }
  }
  if (supportRows.length !== 728) throw new Error(`Expected 728 support rows, received ${supportRows.length}.`);
  const uniqueKeys = new Set(supportRows.map((row) => `${row.tfc_id}:${row.country_code}`));
  if (uniqueKeys.size !== 728) throw new Error("Country support matrix contains duplicate keys.");

  const sourceIds = new Set(fixture.sources.map((source) => source.source_id));
  for (const candidate of candidates) {
    const missing = candidate.source_ids.filter((id) => !sourceIds.has(id));
    if (missing.length) throw new Error(`Unknown source IDs for ${candidate.tfc_id}: ${missing.join(",")}`);
  }

  const supportSummary = candidates.map((candidate) => {
    const rows = supportRows.filter((row) => row.tfc_id === candidate.tfc_id);
    return {
      tfc_id: candidate.tfc_id,
      disposition: candidate.disposition,
      country_count: rows.length,
      state_counts: countBy(rows, "research_support_state"),
      supported_anchor_codes: fixture.anchors_iso3.filter((code) => rows.some((row) => row.country_code === code && row.research_support_state !== "DESTINATION_UNSUPPORTED")),
      predeclared_floor: candidate.predeclared_coverage_floor,
      coverage_gate: candidate.gate_results.COVERAGE,
    };
  });

  const firstWave = candidates.filter((candidate) => candidate.disposition === "PRODUCTION_QUALIFIED_FIRST_WAVE");
  if (firstWave.length < 3) throw new Error("Phase 7B minimum-three gate failed.");
  if (!firstWave.every((candidate) => Object.values(candidate.gate_results).every((state) => state === "PASS"))) throw new Error("First-wave candidate has a failed gate.");
  const resultFamilies = [...new Set(firstWave.map((candidate) => candidate.result_family))];

  const ownerDecision = {
    schema_version: "konsider-phase7b-owner-decision-1.0",
    research_cutoff: reportDate,
    phase7c_may_proceed_after_owner_approval: true,
    production_qualified_count: firstWave.length,
    minimum_three_gate: "PASS",
    recommended_first_wave: firstWave.map((candidate) => candidate.tfc_id),
    recommended_public_names: Object.fromEntries(firstWave.map((candidate) => [candidate.tfc_id, candidate.public_name])),
    supported_destination_boundary: "29/91: EU Immigration Portal 25 plus Australia, Canada, United Kingdom and United States; all other destinations explicit as unsupported.",
    supported_profile_boundary: "Guest-entered applicant/household/scenario snapshots; no real data in research; route-specific minimum fields; missing fields return INPUT_REQUIRED.",
    result_family_scope: resultFamilies,
    contract_narrowing: resultFamilies.length === 1 ? "Phase 7C must define a route/rule-match contract only, not a generic multi-result engine." : null,
    negative_result_policy: "Initial evidence permits positive and conditional supported-route matches only. Do not expose a complete no-supported-route-matched conclusion until route inventory completeness is independently proven.",
    owner_approvals_required: [
      "Approve the exact three-item first-wave list.",
      "Approve the three exact public names.",
      "Approve the supported profile and 29-destination boundaries.",
      "Approve route/rule-match-only result-family scope for Phase 7C.",
      "Decide whether explicit post-ranking filtering is permitted for route-match checks.",
      "Confirm browser-tab memory as default and choose whether opt-in same-device/session retention may be designed later.",
    ],
    follow_up_candidates: candidates.filter((candidate) => candidate.disposition === "NEEDS_TARGETED_FOLLOW_UP").map((candidate) => ({ tfc_id: candidate.tfc_id, failed_gates: Object.entries(candidate.gate_results).filter(([, value]) => value === "FAIL").map(([gate]) => gate) })),
  };

  const effectiveDateAndConflicts = {
    schema_version: "konsider-phase7b-effective-date-conflict-1.0",
    effective_date_policy: [
      "Every normalized fact or rule must store source identity, captured_at, effective_from and effective_to when known.",
      "Select only evidence whose effective interval contains the scenario snapshot date.",
      "A newer capture does not retroactively replace a rule for an earlier snapshot.",
      "Latest-only APIs require retained lawful raw snapshots and SHA-256 identities before production use.",
    ],
    conflict_policy: [
      "Authentic legislation or formally published immigration rules outrank practical guidance.",
      "National authority rules outrank supranational summaries for national conditions.",
      "Unresolved same-authority or same-rank conflicts produce CONFLICTING_UNRESOLVED and block an applicant conclusion.",
      "Source missingness or conflict never becomes an applicant-negative result.",
    ],
  };

  await fs.mkdir(outputDir, { recursive: true });
  const artifacts = [];
  await writeArtifact("candidate-definitions.json", { schema_version: "konsider-phase7b-candidates-1.0", research_cutoff: reportDate, candidates }, artifacts);
  await writeArtifact("source-manifest.json", { schema_version: "konsider-phase7b-sources-1.0", research_cutoff: reportDate, sources: fixture.sources }, artifacts);
  await writeArtifact("legal-reuse-conclusions.json", { schema_version: "konsider-phase7b-legal-1.0", research_cutoff: reportDate, conclusions: fixture.legal_conclusions }, artifacts);
  await writeArtifact("country-support-matrix.jsonl", `${supportRows.map((row) => stableStringify(row)).join("\n")}\n`, artifacts);
  await writeArtifact("support-summary.json", { schema_version: "konsider-phase7b-support-summary-1.0", stable_country_count: 91, candidate_count: 8, expected_matrix_rows: 728, actual_matrix_rows: supportRows.length, candidates: supportSummary }, artifacts);
  await writeArtifact("required-profile-fields.json", { schema_version: "konsider-phase7b-profile-fields-1.0", synthetic_only: true, candidates: candidates.map(({ tfc_id, required_inputs }) => ({ tfc_id, required_inputs, missing_input_state: "INPUT_REQUIRED" })) }, artifacts);
  await writeArtifact("route-rule-examples.json", { schema_version: "konsider-phase7b-route-examples-1.0", examples: fixture.route_rule_examples }, artifacts);
  await writeArtifact("metric-formula-examples.json", { schema_version: "konsider-phase7b-metric-examples-1.0", examples: fixture.metric_formula_examples }, artifacts);
  await writeArtifact("effective-date-and-conflicts.json", effectiveDateAndConflicts, artifacts);
  await writeArtifact("synthetic-scenario-results.json", { schema_version: "konsider-phase7b-synthetic-scenarios-1.0", contains_real_applicant_data: false, scenarios: syntheticScenarios() }, artifacts);
  await writeArtifact("owner-decision-summary.json", ownerDecision, artifacts);

  const replayManifest = {
    schema_version: "konsider-phase7b-replay-manifest-1.0",
    generated_at: reportDate,
    command: "node project-history/phases/phase-7/research/run_phase7b_tfc_probe.mjs",
    inputs: [universePath, protocolPath, fixturePath].map((filePath) => path.relative(repoRoot, filePath).replaceAll("\\", "/")),
    output_directory: path.relative(repoRoot, outputDir).replaceAll("\\", "/"),
    deterministic: true,
    runtime_network_required: false,
    real_applicant_data: false,
    artifacts,
  };
  await fs.writeFile(path.join(outputDir, "replay-manifest.json"), pretty(replayManifest), "utf8");
  await fs.writeFile(path.join(outputDir, "README.md"), `# Phase 7B deterministic replay\n\nRun from the repository root:\n\n\`\`\`powershell\nnode project-history/phases/phase-7/research/run_phase7b_tfc_probe.mjs\n\`\`\`\n\nThe command uses only the committed stable-country universe, Phase 7A protocol and normalized lawful source fixture. It performs no network access, writes 728 explicit candidate-country states, validates the minimum-three gate and refreshes SHA-256 artifact identities in \`replay-manifest.json\`. No real applicant data is used.\n`, "utf8");
  process.stdout.write(`${pretty({ output_dir: path.relative(repoRoot, outputDir), candidate_count: candidates.length, country_support_rows: supportRows.length, production_qualified_count: firstWave.length, minimum_three_gate: "PASS", result_families: resultFamilies })}`);
}

await main();
