# Change log: review v2.1 → v2.2 (final corrections before UI integration)

v1, v2 and v2.1 files are preserved unchanged. v2.2 = `authoring/review_v2_2.json` → `output/step2/review_v2_2.{json,md}`; no operator interview answers were read; the analysis was not expanded.

| # | Correction | What changed |
|---|---|---|
| F1 | Ranking/count claims computed, not hardcoded | `src/build_review_v2.py` now generates `t_<alias>_<metric>_rank_low/_rank_high` (e.g. "third-lowest") and `t_<alias>_n_terms_exceeding_needed_rate`. P3: enterprise subs/signup is **third-lowest** (was "second-lowest"). P5 and the how-to recommendation: **5** sample terms exceed how-to's required 10.2% (was "four"). P1, P5, P6, observed-vs-explanations and per-term evidence now use computed rank phrases throughout. |
| F2 | Unknown capability ≠ confirmed absence | github, free and enterprise negatives are `pending_confirmation`; each states the product fact that must be *confirmed absent* before the negative becomes actionable and what happens if it is confirmed present. Applied in conditional recommendations (lean, flips_if, both branches) and in the new structured `negative_candidates` (with `confirmation_required`, `becomes_actionable_if`, `does_not_apply_if`). |
| F3 | Signup-only optimisation is a concern to investigate | "Bidding signal" row and the sixth justified-now action rewritten: if the account bids to signups the sample suggests that signal would favour free/github, but the current bidding event, lag and usable signal volume are unknown; confirm the bidding setup first. Method note and P1 adjusted accordingly. |

Additions for the canonical artifact (no new analysis): structured `negative_candidates`, `addition_isolation_candidates` (with landing-page tests and prechecks), per-term `term_missing_information` (each item states what it would change), per-term `term_evidence_notes`, reviewed `term_intent_hypotheses` (v1 texts checked; how-to's "broad match may be pulling adjacent queries" removed per C4; core's "head keyword" framing removed), and ratio-only `channel_context_observations`.

Wording fix: github lean now starts "Cost/sub $822.22 is the second-highest in the sample" (placeholder was at sentence start).
