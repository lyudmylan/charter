"""The closed list of questions of the intent reviewer, read by code. Intent: closed-list-of-questions.
Run: python3 -m unittest discover -s tests

No test here calls a model.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "charter" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import charter_gate as cg  # noqa: E402
import charter_review as cr  # noqa: E402

sys.path.insert(0, str(ROOT / "tests"))
from test_workflows import GUARD_STEP, HEAD, MARKER, POST_STEP, TEMPLATES, WORKFLOWS, run_block  # noqa: E402

SKILL = ROOT / "charter-practices" / "skills" / "intent-review" / "SKILL.md"
BEFORE_STEP = "Give the answers of code to the reviewer"
BASE_STEP = "Take the Charter scripts of the base branch"
INTENT = "intents/part.md"
INTENT_TEXT = """# Intent: a part

## Goal

A result.

## Acceptance checks

## Automatic checks

1. The first result.
   test: `tests/test_part.py::Part.test_one`
2. The second result.
   command: `python3 tools/check.py`

## Manual checks

3. A person looks. who: the leader. Not automatic: it is a judgment.
"""


def answers(fails: dict | None = None, unknown: tuple = (), closed: tuple = (), intent: str = INTENT, leave_out: int = 0) -> str:
    lines = []
    for number in cr.QUESTIONS:
        if number == leave_out:
            continue
        if number in (fails or {}):
            lines.append(f"- Q{number}: does not hold: {fails[number]}")
        elif number in unknown:
            lines.append(f"- Q{number}: unknown: the issue could not be read")
        elif number in closed:
            lines.append(f"- Q{number}: closed: Dropped finding: the port: the intent names it")
        else:
            lines.append(f"- Q{number}: holds")
    return f"### {intent}\n" + "\n".join(lines) + "\n"


def report(*sections: str, notes: str = "- none", line: str = "none") -> str:
    return (f"{MARKER}\nCommit: {HEAD}\n\n## Answers\n\n" + "\n".join(sections) + f"\n## Notes\n\n{notes}\n\n"
            f"Highest open severity: {line}\n")


class Repo(unittest.TestCase):
    """A repo with a main branch as `origin/main` and a change on its branch."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.git("init", "--quiet", "--initial-branch", "main")
        self.write("intents/old.md", INTENT_TEXT)
        self.write("intents/other.md", INTENT_TEXT)
        self.write("plans/other.md", "# Plan\n")
        self.commit("the main branch")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "--quiet", "-b", "change")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True).stdout.strip()

    def write(self, path: str, text: str) -> None:
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("-c", "user.name=a test", "-c", "user.email=none", "commit", "--quiet", "-m", message)

    def command(self, *args: str) -> tuple[int, str]:
        done = subprocess.run([sys.executable, str(SCRIPTS / "charter_review.py"), *args, "--root", str(self.root)],
                              capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr


class TheList(unittest.TestCase):
    def test_the_skill_holds_each_question_with_the_severity_of_the_code(self):
        """closed-list, check 1: eight questions; the skill and the code give each one the same severity; each
        severity blocks at the default threshold; a note is below it."""
        text = SKILL.read_text()
        found = {int(number): severity for number, severity in re.findall(r"(?m)^- Q(\d+), `(\w+)`: \S", text)}
        self.assertEqual(found, cr.QUESTIONS)
        self.assertEqual(sorted(found), list(range(1, 9)))
        threshold = cg.SEVERITIES.index(cg.DEFAULT_REVIEW_THRESHOLD)
        for severity in found.values():
            self.assertGreaterEqual(cg.SEVERITIES.index(severity), threshold)
        self.assertLess(cg.SEVERITIES.index(cr.NOTE_SEVERITY), threshold)
        for part in ("`holds`, `does not hold`, or `unknown`", "you choose no severity", "A question that does not apply to the intent holds",
                     "is a note, of severity `low`: it blocks nothing", "not a detail or a rare case of it", "a fact or a list in two places",
                     "a sentence that names a proof that cannot fail, when another check tries that behaviour",
                     "a contradiction that shows only in a rare case or a rare order of events", "one name for two things",
                     "a part of an item of the issue that the intent narrows", "a file that an edit left out",
                     "When that report holds no answers, a sentence that did not change since it holds, unless that report gave a finding on it",
                     "An older intent and the text of an issue are no such decision",
                     "answer `closed` for it", "the section `## Answers`", "a heading `### intents/<part>.md`", "`- Q1: holds`",
                     "answer again each question that did not hold or was unknown, and each question for a changed line",
                     "code reads the answers and writes this line again"):
            with self.subTest(part=part):
                self.assertIn(part, " ".join(text.split()))


class Answers(unittest.TestCase):
    def test_the_forms_of_an_answer_line(self):
        """closed-list, check 2: the line of an answer is read with and without the list mark and the marks of
        emphasis; the text of an answer runs to the next answer; a heading that names no intent ends a section."""
        text = ("### `intents/part.md`\n- Q1: holds\n* **Q2**: Does not hold: \"a sentence\": no check\n  Proposed: a new check.\n\n"
                "Q3 - unknown: the test file is long\n- `Q4`: **closed**: Dropped finding: x\n- Q5. holds.\n"
                "## Notes\n- Q6: does not hold: under no intent\n")
        got, outside = cr.read_answers(text)
        self.assertEqual(list(got), [INTENT])
        self.assertEqual({n: [a for a, _ in lines] for n, lines in got[INTENT].items()},
                         {1: ["holds"], 2: ["does not hold"], 4: ["closed"], 5: ["holds"]})
        self.assertEqual(got[INTENT][2][0][1], '"a sentence": no check\nProposed: a new check.\nQ3 - unknown: the test file is long')
        self.assertEqual(outside, [6])

    def test_the_severity_comes_from_the_list(self):
        """closed-list, check 3: the highest severity of a question that does not hold; `low` with a note or an
        answer `unknown` and no such question; `none` with neither. A closed answer blocks nothing. The worst
        line of a question counts, and the line that the reviewer wrote does not."""
        fail = '"a sentence": no check'
        for text, severity in (
            (report(answers()), "none"),
            (report(answers(), line="high"), "none"),
            (report(answers({2: fail})), "medium"),
            (report(answers({2: fail, 6: fail}), line="low"), "high"),
            (report(answers({5: fail}), answers({1: fail}, intent="intents/two.md")), "high"),
            (report(answers(unknown=(5,))), "low"),
            (report(answers(closed=(3,))), "none"),
            (report(answers(), notes="- `intents/part.md`: the count is wrong."), "low"),
            (report(answers(), notes="1. A numbered note."), "low"),
            (report(answers(), notes="No note."), "none"),
            (report(answers() + f"- Q7: does not hold: {fail}\n"), "medium"),
        ):
            with self.subTest(text=text[60:200]):
                self.assertEqual(cr.severity_of(text), severity)

    def test_a_report_that_lacks_an_answer_is_not_complete(self):
        """closed-list, check 4."""
        fail = '"a sentence": no check'
        for text, expected, message in (
            (report(answers(leave_out=8)), [INTENT], "intents/part.md: no answer to Q8"),
            (report(answers()), [INTENT, "intents/two.md"], "intents/two.md: the report holds no heading with this intent"),
            (report(answers() + "- Q9: holds\n"), [INTENT], "intents/part.md: Q9 is no question of the list"),
            (report(answers({2: ""})), [INTENT], "intents/part.md: Q2 does not hold, and the line names no sentence"),
            (f"{MARKER}\nCommit: {HEAD}\n\nNo finding.\n", [INTENT], "the report holds no answer of the form"),
            (f"{MARKER}\n- Q1: holds\n", [], "an answer to Q1 is under no heading of an intent"),
        ):
            with self.subTest(message=message):
                got, outside = cr.read_answers(text)
                self.assertIn(message, " | ".join(cr.problems(got, outside, expected)))
        got, outside = cr.read_answers(report(answers({2: fail}), answers(intent="intents/more.md")))
        self.assertEqual(cr.problems(got, outside, [INTENT]), [])
        # A change that adds no intent and no plan needs no answer: its report holds notes.
        self.assertEqual(cr.problems({}, [], []), [])


class TheChange(Repo):
    def test_the_intents_that_a_report_answers_for(self):
        """closed-list, check 5: each intent that the change adds, and the intent of each plan that it adds or
        changes. An intent that the change only changes, and a plan at the old place, are not in the list."""
        self.write("intents/new.md", INTENT_TEXT)
        self.write("intents/new.plan.md", "# A plan at the old place\n")
        self.write("intents/old.md", INTENT_TEXT + "\nOne more line.\n")
        self.write("plans/other.md", "# Plan\n\nA new step.\n")
        self.write("plans/alone.md", "# A plan with no intent\n")
        self.commit("the change")
        self.assertEqual(cr.expected_intents("origin/main", self.root), ["intents/new.md", "intents/other.md"])
        code, out = self.command("intents", "--base", "origin/main")
        self.assertEqual((code, out.split()), (0, ["intents/new.md", "intents/other.md"]))
        code, out = self.command("intents", "--base", "no-such-branch")
        self.assertEqual(code, 2)
        self.assertIn("git could not list the change", out)

    def test_code_answers_the_names_of_the_checks(self):
        """closed-list, check 6: a check with no test and no command; a named test file that is not in the repo,
        only when the plan of the intent is there; an intent with no part that code reads."""
        self.write(INTENT, INTENT_TEXT.replace("   command: `python3 tools/check.py`\n", ""))
        self.assertEqual(cr.answers_of_code(INTENT, self.root), ["check 2 names no test and no command"])
        self.write("plans/part.md", "# Plan\n")
        self.assertEqual(cr.answers_of_code(INTENT, self.root),
                         ["check 1: the test file tests/test_part.py is not in the repo", "check 2 names no test and no command"])
        self.write("tests/test_part.py", "")
        self.write(INTENT, INTENT_TEXT)
        self.assertEqual(cr.answers_of_code(INTENT, self.root), [])
        self.write(INTENT, "# Intent\n\nA text in another form.\n")
        self.assertIsNone(cr.answers_of_code(INTENT, self.root))
        self.assertIsNone(cr.answers_of_code("intents/none.md", self.root))

    def test_the_text_for_the_reviewer(self):
        """closed-list, check 6: the command `before` prints the answers of code for each intent of the change."""
        self.write(INTENT, INTENT_TEXT.replace("   command: `python3 tools/check.py`\n", ""))
        self.write("intents/fine.md", INTENT_TEXT)
        self.write("intents/free.md", "# Intent\n\nA text in another form.\n")
        self.commit("the change")
        code, out = self.command("before", "--base", "origin/main")
        self.assertEqual(code, 0)
        self.assertIn('### intents/part.md\n- Q3: does not hold: "check 2 names no test and no command" (the answer of code)\n', out)
        self.assertIn("### intents/fine.md\n- Q3: each automatic check names a test or a command", out)
        self.assertIn("### intents/free.md\n- Q3: code found no part", out)

    def test_the_command_closes_a_report(self):
        """closed-list, check 7: the command adds the answer of code under the heading of its intent, writes the
        severity line as the last line in the place of the one of the reviewer, and prints each open question. A
        report that is not complete ends it with 1 and stays as it is."""
        self.write(INTENT, INTENT_TEXT.replace("   command: `python3 tools/check.py`\n", ""))
        self.commit("the change")
        path = self.root.parent / "report.md"
        path.write_text(report(answers({5: '"an item": it is in no part'}), line="none"))
        code, out = self.command("close", "--report", str(path), "--base", "origin/main")
        self.assertEqual(code, 0, out)
        text = path.read_text()
        self.assertTrue(text.endswith("\n\nHighest open severity: high\n"), text[-80:])
        self.assertEqual(text.count("Highest open severity:"), 1)
        self.assertIn('### intents/part.md\n- Q3: does not hold: "check 2 names no test and no command" (the answer of code)\n- Q1: holds', text)
        self.assertEqual(out.splitlines(), ["intents/part.md: Q3 does not hold (high)", "intents/part.md: Q5 does not hold (medium)",
                                            "Highest open severity: high"])
        # A second pass adds no second line of code.
        self.command("close", "--report", str(path), "--base", "origin/main")
        self.assertEqual(path.read_text().count("(the answer of code)"), 1)
        before = report(answers(leave_out=4))
        path.write_text(before)
        code, out = self.command("close", "--report", str(path), "--base", "origin/main")
        self.assertEqual(code, 1)
        self.assertIn("intents/part.md: no answer to Q4", out)
        self.assertIn("the report is not complete", out)
        self.assertEqual(path.read_text(), before)
        self.assertEqual(self.command("close", "--report", str(path) + ".none", "--base", "origin/main")[0], 2)
        code, out = self.command("severity", "--report", str(path))
        self.assertEqual((code, out.strip()), (0, "Highest open severity: none"))


class TheWorkflow(Repo):
    files = {"this workflow": (WORKFLOWS / "review-intents.yml").read_text(), "the template": (TEMPLATES / "review-intents.yml").read_text()}

    def run_step(self, step: str, record: str | None, with_script: bool = True) -> tuple[int, str, str | None]:
        temp = self.root.parent / "temp"
        shutil.rmtree(temp, ignore_errors=True)
        if with_script:
            shutil.copytree(SCRIPTS, temp / "charter" / "charter" / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        folder = self.root.parent / "host"
        shutil.rmtree(folder, ignore_errors=True)
        (folder / "bin").mkdir(parents=True)
        gh = folder / "bin" / "gh"
        gh.write_text('#!/bin/sh\ncp "$5" "$POSTED"\n')
        gh.chmod(0o755)
        execution = folder / "execution.json"
        if record is not None:
            execution.write_text(json.dumps([{"type": "result", "result": record}]))
        env = {"PATH": f"{folder / 'bin'}:{os.environ['PATH']}", "RUNNER_TEMP": str(temp), "PR_NUMBER": "7", "BASE_REF": "main",
               "EXECUTION_FILE": str(execution), "POSTED": str(folder / "posted")}
        done = subprocess.run(["bash", "-e", "-c", step], cwd=self.root, capture_output=True, text=True, env=env)
        posted = (folder / "posted").read_text() if (folder / "posted").exists() else None
        return done.returncode, done.stdout + done.stderr, posted

    def test_the_step_posts_a_report_with_the_severity_of_code(self):
        """closed-list, check 8: the step that posts the report closes it first. The severity line is the one of
        code; a report that is not complete is not posted; with a version of Charter that has no such script,
        the report is posted as the reviewer wrote it. The step is the same in the template and in this repo."""
        self.write(INTENT, INTENT_TEXT)
        self.commit("the change")
        step = run_block(self.files["this workflow"], POST_STEP)
        self.assertEqual(step, run_block(self.files["the template"], POST_STEP))
        text = report(answers({2: '"a sentence": no check names it'}), line="none")
        code, out, posted = self.run_step(step, "Here it is.\n" + text)
        self.assertEqual(code, 0, out)
        self.assertTrue(posted.startswith(MARKER) and posted.endswith("\nHighest open severity: medium\n"), posted)
        self.assertIn("intents/part.md: Q2 does not hold (medium)", out)
        code, out, posted = self.run_step(step, report(answers(leave_out=6)))
        self.assertEqual(code, 0, out)
        self.assertIsNone(posted)
        self.assertIn("intents/part.md: no answer to Q6", out)
        self.assertIn("no report to post", out)
        code, out, posted = self.run_step(step, text, with_script=False)
        self.assertEqual((code, posted.rstrip("\n")), (0, text.rstrip("\n")), out)

    def test_code_answers_before_the_reviewer_and_runs_no_code_of_the_change(self):
        """closed-list, check 8: the step before the reviewer writes the answers of code into the folder that the
        reviewer reads; the prompt names the file; the scripts are the ones of the fetched Charter or, in this
        repo, of the base branch; the two new steps hold no token."""
        self.write(INTENT, INTENT_TEXT.replace("   command: `python3 tools/check.py`\n", ""))
        self.commit("the change")
        for name, text in self.files.items():
            with self.subTest(file=name):
                self.assertLess(text.index("- name: " + BEFORE_STEP), text.index("uses: anthropics/claude-code-action"))
                self.assertIn("${{ runner.temp }}/review/answers-of-code.md", text)
                self.assertIn("copy each line `does not hold` of it into your answers", text)
                self.assertIn("a report that lacks an answer to a question is not posted", text)
                self.assertIn("Quote it under Q6, with the answer `does not hold`.", text)
                self.assertIn("Read(/${{ runner.temp }}/review/**)", text)
                block = text[text.index("- name: " + BEFORE_STEP):text.index("- name: Note the report before the review")]
                self.assertNotIn("TOKEN", block)
                self.assertLess(text.index("- name: " + POST_STEP), text.index("- name: " + GUARD_STEP))
        own = self.files["this workflow"]
        self.assertNotIn("python3 charter/scripts", own)
        base = own[own.index("- name: " + BASE_STEP):own.index("- name: Give the earlier reports")]
        self.assertIn('git archive "origin/$BASE_REF" charter/scripts | tar -x -C "$RUNNER_TEMP/charter"', base)
        self.assertNotIn("TOKEN", base)
        self.assertIn('git clone --quiet --depth 1 --branch "charter--v$VERSION"', self.files["the template"])
        step = run_block(self.files["the template"], BEFORE_STEP)
        self.assertEqual(step, run_block(own, BEFORE_STEP))
        code, out, _ = self.run_step(step, None)
        self.assertEqual(code, 0, out)
        written = (self.root.parent / "temp" / "review" / "answers-of-code.md").read_text()
        self.assertIn('- Q3: does not hold: "check 2 names no test and no command" (the answer of code)', written)
        code, out, _ = self.run_step(step, None, with_script=False)
        self.assertEqual(code, 0, out)
        self.assertFalse((self.root.parent / "temp" / "review" / "answers-of-code.md").exists())

    def test_the_scripts_of_the_base_branch(self):
        """closed-list, check 8: the step of this repo takes the folder of the scripts from the base branch."""
        self.write("charter/scripts/a.py", "print('the base')\n")
        self.commit("a script on the change")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.write("charter/scripts/a.py", "print('the change')\n")
        self.commit("the change")
        code, out, _ = self.run_step(run_block(self.files["this workflow"], BASE_STEP), None, with_script=False)
        self.assertEqual(code, 0, out)
        self.assertEqual((self.root.parent / "temp" / "charter" / "charter" / "scripts" / "a.py").read_text(), "print('the base')\n")


if __name__ == "__main__":
    unittest.main()
