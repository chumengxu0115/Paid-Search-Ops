#!/usr/bin/env python3
"""Search Ops step 2, review v2: evidence-led cross-term review, independent of v1.

Inputs: output/step1/* (numbers), config/account_context.json (confirmed context),
authoring/review_v2.json (model-authored text with {placeholders}).
No operator interview answers are read. v1 files are not touched.

Placeholders:
  t_<alias>_<metric>   per-term (alias -> term_id map in the authoring file)
  g_<group>_<metric>   group aggregates over aliases listed in the authoring file
  rho_<name>           Spearman rank correlation over the sample (optionally excluding aliases)
  plus the global placeholders from build_diagnosis (benchmark, sample_cost_per_sub, ...)
Every placeholder must resolve, every alias must exist in step 1, or the build fails.
"""
import argparse
import json
import sys
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_diagnosis as bd  # noqa: E402

PROJECT_ROOT = bd.PROJECT_ROOT
DEFAULT_AUTHORING = PROJECT_ROOT / "authoring" / "review_v2.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "step2"


def spearman(xs, ys):
    def ranks(v):
        s = sorted(v)
        return [Decimal(s.index(x) + 1) for x in v]
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return Decimal(1) - Decimal(6) * d2 / (Decimal(n) * (Decimal(n) ** 2 - 1))


ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]


def ordinal(k):
    return ORDINALS[k - 1] if 1 <= k <= len(ORDINALS) else "%dth" % k


RANKED_METRICS = ("paid_sub_per_signup", "cost_per_sub_recomputed", "cpc", "signup_per_click", "cost_per_signup", "cost")


def rank_placeholders(numbers, aliases):
    """Computed ranking/count claims: t_<alias>_<metric>_rank_low / _rank_high ('third-lowest'),
    t_<alias>_<metric>_rank_low_n / _rank_high_n (integers), and
    t_<alias>_n_terms_exceeding_needed_rate (terms whose subs/signup exceeds this term's required rate)."""
    out = {}
    for metric in RANKED_METRICS:
        vals = {tid: n[metric] for tid, n in numbers.items() if n[metric] is not None}
        asc = sorted(vals, key=lambda t: (vals[t], t))
        for alias, tid in aliases.items():
            if tid not in vals:
                continue
            lo = asc.index(tid) + 1
            hi = len(asc) - asc.index(tid)
            out["t_%s_%s_rank_low" % (alias, metric)] = ordinal(lo) + "-lowest" if lo > 1 else "lowest"
            out["t_%s_%s_rank_high" % (alias, metric)] = ordinal(hi) + "-highest" if hi > 1 else "highest"
            out["t_%s_%s_rank_low_n" % (alias, metric)] = str(lo)
            out["t_%s_%s_rank_high_n" % (alias, metric)] = str(hi)
    for alias, tid in aliases.items():
        need = numbers[tid]["sub_rate_needed_at_allowable"]
        if need is None:
            continue
        count = sum(1 for t, n in numbers.items() if t != tid and n["paid_sub_per_signup"] is not None and n["paid_sub_per_signup"] > need)
        out["t_%s_n_terms_exceeding_needed_rate" % alias] = str(count)
    return out


def breakeven(n, allowable):
    subs_needed = (n["cost"] / allowable).to_integral_value(rounding=ROUND_CEILING)
    return {
        "subs_needed_at_allowable": subs_needed,
        "sub_rate_needed_at_allowable": bd.safe_div(subs_needed, n["signup"]),
        "subs_multiple_needed": bd.safe_div(subs_needed, n["paid_sub"]),
    }


