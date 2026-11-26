"""The test set of the intent reviewer: the command that runs it. Intent: intent-reviewer-test-set.

No test here calls a model. A stand-in for Claude Code records how the command started it and answers with
the text that a case of the test holds.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "evals" / "intent-review" / "run.py"
spec = importlib.util.spec_from_file_location("intent_review_run", RUN)
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)

STAND_IN = '''#!/usr/bin/env python3
import json, os, subprocess, sys
if "--version" in sys.argv:
    print("stand-in 0")
    sys.exit(0)
prompt = sys.stdin.read()
case = os.environ["CHARTER_EVAL_CASE"]
shell = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
record = {"argv": sys.argv[1:], "prompt": prompt, "cwd": os.getcwd(), "issue": shell("gh", "issue", "view", "7"),
          "other": subprocess.run(["gh", "api", "user"], capture_output=True).returncode,
          "absent": subprocess.run(["gh", "issue", "view", "8"], capture_output=True).returncode,
          "second": shell("gh", "issue", "view", "9", "--json", "title,body"),
          "diff": shell("git", "diff", "--name-only", "origin/main...HEAD", "--", "intents/", "plans/"),
          "files": sorted(os.listdir("."))}
with open(os.path.join(os.environ["STAND_IN_RECORD"], os.path.basename(case) + ".json"), "w") as out:
    json.dump(record, out)
answer = os.path.join(case, "stand-in-answer.md")
text = open(answer).read() if os.path.exists(answer) else ""
print(json.dumps({"type": "result", "result": text, "num_turns": 3, "total_cost_usd": 0.25, "permission_denials": []}))
'''


def report(severity: str, finding: str = "") -> str:
    return (f"A sentence before the report.\n{run.MARKER}\nCommit: 0000\n\n## Findings\n\n{finding}\n\n"
            f"Highest open severity: {severity}\n")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.cases = self.work / "cases"
        self.record = self.work / "record"
        self.record.mkdir()
        binary = self.work / "bin" / "claude"
        binary.parent.mkdir()
        binary.write_text(STAND_IN)
        binary.chmod(0o755)
        self.old = {key: os.environ.get(key) for key in ("CHARTER_EVAL_CLAUDE", "STAND_IN_RECORD")}
        os.environ["CHARTER_EVAL_CLAUDE"] = str(binary)
        os.environ["STAND_IN_RECORD"] = str(self.record)

    def tearDown(self):
        for key, value in self.old.items():
            os.environ.pop(key, None) if value is None else os.environ.__setitem__(key, value)
        self.temp.cleanup()

    def case(self, name: str, expected: str, answer: str, earlier: bool = False, finding: str = "") -> Path:
        folder = self.cases / name
        shutil.rmtree(folder, ignore_errors=True)
        for state, text in (("base", ""), ("head", "# Intent\n\nThe second text.\n")):
            (folder / state / "intents").mkdir(parents=True)
            (folder / state / "docs").mkdir()
            (folder / state / "docs" / "product.md").write_text("# The product\n")
            (folder / state / "evals").mkdir()
            (folder / state / "evals" / "answers.md").write_text("the answers\n")
            if text:
                (folder / state / "intents" / "part.md").write_text(text)
        if earlier:
            (folder / "earlier" / "intents").mkdir(parents=True)
            (folder / "earlier" / "intents" / "part.md").write_text("# Intent\n\nThe first text.\n")
            (folder / "earlier-report.md").write_text(f"{run.MARKER}\nCommit: an-old-commit\n\nHighest open severity: medium\n")
        (folder / "issue.md").write_text("#7 The issue of the case\n\nIts text.\n\n-----\n\n#9 A second issue\n\nMore text.\n")
        (folder / "stand-in-answer.md").write_text(answer)
        fields = [f'expected = "{expected}"', 'source = "a test"'] + ([f"finding = ['{finding}']"] if finding else [])
        (folder / "case.toml").write_text("\n".join(fields) + "\n")
        return folder

    def start(self, *args: str) -> tuple:
        out = self.work / "out"
        done = subprocess.run(["python3", str(RUN), "--cases", str(self.cases), "--out", str(out), *args],
                              capture_output=True, text=True, cwd=ROOT, check=False)
        return done.returncode, done.stdout, out

    def recorded(self, name: str) -> dict:
        return json.loads((self.record / f"{name}.json").read_text())


class Workspace(Fixture):
    def test_a_case_becomes_a_repo_with_the_base_and_the_change(self):
        # check 1
        built = run.build(run.read_case(self.case("one", "blocks", "", earlier=True)), self.work / "w")
        names = run.git(built["workspace"], "diff", "--name-only", "origin/main...HEAD", "--", "intents/", "plans/")
        self.assertEqual(names, "intents/part.md")
        self.assertEqual(run.git(built["workspace"], "rev-parse", "HEAD"), built["head"])
        earlier = (built["temp"] / "review" / "earlier-reports.md").read_text()
        commit = earlier.split("Commit: ")[1].split()[0]
        self.assertNotEqual(commit, "an-old-commit")
        self.assertIn("The first text", run.git(built["workspace"], "show", f"{commit}:intents/part.md"))
        self.assertEqual(run.git(built["workspace"], "rev-parse", "HEAD~1"), commit)
        self.assertTrue((built["temp"] / "charter" / "charter-practices" / "skills" / "intent-review" / "SKILL.md").is_file())

    def test_the_answers_of_the_test_set_are_in_no_folder_that_the_reviewer_reads(self):
        # check 2
        built = run.build(run.read_case(self.case("one", "passes", "")), self.work / "w")
        self.assertFalse((built["workspace"] / "evals").exists())
        self.assertEqual(list((built["temp"] / "charter").rglob("evals")), [])
        self.assertEqual(list(built["workspace"].rglob("case.toml")), [])

    def test_a_case_of_commits_of_this_repo(self):
        # check 1, the second form
        head = run.git(ROOT, "rev-parse", "HEAD")
        folder = self.cases / "commits"
        folder.mkdir(parents=True)
        (folder / "issue.md").write_text("An issue\n")
        (folder / "case.toml").write_text(f'expected = "passes"\nsource = "a test"\nbase = "{head}"\nhead = "{head}"\n')
        built = run.build(run.read_case(folder), self.work / "w")
        self.assertTrue((built["workspace"] / "charter.toml").is_file())
        self.assertFalse((built["workspace"] / "evals").exists())

    def test_a_case_with_a_missing_part_cannot_run(self):
        # check 6
        folder = self.case("one", "blocks", "")
        for change, message in (
            (lambda: (folder / "issue.md").unlink(), "no issue.md"),
            (lambda: (folder / "case.toml").write_text('expected = "maybe"\nsource = "a test"\n'), "expected is"),
            (lambda: (folder / "case.toml").write_text('expected = "passes"\n'), "source"),
            (lambda: (folder / "case.toml").write_text('expected = "passes"\nsource = "x"\nbase = "a"\nhead = "b"\n'),
             "or it holds the folders"),
        ):
            folder = self.case("one", "blocks", "")
            change()
            with self.assertRaises(run.CannotRun) as raised:
                run.read_case(folder)
            self.assertIn(message, str(raised.exception))
        self.case("one", "blocks", "")
        (self.cases / "one" / "earlier").mkdir()
        with self.assertRaises(run.CannotRun):
            run.read_case(self.cases / "one")


class TheRun(Fixture):
    def test_the_reviewer_starts_in_the_form_of_the_workflow(self):
        # check 3
        self.case("one", "passes", report("low"))
        code, _, _ = self.start()
        self.assertEqual(code, 0)
        got = self.recorded("one")
        template = run.TEMPLATE.read_text()
        argv = got["argv"]
        self.assertEqual(argv[argv.index("--max-turns") + 1], run.re.search(r"--max-turns (\d+)", template).group(1))
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "dontAsk")
        allowed = argv[argv.index("--allowedTools") + 1]
        self.assertIn("Bash(gh issue view:*)", allowed)
        self.assertIn("Read(./**)", allowed)
        self.assertIn("--disallowedTools", argv)
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "project")
        self.assertIn("--strict-mcp-config", argv)
        self.assertEqual(argv[argv.index("--model") + 1], run.MODEL)
        for text in (allowed, got["prompt"]):
            self.assertNotIn("${{", text)
        self.assertIn("charter-practices/skills/intent-review/SKILL.md exactly", got["prompt"])
        self.assertIn("The report is your final answer", got["prompt"])
        self.assertRegex(got["prompt"], r"The head commit is [0-9a-f]{40}\.")
        self.assertEqual(got["diff"].strip(), "intents/part.md")
        self.assertNotIn("evals", got["files"])

    def test_the_stand_in_of_the_code_host_answers_from_the_case(self):
        # check 4
        self.case("one", "passes", report("none"))
        self.start()
        got = self.recorded("one")
        self.assertIn("The issue of the case", got["issue"])
        self.assertNotIn("A second issue", got["issue"])
        self.assertIn("A second issue", got["second"])
        self.assertNotEqual(got["absent"], 0)
        self.assertNotEqual(got["other"], 0)

    def test_the_result_counts_each_kind_and_keeps_each_report(self):
        # check 7
        medium = "1. **medium**, `intents/part.md`, check 2: the check proves nothing."
        self.case("a-right", "blocks", report("medium", medium), earlier=True, finding="check 2")
        self.case("b-alarm", "passes", report("medium", medium))
        self.case("c-miss", "blocks", report("low"))
        self.case("d-subject", "blocks", report("medium", medium), finding="the goal")
        self.case("e-right", "passes", report("none"))
        code, text, out = self.start("--jobs", "3")
        self.assertEqual(code, 0)
        self.assertIn("Cases: 5. Right: 2.", text)
        self.assertIn("False alarms: 1. Misses: 1. Another subject: 1. No report: 0.", text)
        self.assertIn("Cost that the runs report: 1.25 USD", text)
        result = json.loads((out / "result.json").read_text())
        self.assertEqual([row["result"] for row in result["cases"]],
                         ["right", "false alarm", "miss", "other subject", "right"])
        self.assertEqual((out / "report.md").read_text() + "\n", text.split("The result is in")[0])
        kept = (out / "reports" / "a-right.md").read_text()
        self.assertTrue(kept.startswith(run.MARKER))
        self.assertNotIn("A sentence before the report", kept)

    def test_a_case_with_no_report_ends_the_command_with_1(self):
        # check 7
        self.case("one", "passes", "I could not review this.")
        self.case("two", "passes", f"{run.MARKER}\nA report with no severity line.\n")
        code, text, out = self.start()
        self.assertEqual(code, 1)
        self.assertIn("No report: 2.", text)
        self.assertIn("no report", (out / "reports" / "one.md").read_text())

    def test_one_case_by_its_name_and_a_name_that_is_no_case(self):
        # check 7
        self.case("one", "passes", report("low"))
        self.case("two", "passes", report("low"))
        code, text, _ = self.start("--case", "two")
        self.assertEqual(code, 0)
        self.assertIn("Cases: 1.", text)
        code, text, _ = self.start("--case", "three")
        self.assertEqual(code, 2)
        self.assertIn("cannot run: no such case: three", text)


class Grader(unittest.TestCase):
    def test_the_severity_line_against_the_threshold(self):
        # check 5
        for expected, severity, threshold, result in (
            ("blocks", "medium", "medium", run.RIGHT), ("blocks", "high", "medium", run.RIGHT),
            ("blocks", "low", "medium", run.MISS), ("passes", "low", "medium", run.RIGHT),
            ("passes", "none", "medium", run.RIGHT), ("passes", "medium", "medium", run.FALSE_ALARM),
            ("passes", "medium", "high", run.RIGHT), ("blocks", "medium", "high", run.MISS),
        ):
            got = run.grade({"expected": expected}, report(severity), threshold)
            self.assertEqual((got["result"], got["severity"]), (result, severity), (expected, severity, threshold))
        self.assertEqual(run.grade({"expected": "passes"}, "no line", "medium")["result"], run.NO_REPORT)
        bold = f"{run.MARKER}\nHighest open severity: **Medium**\n"
        self.assertEqual(run.grade({"expected": "blocks"}, bold, "medium")["result"], run.RIGHT)
        two = report("medium") + "\nHighest open severity: low\n"
        self.assertEqual(run.grade({"expected": "passes"}, two, "medium")["result"], run.RIGHT)

    def test_the_subject_of_a_finding_at_the_threshold(self):
        # check 5
        text = report("medium", "1. **low**, check 9: a small thing about the goal.\n"
                                "2. **medium** — `intents/part.md`, check 2: no test proves it.")
        case = {"expected": "blocks", "finding": ["check 2"]}
        self.assertEqual(run.grade(case, text, "medium")["result"], run.RIGHT)
        # The subject is in a finding below the threshold only: that finding does not block.
        case = {"expected": "blocks", "finding": ["the goal"]}
        self.assertEqual(run.grade(case, text, "medium")["result"], run.OTHER_SUBJECT)
        case = {"expected": "blocks", "finding": ["no such words", "no TEST proves"]}
        self.assertEqual(run.grade(case, text, "medium")["result"], run.RIGHT)
        # The other forms in which the reviewer writes the number and the severity of a finding.
        for line in ("**1. medium — the text of the change request**\n\nIt differs from check 2.",
                     "1. medium: check 2 proves nothing.", "1. **High**, check 2."):
            got = run.grade({"expected": "blocks", "finding": ["check 2"]}, report("medium", line), "medium")
            self.assertEqual(got["result"], run.RIGHT, line)


class TheSet(unittest.TestCase):
    def test_each_case_of_the_set_has_its_parts_and_the_set_is_balanced(self):
        # check 8
        cases = [run.read_case(folder) for folder in sorted(run.CASES.iterdir()) if folder.is_dir()]
        self.assertGreaterEqual(len(cases), 18)
        for answer in (run.BLOCKS, run.PASSES):
            self.assertGreaterEqual(sum(1 for case in cases if case["expected"] == answer), 8, answer)
        self.assertGreaterEqual(sum(1 for case in cases if not case["commits"]), 4, "cases of an adopter")
        self.assertGreaterEqual(sum(1 for case in cases if case["has_earlier"]), 3, "cases of a later round")
        for case in cases:
            self.assertFalse((case["folder"] / "stand-in-answer.md").exists(), case["name"])
            for key in ("base", "head", "earlier"):
                if key in case:
                    self.assertRegex(case[key], r"^[0-9a-f]{40}$", case["name"])

    def test_the_documents_name_the_command(self):
        # check 9
        for path in ("docs/contract.md", "docs/product.md"):
            self.assertIn("evals/intent-review/run.py", (ROOT / path).read_text(), path)


if __name__ == "__main__":
    unittest.main()
