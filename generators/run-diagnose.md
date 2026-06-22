# Generator — Run Diagnose  ⭐ THE CORE GENERATOR

**Paste this whole file into Claude, in this repo, after `criteria.yaml` is filled and reviewed (Phases 3–4).** It runs the full pipeline and writes `output/[ACCOUNT_SLUG]/[DATE]/insights.docx` + `output/[ACCOUNT_SLUG]/[DATE]/keyword-diagnose.xlsx`. (Phase 5 of SETUP.md.)

---

## Inputs

- `clients/[ACCOUNT_SLUG]/criteria.yaml` — read **`your_value`** for every threshold. If a `your_value` is null/missing, stop and tell the user to finish Phase 4 (do **not** silently fall back to `recommended`).
- `clients/[ACCOUNT_SLUG]/{account-context,conversion-goals,benchmarks,current-problems,brand-terms}.md` — for the bidding-signal/KPI conversion names, benchmark reference lines, and the Insights Doc narrative.
- `data-inputs/[ACCOUNT_SLUG]/` — all 6 files:
  - `keyword-report-L6M.csv` — keyword performance (UTF-16, tab-delimited)
  - `campaign-report-L6M.csv` — campaign performance (incl. IS Lost Budget)
  - `search-terms-L3M.csv` — search terms, 3 months (the action window)
  - `search-terms-L6M.csv` — search terms, 6 months (Campaign Health Source mix only)
  - `asset-association-L3M.csv` — RSA + PMax assets (Level column)
  - `brand-terms.md` — brand manifest
- Methodology: `diagnose/SKILL.md`, `diagnose/bucket-definitions.md`, `diagnose/pmax-intent-clustering.md`, `diagnose/data-window-rationale.md`, `diagnose/reading-the-output.md`.

## Outputs

```
output/[ACCOUNT_SLUG]/[YYYY-MM-DD]/insights.docx        # ~4 pages
output/[ACCOUNT_SLUG]/[YYYY-MM-DD]/keyword-diagnose.xlsx # ~14 sheets
```

## Logic flow (what the code below does)

1. **Load `criteria.yaml`** — pull every `your_value` into a flat dict; abort on any missing. Also read `meta.posture` (Efficiency / Scale / Calibration) and surface it on the Summary sheet and the Insights Doc — the CPA targets are that posture encoded as numbers, so the reader needs to see it up front.
2. **Load the 6 inputs** — keyword (L6M), campaign (L6M), search-terms-L3M, search-terms-L6M, asset-association-L3M, brand-terms. Apply hygiene: drop `Total: …` rows; drop `Source = Unknown` STR rows; coerce numerics; normalize conversion-action column names to `fft` (bidding signal) and `kpi` (business KPI) plus `signup` (top-of-funnel proxy) using the names from `conversion-goals.md`.
3. **Classify campaign type** for every campaign from `campaign_type_rules` (first substring match wins; else `non_brand`); attach the right CPA targets to each keyword.
4. **Keyword-level bucketing** — run the 8-bucket logic from `bucket-definitions.md` per keyword, using per-campaign-type CPA targets and IS-Lost gates; record the bucket, the sub-cause, and the inputs that triggered it.
5. **Generate the Fix Action string** for every Fix → Keep keyword from the templates in `bucket-definitions.md §2`, populated with that keyword's numbers.
6. **Campaign-level health** — aggregate per campaign; compute the STR Source mix from `search-terms-L6M.csv` (PMax / Search keyword / AI Max / DSA share of cost) and a drift note; compute IS Lost Budget from the campaign report; pick a Top Issue + Recommended Action per campaign.
7. **PMax intent clustering** — match `search-terms-L3M.csv` rows with `Source == "Performance Max"` against `pmax-intent-clustering.md`; per PMax campaign report visible-query %, top clusters by spend, top converting cluster.
8. **New Keyword Suggestions** — run the 3-tier logic (below) on `search-terms-L3M.csv`.
9. **Cannibalization** — queries converting on both PMax and Search in `search-terms-L3M.csv`; pick winner per `E_cannibalization`.
10. **Build the Excel** — 14 sheets with conditional formatting (red the CPA/target-ratio and IS-Lost columns).
11. **Build the Word doc** — Account at a glance (active posture + 4 metrics) · 5 data-driven key findings (ranked by spend-at-stake) · Data health & open questions.

## ⭐ New Keyword Suggestions — exact tier logic

Run on `search-terms-L3M.csv`. For a query `q` with campaign-type CPA target `T_fft` (the bidding-signal target of the campaign/ad-group it surfaced under):

- **Exclude entirely** if any of: `Source == "Unknown"`; `q` matches a brand term (from `brand-terms.md`); `len(q.split()) < new_kw_min_query_length_words`; `cost(q) < new_kw_min_cost`; `q` already exists as a Search **exact** or **phrase** keyword.
- **Strict tier** — `Source in {"Performance Max", "AI Max"}` AND `fft(q) >= new_kw_strict_min_fft` AND `fft_cpa(q) <= T_fft * new_kw_strict_cpa_ratio` AND not already a Search exact/phrase keyword.
- **Moderate tier** — same as Strict but `fft_cpa(q) <= T_fft * new_kw_moderate_cpa_ratio` (and it didn't qualify for Strict).
- **Aggressive tier** — `Source == "Search keyword"` (a query already matching a Search keyword, usually broad) AND `clicks(q) >= new_kw_aggressive_min_clicks` AND `fft(q) >= new_kw_aggressive_min_fft` AND `q` is a close variant (token-overlap / Levenshtein) of an existing Search keyword that it's *not* already an exact/phrase form of.
- Each suggested row carries: query, source, suggested match type **for the new keyword** (phrase by default; exact if the query is tight and high-intent), tier, clicks/cost/fft/fft_cpa, the existing keyword it's a variant of (Aggressive only), and a suggested destination campaign (the highest-FFT non-brand Search campaign matching the query's intent cluster).
- This sheet **never** recommends changing the match type of an existing keyword and **never** says a campaign "should be" exact/phrase/broad-dominant — that's the deferred Match-Type logic. It only suggests *queries to add*.

## Embedded code

