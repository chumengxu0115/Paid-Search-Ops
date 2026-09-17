#!/usr/bin/env python3
"""Search Ops step 1: deterministic metrics and data checks.

Reads the two supplied CSVs plus the confirmed context, recomputes descriptive
ratios with Decimal arithmetic, reconciles totals, and writes machine-readable
outputs. No recommendations, forecasts or causal claims are produced here.

Inputs are never modified. Supplied values are always written next to the
recomputed values; a mismatch is reported as a warning, not corrected.
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

IMPLEMENTATION_VERSION = "step1-0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SEARCH_TERMS = PROJECT_ROOT / "data" / "search_terms.csv"
DEFAULT_CHANNELS = PROJECT_ROOT / "data" / "channel_summary.csv"
DEFAULT_CONTEXT = PROJECT_ROOT / "context" / "braid-confirmed.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "step1.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "step1"

MONEY_PLACES = Decimal("0.0001")
RATIO_PLACES = Decimal("0.000001")
CENT = Decimal("0.01")


class InputError(ValueError):
    """Raised for malformed or invalid input; message is meant to be actionable."""


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #

def parse_decimal(raw, field, row_label, required=True, allow_negative=False):
    """Parse a CSV cell into Decimal.

    Accepts thousands separators and a leading currency symbol (e.g. "$1,234.50").
    Returns None for empty optional cells. Rejects negative or non-finite values.
    """
    text = "" if raw is None else str(raw).strip()
    if text == "":
        if required:
            raise InputError(
                "%s: required field '%s' is empty. Fill the cell or remove the row." % (row_label, field)
            )
        return None
    cleaned = text.replace(",", "").replace("$", "").replace("US", "").strip()
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise InputError(
            "%s: field '%s' has non-numeric value %r. Expected a number like 1234.5 or \"$1,234.50\"."
            % (row_label, field, text)
        )
    if not value.is_finite():
        raise InputError("%s: field '%s' is not finite (%r)." % (row_label, field, text))
    if value < 0 and not allow_negative:
        raise InputError(
            "%s: field '%s' is negative (%s). Costs and counts must be >= 0." % (row_label, field, value)
        )
    return value


def normalize_count(value):
    """Keep count precision as supplied (integers stay integers; fractions are preserved)."""
    if value is None:
        return None
    if value == value.to_integral_value():
        return value.quantize(Decimal(1))
    return value.normalize()


def safe_div(numerator, denominator):
    """Return numerator/denominator, or None when the denominator is zero."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def q_money(value):
    return None if value is None else value.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def q_ratio(value):
    return None if value is None else value.quantize(RATIO_PLACES, rounding=ROUND_HALF_UP)


