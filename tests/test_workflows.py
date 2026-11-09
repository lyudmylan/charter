"""Tests of the workflow files, read as text: the standard library has no YAML parser.
Run: python3 -m unittest discover -s tests"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
TEMPLATES = ROOT / "charter" / "templates"
BEFORE_STEP, GUARD_STEP = "Note the report before the review", "The run fails when the reviewer posted no report"
NO_REPORT = "the reviewer posted no report"
READ_ONLY = {"Read", "Glob", "Grep"}
# A command that only reads or only posts the one comment.
ALLOWED_COMMANDS = re.compile(
    r"^Bash\((git diff|git log|gh issue view|gh issue list|gh pr view|gh pr comment):\*\)$|"
    r"^Bash\(gh api repos/\$\{\{ github\.repository \}\}/issues/\*/comments\*\)$|"
    r"^Bash\(gh api -X PATCH repos/\$\{\{ github\.repository \}\}/issues/comments/\*\)$"
)


def run_block(workflow: str, step: str) -> str:
    """The `run:` script of the named step of a workflow, read as text."""
    lines = workflow.splitlines()
    start = lines.index(f"      - name: {step}")
    first = next(i for i in range(start + 1, len(lines)) if lines[i] == "        run: |")
    script = []
    for line in lines[first + 1:]:
        if line and not line.startswith("          "):
            break
        script.append(line[10:])
    return "\n".join(script) + "\n"


def run_shell(script: str, folder: Path, env: dict[str, str]) -> tuple[int, str]:
    """Runs the script of a step with `bash -e`, as the host does, with a `gh` on the path that answers with
    the value of `GH_ANSWER`. Returns the exit code and the output."""
    (folder / "bin").mkdir(parents=True, exist_ok=True)
    gh = folder / "bin" / "gh"
    gh.write_text('#!/bin/sh\necho "$GH_ANSWER"\n')
    gh.chmod(0o755)
    result = subprocess.run(["bash", "-e", "-c", script], cwd=folder, capture_output=True, text=True,
                            env={**env, "PATH": f"{folder / 'bin'}:{os.environ['PATH']}"})
    return result.returncode, result.stdout + result.stderr


class ReviewIntents(unittest.TestCase):
    text = (WORKFLOWS / "review-intents.yml").read_text()
    template = (TEMPLATES / "review-intents.yml").read_text()

    def test_paths_and_tools(self):
        """intent-reviewer, check 1."""
        self.assertIn('paths: ["intents/**"]', self.text)
        self.assertIn("on:\n  pull_request:", self.text)
        self.assertNotIn("pull_request_target", self.text)
        tools = re.search(r'--allowedTools "([^"]+)"', self.text)
        self.assertIsNotNone(tools, "no allowed tools")
        for tool in tools.group(1).split(","):
            with self.subTest(tool=tool):
                self.assertTrue(tool in READ_ONLY or ALLOWED_COMMANDS.match(tool), f"tool not read-only or comment: {tool}")
        for forbidden in ("Write", "Edit", "NotebookEdit", "WebFetch"):
            self.assertNotIn(forbidden, tools.group(1))
        self.assertIn("contents: read", self.text)

    def test_a_run_without_a_report_fails(self):
        """intent-reviewer, check 4 (#70): the run fails when the report comment was neither posted nor updated,
        and passes when it was. The two steps have the same text in the template and in this workflow, and
        they stand before and after the reviewer."""
        step = run_block(self.text, GUARD_STEP)
        self.assertEqual(step, run_block(self.template, GUARD_STEP))
        self.assertEqual(run_block(self.text, BEFORE_STEP), run_block(self.template, BEFORE_STEP))
        for text in (self.text, self.template):
            self.assertLess(text.index(BEFORE_STEP), text.index("anthropics/claude-code-action"))
            self.assertLess(text.index("anthropics/claude-code-action"), text.index(GUARD_STEP))
            self.assertIn(f"      - name: {GUARD_STEP}\n        if: always()\n", text)
        folder = Path(tempfile.mkdtemp())
        try:
            t1, t2 = "2026-11-09T10:00:00Z", "2026-11-09T10:05:00Z"
            for before, after, passes in (("none", "none", False), (t1, t1, False), ("none", t2, True), (t1, t2, True)):
                with self.subTest(before=before, after=after):
                    env = {"BEFORE": before, "GH_ANSWER": after, "PR_NUMBER": "7", "GITHUB_REPOSITORY": "owner/name",
                           "EXECUTION_FILE": ""}
                    code, out = run_shell(step, folder, env)
                    self.assertEqual(code == 0, passes, out)
                    self.assertEqual(NO_REPORT in out, not passes, out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    @unittest.skipUnless(shutil.which("jq"), "jq is not on this computer; the runner of the host has it")
    def test_the_denied_commands_are_printed(self):
        """intent-reviewer, check 4 (#70): the denied commands of the run are in the log, from the execution
        file of the action, so that the next silent run names its cause."""
        step = run_block(self.text, GUARD_STEP)
        folder = Path(tempfile.mkdtemp())
        try:
            log = folder / "execution.json"
            log.write_text(json.dumps([{"type": "system", "subtype": "init"},
                                       {"type": "result", "subtype": "success", "permission_denials": [
                                           {"tool_name": "Bash", "tool_input": {"command": "cat intents/x.md"}}]}]))
            env = {"BEFORE": "none", "GH_ANSWER": "2026-11-09T10:05:00Z", "PR_NUMBER": "7",
                   "GITHUB_REPOSITORY": "owner/name", "EXECUTION_FILE": str(log)}
            code, out = run_shell(step, folder, env)
            self.assertEqual(code, 0, out)
            self.assertIn('denied: Bash {"command":"cat intents/x.md"}', out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_prompt_names_the_tools_and_the_posting_command(self):
        """intent-reviewer, check 5 (#70)."""
        for name, text in (("this workflow", self.text), ("the template", self.template)):
            with self.subTest(file=name):
                prompt = re.search(r"prompt: \|\n((?:            .*\n)+)", text)
                self.assertIsNotNone(prompt, "no prompt")
                for part in ("Read files with the Read tool", "A denied command is no reason to stop",
                             "ends only after it is posted or updated",
                             'gh pr comment ${{ github.event.pull_request.number }} --body "<the report>"',
                             "gh api -X PATCH repos/${{ github.repository }}/issues/comments/<id>"):
                    self.assertIn(part, prompt.group(1))


class Verdict(unittest.TestCase):
    text = (WORKFLOWS / "verdict.yml").read_text()

    def test_runs_after_the_tests_and_after_the_reviewer_and_counts_the_rounds(self):
        """review-loop, check 4."""
        self.assertIn("workflows: [tests, review-intents]", self.text)
        self.assertIn("--review-workflow review-intents.yml", self.text)
        self.assertIn("concurrency:\n  group: verdict-", self.text)
        self.assertIn("--schema change/charter/schema/contract.toml all change/charter.toml", self.text)


if __name__ == "__main__":
    unittest.main()
