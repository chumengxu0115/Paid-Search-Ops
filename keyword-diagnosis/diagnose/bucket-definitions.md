# Bucket Definitions

Eight buckets. Every enabled Search keyword lands in exactly one. Thresholds named below are `your_value` fields in `criteria.yaml` (section letters in brackets). "Target CPA" means the campaign-type-specific bidding-signal CPA target unless stated otherwise.

A note that applies to every bucket: **match type is never the trigger and never the fix.** v2 does not recommend promoting/demoting a keyword between broad/phrase/exact, or reclassifying a campaign's match-type strategy — the user explicitly rejected that. Where you might expect "this should be exact", the bucket instead names a real lever (bid, QS, LP, RSA, CPA target) or routes the *query* (not the match type) to PMax or to the New Keyword Suggestions sheet. Each bucket below ends with a one-line "why match type isn't the issue here".

---

## 1. Keep in Search
- **Trigger:** clears spend/signal floors [A]; bidding-signal conversions ≥ `fft_min_for_signal` [A]; CPA ≤ target [B]; IS Lost (Rank) < `is_lost_rank_fix_flag` [C].
- **Sub-causes:** none — it's healthy.
- **Fix Action template:** *"Healthy — converts at $X vs $Y target, IS Lost (Rank) Z%. No action."*
- **Why match type isn't the issue:** it's converting at target with little lost share — whatever match type it's on is working; changing it only adds risk.

## 2. Fix → Keep in Search
- **Trigger:** has signal [A]; **either** CPA ≤ target but IS Lost (Rank) ≥ `is_lost_rank_fix_flag` [C] (→ Fix-Bid), **or** CPA over target with an identifiable lever (→ Fix-QS / Fix-LP / Fix-RSA / Fix-CPA).
- **Sub-causes & Fix Action templates:**
  - **Fix-Bid:** *"Raise tCPA to ~$X — converts at $Y, IS Lost (Rank) Z%. ~$W/mo more conversions available within target."*
  - **Fix-QS:** *"QS=N (weakest sub-component: <Exp. CTR | LP exp. | Ad relevance>). Improve <that> before bidding up — bidding into a low-QS keyword overpays."*
  - **Fix-LP:** *"Landing page exp. = Below average. Route to a page about “<keyword theme>” instead of the generic LP; re-check QS in 2 weeks."*
  - **Fix-RSA:** *"Ad-group RSA CTR <a%> vs account <b%> (and/or RSA CPA $c vs $d). Refresh headlines/descriptions for this ad group."*
  - **Fix-CPA:** *"Converts at $X vs $Y target with no QS/LP/RSA lever. Lower tCPA to $Y (expect ~Z% fewer conversions) — or move the query to PMax if PMax serves it at/under target."*
- **Why match type isn't the issue:** the gap is a price (bid/tCPA), a quality (QS/LP/RSA), or a target-realism (Fix-CPA) problem — none of which a match-type change addresses; broadening match would add more of the same mispriced traffic, narrowing it just hides volume.

## 3. Fix → Decide (watchlist)
- **Trigger:** has signal [A] but the verdict is ambiguous — CPA mildly over target (between target and `both_losing_threshold`-ish region [E]/[B]), or QS in the watchlist band `qs_watchlist` [D], or signals conflict (good CPA but falling, or thin conversion count just over `fft_min_for_signal`).
- **Sub-causes:** same menu as Fix → Keep, but not confident enough to prescribe — the row carries the *candidate* lever plus "watch one more cycle / needs a human call."
- **Fix Action template:** *"Borderline: converts at $X (target $Y), QS=N, IS Lost Z%. Likely lever: <sub-cause>. Decide after next data refresh or with account context the data can't see."*
- **Why match type isn't the issue:** the uncertainty is about *whether* and *which* lever, not about match type — which would be a guess on top of a guess.

