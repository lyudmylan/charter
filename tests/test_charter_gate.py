"""Tests of the gates. Run: python3 -m unittest discover -s tests

Each test names the intent and the check that it implements, in its docstring.
"""

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_check as cc  # noqa: E402
import charter_gate as cg  # noqa: E402
import charter_setup as cs  # noqa: E402

SAMPLES = ROOT / "tests" / "samples"
ORG = SAMPLES / "organization.toml"
REPO = SAMPLES / "repo.toml"

FACTS_READY = {
    cg.FACT_CHANGE_REQUEST: 23,
    cg.FACT_LINKED_ISSUES: [{cg.ISSUE_NUMBER: 22, cg.ISSUE_STATE: cg.STATE_OPEN}],
    cg.FACT_CHANGED_FILES: ["src/app.py", "docs/product.md"],
    cg.FACT_REASON: None,
    cg.FACT_UNRESOLVED_THREADS: 0,
    cg.FACT_APPROVALS: ["alice"],
    cg.FACT_CHECKS: {"tests": cg.CHECK_PASS, "quality": cg.CHECK_PASS},
}


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cg.main(list(argv))
    return code, out.getvalue()


class Temp(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def facts(self, **changes) -> Path:
        path = self.dir / "facts.json"
        path.write_text(json.dumps({**FACTS_READY, **changes}))
        return path

    def contract_args(self) -> list[str]:
        return [f"--{cc.ARG_CONTRACT}", str(REPO), f"--{cc.ARG_SOURCE}", str(ORG)]


class Link(Temp):
    def test_open_linked_issue_passes(self):
        """gates, check 1."""
        code, out = run(cg.CMD_LINK, f"--{cg.ARG_FACTS}", str(self.facts()))
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("links the open issue [22]", out)

    def test_no_linked_issue_fails(self):
        """gates, check 1."""
        code, out = run(cg.CMD_LINK, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_LINKED_ISSUES: []})))
        self.assertEqual(code, cc.FAIL)
        self.assertIn(cg.msg("no_linked_issue"), out)

    def test_closed_linked_issue_fails(self):
        """gates, check 1."""
        closed = [{cg.ISSUE_NUMBER: 22, cg.ISSUE_STATE: "closed"}]
        code, out = run(cg.CMD_LINK, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_LINKED_ISSUES: closed})))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("no open issue", out)

    def test_malformed_issue_entry_cannot_run(self):
        """gates, check 1: a wrong value gives exit code 2 with the cause."""
        path = self.facts(**{cg.FACT_LINKED_ISSUES: [{"id": 22}]})
        code, out = run(cg.CMD_LINK, f"--{cg.ARG_FACTS}", str(path))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"wrong value for {cg.FACT_LINKED_ISSUES}", out)

    def test_facts_file_without_a_key_cannot_run(self):
        """gates, check 1: a broken facts file gives exit code 2 with the cause."""
        path = self.dir / "facts.json"
        path.write_text(json.dumps({cg.FACT_CHANGE_REQUEST: 1}))
        code, out = run(cg.CMD_LINK, f"--{cg.ARG_FACTS}", str(path))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: the facts file has no key", out)


