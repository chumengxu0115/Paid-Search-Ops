"""Tests for src/build_diagnosis.py. Run: python3 -m unittest tests.test_build_diagnosis -v"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import build_diagnosis as bd  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="so_diag_"))
        self.authored = json.loads(bd.DEFAULT_AUTHORING.read_text())
        self.account = json.loads(bd.DEFAULT_ACCOUNT.read_text())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def dump(self, name, obj):
        p = self.tmp / name
        p.write_text(json.dumps(obj), encoding="utf-8")
        return p


class BuildsFromStep1(Base):
    def test_all_terms_covered_and_numbers_from_step1(self):
        d = bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, bd.DEFAULT_AUTHORING)
        self.assertEqual(len(d["terms"]), 9)
        self.assertEqual([t["rank_by_cost"] for t in d["terms"]], list(range(1, 10)))
        first = d["terms"][0]
        self.assertEqual(first["search_term"], "ai app builder")
        self.assertEqual(str(first["evidence"]["numbers"]["cost_per_sub_recomputed"]), "147.8261")
        self.assertIn("$147.83", first["evidence"]["summary"])
        self.assertEqual(first["comparison"]["vs_allowable"]["status"], "below")
        self.assertIsNone(d["meta"]["posture_selected"])
        self.assertIsNone(first["final_decision"])

    def test_posture_not_chosen_and_allowable_unchanged(self):
        d = bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, bd.DEFAULT_AUTHORING)
        self.assertEqual(d["account_context"]["allowable"]["non_brand_cost_per_sub"], 181)
        for t in d["terms"]:
            self.assertTrue(t["conditional_handling"]["scale"])
            self.assertTrue(t["conditional_handling"]["maintain_efficiency"])
        for c in d["summary"]["negative_candidates"]:
            self.assertEqual(c["status"], "conditional")
            self.assertTrue(c["condition"])

    def test_markdown_renders(self):
        d = bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, bd.DEFAULT_AUTHORING)
        md = bd.render_md(d)
        for t in d["terms"]:
            self.assertIn(t["search_term"], md)
        self.assertIn("Least certain term", md)


class ValidationFailures(Base):
    def test_unknown_term_id_rejected(self):
        self.authored["terms"]["st_deadbeef0000"] = dict(self.authored["terms"]["st_dd3412fed286"], search_term="x")
        with self.assertRaises(bd.DiagnosisError) as ctx:
            bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump("a.json", self.authored))
        self.assertIn("not in step1", str(ctx.exception))

    def test_uncovered_term_rejected(self):
        del self.authored["terms"]["st_66770c31f114"]
        with self.assertRaises(bd.DiagnosisError) as ctx:
            bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump("a.json", self.authored))
        self.assertIn("scaffold alternative", str(ctx.exception))

    def test_search_term_mismatch_rejected(self):
        self.authored["terms"]["st_66770c31f114"]["search_term"] = "scaffold alternatives"
        with self.assertRaises(bd.DiagnosisError):
            bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump("a.json", self.authored))

    def test_unknown_placeholder_rejected(self):
        self.authored["terms"]["st_66770c31f114"]["evidence_summary"] = "cost/sub {made_up_number}"
        with self.assertRaises(bd.DiagnosisError) as ctx:
            bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump("a.json", self.authored))
        self.assertIn("made_up_number", str(ctx.exception))

    def test_summary_reference_to_unknown_term_rejected(self):
        self.authored["summary"]["negative_candidates"][0]["term_id"] = "st_000000000000"
        with self.assertRaises(bd.DiagnosisError):
            bd.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, self.dump("a.json", self.authored))

    def test_benchmark_drift_rejected(self):
        self.account["performance_benchmark"]["scope_cost_per_sub_recomputed"] = 170.0
        with self.assertRaises(bd.DiagnosisError) as ctx:
            bd.build(bd.DEFAULT_STEP1, self.dump("acc.json", self.account), bd.DEFAULT_AUTHORING)
        self.assertIn("benchmark", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
