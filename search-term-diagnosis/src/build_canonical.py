#!/usr/bin/env python3
"""Search Ops: build the canonical, UI-ready analysis artifact.

Combines verified step 1 metrics, the corrected independent review (v2.2) and
the account context into one JSON file. Operator input fields are created empty
and final decisions are unset. Nothing is imported from diagnosis v1: its intent
hypotheses were reviewed into review v2.2 (one corrected), and its
recommendations are replaced by the corrected conditional recommendations.

Output: output/canonical/search_ops_analysis.json (schema in output/canonical/SCHEMA.md)
"""
import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_diagnosis as bd  # noqa: E402
import build_review_v2 as rv  # noqa: E402

PROJECT_ROOT = bd.PROJECT_ROOT
DEFAULT_REVIEW_AUTHORING = PROJECT_ROOT / "authoring" / "review_v2_2.json"
DEFAULT_V1 = PROJECT_ROOT / "output" / "step2" / "diagnosis.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "canonical" / "search_ops_analysis.json"
SCHEMA_VERSION = "1.0.0"

EMPTY_OPERATOR_INPUT = {
    "missing_data_notes": [],
    "product_questions_and_answers": [],
    "operator_insight": None,
    "final_decision": None,
    "decision_rationale": None,
}


def d2(v):
    """Decimal -> JSON-safe string (keeps precision; UI parses)."""
    return None if v is None else format(v, "f")


def build(step1_dir, account_path, review_authoring, v1_path):
    step1_dir = Path(step1_dir)
    review = rv.build(step1_dir, account_path, review_authoring)
    account = bd.read_json(account_path)
    checks = bd.read_json(step1_dir / "checks.json")
    scope = bd.read_json(step1_dir / "scope_summary.json")
    run_log = bd.read_json(step1_dir / "run_log.json")
    channels = bd.read_csv(step1_dir / "metrics_channels.csv")
    v1_exists = Path(v1_path).exists()

    authored = bd.read_json(review_authoring)
    aliases = authored["aliases"]
    alias_of = {tid: a for a, tid in aliases.items()}
    recs = {r.get("alias"): r for r in review["conditional_recommendations"] if r.get("alias")}
    bidding_rec = [r for r in review["conditional_recommendations"] if not r.get("alias")]

    terms = []
    for t in review["observed_performance"]:
        tid = t["term_id"]
        alias = alias_of[tid]
        n = t["numbers"]
        rec = recs[alias]
        terms.append({
            "term_id": tid,
            "search_term": t["search_term"],
            "match_type_source": t["match_type_source"],
            "rank_by_cost": t["rank_by_cost"],
            "metrics": {k: d2(v) for k, v in n.items()},
            "comparison": {
                "vs_allowable": {"reference": d2(n["allowable_cost_per_sub"]), "ratio": d2(n["ratio_to_allowable"]),
                                 "status": "above" if n["cost_per_sub_recomputed"] > n["allowable_cost_per_sub"] else "below"},
                "vs_scope_benchmark": {"reference": d2(n["benchmark_cost_per_sub"]), "ratio": d2(n["ratio_to_benchmark"]),
                                       "status": "above" if n["cost_per_sub_recomputed"] > n["benchmark_cost_per_sub"] else "below",
                                       "note": "benchmark is the scope's recomputed cost/sub, not a target"},
                "allowable_reach": {"subs_needed": d2(n["subs_needed_at_allowable"]),
                                    "sub_rate_needed": d2(n["sub_rate_needed_at_allowable"]),
                                    "note": "arithmetic at current cost; reaching the allowable is not financial break-even"},
            },
            "evidence": {"summary": review["term_evidence_notes"][alias], "status": "fact",
                         "source": "output/step1/metrics_search_terms.csv via review v2.2"},
            "intent_hypothesis": review["term_intent_hypotheses"][alias],
            "conditional_recommendation": {
                "lean": rec["lean"], "changes_decision_if": rec["flips_if"],
                "branches": {"scale": rec["under_scale"], "maintain_efficiency": rec["under_maintain_efficiency"]},
                "status": "conditional", "source": "review_v2_2",
            },
            "missing_information": review["term_missing_information"][alias],
            "operator_input": json.loads(json.dumps(EMPTY_OPERATOR_INPUT)),
            "execution": {"status": "not_executed", "executed_at": None},
        })

    def strip_alias(items):
        out = []
        for it in items:
            it = dict(it)
            it.pop("alias", None)
            out.append(it)
        return out

    channel_rows = []
    for r in channels:
        channel_rows.append({k: (None if v == "" else v) for k, v in r.items()})

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact": "search_ops_analysis",
        "language": "en",
        "account": account["account"],
        "data_status": account["data_status"],
        "versions": {
            "step1_implementation": run_log["implementation_version"],
            "review_basis": review["meta"]["step"],
            "review_supersedes": [review["meta"]["supersedes"], "review_v2_1 -> review_v2", "review_v2 (independent of v1)"],
            "diagnosis_v1": ("output/step2/diagnosis.json (historical baseline, present; not imported; intent hypotheses were reviewed into review v2.2)" if v1_exists else "not found"),
            "corrections_applied": review["meta"]["corrections"],
        },
        "sources": {
            "step1": {"dir": "output/step1", "inputs": run_log["inputs"], "implementation_sha256": run_log["implementation_sha256"]},
            "review": review["meta"]["sources"],
            "operator_interview_answers": "none supplied; not used",
        },
        "account_context": account,
        "posture": {"selected": account["strategic_posture"]["selected"], "options": account["strategic_posture"]["options"],
                    "status": account["strategic_posture"]["status"]},
        "metrics": {
            "scope_levels": scope,
            "channels": channel_rows,
            "checks_summary": checks["summary"],
            "warnings": checks["warnings"],
            "missing_data_register": checks["missing_data"],
        },
        "insights": {
            "patterns": review["patterns"],
            "groups": {g: {k: (d2(v) if isinstance(v, Decimal) else v) for k, v in val.items()} for g, val in review["groups"].items()},
            "observed_vs_explanations": review["observed_vs_explanations"],
            "channel_observations": review["channel_context_observations"],
            "method_note": review["method_note"],
        },
        "terms": terms,
        "negative_candidates": strip_alias(review["negative_candidates"]),
        "addition_isolation_candidates": strip_alias(review["addition_isolation_candidates"]),
        "landing_page_tests": [{"term_id": c["term_id"], "search_term": c["search_term"], "test": c["landing_page_test"],
                                "precheck": c["precheck"], "status": "proposed"}
                               for c in review["addition_isolation_candidates"] if c.get("landing_page_test")],
        "bidding_signal": bidding_rec[0] if bidding_rec else None,
        "actions": review["actions"],
        "least_certain": review["least_certain"],
        "v1_unsupported_assumptions": review["v1_review"],
        "operator_input": json.loads(json.dumps(EMPTY_OPERATOR_INPUT)),
        "execution": {"any_action_executed": False, "note": "no live account changes in this version"},
    }
    validate(artifact, step1_dir)
    return artifact