def fmt(value):
    """Format a Decimal (or None) for CSV/JSON output without exponent notation."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def term_identity(term, match_type):
    """Stable identity: hash of normalized term + match type, independent of row order."""
    key = "%s|%s" % (term.strip().lower(), match_type.strip().lower())
    return "st_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_config(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_context(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_rows(path, required_columns, label):
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            raise InputError("%s: file %s is empty." % (label, path))
        header = [h.strip() for h in header]
        missing = [c for c in required_columns if c not in header]
        if missing:
            raise InputError(
                "%s: missing required column(s) %s in %s. Found columns: %s"
                % (label, missing, path, header)
            )
        rows = []
        for line_no, raw in enumerate(reader, start=2):
            if not raw or all(cell.strip() == "" for cell in raw):
                continue
            if len(raw) != len(header):
                raise InputError(
                    "%s: line %d has %d cells but header has %d. Check for unquoted commas."
                    % (label, line_no, len(raw), len(header))
                )
            rows.append((line_no, dict(zip(header, [c.strip() for c in raw]))))
    return rows


def load_search_terms(path, config):
    schema = config["search_terms_schema"]
    rows = _read_rows(path, list(schema.values()), "search_terms")
    seen = {}
    out = []
    for line_no, row in rows:
        label = "search_terms line %d" % line_no
        term = row[schema["term"]]
        match_type = row[schema["match_type"]]
        if term == "" or match_type == "":
            raise InputError("%s: '%s' and '%s' are required." % (label, schema["term"], schema["match_type"]))
        ident = term_identity(term, match_type)
        if ident in seen:
            raise InputError(
                "%s: duplicate identity (%r, %r) already seen on line %d. Merge or remove the duplicate."
                % (label, term, match_type, seen[ident])
            )
        seen[ident] = line_no
        out.append({
            "term_id": ident,
            "search_term": term,
            "match_type": match_type,
            "clicks": normalize_count(parse_decimal(row[schema["clicks"]], schema["clicks"], label)),
            "cost": parse_decimal(row[schema["cost"]], schema["cost"], label),
            "signup": normalize_count(parse_decimal(row[schema["signup"]], schema["signup"], label)),
            "paid_sub": normalize_count(parse_decimal(row[schema["paid_sub"]], schema["paid_sub"], label)),
            "cost_per_sub_supplied": parse_decimal(
                row[schema["cost_per_sub_supplied"]], schema["cost_per_sub_supplied"], label, required=False
            ),
        })
    if not out:
        raise InputError("search_terms: no data rows in %s." % path)
    return out


def load_channels(path, config):
    schema = config["channels_schema"]
    aggregate_labels = set(config.get("aggregate_channel_labels", []))
    rows = _read_rows(path, list(schema.values()), "channels")
    seen = {}
    out = []
    for line_no, row in rows:
        label = "channels line %d" % line_no
        name = row[schema["channel"]]
        if name == "":
            raise InputError("%s: '%s' is required." % (label, schema["channel"]))
        key = name.lower()
        if key in seen:
            raise InputError(
                "%s: duplicate channel %r already seen on line %d." % (label, name, seen[key])
            )
        seen[key] = line_no
        out.append({
            "channel": name,
            "is_aggregate": name in aggregate_labels,
            "q2_spend": parse_decimal(row[schema["q2_spend"]], schema["q2_spend"], label),
            "q2_subs": normalize_count(parse_decimal(row[schema["q2_subs"]], schema["q2_subs"], label)),
            "q2_cost_per_sub_supplied": parse_decimal(
                row[schema["q2_cost_per_sub_supplied"]], schema["q2_cost_per_sub_supplied"], label, required=False
            ),
            "q1_cost_per_sub_supplied": parse_decimal(
                row[schema["q1_cost_per_sub_supplied"]], schema["q1_cost_per_sub_supplied"], label, required=False
            ),
            "allowable_cost_per_sub": parse_decimal(
                row[schema["allowable_cost_per_sub"]], schema["allowable_cost_per_sub"], label, required=False
            ),
        })
    if not out:
        raise InputError("channels: no data rows in %s." % path)
    return out


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #

def compute_search_term_metrics(terms, allowable, config, warnings):
    """Per-term descriptive ratios. Sorted by cost desc, then term."""
    tolerance = Decimal(config["money_tolerance"])
    total_cost = sum((t["cost"] for t in terms), Decimal(0))
    total_subs = sum((t["paid_sub"] for t in terms), Decimal(0))
    ordered = sorted(terms, key=lambda t: (-t["cost"], t["search_term"].lower(), t["match_type"].lower()))
    results = []
    for rank, t in enumerate(ordered, start=1):
        cost_per_sub = safe_div(t["cost"], t["paid_sub"])
        cpc = safe_div(t["cost"], t["clicks"])
        cost_per_signup = safe_div(t["cost"], t["signup"])
        signup_per_click = safe_div(t["signup"], t["clicks"])
        sub_per_signup = safe_div(t["paid_sub"], t["signup"])
        for name, val, denom_field in (
            ("cpc", cpc, "clicks"),
            ("cost_per_signup", cost_per_signup, "signup"),
            ("signup_per_click", signup_per_click, "clicks"),
            ("paid_sub_per_signup", sub_per_signup, "signup"),
            ("cost_per_sub_recomputed", cost_per_sub, "paid_sub"),
        ):
            if val is None:
                warnings.append({
                    "id": "zero_denominator",
                    "scope": "search_terms",
                    "term_id": t["term_id"],
                    "search_term": t["search_term"],
                    "metric": name,
                    "message": "%s is zero; %s is undefined and left empty." % (denom_field, name),
                })
        supplied = t["cost_per_sub_supplied"]
        match = None
        if supplied is not None and cost_per_sub is not None:
            diff = abs(cost_per_sub - supplied)
            match = diff <= tolerance
            if not match:
                warnings.append({
                    "id": "supplied_vs_recomputed_mismatch",
                    "scope": "search_terms",
                    "term_id": t["term_id"],
                    "search_term": t["search_term"],
                    "metric": "cost_per_sub",
                    "supplied": fmt(supplied),
                    "recomputed": fmt(q_money(cost_per_sub)),
                    "abs_diff": fmt(q_money(diff)),
                    "tolerance": fmt(tolerance),
                    "message": "Supplied cost/sub differs from cost/paid_sub beyond half-cent tolerance. "
                               "Supplied value preserved; cause unknown.",
                })
        results.append({
            "rank_by_cost": rank,
            "term_id": t["term_id"],
            "search_term": t["search_term"],
            "match_type_source": t["match_type"],
            "clicks": t["clicks"],
            "cost": t["cost"],
            "signup": t["signup"],
            "paid_sub": t["paid_sub"],
            "cpc": q_money(cpc),
            "cost_per_signup": q_money(cost_per_signup),
            "signup_per_click": q_ratio(signup_per_click),
            "paid_sub_per_signup": q_ratio(sub_per_signup),
            "cost_per_sub_recomputed": q_money(cost_per_sub),
            "cost_per_sub_supplied": supplied,
            "cost_per_sub_matches_supplied": match,
            "sample_cost_share": q_ratio(safe_div(t["cost"], total_cost)),
            "sample_sub_share": q_ratio(safe_div(t["paid_sub"], total_subs)),
            "allowable_cost_per_sub": allowable,
            "cost_per_sub_to_allowable_ratio": q_ratio(safe_div(cost_per_sub, allowable)),
        })
    return results, {"cost": total_cost, "subs": total_subs}


def compute_channel_metrics(channels, config, warnings):
    """Per-channel metrics. Real channels ranked by spend; aggregate appended, unranked, excluded from sums."""
    tolerance = Decimal(config["money_tolerance"])
    real = [c for c in channels if not c["is_aggregate"]]
    aggregates = [c for c in channels if c["is_aggregate"]]
    sum_spend = sum((c["q2_spend"] for c in real), Decimal(0))
    sum_subs = sum((c["q2_subs"] for c in real), Decimal(0))
    ordered = sorted(real, key=lambda c: (-c["q2_spend"], c["channel"].lower()))
    rows = []

    def build(c, rank):
        q2 = safe_div(c["q2_spend"], c["q2_subs"])
        if q2 is None:
            warnings.append({
                "id": "zero_denominator", "scope": "channels", "channel": c["channel"],
                "metric": "q2_cost_per_sub_recomputed",
                "message": "q2_subs is zero; cost/sub is undefined and left empty.",
            })
        supplied = c["q2_cost_per_sub_supplied"]
        match = None
        if supplied is not None and q2 is not None:
            diff = abs(q2 - supplied)
            match = diff <= tolerance
            if not match:
                warnings.append({
                    "id": "supplied_vs_recomputed_mismatch", "scope": "channels", "channel": c["channel"],
                    "metric": "q2_cost_per_sub",
                    "supplied": fmt(supplied), "recomputed": fmt(q_money(q2)),
                    "abs_diff": fmt(q_money(diff)), "tolerance": fmt(tolerance),
                    "message": "Supplied Q2 cost/sub differs from q2_spend/q2_subs beyond half-cent tolerance. "
                               "Supplied value preserved; cause unknown (not assumed to be rounding).",
                })
        q1 = c["q1_cost_per_sub_supplied"]
        allow = c["allowable_cost_per_sub"]
        if allow is None:
            warnings.append({
                "id": "allowable_unavailable", "scope": "channels", "channel": c["channel"],
                "message": "allowable_cost_per_sub is not supplied; gap and ratio left empty (not zero).",
            })
        qoq_abs = (q2 - q1) if (q2 is not None and q1 is not None) else None
        is_agg = c["is_aggregate"]
        return {
            "rank_by_q2_spend": rank,
            "channel": c["channel"],
            "is_aggregate": is_agg,
            "q2_spend": c["q2_spend"],
            "q2_subs": c["q2_subs"],
            "q2_cost_per_sub_recomputed": q_money(q2),
            "q2_cost_per_sub_supplied": supplied,
            "q2_cost_per_sub_matches_supplied": match,
            "q1_cost_per_sub_supplied": q1,
            "q1_verifiable": False,
            "qoq_cost_per_sub_change_abs": q_money(qoq_abs),
            "qoq_cost_per_sub_change_rel": q_ratio(safe_div(qoq_abs, q1)),
            "allowable_cost_per_sub": allow,
            "gap_to_allowable_abs": q_money((q2 - allow) if (q2 is not None and allow is not None) else None),
            "cost_per_sub_to_allowable_ratio": q_ratio(safe_div(q2, allow)),
            "share_of_paid_spend": None if is_agg else q_ratio(safe_div(c["q2_spend"], sum_spend)),
            "share_of_paid_subs": None if is_agg else q_ratio(safe_div(c["q2_subs"], sum_subs)),
        }

    for rank, c in enumerate(ordered, start=1):
        rows.append(build(c, rank))
    for c in aggregates:
        rows.append(build(c, None))
    return rows, {"spend": sum_spend, "subs": sum_subs, "aggregates": aggregates}


def compute_scope_summary(context, sample_totals, channel_rows, config, warnings):
    """Three distinct levels: all Google Non-Brand, the stated scope, the nine-term sample."""
    task = context["task1"]
    scope_spend = Decimal(str(task["scope_spend"]))
    scope_subs = Decimal(str(task["scope_subscriptions"]))
    scope_reported = Decimal(str(task["scope_cost_per_sub_reported"]))
    reported_cov = Decimal(str(task["sample_spend_coverage_reported"]))
    cov_tol = Decimal(config["coverage_tolerance"])
    tolerance = Decimal(config["money_tolerance"])

    scope_cps = safe_div(scope_spend, scope_subs)
    scope_match = abs(scope_cps - scope_reported) <= tolerance if scope_cps is not None else None
    if scope_match is False:
        warnings.append({
            "id": "supplied_vs_recomputed_mismatch", "scope": "scope", "metric": "scope_cost_per_sub",
            "supplied": fmt(scope_reported), "recomputed": fmt(q_money(scope_cps)),
            "message": "Scope cost/sub recomputed from scope spend/subs differs from reported; supplied preserved.",
        })

    coverage_actual = safe_div(sample_totals["cost"], scope_spend)
    coverage_within = abs(coverage_actual - reported_cov) <= cov_tol if coverage_actual is not None else None
    if coverage_within is False:
        warnings.append({
            "id": "coverage_outside_tolerance", "scope": "scope",
            "reported": fmt(reported_cov), "actual": fmt(q_ratio(coverage_actual)),
            "message": "Sample cost / scope spend is outside the approximate-coverage tolerance.",
        })

    remainder_spend = scope_spend - sample_totals["cost"]
    remainder_subs = scope_subs - sample_totals["subs"]
    remainder = {
        "label": "subtraction_within_stated_scope",
        "definition": "scope totals minus nine-term sample totals; no individual search terms are known or invented",
        "spend": remainder_spend,
        "paid_sub": remainder_subs,
        "cost_per_sub": q_money(safe_div(remainder_spend, remainder_subs)),
        "sub_share_of_scope": q_ratio(safe_div(remainder_subs, scope_subs)),
    }
    if remainder_spend < 0 or remainder_subs < 0:
        warnings.append({
            "id": "remainder_negative", "scope": "scope",
            "message": "Sample totals exceed stated scope totals; remainder is negative and should not be used.",
        })

    nb_rows = [r for r in channel_rows if r["channel"] == task["channel"] and not r["is_aggregate"]]
    non_brand = None
    if nb_rows:
        nb = nb_rows[0]
        non_brand = {
            "level": "all_google_non_brand",
            "source": "channel_summary.csv row %r (Q2 label)" % nb["channel"],
            "spend": nb["q2_spend"],
            "paid_sub": nb["q2_subs"],
            "cost_per_sub_recomputed": nb["q2_cost_per_sub_recomputed"],
            "cost_per_sub_supplied": nb["q2_cost_per_sub_supplied"],
            "allowable_cost_per_sub": nb["allowable_cost_per_sub"],
            "period_alignment_with_scope": "unverified: channel table says Q2, scope says 'last quarter'; no year or dates",
            "scope_share_of_non_brand_spend_if_same_period": q_ratio(safe_div(scope_spend, nb["q2_spend"])),
        }
    else:
        warnings.append({
            "id": "non_brand_row_missing", "scope": "scope",
            "message": "Channel %r not found in channel summary; level 1 omitted." % task["channel"],
        })

    return {
        "levels_are_distinct": True,
        "note": "Sample cost/sub describes only the nine rows. It is not the scope's or the account's cost/sub.",
        "all_google_non_brand": non_brand,
        "scope": {
            "level": "non_brand_ai_app_builder_scope",
            "label": task["scope_label"],
            "period_label": task["period_label"],
            "exact_dates": task["exact_dates"],
            "spend": scope_spend,
            "paid_sub": scope_subs,
            "cost_per_sub_recomputed": q_money(scope_cps),
            "cost_per_sub_supplied": scope_reported,
            "cost_per_sub_matches_supplied": scope_match,
            "allowable_cost_per_sub": Decimal(str(task["allowable_cost_per_sub"])),
            "allowable_status": task["allowable_status"],
        },
        "sample": {
            "level": "nine_term_sample",
            "term_count": None,  # filled by caller
            "cost": sample_totals["cost"],
            "paid_sub": sample_totals["subs"],
            "cost_per_sub_recomputed": q_money(safe_div(sample_totals["cost"], sample_totals["subs"])),
            "spend_coverage_of_scope_actual": q_ratio(coverage_actual),
            "spend_coverage_of_scope_reported": reported_cov,
            "coverage_reported_is_approximate": bool(task.get("sample_coverage_is_approximate", True)),
            "coverage_tolerance": cov_tol,
            "coverage_within_tolerance": coverage_within,
            "sub_coverage_of_scope": q_ratio(safe_div(sample_totals["subs"], scope_subs)),
        },
        "remainder": remainder,
    }


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def build_checks(term_rows, sample_totals, channel_rows, channel_totals, scope, context, config, warnings):
    tolerance = Decimal(config["money_tolerance"])
    expected = config["expected_totals"]
    task = context["task1"]
    passes = []
    failures = []

    def record(check_id, ok, detail):
        (passes if ok else failures).append({"id": check_id, "status": "pass" if ok else "fail", **detail})

    record("sample_cost_total", sample_totals["cost"] == Decimal(expected["sample_cost"]),
           {"expected": expected["sample_cost"], "actual": fmt(sample_totals["cost"])})
    record("sample_subs_total", sample_totals["subs"] == Decimal(expected["sample_subs"]),
           {"expected": expected["sample_subs"], "actual": fmt(sample_totals["subs"])})
    record("channel_spend_sum_excluding_aggregate",
           channel_totals["spend"] == Decimal(expected["channel_spend_excluding_aggregate"]),
           {"expected": expected["channel_spend_excluding_aggregate"], "actual": fmt(channel_totals["spend"])})
    record("channel_subs_sum_excluding_aggregate",
           channel_totals["subs"] == Decimal(expected["channel_subs_excluding_aggregate"]),
           {"expected": expected["channel_subs_excluding_aggregate"], "actual": fmt(channel_totals["subs"])})

    for agg in channel_totals["aggregates"]:
        record("aggregate_matches_channel_sum:%s" % agg["channel"],
               agg["q2_spend"] == channel_totals["spend"] and agg["q2_subs"] == channel_totals["subs"],
               {"aggregate_spend": fmt(agg["q2_spend"]), "aggregate_subs": fmt(agg["q2_subs"]),
                "channel_sum_spend": fmt(channel_totals["spend"]), "channel_sum_subs": fmt(channel_totals["subs"]),
                "note": "aggregate is excluded from ranking, shares and sums; counted once, as a reconciliation row"})
    record("aggregate_rows_unranked",
           all(r["rank_by_q2_spend"] is None for r in channel_rows if r["is_aggregate"]),
           {"aggregate_rows": [r["channel"] for r in channel_rows if r["is_aggregate"]]})

    mismatched_terms = [r["search_term"] for r in term_rows if r["cost_per_sub_matches_supplied"] is False]
    record("search_term_cost_per_sub_within_tolerance", not mismatched_terms,
           {"tolerance": fmt(tolerance), "mismatched": mismatched_terms})

    real_channel_mismatch = [r["channel"] for r in channel_rows
                             if not r["is_aggregate"] and r["q2_cost_per_sub_matches_supplied"] is False]
    record("real_channel_cost_per_sub_within_tolerance", not real_channel_mismatch,
           {"tolerance": fmt(tolerance), "mismatched": real_channel_mismatch})

    tiktok = [r for r in channel_rows if r["channel"].lower() == "tiktok"]
    if tiktok:
        record("tiktok_allowable_unavailable_not_zero", tiktok[0]["allowable_cost_per_sub"] is None,
               {"allowable_cost_per_sub": fmt(tiktok[0]["allowable_cost_per_sub"]) or None})

    record("scope_cost_per_sub_within_tolerance", scope["scope"]["cost_per_sub_matches_supplied"] is True,
           {"supplied": fmt(scope["scope"]["cost_per_sub_supplied"]),
            "recomputed": fmt(scope["scope"]["cost_per_sub_recomputed"])})
    record("sample_coverage_approximately_reported", scope["sample"]["coverage_within_tolerance"] is True,
           {"reported_approx": fmt(scope["sample"]["spend_coverage_of_scope_reported"]),
            "actual": fmt(scope["sample"]["spend_coverage_of_scope_actual"]),
            "tolerance": fmt(scope["sample"]["coverage_tolerance"]),
            "note": "approximate comparison, not exact equality"})
    record("no_negative_or_nonfinite_inputs", True, {"note": "enforced at load time; loader raises on violation"})

    thresholds = config.get("thresholds", {})
    blocked = []
    for key, val in sorted(thresholds.items()):
        if val is None:
            blocked.append({
                "id": "threshold_unset:%s" % key,
                "status": "blocked",
                "reason": "operator-owned threshold is null; not invented",
                "blocks": "data-sufficiency tiering (Monitor/Keep/Pause style) for the diagnostic phase",
                "does_not_block": "descriptive metrics in this checkpoint",
            })

    confirmed = {
        "channel": task["channel"],
        "scope_label": task["scope_label"],
        "scope_spend": task["scope_spend"],
        "scope_subscriptions": task["scope_subscriptions"],
        "allowable_cost_per_sub": task["allowable_cost_per_sub"],
        "allowable_status": task["allowable_status"],
        "main_competitor": task["main_competitor"],
        "period_relative": {
            "search_terms": task["period_label"],
            "channel_summary": "Q1 / Q2 labels",
            "note": "relative period is known; only exact dates and year are missing",
        },
        "event_mapping": config["event_mapping"],
    }

    missing = [
        {"item": "exact_dates_and_year", "status": "missing",
         "known": "search terms = 'last quarter'; channel table = Q1/Q2 labels",
         "limits": "confirming that the sample, the scope and the Non-Brand Q2 row cover the same period; any seasonality reading"},
        {"item": "fft", "status": "unavailable_not_zero",
         "limits": "applying the inherited FFT bidding-signal method; signup->FFT->paid stage diagnosis"},
        {"item": "conversion_maturity_and_lag", "status": "missing",
         "limits": "whether paid_sub_per_signup ratios are comparable across terms; cohort alignment of Subs to the same-period Regs"},
        {"item": "attribution_definition", "status": "missing",
         "limits": "comparing channel cost/sub across channels and to allowables; whether Regs/Subs are last-click or otherwise"},
        {"item": "customer_value_ltv_or_margin", "status": "missing",
         "limits": "judging whether $181 allowable is appropriate per term; any payback interpretation"},
        {"item": "landing_page_and_product_context", "status": "missing",
         "limits": "intent hypotheses for 'free', 'github', 'enterprise', 'internal tool' terms; post-click tests"},
        {"item": "existing_keywords_and_account_structure", "status": "missing",
         "limits": "deciding whether a term is already covered, should be isolated, or added; match-type interpretation"},
        {"item": "campaign_and_ad_group_ids", "status": "missing",
         "limits": "any Editor-importable negative or keyword file; scoping negatives"},
        {"item": "impressions", "status": "missing",
         "limits": "CTR and impression share; cannot be computed from the supplied columns"},
        {"item": "q1_raw_spend_and_subs", "status": "missing",
         "limits": "verifying q1_cost_per_sub; QoQ change uses supplied Q1 as-is"},
        {"item": "tiktok_allowable_cost_per_sub", "status": "unavailable_not_zero",
         "limits": "TikTok gap-to-allowable and ratio"},
        {"item": "remaining_scope_search_terms", "status": "missing",
         "limits": "the ~35% of scope spend outside the sample is only a subtraction; no term-level view of it"},
        {"item": "paid_total_supplied_cost_per_sub_basis", "status": "unexplained",
         "limits": "which figure (supplied 135.47 or recomputed) to cite for the account; cause not assumed"},
        {"item": "operator_thresholds_min_cost_min_subs", "status": "unset",
         "limits": "data-sufficiency tiering; deferred to operator configuration"},
    ]

    return {
        "summary": {
            "pass_count": len(passes),
            "fail_count": len(failures),
            "warning_count": len(warnings),
            "blocked_count": len(blocked),
            "missing_count": len(missing),
            "overall": "pass" if not failures else "fail",
        },
        "confirmed_context": confirmed,
        "passes": passes,
        "failures": failures,
        "warnings": warnings,
        "blocked": blocked,
        "missing_data": missing,
        "scope_note": "This checkpoint produces descriptive metrics only: no negatives, intent labels, forecasts, "
                      "scaling advice or causal claims.",
    }


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def _json_default(value):
    if isinstance(value, Decimal):
        return fmt(value)
    raise TypeError("unserializable %r" % type(value))


def write_csv(path, rows, columns):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([fmt(row.get(col)) for col in columns])


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=_json_default, sort_keys=False)
        fh.write("\n")


SEARCH_TERM_COLUMNS = [
    "rank_by_cost", "term_id", "search_term", "match_type_source", "clicks", "cost", "signup", "paid_sub",
    "cpc", "cost_per_signup", "signup_per_click", "paid_sub_per_signup",
    "cost_per_sub_recomputed", "cost_per_sub_supplied", "cost_per_sub_matches_supplied",
    "sample_cost_share", "sample_sub_share", "allowable_cost_per_sub", "cost_per_sub_to_allowable_ratio",
]
CHANNEL_COLUMNS = [
    "rank_by_q2_spend", "channel", "is_aggregate", "q2_spend", "q2_subs",
    "q2_cost_per_sub_recomputed", "q2_cost_per_sub_supplied", "q2_cost_per_sub_matches_supplied",
    "q1_cost_per_sub_supplied", "q1_verifiable", "qoq_cost_per_sub_change_abs", "qoq_cost_per_sub_change_rel",
    "allowable_cost_per_sub", "gap_to_allowable_abs", "cost_per_sub_to_allowable_ratio",
    "share_of_paid_spend", "share_of_paid_subs",
]


def run(search_terms_path, channels_path, context_path, config_path, output_dir, argv=None):
    started = time.time()
    started_utc = datetime.now(timezone.utc).isoformat()
    config = load_config(config_path)
    context = load_context(context_path)
    warnings = []

    terms = load_search_terms(search_terms_path, config)
    channels = load_channels(channels_path, config)
    allowable = Decimal(str(context["task1"]["allowable_cost_per_sub"]))

    term_rows, sample_totals = compute_search_term_metrics(terms, allowable, config, warnings)
    channel_rows, channel_totals = compute_channel_metrics(channels, config, warnings)
    scope = compute_scope_summary(context, sample_totals, channel_rows, config, warnings)
    scope["sample"]["term_count"] = len(term_rows)
    checks = build_checks(term_rows, sample_totals, channel_rows, channel_totals, scope, context, config, warnings)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "metrics_search_terms.csv", term_rows, SEARCH_TERM_COLUMNS)
    write_csv(output_dir / "metrics_channels.csv", channel_rows, CHANNEL_COLUMNS)
    write_json(output_dir / "scope_summary.json", scope)
    write_json(output_dir / "checks.json", checks)

    run_log = {
        "implementation_version": IMPLEMENTATION_VERSION,
        "python_version": platform.python_version(),
        "command": list(argv) if argv is not None else None,
        "started_utc": started_utc,
        "duration_seconds": round(time.time() - started, 4),
        "inputs": {
            "search_terms": {"path": str(search_terms_path), "sha256": sha256_file(search_terms_path)},
            "channel_summary": {"path": str(channels_path), "sha256": sha256_file(channels_path)},
            "context": {"path": str(context_path), "sha256": sha256_file(context_path)},
            "config": {"path": str(config_path), "sha256": sha256_file(config_path)},
        },
        "implementation_sha256": sha256_file(Path(__file__)),
        "outputs": sorted(p.name for p in output_dir.iterdir() if p.is_file() and p.name != "run_log.json"),
        "overall": checks["summary"]["overall"],
    }
    write_json(output_dir / "run_log.json", run_log)
    return checks


def build_parser():
    p = argparse.ArgumentParser(description="Search Ops step 1: deterministic metrics and checks.")
    p.add_argument("--search-terms", type=Path, default=DEFAULT_SEARCH_TERMS)
    p.add_argument("--channels", type=Path, default=DEFAULT_CHANNELS)
    p.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)
    try:
        checks = run(args.search_terms, args.channels, args.context, args.config, args.output_dir,
                     argv=[Path(sys.argv[0]).name] + argv)
    except InputError as exc:
        print("INPUT ERROR: %s" % exc, file=sys.stderr)
        return 2
    s = checks["summary"]
    print("overall=%s passes=%d failures=%d warnings=%d blocked=%d missing=%d -> %s"
          % (s["overall"], s["pass_count"], s["fail_count"], s["warning_count"],
             s["blocked_count"], s["missing_count"], args.output_dir))
    for f in checks["failures"]:
        print("FAIL %s: %s" % (f["id"], {k: v for k, v in f.items() if k not in ("id", "status")}))
    return 0 if s["overall"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
