# Phase 5D — Generic Deterministic Feasibility-Probe Framework

## Intended for
Codex in the local Konsider repository.

## Inputs
- current repository
- Phase 5A and 5B reports
- at least one completed Phase 5C batch

## Objective

Add a small reusable research framework for measuring candidate-source feasibility. It must not modify active releases, production scoring, the API, or the UI.

## Requirements

1. Reuse current audit, raw-artifact, country-registry, and report conventions where practical.
2. Model:
   - criterion and source candidate IDs;
   - publisher and dataset;
   - access and methodology references;
   - licence evidence;
   - source version and retrieval time;
   - raw artifact checksum;
   - country mapping;
   - observation period;
   - presence, freshness, parse, and validation states;
   - blocker and rejection reason codes.
3. Default to the stable 91-country universe.
4. Generate per-country results and summary counts for found, fresh, parsed, valid, missing, stale, invalid, and unmapped observations.
5. Produce Markdown and machine-readable reports.
6. Keep retrieval and parsing source-specific through small plug-ins or adapters.
7. Do not build an AI-agent or web-search orchestration system.
8. Preserve raw artifacts content-addressed and ignored where appropriate.
9. Support offline replay where practical.
10. Test mapping, freshness, counts, reason codes, deterministic output, and non-modification of active release state.
11. Document how to add and run a probe, and the difference between a probe and production ingestion.

Keep the design minimal and prove it with only one or two fixture-backed examples.