PLACEHOLDER = re.compile(r"\{[a-z_][a-z0-9_]*\}")


def has_placeholder(obj):
    if isinstance(obj, str):
        return bool(PLACEHOLDER.search(obj))
    if isinstance(obj, dict):
        return any(has_placeholder(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_placeholder(v) for v in obj)
    return False


def validate(a, step1_dir):
    step1 = bd.read_csv(Path(step1_dir) / "metrics_search_terms.csv")
    ids = [t["term_id"] for t in a["terms"]]
    if sorted(ids) != sorted(r["term_id"] for r in step1):
        raise bd.DiagnosisError("terms do not match step1 term_ids exactly")
    if len(set(ids)) != len(ids):
        raise bd.DiagnosisError("duplicate term_id in artifact")
    by_id = {r["term_id"]: r for r in step1}
    for t in a["terms"]:
        r = by_id[t["term_id"]]
        for src, dst in (("cost", "cost"), ("paid_sub", "paid_sub"), ("cost_per_sub_recomputed", "cost_per_sub_recomputed")):
            if Decimal(t["metrics"][dst]) != Decimal(r[src]):
                raise bd.DiagnosisError("%s: %s differs from step1" % (t["search_term"], dst))
        if t["operator_input"] != EMPTY_OPERATOR_INPUT:
            raise bd.DiagnosisError("%s: operator_input must be empty" % t["search_term"])
        if t["execution"]["status"] != "not_executed":
            raise bd.DiagnosisError("%s: execution must be not_executed" % t["search_term"])
        for key in ("lean", "changes_decision_if"):
            if not t["conditional_recommendation"][key]:
                raise bd.DiagnosisError("%s: conditional_recommendation.%s empty" % (t["search_term"], key))
        if not t["missing_information"]:
            raise bd.DiagnosisError("%s: missing_information empty" % t["search_term"])
        if has_placeholder(t):
            raise bd.DiagnosisError("%s: unresolved placeholder" % t["search_term"])
    for key in ("negative_candidates", "addition_isolation_candidates", "landing_page_tests"):
        for c in a[key]:
            if c["term_id"] not in by_id:
                raise bd.DiagnosisError("%s references unknown term_id %s" % (key, c["term_id"]))
    for c in a["negative_candidates"]:
        if c["status"] != "pending_confirmation" or not c["confirmation_required"]:
            raise bd.DiagnosisError("negative candidate %s must be pending_confirmation with requirements" % c["search_term"])
    if a["operator_input"] != EMPTY_OPERATOR_INPUT or a["posture"]["selected"] is not None:
        raise bd.DiagnosisError("global operator_input must be empty and posture unset")
    if a["execution"]["any_action_executed"]:
        raise bd.DiagnosisError("no action may be marked executed")
    if a["metrics"]["checks_summary"]["overall"] != "pass":
        raise bd.DiagnosisError("step1 checks not passing")
    if has_placeholder(a["insights"]) or has_placeholder(a["negative_candidates"]) or has_placeholder(a["addition_isolation_candidates"]) or has_placeholder(a["versions"]):
        raise bd.DiagnosisError("unresolved placeholder in insights/candidates")
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description="Build the canonical UI-ready analysis artifact.")
    p.add_argument("--step1-dir", type=Path, default=bd.DEFAULT_STEP1)
    p.add_argument("--account-context", type=Path, default=bd.DEFAULT_ACCOUNT)
    p.add_argument("--review-authoring", type=Path, default=DEFAULT_REVIEW_AUTHORING)
    p.add_argument("--v1", type=Path, default=DEFAULT_V1)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = p.parse_args(argv)
    try:
        a = build(args.step1_dir, args.account_context, args.review_authoring, args.v1)
    except bd.DiagnosisError as exc:
        print("CANONICAL ERROR: %s" % exc, file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(a, fh, indent=2, ensure_ascii=False, default=bd._json_default)
        fh.write("\n")
    print("canonical artifact: %d terms, %d negative candidates (pending), %d addition/isolation, %d LP tests, %d patterns -> %s"
          % (len(a["terms"]), len(a["negative_candidates"]), len(a["addition_isolation_candidates"]),
             len(a["landing_page_tests"]), len(a["insights"]["patterns"]), args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
