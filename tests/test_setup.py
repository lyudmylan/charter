"""Tests of the setup step. Run: python3 -m unittest discover -s tests

Each test names the intent and the check that it implements, in its docstring.
"""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_check as cc  # noqa: E402
import charter_setup as cs  # noqa: E402

ORG = ROOT / "tests" / "samples" / "organization.toml"
FLAGS = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
         "--leader", "alice", "--quality", "python3 -m unittest discover -s tests"]
PHASES = ("plan", "design", "build", "test", "deploy", "maintain")
PUBLISH_STEP = 'Publish the check "verdict" on the change request'


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cs.main(list(argv))
    return code, out.getvalue()


def run_block(workflow: str, step: str) -> str:
    """The `run:` script of the named step of a workflow. The file is read as text: the standard library
    has no YAML parser."""
    lines = workflow.splitlines()
    start = lines.index(f"      - name: {step}")
    first = next(i for i in range(start + 1, len(lines)) if lines[i] == "        run: |")
    script = []
    for line in lines[first + 1:]:
        if line and not line.startswith("          "):
            break
        script.append(line[10:])
    return "\n".join(script) + "\n"


def run_step(script: str, folder: Path, env: dict[str, str], files: dict[str, str]) -> tuple[int, str]:
    """Runs the script of a step with `bash -e`, as the host does, in `folder` with `files` in it and a `gh`
    on the path that records its arguments. Returns the exit code and the recorded arguments, one per line."""
    (folder / "bin").mkdir(parents=True)
    gh = folder / "bin" / "gh"
    gh.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$GH_CALL"\n')
    gh.chmod(0o755)
    for name, text in files.items():
        (folder / name).write_text(text)
    call = folder / "gh-call.txt"
    result = subprocess.run(["bash", "-e", "-c", script], cwd=folder, capture_output=True, text=True,
                            env={**env, "PATH": f"{folder / 'bin'}:{os.environ['PATH']}", "GH_CALL": str(call)})
    return result.returncode, call.read_text() if call.exists() else ""


