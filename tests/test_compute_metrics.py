"""Tests for src/compute_metrics.py. Run: python3 -m unittest tests.test_compute_metrics -v"""
import csv
import json
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import compute_metrics as cm  # noqa: E402

SEARCH_HEADER = "Search term,Match type,Clicks,Cost,Regs,Subs,Cost/sub\n"
CHANNEL_HEADER = "channel,q2_spend,q2_subs,q2_cost_per_sub_reported,q1_cost_per_sub,allowable_cost_per_sub\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="so_test_"))
        self.config = cm.load_config(cm.DEFAULT_CONFIG)
        self.context = cm.load_context(cm.DEFAULT_CONTEXT)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, text):
        p = self.tmp / name
        p.write_text(text, encoding="utf-8")
        return p


class SourceTotals(Base):
    def test_supplied_files_reconcile(self):
        checks = cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT,
                        cm.DEFAULT_CONFIG, self.tmp / "out")
        self.assertEqual(checks["summary"]["overall"], "pass")
        ids = {p["id"]: p for p in checks["passes"]}
        self.assertEqual(ids["sample_cost_total"]["actual"], "337470")
        self.assertEqual(ids["sample_subs_total"]["actual"], "1843")
        self.assertEqual(ids["channel_spend_sum_excluding_aggregate"]["actual"], "1623000")
        self.assertEqual(ids["channel_subs_sum_excluding_aggregate"]["actual"], "11982")
        self.assertIn("aggregate_matches_channel_sum:Paid total", ids)
        self.assertEqual(checks["summary"]["fail_count"], 0)

    def test_scope_summary_levels_and_coverage(self):
        cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT, cm.DEFAULT_CONFIG, self.tmp / "out")
        scope = json.loads((self.tmp / "out" / "scope_summary.json").read_text())
        self.assertEqual(scope["all_google_non_brand"]["spend"], "701000")
        self.assertEqual(scope["scope"]["spend"], "520000")
        self.assertEqual(scope["sample"]["cost"], "337470")
        self.assertEqual(scope["sample"]["spend_coverage_of_scope_actual"], "0.648981")
        self.assertEqual(scope["sample"]["spend_coverage_of_scope_reported"], "0.65")
        self.assertTrue(scope["sample"]["coverage_within_tolerance"])
        self.assertEqual(scope["scope"]["cost_per_sub_recomputed"], "167.7419")
        self.assertEqual(scope["remainder"]["label"], "subtraction_within_stated_scope")
        self.assertEqual(scope["remainder"]["spend"], "182530")
        self.assertEqual(scope["remainder"]["paid_sub"], "1257")

    def test_search_term_rows_sorted_by_cost_with_supplied_side_by_side(self):
        cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT, cm.DEFAULT_CONFIG, self.tmp / "out")
        with open(self.tmp / "out" / "metrics_search_terms.csv", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 9)
        costs = [Decimal(r["cost"]) for r in rows]
        self.assertEqual(costs, sorted(costs, reverse=True))
        self.assertEqual(rows[0]["search_term"], "ai app builder")
        self.assertEqual(rows[0]["cost_per_sub_recomputed"], "147.8261")
        self.assertEqual(rows[0]["cost_per_sub_supplied"], "147.83")
        self.assertEqual(rows[0]["cost_per_sub_matches_supplied"], "true")
        self.assertEqual(rows[0]["allowable_cost_per_sub"], "181")
        self.assertTrue(all(r["cost_per_sub_matches_supplied"] == "true" for r in rows))


class AggregateExclusion(Base):
    def test_paid_total_marked_unranked_and_excluded_from_sums(self):
        channels = cm.load_channels(cm.DEFAULT_CHANNELS, self.config)
        rows, totals = cm.compute_channel_metrics(channels, self.config, [])
        agg = [r for r in rows if r["is_aggregate"]]
        real = [r for r in rows if not r["is_aggregate"]]
        self.assertEqual(len(agg), 1)
        self.assertEqual(agg[0]["channel"], "Paid total")
        self.assertIsNone(agg[0]["rank_by_q2_spend"])
        self.assertIsNone(agg[0]["share_of_paid_spend"])
        self.assertEqual(totals["spend"], Decimal("1623000"))
        self.assertEqual(totals["subs"], Decimal("11982"))
        self.assertEqual(len(real), 7)
        self.assertEqual([r["rank_by_q2_spend"] for r in real], list(range(1, 8)))
        self.assertEqual(sum(r["share_of_paid_spend"] for r in real).quantize(Decimal("0.0001")), Decimal("1.0000"))
        self.assertEqual(rows[-1]["channel"], "Paid total")


