"""Tests for src/build_canonical.py. Run: python3 -m unittest tests.test_build_canonical -v"""
import json
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import build_canonical as bc  # noqa: E402
import build_diagnosis as bd  # noqa: E402


class Canonical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = bc.build(bd.DEFAULT_STEP1, bd.DEFAULT_ACCOUNT, bc.DEFAULT_REVIEW_AUTHORING, bc.DEFAULT_V1)
        cls.step1 = {r["term_id"]: r for r in bd.read_csv(bd.DEFAULT_STEP1 / "metrics_search_terms.csv")}

    def test_terms_match_step1(self):
        self.assertEqual(sorted(t["term_id"] for t in self.a["terms"]), sorted(self.step1))
        for t in self.a["terms"]:
            r = self.step1[t["term_id"]]
            self.assertEqual(Decimal(t["metrics"]["cost"]), Decimal(r["cost"]))
            self.assertEqual(Decimal(t["metrics"]["cost_per_sub_recomputed"]), Decimal(r["cost_per_sub_recomputed"]))
            self.assertEqual(t["search_term"], r["search_term"])

    def test_operator_fields_empty_and_nothing_executed(self):
        self.assertEqual(self.a["operator_input"], bc.EMPTY_OPERATOR_INPUT)
        self.assertIsNone(self.a["posture"]["selected"])
        self.assertFalse(self.a["execution"]["any_action_executed"])
        for t in self.a["terms"]:
            self.assertEqual(t["operator_input"], bc.EMPTY_OPERATOR_INPUT)
            self.assertIsNone(t["operator_input"]["final_decision"])
            self.assertEqual(t["execution"]["status"], "not_executed")

    def test_each_term_has_branches_and_missing_info(self):
        for t in self.a["terms"]:
            b = t["conditional_recommendation"]["branches"]
            self.assertTrue(b["scale"] and b["maintain_efficiency"])
            self.assertTrue(t["conditional_recommendation"]["changes_decision_if"])
            self.assertTrue(all(m["changes_decision"] for m in t["missing_information"]))
            self.assertEqual(t["intent_hypothesis"]["status"], "hypothesis")

    def test_negatives_pending_with_confirmation(self):
        names = {c["search_term"] for c in self.a["negative_candidates"]}
        self.assertEqual(names, {"free ai app builder", "ai app builder github", "enterprise app development platform", "how to build an ai app"})
        for c in self.a["negative_candidates"]:
            self.assertEqual(c["status"], "pending_confirmation")
            self.assertTrue(c["confirmation_required"])
            self.assertIn("match_type_proposed", c)

    def test_computed_ranking_claims(self):
        ent = [t for t in self.a["terms"] if t["search_term"] == "enterprise app development platform"][0]
        self.assertIn("third-lowest", ent["evidence"]["summary"])
        howto = [t for t in self.a["terms"] if t["search_term"] == "how to build an ai app"][0]
        self.assertIn("5 sample terms exceed", howto["evidence"]["summary"])

    def test_no_placeholders_or_broad_multiquery_claims(self):
        body = {k: v for k, v in self.a.items() if k != "v1_unsupported_assumptions"}  # that section quotes v1 verbatim
        s = json.dumps(body)
        self.assertFalse(re.search(r"\{[a-z_][a-z0-9_]*\}", s))
        for bad in ("query mix", "heterogeneous", "mixing intents", "broad-match spillover", "pulling adjacent"):
            self.assertNotIn(bad, s.lower(), bad)
        self.assertNotIn("second-lowest", s)

    def test_bidding_signal_is_a_concern_not_a_change(self):
        b = self.a["bidding_signal"]
        self.assertIn("Concern to investigate", b["lean"])
        self.assertNotIn("Do not optimise", json.dumps(self.a["actions"]["justified_now"]))

    def test_validate_rejects_set_decision(self):
        bad = json.loads(json.dumps(self.a, default=str))
        bad["terms"][0]["operator_input"]["final_decision"] = "keep"
        with self.assertRaises(bd.DiagnosisError):
            bc.validate(bad, bd.DEFAULT_STEP1)

    def test_validate_rejects_executed(self):
        bad = json.loads(json.dumps(self.a, default=str))
        bad["execution"]["any_action_executed"] = True
        with self.assertRaises(bd.DiagnosisError):
            bc.validate(bad, bd.DEFAULT_STEP1)


if __name__ == "__main__":
    unittest.main()
