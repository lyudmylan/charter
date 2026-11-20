"""Tests of the collecting script, without a network. Run: python3 -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_check as cc  # noqa: E402
import charter_facts_github as cf  # noqa: E402
import charter_gate as cg  # noqa: E402


PR = {
    cf.PR_NUMBER: 24,
    cf.PR_TITLE: "Add the four gates",
    cf.PR_BODY: "Closes #4.\n\nNo document change: the gates implement what the product document says already.\n\nSee also #4 and #22.",
}
FILES = [{cf.FILE_NAME: "charter/scripts/charter_gate.py"}, {cf.FILE_NAME: "docs/contract.md"}]
ISSUES = {4: {cf.ISSUE_STATE: "open"}, 22: {cf.ISSUE_STATE: "closed"}, 23: {cf.ISSUE_STATE: "open", cf.ISSUE_IS_PR: {}}, 999: None}


class Text(unittest.TestCase):
    def test_issue_numbers_in_order_each_once(self):
        """code-host, check 2."""
        self.assertEqual(cf.issue_numbers("Closes #4. Fixes #22, closes #4 again. Resolved: #4. Not closes #a. closes path/#9 no."), [4, 22])

    def test_a_mention_is_not_a_link(self):
        """code-host, check 2 (#67): a sentence that names an issue links nothing; the nine closing keywords
        of the code host link, in any case, with or without a colon."""
        text = "Closes #4. The re-run of #81 replaces this table. Fixes: #5. resolved #6. See #7 and issue#8. CLOSED #9"
        self.assertEqual(cf.issue_numbers(text), [4, 5, 6, 9])
        self.assertEqual(cf.issue_numbers("See #7. Part of #8."), [8])
        for keyword in ("close", "closes", "closed", "fix", "fixes", "fixed", "resolve", "resolves", "resolved"):
            with self.subTest(keyword=keyword):
                self.assertEqual(cf.issue_numbers(f"{keyword} #3"), [3])

    def test_part_of_links_the_issue(self):
        """code-host, check 2 (#76): `Part of #N` links the issue without closing it, so that a change request
        of the Plan phase, the intent alone, has a link form; the case and a colon do not matter."""
        self.assertEqual(cf.issue_numbers("Part of #8. part of: #9. See #7. Closes #8."), [8, 9])

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

    def test_finding_lines(self):
        """intent-reviewer, check 3."""
        text = "a\nDropped finding: the check is a command, not a test\nFalse finding: the scope is bounded\nb"
        self.assertEqual(cf.finding_lines(text), (["the check is a command, not a test"], ["the scope is bounded"]))
        self.assertEqual(cf.finding_lines("none"), ([], []))

    def test_intent_path_from_issue(self):
        """plan-before-the-code, check 2."""
        issues = {
            22: {cf.ISSUE_BODY: "## Goal\n\nIntent: intents/app.md\n\nmore", cf.ISSUE_STATE: "open"},
            23: {cf.ISSUE_BODY: "Intent: `intents/app.md`\nIntent: intents/other.md", cf.ISSUE_STATE: "open"},
            24: {cf.ISSUE_BODY: "Intent: intents/pr.md", cf.ISSUE_STATE: "open", cf.ISSUE_IS_PR: {}},     # a change request
            25: None,                                                                                   # not an issue
            26: {cf.ISSUE_BODY: "no line here, and intents/not-a-line.md in prose", cf.ISSUE_STATE: "open"},
            27: {cf.ISSUE_BODY: "## Goal\n\ntext\n\n## Intent\n`intents/older-form.md`\n", cf.ISSUE_STATE: "open"},
            28: {cf.ISSUE_BODY: "Intent: intents/app.plan.md\nIntent: intents/App.MD", cf.ISSUE_STATE: "open"},   # a plan, a wrong case
        }
        self.assertEqual(cf.intent_paths(issues), ["intents/app.md", "intents/other.md", "intents/older-form.md"])
        self.assertEqual(cg.plan_of("intents/app.md"), "plans/app.md")
        facts = cf.build_facts({cf.PR_NUMBER: 7, cf.PR_TITLE: "t", cf.PR_BODY: ""}, [], {}, 0, {},
                               plans={"intents/app.md": True, "intents/other.md": False})
        self.assertEqual(facts[cg.FACT_INTENTS], [{cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: True, cg.INTENT_REMOVED: False},
                                                  {cg.INTENT_PATH: "intents/other.md", cg.INTENT_PLAN: False, cg.INTENT_REMOVED: False}])

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


class ReviewLoop(unittest.TestCase):
    bot = {cf.COMMENT_USER: {cf.USER_LOGIN: cf.RECORD_AUTHOR}}

    def test_highest_severity_from_the_report_of_the_workflow_account(self):
        """review-loop, check 4."""
        report = f"{cf.REVIEW_MARKER}\n**Intent review**\n...\nHighest open severity: Medium\n"
        person = {**self.bot, cf.COMMENT_USER: {cf.USER_LOGIN: "alice"}, cf.COMMENT_BODY: report.replace("Medium", "blocker")}
        self.assertEqual(cf.highest_severity([person, {**self.bot, cf.COMMENT_BODY: report}], cf.RECORD_AUTHOR), "medium")
        older = {**self.bot, cf.COMMENT_BODY: report.replace("Medium", "high")}     # the API lists the oldest first
        self.assertEqual(cf.highest_severity([older, {**self.bot, cf.COMMENT_BODY: report}], cf.RECORD_AUTHOR), "medium")
        self.assertIsNone(cf.highest_severity([person], cf.RECORD_AUTHOR))
        self.assertIsNone(cf.highest_severity([{**self.bot, cf.COMMENT_BODY: f"{cf.REVIEW_MARKER}\nno line"}], cf.RECORD_AUTHOR))

    def test_rounds_are_the_successful_runs_since_the_change_request_opened(self):
        """review-loop, check 4. Since review-rounds (#61) a successful run is a run that added a report, so the
        fact `review_rounds` is the number of the reports of the reviewer; a comment of another author is none."""
        report = f"{cf.REVIEW_MARKER}\nHighest open severity: low\n"
        person = {cf.COMMENT_USER: {cf.USER_LOGIN: "alice"}, cf.COMMENT_BODY: report}
        comments = [{**self.bot, cf.COMMENT_BODY: report}, person, {**self.bot, cf.COMMENT_BODY: report}]
        pr = {cf.PR_NUMBER: 7, cf.PR_TITLE: "t", cf.PR_BODY: ""}
        facts = cf.build_facts(pr, [], {}, 0, {}, review=cf.review_reports(comments, cf.RECORD_AUTHOR))
        self.assertEqual(facts[cg.FACT_REVIEW_ROUNDS], 2)

    def test_facts_carry_the_loop_only_when_a_reviewer_is_named(self):
        """review-loop, check 4."""
        pr = {cf.PR_NUMBER: 7, cf.PR_TITLE: "t", cf.PR_BODY: ""}
        without = cf.build_facts(pr, [], {}, 0, {})
        self.assertNotIn(cg.FACT_REVIEW_ROUNDS, without)
        with_loop = cf.build_facts(pr, [], {}, 0, {}, review=["high", "low"])
        self.assertEqual((with_loop[cg.FACT_REVIEW_ROUNDS], with_loop[cg.FACT_REVIEW_SEVERITY]), (2, "low"))
        self.assertEqual(with_loop[cg.FACT_REVIEW_REPORTS], ["high", "low"])


class Facts(unittest.TestCase):
    def test_facts_from_api_data(self):
        """code-host, check 1: change requests and numbers that are no issue are left out."""
        facts = cf.build_facts(PR, FILES, ISSUES, 2, {"quality": "success", "tests": None})
        self.assertEqual(facts[cg.FACT_CHANGE_REQUEST], 24)
        self.assertEqual(facts[cg.FACT_LINKED_ISSUES],
                         [{cg.ISSUE_NUMBER: 4, cg.ISSUE_STATE: "open"}, {cg.ISSUE_NUMBER: 22, cg.ISSUE_STATE: "closed"}])
        self.assertEqual(facts[cg.FACT_CHANGED_FILES], ["charter/scripts/charter_gate.py", "docs/contract.md"])
        self.assertEqual(facts[cg.FACT_REASON], "the gates implement what the product document says already.")
        self.assertEqual(facts[cg.FACT_UNRESOLVED_THREADS], 2)
        self.assertEqual(facts[cg.FACT_CHECKS], {"quality": cg.CHECK_PASS, "tests": cf.CHECK_PENDING})
        for key in cg.FACT_SHAPES:
            self.assertTrue(cg.FACT_SHAPES[key](facts[key]), key)

    def test_a_renamed_or_removed_intent_is_marked(self):
        """plan-before-the-code, check 4 (#71): the intent of a linked issue that the change request removes, or
        renames away, carries `removed`; the gate then asks no plan for it."""
        files = [{cf.FILE_NAME: "intents/b.md", cf.FILE_STATUS: cf.STATUS_RENAMED, cf.FILE_PREVIOUS: "intents/a.md"},
                 {cf.FILE_NAME: "intents/c.md", cf.FILE_STATUS: cf.STATUS_REMOVED},
                 {cf.FILE_NAME: "docs/product.md", cf.FILE_STATUS: "modified"}]
        self.assertEqual(cf.removed_paths(files), {"intents/a.md", "intents/c.md"})
        plans = {"intents/a.md": False, "intents/b.md": True, "intents/c.md": False}
        facts = cf.build_facts(PR, files, ISSUES, 0, {}, None, plans, cf.removed_paths(files))
        self.assertEqual(facts[cg.FACT_INTENTS], [
            {cg.INTENT_PATH: "intents/a.md", cg.INTENT_PLAN: False, cg.INTENT_REMOVED: True},
            {cg.INTENT_PATH: "intents/b.md", cg.INTENT_PLAN: True, cg.INTENT_REMOVED: False},
            {cg.INTENT_PATH: "intents/c.md", cg.INTENT_PLAN: False, cg.INTENT_REMOVED: True}])
        self.assertEqual(facts[cg.FACT_CHANGED_FILES], ["intents/b.md", "intents/c.md", "docs/product.md"])

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


class FakeHost:
    """The code host as data: a change request that links issue 4, whose intent is `intents/app.md`, and the
    files that exist at the head commit. A missing file is None, as the API answers with optional."""
    REPO, NUMBER, COMMIT = "o/r", 7, "abc"

    def __init__(self, files_at_head: set[str]):
        self.files_at_head = files_at_head
        self.asked: list[str] = []

    def get(self, path: str, optional: bool = False) -> object:
        self.asked.append(path)
        if path == f"/repos/{self.REPO}/pulls/{self.NUMBER}":
            return {cf.PR_NUMBER: self.NUMBER, cf.PR_TITLE: "t", cf.PR_BODY: "Closes #4.", cf.PR_HEAD: {cf.HEAD_SHA: self.COMMIT}}
        if path == f"/repos/{self.REPO}/issues/4":
            return {cf.ISSUE_BODY: "Intent: intents/app.md", cf.ISSUE_STATE: "open"}
        prefix, suffix = f"/repos/{self.REPO}/contents/", f"?ref={self.COMMIT}"
        if path.startswith(prefix) and path.endswith(suffix):
            return {} if path[len(prefix):-len(suffix)] in self.files_at_head else None
        raise AssertionError(f"not expected: {path}")

    def pages(self, path: str) -> list:
        return [{cf.FILE_NAME: "src/app.py", cf.FILE_STATUS: "modified"}]

    def unresolved_threads(self, owner: str, name: str, number: int) -> int:
        return 0


class ReviewReports(unittest.TestCase):
    bot = {cf.COMMENT_USER: {cf.USER_LOGIN: cf.RECORD_AUTHOR}}

    def report(self, line: str) -> dict:
        return {**self.bot, cf.COMMENT_BODY: f"{cf.REVIEW_MARKER}\nCommit: abc\n{line}\n"}

    def test_each_report_gives_its_severity_in_order(self):
        """review-rounds, check 5."""
        person = {cf.COMMENT_USER: {cf.USER_LOGIN: "alice"},
                  cf.COMMENT_BODY: f"{cf.REVIEW_MARKER}\nHighest open severity: blocker\n"}
        plain = {**self.bot, cf.COMMENT_BODY: "Highest open severity: high"}     # no marker: no report
        comments = [self.report("Highest open severity: Medium"), person, plain, self.report("no line"),
                    self.report("Highest open severity: low")]
        self.assertEqual(cf.review_reports(comments, cf.RECORD_AUTHOR), ["medium", None, "low"])
        self.assertEqual(cf.review_reports([person], cf.RECORD_AUTHOR), [])

    def test_the_collector_lists_no_workflow_runs(self):
        """review-rounds, check 5: the collector reads the reports from the comments, and asks the code host
        for no list of workflow runs."""
        reports = [self.report("Highest open severity: high"), self.report("Highest open severity: none")]

        class Host(FakeHost):
            def pages(self, path: str) -> list:
                self.asked.append(path)
                return reports if path.endswith("/comments") else super().pages(path)

        host = Host(set())
        facts = cf.collect(FakeHost.REPO, FakeHost.NUMBER, {}, [], host, review_workflow="review-intents.yml")
        self.assertEqual(facts[cg.FACT_REVIEW_REPORTS], ["high", "none"])
        self.assertEqual((facts[cg.FACT_REVIEW_ROUNDS], facts[cg.FACT_REVIEW_SEVERITY]), (2, "none"))
        self.assertIn(f"/repos/{FakeHost.REPO}/issues/{FakeHost.NUMBER}/comments", host.asked)
        self.assertFalse([path for path in host.asked if "/actions/" in path], host.asked)


class PlanPlace(unittest.TestCase):
    def facts(self, *files_at_head: str) -> dict:
        host = FakeHost(set(files_at_head))
        return cf.collect(FakeHost.REPO, FakeHost.NUMBER, {}, [], host)[cg.FACT_INTENTS]

    def test_the_plan_is_found_in_the_plans_folder(self):
        """plan-tier, check 2."""
        self.assertEqual(self.facts("plans/app.md"),
                         [{cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: True, cg.INTENT_REMOVED: False}])

    def test_a_plan_at_the_old_place_still_counts(self):
        """plan-tier, check 2."""
        self.assertEqual(self.facts("intents/app.plan.md"),
                         [{cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: True, cg.INTENT_REMOVED: False}])

    def test_a_plan_at_neither_place_is_missing(self):
        """plan-tier, check 2."""
        self.assertEqual(self.facts("intents/app.md", "plans/other.md"),
                         [{cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: False, cg.INTENT_REMOVED: False}])


if __name__ == "__main__":
    unittest.main()
