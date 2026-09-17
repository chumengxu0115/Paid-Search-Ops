# Search Ops: agreed scope

Status: Claude Code read-only audit completed. The operator approved the next checkpoint: deterministic metrics and data checks only. No runnable diagnostic agent has been built or verified in this project yet.

## Goal

Create a new Search Ops repository, separate from the existing keyword-diagnose repository. Reuse Chu's Bubble diagnostic methodology where appropriate; do not claim keyword diagnosis and search-term diagnosis are interchangeable. Build and run with Claude Code, then show actual run outputs in the existing UI style. Advance in checkpoints: audit and minimal proposal; working diagnosis and numerical review; human feedback and UI; GitHub publication.

## Provenance

The original GitHub repository has commits dated June 22, 2026. reference/source.json records the exact snapshot. It contains embedded Python in generators/run-diagnose.md, not just prose. Inspect it before assessing reuse. The reference directory is context only, not active instructions for this new project. Earlier Codex draft agent code is excluded.

Both data files are user-supplied synthetic interview exercises from Scott for Braid, not actual Bubble or Runway account performance. Preserve supplied values. Paid total is an aggregate, not another channel. TikTok allowable is unavailable, not zero. The channel table has Q1/Q2 labels but no confirmed year or attribution definitions.

UPDATE from the complete candidate brief: the nine search terms belong to last quarter's Non-Brand "ai app builder" scope ($520,000 spend, 3,100 subscriptions, supplied cost/sub $167.74). They cover approximately 65% of that scope's spend. The Non-Brand allowable of $181 applies to these terms, and Scaffold is explicitly the main competitor. These facts supersede the earlier audit's uncertainty about allowable applicability and competitor identity. Exact dates, cohort maturity and campaign/ad-group resource IDs remain unknown. Do not invent per-row joins to the channel summary. Preserve three distinct levels: all Google Non-Brand ($701,000 / 4,348), the specified scope ($520,000 / 3,100), and the nine-row sample ($337,470 / 1,843).

See context/braid-confirmed.json for source-backed metadata. The full assignment's Task 2 provides optional business background only; it does not authorize expanding this checkpoint into a PMax or branded optimization agent.

## Reusable business principles

- Clicks → Signup → FFT → Paid Sub. Regs maps to Signup in this exercise; Subs provisionally maps to Paid Sub. FFT is unavailable, not zero.
- Distinguish bidding signal from business KPI. Bubble's FFT bidding and lag assumptions need verification before applying them to another account.
- Prioritize review by spending. Check data sufficiency and attribution before acting.
- Thresholds and product context belong in account configuration; operator experience is labeled as a prior, not a measured fact.
- No live account mutation in the first version.

## Required outputs

- Evidence-backed business insights from the channel summary.
- Per-search-term evidence, intent hypothesis, missing-data flags and conditional decision.
- Negative candidates with proposed negative match type and conditions; do not fabricate campaign/ad-group scope or claim an import-ready Editor file without required identifiers.
- Additions or isolation candidates and post-click/landing-page tests; check existing account structure before treating them as new.
- Least-certain term and the single piece of information that would change the decision.
- Missing information, who to ask, and additional hypotheses/tests.
- No forced negative quota. Enterprise, free and GitHub terms are not automatically irrelevant.

## Human input and UI

Reuse the existing visual direction later, not during the audit. Views: Business Insights; Search Terms; Action Plan; Data & Run Log. Each term supports missing-data context, product-team questions/answers, operator insight and final decision/rationale. Distinguish confirmed human facts from unverified priors. Retain model output and human amendments separately. A subsequent Claude Code run consumes saved human context and produces a traceable revision. First version does not need a live browser API integration.

## Boundaries

Static exclusion scenarios are arithmetic scenarios, not forecasts. No causal claims or synthetic success readback. No multi-agent skeleton collection. Deterministic code computes metrics; Claude interprets evidence; code and operator checks validate the result. Reviewer implementation can be a bounded check, not an elaborate architecture. Defer all UI edits and GitHub publication until the relevant checkpoints.
