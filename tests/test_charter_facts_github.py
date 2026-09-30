"""Tests of the collecting script, without a network. Run: python3 -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import charter_check as cc  # noqa: E402
import charter_facts_github as cf  # noqa: E402
import charter_gate as cg  # noqa: E402


PR = {
    cf.PR_NUMBER: 24,
    cf.PR_TITLE: "Add the four gates",
    cf.PR_BODY: "Closes #4.\n\nNo document change: the gates implement what the product document says already.\n\nSee also #4 and #22.",
}
FILES = [{cf.FILE_NAME: "scripts/charter_gate.py"}, {cf.FILE_NAME: "docs/contract.md"}]
ISSUES = {4: {cf.ISSUE_STATE: "open"}, 22: {cf.ISSUE_STATE: "closed"}, 23: {cf.ISSUE_STATE: "open", cf.ISSUE_IS_PR: {}}, 999: None}


class Text(unittest.TestCase):
    def test_issue_numbers_in_order_each_once(self):
        """code-host, check 1."""
        self.assertEqual(cf.issue_numbers("Closes #4. See #22 and #4. Not #a. path/#9 no. issue#7 no."), [4, 22])

    def test_recorded_reason(self):
        """code-host, check 1."""
        self.assertEqual(cf.recorded_reason("x\nno document change:  because  \ny"), "because")
        self.assertIsNone(cf.recorded_reason("no such line"))

    def test_false_failure_lines(self):
        """evidence-record, check 2."""
        text = "x\nFalse failure: Documents: the gate misread a path\nfalse failure: link : the issue was renamed\ny"
        self.assertEqual(cf.false_failures(text), [{cg.JSON_KEY_GATE: "documents", "reason": "the gate misread a path"},
                                                   {cg.JSON_KEY_GATE: "link", "reason": "the issue was renamed"}])
        self.assertEqual(cf.false_failures("no such line"), [])

    def test_record_comment_round_trip(self):
        """evidence-record, check 1: the comment carries the record, and the record comes back from the comment."""
        record = {cg.JSON_KEY_VERDICT: "ready", cg.JSON_KEY_TIER: "low", cg.JSON_KEY_APPROVER: "engineer",
                  cg.FACT_CHECKS: {"tests": "pass"}, cg.JSON_KEY_SOURCE: "s v1", cg.RECORD_KEYS[3]: "abc", cg.RECORD_KEYS[2]: "t"}
        body = cf.comment_body(record)
        self.assertIn(cf.RECORD_MARKER, body)
        self.assertIn("| Verdict | ready |", body)
        self.assertEqual(cf.record_from_comment(body), record)
        self.assertIsNone(cf.record_from_comment("a plain comment"))

    def test_three_backticks_inside_a_reason_survive_the_round_trip(self):
        """evidence-record, check 1."""
        record = {cg.RECORD_KEYS[4]: [{cg.JSON_KEY_GATE: "documents", "reason": "the gate misread ```docs/x.md```"}]}
        self.assertEqual(cf.record_from_comment(cf.comment_body(record)), record)

    def test_only_a_comment_by_the_workflow_account_is_the_record(self):
        """evidence-record, check 1: a person cannot forge or hijack the record."""
        forged = {cf.COMMENT_USER: {cf.USER_LOGIN: "someone"}, cf.COMMENT_BODY: cf.RECORD_MARKER}
        real = {cf.COMMENT_USER: {cf.USER_LOGIN: cf.RECORD_AUTHOR}, cf.COMMENT_BODY: cf.RECORD_MARKER}
        self.assertFalse(cf.is_record_comment(forged, cf.RECORD_AUTHOR))
        self.assertTrue(cf.is_record_comment(real, cf.RECORD_AUTHOR))

    def test_job_result_maps_to_check_state(self):
        """code-host, check 1."""
        self.assertEqual(cf.check_state("success"), cg.CHECK_PASS)
        self.assertEqual(cf.check_state("failure"), cf.CHECK_FAIL)
        self.assertEqual(cf.check_state("cancelled"), cf.CHECK_FAIL)
        self.assertEqual(cf.check_state(None), cf.CHECK_PENDING)

    def test_newest_completed_check_run_of_each_name(self):
        """code-host, check 1."""
        runs = [
            {cf.RUN_NAME: "tests", cf.RUN_STATUS: "in_progress", cf.RUN_CONCLUSION: None},
            {cf.RUN_NAME: "tests", cf.RUN_STATUS: cf.RUN_COMPLETED, cf.RUN_CONCLUSION: "failure"},
            {cf.RUN_NAME: "tests", cf.RUN_STATUS: cf.RUN_COMPLETED, cf.RUN_CONCLUSION: "success"},
            {cf.RUN_NAME: "other", cf.RUN_STATUS: cf.RUN_COMPLETED, cf.RUN_CONCLUSION: "success"},
        ]
        self.assertEqual(cf.conclusions(runs, ["tests", "missing"]), {"tests": "failure", "missing": None})


class Facts(unittest.TestCase):
    def test_facts_from_api_data(self):
        """code-host, check 1: change requests and numbers that are no issue are left out."""
        facts = cf.build_facts(PR, FILES, ISSUES, 2, {"quality": "success", "tests": None})
        self.assertEqual(facts[cg.FACT_CHANGE_REQUEST], 24)
        self.assertEqual(facts[cg.FACT_LINKED_ISSUES],
                         [{cg.ISSUE_NUMBER: 4, cg.ISSUE_STATE: "open"}, {cg.ISSUE_NUMBER: 22, cg.ISSUE_STATE: "closed"}])
        self.assertEqual(facts[cg.FACT_CHANGED_FILES], ["scripts/charter_gate.py", "docs/contract.md"])
        self.assertEqual(facts[cg.FACT_REASON], "the gates implement what the product document says already.")
        self.assertEqual(facts[cg.FACT_UNRESOLVED_THREADS], 2)
        self.assertEqual(facts[cg.FACT_CHECKS], {"quality": cg.CHECK_PASS, "tests": cf.CHECK_PENDING})
        for key in cg.FACT_SHAPES:
            self.assertTrue(cg.FACT_SHAPES[key](facts[key]), key)

    def test_open_change_request_is_preferred_and_closed_never_counts(self):
        """code-host, check 1: a closed change request of the same commit is not the one."""
        closed, opened = {cf.PR_NUMBER: 1, cf.PR_STATE: "closed"}, {cf.PR_NUMBER: 2, cf.PR_STATE: cf.PR_OPEN}
        self.assertEqual(cf.open_change_request([closed, opened]), opened)
        self.assertIsNone(cf.open_change_request([closed]))

    def test_parse_checks(self):
        """code-host, check 1."""
        self.assertEqual(cf.parse_checks(["quality=success", " tests = failure "]), {"quality": "success", "tests": "failure"})
        with self.assertRaises(cc.CannotRun):
            cf.parse_checks(["quality"])


if __name__ == "__main__":
    unittest.main()
