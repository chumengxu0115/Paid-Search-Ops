# paid-search-keyword-diagnose

## What this project does

This tool takes a Google Ads account's exported reports and produces a **per-keyword diagnosis**: every enabled Search keyword is placed into one of 8 buckets (Keep / Fix→Keep / Fix→Decide / Move to PMax / Pause / Monitor×3), each Fix keyword gets a **concrete, account-specific Fix instruction** (e.g. "Raise tCPA to ~$140 — converts at $128, IS Lost (Rank) 74%", not "consider lifting bids"), and the whole account gets a **campaign health snapshot** plus PMax intent clustering, PMax↔Search cannibalization, and new-keyword suggestions. It is deliberately **narrow**: it diagnoses keywords and surfaces campaign health. It is **not** an account-level strategy SOP, an audience-segmentation framework, an ad-copy generator, or a campaign-structure planner.

## Output format

Two files per run, written to `output/[account-slug]/[date]/`:

- **`insights.docx`** — a ~4-page Word report: account at a glance (4 metrics), 5 data-driven key findings, data health & open questions. Narrative, not an action plan.
- **`keyword-diagnose.xlsx`** — a workbook of ~14 sheets with conditional formatting: Summary, Campaign Health, PMax Intent, High-Spend Alerts, Fix→Keep in Search, Keep in Search, Move to PMax, Fix→Decide, Monitor (has signal), Monitor (low data), Pause, New Keyword Suggestions, PMax-Search Cannibalization. The Excel is the working artifact; the Doc is the read.

## Quick start

See **[SETUP.md](SETUP.md)** — copy the client template, export 6 Google Ads reports (note the **dual search-terms window**: L3M *and* L6M), run `generators/recommend-criteria.md` to draft `criteria.yaml`, review/edit it, then run `generators/run-diagnose.md`.

## Design principles

**a) Excel-first output.** Emits a workbook you can sort, filter, and hand to a media buyer, plus a short Word narrative. No long-form Markdown deliverables.

**b) Per-keyword actionable Fix instructions (not abstract advice).** Every Fix→Keep keyword gets a templated instruction populated with that keyword's own numbers: the tCPA to set, what it converts at, its IS Lost, its QS sub-components, its landing page. "Lift bid" is not an output; "Raise tCPA to ~$X" is.

**c) yaml-driven criteria (the user owns the thresholds).** All decision boundaries live in `clients/[slug]/criteria.yaml`. The AI fills `recommended` + `rationale` per threshold (read-only); the user edits `your_value` only. Re-running the diagnosis with a different `your_value` is the supported way to explore "what if I'm stricter on CPA".

**d) Universal across accounts (brand / non-brand / competitor segmentation).** Nothing is client-specific in the methodology. Campaign type is inferred per campaign from name-matching rules in `criteria.yaml` (`campaign_type_rules`), and CPA targets, IS Lost gates, and bucket tie-breakers all support per-campaign-type overrides. The `_example-client-alpha/` client is a worked example, not a dependency.

## What's deferred (explicitly out of scope)

**Match Type promote/demote recommendations.** This project says nothing about whether a keyword "should be" exact vs phrase. Match Type promote/demote is noisy, account-structure-dependent, and not what people come to a keyword diagnosis for. `bucket-definitions.md` documents *why match type is not the issue* for each bucket so the diagnosis doesn't backslide into it. The **New Keyword Suggestions** sheet (3 tiers) suggests *queries to add as keywords*, never a match-type change to an existing one.

Also out of scope: audience segmentation framework, ad-copy / RSA frameworks, campaign-structure planner, competitor-mapping SOP, AI Max pinning logic.

## About the example

The `_example-client-alpha/` client folder is a worked example based on anonymized aggregate data from a real SaaS paid-search account. All specific numbers, keyword lists, and strategic CPA targets have been genericized for this public release. The example demonstrates the methodology, not actual client performance.
