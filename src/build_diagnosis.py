#!/usr/bin/env python3
"""Search Ops step 2: assemble and validate the first-pass search-term diagnosis.

Merges three inputs:
  output/step1/*            deterministic numbers (the only source of figures)
  config/account_context.json  editable business context, posture, allowable, benchmark
  authoring/diagnosis_v1.json  model-authored interpretation with {placeholders}

Every placeholder is resolved from step 1 or the account context; an unknown
placeholder, unknown term_id, or a term left uncovered fails the build. This
keeps every number in the diagnosis traceable to a computed value.
"""
import argparse
import csv
import hashlib
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STEP1 = PROJECT_ROOT / "output" / "step1"
DEFAULT_ACCOUNT = PROJECT_ROOT / "config" / "account_context.json"
DEFAULT_AUTHORING = PROJECT_ROOT / "authoring" / "diagnosis_v1.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "step2"


class DiagnosisError(ValueError):
    pass


class StrictDict(dict):
    def __missing__(self, key):
        raise DiagnosisError("unknown placeholder {%s}; add it to build_diagnosis.py or fix the authoring file" % key)


# ---------------------------------------------------------------- loading ---

def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dec(text):
    return None if text in (None, "") else Decimal(text)


# ------------------------------------------------------------- formatting ---

def money(value):
    return "" if value is None else "$" + format(value.quantize(Decimal("0.01"), ROUND_HALF_UP), ",f")


def count(value):
    if value is None:
        return ""
    return format(value, ",f") if value != value.to_integral_value() else format(int(value), ",d")


def pct(value):
    return "" if value is None else format((value * 100).quantize(Decimal("0.1"), ROUND_HALF_UP), "f") + "%"


def times(value):
    return "" if value is None else format(value.quantize(Decimal("0.01"), ROUND_HALF_UP), "f") + "x"


def safe_div(a, b):
    return None if a is None or b is None or b == 0 else a / b


# ------------------------------------------------------------ assembling ---

def term_numbers(row, benchmark, sample_cost, sample_subs):
    cost = dec(row["cost"])
    subs = dec(row["paid_sub"])
    cps = dec(row["cost_per_sub_recomputed"])
    allowable = dec(row["allowable_cost_per_sub"])
    rest_cps = safe_div(sample_cost - cost, sample_subs - subs)
    return {
        "clicks": dec(row["clicks"]), "cost": cost, "signup": dec(row["signup"]), "paid_sub": subs,
        "cpc": dec(row["cpc"]), "cost_per_signup": dec(row["cost_per_signup"]),
        "signup_per_click": dec(row["signup_per_click"]), "paid_sub_per_signup": dec(row["paid_sub_per_signup"]),
        "cost_per_sub_recomputed": cps, "cost_per_sub_supplied": dec(row["cost_per_sub_supplied"]),
        "sample_cost_share": dec(row["sample_cost_share"]), "sample_sub_share": dec(row["sample_sub_share"]),
        "allowable_cost_per_sub": allowable,
        "ratio_to_allowable": dec(row["cost_per_sub_to_allowable_ratio"]),
        "gap_to_allowable": None if cps is None else cps - allowable,
        "benchmark_cost_per_sub": benchmark,
        "ratio_to_benchmark": safe_div(cps, benchmark),
        "gap_to_benchmark": None if cps is None else cps - benchmark,
        "sample_without_term_cost_per_sub": rest_cps,
    }


def term_placeholders(n, global_ph):
    ph = StrictDict(global_ph)
    ph.update({
        "clicks": count(n["clicks"]), "cost": money(n["cost"]), "signup": count(n["signup"]),
        "paid_sub": count(n["paid_sub"]), "cpc": money(n["cpc"]), "cost_per_signup": money(n["cost_per_signup"]),
        "signup_per_click_pct": pct(n["signup_per_click"]), "paid_sub_per_signup_pct": pct(n["paid_sub_per_signup"]),
        "cost_per_sub": money(n["cost_per_sub_recomputed"]), "cost_share_pct": pct(n["sample_cost_share"]),
        "sub_share_pct": pct(n["sample_sub_share"]), "allowable": money(n["allowable_cost_per_sub"]),
        "ratio_to_allowable": times(n["ratio_to_allowable"]), "ratio_to_benchmark": times(n["ratio_to_benchmark"]),
        "sample_without_term_cost_per_sub": money(n["sample_without_term_cost_per_sub"]),
    })
    return ph