class Documents(Temp):
    def test_document_changed_with_code_passes(self):
        """gates, check 1. The sample contract watches src/** and needs docs/product.md."""
        code, out = run(cg.CMD_DOCUMENTS, f"--{cg.ARG_FACTS}", str(self.facts()), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("a necessary document changed", out)

    def test_no_code_change_passes(self):
        """gates, check 1."""
        path = self.facts(**{cg.FACT_CHANGED_FILES: ["README.md"]})
        code, out = run(cg.CMD_DOCUMENTS, f"--{cg.ARG_FACTS}", str(path), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)

    def test_code_changed_without_document_or_reason_fails(self):
        """gates, check 1."""
        path = self.facts(**{cg.FACT_CHANGED_FILES: ["src/app.py"]})
        code, out = run(cg.CMD_DOCUMENTS, f"--{cg.ARG_FACTS}", str(path), *self.contract_args())
        self.assertEqual(code, cc.FAIL)
        self.assertIn("no necessary document changed and no reason is recorded", out)

    def test_no_code_paths_declared_is_said(self):
        """gates, check 1: a contract without code paths passes and says so."""
        text = REPO.read_text().replace('code_paths = ["src/**"]\n', "")
        contract = self.dir / "repo.toml"
        contract.write_text(text)
        path = self.facts(**{cg.FACT_CHANGED_FILES: ["src/app.py"]})
        code, out = run(cg.CMD_DOCUMENTS, f"--{cg.ARG_FACTS}", str(path), f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("declares no code paths", out)

    def test_code_changed_with_a_recorded_reason_passes(self):
        """gates, check 1."""
        path = self.facts(**{cg.FACT_CHANGED_FILES: ["src/app.py"], cg.FACT_REASON: "the change alters no behavior"})
        code, out = run(cg.CMD_DOCUMENTS, f"--{cg.ARG_FACTS}", str(path), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("the recorded reason: the change alters no behavior", out)


class Quality(Temp):
    def contract_with(self, commands: list[str]) -> Path:
        text = REPO.read_text().replace('quality = ["python3 -m unittest discover -s tests"]',
                                        "quality = " + json.dumps(commands))
        path = self.dir / "repo.toml"
        path.write_text(text)
        return path

    def test_passing_commands_pass(self):
        """gates, check 1."""
        contract = self.contract_with(["python3 -c pass", "python3 -c 'import sys; sys.exit(0)'"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.PASS, out)
        self.assertEqual(out.count(f"{cc.OUT_PASS}: {cg.CMD_QUALITY}: passed:"), 2)

    def test_failing_command_fails_and_names_it(self):
        """gates, check 1."""
        contract = self.contract_with(["python3 -c pass", "python3 -c 'import sys; sys.exit(3)'"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("failed with exit code 3: python3 -c 'import sys; sys.exit(3)'", out)

    def test_shell_syntax_is_refused_with_a_clear_message(self):
        """gates, check 1."""
        contract = self.contract_with(["python3 -c pass && python3 -c pass"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("shell syntax is not supported", out)

    def test_output_of_a_failed_check_is_shown(self):
        """gates, check 1."""
        contract = self.contract_with(["python3 -c 'print(\"the cause\"); raise SystemExit(2)'"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("the cause", out)

    def test_repo_only_needs_no_source(self):
        """gates, check 1: a run without access to the organization source."""
        contract = self.contract_with(["python3 -c pass"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), "--repo-only")
        self.assertEqual(code, cc.PASS, out)

    def test_repo_only_refuses_an_organization_file(self):
        """code-host, check 1."""
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(ORG), "--repo-only")
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn("not a repo contract", out)

    def test_missing_program_fails_and_names_it(self):
        """gates, check 1."""
        contract = self.contract_with(["no-such-program-xyz --version"])
        code, out = run(cg.CMD_QUALITY, f"--{cc.ARG_CONTRACT}", str(contract), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("cannot run: no-such-program-xyz", out)


class Verdict(Temp):
    def verdict(self, **changes) -> tuple[int, str]:
        return run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**changes)), *self.contract_args())

    def test_ready(self):
        """gates, check 1."""
        code, out = self.verdict()
        self.assertEqual(code, cc.PASS, out)
        self.assertTrue(out.startswith(cg.VERDICT_READY + "\n"))
        self.assertIn("tier low: review light, the engineer merges (['alice'])", out)

    def test_high_tier_for_a_protected_file(self):
        """gates, check 1: the first declared tier that matches a file applies."""
        code, out = self.verdict(**{cg.FACT_CHANGED_FILES: ["scripts/x.py", "docs/product.md"]})
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("tier high: review deep, the leader merges (['alice'])", out)

    def test_tier_order_comes_from_the_repo_contract(self):
        """gates, check 1: an organization file that declares a lower tier first does not change the order."""
        org = self.dir / "org.toml"
        org.write_text(ORG.read_text().replace("[tiers.high]\n", "[tiers.low]\nreview = \"light\"\n\n[tiers.high]\n"))
        path = self.facts(**{cg.FACT_CHANGED_FILES: ["scripts/x.py", "docs/product.md"]})
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(path), f"--{cc.ARG_CONTRACT}", str(REPO), f"--{cc.ARG_SOURCE}", str(org))
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("tier high:", out)

    def test_approvals_are_named_as_not_checked(self):
        """gates, check 1: the decision of iteration 1 is visible in the output."""
        code, out = self.verdict()
        self.assertIn("approvals are not checked in this version", out)

    def test_not_ready_names_each_reason(self):
        """gates, check 1."""
        code, out = self.verdict(**{
            cg.FACT_LINKED_ISSUES: [],
            cg.FACT_CHANGED_FILES: ["src/app.py"],
            cg.FACT_UNRESOLVED_THREADS: 2,
            cg.FACT_CHECKS: {"tests": cg.CHECK_PASS, "quality": "fail"},
        })
        self.assertEqual(code, cc.FAIL)
        self.assertTrue(out.startswith(cg.VERDICT_NOT_READY + "\n"))
        for expected in ("links no issue", "no reason is recorded", "checks not passed: ['quality']",
                         "2 unresolved review threads"):
            self.assertIn(expected, out)

    def test_first_line_is_the_verdict_and_exit_code_matches(self):
        """gates, check 2."""
        code, out = self.verdict()
        self.assertEqual((code, out.splitlines()[0]), (cc.PASS, cg.VERDICT_READY))
        code, out = self.verdict(**{cg.FACT_UNRESOLVED_THREADS: 1})
        self.assertEqual((code, out.splitlines()[0]), (cc.FAIL, cg.VERDICT_NOT_READY))

    def test_json_verdict(self):
        """gates, check 2: the JSON form for the evidence record."""
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts()), *self.contract_args(), f"--{cc.ARG_JSON}")
        self.assertEqual(code, cc.PASS, out)
        data = json.loads(out)
        self.assertEqual(data[cg.JSON_KEY_VERDICT], cg.VERDICT_READY)
        self.assertEqual(data[cg.JSON_KEY_TIER], "low")
        self.assertEqual([g[cg.JSON_KEY_GATE] for g in data[cg.JSON_KEY_GATES]], [cg.CMD_LINK, cg.CMD_DOCUMENTS])

    def test_plan_before_code(self):
        """plan-before-the-code, check 1."""
        with_flag = self.dir / "repo-with-plan-flag.toml"
        with_flag.write_text(REPO.read_text() + f"\n[build]\n{cg.FIELD_PLAN_BEFORE_CODE.split('.')[1]} = true\n")
        args = [f"--{cc.ARG_CONTRACT}", str(with_flag), f"--{cc.ARG_SOURCE}", str(ORG)]
        intent = {cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: False}

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [intent]})), *args)
        self.assertEqual(code, cc.FAIL)
        self.assertIn("plan: `plans/app.md` is missing", out)

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [{**intent, cg.INTENT_PLAN: True}]})), *args)
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("plan: plans/app.md exists", out)

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts()), *args)
        self.assertEqual(code, cc.FAIL)
        self.assertIn("plan: no linked issue names an intent", out)

        intents_only = {cg.FACT_CHANGED_FILES: ["intents/app.md"]}
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**intents_only)), *args)
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("plan: not needed, the change is the Plan phase", out)

        code, out = self.verdict(**{cg.FACT_INTENTS: [intent]})     # the sample contract has no flag
        self.assertEqual(code, cc.PASS, out)
        self.assertNotIn("plan:", out)

    def test_a_removed_intent_needs_no_plan(self):
        """plan-before-the-code, check 4 (#71): a change request that renames an intent and its plan is ready;
        the old path needs no plan, and the reasons name both files. A deletion alone is ready too. A path
        that the change request does not touch still needs its plan."""
        with_flag = self.dir / "repo-with-plan-flag.toml"
        with_flag.write_text(REPO.read_text() + f"\n[build]\n{cg.FIELD_PLAN_BEFORE_CODE.split('.')[1]} = true\n")
        args = [f"--{cc.ARG_CONTRACT}", str(with_flag), f"--{cc.ARG_SOURCE}", str(ORG)]
        old = {cg.INTENT_PATH: "intents/a.md", cg.INTENT_PLAN: False, cg.INTENT_REMOVED: True}
        new = {cg.INTENT_PATH: "intents/b.md", cg.INTENT_PLAN: True, cg.INTENT_REMOVED: False}
        wrong = {cg.INTENT_PATH: "intents/gatez.md", cg.INTENT_PLAN: False}

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [old, new]})), *args)
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("plan: plans/b.md exists", out)
        self.assertIn("plan: intents/a.md is removed by the change request, no plan needed", out)

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [old]})), *args)
        self.assertEqual(code, cc.PASS, out)

        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [old, wrong]})), *args)
        self.assertEqual(code, cc.FAIL)
        self.assertIn("plan: `plans/gatez.md` is missing", out)


