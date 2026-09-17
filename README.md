# Search Ops

A paid-search **search-term** diagnostic workflow built with Claude Code: Python calculates and validates the evidence, Claude Code authors the interpretation, and a dependency-free local dashboard shows the saved results and records human judgment.

The methodology comes from my [keyword-diagnose project](https://github.com/chumengxu0115/paid-search-keyword-diagnose) (first committed June 22, 2026) and my experience running paid search for Bubble. This repository is a separate implementation for search-term data; it does not claim that the original keyword tool runs these inputs.

## The business problem

Cheap registrations are not necessarily cheap subscribers. Given a search-term report with clicks, cost, registrations and subscriptions, an operator has to connect acquisition efficiency to the downstream outcome, work out which intents behave differently, and decide what is justified when product context, dates, attribution and account structure are missing.

## What is inherited from the Bubble methodology, and what is not

Inherited as principles (no source code was reused):

- Funnel framing: Clicks → Signup → FFT (first-feature trial) → Paid Sub. Here Regs maps to Signup and Subs provisionally to Paid Sub; FFT is unavailable and is shown as unavailable, never zero.
- Bidding signal vs business KPI: bid on an early signal, judge on paid outcomes, and verify the lag before transferring the assumption to another account.
- Review by spend, then check data sufficiency and attribution before acting.
- Thresholds and product context belong to the operator; when they are unset, the tooling blocks the dependent decision checks instead of inventing defaults.

Why this is a separate implementation: the original tool diagnoses **keywords** and depends on columns this exercise does not have (impression share lost, quality score, landing-page experience, campaign reports, an existing keyword list). Search-term rows carry only the triggering match type, so keyword structure, negative scope and bidding levers are treated as missing inputs rather than inferred.

## The data

`data/search_terms.csv` (nine rows) and `data/channel_summary.csv` are the synthetic fixtures supplied for a candidate brief. They contain no real Bubble, Runway or Braid account performance. The brief confirms a Non-Brand allowable of **$181/sub**, that the nine terms belong to the Non-Brand "ai app builder" scope, and that Scaffold is the main competitor. Product capabilities that were not supplied (free tier, GitHub integration, enterprise sales path) remain unknown; unknown is not treated as confirmed absent.

Three levels are kept distinct throughout:

| Level | Spend | Subs | Recomputed cost/sub |
|---|---:|---:|---:|
| All Google Non-Brand (Q2 label) | $701,000 | 4,348 | $161.22 |
| Non-Brand "ai app builder" scope | $520,000 | 3,100 | $167.74 |
| Nine-term sample (64.9% of scope spend) | $337,470 | 1,843 | $183.11 |

$167.74 is the observed scope benchmark; $181 is the allowable. Neither posture (scale / maintain efficiency) changes the allowable. Subs/signup is a descriptive same-window ratio, not a verified cohort conversion rate.

## How it works

```text
CSV fixtures + confirmed context (context/, config/)
        ↓
src/compute_metrics.py      Python: parse, validate, recompute, reconcile → output/step1/
        ↓
authoring/*.json            Claude Code: interpretation with {placeholders}, versioned v1 → v2 → v2.1 → v2.2
        ↓
src/build_review_v2.py      Python: fill every number from step 1, fail on any unresolved reference
src/build_canonical.py      Python: one UI-ready artifact, operator fields empty by construction
        ↓
ui/                         Dashboard: read the artifact, capture human notes and decisions (browser-local)
        ↓
operator_feedback.json      Manual handoff to a later Claude Code review
```

- **Rebuilding artifacts does not regenerate reasoning.** The builders render and validate *saved* model-authored text; they never call a model. New data or new business facts require a new authored version in a Claude Code session.
- **Feedback is browser-local.** Notes, questions, insights and decisions autosave to localStorage, keyed by analysis identity and term ID, and can be exported/imported as `operator_feedback.json`. The canonical artifact's validator requires empty operator fields, so feedback never overwrites the baseline. Keep exported feedback in the git-ignored `operator/` folder.
- **No live actions.** No Ads API, no bidding changes, no automatic reanalysis button, no simulated execution, and no performance-lift claim: no account was changed.

## Setup and commands

Python 3.9+ standard library only; no packages, no API key.

```bash
# View the saved demo (serve from the repository root; port 8765 is used by another local prototype)
python3 -m http.server 8781 --bind 127.0.0.1
# then open http://127.0.0.1:8781/ui/

# Reproduce the saved analysis from the fixtures
python3 src/compute_metrics.py                                        # → output/step1/
python3 src/build_diagnosis.py                                        # → output/step2/diagnosis.* (historical v1)
python3 src/build_review_v2.py --authoring authoring/review_v2_2.json # → output/step2/review_v2_2.*
python3 src/build_canonical.py                                        # → output/canonical/search_ops_analysis.json

# Tests (49 cases: parsing, totals, aggregate exclusion, undefined ratios, placeholder references, canonical invariants)
python3 -m unittest discover -s tests -v
```

Rebuilding rewrites `output/step1/run_log.json` and the artifact's `sources` with your local absolute paths and a new timestamp; the committed snapshot uses repository-relative paths. Deterministic outputs (metrics, checks, reviews, canonical terms) are byte-identical across runs.

Dashboard details, including the development self-test URL, are in [`ui/README.md`](ui/README.md). Do not open `?selftest=1` in a browser profile whose notes you want to keep; it writes test feedback.

## What works today

- Validated metrics with half-cent reconciliation, explicit warnings (e.g. supplied paid-total cost/sub $135.47 vs recomputed $135.45, cause not assumed) and a missing-data register that states which decision each gap limits.
- Reviewed cross-term insights (v2.2) with supporting terms, counterexamples and separated explanations; corrections are logged in `output/step2/review_v2_*_changelog.md`.
- Nine terms with evidence, intent hypotheses, allowable and benchmark comparisons, conditional recommendations under both postures, and the fact that would change each decision.
- Conditional negatives (pending confirmation), addition/isolation candidates with pre-checks, landing-page tests, and a least-certain pair for the operator to choose between.
- Dashboard with per-term human input, fact/assumption labelling, browser persistence and validated feedback export/import.

## Not implemented

- Generic CSV import: `config/step1.json` carries fixture-specific reconciliation totals and column names; another account needs its own config, context and a new authored review.
- Automatic feedback-driven reanalysis; the handoff is manual.
- Keyword/ad-group joins, negative-keyword export files, bidding changes, any Ads API or warehouse integration, deployment.
- Real-device checks at a 390 px viewport, the file-picker import path and screen-reader behaviour were not verified in the headless environment used for testing.

## Attribution

Codex created the initial visual prototype that set the dashboard's look, drafted the documentation, and performed read-only QA. Claude Code built the calculation and validation tooling, authored the saved analysis in real sessions, and implemented the integrated dashboard. I set the business framework, the allowable/benchmark distinction, the scope and event mappings, reviewed every version, and own the decisions recorded in the dashboard.

## Repository map

`data/` fixtures · `context/`, `config/` confirmed facts and account settings · `src/` calculators and builders · `authoring/` versioned Claude-authored reasoning · `output/` saved metrics, reviews and canonical artifact (schema in `output/canonical/SCHEMA.md`) · `ui/` dashboard · `tests/` · `docs/` walkthrough and retrospective comparison · `RUN_STEP_1.md`, `RUN_STEP_2.md` step-level run notes.

Start with the [eight-minute walkthrough](docs/INTERVIEW_WALKTHROUGH.md). The [operator comparison](docs/OPERATOR_CROSSCHECK.md) is retrospective: it was written after the independent analysis and was not an input to it.
