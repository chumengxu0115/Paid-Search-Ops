# Data Window Rationale

Why the 6 inputs aren't all on the same date range, and why that's deliberate rather than sloppy.

## The windows

| Input | Window | Why this window |
|---|---|---|
| `keyword-report-L6M.csv` | **L6M** | Per-keyword decisions need a Smart Bidding learning-sized sample. At the median 30-day per-keyword spend most accounts see (often ~$1–$5), a 30- or 90-day window has almost no conversions per keyword — bucketing on it is coin-flipping. Six months smooths week-to-week noise and seasonality and lets QS / IS Lost trends stabilize. Google retains keyword-level data well past 6 months, so L6M costs nothing. |
| `campaign-report-L6M.csv` | **L6M** | Matched to the keyword report so campaign roll-ups reconcile with the keyword rows. Budget / pacing / IS Lost (Budget) trends also want the longer window to be read as trend rather than blip. |
| `search-terms-L3M.csv` | **L3M** | Query behavior changes fast — a query that converted in November may be dead in April. And the PMax "black box" *grows* with time: the share of PMax queries Google actually discloses decays the further back you look. For the action-oriented analyses (New Keyword Suggestions, cannibalization, negative candidates) you want the *freshest* picture, because the output is "do this now". 3 months is also Google's practical retention sweet spot for full STR detail. |
| `search-terms-L6M.csv` | **L6M** | One job only: the **Campaign Health** sheet's campaign-level STR **Source mix** (PMax vs Search vs AI Max vs DSA-legacy) and whether that mix is *drifting*. Source mix is a slow-moving structural property of the account; over 3 months it's too jumpy to trust a "drift" read on. So the health snapshot uses 6 months for *this column specifically* — not for the action analyses. |
| `asset-association-L3M.csv` | **L3M** | You want current-state RSA and PMax assets — what's live and performing *now*, not assets that may have been swapped out months ago. 3 months is also where Google keeps full asset-level detail. |

## The trade-off we're accepting on purpose

Keyword spend is read over L6M; the search-terms cost feeding cannibalization and new-keyword analysis is read over L3M. **These don't perfectly reconcile** — a keyword's L6M cost is not the sum of its L3M search-term costs ×2, and a campaign's L6M keyword spend won't tie out to its L3M STR spend. That's a known, accepted seam, not a bug:

- The keyword-level decisions (bucketing, Fix actions, High-Spend Alerts) are *internally* consistent — all on L6M.
- The query-level decisions (cannibalization, new keywords, negatives, PMax intent) are *internally* consistent — all on L3M.
- The Campaign Health Source-mix column is on L6M and is reported as its own column, not mixed into the L3M analyses.
- Where a number bridges the two (e.g. "Move to PMax" compares an L6M keyword cost to an L3M PMax STR CPA), the diagnose says so in the row's notes rather than pretending the windows align.

Different analyses need different freshness. Forcing one window would either (a) starve the per-keyword analysis of sample (if everything went L3M) or (b) feed stale, partly-undisclosed query data into the action sheets (if everything went L6M). The dual window is the lesser evil, made explicit.