class ReviewLoop(Temp):
    """The sample repo: review_loop 3, threshold medium."""

    def verdict(self, **changes) -> str:
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**changes)), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)     # shadow mode: the loop changes no verdict
        return out

    def test_no_review_yet(self):
        """review-loop, check 3."""
        self.assertIn("review loop: no review yet", self.verdict())
        self.assertIn("review loop: no review yet", self.verdict(**{cg.FACT_REVIEW_ROUNDS: 0, cg.FACT_REVIEW_SEVERITY: None}))

    def test_open_below_the_limit(self):
        """review-loop, check 3."""
        out = self.verdict(**{cg.FACT_REVIEW_ROUNDS: 1, cg.FACT_REVIEW_SEVERITY: "high"})
        self.assertIn("review loop: round 1 of 3, highest open severity high: a finding at medium or above keeps the loop open", out)

    def test_limit_reached_a_person_decides(self):
        """review-loop, check 3."""
        out = self.verdict(**{cg.FACT_REVIEW_ROUNDS: 3, cg.FACT_REVIEW_SEVERITY: "medium"})
        self.assertIn("review loop: round 3 of 3, highest open severity medium: the limit is reached, a person decides", out)

    def test_closed_below_the_threshold(self):
        """review-loop, check 3."""
        for severity in ("low", "none"):
            with self.subTest(severity=severity):
                out = self.verdict(**{cg.FACT_REVIEW_ROUNDS: 2, cg.FACT_REVIEW_SEVERITY: severity})
                self.assertIn(f"review loop: round 2 of 3, highest open severity {severity}: the loop is closed", out)

    def test_a_report_without_the_line_still_shows_the_round(self):
        """review-loop, check 3."""
        out = self.verdict(**{cg.FACT_REVIEW_ROUNDS: 2, cg.FACT_REVIEW_SEVERITY: None})
        self.assertIn("review loop: round 2 of 3, no severity line in the report", out)

    def test_a_wrong_severity_or_count_cannot_run(self):
        """review-loop, check 3: the facts are validated."""
        for changes in ({cg.FACT_REVIEW_SEVERITY: "huge"}, {cg.FACT_REVIEW_ROUNDS: -1}, {cg.FACT_REVIEW_ROUNDS: "3"}):
            with self.subTest(changes=changes):
                code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**changes)), *self.contract_args())
                self.assertEqual(code, cc.CANNOT_RUN)
                self.assertIn("wrong value", out)


