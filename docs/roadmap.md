# Konsider roadmap

Status: worker-first gate reached; product-stack work still requires an explicit next decision

Last updated: 2026-07-20

This roadmap supersedes the fixture-first sequence in `konsider_context.md`. Fixture scores remain
test-only and never fill gaps in a real release.

## Dataset completion gate

Release `2026-07-20.2` is structurally valid and has five of six product-ready criteria across all
20 countries. The gate is therefore green under the defined `>=5` policy. UHC remains criterion-level
blocked because 2021 data fails the three-year freshness rule. Ten material-change warnings from the
previous release are retained for review and do not indicate structural corruption.

A ready criterion must have audited redistribution terms, complete expected attempts and 20-country
coverage, acceptable freshness/type/unit/quality flags, exact record provenance, compatible schemas,
valid artifact and release checksums, versioned parsing/scoring, and reproducible replay.

## Completed worker sequence

1. Audited the fixed 20-country source universe, methodology, reference periods, coverage, freshness,
   and usage terms.
2. Implemented immutable local raw capture, source registrations, exact record provenance, normalized
   observations, explicit attempts, structural validation, criterion readiness, candidate publication,
   and replay.
3. Replaced direct WHO PM2.5 and UHC capture with World Bank-distributed CC BY 4.0 indicators.
4. Retained UNODC-lineage homicide through WDI and narrowed ICP output to broad cost bands.
5. Replaced WPS with the WBL 2026 Legal Framework economy index, renamed “Women’s legal and economic
   equality.”
6. Tested and provisionally admitted an equal-weight WDI infrastructure composite covering internet
   use, fixed broadband, and LPI trade/transport infrastructure quality.
7. Compared threshold, percentile, and winsorized min-max scoring under country-set and tight-cluster
   perturbations; selected fixed, versioned transformations.
8. Published immutable release `2026-07-20.2` only after five criteria passed.

## Immediate stabilization work

- Monitor World Bank/WHO for a post-2021 UHC release; do not waive or silently relax freshness.
- Review the ten material changes caused by source/method transitions and document acceptance before
  any consumer treats changes as trend movements.
- Obtain subject-matter review of the PM2.5, homicide, WBL, and infrastructure anchors.
- Keep infrastructure labelled experimental and reassess its component correlation, mixed-year
  composition, and equal weighting on each refresh.
- Add machine-readable JSON Schemas before another application becomes a release consumer.

## Deferred product sequence

No engine, FastAPI, React, retrieval, agents, chat, MCP, or cloud deployment was implemented in this
worker milestone. If the project explicitly proceeds beyond the gate, the order is:

1. Define the release-consumer contract and framework-free ranking service against one published
   release, excluding non-ready criteria by default.
2. Add API endpoints and contract tests.
3. Add the comparison UI.
4. Add structured evidence lookup and deterministic explanations.
5. Add retrieval only if metadata/lexical lookup proves insufficient.
6. Add LLM chat, typed events, agents, and MCP only after deterministic behavior is proven.
7. Add AWS storage and scheduling adapters after local worker operations remain stable.

## Delivery rules

- Published releases and raw artifacts are immutable; corrections produce new IDs.
- Raw third-party bytes stay out of Git even where redistribution is allowed, unless a later decision
  explicitly changes that conservative policy.
- Missing, stale, incomparable, and rejected data remains explicit; fixture-style scores are forbidden.
- Structural validity and product readiness are separate decisions.
- Passing the aggregate gate never hides a failed individual criterion.