> The script below is the reference implementation. It expects `pandas`, `openpyxl`, `python-docx`, `pyyaml` (`pip install pandas openpyxl python-docx pyyaml`). It's deliberately self-contained — read the inline comments; adjust column-name constants near the top to match the account's exact Google Ads export headers. Anything it can't compute confidently (e.g. a `[VERIFY]` context value) it records in the data-health block rather than guessing.

```python
#!/usr/bin/env python3
"""run-diagnose.py — keyword-diagnose-v2 core generator.

Usage:
    python run-diagnose.py --slug ACCOUNT_SLUG [--date YYYY-MM-DD] [--repo .]

Reads clients/<slug>/criteria.yaml (your_value fields) + the 6 data-inputs/<slug>/ files,
writes output/<slug>/<date>/{insights.docx, keyword-diagnose.xlsx}.
"""
from __future__ import annotations
import argparse, datetime as dt, os, re, sys
from pathlib import Path
import yaml
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from docx import Document
from docx.shared import Pt

# ---------------------------------------------------------------------------
# 0. Config — adjust these to match the account's exact export headers if needed
# ---------------------------------------------------------------------------
COL = {  # canonical -> list of acceptable header spellings (first match wins)
    "keyword":      ["Keyword", "Search keyword"],
    "match_type":   ["Match type", "Keyword match type"],
    "campaign":     ["Campaign"],
    "ad_group":     ["Ad group", "Ad group name"],
    "status":       ["Status", "Keyword status", "Campaign status"],
    "cost":         ["Cost", "Cost (USD)"],
    "clicks":       ["Clicks"],
    "impr":         ["Impr.", "Impressions"],
    "max_cpc":      ["Max. CPC", "Max CPC"],
    "is_lost_rank": ["Search lost IS (rank)", "Search Lost IS (rank)"],
    "is_lost_budget":["Search lost IS (budget)", "Search Lost IS (budget)"],
    "qs":           ["Quality Score", "Quality score"],
    "exp_ctr":      ["Exp. CTR", "Expected CTR"],
    "lp_exp":       ["Landing page exp.", "Landing page experience"],
    "ad_rel":       ["Ad relevance"],
    "campaign_type":["Campaign type"],
    "budget":       ["Budget", "Budget amount"],
    "source":       ["Source", "Search keyword source"],
    "search_term":  ["Search term"],
    "level":        ["Level"],
    "asset":        ["Asset"],
    "asset_type":   ["Asset type"],
}

def pick(df, canon):
    for name in COL[canon]:
        if name in df.columns:
            return name
    return None

def num(s):
    """Coerce a Google-Ads-formatted cell to float ('1,234.5', '12.3%', '--', '< 10%' -> float/NaN)."""
    if pd.isna(s): return float("nan")
    t = str(s).strip().replace(",", "").replace("$", "")
    if t in {"--", "", "-", "—"}: return float("nan")
    t = t.replace("< ", "").replace("> ", "").replace("%", "")
    try: return float(t)
    except ValueError: return float("nan")

def read_csv_smart(path: Path) -> pd.DataFrame:
    """Try UTF-16 tab-delimited first (the keyword report), then UTF-8 CSV."""
    for kwargs in ({"encoding": "utf-16", "sep": "\t"}, {"encoding": "utf-8-sig"}, {"encoding": "utf-8"}):
        try:
            df = pd.read_csv(path, dtype=str, **kwargs)
            if df.shape[1] > 1:
                return df
        except Exception:
            continue
    raise RuntimeError(f"Could not parse {path}")

def drop_total_rows(df: pd.DataFrame) -> pd.DataFrame:
    first = df.columns[0]
    return df[~df[first].astype(str).str.startswith("Total: ")].copy()

# ---------------------------------------------------------------------------
# 1. criteria.yaml
# ---------------------------------------------------------------------------
def load_criteria(repo: Path, slug: str) -> dict:
    raw = yaml.safe_load((repo / "clients" / slug / "criteria.yaml").read_text())
    flat, missing = {}, []
    def walk(node, prefix=""):
        if isinstance(node, dict):
            if set(node) >= {"recommended", "rationale", "your_value"}:
                key = prefix.rstrip(".")
                flat[key] = node["your_value"]
                if node["your_value"] is None:
                    missing.append(key)
            else:
                for k, v in node.items():
                    walk(v, f"{prefix}{k}.")
    walk(raw)
    if missing:
        sys.exit("criteria.yaml has un-set your_value fields (finish Phase 4 first):\n  " +
                 "\n  ".join(missing))
    flat["_raw"] = raw
    flat["campaign_type_rules"] = raw["B_cpa_targets"]["campaign_type_rules"]
    flat["custom_tiers"] = raw["B_cpa_targets"].get("custom_tiers", []) or []
    return flat

# ---------------------------------------------------------------------------
# 2. context (conversion names, brand terms)
# ---------------------------------------------------------------------------
def load_context(repo: Path, slug: str) -> dict:
    cdir = repo / "clients" / slug
    ctx = {p.stem: (cdir / p.name).read_text() for p in cdir.glob("*.md")}
    # bidding signal / KPI / signup proxy conversion-action names — parsed from conversion-goals.md
    cg = ctx.get("conversion-goals", "")
    def grab(label):
        m = re.search(rf"{label}.*?`([^`]+)`", cg, re.S | re.I)
        return m.group(1).strip() if m else None
    ctx["_fft_action"]   = grab(r"Bidding signal.*?Conversion action name")
    ctx["_kpi_action"]   = grab(r"Business KPI.*?Conversion action name")
    ctx["_signup_action"]= grab(r"top-of-funnel proxy.*?`|Signed Up")  # best-effort
    # brand terms
    bt = (repo / "data-inputs" / slug / "brand-terms.md")
    bt_text = bt.read_text() if bt.exists() else ctx.get("brand-terms", "")
    terms, excludes = [], []
    section = None
    for line in bt_text.splitlines():
        l = line.strip()
        if l.lower().startswith("## not brand"): section = "exclude"; continue
        if l.startswith("## "): section = "include"; continue
        if l.startswith("- "):
            term = re.sub(r"\s*[←#].*$", "", l[2:]).split("/")[0].strip().lower()
            term = term.strip("* ").replace(" * ", " ")
            if not term or "*" in term: continue
            (excludes if section == "exclude" else terms).append(term)
    ctx["_brand_terms"] = sorted(set(terms))
    ctx["_brand_excludes"] = sorted(set(excludes))
    ctx["_verify_count"] = sum(t.count("[VERIFY") for t in ctx.values() if isinstance(t, str))
    return ctx

def is_brand(text: str, ctx: dict) -> bool:
    t = (text or "").lower()
    if any(e and e in t for e in ctx["_brand_excludes"]): return False
    return any(b and b in t for b in ctx["_brand_terms"])

# ---------------------------------------------------------------------------
# 3. campaign typing + CPA target lookup
# ---------------------------------------------------------------------------
def campaign_type(name: str, rules: list) -> str:
    n = (name or "").lower()
    for rule in rules:
        if any(s.lower() in n for s in rule.get("match_campaign_contains", [])):
            return rule["type"]
    return "non_brand"

def targets_for(ctype: str, crit: dict) -> tuple[float, float]:
    base = f"B_cpa_targets.per_campaign_type.{ctype}"
    fft = crit.get(f"{base}.target_fft_cpa", crit["B_cpa_targets.target_fft_cpa_blended"])
    kpi = crit.get(f"{base}.target_kpi_cpa", crit["B_cpa_targets.target_kpi_cpa_blended"])
    return float(fft), float(kpi)

def is_lost_fix_gate(ctype: str, crit: dict) -> float:
    ov = crit.get(f"C_is_lost_rank_gates.per_campaign_type_overrides.{ctype}.is_lost_rank_fix_flag")
    return float(ov if ov is not None else crit["C_is_lost_rank_gates.is_lost_rank_fix_flag"])

# ---------------------------------------------------------------------------
# 4. load the 6 inputs
# ---------------------------------------------------------------------------
def load_inputs(repo: Path, slug: str, ctx: dict):
    d = repo / "data-inputs" / slug
    kw  = drop_total_rows(read_csv_smart(d / "keyword-report-L6M.csv"))
    cmp_= drop_total_rows(read_csv_smart(d / "campaign-report-L6M.csv"))
    st3 = drop_total_rows(read_csv_smart(d / "search-terms-L3M.csv"))
    st6 = drop_total_rows(read_csv_smart(d / "search-terms-L6M.csv"))
    aa  = drop_total_rows(read_csv_smart(d / "asset-association-L3M.csv"))
    # drop Source = Unknown from STR
    for df in (st3, st6):
        sc = pick(df, "source")
        if sc: df.drop(df[df[sc].astype(str).str.strip().str.lower() == "unknown"].index, inplace=True)
    # map conversion columns -> fft / kpi / signup
    def conv_col(df, action_name):
        if not action_name: return None
        for c in df.columns:
            if c.strip().lower() == action_name.strip().lower(): return c
        # tolerate "[Offline]" suffix differences
        base = re.sub(r"\s*\[.*?\]\s*$", "", action_name).strip().lower()
        for c in df.columns:
            if re.sub(r"\s*\[.*?\]\s*$", "", c).strip().lower() == base: return c
        return None
    for df in (kw, cmp_, st3, st6):
        df["_fft"]    = df[conv_col(df, ctx["_fft_action"])].map(num)    if conv_col(df, ctx["_fft_action"])    else 0.0
        df["_kpi"]    = df[conv_col(df, ctx["_kpi_action"])].map(num)    if conv_col(df, ctx["_kpi_action"])    else 0.0
        df["_signup"] = df[conv_col(df, ctx["_signup_action"])].map(num) if conv_col(df, ctx["_signup_action"]) else 0.0
        for cn in ("cost", "clicks", "impr"):
            col = pick(df, cn)
            if col: df["_" + cn] = df[col].map(num)
    return dict(kw=kw, cmp=cmp_, st3=st3, st6=st6, aa=aa)

# ---------------------------------------------------------------------------
# 5. keyword-level bucketing  (implements diagnose/bucket-definitions.md)
# ---------------------------------------------------------------------------
def bucket_keywords(kw: pd.DataFrame, crit: dict, ctx: dict) -> pd.DataFrame:
    rows = []
    c_kw, c_cmp, c_ag = pick(kw, "keyword"), pick(kw, "campaign"), pick(kw, "ad_group")
    c_mt, c_st = pick(kw, "match_type"), pick(kw, "status")
    c_islr, c_qs = pick(kw, "is_lost_rank"), pick(kw, "qs")
    c_lp, c_ctr, c_ar = pick(kw, "lp_exp"), pick(kw, "exp_ctr"), pick(kw, "ad_rel")
    spend_min   = float(crit["A_spend_and_signal_floors.spend_min_30d"])
    fft_min     = float(crit["A_spend_and_signal_floors.fft_min_for_signal"])
    signup_min  = float(crit["A_spend_and_signal_floors.signup_min_for_top_of_funnel"])
    pause_spend = float(crit["G_bucketing_tiebreakers.pause_threshold_spend_no_fft"])
    dormant     = float(crit["G_bucketing_tiebreakers.dormant_definition"])
    qs_sev, qs_watch, qs_clear = (float(crit["D_quality_score_gates.qs_severe"]),
                                  float(crit["D_quality_score_gates.qs_watchlist"]),
                                  float(crit["D_quality_score_gates.qs_clear"]))
    hs_islr = float(crit["C_is_lost_rank_gates.is_lost_rank_high_spend_alert"])
    rules = crit["campaign_type_rules"]

    for _, r in kw.iterrows():
        if c_st and str(r.get(c_st, "")).strip().lower() not in {"enabled", "eligible", ""}:
            continue
        camp = str(r.get(c_cmp, ""))
        ctype = campaign_type(camp, rules)
        t_fft, t_kpi = targets_for(ctype, crit)
        cost = float(r.get("_cost", 0) or 0); cost30 = cost / 6.0
        fft  = float(r.get("_fft", 0) or 0);  signup = float(r.get("_signup", 0) or 0)
        islr = num(r.get(c_islr)) if c_islr else float("nan")
        qs   = num(r.get(c_qs)) if c_qs else float("nan")
        lp   = str(r.get(c_lp, "")).strip() if c_lp else ""
        cpa  = (cost / fft) if fft > 0 else float("nan")
        ratio= (cpa / t_fft) if fft > 0 else float("nan")
        gate = is_lost_fix_gate(ctype, crit)

        bucket, subcause, action, secondary = "Monitor (low data)", "", "", ""
        # --- dormant / low data
        if cost < dormant and fft == 0 and signup == 0:
            bucket, action = "Monitor (low data)", f"${cost30:.2f}/30d, no signal. Hold."
        # --- pause: real spend, zero bidding-signal conversions
        elif fft == 0 and cost >= pause_spend:
            bucket = "Pause"
            action = f"Spent ${cost:.0f} over L6M, 0 bidding-signal conversions. Pause or hard-cap; mine its search terms for negatives."
        # --- has top-of-funnel signal but not enough bidding signal / spend
        elif fft < fft_min and cost30 < spend_min:
            if signup >= signup_min:
                bucket, action = "Monitor (has signal)", f"Thin spend (${cost30:.2f}/30d) but {signup:.0f} top-of-funnel events. Hold; re-check next run."
            else:
                bucket, action = "Monitor (low data)", f"${cost30:.2f}/30d, {fft:.0f} bidding-signal. Below floors. Hold."
        else:
            # --- has signal: judge on CPA
            if fft >= fft_min and not pd.isna(cpa):
                if cpa <= t_fft and (pd.isna(islr) or islr < gate):
                    bucket = "Keep in Search"
                    action = f"Healthy — converts at ${cpa:.0f} vs ${t_fft:.0f} target, IS Lost (Rank) {islr:.0f}%. No action."
                elif cpa <= t_fft and islr >= gate:
                    bucket, subcause = "Fix → Keep in Search", "Fix-Bid"
                    action = f"Raise tCPA to ~${t_fft:.0f} — converts at ${cpa:.0f}, IS Lost (Rank) {islr:.0f}%. Affordable share being lost."
                else:  # over target — find a lever
                    if not pd.isna(qs) and qs <= qs_sev:
                        weak = min([("Exp. CTR", str(r.get(c_ctr, ""))), ("Landing page exp.", lp), ("Ad relevance", str(r.get(c_ar, "")))],
                                   key=lambda x: 0 if "below" in x[1].lower() else 1)[0]
                        bucket, subcause = "Fix → Keep in Search", "Fix-QS"
                        action = f"QS={qs:.0f} (weakest: {weak}). Fix {weak} before bidding up — converts at ${cpa:.0f} vs ${t_fft:.0f} target."
                    elif "below" in lp.lower():
                        bucket, subcause = "Fix → Keep in Search", "Fix-LP"
                        action = f"Landing page exp. Below average. Route to a page about “{r.get(c_kw,'')}” instead of the generic LP; re-check QS in 2 weeks."
                    elif len(str(r.get(c_kw, "")).split()) >= 4 and ratio >= float(crit["E_cannibalization.both_losing_threshold"]):
                        bucket = "Move to PMax"
                        action = f"Spends ${cost:.0f} at ${cpa:.0f} CPA (target ${t_fft:.0f}); long-tail intent. Move to PMax, add as Search negative — if PMax serves it at/under target (check PMax Intent sheet)."
                    elif ratio <= 1.5:
                        bucket, subcause = "Fix → Decide", "Fix-CPA?"
                        action = f"Borderline: converts at ${cpa:.0f} (target ${t_fft:.0f}), QS={qs if not pd.isna(qs) else 'n/a'}. Likely lever: tCPA trim. Decide after next refresh."
                    else:
                        bucket, subcause = "Fix → Keep in Search", "Fix-CPA"
                        action = f"Converts at ${cpa:.0f} vs ${t_fft:.0f} target, no QS/LP lever. Lower tCPA toward ${t_fft:.0f} (expect fewer conversions) or move the query to PMax."
                if not pd.isna(qs) and qs_sev < qs <= qs_watch and bucket.startswith("Fix"):
                    secondary = (secondary + "; " if secondary else "") + f"QS={qs:.0f} watchlist"
            else:
                bucket, action = "Monitor (low data)", f"${cost30:.2f}/30d, {fft:.0f} bidding-signal. Below floors. Hold."

        high_spend_alert = (not pd.isna(islr) and islr >= hs_islr and cost >= 3 * t_fft and fft == 0) or \
                           (not pd.isna(islr) and islr >= hs_islr and not pd.isna(ratio) and ratio >= 3)
        rows.append(dict(Keyword=r.get(c_kw, ""), MatchType=r.get(c_mt, ""), Campaign=camp,
                         AdGroup=r.get(c_ag, ""), CampaignType=ctype, Cost=round(cost, 2), Cost30d=round(cost30, 2),
                         BiddingSignalConv=fft, BiddingSignalCPA=(round(cpa, 2) if not pd.isna(cpa) else None),
                         CPAvsTarget=(round(ratio, 2) if not pd.isna(ratio) else None), TargetFFTCPA=t_fft,
                         ISLostRank=(round(islr, 1) if not pd.isna(islr) else None), QS=(qs if not pd.isna(qs) else None),
                         LPexp=lp, Bucket=bucket, SubCause=subcause, FixAction=action,
                         SecondarySubCauses=secondary, HighSpendAlert=high_spend_alert))
    return pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# 6. campaign-level health  (Source mix from L6M STR)
# ---------------------------------------------------------------------------
SOURCE_LABELS = {"search keyword": "Search", "performance max": "PMax", "ai max": "AI Max",
                 "dynamic search ad": "DSA", "dynamic search ads": "DSA", "search partners": "Search"}

def campaign_health(inp, kbuckets: pd.DataFrame, crit: dict) -> pd.DataFrame:
    cmp_ = inp["cmp"]; st6 = inp["st6"]; st3 = inp["st3"]
    c_name, c_type = pick(cmp_, "campaign"), pick(cmp_, "campaign_type")
    c_islb, c_islr = pick(cmp_, "is_lost_budget"), pick(cmp_, "is_lost_rank")
    c_st = pick(cmp_, "status")
    rules = crit["campaign_type_rules"]
    # source mix per campaign from L6M STR
    sc, cc, costc = pick(st6, "source"), pick(st6, "campaign"), "_cost"
    mix = {}
    if sc and cc:
        g = st6.copy(); g["_lbl"] = g[sc].astype(str).str.strip().str.lower().map(lambda s: SOURCE_LABELS.get(s, "Other"))
        for camp, sub in g.groupby(cc):
            tot = sub[costc].sum() or 1.0
            mix[camp] = {lbl: f"{(s[costc].sum()/tot*100):.0f}%" for lbl, s in sub.groupby("_lbl")}
    # pmax visible % (rough: distinct visible queries vs campaign clicks proxy) + top intent — see clustering fn
    rows = []
    for _, r in cmp_.iterrows():
        camp = str(r.get(c_name, "")); ctype = campaign_type(camp, rules)
        channel = "PMax" if "performance max" in str(r.get(c_type, "")).lower() or "performancemax" in camp.lower() else \
                  "AI Max" if "ai max" in str(r.get(c_type, "")).lower() else "Search"
        cost = float(r.get("_cost", 0) or 0); fft = float(r.get("_fft", 0) or 0)
        cpa = (cost / fft) if fft > 0 else float("nan")
        islb, islr = num(r.get(c_islb)) if c_islb else float("nan"), num(r.get(c_islr)) if c_islr else float("nan")
        t_fft, _ = targets_for(ctype, crit)
        # top issue
        issue, rec = "—", "Monitor"
        sub = kbuckets[kbuckets.Campaign == camp]
        if channel == "Search":
            if not sub.empty and (sub.Bucket == "Pause").mean() > 0.3:
                issue, rec = "Many keywords spending without converting", "Audit & pause non-converters; mine search terms for negatives"
            if not pd.isna(islb) and islb >= 20:
                issue, rec = f"Budget-constrained (IS Lost Budget {islb:.0f}%)", "Raise daily budget or it can't enter the auction"
            if not pd.isna(islr) and islr > 80 and (pd.isna(islb) or islb < 10):
                issue, rec = f"Can't win the auction (IS Lost Rank {islr:.0f}%, Budget low)", "tCPA likely too strict — loosen or restructure; campaign isn't serving"
            if not pd.isna(cpa) and cpa > 1.5 * t_fft:
                issue, rec = f"Over CPA target (${cpa:.0f} vs ${t_fft:.0f})", "Tighten keyword set; see Fix sheets"
        else:
            issue, rec = "PMax — see PMax Intent sheet for cluster mix", "Review intent clusters; add negatives for off-target clusters"
        rows.append(dict(Campaign=camp, Type=ctype, Channel=channel,
                         Status=str(r.get(c_st, "")), Spend=round(cost, 2), BiddingSignalConv=fft,
                         BiddingSignalCPA=(round(cpa, 2) if not pd.isna(cpa) else None),
                         ISLostRank=(round(islr, 1) if not pd.isna(islr) else None),
                         ISLostBudget=(round(islb, 1) if not pd.isna(islb) else None),
                         TopIssue=issue, RecommendedAction=rec,
                         STRSignal=("Source mix: " + " / ".join(f"{k} {v}" for k, v in mix.get(camp, {}).items())
                                    if channel == "Search" else "see PMax Intent")))
    return pd.DataFrame(rows)

# ---------------------------------------------------------------------------
# 7. PMax intent clustering  (reads diagnose/pmax-intent-clustering.md)
# ---------------------------------------------------------------------------
def load_clusters(repo: Path) -> list[tuple[str, list[str]]]:
    txt = (repo / "diagnose" / "pmax-intent-clustering.md").read_text()
    clusters, cur = [], None
    for line in txt.splitlines():
        m = re.match(r"###\s+\d+\.\s+(.*)", line.strip())
        if m: cur = m.group(1).strip(); continue
        mm = re.match(r"-\s*\*\*Match keywords:\*\*\s*(.*)", line.strip())
        if mm and cur:
            kws = [re.sub(r"[`*]", "", k).strip().lower() for k in mm.group(1).split(",")]
            clusters.append((cur, [k for k in kws if k]))
            cur = None
    return clusters

def cluster_of(query: str, clusters) -> str:
    q = (query or "").lower()
    for name, kws in clusters:
        if any(k and k in q for k in kws): return name
    return "Other / unclassified"

def pmax_intent(inp, crit: dict, repo: Path) -> pd.DataFrame:
    st3 = inp["st3"]; sc, cc, tc = pick(st3, "source"), pick(st3, "campaign"), pick(st3, "search_term")
    if not (sc and cc and tc): return pd.DataFrame()
    clusters = load_clusters(repo)
    pmx = st3[st3[sc].astype(str).str.strip().str.lower() == "performance max"].copy()
    if pmx.empty: return pd.DataFrame()
    pmx["_cluster"] = pmx[tc].map(lambda q: cluster_of(q, clusters))
    rows = []
    for camp, sub in pmx.groupby(cc):
        tot_cost = sub["_cost"].sum() or 1.0
        # visible-query % proxy: visible STR cost / campaign cost (campaign cost from cmp report)
        camp_cost = inp["cmp"].loc[inp["cmp"][pick(inp["cmp"], "campaign")] == camp, "_cost"]
        camp_cost = float(camp_cost.iloc[0]) if len(camp_cost) else tot_cost
        vis_pct = min(100.0, tot_cost / (camp_cost or tot_cost) * 100.0)
        for cl, s in sub.groupby("_cluster"):
            rows.append(dict(Campaign=camp, Cluster=cl, Cost=round(s["_cost"].sum(), 2),
                             Clicks=int(s["_clicks"].sum()), BiddingSignalConv=float(s["_fft"].sum()),
                             BiddingSignalCPA=(round(s["_cost"].sum()/s["_fft"].sum(), 2) if s["_fft"].sum() > 0 else None),
                             ShareOfCampaignCost=f"{s['_cost'].sum()/tot_cost*100:.0f}%",
                             VisibleQueryPct=f"{vis_pct:.0f}%"))
    return pd.DataFrame(rows).sort_values(["Campaign", "Cost"], ascending=[True, False])

# ---------------------------------------------------------------------------
# 8. New Keyword Suggestions  (3 tiers — see this file's "exact tier logic")
# ---------------------------------------------------------------------------
def new_keyword_suggestions(inp, crit: dict, ctx: dict) -> pd.DataFrame:
    st3 = inp["st3"]; sc, cc, tc = pick(st3, "source"), pick(st3, "campaign"), pick(st3, "search_term")
    kw = inp["kw"]; kkw, kmt = pick(kw, "keyword"), pick(kw, "match_type")
    rules = crit["campaign_type_rules"]
    exact_phrase = set()
    for _, r in kw.iterrows():
        if str(r.get(kmt, "")).strip().lower() in {"exact", "exact match", "phrase", "phrase match"}:
            exact_phrase.add(str(r.get(kkw, "")).strip().lower())
    all_search_kws = set(str(r.get(kkw, "")).strip().lower() for _, r in kw.iterrows())
    min_words = int(crit["F_new_keyword_suggestions.new_kw_min_query_length_words"])
    min_cost  = float(crit["F_new_keyword_suggestions.new_kw_min_cost"])
    s_fft     = float(crit["F_new_keyword_suggestions.new_kw_strict_min_fft"])
    s_ratio   = float(crit["F_new_keyword_suggestions.new_kw_strict_cpa_ratio"])
    m_ratio   = float(crit["F_new_keyword_suggestions.new_kw_moderate_cpa_ratio"])
    a_clicks  = float(crit["F_new_keyword_suggestions.new_kw_aggressive_min_clicks"])
    a_fft     = float(crit["F_new_keyword_suggestions.new_kw_aggressive_min_fft"])
    def close_variant(q):
        qt = set(q.lower().split())
        for k in all_search_kws:
            kt = set(k.split())
            if k != q.lower() and qt and kt and len(qt & kt) / len(qt | kt) >= 0.6:
                return k
        return None
    rows = []
    for _, r in st3.iterrows():
        q = str(r.get(tc, "")).strip(); src = str(r.get(sc, "")).strip()
        cost = float(r.get("_cost", 0) or 0); clk = float(r.get("_clicks", 0) or 0); fft = float(r.get("_fft", 0) or 0)
        ql = q.lower()
        if not q or src.lower() == "unknown": continue
        if is_brand(q, ctx): continue
        if len(q.split()) < min_words or cost < min_cost: continue
        if ql in exact_phrase: continue
        ctype = campaign_type(str(r.get(cc, "")), rules); t_fft, _ = targets_for(ctype, crit)
        cpa = (cost / fft) if fft > 0 else float("nan")
        tier = sugg_mt = variant_of = None
        if src.lower() in {"performance max", "ai max"} and fft >= s_fft and not pd.isna(cpa) and cpa <= t_fft * s_ratio:
            tier, sugg_mt = "Strict", ("Exact" if len(q.split()) <= 4 else "Phrase")
        elif src.lower() in {"performance max", "ai max"} and fft >= s_fft and not pd.isna(cpa) and cpa <= t_fft * m_ratio:
            tier, sugg_mt = "Moderate", "Phrase"
        elif src.lower() in {"search keyword", "search partners"} and clk >= a_clicks and fft >= a_fft:
            v = close_variant(ql)
            if v: tier, sugg_mt, variant_of = "Aggressive", "Phrase", v
        if not tier: continue
        rows.append(dict(Query=q, Source=src, SuggestedMatchTypeForNewKeyword=sugg_mt, Tier=tier,
                         Clicks=int(clk), Cost=round(cost, 2), BiddingSignalConv=fft,
                         BiddingSignalCPA=(round(cpa, 2) if not pd.isna(cpa) else None),
                         CampaignType=ctype, VariantOfExistingKeyword=variant_of,
                         SuggestedDestinationCampaign=str(r.get(cc, ""))))
    order = {"Strict": 0, "Moderate": 1, "Aggressive": 2}
    df = pd.DataFrame(rows)
    return df.sort_values(["Tier", "Cost"], key=lambda s: s.map(order) if s.name == "Tier" else s,
                          ascending=[True, False]) if not df.empty else df

# ---------------------------------------------------------------------------
# 9. PMax–Search cannibalization
# ---------------------------------------------------------------------------
def cannibalization(inp, crit: dict) -> pd.DataFrame:
    st3 = inp["st3"]; sc, tc = pick(st3, "source"), pick(st3, "search_term")
    if not (sc and tc): return pd.DataFrame()
    g = st3.copy(); g["_lbl"] = g[sc].astype(str).str.strip().str.lower()
    g = g[g["_lbl"].isin(["performance max", "search keyword", "search partners"])]
    g["_lbl"] = g["_lbl"].map(lambda s: "PMax" if s == "performance max" else "Search")
    margin = float(crit["E_cannibalization.winning_margin"])
    min_fft = float(crit["E_cannibalization.min_fft_either_side"])
    both_lose = float(crit["E_cannibalization.both_losing_threshold"])
    min_spend = float(crit["E_cannibalization.min_combined_spend"])
    rows = []
    for q, sub in g.groupby(g[tc].astype(str).str.lower()):
        piv = sub.groupby("_lbl").agg(cost=("_cost", "sum"), fft=("_fft", "sum")).to_dict("index")
        if "PMax" not in piv or "Search" not in piv: continue
        p, s = piv["PMax"], piv["Search"]
        if min(p["fft"], s["fft"]) < min_fft: continue
        if (p["cost"] + s["cost"]) < min_spend: continue
        pc = p["cost"]/p["fft"] if p["fft"] else float("inf"); scpa = s["cost"]/s["fft"] if s["fft"] else float("inf")
        # need a target — use non_brand blended (query-level type is fuzzy)
        t_fft = float(crit["B_cpa_targets.per_campaign_type.non_brand.target_fft_cpa"])
        if pc > t_fft*both_lose and scpa > t_fft*both_lose:
            verdict, winner = "Both losing — kill the query on both channels", "—"
        elif pc <= scpa*(1-margin):
            verdict, winner = "Let PMax own it — add the query as a Search negative", "PMax"
        elif scpa <= pc*(1-margin):
            verdict, winner = "Let Search own it — exclude/negative on the PMax side", "Search"
        else:
            verdict, winner = "No clear winner — monitor", "—"
        rows.append(dict(Query=q, PMaxCost=round(p["cost"],2), PMaxConv=p["fft"], PMaxCPA=(round(pc,2) if pc!=float('inf') else None),
                         SearchCost=round(s["cost"],2), SearchConv=s["fft"], SearchCPA=(round(scpa,2) if scpa!=float('inf') else None),
                         Winner=winner, Verdict=verdict))
    return pd.DataFrame(rows).sort_values(["PMaxCost"], ascending=False) if rows else pd.DataFrame()

# ---------------------------------------------------------------------------
# 10. Excel
# ---------------------------------------------------------------------------
HDR_FILL = PatternFill("solid", fgColor="1F4E78"); HDR_FONT = Font(bold=True, color="FFFFFF")
RED = PatternFill("solid", fgColor="F8CBAD"); AMBER = PatternFill("solid", fgColor="FFE699")

def _sheet(wb, name, df, note=None, red_cols=()):
    ws = wb.create_sheet(name[:31])
    if note: ws.append([note]); ws.append([])
    if df is None or df.empty:
        ws.append(["(no rows)"]); return
    ws.append(list(df.columns))
    for c in range(1, len(df.columns)+1):
        cell = ws.cell(row=ws.max_row, column=c); cell.fill = HDR_FILL; cell.font = HDR_FONT
    for _, r in df.iterrows():
        ws.append(list(r.values))
        for cn in red_cols:
            if cn in df.columns:
                ci = list(df.columns).index(cn)+1; v = ws.cell(row=ws.max_row, column=ci).value
                try:
                    fv = float(v)
                    if cn.lower().startswith("cpavstarget") and fv >= 2: ws.cell(row=ws.max_row, column=ci).fill = RED
                    elif cn.lower().startswith("cpavstarget") and fv > 1: ws.cell(row=ws.max_row, column=ci).fill = AMBER
                    if cn.lower().startswith("islost") and fv >= 70: ws.cell(row=ws.max_row, column=ci).fill = RED
                    elif cn.lower().startswith("islost") and fv >= 30: ws.cell(row=ws.max_row, column=ci).fill = AMBER
                except (TypeError, ValueError): pass
    for i, _ in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = 22

def build_excel(path: Path, kb: pd.DataFrame, ch: pd.DataFrame, pmi: pd.DataFrame,
                nks: pd.DataFrame, can: pd.DataFrame, crit: dict, ctx: dict, inp):
    wb = Workbook(); wb.remove(wb.active)
    # 1. Summary
    ws = wb.create_sheet("Summary")
    total_cost = inp["kw"]["_cost"].sum(); total_fft = inp["kw"]["_fft"].sum(); total_kpi = inp["kw"]["_kpi"].sum()
    blended_ctr = (inp["kw"]["_clicks"].sum() / inp["kw"]["_impr"].sum() * 100) if inp["kw"]["_impr"].sum() else float("nan")
    ws.append(["keyword-diagnose-v2 — Summary"]); ws.append([])
    ws.append(["Strategic posture", crit["_raw"].get("meta", {}).get("posture", "(not set in criteria.yaml meta — see conversion-goals.md → Strategic Posture)")])
    ws.append(["Window", "Keyword/Campaign: L6M · Search Terms: L3M (actions) + L6M (Source mix) · Assets: L3M"])
    ws.append(["Total Search spend (L6M)", round(total_cost,2)])
    ws.append(["Bidding-signal conversions (L6M)", total_fft, "blended CPA", round(total_cost/total_fft,2) if total_fft else None,
               "target", crit["B_cpa_targets.target_fft_cpa_blended"]])
    ws.append(["Business-KPI conversions (L6M)", total_kpi, "blended CPA", round(total_cost/total_kpi,2) if total_kpi else None,
               "target", crit["B_cpa_targets.target_kpi_cpa_blended"]])
    ws.append(["Blended Search CTR", f"{blended_ctr:.2f}%"])
    ws.append([]); ws.append(["Bucket", "# keywords", "% of Search spend"])
    if not kb.empty:
        for b, sub in kb.groupby("Bucket"):
            ws.append([b, len(sub), f"{sub.Cost.sum()/total_cost*100:.1f}%" if total_cost else "—"])
        ws.append(["High-Spend Alert (overlay)", int(kb.HighSpendAlert.sum()), "—"])
    ws.append([]); ws.append(["Data health"])
    ws.append(["[VERIFY] context markers in client files", ctx.get("_verify_count", 0)])
    ws.append(["PMax queries — visible % (proxy)", (pmi.VisibleQueryPct.iloc[0] if not pmi.empty else "n/a")])
    for i in range(1, 7): ws.column_dimensions[get_column_letter(i)].width = 32
    # other sheets
    _sheet(wb, "Campaign Health", ch, "⭐ Campaign-level snapshot. STR Source mix = L6M. PMax rows: see PMax Intent.", red_cols=["ISLostRank","ISLostBudget"])
    _sheet(wb, "PMax Intent", pmi, "⭐ PMax STR (L3M) clustered into intent buckets. VisibleQueryPct = black-box honesty signal.")
    _sheet(wb, "High-Spend Alerts", kb[kb.HighSpendAlert] if not kb.empty else kb, "🔴 Spending >=3x target AND IS Lost (Rank) >=70%.", red_cols=["CPAvsTarget","ISLostRank"])
    fk = kb[kb.Bucket == "Fix → Keep in Search"] if not kb.empty else kb
    _sheet(wb, "Fix Keep in Search", fk, "⭐ Actionable per-keyword Fix instructions. Match type column is informational, not an action.", red_cols=["CPAvsTarget","ISLostRank"])
    _sheet(wb, "Keep in Search", kb[kb.Bucket == "Keep in Search"] if not kb.empty else kb, "Healthy keywords — no action.")
    _sheet(wb, "Move to PMax", kb[kb.Bucket == "Move to PMax"] if not kb.empty else kb, "Hemorrhage candidates: long-tail Search intent PMax serves more cheaply.", red_cols=["CPAvsTarget"])
    _sheet(wb, "Fix Decide", kb[kb.Bucket == "Fix → Decide"] if not kb.empty else kb, "Watchlist — ambiguous; bring to a review call.", red_cols=["CPAvsTarget"])
    _sheet(wb, "Monitor has signal", kb[kb.Bucket == "Monitor (has signal)"] if not kb.empty else kb, "Low spend but firing the top-of-funnel proxy.")
    _sheet(wb, "Monitor low data", kb[kb.Bucket == "Monitor (low data)"] if not kb.empty else kb, "Below spend & signal floors. Excluded from alerts/Fix logic.")
    _sheet(wb, "Pause", kb[kb.Bucket == "Pause"] if not kb.empty else kb, "Spent without converting — pause / hard-cap.")
    _sheet(wb, "New Keyword Suggestions", nks, "⭐ Queries to ADD as Search keywords (3 tiers). Never recommends match-type changes to existing keywords.")
    _sheet(wb, "PMax-Search Cannibalization", can, "⭐ Queries converting on both channels — pick a winner or kill both.")
    wb.save(path)

# ---------------------------------------------------------------------------
# 11. Word
# ---------------------------------------------------------------------------
def build_word(path: Path, kb, ch, pmi, nks, can, crit, ctx, inp):
    doc = Document()
    h = doc.add_heading("Keyword Diagnosis — Insights", level=0)
    total_cost = inp["kw"]["_cost"].sum(); total_fft = inp["kw"]["_fft"].sum(); total_kpi = inp["kw"]["_kpi"].sum()
    blended_ctr = (inp["kw"]["_clicks"].sum() / inp["kw"]["_impr"].sum() * 100) if inp["kw"]["_impr"].sum() else float("nan")
    doc.add_heading("Account at a glance", level=1)
    posture = crit["_raw"].get("meta", {}).get("posture")
    if posture:
        doc.add_paragraph(f"Strategic posture: {posture} — the CPA targets below encode this; bucketing is harsher in Efficiency mode, more generous in Scale mode (see conversion-goals.md → Strategic Posture).")
    for line in [
        f"Total Search spend (L6M): ${total_cost:,.0f}",
        f"Bidding-signal conversions: {total_fft:,.0f} at ${ (total_cost/total_fft) if total_fft else 0:,.0f} CPA (target ${crit['B_cpa_targets.target_fft_cpa_blended']})",
        f"Business-KPI conversions: {total_kpi:,.0f} at ${ (total_cost/total_kpi) if total_kpi else 0:,.0f} CPA (target ${crit['B_cpa_targets.target_kpi_cpa_blended']})",
        f"Blended Search CTR: {blended_ctr:.2f}%",
    ]:
        doc.add_paragraph(line, style="List Bullet")
    doc.add_heading("Five key findings", level=1)
    findings = []
    if not kb.empty:
        pause_spend = kb.loc[kb.Bucket == "Pause", "Cost"].sum()
        if pause_spend: findings.append((pause_spend, f"${pause_spend:,.0f} of L6M Search spend is on keywords with zero bidding-signal conversions (Pause bucket). See the Pause sheet."))
        hs = kb[kb.HighSpendAlert]
        if not hs.empty: findings.append((hs.Cost.sum(), f"{len(hs)} keywords are bidding hard into auctions they mostly lose (>=70% IS Lost Rank) while spending >=3x target — ${hs.Cost.sum():,.0f} at stake. See High-Spend Alerts."))
        movp = kb.loc[kb.Bucket == "Move to PMax", "Cost"].sum()
        if movp: findings.append((movp, f"${movp:,.0f} of Search spend is long-tail intent that PMax can likely serve more cheaply (Move to PMax bucket)."))
    if not ch.empty:
        stalled = ch[(ch.Channel == "Search") & (ch.ISLostRank.fillna(0) > 80) & (ch.ISLostBudget.fillna(0) < 10)]
        if not stalled.empty: findings.append((stalled.Spend.sum(), f"{len(stalled)} Search campaigns can't enter the auction (IS Lost Rank >80%, Budget loss low) — tCPA too strict or structure broken. See Campaign Health."))
    if not pmi.empty:
        top = pmi.groupby("Cluster").Cost.sum().sort_values(ascending=False)
        if len(top): findings.append((top.iloc[0], f"PMax's biggest visible intent cluster is “{top.index[0]}” (${top.iloc[0]:,.0f}); visible-query % is {pmi.VisibleQueryPct.iloc[0]} — treat the PMax read as partial. See PMax Intent."))
    if not can.empty: findings.append((can.PMaxCost.sum(), f"{len(can)} queries are running on both PMax and Search; the Cannibalization sheet picks a winner (or 'kill both') for each."))
    for _, txt in sorted(findings, reverse=True)[:5]:
        doc.add_paragraph(txt, style="List Number")
    if not findings:
        doc.add_paragraph("No material findings cleared the thresholds — review the bucket distribution on the Summary sheet.")
    doc.add_heading("Data health & open questions", level=1)
    doc.add_paragraph(f"{ctx.get('_verify_count',0)} [VERIFY] markers remain in the client context files — values used on faith; treat dependent findings as provisional.", style="List Bullet")
    if not pmi.empty: doc.add_paragraph(f"PMax visible-query share ≈ {pmi.VisibleQueryPct.iloc[0]} — Google does not disclose all PMax queries; the 'Other / unclassified' cluster is partly invisible traffic.", style="List Bullet")
    doc.add_paragraph("Window seam: keyword spend is L6M; cannibalization / new-keyword / PMax-intent figures are L3M — they don't reconcile by construction (see diagnose/data-window-rationale.md).", style="List Bullet")
    doc.add_paragraph("Questions no export can answer (confirm with the account team): consent-mode v2 status, localized-pricing status, recent restructure timing — see clients/<slug>/current-problems.md.", style="List Bullet")
    doc.save(path)

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True); ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--repo", default="."); a = ap.parse_args()
    repo = Path(a.repo).resolve()
    crit = load_criteria(repo, a.slug)
    ctx  = load_context(repo, a.slug)
    inp  = load_inputs(repo, a.slug, ctx)
    kb   = bucket_keywords(inp["kw"], crit, ctx)
    ch   = campaign_health(inp, kb, crit)
    pmi  = pmax_intent(inp, crit, repo)
    nks  = new_keyword_suggestions(inp, crit, ctx)
    can  = cannibalization(inp, crit)
    outd = repo / "output" / a.slug / a.date; outd.mkdir(parents=True, exist_ok=True)
    build_excel(outd / "keyword-diagnose.xlsx", kb, ch, pmi, nks, can, crit, ctx, inp)
    build_word(outd / "insights.docx", kb, ch, pmi, nks, can, crit, ctx, inp)
    print(f"Wrote {outd/'keyword-diagnose.xlsx'} and {outd/'insights.docx'}")

if __name__ == "__main__":
    main()
```

After running, point the user at `diagnose/reading-the-output.md` for the sheet-by-sheet walkthrough, and re-read the Insights Doc's "Data health & open questions" page out loud to them — the `[VERIFY]` count and PMax visible-% are the confidence caveats that matter most.