class Record(Temp):
    def test_record_has_the_documented_form(self):
        """evidence-record, check 1."""
        record = self.dir / "record.json"
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts()), *self.contract_args(),
                        f"--{cg.ARG_RECORD}", str(record), "--scripts-version", "abc123")
        self.assertEqual(code, cc.PASS, out)
        self.assertTrue(out.startswith(cg.VERDICT_READY + "\n"))
        data = json.loads(record.read_text())
        for key in cg.RECORD_KEYS + (cg.JSON_KEY_VERDICT, cg.JSON_KEY_SOURCE, cg.JSON_KEY_REASONS, cg.JSON_KEY_TIER,
                                     cg.JSON_KEY_APPROVER, cg.JSON_KEY_MERGES, cg.JSON_KEY_GATES, cg.FACT_CHECKS):
            self.assertIn(key, data)
        self.assertEqual(data[cg.RECORD_KEYS[0]], cg.RECORD_FORM)
        self.assertEqual(data[cg.RECORD_KEYS[1]], 23)
        self.assertEqual(data[cg.RECORD_KEYS[3]], "abc123")
        self.assertEqual(data[cg.RECORD_KEYS[4]], [])
        self.assertEqual(data[cg.RECORD_KEYS[5]], [])
        self.assertEqual(data[cg.FACT_REVIEW_ROUNDS], 0)
        self.assertIsNone(data[cg.FACT_REVIEW_SEVERITY])
        self.assertRegex(data[cg.RECORD_KEYS[2]], r"^\d{4}-\d{2}-\d{2}T")

    def test_false_failures_of_the_facts_are_in_the_record(self):
        """evidence-record, check 2."""
        record = self.dir / "record.json"
        facts = self.facts(**{cg.FACT_FALSE_FAILURES: [{cg.JSON_KEY_GATE: "documents", "reason": "the gate misread a path"}]})
        code, _ = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(facts), *self.contract_args(), f"--{cg.ARG_RECORD}", str(record))
        self.assertEqual(code, cc.PASS)
        self.assertEqual(json.loads(record.read_text())[cg.RECORD_KEYS[4]][0]["reason"], "the gate misread a path")


