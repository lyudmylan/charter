"""Tests of the gates. Run: python3 -m unittest discover -s tests

Each test names the scenario file and the check that it implements, in its docstring.
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import charter_check as cc  # noqa: E402
import charter_gate as cg  # noqa: E402

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
        self.assertIn("references the open issue [22]", out)

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
        for expected in ("references no issue", "no reason is recorded", "checks not passed: ['quality']",
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


class Patterns(unittest.TestCase):
    def test_star_stays_in_one_segment_and_double_star_crosses(self):
        """gates, check 1: the pattern language of paths."""
        cases = [
            ("src/*", "src/x.py", True), ("src/*", "src/a/b.py", False),
            ("*.py", "x.py", True), ("*.py", "a/x.py", False),
            ("scripts/**", "scripts/x.py", True), ("scripts/**", "scripts/a/b.py", True),
            ("docs/**/*.md", "docs/b.md", True), ("docs/**/*.md", "docs/a/b.md", True), ("docs/**/*.md", "docs/a/b.txt", False),
            ("**", "any/where.txt", True), ("charter.toml", "charter.toml", True), ("charter.toml", "x/charter.toml", False),
        ]
        for pattern, file, expected in cases:
            with self.subTest(pattern=pattern, file=file):
                self.assertEqual(cg.matches(file, [pattern]), expected)


class NoModel(unittest.TestCase):
    def test_the_gate_script_imports_no_network_or_model_library(self):
        """gates, check 3."""
        text = (ROOT / "scripts" / "charter_gate.py").read_text()
        for name in ("anthropic", "openai", "urllib", "http.client", "requests", "socket"):
            self.assertNotIn(f"import {name}", text)
            self.assertNotIn(f"from {name}", text)


if __name__ == "__main__":
    unittest.main()
