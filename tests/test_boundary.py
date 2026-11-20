"""Tests of the boundary of a run without a person. Run: python3 -m unittest discover -s tests

Each test names the intent and the check that it implements, in its docstring. No test starts Claude Code:
the settings are read as data.
"""

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import tomllib
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
SETUP_FLAGS = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
               "--leader", "alice", "--quality", "python3 -m unittest discover -s tests"]
DEFAULT_NO_WRITE = ["charter.toml", "AGENTS.md", "CLAUDE.md", "intents/**", ".github/**", ".claude/**"]
DEFAULT_NO_READ = [".env", ".env.*", "**/.env", "**/.env.*"]
SOURCE = f"--{cc.ARG_SOURCE}"


def run(main, *argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


def boundary(no_write: list[str], no_read: list[str] | None = None) -> str:
    return f"\n[boundary]\nno_write = {json.dumps(no_write)}\nno_read = {json.dumps(no_read or [])}\n"


class Temp(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()).resolve()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def contract(self, section: str = "") -> Path:
        path = self.dir / cs.CONTRACT_FILE
        path.write_text(REPO.read_text() + section)
        return path

    def files(self, *names: str) -> None:
        for name in names:
            path = self.dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("text\n")

    def settings(self, section: str = "") -> dict:
        e = cc.effective_contract(self.contract(section), cc.DEFAULT_SCHEMA, ORG, self.dir / "cache")
        self.assertEqual(e.failures, [])
        return cc.boundary_settings(e, self.dir)

    def gate(self, contract: Path, *changed: str) -> tuple[int, str]:
        listed = self.dir / "changed.txt"
        listed.write_text("\n".join(changed) + "\n")
        return run(cg.main, cg.CMD_BOUNDARY, f"--{cc.ARG_CONTRACT}", str(contract), SOURCE, str(ORG),
                   f"--{cg.ARG_CHANGED}", str(listed))

    def gate_nul(self, contract: Path, *changed: str) -> tuple[int, str]:
        """The gate on a list with a NUL character after each path, as git writes it with `-z`."""
        listed = self.dir / "changed.bin"
        listed.write_text("".join(path + "\0" for path in changed))
        return run(cg.main, cg.CMD_BOUNDARY, f"--{cc.ARG_CONTRACT}", str(contract), SOURCE, str(ORG),
                   f"--{cg.ARG_CHANGED}", str(listed))


class Fields(Temp):
    def test_the_fields_are_in_the_schema_and_in_the_contract_document(self):
        """boundary-of-a-run, check 1."""
        fields = cc.load_schema(cc.DEFAULT_SCHEMA)
        document = (ROOT / "docs" / "contract.md").read_text()
        for name in (cc.FIELD_NO_WRITE, cc.FIELD_NO_READ):
            with self.subTest(field=name):
                self.assertEqual(fields[name][cc.ATTR_KIND], "set")
                self.assertIn(f"| `{name}` | set |", document)
        self.assertIn("charter_check.py boundary charter.toml", document)
        self.assertIn("charter_gate.py boundary --contract charter.toml --changed", document)

    def test_a_repo_cannot_drop_a_locked_pattern(self):
        """boundary-of-a-run, check 2: the organization locks a minimum; a repo adds, and cannot drop."""
        text = ORG.read_text().replace('  "tools.code_host",\n]', f'  "tools.code_host",\n  "{cc.FIELD_NO_WRITE}",\n]')
        self.assertIn(cc.FIELD_NO_WRITE, text)
        org = self.dir / "organization.toml"
        org.write_text(text + boundary(["charter.toml", ".github/**"]))
        for repo_patterns, expected in ((["charter.toml"], cc.FAIL),
                                        (["charter.toml", ".github/**", "package.json"], cc.PASS)):
            with self.subTest(repo=repo_patterns):
                code, out = run(cc.main, cc.CMD_CHECK, str(self.contract(boundary(repo_patterns))), SOURCE, str(org))
                self.assertEqual(code, expected, out)
                if expected == cc.FAIL:
                    self.assertIn(f"changes locked rule {cc.FIELD_NO_WRITE}", out)


class Settings(Temp):
    NO_WRITE = ["charter.toml", ".github/**", "src/*.lock", "keys/*.pem", "intents/**"]
    NO_READ = [".env", "**/.env.*"]
    FILES = (".github/workflows/tests.yml", "src/a.lock", "src/b.txt", "intents/a.md", "intents/a.plan.md",
             "intents/sub/b.md")

    def here(self, path: str) -> str:
        return f"{self.dir.as_posix()}/{path}"

    def edit(self, path: str) -> str:
        return f"Edit(/{self.here(path)})"

    def read(self, path: str) -> str:
        return f"Read(/{self.here(path)})"

    def full(self) -> dict:
        self.files(*self.FILES)
        return self.settings(boundary(self.NO_WRITE, self.NO_READ))

    def test_the_sandbox_is_on_and_the_run_fails_without_it(self):
        """boundary-of-a-run, check 3. The command prints the same settings, as JSON."""
        sandbox = self.full()["sandbox"]
        self.assertIs(sandbox["enabled"], True)
        self.assertIs(sandbox["failIfUnavailable"], True)
        self.assertIs(sandbox["allowUnsandboxedCommands"], False)
        code, out = run(cc.main, cc.CMD_BOUNDARY, str(self.dir / cs.CONTRACT_FILE), SOURCE, str(ORG))
        self.assertEqual(code, cc.PASS, out)
        self.assertEqual(json.loads(out), self.settings(boundary(self.NO_WRITE, self.NO_READ)))

    def test_the_shell_has_no_network(self):
        """boundary-of-a-run, check 3."""
        network = self.full()["sandbox"]["network"]
        self.assertEqual(network["allowedDomains"], [])
        self.assertIs(network["strictAllowlist"], True)

    def test_each_no_write_pattern_is_denied_in_both_layers(self):
        """boundary-of-a-run, check 4. A path and a folder go into both layers as they are. On Linux the
        sandbox honours no other wildcard, so such a pattern enters it as the files that match now, and a
        pattern that no file matches has a deny rule and no entry of the sandbox."""
        settings = self.full()
        deny, shell = settings["permissions"]["deny"], settings["sandbox"]["filesystem"]["denyWrite"]
        for path in ("charter.toml", ".github/**"):
            with self.subTest(pattern=path):
                self.assertIn(self.edit(path), deny)
                self.assertIn(self.here(path), shell)
        self.assertIn(self.edit("src/*.lock"), deny)
        self.assertIn(self.here("src/a.lock"), shell)
        self.assertNotIn(self.here("src/b.txt"), shell)
        self.assertIn(self.edit("keys/*.pem"), deny)
        self.assertFalse([entry for entry in shell if "keys" in entry])
        self.assertFalse([entry for entry in shell if any(c in entry.removesuffix("/**") for c in "*?")], shell)

    def test_each_no_read_pattern_is_denied_in_both_layers(self):
        """boundary-of-a-run, check 4."""
        settings = self.full()
        for pattern in self.NO_READ:
            with self.subTest(pattern=pattern):
                self.assertIn(self.read(pattern), settings["permissions"]["deny"])
                self.assertIn(self.here(pattern), settings["sandbox"]["filesystem"]["denyRead"])

    def test_the_tokens_leave_the_environment_of_the_shell(self):
        """boundary-of-a-run, check 5: the tokens of the model and of the code host."""
        entries = self.full()["sandbox"]["credentials"]["envVars"]
        self.assertTrue(all(entry["mode"] == "deny" for entry in entries))
        names = {entry["name"] for entry in entries}
        for name in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "CHARTER_ORG_TOKEN"):
            self.assertIn(name, names)

    def test_a_call_that_needs_a_question_is_refused(self):
        """boundary-of-a-run, check 5 (decision E6)."""
        self.assertIs(self.full()["permissions"]["denyInsteadOfPrompting"], True)

    def test_an_empty_section_keeps_the_sandbox(self):
        """boundary-of-a-run, check 6: an absent section, and an empty one."""
        for section in ("", boundary([])):
            with self.subTest(section=section):
                settings = self.settings(section)
                self.assertEqual(settings["permissions"]["deny"], [])
                self.assertEqual(settings["sandbox"]["filesystem"], {"denyWrite": [], "denyRead": []})
                self.assertIs(settings["sandbox"]["enabled"], True)
                self.assertIs(settings["sandbox"]["failIfUnavailable"], True)
                self.assertEqual(settings["sandbox"]["network"]["allowedDomains"], [])
                self.assertIs(settings["permissions"]["denyInsteadOfPrompting"], True)

    def test_the_plan_file_is_not_denied(self):
        """boundary-of-a-run, check 9: a deny rule for a folder cannot be opened again for one file, so
        `intents/**` is written as the files under it that are no plan, in both layers."""
        settings = self.full()
        deny, shell = settings["permissions"]["deny"], settings["sandbox"]["filesystem"]["denyWrite"]
        for path in ("intents/a.md", "intents/sub/b.md"):
            with self.subTest(file=path):
                self.assertIn(self.edit(path), deny)
                self.assertIn(self.here(path), shell)
        for entry in deny + shell:
            self.assertNotIn(".plan.md", entry)
            self.assertFalse(entry.rstrip(")").endswith(("intents", "intents/**")), entry)


