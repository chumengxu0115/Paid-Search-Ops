# Generator — Recommend Criteria

**Paste this whole file into Claude, in this repo, after you've filled the 6 context files and exported the 5 CSVs.** It produces a populated `criteria.yaml`. (Phase 3 of SETUP.md.)

---

You are filling in `clients/[ACCOUNT_SLUG]/criteria.yaml` for the account whose slug is `[ACCOUNT_SLUG]` (the human running this will tell you the slug; it must match a folder under `clients/` and one under `data-inputs/`).

## What to read

1. `clients/[ACCOUNT_SLUG]/account-context.md`
2. `clients/[ACCOUNT_SLUG]/conversion-goals.md` — **note carefully (a) which conversion is the bidding signal vs the business KPI (they're usually different), and (b) the Strategic Posture section: Efficiency / Scale / Calibration. The posture is what the CPA targets in section B *are* — encode it, don't second-guess it. If the posture box is blank, stop and ask the user to pick one before you set any CPA target.**
3. `clients/[ACCOUNT_SLUG]/benchmarks.md`
4. `clients/[ACCOUNT_SLUG]/current-problems.md`
5. `clients/[ACCOUNT_SLUG]/brand-terms.md`
6. The 5 CSVs in `data-inputs/[ACCOUNT_SLUG]/`: `keyword-report-L6M.csv` (UTF-16, tab-delimited — read with `encoding='utf-16', sep='\t'`), `campaign-report-L6M.csv`, `search-terms-L3M.csv`, `search-terms-L6M.csv`, `asset-association-L3M.csv`. Drop rows whose first cell starts with `Total: `; skip `Source = Unknown` STR rows.
7. The methodology: `diagnose/SKILL.md`, `diagnose/bucket-definitions.md`. And the structure you're filling: `clients/_template/criteria.yaml`.

## What to compute (per criteria.yaml section)

- **A. Spend & signal floors** — from the per-keyword 30d cost distribution (compute it: `Cost / 6` per keyword from the L6M keyword report; report median/p75/p90/p95). Set `spend_min_30d` low enough that you don't park the whole account in Monitor, and set the FFT / Signed-Up signal fallbacks from the actual per-keyword conversion counts.
- **B. CPA targets** — pull the blended bidding-signal and KPI targets straight from `conversion-goals.md` (which already reflects the chosen Strategic Posture — Efficiency targets are low/harsh, Scale targets are high/generous, Calibration means "we'll re-run with a few values"). Do not re-derive the posture; the rationale for `target_fft_cpa_blended` should name the posture explicitly (e.g. "SCALE MODE — …"). Set per-campaign-type targets (brand tighter, competitor looser) from the per-audience table there and from what the campaign names imply — and keep the *ratios* between tiers sane so that if the posture flips next quarter, scaling is a one-line change. Note the CPA-derived gates that move with the target: `is_lost_rank_high_spend_alert`'s $-spend companion (3× target), `both_losing_threshold`'s implied $ line (×target), the new-keyword CPA ceilings (×target), and `pause_threshold_spend_no_fft` (2× target) — set them consistent with the posture. Write `campaign_type_rules` so the substring matches actually catch this account's campaign names (look at the campaign list in the campaign report). Add `custom_tiers` only if `conversion-goals.md`/`benchmarks.md` give confirmed per-geo or per-audience targets — otherwise leave it `[]` and say so in the rationale.
- **C. IS Lost (Rank) gates** — 30% fix-flag / 70% high-spend-alert are sane defaults; tighten the brand override (~20%) if brand runs a defend-share posture. Check the campaign report's IS Lost (Budget) and mention any budget-capped campaigns in the rationale (that's a campaign-level finding, not this keyword-level gate, but worth noting).
- **D. Quality Score gates** — default 4 / 6 / 7 unless the QS-by-spend distribution in `benchmarks.md` says otherwise.
- **E. Cannibalization** — `winner_signal = "fft_cpa"` unless KPI volume per query is genuinely high; `winning_margin` ~0.20; `min_fft_either_side` 1–2 depending on account volume; `both_losing_threshold` ~1.75; `min_combined_spend` scaled to the account.
- **F. New Keyword Suggestions** — the defaults in the template (`new_kw_strict_min_fft: 2`, `new_kw_strict_cpa_ratio: 1.10`, `new_kw_moderate_cpa_ratio: 1.50`, `new_kw_min_query_length_words: 3`, `new_kw_min_cost: 20`, `new_kw_aggressive_min_clicks: 50`, `new_kw_aggressive_min_fft: 1`) are good starting points — keep them unless the data argues otherwise, but still write a rationale that references this account's numbers.
- **G. Bucketing tie-breakers** — `pause_threshold_spend_no_fft` ~2× the bidding-signal CPA target; `dormant_definition` from the bottom of the spend distribution.
- **H. Negative generation** — `negative_min_spend_account_level` scaled to the account; `negative_max_fft_for_neg_candidate` usually 0.