def comparison(cps, reference, label):
    if cps is None or reference is None:
        return {"reference": label, "status": "undefined"}
    return {
        "reference": label, "reference_value": reference, "term_value": cps,
        "ratio": safe_div(cps, reference), "gap": cps - reference,
        "status": "above" if cps > reference else "below",
        "note": "descriptive; cohort alignment of subs to signups unverified",
    }


def fill(template, ph):
    if isinstance(template, str):
        return template.format_map(ph)
    if isinstance(template, list):
        return [fill(t, ph) for t in template]
    if isinstance(template, dict):
        return {k: fill(v, ph) for k, v in template.items()}
    return template


def build(step1_dir, account_path, authoring_path):
    step1_dir = Path(step1_dir)
    terms_rows = read_csv(step1_dir / "metrics_search_terms.csv")
    channel_rows = read_csv(step1_dir / "metrics_channels.csv")
    scope = read_json(step1_dir / "scope_summary.json")
    checks = read_json(step1_dir / "checks.json")
    account = read_json(account_path)
    authored = read_json(authoring_path)

    if checks["summary"]["overall"] != "pass":
        raise DiagnosisError("step 1 checks did not pass; refusing to build a diagnosis on failed reconciliation")

    benchmark = Decimal(scope["scope"]["cost_per_sub_recomputed"])
    if Decimal(str(account["performance_benchmark"]["scope_cost_per_sub_recomputed"])) != benchmark:
        raise DiagnosisError("account_context benchmark %s != step1 scope cost/sub %s; update the config"
                             % (account["performance_benchmark"]["scope_cost_per_sub_recomputed"], benchmark))
    allowable_cfg = Decimal(str(account["allowable"]["non_brand_cost_per_sub"]))
    sample_cost = Decimal(scope["sample"]["cost"])
    sample_subs = Decimal(scope["sample"]["paid_sub"])

    ch = {r["channel"]: r for r in channel_rows}
    for needed in ("Google Non-Brand", "Google Performance Max", "Meta prospecting", "Paid total"):
        if needed not in ch:
            raise DiagnosisError("channel %r missing from step1 metrics_channels.csv" % needed)
    global_ph = {
        "benchmark": money(benchmark),
        "sample_cost_per_sub": money(Decimal(scope["sample"]["cost_per_sub_recomputed"])),
        "remainder_cost_per_sub": money(Decimal(scope["remainder"]["cost_per_sub"])),
        "non_brand_cost_per_sub": money(dec(ch["Google Non-Brand"]["q2_cost_per_sub_recomputed"])),
        "non_brand_q1_cost_per_sub": money(dec(ch["Google Non-Brand"]["q1_cost_per_sub_supplied"])),
        "non_brand_spend_share": pct(dec(ch["Google Non-Brand"]["share_of_paid_spend"])),
        "pmax_cost_per_sub": money(dec(ch["Google Performance Max"]["q2_cost_per_sub_recomputed"])),
        "meta_prospecting_cost_per_sub": money(dec(ch["Meta prospecting"]["q2_cost_per_sub_recomputed"])),
        "paid_total_supplied": money(dec(ch["Paid total"]["q2_cost_per_sub_supplied"])),
        "paid_total_recomputed": money(dec(ch["Paid total"]["q2_cost_per_sub_recomputed"])),
    }

    step1_ids = {r["term_id"]: r for r in terms_rows}
    authored_terms = authored["terms"]
    unknown = sorted(set(authored_terms) - set(step1_ids))
    uncovered = sorted(set(step1_ids) - set(authored_terms))
    if unknown:
        raise DiagnosisError("authored term_ids not in step1: %s" % unknown)
    if uncovered:
        raise DiagnosisError("step1 terms without a diagnosis: %s" % [step1_ids[i]["search_term"] for i in uncovered])

    terms_out = []
    for row in sorted(terms_rows, key=lambda r: int(r["rank_by_cost"])):
        tid = row["term_id"]
        a = authored_terms[tid]
        if a["search_term"] != row["search_term"]:
            raise DiagnosisError("term_id %s: authored search_term %r != step1 %r" % (tid, a["search_term"], row["search_term"]))
        n = term_numbers(row, benchmark, sample_cost, sample_subs)
        if n["allowable_cost_per_sub"] != allowable_cfg:
            raise DiagnosisError("term %s allowable %s != account allowable %s" % (tid, n["allowable_cost_per_sub"], allowable_cfg))
        ph = term_placeholders(n, global_ph)
        terms_out.append({
            "rank_by_cost": int(row["rank_by_cost"]),
            "term_id": tid,
            "search_term": row["search_term"],
            "match_type_source": row["match_type_source"],
            "evidence": {
                "source": "output/step1/metrics_search_terms.csv",
                "numbers": n,
                "summary": fill(a["evidence_summary"], ph),
                "status": "fact",
            },
            "intent_hypothesis": a["intent_hypothesis"],
            "comparison": {
                "vs_allowable": comparison(n["cost_per_sub_recomputed"], n["allowable_cost_per_sub"],
                                           "Non-Brand allowable (candidate brief)"),
                "vs_scope_benchmark": comparison(n["cost_per_sub_recomputed"], benchmark,
                                                 "scope cost/sub recomputed (step1), not a target"),
            },
            "missing_info": [dict(m, status="to_confirm") for m in fill(a["missing_info"], ph)],
            "conditional_handling": {
                "posture_selected": account["strategic_posture"]["selected"],
                "scale": fill(a["under_scale"], ph),
                "maintain_efficiency": fill(a["under_maintain_efficiency"], ph),
                "status": "conditional; no final decision until posture is selected",
            },
            "investigate_now": fill(a["investigate_now"], ph),
            "final_decision": None,
            "human_amendments": None,
        })

    # summary: validate term references, fill placeholders
    ph_global = StrictDict(global_ph)
    summary = json.loads(json.dumps(authored["summary"]))
    for key in ("negative_candidates", "addition_or_isolation_candidates"):
        for item in summary[key]:
            if item["term_id"] not in step1_ids:
                raise DiagnosisError("%s references unknown term_id %s" % (key, item["term_id"]))
            item["search_term"] = step1_ids[item["term_id"]]["search_term"]
            item["status"] = "conditional"
    lc = summary["least_certain_term"]
    if lc["term_id"] not in step1_ids:
        raise DiagnosisError("least_certain_term references unknown term_id %s" % lc["term_id"])
    lc["search_term"] = step1_ids[lc["term_id"]]["search_term"]
    lc_numbers = [t for t in terms_out if t["term_id"] == lc["term_id"]][0]["evidence"]["numbers"]
    lc["why"] = fill(lc["why"], term_placeholders(lc_numbers, global_ph))
    summary["other_hypotheses_and_tests"] = fill(summary["other_hypotheses_and_tests"], ph_global)
    summary["notes"] = [
        "No forced negative quota; every negative is conditional on a product or data fact listed with it.",
        "Existing keywords and account structure are unknown: every addition/isolation requires a coverage check first.",
        "Campaign/ad-group IDs are unknown: nothing here is an import-ready file.",
    ]

    return {
        "meta": {
            "step": "step2-diagnosis-v1",
            "author": authored["author"],
            "status_legend": authored["status_legend"],
            "posture_selected": account["strategic_posture"]["selected"],
            "allowable": account["allowable"],
            "benchmark": account["performance_benchmark"],
            "sources": {
                "step1_metrics_search_terms_sha256": sha256_file(step1_dir / "metrics_search_terms.csv"),
                "step1_metrics_channels_sha256": sha256_file(step1_dir / "metrics_channels.csv"),
                "step1_scope_summary_sha256": sha256_file(step1_dir / "scope_summary.json"),
                "step1_checks_sha256": sha256_file(step1_dir / "checks.json"),
                "account_context_sha256": sha256_file(account_path),
                "authoring_sha256": sha256_file(authoring_path),
            },
            "validation": {
                "terms_covered": len(terms_out),
                "all_term_ids_resolved": True,
                "all_placeholders_resolved": True,
                "benchmark_matches_step1": True,
                "step1_checks_overall": checks["summary"]["overall"],
            },
        },
        "account_context": account,
        "scope_levels": scope,
        "channel_context_observations": fill(authored["channel_context_observations"], ph_global),
        "terms": terms_out,
        "summary": summary,
        "step1_missing_data": checks["missing_data"],
    }


