"""Tests for src/build_review_v2.py. Run: python3 -m unittest tests.test_build_review_v2 -v"""
import json
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import build_diagnosis as bd  # noqa: E402
import build_review_v2 as rv  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="so_rv2_"))
        self.authored = json.loads(rv.DEFAULT_AUTHORING.read_text())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def dump(self, obj):
        p = self.tmp / "a.json"
        p.write_text(json.dumps(obj), encoding="utf-8")
        return p


class Builds(Base):
    def test_builds_with_computed_numbers(self):
        d = rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, rv.DEFAULT_AUTHORING)
        self.assertEqual(len(d["observed_performance"]), 9)
        self.assertEqual(d["groups"]["below_allowable"]["cost"], Decimal("191120"))
        self.assertEqual(d["groups"]["below_allowable"]["paid_sub"], Decimal("1491"))
        self.assertEqual(d["groups"]["above_allowable"]["cost"], Decimal("146350"))
        self.assertEqual(d["groups"]["above_allowable"]["paid_sub"], Decimal("352"))
        # sums of the two tiers reconcile to the sample
        self.assertEqual(d["groups"]["below_allowable"]["cost"] + d["groups"]["above_allowable"]["cost"], Decimal("337470"))
        self.assertEqual(d["correlations"]["sub_rate_vs_cost_per_sub"]["spearman_rho"], Decimal("-0.92"))
        self.assertEqual(d["correlations"]["cpc_vs_sub_rate_excl_enterprise"]["n"], 8)
        ent = [t for t in d["observed_performance"] if t["search_term"] == "enterprise app development platform"][0]
        self.assertEqual(ent["numbers"]["subs_needed_at_allowable"], Decimal("93"))
        self.assertIsNone(d["meta"]["posture_selected"])

    def test_spearman_known_values(self):
        self.assertEqual(rv.spearman([1, 2, 3], [1, 2, 3]), Decimal(1))
        self.assertEqual(rv.spearman([1, 2, 3], [3, 2, 1]), Decimal(-1))

    def test_markdown_renders(self):
        d = rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, rv.DEFAULT_AUTHORING)
        md = rv.render_md(d)
        self.assertIn("Review of v1 recommendations", md)
        self.assertNotIn("{", md.split("## Method note")[0].split("## Observed performance")[1])


class Validation(Base):
    def test_unknown_alias_in_group_rejected(self):
        self.authored["groups"]["bad"] = ["core", "nope"]
        with self.assertRaises(bd.DiagnosisError):
            rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump(self.authored))

    def test_alias_with_unknown_term_id_rejected(self):
        self.authored["aliases"]["core"] = "st_000000000000"
        with self.assertRaises(bd.DiagnosisError):
            rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump(self.authored))

    def test_uncovered_term_rejected(self):
        del self.authored["aliases"]["scaffold"]
        for g in self.authored["groups"].values():
            if "scaffold" in g:
                g.remove("scaffold")
        with self.assertRaises(bd.DiagnosisError) as ctx:
            rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump(self.authored))
        self.assertIn("without alias", str(ctx.exception))

    def test_unknown_placeholder_rejected(self):
        self.authored["method_note"] = "invented {t_core_made_up}"
        with self.assertRaises(bd.DiagnosisError) as ctx:
            rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump(self.authored))
        self.assertIn("t_core_made_up", str(ctx.exception))

    def test_pattern_unknown_supporting_alias_rejected(self):
        self.authored["patterns"][0]["supporting"].append("ghost")
        with self.assertRaises(bd.DiagnosisError):
            rv.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump(self.authored))


if __name__ == "__main__":
    unittest.main()