def build(step1_dir, account_path, authoring_path):
    step1_dir = Path(step1_dir)
    terms_rows = bd.read_csv(step1_dir / "metrics_search_terms.csv")
    channel_rows = bd.read_csv(step1_dir / "metrics_channels.csv")
    scope = bd.read_json(step1_dir / "scope_summary.json")
    checks = bd.read_json(step1_dir / "checks.json")
    account = bd.read_json(account_path)
    authored = bd.read_json(authoring_path)
    if checks["summary"]["overall"] != "pass":
        raise bd.DiagnosisError("step 1 checks did not pass")

    benchmark = Decimal(scope["scope"]["cost_per_sub_recomputed"])
    allowable = Decimal(str(account["allowable"]["non_brand_cost_per_sub"]))
    sample_cost = Decimal(scope["sample"]["cost"])
    sample_subs = Decimal(scope["sample"]["paid_sub"])
    by_id = {r["term_id"]: r for r in terms_rows}

    numbers = {}
    for r in terms_rows:
        n = bd.term_numbers(r, benchmark, sample_cost, sample_subs)
        n.update(breakeven(n, allowable))
        numbers[r["term_id"]] = n

    aliases = authored["aliases"]
    unknown = [a for a, tid in aliases.items() if tid not in by_id]
    if unknown:
        raise bd.DiagnosisError("aliases with unknown term_id: %s" % unknown)
    uncovered = sorted(set(by_id) - set(aliases.values()))
    if uncovered:
        raise bd.DiagnosisError("step1 terms without alias: %s" % [by_id[t]["search_term"] for t in uncovered])

    ch = {r["channel"]: r for r in channel_rows}
    ph = bd.StrictDict({
        "benchmark": bd.money(benchmark), "allowable": bd.money(allowable),
        "sample_cost_per_sub": bd.money(Decimal(scope["sample"]["cost_per_sub_recomputed"])),
        "remainder_cost_per_sub": bd.money(Decimal(scope["remainder"]["cost_per_sub"])),
        "sample_coverage_pct": bd.pct(Decimal(scope["sample"]["spend_coverage_of_scope_actual"])),
        "sample_sub_coverage_pct": bd.pct(Decimal(scope["sample"]["sub_coverage_of_scope"])),
        "non_brand_cost_per_sub": bd.money(bd.dec(ch["Google Non-Brand"]["q2_cost_per_sub_recomputed"])),
        "non_brand_q1_cost_per_sub": bd.money(bd.dec(ch["Google Non-Brand"]["q1_cost_per_sub_supplied"])),
        "non_brand_spend_share": bd.pct(bd.dec(ch["Google Non-Brand"]["share_of_paid_spend"])),
        "non_brand_allowable_ratio": bd.times(bd.dec(ch["Google Non-Brand"]["cost_per_sub_to_allowable_ratio"])),
        "pmax_cost_per_sub": bd.money(bd.dec(ch["Google Performance Max"]["q2_cost_per_sub_recomputed"])),
        "pmax_allowable_ratio": bd.times(bd.dec(ch["Google Performance Max"]["cost_per_sub_to_allowable_ratio"])),
        "meta_prospecting_cost_per_sub": bd.money(bd.dec(ch["Meta prospecting"]["q2_cost_per_sub_recomputed"])),
        "meta_prospecting_allowable_ratio": bd.times(bd.dec(ch["Meta prospecting"]["cost_per_sub_to_allowable_ratio"])),
        "reddit_cost_per_sub": bd.money(bd.dec(ch["Reddit"]["q2_cost_per_sub_recomputed"])),
        "reddit_allowable_ratio": bd.times(bd.dec(ch["Reddit"]["cost_per_sub_to_allowable_ratio"])),
        "paid_total_supplied": bd.money(bd.dec(ch["Paid total"]["q2_cost_per_sub_supplied"])),
        "paid_total_recomputed": bd.money(bd.dec(ch["Paid total"]["q2_cost_per_sub_recomputed"])),
        "max_observed_sub_rate_pct": bd.pct(max(n["paid_sub_per_signup"] for n in numbers.values())),
        "min_observed_sub_rate_pct": bd.pct(min(n["paid_sub_per_signup"] for n in numbers.values())),
        "term_count": str(len(terms_rows)),
    })

    term_table = []
    for alias, tid in aliases.items():
        n = numbers[tid]
        row = by_id[tid]
        tp = bd.term_placeholders(n, {})
        tp.update({
            "term": row["search_term"], "match": row["match_type_source"], "rank": row["rank_by_cost"],
            "subs_needed": bd.count(n["subs_needed_at_allowable"]),
            "sub_rate_needed_pct": bd.pct(n["sub_rate_needed_at_allowable"]),
            "subs_multiple_needed": bd.times(n["subs_multiple_needed"]),
        })
        for k, v in tp.items():
            ph["t_%s_%s" % (alias, k)] = v
        term_table.append(dict(alias=alias, term_id=tid, search_term=row["search_term"],
                               match_type_source=row["match_type_source"], rank_by_cost=int(row["rank_by_cost"]), numbers=n))
    term_table.sort(key=lambda t: t["rank_by_cost"])
    ph.update(rank_placeholders(numbers, aliases))

    groups_out = {}
    for gname, members in authored["groups"].items():
        bad = [m for m in members if m not in aliases]
        if bad:
            raise bd.DiagnosisError("group %s has unknown aliases %s" % (gname, bad))
        ns = [numbers[aliases[m]] for m in members]
        cost = sum(n["cost"] for n in ns)
        subs = sum(n["paid_sub"] for n in ns)
        signups = sum(n["signup"] for n in ns)
        g = {"members": [by_id[aliases[m]]["search_term"] for m in members], "term_count": len(ns),
             "cost": cost, "paid_sub": subs, "signup": signups,
             "cost_per_sub": bd.safe_div(cost, subs), "sub_rate": bd.safe_div(subs, signups),
             "cost_share": bd.safe_div(cost, sample_cost), "sub_share": bd.safe_div(subs, sample_subs)}
        groups_out[gname] = g
        ph.update({
            "g_%s_n" % gname: str(len(ns)), "g_%s_cost" % gname: bd.money(cost), "g_%s_subs" % gname: bd.count(subs),
            "g_%s_cost_per_sub" % gname: bd.money(g["cost_per_sub"]), "g_%s_sub_rate_pct" % gname: bd.pct(g["sub_rate"]),
            "g_%s_cost_share_pct" % gname: bd.pct(g["cost_share"]), "g_%s_sub_share_pct" % gname: bd.pct(g["sub_share"]),
        })

    corr_out = {}
    for cname, spec in authored.get("correlations", {}).items():
        excl = {aliases[a] for a in spec.get("exclude", [])}
        pts = [(numbers[t][spec["x"]], numbers[t][spec["y"]]) for t in by_id if t not in excl]
        rho = spearman([p[0] for p in pts], [p[1] for p in pts])
        corr_out[cname] = {"x": spec["x"], "y": spec["y"], "excluded": spec.get("exclude", []), "n": len(pts),
                           "spearman_rho": rho.quantize(Decimal("0.01"))}
        ph["rho_%s" % cname] = format(rho.quantize(Decimal("0.01")), "f")
        ph["n_%s" % cname] = str(len(pts))

    patterns = bd.fill(authored["patterns"], ph)
    for p in patterns:
        for key in ("supporting", "counterexamples"):
            for a in p.get(key, []):
                if a not in aliases:
                    raise bd.DiagnosisError("pattern %s: unknown alias %s" % (p["id"], a))
            p[key] = [by_id[aliases[a]]["search_term"] for a in p.get(key, [])]

    review = {
        "meta": {
            "step": "step2-review-%s" % authored.get("version", "v2"), "author": authored["author"],
            "supersedes": authored.get("supersedes"), "corrections": bd.fill(authored.get("corrections"), ph),
            "independent_of": "diagnosis v1 (preserved, not read for content)",
            "inputs": "supplied datasets via output/step1, config/account_context.json, methodology priors; no operator interview answers",
            "posture_selected": account["strategic_posture"]["selected"],
            "sources": {
                "step1_metrics_search_terms_sha256": bd.sha256_file(step1_dir / "metrics_search_terms.csv"),
                "step1_scope_summary_sha256": bd.sha256_file(step1_dir / "scope_summary.json"),
                "step1_checks_sha256": bd.sha256_file(step1_dir / "checks.json"),
                "account_context_sha256": bd.sha256_file(account_path),
                "authoring_sha256": bd.sha256_file(authoring_path),
            },
            "validation": {"aliases_resolved": len(aliases), "groups": len(groups_out), "correlations": len(corr_out),
                           "all_placeholders_resolved": True},
        },
        "observed_performance": term_table,
        "groups": groups_out,
        "correlations": corr_out,
        "patterns": patterns,
        "observed_vs_explanations": bd.fill(authored["observed_vs_explanations"], ph),
        "actions": bd.fill(authored["actions"], ph),
        "v1_review": bd.fill(authored["v1_review"], ph),
        "least_certain": bd.fill(authored["least_certain"], ph),
        "conditional_recommendations": bd.fill(authored.get("conditional_recommendations", []), ph),
        "negative_candidates": bd.fill(authored.get("negative_candidates", []), ph),
        "addition_isolation_candidates": bd.fill(authored.get("addition_isolation_candidates", []), ph),
        "term_missing_information": bd.fill(authored.get("term_missing_information", {}), ph),
        "term_evidence_notes": bd.fill(authored.get("term_evidence_notes", {}), ph),
        "term_intent_hypotheses": bd.fill(authored.get("term_intent_hypotheses", {}), ph),
        "channel_context_observations": bd.fill(authored.get("channel_context_observations", []), ph),
        "table_note": authored.get("table_note"),
        "method_note": bd.fill(authored["method_note"], ph),
    }
    for key in ("negative_candidates", "addition_isolation_candidates"):
        for item in review[key]:
            if item["alias"] not in aliases:
                raise bd.DiagnosisError("%s: unknown alias %s" % (key, item["alias"]))
            item["term_id"] = aliases[item["alias"]]
            item["search_term"] = by_id[aliases[item["alias"]]]["search_term"]
    for key in ("term_missing_information", "term_evidence_notes", "term_intent_hypotheses"):
        for alias in review[key]:
            if alias not in aliases:
                raise bd.DiagnosisError("%s: unknown alias %s" % (key, alias))
    for rec in review["conditional_recommendations"]:
        if rec.get("alias") and rec["alias"] not in aliases:
            raise bd.DiagnosisError("conditional_recommendations: unknown alias %s" % rec["alias"])
        if rec.get("alias"):
            rec["search_term"] = by_id[aliases[rec["alias"]]]["search_term"]
    return review