## How to write the file

- Overwrite `clients/[ACCOUNT_SLUG]/criteria.yaml` (starting from `clients/_template/criteria.yaml`'s structure).
- For **every** threshold: set `recommended` to your computed value, `rationale` to a 1–3 sentence explanation that *cites this account's actual numbers* (not generic advice), and `your_value` **equal to `recommended`** (the user edits `your_value` afterward in Phase 4).
- Fill `meta:` — `account_slug`, `reporting_currency` (from `account-context.md`), `generated_by: "recommend-criteria.md"`, `generated_on: <today>`, `posture:` (Efficiency / Scale / Calibration + the review quarter, copied from `conversion-goals.md`), and a `notes:` line capturing the posture and the one or two things that most shaped your numbers (e.g. "SCALE mode; per-keyword spend is tiny → low floors + signal fallback").
- Then print a short summary to the chat: the **posture**, the bidding signal & KPI you used, the headline thresholds, and which sections you had low confidence in (so the user knows where to look in Phase 4). If the posture is Calibration, tell the user to run `run-diagnose.md` 2–3 times with different `target_fft_cpa_blended.your_value`s and compare the Summary-sheet bucket distributions before settling.

## Worked example — "When applied to Client Alpha..." (Q2, **Scale mode**)

Running this on `clients/_example-client-alpha/` produced (see that folder's `criteria.yaml` for the full file):

- **Strategic Posture:** **SCALE** — the region is the company's biggest under-penetrated market and the funnel below clicks converts well (FFT→Paid 26%), so leadership ratified a growth phase at higher CAC for the quarter (review next quarter). This is a deliberate divergence from a profitability-first posture, chosen for this region specifically — and reverting would itself be a strategic decision + sign-off, not a config change. *Everything in section B follows from this.*
- **Bidding signal:** First Free Trial; **KPI:** First Subs. → `B_cpa_targets.target_fft_cpa_blended.your_value = X`, `target_kpi_cpa_blended.your_value = Y` (a profitability-first posture for an account like this would land at a markedly tighter FFT/KPI pair — that figure appears in some rationales as an *illustration of the Efficiency-mode mechanic*, not a parked alternative).
- **Per-keyword spend is extreme-thin** — median 30d cost **$1.06**, only ~13 keywords clear $150/30d. → `spend_min_30d = 50`, `fft_min_for_signal = 1`, `signup_min_for_top_of_funnel = 5` (a "3× target" floor would park ~99% of keywords in Monitor; these floors are data-sufficiency, not posture, so they don't move).
- **Per-campaign-type (Scale mode):** brand `target_fft_cpa` set to the tightest tier (defend-share — only modestly lifted, brand isn't a growth lever) / non_brand at the blended FFT target / competitor modestly above it (the named-competitor auction is contested). `campaign_type_rules` match `"branded"/"brand"` → brand and `"competitor"/"conquest"` → competitor; everything else (PerformanceMax_*, Core Mobile Builder, Database, Use Case, …) → non_brand.
- **IS Lost (Rank):** 30% fix-flag / 70% high-spend-alert (% gates — posture-neutral); **brand override 20%** (defend share). The high-spend-alert's $-spend companion is 3× target under Scale mode. Noted: two branded campaigns currently budget-capped (IS Lost Budget 53% and 23%) — a campaign-level Fix-Budget finding.
- **QS gates:** 4 / 6 / 7 (default — ~80% of QS-tagged spend is QS≥7; posture-neutral).
- **Cannibalization:** `fft_cpa`, margin 0.20, `min_fft_either_side = 2`, `both_losing_threshold = 1.75` (→ implied "kill both" line at 1.75× the FFT target), `min_combined_spend = 100` (bumped with the higher targets).
- **New Keyword Suggestions:** template ratios kept (2 / 1.10 / 1.50 / 3 words / $20 / 50 clicks / 1 FFT); rationales note the $ ceilings move with the target — strict and moderate tiers scale off the FFT target (tighter under Efficiency mode).
- **Tie-breakers:** `pause_threshold_spend_no_fft` set to 2× the FFT target (tighter under Efficiency mode), `dormant_definition = 30` (account-scale, not target-scale).
- **Negatives:** `negative_min_spend_account_level = 100` (raised — Scale mode tolerates more inefficiency), `negative_max_fft_for_neg_candidate = 0`.

Use that as a model for the level of specificity expected — name the posture, ground every rationale in the account's own data, and make the CPA-derived gates visibly consistent with the posture so a future flip is a clean re-derivation, never boilerplate.
