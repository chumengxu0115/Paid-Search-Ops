# CLAUDE.md — keyword-diagnose-v2

Guidance for Claude working in this repo.

## What this repo is

A focused tool: ingest 6 Google Ads exports → emit `insights.docx` + `keyword-diagnose.xlsx`. Per-keyword bucketing, per-keyword actionable Fix instructions, campaign health snapshot, PMax intent clustering, PMax↔Search cannibalization, new-keyword suggestions. Nothing else.

## What this repo is NOT (do not add these back)

- Not an account-level strategy SOP. (The predecessor `../keyword-diagnose/` drifted into this — it's deprecated; don't mine it for "missing" features.)
- Not an audience-segmentation, ad-copy/RSA, campaign-structure, or competitor-mapping framework.
- **No Match Type promote/demote logic.** The user explicitly rejected it. The diagnosis never tells anyone to "graduate broad → exact" or reclassify a campaign's match-type strategy. `diagnose/bucket-definitions.md` documents *why match type is not the issue* per bucket so this doesn't creep back in. The only "new keyword" output is the New Keyword Suggestions sheet — it suggests *queries to add*, never a match-type change.

## Repo map

- `README.md`, `SETUP.md` — overview + the 5-phase workflow.
- `clients/_template/` — the 6 files a new account fills (`account-context.md`, `conversion-goals.md`, `benchmarks.md`, `current-problems.md`, `brand-terms.md`, `criteria.yaml`).
- `clients/_example-client-alpha/` — a fully worked example. Reference for what good context looks like and for the criteria.yaml structure.
- `data-inputs/_template/README.md` — the 6 expected CSV files, their schemas, and export gotchas. Real exports go under `data-inputs/[slug]/` (gitignored).
- `diagnose/` — the methodology: `SKILL.md` (core logic), `bucket-definitions.md`, `pmax-intent-clustering.md`, `data-window-rationale.md`, `reading-the-output.md`.
- `generators/` — standalone Claude prompts: `recommend-criteria.md` (fills criteria.yaml), `run-diagnose.md` (produces the Excel + Word; embeds the full Python).
- `examples/client-alpha-q2/` — placeholder output files; regenerate with `run-diagnose.md`.

## Conventions

- **Criteria flow:** AI writes `recommended` + `rationale` (read-only to the user); user edits `your_value` only; the diagnosis reads `your_value` exclusively. Never have the diagnosis fall back to `recommended` silently — if `your_value` is missing, that's an error to surface.
- **Strategic posture drives CPA targets:** `conversion-goals.md` has a Strategic Posture section (Efficiency / Scale / Calibration). The CPA targets in `criteria.yaml` section B *are* that posture as numbers — Efficiency = low/harsh, Scale = high/generous, Calibration = re-run with a few values and compare bucket distributions. `criteria.yaml` carries `meta.posture`; the generators surface it. The CPA-derived gates (high-spend-alert $-companion = 3× target, cannibalization both-losing line = ×target, new-keyword ceilings = ×target, pause threshold = 2× target) scale with the target so a *deliberate* posture change is a clean re-derivation — but changing posture is a strategic decision with sign-off (LTV economics, growth mandate, cash position), not just editing a number. The client-alpha example runs in **Scale mode** (FFT $X / Subs $Y) — that's its standing posture, not a draft; don't "correct" it down to $110. Where rationales mention ~$110 / ~$330 they're illustrating the Efficiency-mode mechanic (what the same gates compute against a tighter target), not naming a parked alternative. The "$50/$175 US default" reference from early prompts is *not validated* — don't reintroduce it; use a generic illustrative example instead.
- **Campaign type** (brand / non_brand / competitor) is inferred per campaign from `criteria.yaml` → `campaign_type_rules` (substring match on campaign name; everything unmatched is `non_brand`). All CPA targets, IS Lost gates, and bucket tie-breakers support per-campaign-type overrides.
- **Data windows:** keyword + campaign = L6M; search terms = pulled at BOTH L3M and L6M (L3M for actions, L6M for the campaign-health Source mix); asset association = L3M. See `diagnose/data-window-rationale.md`. Don't "simplify" to one window.
- **Bidding signal vs business KPI:** these are usually different conversion actions (e.g. First Free Trial is what Smart Bidding optimizes; First Subs is the revenue metric). Bucketing weighs against the bidding signal where volume is thin and against the KPI where volume allows. Keep them distinct everywhere.
- **Data hygiene:** strip "Total: ..." aggregate rows; skip `Source = Unknown` STR rows (data-quality artifact); the keyword report is UTF-16 LE tab-delimited (read with `encoding='utf-16'`, `sep='\t'`).

## When asked to extend

- New PMax intent cluster → edit `diagnose/pmax-intent-clustering.md` (it's designed to be extended per account).
- New threshold → add it to `clients/_template/criteria.yaml` AND `clients/_example-client-alpha/criteria.yaml` AND wire it in `generators/run-diagnose.md`; document it in `diagnose/bucket-definitions.md` or `reading-the-output.md`.
- "Can you add match-type recommendations" → no; explain it was explicitly deferred (see README "What's deferred").
