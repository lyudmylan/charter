"""Tests of the update of a repo. Intent: update-a-repo. Run: python3 -m unittest discover -s tests

Each test builds a repo with the setup step from templates of an older version, a copy of the templates of
today with a few lines less, and then runs the update. No test uses the network: the folder of the older
templates is given to the command.
"""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_setup as cs  # noqa: E402
import charter_update as cu  # noqa: E402

OLD_VERSION = "0.3.1"
TOOLCHAIN_STEP = "- uses: example/setup-tool@v1     # the toolchain of the sample repo"
FLAGS = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
         "--leader", "alice", "--quality", "python3 -m unittest discover -s tests"]
HAND_LINE = "# a line that this repo added by hand"
NEW_FIELD, NEW_RULE = "boundary.no_read", "boundary.no_write"
WORKFLOWS = ".github/workflows"


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cu.main(list(argv))
    return code, out.getvalue()


def without(text: str, part: str) -> str:
    """The text with no line that holds `part`; the test fails when no line holds it."""
    lines = text.splitlines(keepends=True)
    kept = [line for line in lines if part not in line]
    assert len(kept) < len(lines), part
    return "".join(kept)


class Update(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        self.old = self.work / "old-templates"
        shutil.copytree(cs.TEMPLATES, self.old)
        # The older version: two workflows with one line less, a contract template with one field less, and
        # a rules file with one rule less.
        for name in ("verdict.yml", "review-code.yml"):
            path = self.old / name
            path.write_text("".join(path.read_text().splitlines(keepends=True)[1:]))
        contract = self.old / "charter.toml"
        contract.write_text(without(contract.read_text(), "no_read ="))
        rules = self.old / "AGENTS.md"
        rules.write_text(without(rules.read_text(), f"[{NEW_RULE}]"))
        toolchain = self.work / "toolchain.yml"
        toolchain.write_text(TOOLCHAIN_STEP + "\n")
        self.repo = self.work / "repo"
        self.repo.mkdir()
        with mock.patch.object(cs, "TEMPLATES", self.old), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cs.main([*FLAGS, "--toolchain", str(toolchain), "--target", str(self.repo)]), 0)
        contract = self.repo / cs.CONTRACT_FILE
        contract.write_text(contract.read_text().replace(f'version = "{cs.charter_version()}"', f'version = "{OLD_VERSION}"'))
        self.assertEqual(tomllib.loads(contract.read_text())["charter"]["version"], OLD_VERSION)
        self.flags = ["--target", str(self.repo), "--old-templates", str(self.old)]

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def files(self) -> dict:
        return {str(p.relative_to(self.repo)): p.read_text() for p in sorted(self.repo.rglob("*")) if p.is_file()}

    def test_the_generated_files_move_and_the_block_of_the_repo_stays(self):
        """update-a-repo, check 1: each workflow and each template has the text of this version, with the
        toolchain of the repo in `tests` and in `run`; a file that did not change is named as the same."""
        code, out = run(*self.flags)
        self.assertEqual(code, 0, out)
        for name, written in cu.GENERATED.items():
            with self.subTest(file=written):
                block = TOOLCHAIN_STEP + "\n" if name in cs.TOOLCHAIN_TEMPLATES else ""
                self.assertEqual((self.repo / written).read_text(), cu.text_of(cs.TEMPLATES, name, block))
        for name in ("tests.yml", "run.yml"):
            lines = (self.repo / WORKFLOWS / name).read_text().splitlines()
            start = lines.index(cs.STEP_INDENT + cs.TOOLCHAIN_START)
            self.assertEqual(lines[start + 1], cs.STEP_INDENT + TOOLCHAIN_STEP)
            self.assertEqual(lines[start + 2], cs.STEP_INDENT + cs.TOOLCHAIN_END)
        # A fixed anchor, with no function of the command: the template of today with its one value.
        self.assertEqual((self.repo / WORKFLOWS / "verdict.yml").read_text(),
                         (cs.TEMPLATES / "verdict.yml").read_text().replace("%{charter_address}", cs.CHARTER_ADDRESS))
        self.assertIn(f"updated: {WORKFLOWS}/verdict.yml\n", out)
        self.assertIn(f"updated: {WORKFLOWS}/review-code.yml\n", out)
        self.assertIn(f"same: {WORKFLOWS}/tests.yml\n", out)
        self.assertNotIn("changed it by hand", out)
        self.assertEqual(run(*self.flags)[1].count("same: "), len(cu.GENERATED))

    def test_a_file_that_the_repo_changed_by_hand_is_named(self):
        """update-a-repo, check 2: the file gets the text of this version, and the output names it and prints
        the line of the repo, so that the change is not lost without notice."""
        path = self.repo / WORKFLOWS / "review-code.yml"
        path.write_text(path.read_text() + HAND_LINE + "\n")
        code, out = run(*self.flags)
        self.assertEqual(code, 0, out)
        self.assertIn(f"this repo changed it by hand: {WORKFLOWS}/review-code.yml", out)
        self.assertIn(f"  +{HAND_LINE}", out)
        self.assertEqual(path.read_text(), cu.text_of(cs.TEMPLATES, "review-code.yml", ""))
        self.assertIn(f"updated: {WORKFLOWS}/verdict.yml\n", out)

    def test_a_file_with_content_of_the_repo_keeps_it(self):
        """update-a-repo, check 3: in the contract only the version line moves; the rules file and the
        documents stay; the output names the field and the rule that this version adds."""
        before = self.files()
        code, out = run(*self.flags)
        self.assertEqual(code, 0, out)
        after = self.files()
        contract = after[cs.CONTRACT_FILE].splitlines()
        self.assertEqual([line for line in contract if line not in before[cs.CONTRACT_FILE].splitlines()],
                         [f'version = "{cs.charter_version()}"'])
        self.assertEqual(len(contract), len(before[cs.CONTRACT_FILE].splitlines()))
        self.assertEqual(tomllib.loads(after[cs.CONTRACT_FILE])["source"]["version"], "v1")
        for name in (cs.INSTRUCTIONS_FILE, cs.PRODUCT_FILE, "docs/architecture.md"):
            self.assertEqual(after[name], before[name], name)
        self.assertIn(f"version: {OLD_VERSION} -> {cs.charter_version()} in {cs.CONTRACT_FILE}", out)
        self.assertIn(f"new field: {NEW_FIELD}.", out)
        self.assertIn(f"new rule: [{NEW_RULE}].", out)
        self.assertIn("The contract of this repo is not changed", out)
        self.assertNotIn("new field: charter.version", out)

    def test_the_check_form_writes_no_file(self):
        """update-a-repo, check 4."""
        before = self.files()
        code, out = run(*self.flags, "--check")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.files(), before)
        self.assertIn("check only: no file was written", out)
        self.assertIn(f"updated: {WORKFLOWS}/verdict.yml\n", out)

    def test_the_command_refuses_and_ends(self):
        """update-a-repo, check 5: nothing to change after an update; a contract of a newer version is
        refused; a folder with no contract cannot run."""
        self.assertEqual(run(*self.flags)[0], 0)
        code, out = run(*self.flags)
        self.assertEqual(code, 0, out)
        self.assertIn("nothing to change", out)
        contract = self.repo / cs.CONTRACT_FILE
        contract.write_text(contract.read_text().replace(f'version = "{cs.charter_version()}"', 'version = "99.0.0"'))
        before = self.files()
        code, out = run(*self.flags)
        self.assertEqual(code, 1, out)
        self.assertIn("refused: the contract names Charter 99.0.0", out)
        self.assertEqual(self.files(), before)
        # A version line that the command cannot change, here in single quotes: refused, and no file is written.
        contract.write_text(contract.read_text().replace('version = "99.0.0"', f"version = '{OLD_VERSION}'"))
        workflow = self.repo / WORKFLOWS / "verdict.yml"
        workflow.write_text(workflow.read_text() + HAND_LINE + "\n")
        before = self.files()
        code, out = run(*self.flags)
        self.assertEqual(code, 1, out)
        self.assertIn("refused: the version line of the table [charter] cannot be changed", out)
        self.assertEqual(self.files(), before)
        contract.write_text(contract.read_text().replace(f"version = '{OLD_VERSION}'", 'version = "0.3.21-rc1"'))
        code, out = run(*self.flags)
        self.assertEqual(code, 2, out)
        self.assertIn("is not a row of numbers with points: 0.3.21-rc1", out)
        self.assertEqual(self.files()[f"{WORKFLOWS}/verdict.yml"], before[f"{WORKFLOWS}/verdict.yml"])
        empty = self.work / "empty"
        empty.mkdir()
        code, out = run("--target", str(empty))
        self.assertEqual(code, 2, out)
        self.assertIn("no contract in this folder", out)

    def test_without_the_older_templates_each_changed_file_is_named(self):
        """update-a-repo, check 6: when the older version cannot be fetched, the update still writes, and it
        says for each changed file that it was not compared."""
        code, out = run("--target", str(self.repo), "--charter-address", str(self.work / "no-such-repo"))
        self.assertEqual(code, 0, out)
        self.assertIn(f"the templates of Charter {OLD_VERSION} are not here", out)
        self.assertIn(f"updated, not compared with Charter {OLD_VERSION}: {WORKFLOWS}/verdict.yml", out)
        self.assertEqual((self.repo / WORKFLOWS / "verdict.yml").read_text(), cu.text_of(cs.TEMPLATES, "verdict.yml", ""))
        self.assertNotIn("new field", out)

    def test_the_command_the_documents_and_the_version(self):
        """update-a-repo, check 7."""
        command = ROOT / "charter" / "bin" / "charter-update"
        self.assertTrue(command.is_file() and command.stat().st_mode & 0o111)
        self.assertIn("scripts/charter_update.py", command.read_text())
        contract = " ".join((ROOT / "docs" / "contract.md").read_text().split())
        for part in ("### The update of a repo", "`charter-update`", "changed it by hand", "only the version line moves"):
            self.assertIn(part, contract)
        self.assertIn("`charter-update`", (ROOT / "README.md").read_text())
        self.assertIn("`charter-update`", (ROOT / "docs" / "product.md").read_text())
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 21))


if __name__ == "__main__":
    unittest.main()
