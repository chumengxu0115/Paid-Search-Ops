# Search Ops architecture: six paid-search roles

Status of this document: **role definitions and a proposed workflow**. One role (Search-Term Diagnosis) is implemented in this repository; one (Keyword Diagnosis) exists as a separate earlier project; the other four are defined here and not built. There is no orchestration runtime and no multi-agent execution has taken place.

Architectural inspiration: [GrowthOS](https://github.com/scottjs12/GrowthOS) by Scott Schmidt, in particular its two-layer split between universal methodology and swappable client context, explicit "owns / does not own" boundaries per role, input and output specs, and written handoffs between roles. Search Ops narrows those ideas to a single function (paid search) and to a human-approved, non-executing system.

## Two layers, one source of truth each

| Layer | What it holds | Where it lives | Rule |
|---|---|---|---|
| Reusable methodology (Bubble-informed) | Funnel framing (Clicks → Signup → FFT → Paid Sub), bidding signal vs business KPI, review by spend, data-sufficiency before action, thresholds owned by the operator | `README.md` (principles), `config/account_context.json → methodology_priors`, the original keyword workflow in [`../../keyword-diagnosis/`](../../keyword-diagnosis/README.md) | Labelled as priors; never treated as facts about the current account |
| Account context (Braid, simulated exercise) | Confirmed facts from the brief, scope levels, allowable, event mappings, unknown product capabilities, fixtures | `context/BRIEF.md`, `context/braid-confirmed.json`, `config/account_context.json`, `config/step1.json`, `data/` | Referenced, not duplicated; unknown fields stay `unknown`, never filled by inference |

Every role reads the same context files. A role may add to its own outputs; it may not rewrite the context layer. Changing a confirmed fact is a human edit to the context files followed by a new authored version.

## Shared conventions (all roles)

- **Facts vs hypotheses vs to-confirm** are labelled in every output (as in `output/canonical/search_ops_analysis.json`).
- **Missing data blocks the dependent decision only**; descriptive work continues. No numeric zero stands in for an unknown, and unknown capability is not confirmed absence.
- **Numbers come from code.** Any authored text references computed values through placeholders that a build step resolves and validates (`src/build_review_v2.py`, `src/build_canonical.py`).
- **No role executes.** Outputs are proposals with conditions; a human records decisions (dashboard `operator_input`); nothing touches an ad account.
- **Handoffs are files**, not messages: a role's output artifact plus the fact list the next role must confirm or consume.

## The six roles

### 1. Account Strategist

**Business questions.** What is the account trying to achieve this period, at what allowable, under which posture (scale / maintain efficiency), measured how? Which recommendations from the diagnostic roles are consistent with that, and which need a human choice?

**Responsibilities.** Own the account context layer: business model facts, objectives, allowable(s), strategic posture, measurement constraints (attribution window, lag, usable conversion events). Consolidate the other roles' outputs into one review for the human. Route unknowns to the people who can answer them.

**Required inputs.** Confirmed facts from the client (brief, product team, finance), the data-availability register, outputs from roles 2–6.
**Missing-data behaviour.** Records the gap with the decision it limits and asks; **must not invent business targets, margins, customer value or product facts**. If the posture is not selected, presents both branches and stops.

**Outputs.** `config/account_context.json` (facts with status), posture selection, a consolidated recommendation review with each item's conditions and owner, a question list by recipient.
**Decision boundaries.** Owns context and consolidation. Does not own diagnosis, structure, copy or execution; does not change an allowable to make a recommendation fit.

**Handoffs.** Context → all roles. Consolidated review → human. Answered questions → back to the originating role for a new version.

**Status.** Partially represented, not an agent: the context layer exists (`context/`, `config/account_context.json` with explicit `unknown`/`prior` statuses), the posture selector and operator fields exist in the dashboard, and consolidation was done by hand in the review passes (`output/step2/review_v2_*`). No Strategist prompt, skill file or automation exists.

### 2. Campaign

**Business questions.** Which campaigns exist, with what budgets, bidding strategy, targets and conversion events? Is a campaign budget-limited or rank-limited? Which structural changes (new campaign, budget move, bidding-target change) are justified under the selected posture?

**Responsibilities.** Campaign-level structure, budgets, bidding strategy and lever availability; translating a posture into campaign-level moves.

**Required inputs.** Campaign report (spend, conversions by event, impression share lost to budget/rank), bidding strategy and targets per campaign, posture and allowable from role 1, isolation/expansion candidates from roles 5–6.
**Missing-data behaviour.** Without bidding strategy and impression-share data, no bid or budget change is proposed; the role returns the request list (this is exactly the state of the current exercise).

**Outputs.** Campaign-level options with conditions (budget reallocation, target changes, new campaign for an isolated intent), each marked with the lever the bidding strategy allows.
**Decision boundaries.** Owns campaign structure and budget proposals. Does not decide keyword lists, ad-group grouping or copy; does not execute.

**Handoffs.** Receives candidates from 5 and 6; sends structural options to 1 and grouping needs to 3.

**Status.** Not implemented. Defined here only. The channel table in `output/step1/metrics_channels.csv` is channel-level, not campaign-level, and is not a substitute.

### 3. Ad Group

**Business questions.** Which intents deserve their own ad group so that efficiency can be observed and protected? Is a candidate term already covered by an existing ad group? What match types and negatives keep intents from overlapping?

**Responsibilities.** Ad-group grouping by intent, match-type policy, cross-group negatives, coverage checks before any addition.

**Required inputs.** Existing ad-group and keyword list with match types, search-term report with matched keyword and ad group, isolation candidates from role 6, keyword findings from role 5.
**Missing-data behaviour.** Without the existing structure, every "isolate" or "add" remains a candidate with a coverage pre-check, and negatives cannot be scoped (as recorded in the current `negative_candidates` and `addition_isolation_candidates`).

**Outputs.** Proposed grouping, keyword additions with match type, scoped negative lists with the queries they would block, all conditional on the coverage check.
**Decision boundaries.** Owns grouping and match-type proposals. Does not own budgets (2), copy (4) or intent interpretation (5, 6).

**Handoffs.** Receives candidates from 5 and 6; sends copy needs per group to 4; sends structure changes that need budget to 2.

**Status.** Not implemented. Defined here only.

### 4. Ad Copy

**Business questions.** Does the ad and landing page promise match the intent that is being bought? Which intents need a dedicated message or page before a bid decision is fair?

**Responsibilities.** Ad and landing-page message fit per intent, landing-page test design, post-click hypotheses.

**Required inputs.** Ads and landing pages served per ad group, product positioning facts from role 1 (no-code, free tier, developer, enterprise), landing-page test candidates from role 6.
**Missing-data behaviour.** Without the served pages, the role can list which intents to audit but cannot judge fit; without positioning facts, it proposes tests conditional on confirmation.

**Outputs.** Message/page audit per intent, test proposals with the metric to judge them on (cohort-aligned subs/signup, not signups), copy variants once positioning is confirmed.
**Decision boundaries.** Owns messaging and page proposals. Does not decide to negate or scale a term; does not create ad groups.

**Handoffs.** Receives test candidates from 6 and grouping from 3; returns results to 6 for re-diagnosis.

**Status.** Not implemented. Defined here only. The landing-page tests in the canonical artifact are role-6 proposals awaiting this role.

### 5. Keyword Diagnosis (existing workflow)

**Business questions.** For each keyword, is it healthy, and if not, why: bid/rank, quality score, landing-page experience, budget, or wrong campaign type? What should be paused, fixed or moved?

**Responsibilities.** Keyword-level bucketing with data-sufficiency floors, campaign health checks, PMax intent clustering, cannibalisation checks.

**Required inputs.** Keyword report with impression share lost, quality score components, conversions by event over a stated window; campaign report; existing keyword list; operator criteria (`criteria.yaml`, no fallback to recommended values).
**Missing-data behaviour.** Missing operator criteria stop the run; missing columns disable the dependent buckets.

**Outputs.** Bucketed keyword sheets and a written summary (Excel/Word in the original tool).
**Decision boundaries.** Owns keyword-level diagnosis. Does not mine search terms for negatives (specified in the original criteria but not implemented there), and does not own structure or copy.

**Handoffs.** Sends existing-keyword coverage and keyword health to 3 and 6; receives search-term candidates from 6 for coverage checks.

**Status.** Exists as the sibling module [`keyword-diagnosis/`](../../keyword-diagnosis/README.md) in this repository (its own history, commits dated June 22, 2026; embedded Python in `generators/run-diagnose.md`). Not wired to this module's context layer and not run on the Braid data, which lacks the columns it needs. Only its principles were carried over (see the methodology layer above).

### 6. Search-Term Diagnosis (implemented)

**Business questions.** Which search terms are efficient against the allowable and the scope benchmark? What intent does each represent, what is missing before acting, and what would each posture do?

**Responsibilities.** Validate and recompute term metrics, reconcile totals, cross-term patterns with counterexamples, per-term evidence, hypotheses, conditional recommendations, negative and isolation candidates, landing-page test proposals, missing-information register.

**Required inputs.** Search-term report (term, match type, clicks, cost, signups, subs), scope totals and allowable from the context layer.
**Missing-data behaviour.** FFT shown as unavailable; undefined ratios left null with a warning; thresholds unset → sufficiency tiering blocked; unknown product facts → negatives stay pending confirmation.

**Outputs.** `output/step1/` (metrics, checks, run log), `output/step2/` (authored versions v1 → v2.2 with change logs), `output/canonical/search_ops_analysis.json` (UI artifact), dashboard in `ui/`.
**Decision boundaries.** Proposes; does not choose the posture, adjust the allowable, scope negatives to ad groups, or execute.

**Handoffs.** See the example below.

**Status.** Implemented: `src/compute_metrics.py`, `src/build_review_v2.py`, `src/build_canonical.py`, `authoring/`, `tests/` (49 cases), `ui/`. The reasoning is authored in Claude Code sessions and rendered by code; rebuilding does not regenerate it.

## Proposed handoff example (not an executed run)

Everything below is a **proposed workflow** using findings that already exist in `output/canonical/search_ops_analysis.json`. No agent ran; the arrows describe which file would go to which role and what that role would have to confirm.

```text
[6] Search-Term Diagnosis  ──canonical artifact──▶  [1] Account Strategist
      │                                                   │ selects posture (human), routes questions
      │                                                   ▼
      ├─ negative candidates (pending) ────────────▶ product / sales answers ──▶ [1] updates context
      ├─ isolation / addition candidates ─────────▶ [5] coverage check ──▶ [3] Ad Group proposal
      ├─ landing-page test candidates ────────────▶ [4] Ad Copy test design
      └─ "bidding signal" concern ────────────────▶ [2] Campaign: confirm bidding event / strategy
                                                          │
                                                          ▼
                                             [1] consolidated review ──▶ human decision (dashboard)
```

Walking one term through it — `free ai app builder` (18.4% of sample cost, $553.13/sub, 2.0% subs/signup, needs about 6.1% to reach $181):

1. **[6] → [1]**: the artifact carries the conditional recommendation (reduce exposure; keep-and-isolate if a free tier exists and cohort subs/signup reaches ~6.1%), the negative candidate `"free"` (phrase, pending confirmation), and the missing items (free tier? cohort conversion? landing page served?).
2. **[1]**: records the posture chosen by the human; sends "does a free tier exist; median and 90-day free→paid?" to product and "cohort-aligned subs by term" to data. Does not assume an answer.
3. **[1] → [4]** (if a free tier is confirmed): landing-page test "free-tier page vs current, measured on cohort-aligned subs", already listed in `landing_page_tests`.
4. **[1] → [5] → [3]** (if a free tier is confirmed): Keyword Diagnosis checks whether a "free" keyword or ad group already exists; Ad Group proposes isolation with reduced exposure by whatever lever the bidding strategy allows.
5. **[1] → [3]** (if no free tier is confirmed): the negative becomes actionable; Ad Group scopes it to the matched keyword's ad group after listing the queries it would block in the remaining ~35% of scope spend.
6. **[2]**: whichever branch, confirms the campaign's bidding event and strategy first, because the artifact flags signup-based optimisation as a concern to investigate, not a finding.
7. **Human**: records the final decision and rationale in the dashboard; exports `operator_feedback.json`; a new authored version is produced in Claude Code that cites the answers. Nothing is executed by any role.

## What would be needed to make this operational

- Role prompt/skill files for roles 1–4 with the input/output specs above (none exist).
- Campaign and keyword reports with matched keyword, ad group, campaign, bidding strategy and impression-share columns for the Braid account (none supplied).
- A consumer for `operator_feedback.json` in the authoring step (manual today).
- Integration or re-implementation of the keyword workflow against a shared context layer (today it uses its own `clients/<slug>/` files).

Until then, the accurate description of this repository is: one implemented diagnostic role, one pre-existing external role, four defined roles, and a context layer that all of them are designed to share.