class Patterns(unittest.TestCase):
    def test_star_stays_in_one_segment_and_double_star_crosses(self):
        """gates, check 1: the pattern language of paths. reason-next-to-the-part, check 11: the matcher
        lives in the checker, and the gate calls it there."""
        cases = [
            ("src/*", "src/x.py", True), ("src/*", "src/a/b.py", False),
            ("*.py", "x.py", True), ("*.py", "a/x.py", False),
            ("scripts/**", "scripts/x.py", True), ("scripts/**", "scripts/a/b.py", True),
            ("docs/**/*.md", "docs/b.md", True), ("docs/**/*.md", "docs/a/b.md", True), ("docs/**/*.md", "docs/a/b.txt", False),
            ("**", "any/where.txt", True), ("charter.toml", "charter.toml", True), ("charter.toml", "x/charter.toml", False),
        ]
        for pattern, file, expected in cases:
            with self.subTest(pattern=pattern, file=file):
                self.assertEqual(cc.matches(file, [pattern]), expected)


class NoModel(unittest.TestCase):
    def test_the_gate_script_imports_no_network_or_model_library(self):
        """gates, check 3."""
        text = (ROOT / "charter" / "scripts" / "charter_gate.py").read_text()
        for name in ("anthropic", "openai", "urllib", "http.client", "requests", "socket"):
            self.assertNotIn(f"import {name}", text)
            self.assertNotIn(f"from {name}", text)