class Gate(Temp):
    NO_WRITE = ["charter.toml", "AGENTS.md", "intents/**", ".github/**"]

    def closed(self) -> Path:
        return self.contract(boundary(self.NO_WRITE))

    def test_a_path_under_no_write_fails(self):
        """boundary-of-a-run, check 7."""
        code, out = self.gate(self.closed(), "src/core.py", "charter.toml")
        self.assertEqual(code, cc.FAIL, out)

    def test_the_failure_names_the_path_the_field_and_the_remedy(self):
        """boundary-of-a-run, check 7."""
        code, out = self.gate(self.closed(), "src/core.py", ".github/workflows/tests.yml")
        self.assertEqual(code, cc.FAIL, out)
        self.assertIn(".github/workflows/tests.yml: a run without a person cannot change this path", out)
        self.assertIn(cc.FIELD_NO_WRITE, out)
        self.assertIn("A person makes this change, in its own change request.", out)
        self.assertNotIn("src/core.py", out)

    def test_paths_outside_the_patterns_pass(self):
        """boundary-of-a-run, check 7: also a file whose name only looks like a closed one, and no section."""
        code, out = self.gate(self.closed(), "src/core.py", "docs/charter.toml", "tests/test_core.py", "AGENTS.md.txt")
        self.assertEqual(code, cc.PASS, out)
        self.assertEqual(self.gate(self.contract(), "charter.toml")[0], cc.PASS)

    def test_the_forms_that_go_around_a_pattern_fail(self):
        """boundary-of-a-run, check 8. A deleted file and the two names of a rename are lines of the list,
        as the gate asks for them."""
        contract = self.closed()
        forms = {
            "dot segments": ["./charter.toml"],
            "a way through another folder": ["docs/../charter.toml"],
            "a file at depth under a folder pattern": [".github/workflows/deep/more/x.yml"],
            "a deleted file": ["AGENTS.md"],
            "a rename from a closed path": ["intents/a.md", "notes/a.md"],
            "a rename to a closed path": ["notes/b.md", "intents/b.md"],
            "a path that leaves the repo": ["../outside.txt"],
            "a path that leaves the repo through a folder": ["src/../../outside.txt"],
            "an absolute path": ["/etc/hosts"],
        }
        for form, changed in forms.items():
            with self.subTest(form=form):
                code, out = self.gate(contract, "src/core.py", *changed)
                self.assertEqual(code, cc.FAIL, out)

    def test_the_plan_file_passes_and_the_intent_fails(self):
        """boundary-of-a-run, check 9 (decision E10)."""
        contract = self.closed()
        code, out = self.gate(contract, "intents/core-state.plan.md", "src/core.py")
        self.assertEqual(code, cc.PASS, out)
        code, out = self.gate(contract, "intents/core-state.plan.md", "intents/core-state.md")
        self.assertEqual(code, cc.FAIL, out)
        self.assertIn("intents/core-state.md: a run without a person", out)
        self.assertNotIn("core-state.plan.md", out)


    SPECIAL = ("caf\u00e9.md", "a b.md", "a\nb.md", '"q".md', "a\\b.md")

    def test_a_list_with_nul_between_the_paths_is_read(self):
        """boundary-gate-reads-any-path, check 1: a letter outside ASCII, a space, a line break; a name
        that starts with a double quote and a name with a backslash are read as they are."""
        contract = self.closed()
        for name in self.SPECIAL:
            with self.subTest(name=name):
                code, out = self.gate_nul(contract, "src/core.py", f"intents/{name}")
                self.assertEqual(code, cc.FAIL, out)
                self.assertIn(f"intents/{name}: a run without a person cannot change this path", out)
                code, out = self.gate_nul(contract, "src/core.py", f"notes/{name}")
                self.assertEqual(code, cc.PASS, out)
        self.assertEqual(self.gate_nul(contract, "charter.toml")[0], cc.FAIL)
        code, out = self.gate_nul(contract, '"q".md', "src/core.py")
        self.assertEqual(code, cc.PASS, out)

    def test_a_path_in_the_quotes_of_git_fails(self):
        """boundary-gate-reads-any-path, check 2: git writes `intents/café.md` in this form in a list of
        lines. The failure names the line and holds the text `-z`."""
        line = '"intents/caf\\303\\251.md"'
        code, out = self.gate(self.closed(), "src/core.py", line)
        self.assertEqual(code, cc.FAIL, out)
        self.assertIn(line, out)
        self.assertIn("`-z`", out)
        self.assertNotIn("src/core.py", out)

    def test_the_contract_document_names_the_two_forms_of_the_list(self):
        """boundary-gate-reads-any-path, check 4."""
        text = (ROOT / "docs" / "contract.md").read_text()
        section = " ".join(text.split("## The boundary of a run")[1].split("\n## ")[0].split())
        self.assertIn("With a NUL character between the paths, as git writes them with `-z`", section)
        self.assertIn("a line in the quotes of git fails", section)

    def test_the_version_carries_the_correction(self):
        """boundary-gate-reads-any-path, check 5."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 7))


class Defaults(Temp):
    RULE = ("A run of an agent without a person does not change the files that the contract closes to it. "
            "A person makes such a change, in its own change request. [boundary.no_write]")

    def setup_repo(self) -> Path:
        code, out = run(cs.main, *SETUP_FLAGS, "--target", str(self.dir))
        self.assertEqual(code, cc.PASS, out)
        return self.dir / cs.CONTRACT_FILE

    def test_the_new_contract_carries_the_default_patterns(self):
        """boundary-of-a-run, check 10. The contract of this repo carries the same section (check 13)."""
        for contract in (self.setup_repo(), ROOT / cs.CONTRACT_FILE):
            with self.subTest(contract=str(contract)):
                data = tomllib.loads(contract.read_text())
                self.assertEqual(data["boundary"]["no_write"], DEFAULT_NO_WRITE)
                self.assertEqual(data["boundary"]["no_read"], DEFAULT_NO_READ)
        self.assertEqual(run(cc.main, cc.CMD_ALL, str(self.dir / cs.CONTRACT_FILE), SOURCE, str(ORG))[0], cc.PASS)

    def test_the_gate_refuses_each_default_path_in_a_new_repo(self):
        """boundary-of-a-run, check 10: one path under each default pattern, one at a time."""
        contract = self.setup_repo()
        for path in ("charter.toml", "AGENTS.md", "CLAUDE.md", "intents/core-state.md", ".github/workflows/tests.yml",
                     ".claude/settings.json"):
            with self.subTest(path=path):
                code, out = self.gate(contract, path)
                self.assertEqual(code, cc.FAIL, out)
                self.assertIn(f"{path}: a run without a person", out)
        self.assertEqual(self.gate(contract, "src/core.py", "docs/product.md")[0], cc.PASS)

    def test_the_instructions_carry_the_rule(self):
        """boundary-of-a-run, check 11: the template that the setup step writes, and this repo."""
        self.setup_repo()
        for path in (self.dir / cs.INSTRUCTIONS_FILE, ROOT / cs.INSTRUCTIONS_FILE):
            with self.subTest(file=str(path)):
                self.assertIn(self.RULE, " ".join(path.read_text().split()))

    def test_the_decisions_are_recorded(self):
        """boundary-of-a-run, check 12: four decisions with a reason each, and E4 names the one that
        replaces its conformance check for a run."""
        text = (ROOT / "docs" / "decisions.md").read_text()
        for row, words in (("E7", "no credential of the code host"), ("E8", "at the start of each run"),
                           ("E9", "two layers"), ("E10", "the plan of a work item")):
            with self.subTest(row=row):
                found = re.search(rf"^\| {row} \| (.+?) \| (.+?) \| 2026-11-20 \|$", text, re.M)
                self.assertIsNotNone(found, f"no row {row}")
                self.assertIn(words, found.group(1))
                self.assertTrue(found.group(2).strip(), f"{row} has no reason")
        e4 = re.search(r"^\| E4 \| (.+?) \|", text, re.M)
        self.assertIn("E8 replaces the conformance check", e4.group(1))

    def test_both_manifests_name_the_version(self):
        """boundary-of-a-run, check 14: 0.3.6 carries the boundary; a later version carries it too."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 6))

    def test_the_product_document_states_the_boundary_of_a_run(self):
        """boundary-of-a-run, check 15."""
        text = (ROOT / "docs" / "product.md").read_text()
        section = " ".join(text.split("## Who does the work")[1].split("\n## ")[0].split())
        self.assertIn("with no person present cannot change the contract", section)
        self.assertIn("holds no credential of the code host", section)


if __name__ == "__main__":
    unittest.main()