class Temp(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def setup(self, *more: str) -> tuple[int, str]:
        return run(*FLAGS, "--target", str(self.dir), *more)


class Setup(Temp):
    def test_writes_a_valid_repo(self):
        """setup-step, check 1."""
        code, out = self.setup()
        self.assertEqual(code, cc.PASS, out)
        for written in list(cs.WRITTEN.values()) + list(cs.WRITTEN_IF_MISSING.values()):
            self.assertTrue((self.dir / written).is_file(), written)
        contract = self.dir / cs.CONTRACT_FILE
        code, out = io.StringIO(), None
        with contextlib.redirect_stdout(code):
            result = cc.main([cc.CMD_ALL, str(contract), f"--{cc.ARG_SOURCE}", str(ORG)])
        self.assertEqual(result, cc.PASS, code.getvalue())
        data = tomllib.loads(contract.read_text())
        manifest = json.loads(cs.MANIFEST.read_text())
        self.assertEqual(data["charter"]["version"], manifest["version"])
        self.assertEqual(data["roles"]["team_lead"], ["alice"])
        self.assertNotIn("README.md", data["documents"]["text_checked"])     # no README in the folder

    def test_refuses_to_overwrite(self):
        """setup-step, check 2."""
        (self.dir / cs.INSTRUCTIONS_FILE).write_text("mine\n")
        code, out = self.setup()
        self.assertEqual(code, cc.FAIL)
        self.assertIn(f"the file exists: {cs.INSTRUCTIONS_FILE}", out)
        self.assertFalse((self.dir / cs.CONTRACT_FILE).exists(), "nothing is written when one file exists")
        self.assertEqual((self.dir / cs.INSTRUCTIONS_FILE).read_text(), "mine\n")

    def test_keeps_the_documents_that_exist(self):
        """setup-step, check 2: the two documents are written only when missing."""
        (self.dir / "docs").mkdir()
        (self.dir / cs.PRODUCT_FILE).write_text("# Mine\n")
        code, out = self.setup()
        self.assertEqual(code, cc.PASS, out)
        self.assertEqual((self.dir / cs.PRODUCT_FILE).read_text(), "# Mine\n")
        self.assertIn(f"kept: {cs.PRODUCT_FILE}", out)

    def test_prints_the_manual_steps(self):
        """setup-step, check 3."""
        (self.dir / cs.CLAUDE_FILE).write_text("# project\n")
        code, out = run("--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
                        "--leader", "alice", "--target", str(self.dir))
        self.assertEqual(code, cc.PASS, out)
        for step in ("CHARTER_ORG_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", 'the check "verdict" is required',
                     "git clone https://example.com/org/rules", "checks.quality",
                     f"Add the line `@{cs.INSTRUCTIONS_FILE}` to {cs.CLAUDE_FILE}", f"first intent from {cs.INTENT_TEMPLATE}"):
            self.assertIn(step, out)

    def test_a_quote_in_a_value_cannot_break_the_contract(self):
        """setup-step, check 1: every text value is a TOML string."""
        code, out = run("--repo", 'a"b', "--source", "https://example.com/org/rules", "--source-version", "v1",
                        "--leader", "alice", "--target", str(self.dir))
        self.assertEqual(code, cc.PASS, out)
        self.assertEqual(tomllib.loads((self.dir / cs.CONTRACT_FILE).read_text())["repo"]["name"], 'a"b')

    def test_a_missing_value_is_named(self):
        """setup-step, check 2: without a terminal, a missing flag is refused by name."""
        code, out = run("--repo", "sample", "--target", str(self.dir))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("no value for --source", out)


class Templates(Temp):
    def test_workflow_templates_fetch_charter_at_the_version(self):
        """charter-version-in-ci, check 2."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for name in ("tests.yml", "verdict.yml", "review-intents.yml", "review-code.yml", "run.yml"):
            text = (self.dir / cs.WORKFLOWS / name).read_text()
            with self.subTest(workflow=name):
                self.assertIn('tomllib.load(open("charter.toml", "rb"))["charter"]["version"]', text)
                self.assertIn('--branch "charter--v$VERSION"', text)
                self.assertIn(cs.CHARTER_ADDRESS, text)
                self.assertNotIn("%{", text)
        verdict = (self.dir / cs.WORKFLOWS / "verdict.yml").read_text()
        self.assertIn('"$CHARTER_SCRIPTS/charter_gate.py" verdict', verdict)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", verdict)

    def test_no_runner_context_in_a_job_env(self):
        """setup-step, check 6 (#58): GitHub refuses the `runner` context in a job-level env; the file then
        does not parse, and the run has no job and no log."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for name in ("tests.yml", "verdict.yml", "review-intents.yml", "review-code.yml", "run.yml"):
            text = (self.dir / cs.WORKFLOWS / name).read_text()
            with self.subTest(workflow=name):
                self.assertIsNone(re.search(r"^    env:\n(?:      .*\n)*?      \w+: \$\{\{ runner\.", text, re.M),
                                  "a job-level env uses the runner context")
                self.assertIn('>> "$GITHUB_ENV"', text) if name not in ("review-intents.yml", "review-code.yml") else None

    def test_verdict_template_declares_actions_read(self):
        """setup-step, check 7 (#63): the facts step lists the runs of the review workflow to count the
        rounds; a private repo serves that listing only with `actions: read`, a public repo without it. The
        template and the workflow of this repo stay identical, so both are read."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for name, path in (("the written verdict.yml", self.dir / cs.WORKFLOWS / "verdict.yml"),
                           ("the verdict.yml of this repo", ROOT / ".github" / "workflows" / "verdict.yml")):
            with self.subTest(file=name):
                block = re.search(r"^permissions:\n((?:  [\w-]+: \w+.*\n)+)", path.read_text(), re.M)
                self.assertIsNotNone(block, f"{name} has no permissions block")
                self.assertRegex(block.group(1), r"(?m)^  actions: read\b", f"{name} lacks actions: read")

    def test_the_check_is_published_when_the_verdict_could_not_run(self):
        """setup-step, check 8 (#68): the step runs under the `-e` shell of the host, and a read of the
        missing `verdict.txt` ended it before the fallback title; the change request then showed no check.
        The step runs here as the host runs it, with a `gh` that records its one call."""
        self.assertEqual(self.setup()[0], cc.PASS)
        written = (self.dir / cs.WORKFLOWS / "verdict.yml").read_text()
        step = run_block(written, PUBLISH_STEP)
        self.assertEqual(step, run_block((ROOT / ".github" / "workflows" / "verdict.yml").read_text(), PUBLISH_STEP),
                         "the template and the verdict.yml of this repo differ in the step")
        self.assertIn("PR_SHA: ${{ steps.pr.outputs.sha || github.event.workflow_run.head_sha }}", written)
        cases = (
            ("no-verdict", "", {}, False, ("conclusion=failure", "output[title]=the verdict could not run")),
            ("ready", "0", {"verdict.txt": "ready\nlink: the change request links the open issue 1\n"}, True,
             ("conclusion=success", "output[title]=ready")),
        )
        for name, code, files, passes, expected in cases:
            with self.subTest(case=name):
                env = {"VERDICT_CODE": code, "PR_SHA": "0123abc", "GITHUB_REPOSITORY": "owner/name"}
                exit_code, call = run_step(step, self.dir / name, env, files)
                self.assertEqual(exit_code == 0, passes, call)
                for part in expected:
                    self.assertIn(part, call.splitlines())

    def test_lifecycle_map_has_the_six_phases(self):
        """default-lifecycle-map, check 1: six phases, the tracker skill in Plan, the document points to the template."""
        self.assertEqual(self.setup()[0], cc.PASS)
        data = tomllib.loads((self.dir / cs.CONTRACT_FILE).read_text())
        self.assertEqual(tuple(data["lifecycle"]), PHASES)
        for phase in PHASES:
            self.assertIn("work", data["lifecycle"][phase])
            self.assertIn("builtin", data["lifecycle"][phase])
        self.assertIn("skill tracker", data["lifecycle"]["plan"]["work"])
        own = tomllib.loads((ROOT / "charter.toml").read_text())
        self.assertEqual(tuple(own["lifecycle"]), PHASES, "this repo follows its own map")
        self.assertIn("charter/templates/charter.toml", (ROOT / "docs" / "contract.md").read_text())

    def test_no_placeholder_survives(self):
        """setup-step, check 1: every written file is complete."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for written in list(cs.WRITTEN.values()) + list(cs.WRITTEN_IF_MISSING.values()):
            self.assertNotIn("%{", (self.dir / written).read_text(), written)


class DecisionFiles(Temp):
    DEFAULT = ["docs/adr/**", "doc/adr/**", "doc/arch/adr-*.md", "docs/decisions/**"]
    COLUMN = "| Part | What it does, and why it is built this way | Where | Since |"
    RULE = "No separate file holds one decision; a choice that must always hold becomes a check. [documents.absent]"

    def check_all(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cc.main([cc.CMD_ALL, str(self.dir / cs.CONTRACT_FILE), f"--{cc.ARG_SOURCE}", str(ORG)])
        return code, out.getvalue()

    def test_the_new_contract_carries_the_default_patterns(self):
        """reason-next-to-the-part, check 4."""
        self.assertEqual(self.setup()[0], cc.PASS)
        data = tomllib.loads((self.dir / cs.CONTRACT_FILE).read_text())
        self.assertEqual(data["documents"]["absent"], self.DEFAULT)
        self.assertEqual(self.check_all()[0], cc.PASS)

    def test_a_decision_file_fails_the_check_of_a_new_repo(self):
        """reason-next-to-the-part, check 4: one file under each of the four default patterns, one at a time."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for name in ("docs/adr/adr-001-store.md", "doc/adr/0001-store.md", "doc/arch/adr-001.md",
                     "docs/decisions/0001-store.md"):
            with self.subTest(file=name):
                path = self.dir / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# A decision\n")
                code, out = self.check_all()
                self.assertEqual(code, cc.FAIL, out)
                self.assertIn(f"fail: {name}: the contract forbids this path", out)
                path.unlink()
                self.assertEqual(self.check_all()[0], cc.PASS)

    def test_the_architecture_template_holds_the_choice_at_the_part(self):
        """reason-next-to-the-part, check 5."""
        self.assertEqual(self.setup()[0], cc.PASS)
        text = (self.dir / "docs" / "architecture.md").read_text()
        self.assertIn(self.COLUMN, text)
        self.assertEqual(re.findall(r"^## (.*)$", text, re.M), ["Parts"])
        self.assertNotIn("Decisions", text)
        self.assertNotIn("What runs on a change request", text)

    def test_the_instructions_carry_the_rule(self):
        """reason-next-to-the-part, check 6: the template that the setup step writes, and this repo."""
        self.assertEqual(self.setup()[0], cc.PASS)
        for path in (self.dir / cs.INSTRUCTIONS_FILE, ROOT / cs.INSTRUCTIONS_FILE):
            with self.subTest(file=str(path)):
                self.assertIn(self.RULE, " ".join(path.read_text().split()))
        data = tomllib.loads((ROOT / cs.CONTRACT_FILE).read_text())
        self.assertEqual(data["documents"]["absent"], self.DEFAULT)

    def test_both_manifests_name_the_version(self):
        """reason-next-to-the-part, check 9: 0.3.5 carries the check; a later version carries it too."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 5))

    def test_the_design_row_of_the_product_document_names_the_choice(self):
        """reason-next-to-the-part, check 10."""
        row = re.search(r"^\| Design \| (.*?) \|", (ROOT / "docs" / "product.md").read_text(), re.M)
        self.assertIsNotNone(row, "no Design row")
        self.assertIn("with each choice and its reason at the part", row.group(1))


class Commands(unittest.TestCase):
    def test_the_four_commands_exist_and_the_manifests_agree(self):
        """setup-step, check 5."""
        for name in ("charter-setup", "charter-check", "charter-gate", "charter-facts-github", "charter-run"):
            path = ROOT / "charter" / "bin" / name
            with self.subTest(command=name):
                self.assertTrue(path.is_file(), name)
                self.assertTrue(path.stat().st_mode & 0o111, f"{name} is not executable")
                self.assertIn(f"scripts/{name.replace('-', '_')}.py", path.read_text())
        core = json.loads(cs.MANIFEST.read_text())["version"]
        practices = json.loads((ROOT / "charter-practices" / ".claude-plugin" / "plugin.json").read_text())["version"]
        self.assertEqual(core, practices)


class PlanPlace(Temp):
    def test_the_setup_writes_the_template_of_a_plan(self):
        """plan-tier, check 4."""
        code, out = self.setup()
        self.assertEqual(code, cc.PASS, out)
        text = (self.dir / cs.PLAN_TEMPLATE).read_text()
        self.assertEqual(cs.PLAN_TEMPLATE, "plans/_template.md")
        for heading in ("## Steps", "## Files", "## Tests"):
            self.assertIn(heading, text)
        self.assertIn("Intent: `intents/", text)
        high = tomllib.loads((self.dir / cs.CONTRACT_FILE).read_text())["tiers"]["high"]["paths"]
        for path in ("plans/app.md", "plans/sub/app.md", cs.PLAN_TEMPLATE):
            with self.subTest(path=path):
                self.assertFalse(cc.matches(path, high), high)

    def test_the_instructions_and_the_documents_name_the_new_place(self):
        """plan-tier, check 7: the instruction template, the instructions of this repo, the skill `tracker`,
        and the document of the contract, which also holds the command of the move."""
        files = (ROOT / "charter" / "templates" / cs.INSTRUCTIONS_FILE, ROOT / cs.INSTRUCTIONS_FILE,
                 ROOT / "charter-practices" / "skills" / "tracker" / "SKILL.md", ROOT / "docs" / "contract.md")
        for path in files:
            with self.subTest(file=path.name):
                text = path.read_text()
                self.assertIn("plan `plans/<part>.md`", " ".join(text.split()))
                self.assertNotIn("plan `intents/<part>.plan.md`", " ".join(text.split()))
        contract = (ROOT / "docs" / "contract.md").read_text()
        self.assertIn("git mv intents/<part>.plan.md plans/<part>.md", contract)


class ReviewRounds(unittest.TestCase):
    def test_the_intent_template_names_no_language(self):
        """review-rounds, check 8: the test line of the intent template names no file of one language."""
        text = (ROOT / "charter" / "templates" / "intent.md").read_text()
        test_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("test:")]
        self.assertEqual(test_lines, ["test: <the file of the test, and the name of the test in it>"])
        for language in (".py", ".ts", ".js", ".go", ".rb", "::"):
            with self.subTest(language=language):
                self.assertNotIn(language, " ".join(test_lines))


class CodeReviewer(unittest.TestCase):
    def test_the_instructions_and_the_product_document_name_the_reviewer(self):
        """code-reviewer, check 12: the instruction template and the instructions of this repo name the reviewer of
        the code with its rule, and the Test row of the lifecycle map names it."""
        for path in (ROOT / "charter" / "templates" / cs.INSTRUCTIONS_FILE, ROOT / cs.INSTRUCTIONS_FILE):
            with self.subTest(file=str(path.relative_to(ROOT))):
                section = " ".join(path.read_text().split("## Review and limits", 1)[1].split())
                self.assertIn("The reviewer of the code, the workflow `review-code`", section)
                self.assertIn("with the skill `change-review`", section)
                self.assertIn("[review.code_blocks]", section)
        row = re.search(r"^\| Test \| (.*)$", (ROOT / "docs" / "product.md").read_text(), re.M)
        self.assertIsNotNone(row, "no Test row")
        self.assertIn("An agent that is not the author reviews the code.", row.group(1))
        for name in ("charter.toml", "charter/templates/charter.toml"):
            with self.subTest(contract=name):
                table = (ROOT / name).read_text().split("\n[review]\n", 1)[1].split("\n[", 1)[0]
                self.assertIn("\ncode_blocks = false\n", "\n" + table + "\n")


class VerdictMerges(Temp):
    def test_the_setup_turns_no_merge_on_and_names_the_token(self):
        """verdict-merges, check 7: the written contract and the contract of this repo name no tier with the
        approver `agent` and set the flag to false; the printed steps name the merge token as optional."""
        code, out = self.setup()
        self.assertEqual(code, cc.PASS, out)
        for name, path in (("the written contract", self.dir / cs.CONTRACT_FILE), ("this repo", ROOT / cs.CONTRACT_FILE)):
            with self.subTest(contract=name):
                data = tomllib.loads(path.read_text())
                self.assertTrue(data["tiers"])
                for tier, spec in data["tiers"].items():
                    self.assertNotEqual(spec.get("approver"), "agent", tier)
                self.assertIs(data["review"]["code_blocks"], False)
        steps = out.split(cs.msg("steps_title"), 1)[1]
        line = next((step for step in steps.splitlines() if "CHARTER_MERGE_TOKEN" in step), None)
        self.assertIsNotNone(line, steps)
        self.assertIn("Optional, for a repo that gives a tier the approver `agent`", line)
        self.assertRegex(line, r"^  \d+\. ")

    def test_the_instructions_say_who_merges(self):
        """verdict-merges, check 7: the instruction template and the instructions of this repo."""
        for path in (ROOT / "charter" / "templates" / cs.INSTRUCTIONS_FILE, ROOT / cs.INSTRUCTIONS_FILE):
            with self.subTest(file=str(path.relative_to(ROOT))):
                text = " ".join(path.read_text().split())
                self.assertIn("The approver of the tier merges: a person, or the verdict for a tier whose approver is "
                              "`agent`. [tiers.high.approver]", text)
                self.assertIn("In a tier whose approver is `agent`, the review of the plan by the intent reviewer is its "
                              "acceptance.", text)
                self.assertNotIn("A person merges.", text)


if __name__ == "__main__":
    unittest.main()