class PlanPlace(Temp):
    SETUP_FLAGS = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
                   "--leader", "alice", "--quality", "python3 -m unittest discover -s tests"]

    def test_the_plan_of_an_intent_is_in_the_plans_folder(self):
        """plan-tier, check 1."""
        self.assertEqual(cg.plan_of("intents/app.md"), "plans/app.md")
        self.assertEqual(cg.plan_of("intents/sub/app.md"), "plans/sub/app.md")
        self.assertEqual(cg.old_plan_of("intents/app.md"), "intents/app.plan.md")
        self.assertEqual(cg.old_plan_of("intents/sub/app.md"), "intents/sub/app.plan.md")

    def test_the_missing_plan_names_the_new_place(self):
        """plan-tier, check 2: the message names the new place, and the old place that counts too."""
        with_flag = self.dir / "repo-with-plan-flag.toml"
        with_flag.write_text(REPO.read_text() + f"\n[build]\n{cg.FIELD_PLAN_BEFORE_CODE.split('.')[1]} = true\n")
        args = [f"--{cc.ARG_CONTRACT}", str(with_flag), f"--{cc.ARG_SOURCE}", str(ORG)]
        intent = {cg.INTENT_PATH: "intents/app.md", cg.INTENT_PLAN: False}
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_INTENTS: [intent]})), *args)
        self.assertEqual(code, cc.FAIL)
        self.assertIn("plan: `plans/app.md` is missing. A plan at the old place, `intents/app.plan.md`, counts too.", out)

    def test_a_change_with_its_plan_takes_the_tier_of_its_code(self):
        """plan-tier, check 3: the tiers of the contract that the setup step writes."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cs.main([*self.SETUP_FLAGS, "--target", str(self.dir)]), cc.PASS)
        e = cc.effective_contract(self.dir / cs.CONTRACT_FILE, cc.DEFAULT_SCHEMA, ORG, self.dir / "cache")
        self.assertEqual(e.failures, [])
        self.assertEqual(cg.tier_of(["src/app.py", "plans/app.md"], e)[0], "low")
        self.assertEqual(cg.tier_of(["src/app.py", "intents/app.plan.md"], e)[0], "high")

    def test_the_decision_is_recorded(self):
        """plan-tier, check 9: the row D18 with its reason, and the row E10 names it."""
        text = (ROOT / "docs" / "decisions.md").read_text()
        d18 = re.search(r"^\| D18 \| (.+?) \| (.+?) \| 2026-11-20 \|$", text, re.M)
        self.assertIsNotNone(d18, "no row D18")
        self.assertIn("`plans/<part>.md`", d18.group(1))
        self.assertIn("no exclusion", d18.group(2))
        e10 = re.search(r"^\| E10 \| (.+?) \|", text, re.M)
        self.assertIn("Replaced by D18", e10.group(1))

    def test_both_manifests_name_the_version(self):
        """plan-tier, check 10."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 8))


