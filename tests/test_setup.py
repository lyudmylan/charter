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
        for name in ("tests.yml", "verdict.yml", "review-intents.yml"):
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
        for name in ("tests.yml", "verdict.yml", "review-intents.yml"):
            text = (self.dir / cs.WORKFLOWS / name).read_text()
            with self.subTest(workflow=name):
                self.assertIsNone(re.search(r"^    env:\n(?:      .*\n)*?      \w+: \$\{\{ runner\.", text, re.M),
                                  "a job-level env uses the runner context")
                self.assertIn('>> "$GITHUB_ENV"', text) if name != "review-intents.yml" else None

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


class Commands(unittest.TestCase):
    def test_the_four_commands_exist_and_the_manifests_agree(self):
        """setup-step, check 5."""
        for name in ("charter-setup", "charter-check", "charter-gate", "charter-facts-github"):
            path = ROOT / "charter" / "bin" / name
            with self.subTest(command=name):
                self.assertTrue(path.is_file(), name)
                self.assertTrue(path.stat().st_mode & 0o111, f"{name} is not executable")
                self.assertIn(f"scripts/{name.replace('-', '_')}.py", path.read_text())
        core = json.loads(cs.MANIFEST.read_text())["version"]
        practices = json.loads((ROOT / "charter-practices" / ".claude-plugin" / "plugin.json").read_text())["version"]
        self.assertEqual(core, practices)


if __name__ == "__main__":
    unittest.main()
