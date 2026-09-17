# SKILL — keyword-diagnose

The core diagnostic logic. The two generators (`recommend-criteria.md`, `run-diagnose.md`) are the executable wrappers; this file is the spec they implement.

## 1. Overview — what the diagnose does

Given 6 Google Ads exports and a filled `criteria.yaml`, the diagnose:

1. **Buckets every enabled Search keyword** into one of 8 buckets (see `bucket-definitions.md`): Keep · Fix → Keep · Fix → Decide · Move to PMax · Pause · Monitor (has signal) · Monitor (low data) · (Monitor is the family; "has signal" and "low data" are its two members — counting "Keep / Fix→Keep / Fix→Decide / Move to PMax / Pause / Monitor×3" gives 8).
2. **Attaches an actionable Fix Action** to every Fix → Keep keyword — a templated instruction populated with that keyword's own numbers (the tCPA to set, what it converts at, its IS Lost, its QS sub-components, its landing page).
3. **Surfaces campaign health** for every campaign (Search and PMax): type, channel, status, spend, bidding-signal conversions + CPA, IS Lost, top issue, recommended action, and an STR signal column (for PMax: visible-query % + top intent cluster; for Search: STR Source mix).
4. **Clusters PMax search terms** into intent clusters (see `pmax-intent-clustering.md`) so the PMax black box becomes legible.
5. **Identifies PMax↔Search cannibalization** — queries converting on both channels — and picks a winner (or "kill both").
6. **Suggests new keywords** — queries (mostly from PMax/AI Max) good enough to add as Search keywords, in 3 confidence tiers. This is the *only* "what to add" output; it never recommends match-type changes to existing keywords.

It does **not**: recommend match-type promotion/demotion, design campaign structure, segment audiences, write ad copy, or map competitors. (Those lived in the deprecated `../keyword-diagnose/`.)

## 2. Input contract — 6 files

All paths relative to `data-inputs/[account-slug]/`. Schemas in `../data-inputs/_template/README.md`.

