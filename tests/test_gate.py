import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from x1_evals.gate import canonical_sha256, evaluate_release

ROOT = Path(__file__).parents[1]
NOW = datetime(2026, 9, 21, 17, 30, tzinfo=timezone.utc)


def valid_evidence(policy):
    digest = "a" * 64
    observed = "2026-09-21T17:29:00Z"
    sha = "b" * 40
    return {
        "source_sha": sha,
        "executor_agent_id": "forge",
        "validator_agent_id": "sentinel",
        "open_p0": 0,
        "open_p1": 0,
        "categories": {name: {"status": "PASS", "score": 100, "evidence_sha256": digest, "observed_at": observed, "max_age_seconds": 3600} for name in policy["categories"]},
        "clean_cycles": [{"status": "PASS", "source_sha": sha, "replayed": False, "cycle": i} for i in range(1, 4)],
    }


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads((ROOT / "config/mandatory-100.json").read_text())

    def test_valid_evidence_unlocks_release(self):
        report = evaluate_release(self.policy, valid_evidence(self.policy), now=NOW)
        self.assertTrue(report["release_allowed"])
        self.assertEqual(report["score"], 100)
        self.assertEqual(report["status"], "PASS")

    def test_missing_category_fails_closed(self):
        evidence = valid_evidence(self.policy)
        evidence["categories"].pop("security")
        report = evaluate_release(self.policy, evidence, now=NOW)
        self.assertFalse(report["release_allowed"])
        self.assertEqual(report["categories"]["security"]["status"], "UNKNOWN")

    def test_self_certification_is_rejected(self):
        evidence = valid_evidence(self.policy)
        evidence["validator_agent_id"] = evidence["executor_agent_id"]
        report = evaluate_release(self.policy, evidence, now=NOW)
        self.assertIn("VALIDATOR_NOT_INDEPENDENT", {f["code"] for f in report["findings"]})

    def test_skipped_or_waived_is_not_pass(self):
        for status in ("SKIPPED", "WAIVED", "BLOCKED", "UNKNOWN"):
            evidence = valid_evidence(self.policy)
            evidence["categories"]["browser_e2e"]["status"] = status
            self.assertFalse(evaluate_release(self.policy, evidence, now=NOW)["release_allowed"])

    def test_requires_three_non_replayed_cycles_same_sha(self):
        evidence = valid_evidence(self.policy)
        evidence["clean_cycles"][2]["replayed"] = True
        report = evaluate_release(self.policy, evidence, now=NOW)
        self.assertIn("INSUFFICIENT_CLEAN_CYCLES", {f["code"] for f in report["findings"]})

    def test_report_hash_is_deterministic(self):
        evidence = valid_evidence(self.policy)
        a = evaluate_release(self.policy, evidence, now=NOW)
        b = evaluate_release(self.policy, evidence, now=NOW)
        self.assertEqual(a["report_sha256"], b["report_sha256"])
        self.assertEqual(len(canonical_sha256({"b": 1, "a": 2})), 64)


if __name__ == "__main__":
    unittest.main()
