# Paid-Search-Ops

A paid-search decision-support toolkit in two modules: the original keyword-diagnosis workflow and a completed search-term diagnosis with a local review dashboard. Both are built around the same principles (funnel framing, bidding signal vs business KPI, review by spend, thresholds owned by the operator) and both propose actions for human review; neither changes an ad account.

| Module | What it is | Status | Start here |
|---|---|---|---|
| [`keyword-diagnosis/`](keyword-diagnosis/README.md) | Keyword-level diagnosis for Google Ads exports: bucketing with data-sufficiency floors, campaign health, PMax intent clustering, cannibalisation checks. Claude Code skill files with embedded Python; Excel + Word output. | Original workflow (June 2026), moved here unchanged | [`keyword-diagnosis/README.md`](keyword-diagnosis/README.md), [`SETUP.md`](keyword-diagnosis/SETUP.md) |
| [`search-term-diagnosis/`](search-term-diagnosis/README.md) | Search-term diagnosis on a synthetic interview dataset: Python computes and validates metrics, Claude Code authors versioned reasoning, a dependency-free dashboard shows the saved analysis and captures human decisions. | Implemented and tested (49 unit tests, browser self-test) | [`search-term-diagnosis/README.md`](search-term-diagnosis/README.md), [eight-minute walkthrough](search-term-diagnosis/docs/INTERVIEW_WALKTHROUGH.md) |

The intended six-role design (Account Strategist, Campaign, Ad Group, Ad Copy, Keyword Diagnosis, Search-Term Diagnosis) and the honest status of each role are in [`search-term-diagnosis/docs/ARCHITECTURE.md`](search-term-diagnosis/docs/ARCHITECTURE.md). Two roles exist (one per module); four are defined only; there is no orchestration runtime.

## Quick start (search-term dashboard)

```bash
cd search-term-diagnosis
python3 -m http.server 8781 --bind 127.0.0.1     # Python 3.9+, no packages
# open http://127.0.0.1:8781/ui/
python3 -m unittest discover -s tests -v          # 49 cases
```

## Repository history

The repository began as `paid-search-keyword-diagnose` and was renamed. Its original commits are preserved; the keyword files were moved into `keyword-diagnosis/` with `git mv`, and the search-term project was merged in with `git subtree` so its own commit history is retained under `search-term-diagnosis/`.

## Data and claims

`search-term-diagnosis/data/` holds synthetic fixtures supplied for a candidate brief, not real account performance. Nothing in this repository performs live advertising actions, automatic reanalysis, or demonstrates a performance lift.