class ReviewRounds(Temp):
    """The sample repo: review_loop 3, threshold medium. The facts carry the reports, as the collector writes them."""
    OPEN = "keeps the loop open"
    CLOSED = "the loop is closed"
    LIMIT = "the limit is reached, a person decides"

    def verdict(self, reports: list, **changes) -> str:
        facts = {cg.FACT_REVIEW_REPORTS: reports, cg.FACT_REVIEW_ROUNDS: len(reports),
                 cg.FACT_REVIEW_SEVERITY: reports[-1] if reports else None, **changes}
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**facts)), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)     # shadow mode: the loop changes no verdict
        return out

    def test_the_round_is_the_number_of_reports_in_the_current_loop(self):
        """review-rounds, check 1."""
        self.assertEqual(cg.current_round(["high", "medium", "blocker"], "medium"), 3)
        self.assertEqual(cg.current_round(["high"], "medium"), 1)
        self.assertEqual(cg.current_round([], "medium"), 0)
        self.assertIn("review loop: round 2 of 3, highest open severity high: a finding at medium", self.verdict(["medium", "high"]))

    def test_a_report_after_a_closed_one_starts_a_new_loop(self):
        """review-rounds, check 1."""
        self.assertEqual(cg.current_round(["high", "low", "medium"], "medium"), 1)
        self.assertEqual(cg.current_round(["high", "none", "high", "medium"], "medium"), 2)
        self.assertEqual(cg.current_round(["high", "medium", "low"], "medium"), 3)     # the closing report ends its own loop
        self.assertEqual(cg.current_round(["medium", "medium"], "high"), 1)            # the threshold of the contract decides
        self.assertEqual(cg.current_round(["medium", "medium"], "medium"), 2)
        out = self.verdict(["high", "low", "low"])
        self.assertIn("review loop: round 1 of 3, highest open severity low: " + self.CLOSED, out)

    def test_the_first_review_of_a_plan_is_round_one(self):
        """review-rounds, check 2: the case of the adopter, an intent that used three rounds and closed, then the
        first review of its plan with a medium finding."""
        out = self.verdict(["high", "medium", "low", "medium"])
        self.assertIn("review loop: round 1 of 3, highest open severity medium: a finding at medium or above " + self.OPEN, out)

    def test_a_push_after_a_closed_loop_is_no_round_above_the_limit(self):
        """review-rounds, check 2: the case of #57, pushes after a closed loop."""
        for reports in (["high", "medium", "low", "low", "none"], ["high", "high", "high", "none", "low", "none", "low"]):
            with self.subTest(reports=reports):
                out = self.verdict(reports)
                self.assertIn("review loop: round 1 of 3, highest open severity", out)
                self.assertIn(self.CLOSED, out)
                self.assertNotRegex(out, r"round [4-9] of 3")

    def test_three_open_reports_reach_the_limit(self):
        """review-rounds, check 3."""
        out = self.verdict(["high", "medium", "high"])
        self.assertIn("review loop: round 3 of 3, highest open severity high: " + self.LIMIT, out)
        out = self.verdict(["low", "high", "medium", "high"])
        self.assertIn("review loop: round 3 of 3, highest open severity high: " + self.LIMIT, out)

    def test_a_report_without_a_severity_line_counts_as_open(self):
        """review-rounds, check 3."""
        self.assertEqual(cg.current_round(["high", None, "medium"], "medium"), 3)
        self.assertEqual(cg.current_round([None, None], "medium"), 2)
        out = self.verdict(["high", None, "medium"])
        self.assertIn("review loop: round 3 of 3, highest open severity medium: " + self.LIMIT, out)
        self.assertIn("review loop: round 2 of 3, no severity line in the report", self.verdict(["low", "high", None]))

    def test_older_facts_are_read_as_before(self):
        """review-rounds, check 4: a facts file without `review_reports` takes the round from `review_rounds`."""
        older = {cg.FACT_REVIEW_ROUNDS: 2, cg.FACT_REVIEW_SEVERITY: "medium"}
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**older)), *self.contract_args())
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("review loop: round 2 of 3, highest open severity medium: a finding at medium or above " + self.OPEN, out)
        for wrong in (["huge"], "low", [1]):
            with self.subTest(reports=wrong):
                code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(self.facts(**{cg.FACT_REVIEW_REPORTS: wrong})),
                                *self.contract_args())
                self.assertEqual(code, cc.CANNOT_RUN)
                self.assertIn(f"wrong value for {cg.FACT_REVIEW_REPORTS}", out)

    def test_the_record_holds_the_reports_and_the_round(self):
        """review-rounds, check 7."""
        reports = ["high", "low", None, "medium"]
        record = self.dir / "record.json"
        facts = self.facts(**{cg.FACT_REVIEW_REPORTS: reports, cg.FACT_REVIEW_ROUNDS: 4, cg.FACT_REVIEW_SEVERITY: "medium"})
        code, out = run(cg.CMD_VERDICT, f"--{cg.ARG_FACTS}", str(facts), *self.contract_args(), f"--{cg.ARG_RECORD}", str(record))
        self.assertEqual(code, cc.PASS, out)
        data = json.loads(record.read_text())
        self.assertEqual(data[cg.FACT_REVIEW_REPORTS], reports)
        self.assertEqual(data[cg.FACT_REVIEW_ROUNDS], 2)
        self.assertEqual(data[cg.FACT_REVIEW_SEVERITY], "medium")

    def test_the_contract_document_says_what_a_round_is(self):
        """review-rounds, check 9."""
        text = (ROOT / "docs" / "contract.md").read_text()
        section = " ".join(text[text.index("### The review loop"):text.index("## The evidence record")].split())
        for part in ("A round is a report of the reviewer in the current loop", "A loop starts with the first report",
                     "a report without a severity line counts as open", "Each report stays on the change request as its own comment",
                     "fails, is no round"):
            with self.subTest(part=part):
                self.assertIn(part, section)

    def test_both_manifests_name_the_version(self):
        """review-rounds, check 10."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 9))


if __name__ == "__main__":
    unittest.main()