| # | File | Window | Encoding | Key columns | Used for |
|---|---|---|---|---|---|
| 1 | `keyword-report-L6M.csv` | L6M | UTF-16, tab | Keyword, Match type, Campaign, Ad group, Status, Cost, Impr., Clicks, Max CPC, Search lost IS (rank), QS + Exp.CTR + LP exp. + Ad relevance, all conv actions | keyword bucketing, Fix actions |
| 2 | `campaign-report-L6M.csv` | L6M | UTF-8 | Campaign, Campaign type, Campaign status, Cost, all conv actions, Search lost IS (rank), **Search lost IS (budget)**, Budget | campaign health, budget-constrained flag |
| 3 | `search-terms-L3M.csv` | L3M | UTF-8 | Search term, Match type, Campaign, Ad group, **Source**, Clicks, Impr., Cost, all conv actions | PMax intent clustering, New Keyword Suggestions, cannibalization, negatives |
| 4 | `search-terms-L6M.csv` | L6M | UTF-8 | (same as #3) | Campaign Health Source mix + drift only |
| 5 | `asset-association-L3M.csv` | L3M | UTF-8 | **Level** (Ad/Asset group/Campaign), Campaign, Ad group, Asset, Asset type, Impr., Clicks, Cost, conv actions | RSA-asset and PMax-asset signal for Fix-RSA + campaign health |
| 6 | `brand-terms.md` | — | — | Markdown list | brand/non-brand/competitor classification; exclusions from negatives & new-keyword suggestions |

Hygiene applied on load: drop rows whose first cell starts with `Total: `; drop `Source = Unknown` STR rows; coerce money/number columns; normalize conversion column names against `conversion-goals.md`.

## 3. Output contract

`output/[account-slug]/[date]/`:
- **`keyword-diagnose.xlsx`** — ~14 sheets (Summary + the 13 listed in `reading-the-output.md`), with conditional formatting on the CPA-ratio and IS-Lost columns.
- **`insights.docx`** — ~4 pages: Account at a glance (4 metrics) · 5 data-driven key findings · Data health & open questions.

(Doc is narrative; Excel is the working artifact. Doc has no action plan — actions live in the Excel Fix sheets.)

## 4. Bucketing logic

See `bucket-definitions.md` for the full trigger table. Sketch:

1. **Classify** the keyword's campaign type from `criteria.yaml → campaign_type_rules` (brand / non_brand / competitor / custom tier). This selects the CPA target and IS-Lost gate to use.
2. **Signal check:** does the keyword clear `spend_min_30d` OR `fft_min_for_signal`? If not → **Monitor (low data)** (or **Monitor (has signal)** if it clears `signup_min_for_top_of_funnel` on the top-of-funnel proxy).
3. **Pause check:** spent ≥ `pause_threshold_spend_no_fft` with zero bidding-signal conversions → **Pause**.
4. **Health check** (has signal, converting): bidding-signal CPA vs the campaign-type target.
   - At/under target, IS Lost (Rank) under `is_lost_rank_fix_flag` → **Keep**.
   - At/under target but IS Lost (Rank) ≥ `is_lost_rank_fix_flag` → **Fix → Keep** (sub-cause Fix-Bid: you can afford more share).
   - Over target → look for a fixable cause (QS, LP, RSA, bid/tCPA) → **Fix → Keep** with the relevant sub-cause; if the only lever is a deep CPA cut → **Fix → Keep** (Fix-CPA) or, if the query is broad/long and PMax already serves it well, **Move to PMax**.
   - Over target and *also* high-spend + high IS-Lost-Rank → also listed on **High-Spend Alerts**.
   - Ambiguous (mild over-target, mixed signals, watchlist QS) → **Fix → Decide**.

## 5. Per-bucket diagnostic priorities (sub-causes)

For Fix buckets, the sub-cause determines the Fix Action template:

- **Pause** — spending without converting; no fix worth attempting; recommend pause / heavy de-prioritization.
- **Fix-Bid** — converting at/under target but IS Lost (Rank) high → raise tCPA / bid to capture affordable share. Template: *"Raise tCPA to ~$X — converts at $Y, IS Lost (Rank) Z%."*
- **Fix-QS** — QS ≤ `qs_severe` (or in watchlist with a clear weak sub-component): name the weakest of Exp. CTR / Landing page exp. / Ad relevance. Template: *"QS=N (weak: <sub-component>). Fix <sub-component> before bidding up."*
- **Fix-LP** — Landing page exp. is "Below average" and the LP is shared/generic → recommend a tighter landing page. Template: *"LP exp. Below average — point to a page about <keyword theme>, not the generic LP."*
- **Fix-RSA** — ad-group RSAs underperform account CTR/CPA (from `asset-association-L3M.csv`, Level=Ad) → refresh assets. Template: *"Ad-group RSA CTR <x%> vs account <y%> — refresh headlines."*
- **Fix-CPA** — converts, but over target with no QS/LP/RSA lever → lower tCPA to target and accept the volume hit, or move to PMax. Template: *"Converts at $X vs $Y target — drop tCPA to $Y (expect ~Z% fewer conversions) or move to PMax."*
- **Keep** — healthy; no action; included so the sheet is exhaustive.
- **Move to PMax** — long/broad query, hemorrhaging in Search, and PMax serves the same intent at/under target → fold into PMax, add as Search negative. Template: *"Spends $X at $Y CPA (target $Z); PMax serves this intent at $W — move to PMax, negative in Search."*
- **Monitor (has signal)** — top-of-funnel proxy fires but not enough bidding-signal volume → hold, re-check next run.
- **Monitor (low data)** — below spend & signal floors → hold; excluded from alerts and most fixes.

## 6. PMax intent clustering

`search-terms-L3M.csv` rows with `Source = Performance Max` are matched against the cluster keyword lists in `pmax-intent-clustering.md`. Each query → one cluster (first match wins; unmatched → "Other / unclassified"). Per PMax campaign the diagnose reports: visible query % (a black-box honesty signal — Google doesn't disclose every PMax query), top 3 clusters by spend, and top converting cluster. Clusters are **extensible per account** by editing that file.

## 7. Dual window rationale

Keyword + campaign data = L6M (stable learning sample, stable QS/IS trends). Search terms = L3M **and** L6M — L3M for action-oriented analyses (fresh query behavior; PMax disclosure decays with age), L6M for the Campaign Health Source-mix snapshot (slow-moving structural signal needs the longer window to be stable). Asset association = L3M (current-state assets). Full reasoning + the acknowledged keyword-spend-vs-STR-cost misalignment trade-off: `data-window-rationale.md`.
