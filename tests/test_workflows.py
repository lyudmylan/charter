"""Tests of the workflow files, read as text: the standard library has no YAML parser.
Run: python3 -m unittest discover -s tests"""

import contextlib
import io
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
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_check as cc  # noqa: E402
import charter_setup as cs  # noqa: E402

WORKFLOWS = ROOT / ".github" / "workflows"
TEMPLATES = ROOT / "charter" / "templates"
BEFORE_STEP, GUARD_STEP = "Note the report before the review", "The run fails when the reviewer posted no report"
NO_REPORT = "the reviewer posted no report"
MARKER = "<!-- charter-intent-review -->"
HEAD, OTHER = "1111111111111111111111111111111111111111", "2222222222222222222222222222222222222222"
HEAD_SHA = "${{ github.event.pull_request.head.sha }}"
READ_ONLY = {"Read", "Glob", "Grep"}
# A command that only reads or only posts the one comment.
ALLOWED_COMMANDS = re.compile(
    r"^Bash\((git diff|git log|gh issue view|gh issue list|gh pr view|gh pr comment):\*\)$|"
    r"^Bash\(gh api repos/\$\{\{ github\.repository \}\}/issues/\*/comments\*\)$"
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


def answer(count: int, commit: str | None = HEAD) -> str:
    """The answer of the code host to the last step: the number of the reports, then the newest report."""
    if not count:
        return "0\n"
    return f"{count}\n{MARKER}\nCommit: {commit}\n\n| intent | verdict |\nHighest open severity: low\n"


def guard_env(before: str, gh_answer: str) -> dict[str, str]:
    return {"BEFORE": before, "GH_ANSWER": gh_answer, "PR_NUMBER": "7", "GITHUB_REPOSITORY": "owner/name",
            "HEAD_SHA": HEAD, "EXECUTION_FILE": ""}


def prompt_of(text: str) -> str:
    return re.search(r"prompt: \|\n((?:            .*\n)+)", text).group(1)


class ReviewIntents(unittest.TestCase):
    text = (WORKFLOWS / "review-intents.yml").read_text()
    template = (TEMPLATES / "review-intents.yml").read_text()

    def test_paths_and_tools(self):
        """intent-reviewer, check 1."""
        self.assertIn('paths: ["intents/**", "plans/**"]', self.text)
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
        """intent-reviewer, check 4 (#70): the run fails when no new report was posted, and passes when one was
        (review-rounds: each report is a new comment, so the step compares the number of the reports). The two
        steps have the same text in the template and in this workflow, and they stand before and after the reviewer."""
        step = run_block(self.text, GUARD_STEP)
        self.assertEqual(step, run_block(self.template, GUARD_STEP))
        self.assertEqual(run_block(self.text, BEFORE_STEP), run_block(self.template, BEFORE_STEP))
        for text in (self.text, self.template):
            self.assertLess(text.index(BEFORE_STEP), text.index("anthropics/claude-code-action"))
            self.assertLess(text.index("anthropics/claude-code-action"), text.index(GUARD_STEP))
            self.assertIn(f"      - name: {GUARD_STEP}\n        if: always()\n", text)
        folder = Path(tempfile.mkdtemp())
        try:
            for before, after, passes in (("0", 0, False), ("1", 1, False), ("0", 1, True), ("1", 2, True)):
                with self.subTest(before=before, after=after):
                    code, out = run_shell(step, folder, guard_env(before, answer(after)))
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
            env = {**guard_env("0", answer(1)), "EXECUTION_FILE": str(log)}
            code, out = run_shell(step, folder, env)
            self.assertEqual(code, 0, out)
            self.assertIn('denied: Bash {"command":"cat intents/x.md"}', out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_prompt_names_the_tools_and_the_posting_command(self):
        """intent-reviewer, check 5 (#70). Since review-rounds (#61) the reviewer posts and updates no comment."""
        for name, text in (("this workflow", self.text), ("the template", self.template)):
            with self.subTest(file=name):
                prompt = re.search(r"prompt: \|\n((?:            .*\n)+)", text)
                self.assertIsNotNone(prompt, "no prompt")
                for part in ("Read files with the Read tool", "A denied command is no reason to stop",
                             "ends only after it is posted",
                             "gh pr comment ${{ github.event.pull_request.number }} --body-file - <<'REPORT'"):
                    self.assertIn(part, prompt.group(1))


class ReviewRounds(unittest.TestCase):
    files = {"this workflow": (WORKFLOWS / "review-intents.yml").read_text(),
             "the template": (TEMPLATES / "review-intents.yml").read_text()}

    def test_the_reviewer_posts_a_new_comment_and_updates_none(self):
        """review-rounds, check 6."""
        for name, text in self.files.items():
            with self.subTest(file=name):
                prompt = " ".join(prompt_of(text).split())
                self.assertIn("The report is a new comment on change request", prompt)
                self.assertIn("at each run", prompt)
                self.assertIn("Change no earlier comment", prompt)
                self.assertNotIn("PATCH", text)
                tools = re.search(r'--allowedTools "([^"]+)"', text).group(1)
                self.assertIn("Bash(gh pr comment:*)", tools.split(","))
                self.assertFalse([tool for tool in tools.split(",") if "-X" in tool], tools)

    def test_the_run_fails_when_no_report_was_added(self):
        """review-rounds, check 6: the last step, run with `bash -e` and a fake of the code host."""
        step = run_block(self.files["this workflow"], GUARD_STEP)
        self.assertEqual(step, run_block(self.files["the template"], GUARD_STEP))
        before = run_block(self.files["this workflow"], BEFORE_STEP)
        self.assertEqual(before, run_block(self.files["the template"], BEFORE_STEP))
        self.assertIn("| length", before)
        self.assertIn("reports=$REPORTS", before)
        folder = Path(tempfile.mkdtemp())
        try:
            cases = (("2", answer(2), False), ("0", answer(0), False), ("", answer(0), False), ("3", answer(2), False),
                     ("1", "not a number", False), ("2", answer(3), True), ("", answer(1), True))
            for before_count, gh_answer, passes in cases:
                with self.subTest(before=before_count, answer=gh_answer.splitlines()[0]):
                    code, out = run_shell(step, folder, guard_env(before_count, gh_answer))
                    self.assertEqual(code == 0, passes, out)
                    self.assertEqual(NO_REPORT in out, not passes, out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class ReviewerDiff(unittest.TestCase):
    files = ReviewRounds.files

    def test_the_report_names_its_commit(self):
        """reviewer-reads-the-diff-of-a-round, check 1: the head commit comes to the reviewer in the prompt, and to
        the last step through `env:`, never into the text of the script."""
        for name, text in self.files.items():
            with self.subTest(file=name):
                prompt = " ".join(prompt_of(text).split())
                self.assertIn(f"The head commit is {HEAD_SHA}.", prompt)
                self.assertIn(f"The report holds one line `Commit: {HEAD_SHA}`.", prompt)
                self.assertIn(f"          HEAD_SHA: {HEAD_SHA}\n", text)
                self.assertNotIn("${{", run_block(text, GUARD_STEP))
        skill = " ".join((ROOT / "charter-practices" / "skills" / "intent-review" / "SKILL.md").read_text().split())
        self.assertIn("`Commit: <the full identifier of the head commit>`", skill)

    def test_the_run_fails_when_the_report_names_another_commit(self):
        """reviewer-reads-the-diff-of-a-round, check 2: the last step, run with `bash -e` and a fake of the code host."""
        step = run_block(self.files["this workflow"], GUARD_STEP)
        folder = Path(tempfile.mkdtemp())
        try:
            wrong = (answer(2, OTHER), answer(2, None), answer(2, HEAD[:12]),
                     f"2\n{MARKER}\nThe report covers Commit: {HEAD}\n")
            for gh_answer in wrong:
                with self.subTest(answer=gh_answer):
                    code, out = run_shell(step, folder, guard_env("1", gh_answer))
                    self.assertEqual(code, 1, out)
                    self.assertIn(f"Commit: {HEAD}", out)
                    self.assertNotIn(NO_REPORT, out)
            code, out = run_shell(step, folder, guard_env("1", answer(2, HEAD)))
            self.assertEqual(code, 0, out)
            self.assertIn(HEAD, out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_a_later_round_starts_from_the_diff(self):
        """reviewer-reads-the-diff-of-a-round, check 3."""
        for name, text in self.files.items():
            with self.subTest(file=name):
                prompt = " ".join(prompt_of(text).split())
                for part in ("When the change request has a report already, read the line `Commit:` of the newest report",
                             "`git diff <that commit>..${{ github.event.pull_request.head.sha }} -- intents/ plans/`",
                             'write the section "Changed since the last report"',
                             "start the findings of this round from that diff"):
                    self.assertIn(part, prompt)
                tools = re.search(r'--allowedTools "([^"]+)"', text).group(1).split(",")
                self.assertIn("Bash(git diff:*)", tools)


class PlanPlace(unittest.TestCase):
    def test_the_reviewer_runs_on_a_change_of_a_plan(self):
        """plan-tier, check 5: in the template and in this repo."""
        for name, path in (("this workflow", WORKFLOWS), ("the template", TEMPLATES)):
            with self.subTest(file=name):
                text = (path / "review-intents.yml").read_text()
                self.assertIn('paths: ["intents/**", "plans/**"]', text)
                prompt = re.search(r"prompt: \|\n((?:            .*\n)+)", text).group(1)
                self.assertIn("git diff --name-only origin/${{ github.base_ref }}...HEAD -- intents/ plans/", prompt)


class Verdict(unittest.TestCase):
    text = (WORKFLOWS / "verdict.yml").read_text()

    def test_runs_after_the_tests_and_after_the_reviewer_and_counts_the_rounds(self):
        """review-loop, check 4."""
        started_by = re.search(r"^    workflows: \[(.*)\]$", self.text, re.M).group(1).split(", ")
        self.assertEqual(started_by[:2], ["tests", "review-intents"])
        self.assertIn("--review-workflow review-intents.yml", self.text)
        self.assertIn("concurrency:\n  group: verdict-", self.text)
        self.assertIn("--schema change/charter/schema/contract.toml all change/charter.toml", self.text)


CODE_MARKER = "<!-- charter-code-review -->"
CODE_SECRETS = {"GITHUB_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN"}   # the two secrets of review-intents.yml
# A command of a step that would run the code of the change request: an install, a test, or a build.
RUNS_CODE = re.compile(r"\b(pip|npm|yarn|pnpm|make|pytest|unittest|tox|cargo|go|mvn|gradle|bundle|setup\.py)\b|\./|python3? -m\b|\bsh |\bbash ")


def steps_with_run(text: str) -> dict[str, str]:
    """Each named step of a workflow that has a `run: |` script, with the script."""
    steps = {}
    for name in re.findall(r"^      - name: (.*)$", text, re.M):
        body = text.split(f"      - name: {name}\n", 1)[1].split("\n      - ", 1)[0]
        if "\n        run: |" in "\n" + body:
            steps[name] = run_block(text, name)
    return steps


def triggers(patterns: list[str], files: list[str]) -> bool:
    """Whether a change of the files starts a workflow with these `paths`, as the code host reads them: for each
    file the last pattern that matches decides, and a pattern with `!` in front excludes."""
    started = False
    for path in files:
        included = False
        for pattern in patterns:
            if cc.matches(path, [pattern.lstrip("!")]):
                included = not pattern.startswith("!")
        started = started or included
    return started


class CodeReviewer(unittest.TestCase):
    text = (WORKFLOWS / "review-code.yml").read_text()
    template = (TEMPLATES / "review-code.yml").read_text()
    files = {"this workflow": text, "the template": template}

    def test_the_setup_writes_the_workflow(self):
        """code-reviewer, check 1."""
        folder = Path(tempfile.mkdtemp())
        try:
            flags = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
                     "--leader", "alice", "--target", str(folder)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cs.main(flags), 0)
            self.assertEqual(cs.WRITTEN["review-code.yml"], ".github/workflows/review-code.yml")
            written = (folder / cs.WORKFLOWS / "review-code.yml").read_text()
            self.assertEqual(written, self.template.replace("%{charter_address}", cs.CHARTER_ADDRESS))
            self.assertNotIn("%{", written)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_depth_comes_from_the_base_contract(self):
        """code-reviewer, check 16: a change request that edits its own tiers gets the depth of the base. The
        step runs in a git repo whose base says `deep` for `scripts/**` and whose head says `light`."""
        base = (ROOT / "tests" / "samples" / "repo.toml").read_text()
        self.assertIn('review = "deep"', base)
        for name, text in self.files.items():
            with self.subTest(file=name):
                folder = Path(tempfile.mkdtemp()).resolve()
                try:
                    repo, runner, output = folder / "repo", folder / "runner", folder / "output"
                    repo.mkdir()
                    runner.mkdir()
                    (runner / "charter").symlink_to(ROOT)       # the scripts of Charter, as the step before leaves them
                    git = ["git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@example.invalid"]
                    subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
                    (repo / "charter.toml").write_text(base)
                    subprocess.run([*git, "add", "-A"], check=True)
                    subprocess.run([*git, "commit", "-q", "-m", "base"], check=True)
                    subprocess.run([*git, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
                    (repo / "charter.toml").write_text(base.replace('review = "deep"', 'review = "light"'))
                    (repo / "scripts").mkdir()
                    (repo / "scripts" / "x.py").write_text("pass\n")
                    subprocess.run([*git, "add", "-A"], check=True)
                    subprocess.run([*git, "commit", "-q", "-m", "head"], check=True)
                    env = {**os.environ, "BASE_REF": "main", "RUNNER_TEMP": str(runner), "GITHUB_OUTPUT": str(output)}
                    done = subprocess.run(["bash", "-e", "-c", run_block(text, "Read the tier of the change and the depth of its review")],
                                          cwd=repo, env=env, capture_output=True, text=True)
                    self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                    self.assertEqual(output.read_text().splitlines(), ["tier=high", "depth=deep"])
                finally:
                    shutil.rmtree(folder, ignore_errors=True)

    def test_the_workflow_runs_on_code_and_not_on_intents_alone(self):
        """code-reviewer, check 1: the trigger, read as the code host reads it, and no review for a fork."""
        for name, text in self.files.items():
            with self.subTest(file=name):
                self.assertIn("on:\n  pull_request:\n", text)
                self.assertNotIn("pull_request_target", text)
                self.assertIn("    if: github.event.pull_request.head.repo.full_name == github.repository\n", text)
                patterns = json.loads(re.search(r"^    paths: (\[.*\])$", text, re.M).group(1))
                for files, starts in ((["src/app.py"], True), (["intents/a.md", "src/app.py"], True), ([".github/x.yml"], True),
                                      (["README.md"], True), (["plans/a.md", "charter.toml"], True), (["intents/a.md"], False),
                                      (["intents/a.md", "plans/a.md"], False), (["plans/sub/a.md"], False)):
                    with self.subTest(files=files):
                        self.assertEqual(triggers(patterns, files), starts, patterns)

    def test_the_reviewer_reads_and_posts_and_runs_no_code(self):
        """code-reviewer, check 1: the allowed tools read files and post one comment; no step runs the code of
        the change request; a value of the code host comes to a script through `env:`; two secrets only."""
        for name, text in self.files.items():
            with self.subTest(file=name):
                tools = re.search(r'--allowedTools "([^"]+)"', text).group(1).split(",")
                for tool in tools:
                    self.assertTrue(tool in READ_ONLY or ALLOWED_COMMANDS.match(tool), f"tool not read-only or comment: {tool}")
                self.assertIn("Bash(gh pr comment:*)", tools)
                self.assertIn("contents: read", text)
                self.assertNotIn("PATCH", text)
                self.assertEqual(set(re.findall(r"secrets\.(\w+)", text)), CODE_SECRETS)
                steps = steps_with_run(text)
                self.assertGreaterEqual(len(steps), 3, list(steps))
                for step, script in steps.items():
                    with self.subTest(step=step):
                        self.assertNotIn("${{", script)
                        self.assertIsNone(RUNS_CODE.search(script), script)
                        for call in re.findall(r"python3 (\S+)", script):
                            self.assertTrue(call == "-c" or call.startswith('"$RUNNER_TEMP/charter/'), call)
                prompt = " ".join(prompt_of(text).split())
                self.assertIn("Run no code of the change request: no install, no test, no build.", prompt)
                self.assertIn("change-review/SKILL.md exactly", prompt)
                self.assertIn("the depth of the review is ${{ steps.tier.outputs.depth }}", prompt)

    def test_the_run_fails_without_a_new_report_of_the_head_commit(self):
        """code-reviewer, check 2: the last step, run with `bash -e` and a fake of the code host."""
        step = run_block(self.text, GUARD_STEP)
        self.assertEqual(step, run_block(self.template, GUARD_STEP))
        self.assertEqual(step, run_block((WORKFLOWS / "review-intents.yml").read_text(), GUARD_STEP).replace(MARKER, CODE_MARKER))
        before = run_block(self.text, BEFORE_STEP)
        self.assertIn(CODE_MARKER, before)
        self.assertIn(CODE_MARKER, step)
        self.assertNotIn(MARKER, step + before)
        for text in (self.text, self.template):
            self.assertLess(text.index(BEFORE_STEP), text.index("anthropics/claude-code-action"))
            self.assertLess(text.index("anthropics/claude-code-action"), text.index(GUARD_STEP))
            self.assertIn(f"      - name: {GUARD_STEP}\n        if: always()\n", text)

        def report(count: int, commit: str | None) -> str:
            return f"{count}\n{CODE_MARKER}\nCommit: {commit}\n\n| item | finding |\nHighest open severity: low\n"

        folder = Path(tempfile.mkdtemp())
        try:
            cases = (("1", report(1, HEAD), False, True), ("0", "0\n", False, True), ("", "0\n", False, True),
                     ("1", report(2, OTHER), False, False), ("1", report(2, None), False, False),
                     ("1", report(2, HEAD[:12]), False, False), ("1", report(2, HEAD), True, False), ("", report(1, HEAD), True, False))
            for before_count, gh_answer, passes, no_report in cases:
                with self.subTest(before=before_count, answer=gh_answer):
                    code, out = run_shell(step, folder, guard_env(before_count, gh_answer))
                    self.assertEqual(code == 0, passes, out)
                    self.assertEqual(NO_REPORT in out, no_report, out)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_the_workflow_of_this_repo_follows_the_template(self):
        """code-reviewer, check 3: the two files differ only in the place of the skill and in the way to the
        scripts of Charter, which this repo takes from its base branch."""
        fetch = ("      - name: Fetch Charter at the version of the contract\n"
                 "        run: |\n"
                 "          VERSION=$(python3 -c 'import tomllib; print(tomllib.load(open(\"charter.toml\", \"rb\"))[\"charter\"][\"version\"])')\n"
                 "          git clone --quiet --depth 1 --branch \"charter--v$VERSION\" %{charter_address} \"$RUNNER_TEMP/charter\"\n")
        base = ("      - name: Take the scripts of Charter from the base branch\n"
                "        env:\n"
                "          BASE_REF: ${{ github.base_ref }}\n"
                "        run: |\n"
                "          git worktree add --quiet --detach \"$RUNNER_TEMP/charter\" \"origin/$BASE_REF\"\n")
        header = ("# The skill and the scripts come from Charter, fetched at the version that the contract names.\n",
                  "# The skill comes from the change request, and the scripts from the base branch: the run executes no script of the change.\n")
        skill = ("Follow ${{ runner.temp }}/charter/charter-practices/skills/change-review/SKILL.md",
                 "Follow charter-practices/skills/change-review/SKILL.md")
        expected = self.template
        for old, new in ((fetch, base), header, skill):
            self.assertEqual(expected.count(old), 1, old)
            expected = expected.replace(old, new)
        self.assertEqual(self.text, expected)
        self.assertTrue((ROOT / "charter-practices" / "skills" / "change-review" / "SKILL.md").is_file())
        self.assertNotIn("%{", self.text)

    def test_the_verdict_runs_after_the_code_review(self):
        """code-reviewer, check 11: the template and this repo."""
        for name, path in (("this workflow", WORKFLOWS), ("the template", TEMPLATES)):
            with self.subTest(file=name):
                text = (path / "verdict.yml").read_text()
                started_by = re.search(r"^    workflows: \[(.*)\]$", text, re.M).group(1).split(", ")
                self.assertEqual(set(started_by), {"tests", "review-intents", "review-code"})
                self.assertIn("          --code-review-workflow review-code.yml\n", text)
                self.assertIn("          --review-workflow review-intents.yml\n", text)


if __name__ == "__main__":
    unittest.main()