## 4. Move to PMax
- **Trigger:** has signal [A]; CPA over target [B] (often well over, ≥ `both_losing_threshold` × target [E]); the keyword/query is broad or long-tail (4+ words is a common cut, but it's the *nature* of the intent that matters); and PMax already serves the same intent at/under target (evidenced in `search-terms-L3M.csv`, `Source = Performance Max`).
- **Sub-causes:** n/a — the recommendation is structural: stop paying Search prices for intent PMax converts more cheaply.
- **Fix Action template:** *"Spends $X/mo at $Y CPA (target $Z). PMax serves this intent at $W. Move: pause/lower this keyword and add it as a Search negative so PMax owns the query."*
- **Why match type isn't the issue:** the problem is *channel*, not match type — the same intent is cheaper in PMax regardless of how you'd match it in Search.

## 5. Pause
- **Trigger:** spent ≥ `pause_threshold_spend_no_fft` [G] with **zero** bidding-signal conversions in the window (and not dormant per `dormant_definition` [G] — dormant ones go to Monitor (low data), not Pause).
- **Sub-causes:** n/a.
- **Fix Action template:** *"Spent $X over the window, 0 <bidding-signal> conversions. Pause (or strip to a hard daily cap and watch). Check the search-terms it triggered for a negative list."*
- **Why match type isn't the issue:** zero conversions on real spend means the intent doesn't pay, full stop — broadening or narrowing match changes the volume of waste, not the fact of it.

## 6. Monitor — has signal (top-of-funnel only)
- **Trigger:** below `spend_min_30d` and below `fft_min_for_signal` [A], **but** clears `signup_min_for_top_of_funnel` [A] on the top-of-funnel proxy conversion.
- **Sub-causes:** n/a — too little money/signal to act, but it's *doing something*.
- **Fix Action template:** *"Thin spend ($X/30d) but N <top-of-funnel> events. Hold; re-check next run. Don't bid up — let it accumulate."*
- **Why match type isn't the issue:** there isn't enough data to justify *any* change, match type included.

## 7. Monitor — low data
- **Trigger:** below `spend_min_30d` AND below all signal floors [A] (and/or below `dormant_definition` [G] with no conversions — i.e. dormant).
- **Sub-causes:** n/a.
- **Fix Action template:** *"$X/30d, no meaningful signal. Hold. Excluded from High-Spend Alerts and Fix logic. Consider cleanup only if the account has hundreds of these."*
- **Why match type isn't the issue:** nothing to diagnose yet.

## 8. (the eighth) — High-Spend Alert is an overlay, not a bucket
High-Spend Alerts is a *cross-cut*, not a mutually-exclusive bucket: any keyword (usually a Fix → Keep / Fix-CPA or a Move-to-PMax) that spends ≥ `is_lost_rank_high_spend_alert`'s spend companion AND has IS Lost (Rank) ≥ `is_lost_rank_high_spend_alert` [C] appears *additionally* on the High-Spend Alerts sheet. Counting the mutually-exclusive set — Keep, Fix→Keep, Fix→Decide, Move to PMax, Pause, Monitor(has signal), Monitor(low data) — that's 7; the High-Spend Alert overlay is the 8th named output (and `reading-the-output.md` lists it as its own sheet). If you prefer a clean 8 mutually-exclusive buckets, split Monitor into its two members and count: Keep / Fix→Keep / Fix→Decide / Move-to-PMax / Pause / Monitor-has-signal / Monitor-low-data — that's 7 — plus the rarely-needed **Just-launched (hold 30d)** transient state used for keywords whose campaign launched inside the window = 8. The diagnose emits whichever of these are non-empty.

---

## Sub-cause priority order (when a keyword could be flagged for more than one)
1. Fix-QS (a low-QS keyword overpays on everything else) →
2. Fix-LP (often the cause of low QS; fix it first) →
3. Fix-RSA →
4. Fix-Bid (only bid up once quality is sane) →
5. Fix-CPA / Move-to-PMax (if after the above the target still isn't reachable).

The Fix Action shown is the top-priority applicable sub-cause; the row also lists secondary sub-causes in a notes column.