def render_md(d):
    L = ["# Braid Search Ops: evidence-led review %s (independent of v1)\n" % d["meta"]["step"].replace("step2-review-", ""),
         "Inputs: the two supplied datasets (via `output/step1/`), confirmed account context, methodology priors. "
         "No operator interview answers were used. v1 is preserved unchanged as the baseline. "
         "Posture: **%s**. All figures are filled from step 1 by `src/build_review_v2.py`.\n" % (d["meta"]["posture_selected"] or "not selected"),
         "## Observed performance (fact), sorted by spend\n",
         "| # | Term | Match | Cost | Signups | Subs | CPC | Cost/signup | Signup/click | Sub/signup | Cost/sub | vs $181 | Subs needed at $181 | Sub rate needed |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in d["observed_performance"]:
        n = t["numbers"]
        L.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            t["rank_by_cost"], t["search_term"], t["match_type_source"], bd.money(n["cost"]), bd.count(n["signup"]),
            bd.count(n["paid_sub"]), bd.money(n["cpc"]), bd.money(n["cost_per_signup"]), bd.pct(n["signup_per_click"]),
            bd.pct(n["paid_sub_per_signup"]), bd.money(n["cost_per_sub_recomputed"]), bd.times(n["ratio_to_allowable"]),
            bd.count(n["subs_needed_at_allowable"]), bd.pct(n["sub_rate_needed_at_allowable"])))
    L.append("\n" + (d.get("table_note") or "'Subs needed at $181' = ceil(cost / 181); 'sub rate needed' = that / signups. Arithmetic at current cost, not a forecast.") + "\n")
    L.append("## Groups (arithmetic over sample rows)\n")
    L.append("| Group | Terms | Cost | Subs | Cost/sub | Sub/signup | Share of sample cost | Share of sample subs |\n|---|---|---|---|---|---|---|---|")
    for g, v in d["groups"].items():
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (g, "; ".join(v["members"]), bd.money(v["cost"]), bd.count(v["paid_sub"]),
                 bd.money(v["cost_per_sub"]), bd.pct(v["sub_rate"]), bd.pct(v["cost_share"]), bd.pct(v["sub_share"])))
    if d["correlations"]:
        L.append("\n## Rank correlations (Spearman, n is small; direction only)\n")
        L.append("| Name | x | y | Excluded | n | rho |\n|---|---|---|---|---|---|")
        for c, v in d["correlations"].items():
            L.append("| %s | %s | %s | %s | %d | %s |" % (c, v["x"], v["y"], ", ".join(v["excluded"]) or "—", v["n"], v["spearman_rho"]))
    L.append("\n## Cross-term patterns\n")
    for p in d["patterns"]:
        L.append("### %s. %s\n" % (p["id"], p["title"]))
        L.append("**Observed (fact).** %s\n" % p["observed"])
        L.append("**Supporting terms:** %s  " % ", ".join(p["supporting"]))
        L.append("**Counterexamples:** %s\n" % (", ".join(p["counterexamples"]) or "none in the sample"))
        L.append("**Possible explanations (hypotheses, not ranked):**")
        for e in p["explanations"]:
            L.append("- " + e)
        L.append("\n**What would distinguish them:** %s\n" % p["distinguishing_evidence"])
    L.append("## Observed performance vs possible explanations\n")
    L.append("| Observation (fact) | Possible explanations (hypotheses) | Evidence that would settle it |\n|---|---|---|")
    for r in d["observed_vs_explanations"]:
        L.append("| %s | %s | %s |" % (r["observation"], r["explanations"], r["settling_evidence"]))
    L.append("\n## Actions\n")
    L.append("### Justified now on the supplied data alone\n")
    for a in d["actions"]["justified_now"]:
        L.append("- **%s** — %s" % (a["action"], a["why"]))
    L.append("\n### Requires more evidence before acting\n")
    L.append("| Candidate action | Missing evidence | Why it cannot be decided from the data |\n|---|---|---|")
    for a in d["actions"]["requires_evidence"]:
        L.append("| %s | %s | %s |" % (a["action"], a["needs"], a["why"]))
    L.append("\n## Review of v1 recommendations: unsupported assumptions\n")
    L.append("| v1 statement | Assumption not supported by the data | v2 position |\n|---|---|---|")
    for r in d["v1_review"]:
        L.append("| %s | %s | %s |" % (r["v1_statement"], r["unsupported_assumption"], r["v2_position"]))
    if d.get("conditional_recommendations"):
        L.append("\n## Conditional recommendations (what the data supports now, and what would change it)\n")
        L.append("| Term / decision | Current lean on supplied data | Changes the decision | Under scale | Under maintain efficiency |\n|---|---|---|---|---|")
        for r in d["conditional_recommendations"]:
            L.append("| %s | %s | %s | %s | %s |" % (r.get("search_term") or r["decision"], r["lean"], r["flips_if"], r["under_scale"], r["under_maintain_efficiency"]))
    L.append("\n## Least certain\n")
    lc = d["least_certain"]
    L.append(lc["text"] + "\n")
    for c in lc["candidates"]:
        L.append("- **%s** — %s" % (c["term"], c["why"]))
    L.append("\n## Method note\n")
    L.append(d["method_note"] + "\n")
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description="Search Ops step 2: build the independent v2 review.")
    p.add_argument("--step1-dir", type=Path, default=bd.DEFAULT_STEP1)
    p.add_argument("--account-context", type=Path, default=bd.DEFAULT_ACCOUNT)
    p.add_argument("--authoring", type=Path, default=DEFAULT_AUTHORING)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--name", default=None, help="output basename; defaults to review_<version> from the authoring file")
    args = p.parse_args(argv)
    try:
        d = build(args.step1_dir, args.account_context, args.authoring)
    except bd.DiagnosisError as exc:
        print("REVIEW ERROR: %s" % exc, file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    name = args.name or ("review_" + d["meta"]["step"].replace("step2-review-", "").replace(".", "_"))
    with open(args.output_dir / (name + ".json"), "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False, default=bd._json_default)
        fh.write("\n")
    (args.output_dir / (name + ".md")).write_text(render_md(d), encoding="utf-8")
    print("review %s built: %d patterns, %d groups, %d correlations -> %s"
          % (d["meta"]["step"].replace("step2-review-", ""), len(d["patterns"]), len(d["groups"]), len(d["correlations"]), args.output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