# ------------------------------------------------------------- rendering ---

def _json_default(v):
    if isinstance(v, Decimal):
        return format(v, "f")
    raise TypeError(type(v))


def render_md(d):
    L = []
    a = d["account_context"]
    L.append("# Braid Search Ops: search-term diagnosis (v1, model-authored)\n")
    L.append("Posture selected: **%s** (not chosen by operator; both options shown per term). "
             "Allowable: **$%s/sub** (%s). Benchmark: **%s/sub** (%s).\n"
             % (d["meta"]["posture_selected"] or "none", a["allowable"]["non_brand_cost_per_sub"],
                a["allowable"]["source"], money(Decimal(str(a["performance_benchmark"]["scope_cost_per_sub_recomputed"]))),
                a["performance_benchmark"]["note"]))
    L.append("Legend: **fact** = supplied data/confirmed context; **hypothesis** = model interpretation; "
             "**to confirm** = needs product/data/operator input. All figures come from `output/step1/`.\n")

    L.append("## Account context (editable: `config/account_context.json`)\n")
    L.append("| Field | Value | Status |\n|---|---|---|")
    for k, v in a["business_model"].items():
        L.append("| %s | %s | %s |" % (k, v["value"] if v["value"] is not None else "—", v["status"]))
    L.append("| strategic_posture | %s | %s |" % (a["strategic_posture"]["selected"] or "—", a["strategic_posture"]["status"]))
    L.append("")

    L.append("## Scope levels (fact)\n")
    s = d["scope_levels"]
    L.append("| Level | Spend | Subs | Cost/sub (recomputed) |\n|---|---|---|---|")
    L.append("| Google Non-Brand (Q2 label; period alignment unverified) | $%s | %s | %s |"
             % (count(Decimal(s["all_google_non_brand"]["spend"])), s["all_google_non_brand"]["paid_sub"],
                money(Decimal(s["all_google_non_brand"]["cost_per_sub_recomputed"]))))
    L.append("| Scope: %s | $%s | %s | %s |" % (s["scope"]["label"], count(Decimal(s["scope"]["spend"])),
             s["scope"]["paid_sub"], money(Decimal(s["scope"]["cost_per_sub_recomputed"]))))
    L.append("| Nine-term sample (%s of scope spend; reported ~%s) | $%s | %s | %s |"
             % (pct(Decimal(s["sample"]["spend_coverage_of_scope_actual"])), pct(Decimal(s["sample"]["spend_coverage_of_scope_reported"])),
                count(Decimal(s["sample"]["cost"])), s["sample"]["paid_sub"], money(Decimal(s["sample"]["cost_per_sub_recomputed"]))))
    L.append("| Remainder (subtraction within scope; no terms known) | $%s | %s | %s |"
             % (count(Decimal(s["remainder"]["spend"])), s["remainder"]["paid_sub"], money(Decimal(s["remainder"]["cost_per_sub"]))))
    L.append("")

    L.append("## Channel context (descriptive, from `metrics_channels.csv`)\n")
    for o in d["channel_context_observations"]:
        L.append("- " + o)
    L.append("")

    L.append("## Terms, sorted by spend\n")
    for t in d["terms"]:
        n = t["evidence"]["numbers"]
        L.append("### %d. %s  (`%s`, %s match)\n" % (t["rank_by_cost"], t["search_term"], t["term_id"], t["match_type_source"]))
        L.append("**Evidence (fact).** %s" % t["evidence"]["summary"])
        L.append("")
        L.append("| Clicks | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | vs benchmark |\n|---|---|---|---|---|---|---|---|---|---|---|")
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s (%s) | %s (%s) |" % (
            count(n["clicks"]), money(n["cost"]), count(n["signup"]), count(n["paid_sub"]), money(n["cpc"]),
            money(n["cost_per_signup"]), pct(n["signup_per_click"]), pct(n["paid_sub_per_signup"]),
            money(n["cost_per_sub_recomputed"]), times(n["ratio_to_allowable"]), t["comparison"]["vs_allowable"]["status"],
            times(n["ratio_to_benchmark"]), t["comparison"]["vs_scope_benchmark"]["status"]))
        L.append("")
        ih = t["intent_hypothesis"]
        L.append("**Intent (hypothesis, %s confidence).** %s\n" % (ih["confidence"], ih["text"]))
        L.append("**Missing information (to confirm).**")
        for m in t["missing_info"]:
            L.append("- %s — limits: %s" % (m["item"], m["limits"]))
        L.append("")
        L.append("**If posture = scale.** %s\n" % t["conditional_handling"]["scale"])
        L.append("**If posture = maintain efficiency.** %s\n" % t["conditional_handling"]["maintain_efficiency"])
        L.append("**Investigate now (either posture).**")
        for i in t["investigate_now"]:
            L.append("- " + i)
        L.append("")

    sm = d["summary"]
    L.append("## Summary\n")
    L.append("### Conditional negative candidates\n")
    L.append("| Term | Proposed negative | Match type | Condition | Scope |\n|---|---|---|---|---|")
    for c in sm["negative_candidates"]:
        L.append("| %s | %s | %s | %s | %s |" % (c["search_term"], c["proposed_negative"], c["match_type"], c["condition"], c["scope_note"]))
    L.append("")
    L.append("### Addition / isolation candidates and landing-page tests\n")
    L.append("| Term | Action | Landing-page test | Check before adding |\n|---|---|---|---|")
    for c in sm["addition_or_isolation_candidates"]:
        L.append("| %s | %s | %s | %s |" % (c["search_term"], c["action"], c["landing_page_test"], c["precheck"]))
    L.append("")
    lc = sm["least_certain_term"]
    L.append("### Least certain term: %s\n" % lc["search_term"])
    L.append("%s\n\n**The one piece of information that would change the decision:** %s\n" % (lc["why"], lc["single_piece_of_information"]))
    L.append("### Questions for product / data / operator\n")
    L.append("| To | Question | Unblocks |\n|---|---|---|")
    for q in sm["questions_for_product_or_data_team"]:
        L.append("| %s | %s | %s |" % (q["to"], q["question"], q["unblocks"]))
    L.append("")
    L.append("### Other hypotheses and tests\n")
    for h in sm["other_hypotheses_and_tests"]:
        L.append("- **Hypothesis:** %s **Test:** %s" % (h["hypothesis"], h["test"]))
    L.append("")
    L.append("### Notes\n")
    for nmsg in sm["notes"]:
        L.append("- " + nmsg)
    L.append("")
    L.append("## Step 1 missing-data register (carried forward)\n")
    for m in d["step1_missing_data"]:
        L.append("- `%s` (%s) — limits: %s" % (m["item"], m["status"], m["limits"]))
    L.append("")
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description="Search Ops step 2: build and validate the diagnosis.")
    p.add_argument("--step1-dir", type=Path, default=DEFAULT_STEP1)
    p.add_argument("--account-context", type=Path, default=DEFAULT_ACCOUNT)
    p.add_argument("--authoring", type=Path, default=DEFAULT_AUTHORING)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = p.parse_args(argv)
    try:
        d = build(args.step1_dir, args.account_context, args.authoring)
    except DiagnosisError as exc:
        print("DIAGNOSIS ERROR: %s" % exc, file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.output_dir / "diagnosis.json", "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False, default=_json_default)
        fh.write("\n")
    (args.output_dir / "diagnosis.md").write_text(render_md(d), encoding="utf-8")
    v = d["meta"]["validation"]
    print("diagnosis built: %d terms, posture=%s, negatives=%d (conditional), isolation=%d -> %s"
          % (v["terms_covered"], d["meta"]["posture_selected"], len(d["summary"]["negative_candidates"]),
             len(d["summary"]["addition_or_isolation_candidates"]), args.output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
