# Reading the Output

A sheet-by-sheet guide to `keyword-diagnose.xlsx` (~14 sheets) and `insights.docx` (~4 pages). ⭐ marks the sheets that are new or central in v2.

## How to read it (in order)
1. **Insights Doc** first — the 5 key findings tell you where to look.
2. **Summary** sheet — bucket distribution + spend-at-stake by bucket.
3. **⭐ Campaign Health** — the account-shape view; tells you whether the problem is a few keywords or a structural campaign issue.
4. **🔴 High-Spend Alerts** — the "stop the bleeding today" list.
5. **⭐ Fix → Keep in Search** — the bulk of the actionable work, one row per keyword with a populated Fix instruction.
6. Everything else as needed.

---

## Excel sheets

### 1. Summary
Account at a glance (spend, bidding-signal conversions + CPA, KPI conversions + CPA, blended CTR — all over the window). Bucket distribution table: count of keywords and **% of Search spend** in each bucket (the spend column is the one that matters — 400 Monitor keywords spending $300 total is fine; 3 Pause keywords spending $40k isn't). Key findings list (mirrors the Doc). A "data health" mini-block: which `[VERIFY]` context values were used, what % of PMax queries were visible, how many rows were dropped as Totals/Unknown.

### 2. ⭐ Campaign Health
One row per campaign (Search and PMax — typically 15–30 rows). Columns: Campaign · Type (brand/non_brand/competitor/custom) · Channel (Search/PMax/AI Max/DSA) · Status · Spend · bidding-signal conversions · bidding-signal CPA · IS Lost (Rank) · IS Lost (Budget) · Top Issue · Recommended Action · **STR Signal** — for PMax: "*N% queries visible · top intent: <cluster>*" (the visible-% honesty signal from the L3M STR); for Search: "*Source mix: keyword X% / PMax Y% / AI Max Z%*" (from the L6M STR) with a drift note if the mix moved. This is where you see "6 of 15 Search campaigns are stalled" or "PMax is 80% one intent cluster" at a glance.

### 3. ⭐ PMax Intent
Per PMax campaign, the full intent-cluster breakdown (from `pmax-intent-clustering.md`): each cluster's spend, clicks, bidding-signal conversions, CPA, and share of the campaign; the visible-query % header; the top converting cluster called out. Use it to decide PMax negatives, whether a cluster deserves its own Search campaign, and whether PMax is mostly serving hype/off-target traffic (CTR dilution).

### 4. 🔴 High-Spend Alerts
The triage sheet: keywords spending ≥ 3× the bidding-signal CPA target (the spend companion of `is_lost_rank_high_spend_alert`) **AND** with IS Lost (Rank) ≥ `is_lost_rank_high_spend_alert`. These are keywords pouring money into an auction they're mostly losing — either the tCPA is unrealistic for the position they want, or the intent doesn't pay. Each row carries its bucket and its Fix Action. Empty sheet = good news.

### 5. ⭐ Fix → Keep in Search
One row per Fix→Keep keyword: Keyword · Match type (informational — never an action) · Campaign · Type · Spend · bidding-signal conv · CPA · CPA/target ratio · IS Lost (Rank) · QS + the three sub-components · Landing page exp. · Ad relevance · **Sub-cause** (Fix-Bid/QS/LP/RSA/CPA) · **Fix Action** (the populated instruction, e.g. *"Raise tCPA to ~$140 — converts at $128, IS Lost (Rank) 74%"*) · secondary sub-causes. Sorted by spend descending. Conditional formatting reds the CPA/target ratio and IS-Lost cells.

### 6. Keep in Search
Healthy keywords — converting at/under target with low lost share. One row each, no Fix Action (just "Healthy — no action"). Here for completeness so the workbook accounts for every keyword; also useful as a "what good looks like" reference.

### 7. Move to PMax
Hemorrhage candidates: broad/long-tail keywords spending well over target in Search where PMax already serves the same intent at/under target. Columns include the PMax-side CPA evidence and the Fix Action ("Move: pause/lower, add Search negative").

### 8. Fix → Decide (watchlist)
Ambiguous keywords — mildly over target, watchlist-band QS, or conflicting signals. Carries the *candidate* lever and "decide after next refresh / needs human context". The sheet you bring to a review call.

### 9. Monitor (has signal)
Low-spend keywords that fire the top-of-funnel proxy conversion but not enough of the bidding signal to judge. Hold, re-check next run.

### 10. Monitor (low data)
Below spend and signal floors (and dormant keywords). Excluded from alerts and Fix logic. Skim only if the account has hundreds of these and you want to cleanup.

### 11. Pause
Keywords that spent ≥ `pause_threshold_spend_no_fft` with zero bidding-signal conversions. Each row: spend, the search terms it triggered (for a negative list), Fix Action ("Pause / hard-cap").

### 12. ⭐ New Keyword Suggestions
Queries (mostly `Source = Performance Max` / AI Max, some `Source = Search keyword` close-variants) good enough to add as Search keywords — **not** match-type changes to existing keywords. Three tiers (see `../generators/run-diagnose.md` for the exact gates): **Strict** (≥`new_kw_strict_min_fft` bidding-signal conv, CPA ≤ target ×`new_kw_strict_cpa_ratio`, not already a Search exact/phrase), **Moderate** (same but CPA ≤ target ×`new_kw_moderate_cpa_ratio`), **Aggressive** (no conversions but ≥`new_kw_aggressive_min_clicks` clicks and a close variant of an existing Search keyword). Excludes: `Source = Unknown`, brand terms, queries < `new_kw_min_query_length_words` words, queries with < $`new_kw_min_cost` spend. Columns: Query · Source · Suggested match type (a suggestion for the *new* keyword, not a reclassification) · Tier · clicks/cost/conv/CPA · the existing keyword it's a variant of (Aggressive tier) · suggested destination campaign. This sheet replaces the deprecated "PMax → Search Graduation" sheet — narrower scope, no match-type-strategy claims.

### 13. ⭐ PMax-Search Cannibalization
Queries converting on both PMax and Search (from L3M STR). Columns: Query · PMax spend/conv/CPA · Search spend/conv/CPA · Winner (per `cannibalization_winner_signal`, must beat the loser by `winning_margin`) · Verdict — "let PMax own it (negative in Search)" / "let Search own it (PMax negative or exclusion)" / "no clear winner — monitor" / "both losing — kill on both". Gated by `min_fft_either_side`, `min_combined_spend`, `both_losing_threshold`.

### (14) Summary is sheet 1; counting Summary + the 13 above = 14 sheets. Empty sheets are still emitted as empty (with a header note) so the workbook shape is stable run-to-run.

---

## Word Insights Doc (~4 pages)

**Page 1 — Account at a glance.** Four metrics, no more: total Search spend (window), bidding-signal conversions + CPA vs target, KPI conversions + CPA vs target, blended Search CTR vs benchmark. A one-line account verdict.

**Pages 2–3 — Five key findings.** Data-driven, not an action plan — each finding is "here's what the data shows and why it matters", with the numbers behind it. (Actions live in the Excel Fix sheets; the Doc points at them but doesn't list them.) Findings are ranked by spend-at-stake. Typical findings: a Pause/High-Spend cluster, a campaign-health structural issue, a PMax-intent observation (incl. visible-% caveat), a cannibalization pattern, a CTR/QS pattern.

**Page 4 — Data health & open questions.** Which `[VERIFY]` context values were taken on faith and how that limits confidence; PMax visible-query %; window-misalignment caveats that affected any finding; the 2–3 questions a human needs to answer that no export can ("is the EU pricing localized?", "is consent mode v2 on?") — surfaced, not guessed.