class SuppliedVsRecomputed(Base):
    def test_paid_total_mismatch_is_warning_and_preserved(self):
        channels = cm.load_channels(cm.DEFAULT_CHANNELS, self.config)
        warnings = []
        rows, _ = cm.compute_channel_metrics(channels, self.config, warnings)
        agg = [r for r in rows if r["is_aggregate"]][0]
        self.assertEqual(agg["q2_cost_per_sub_supplied"], Decimal("135.47"))
        self.assertEqual(agg["q2_cost_per_sub_recomputed"], Decimal("135.4532"))
        self.assertFalse(agg["q2_cost_per_sub_matches_supplied"])
        mism = [w for w in warnings if w["id"] == "supplied_vs_recomputed_mismatch"]
        self.assertEqual(len(mism), 1)
        self.assertEqual(mism[0]["channel"], "Paid total")
        self.assertNotIn("rounding", mism[0]["message"].split("not assumed to be")[0].lower())

    def test_real_channels_all_within_half_cent(self):
        channels = cm.load_channels(cm.DEFAULT_CHANNELS, self.config)
        rows, _ = cm.compute_channel_metrics(channels, self.config, [])
        for r in rows:
            if not r["is_aggregate"]:
                self.assertTrue(r["q2_cost_per_sub_matches_supplied"], r["channel"])

    def test_search_term_mismatch_flagged(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,100,5,2,55.00\n")
        terms = cm.load_search_terms(p, self.config)
        warnings = []
        rows, _ = cm.compute_search_term_metrics(terms, Decimal(181), self.config, warnings)
        self.assertEqual(rows[0]["cost_per_sub_recomputed"], Decimal("50.0000"))
        self.assertEqual(rows[0]["cost_per_sub_supplied"], Decimal("55.00"))
        self.assertFalse(rows[0]["cost_per_sub_matches_supplied"])
        self.assertEqual(warnings[0]["id"], "supplied_vs_recomputed_mismatch")


class TikTokAllowable(Base):
    def test_tiktok_allowable_is_none_not_zero(self):
        channels = cm.load_channels(cm.DEFAULT_CHANNELS, self.config)
        warnings = []
        rows, _ = cm.compute_channel_metrics(channels, self.config, warnings)
        tiktok = [r for r in rows if r["channel"] == "TikTok"][0]
        self.assertIsNone(tiktok["allowable_cost_per_sub"])
        self.assertIsNone(tiktok["gap_to_allowable_abs"])
        self.assertIsNone(tiktok["cost_per_sub_to_allowable_ratio"])
        self.assertIsNotNone(tiktok["qoq_cost_per_sub_change_abs"])
        self.assertTrue(any(w["id"] == "allowable_unavailable" and w["channel"] == "TikTok" for w in warnings))


class ZeroDenominator(Base):
    def test_zero_subs_and_clicks_give_null_with_warning(self):
        p = self.write("st.csv", SEARCH_HEADER + "a,Broad,0,100,0,0,\nb,Broad,10,50,5,1,50\n")
        terms = cm.load_search_terms(p, self.config)
        warnings = []
        rows, totals = cm.compute_search_term_metrics(terms, Decimal(181), self.config, warnings)
        a = [r for r in rows if r["search_term"] == "a"][0]
        for field in ("cpc", "cost_per_signup", "signup_per_click", "paid_sub_per_signup",
                      "cost_per_sub_recomputed", "cost_per_sub_to_allowable_ratio"):
            self.assertIsNone(a[field], field)
        self.assertIsNone(a["cost_per_sub_matches_supplied"])
        self.assertEqual(a["sample_cost_share"], Decimal("0.666667"))
        self.assertEqual(a["sample_sub_share"], Decimal("0.000000"))
        zero_warns = [w for w in warnings if w["id"] == "zero_denominator" and w["search_term"] == "a"]
        self.assertEqual(len(zero_warns), 5)
        self.assertEqual(cm.fmt(a["cpc"]), "")

    def test_zero_channel_subs(self):
        p = self.write("ch.csv", CHANNEL_HEADER + "X,100,0,,50,10\nPaid total,100,0,,,\n")
        channels = cm.load_channels(p, self.config)
        warnings = []
        rows, _ = cm.compute_channel_metrics(channels, self.config, warnings)
        self.assertIsNone(rows[0]["q2_cost_per_sub_recomputed"])
        self.assertIsNone(rows[0]["qoq_cost_per_sub_change_abs"])
        self.assertTrue(any(w["id"] == "zero_denominator" for w in warnings))


class InputValidation(Base):
    def test_quoted_thousands_and_currency_parse(self):
        p = self.write("st.csv", SEARCH_HEADER + '"ai app builder",Phrase,"34,000","$102,000.00","4,760",690,"$147.83"\n')
        terms = cm.load_search_terms(p, self.config)
        self.assertEqual(terms[0]["clicks"], Decimal("34000"))
        self.assertEqual(terms[0]["cost"], Decimal("102000.00"))
        self.assertEqual(terms[0]["cost_per_sub_supplied"], Decimal("147.83"))

    def test_fractional_counts_preserved(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,100,5.5,2.25,44.44\n")
        terms = cm.load_search_terms(p, self.config)
        self.assertEqual(terms[0]["signup"], Decimal("5.5"))
        self.assertEqual(cm.fmt(terms[0]["paid_sub"]), "2.25")

    def test_negative_rejected(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,-100,5,2,50\n")
        with self.assertRaises(cm.InputError) as ctx:
            cm.load_search_terms(p, self.config)
        self.assertIn("negative", str(ctx.exception))
        self.assertIn("line 2", str(ctx.exception))

    def test_nonfinite_and_nonnumeric_rejected(self):
        for bad in ("NaN", "Infinity", "abc"):
            p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,%s,5,2,50\n" % bad)
            with self.assertRaises(cm.InputError):
                cm.load_search_terms(p, self.config)

    def test_missing_required_column(self):
        p = self.write("st.csv", "Search term,Match type,Clicks,Cost,Regs,Cost/sub\nx,Broad,1,1,1,1\n")
        with self.assertRaises(cm.InputError) as ctx:
            cm.load_search_terms(p, self.config)
        self.assertIn("Subs", str(ctx.exception))

    def test_missing_required_field(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,,100,5,2,50\n")
        with self.assertRaises(cm.InputError) as ctx:
            cm.load_search_terms(p, self.config)
        self.assertIn("Clicks", str(ctx.exception))

    def test_malformed_row_rejected(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,100,5,2\n")
        with self.assertRaises(cm.InputError) as ctx:
            cm.load_search_terms(p, self.config)
        self.assertIn("cells", str(ctx.exception))

    def test_duplicate_identity_rejected(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,100,5,2,50\nX ,broad,1,1,1,1,1\n")
        with self.assertRaises(cm.InputError) as ctx:
            cm.load_search_terms(p, self.config)
        self.assertIn("duplicate", str(ctx.exception))

    def test_same_term_different_match_type_allowed(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,100,5,2,50\nx,Phrase,1,1,1,1,1\n")
        terms = cm.load_search_terms(p, self.config)
        self.assertEqual(len(terms), 2)
        self.assertNotEqual(terms[0]["term_id"], terms[1]["term_id"])

    def test_duplicate_channel_rejected(self):
        p = self.write("ch.csv", CHANNEL_HEADER + "A,1,1,1,1,1\nA,1,1,1,1,1\n")
        with self.assertRaises(cm.InputError):
            cm.load_channels(p, self.config)

    def test_cli_exit_code_on_invalid_input(self):
        p = self.write("st.csv", SEARCH_HEADER + "x,Broad,10,-100,5,2,50\n")
        code = cm.main(["--search-terms", str(p), "--output-dir", str(self.tmp / "out")])
        self.assertEqual(code, 2)


class Thresholds(Base):
    def test_null_thresholds_block_only_decision_checks(self):
        checks = cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT,
                        cm.DEFAULT_CONFIG, self.tmp / "out")
        self.assertEqual(checks["summary"]["overall"], "pass")
        blocked_ids = {b["id"] for b in checks["blocked"]}
        self.assertIn("threshold_unset:min_cost", blocked_ids)
        self.assertIn("threshold_unset:min_subs", blocked_ids)
        missing_items = {m["item"] for m in checks["missing_data"]}
        for item in ("fft", "conversion_maturity_and_lag", "customer_value_ltv_or_margin",
                     "landing_page_and_product_context", "existing_keywords_and_account_structure",
                     "campaign_and_ad_group_ids", "exact_dates_and_year"):
            self.assertIn(item, missing_items)
        self.assertTrue(all(m["limits"] for m in checks["missing_data"]))
        self.assertEqual(checks["confirmed_context"]["allowable_cost_per_sub"], 181)
        self.assertEqual(checks["confirmed_context"]["main_competitor"], "Scaffold")


class Determinism(Base):
    def test_two_runs_identical_metric_outputs(self):
        a, b = self.tmp / "a", self.tmp / "b"
        cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT, cm.DEFAULT_CONFIG, a)
        cm.run(cm.DEFAULT_SEARCH_TERMS, cm.DEFAULT_CHANNELS, cm.DEFAULT_CONTEXT, cm.DEFAULT_CONFIG, b)
        for name in ("metrics_search_terms.csv", "metrics_channels.csv", "scope_summary.json", "checks.json"):
            self.assertEqual((a / name).read_bytes(), (b / name).read_bytes(), name)
        log_a = json.loads((a / "run_log.json").read_text())
        log_b = json.loads((b / "run_log.json").read_text())
        self.assertEqual(log_a["inputs"], log_b["inputs"])
        self.assertNotIn("started_utc", json.loads((a / "checks.json").read_text()))


if __name__ == "__main__":
    unittest.main()
