# Canonical analysis artifact: schema

Path: `output/canonical/search_ops_analysis.json` · `schema_version` 1.0.0 · language: English
Built by `python3 src/build_canonical.py` from `output/step1/` (verified metrics), `authoring/review_v2_2.json` (corrected independent review, built via `src/build_review_v2.py`) and `config/account_context.json`. Validated on build (`tests/test_build_canonical.py`, 9 cases).

Numeric values are strings holding exact decimals (e.g. `"147.8261"`); the UI parses them. `null` means unknown/undefined, never zero. All ranking and count phrases in text are computed from step 1, not typed.

## Top level

| Key | Type | Content |
|---|---|---|
| `schema_version`, `artifact`, `language`, `account`, `data_status` | string | identity; `data_status` = `synthetic_interview_exercise` |
| `versions` | object | `step1_implementation`, `review_basis` (`step2-review-v2.2`), `review_supersedes[]`, `diagnosis_v1` (historical, not imported), `corrections_applied[]` |
| `sources` | object | SHA-256 of inputs, step 1 implementation, review authoring; `operator_interview_answers: "none supplied; not used"` |
| `account_context` | object | copy of `config/account_context.json` (business model with `status` per field, allowable, benchmark, event mapping, methodology priors) |
| `posture` | object | `selected: null`, `options: ["scale","maintain_efficiency"]`, `status` |
| `metrics` | object | `scope_levels` (step 1 `scope_summary.json`), `channels[]` (step 1 rows; `Paid total` has `is_aggregate: "true"`), `checks_summary`, `warnings[]`, `missing_data_register[]` |
| `insights` | object | `patterns[]` (P1–P7: `id,title,observed,supporting[],counterexamples[],explanations[],distinguishing_evidence`), `groups{}` (arithmetic sums), `observed_vs_explanations[]`, `channel_observations[]`, `method_note` |
| `terms[]` | array (9) | see below; sorted by `rank_by_cost` |
| `negative_candidates[]` | array (4) | `term_id, search_term, proposed_negative, match_type_proposed, status: "pending_confirmation", confirmation_required[], becomes_actionable_if, does_not_apply_if` |
| `addition_isolation_candidates[]` | array (7) | `term_id, search_term, action, landing_page_test, precheck[], status: "pending_precheck", note` |
| `landing_page_tests[]` | array (6) | `term_id, search_term, test, precheck[], status: "proposed"` |
| `bidding_signal` | object | `decision, lean, flips_if, under_scale, under_maintain_efficiency` — a concern to investigate, not a change |
| `actions` | object | `justified_now[] {action, why}`, `requires_evidence[] {action, needs, why}` |
| `least_certain` | object | `text`, `candidates[] {term, why}` (two candidates; operator picks) |
| `v1_unsupported_assumptions[]` | array (9) | `v1_statement, unsupported_assumption, v2_position` — quotes v1 verbatim for the record |
| `operator_input` | object | global operator fields, initially empty (see below) |
| `execution` | object | `any_action_executed: false`, `note` |

## `terms[i]`

| Key | Content |
|---|---|
| `term_id`, `search_term`, `match_type_source`, `rank_by_cost` | identity from step 1 (`match_type_source` is the triggering match type, not keyword structure) |
| `metrics` | step 1 numbers plus derived: `clicks, cost, signup, paid_sub, cpc, cost_per_signup, signup_per_click, paid_sub_per_signup, cost_per_sub_recomputed, cost_per_sub_supplied, sample_cost_share, sample_sub_share, allowable_cost_per_sub, ratio_to_allowable, gap_to_allowable, benchmark_cost_per_sub, ratio_to_benchmark, gap_to_benchmark, sample_without_term_cost_per_sub, subs_needed_at_allowable, sub_rate_needed_at_allowable, subs_multiple_needed` |
| `comparison` | `vs_allowable {reference, ratio, status}`, `vs_scope_benchmark {reference, ratio, status, note}`, `allowable_reach {subs_needed, sub_rate_needed, note}` |
| `evidence` | `summary` (fact text with computed numbers/rankings), `status: "fact"`, `source` |
| `intent_hypothesis` | `text, confidence, status: "hypothesis", source` (reviewed into v2.2 from v1; one corrected) |
| `conditional_recommendation` | `lean`, `changes_decision_if`, `branches {scale, maintain_efficiency}`, `status: "conditional"`, `source: "review_v2_2"` |
| `missing_information[]` | `{item, changes_decision}` — each item names what it would change |
| `operator_input` | per-term operator fields, initially empty (see below) |
| `execution` | `{status: "not_executed", executed_at: null}` |

## Operator input (global and per term), initially empty

```json
{
  "missing_data_notes": [],
  "product_questions_and_answers": [],
  "operator_insight": null,
  "final_decision": null,
  "decision_rationale": null
}
```
Suggested entry shapes for the UI: `missing_data_notes[]: {item, note, added_at}`; `product_questions_and_answers[]: {question, to, answer, answered_by, status}`; `final_decision`: one of `keep | expand | isolate | reduce_exposure | negative | measure_on_leads | hold`; `decision_rationale`: free text. The build validator rejects an artifact whose operator fields are non-empty or whose `execution` is anything other than not executed, so operator edits must be stored separately (e.g. a sidecar file the UI merges), not written back into this artifact.

## Invariants enforced by `build_canonical.validate`
- `terms[].term_id` equals the step 1 set exactly, no duplicates; cost, paid_sub and cost_per_sub_recomputed equal step 1.
- Every candidate references a known `term_id`; every negative is `pending_confirmation` with non-empty `confirmation_required`.
- Every term has non-empty `lean`, `changes_decision_if`, both branches, and `missing_information`.
- No unresolved `{placeholder}` in terms, insights, candidates or versions.
- Global and per-term `operator_input` empty; `posture.selected` null; nothing executed; step 1 checks `pass`.
