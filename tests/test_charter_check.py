"""Tests of the contract checker. Run: python3 -m unittest discover -s tests

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
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "charter" / "scripts"))
import charter_check as cc  # noqa: E402

SAMPLES = ROOT / "tests" / "samples"
ORG = SAMPLES / "organization.toml"
REPO = SAMPLES / "repo.toml"
SAMPLE_ADDRESS = "https://example.com/org/rules"


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cc.main(list(argv))
    return code, out.getvalue()


def repo_with(**changes: str) -> str:
    """The sample repo contract with lines replaced. Keys are the exact lines to replace."""
    text = REPO.read_text()
    for old, new in changes.items():
        assert old in text, old
        text = text.replace(old, new)
    return text


class Temp(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, name: str, text: str) -> Path:
        path = self.dir / name
        path.write_text(text)
        return path


class Validate(Temp):
    def test_valid_files_pass(self):
        """contract-checker, check 1."""
        self.assertEqual(run(cc.CMD_VALIDATE, str(ORG))[0], cc.PASS)
        self.assertEqual(run(cc.CMD_VALIDATE, str(REPO))[0], cc.PASS)

    def test_missing_field_names_the_field(self):
        """contract-checker, check 2."""
        path = self.write("r.toml", repo_with(**{'version = "v1"\n': ""}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn(f"{cc.TABLE_SOURCE}.version", out)

    def test_wrong_type_names_the_field(self):
        """contract-checker, check 2."""
        path = self.write("r.toml", repo_with(**{"refusals = 3": 'refusals = "two"'}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("limits.refusals", out)

    def test_unknown_field_fails(self):
        """contract-checker, check 2."""
        path = self.write("r.toml", repo_with(**{"refusals = 3": "refusals = 3\nretries = 9"}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn(cc.msg("unknown_field", name=path, field="limits.retries"), out)

    def test_charter_version_field(self):
        """charter-version-in-ci, check 1."""
        path = self.write("r.toml", repo_with(**{"refusals = 3": 'refusals = 3\n[charter]\nversion = "0.1.0"'}))
        self.assertEqual(run(cc.CMD_VALIDATE, str(path))[0], cc.PASS)
        path = self.write("r.toml", repo_with(**{"refusals = 3": "refusals = 3\n[charter]\nversion = 1"}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("charter.version", out)

    def test_locked_field_without_value_fails(self):
        """contract-checker, check 2."""
        path = self.write("o.toml", ORG.read_text().replace('code_host = "github"\n', ""))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn(cc.msg("lock_no_value", name=path, field="tools.code_host"), out)


class Check(Temp):
    def check(self, repo_text: str) -> tuple[int, str]:
        path = self.write("r.toml", repo_text)
        return run(cc.CMD_CHECK, str(path), f"--{cc.ARG_SOURCE}", str(ORG))

    def test_valid_pair_passes_and_names_the_source(self):
        """contract-checker, checks 1 and 7."""
        code, out = run(cc.CMD_CHECK, str(REPO), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.PASS)
        self.assertIn(f"{cc.OUT_SOURCE}: ", out)
        self.assertIn(f"{cc.OUT_PASS}:", out)

    def test_repo_adds_an_unlocked_rule(self):
        """contract-checker, check 3."""
        code, _ = self.check(repo_with(**{"refusals = 3": "refusals = 3\nacceptance_loop = 9"}))
        self.assertEqual(code, cc.PASS)

    def test_stricter_in_each_direction_passes(self):
        """contract-checker, check 4. Flag stays true; limit equal; count 2 > 1; set is a superset;
        choice leader > team_lead; text equal."""
        code, _ = self.check(repo_with(**{"refusals = 3": "refusals = 3\n[change]\nperson_approves_contract = true"}))
        self.assertEqual(code, cc.PASS)

    def test_a_locked_limit_is_exact(self):
        """contract-checker, check 5: a smaller and a larger number both change the policy (#51)."""
        for value in ("2", "4"):
            with self.subTest(value=value):
                code, out = self.check(repo_with(**{"refusals = 3": f"refusals = {value}"}))
                self.assertEqual(code, cc.FAIL)
                self.assertIn("changes locked rule limits.refusals", out)

    def test_weaker_in_each_direction_fails_and_names_the_rule(self):
        """contract-checker, check 5."""
        cases = {
            "change.person_approves_contract": {"refusals = 3": "refusals = 3\n[change]\nperson_approves_contract = false"},
            "limits.refusals": {"refusals = 3": "refusals = 5"},
            "tiers.high.approvals": {"approvals = 2": "approvals = 0"},
            "documents.necessary": {'necessary = ["docs/product.md", "docs/architecture.md"]': 'necessary = ["docs/architecture.md"]'},
            "tiers.high.approver": {'approver = "leader"': 'approver = "engineer"'},
            "tools.code_host": {'code_host = "github"': 'code_host = "gitlab"'},
        }
        for rule, change in cases.items():
            with self.subTest(rule=rule):
                code, out = self.check(repo_with(**change))
                self.assertEqual(code, cc.FAIL)
                self.assertIn(f"changes locked rule {rule}", out)

    def test_json_output_is_json_and_redacts_the_pattern_sets(self):
        """contract-checker, check 1: the effective contract merges the source and the repo."""
        code, out = run(cc.CMD_CHECK, str(REPO), f"--{cc.ARG_SOURCE}", str(ORG), f"--{cc.ARG_JSON}")
        self.assertEqual(code, cc.PASS)
        data = json.loads(out)
        effective = data[cc.JSON_KEY_EFFECTIVE]
        self.assertEqual(effective["tiers.high.approvals"], 2)      # the repo's stricter value
        self.assertEqual(effective["limits.review_loop"], 3)         # inherited from the source
        self.assertNotIn("secret-project", out)
        self.assertEqual(effective["text.project_name_patterns"], cc.msg("redacted", count=1))


class CannotRun(Temp):
    def test_no_file(self):
        """contract-checker, check 6."""
        path = self.dir / "none.toml"
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: {cc.msg('no_file', path=path)}", out)

    def test_a_directory_is_not_a_file(self):
        """contract-checker, check 6."""
        code, out = run(cc.CMD_VALIDATE, str(self.dir))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: {cc.msg('not_a_file', path=self.dir)}", out)

    def test_not_toml(self):
        """contract-checker, check 6."""
        path = self.write("bad.toml", "schema = [unclosed")
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: not TOML", out)

    def test_source_not_found(self):
        """contract-checker, check 6."""
        code, out = run(cc.CMD_CHECK, str(REPO), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: source not found: {SAMPLE_ADDRESS}", out)
        self.assertIn(f"{cc.GIT} clone", out)

    def test_address_that_escapes_the_cache_is_refused(self):
        """contract-checker, check 6: a source address cannot point outside the cache."""
        path = self.write("r.toml", repo_with(**{f'address = "{SAMPLE_ADDRESS}"': 'address = "https://example.com/../../etc"'}))
        code, out = run(cc.CMD_CHECK, str(path), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn("cannot be a cache path", out)

    def make_cache(self) -> Path:
        cache = cc.cache_path(SAMPLE_ADDRESS, self.dir)
        cache.mkdir(parents=True)
        shutil.copy(ORG, cache / "organization.toml")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        for cmd in ([cc.GIT, "init", "-q"], [cc.GIT, "add", "."], [cc.GIT, "commit", "-q", "-m", "rules"], [cc.GIT, "tag", "v1"]):
            subprocess.run(cmd, cwd=cache, check=True, env=env, capture_output=True)
        return cache

    def test_cache_resolves_and_names_the_version(self):
        """contract-checker, check 7."""
        self.make_cache()
        code, out = run(cc.CMD_CHECK, str(REPO), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.PASS, out)
        self.assertIn(f"{cc.OUT_SOURCE}: {cc.msg('source_origin', address=SAMPLE_ADDRESS, version='v1')}", out)

    def test_version_not_found(self):
        """contract-checker, check 6."""
        self.make_cache()
        path = self.write("r.toml", repo_with(**{'version = "v1"': 'version = "v9"'}))
        code, out = run(cc.CMD_CHECK, str(path), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: version not found: v9", out)

    @unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "file permissions")
    def test_access_denied(self):
        """contract-checker, check 6."""
        path = self.write("r.toml", REPO.read_text())
        path.chmod(0)
        try:
            code, out = run(cc.CMD_VALIDATE, str(path))
        finally:
            path.chmod(0o600)
        self.assertEqual(code, cc.CANNOT_RUN)
        self.assertIn(f"{cc.OUT_CANNOT_RUN}: {cc.msg('access_denied', path=path)}", out)


class Instructions(Temp):
    def instructions(self, text: str) -> tuple[int, str]:
        path = self.write("AGENTS.md", text)
        return run(cc.CMD_INSTRUCTIONS, str(path), f"--{cc.ARG_CONTRACT}", str(REPO), f"--{cc.ARG_SOURCE}", str(ORG))

    def test_known_identifiers_pass(self):
        """repository-instructions, check 1."""
        code, out = self.instructions("Refusals stop at the limit. [limits.refusals]\nOne approver. [tiers.high.approver]\n")
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("2 identifiers", out)

    def test_unknown_identifier_fails(self):
        """repository-instructions, check 1."""
        code, out = self.instructions("Rule. [limits.retries]\n")
        self.assertEqual(code, cc.FAIL)
        self.assertIn("[limits.retries] has no value", out)

    def test_bracketed_file_names_are_not_identifiers(self):
        """repository-instructions, check 1."""
        code, out = self.instructions("See [charter.toml] and [docs/x.md]. Limit. [limits.refusals]\n")
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("1 identifiers", out)

    def test_no_identifiers_fails(self):
        """repository-instructions, check 1."""
        code, out = self.instructions("No marks here.\n")
        self.assertEqual(code, cc.FAIL)
        self.assertIn("no rule identifiers", out)

    def test_private_material_and_project_names_fail(self):
        """repository-instructions, checks 2 and 3."""
        code, out = self.instructions("Mail a@example.com [limits.refusals]\nThe Secret-Project [limits.refusals]\ncode/session_1 [limits.refusals]\n")
        self.assertEqual(code, cc.FAIL)
        self.assertIn(":1: matches a pattern of text.private_material_patterns", out)
        self.assertIn(":2: matches a pattern of text.project_name_patterns", out)
        self.assertIn(":3: matches a pattern of text.session_link_patterns", out)


class OwnName(Temp):
    def test_the_name_of_the_repo_is_not_a_foreign_project_name(self):
        """repository-instructions, check 1: the organization lists every project; a repo may name itself."""
        repo = self.write("r.toml", repo_with(**{'name = "sample-repo"': 'name = "Secret-Project"'}))
        path = self.write("README.md", "The secret-project investigates incidents.\n")
        code, out = run(cc.CMD_TEXT, str(path), f"--{cc.ARG_CONTRACT}", str(repo), f"--{cc.ARG_SOURCE}", str(ORG))
        self.assertEqual(code, cc.PASS, out)


class Source(Temp):
    def test_source_prints_address_file_version_and_cache_path(self):
        """code-host, check 1: the workflow populates the cache from these lines."""
        code, out = run(cc.CMD_SOURCE, str(REPO), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.PASS, out)
        lines = out.splitlines()
        self.assertEqual(lines[:3], [SAMPLE_ADDRESS, "organization.toml", "v1"])
        self.assertEqual(Path(lines[3]), cc.cache_path(SAMPLE_ADDRESS, self.dir))


    def test_source_refuses_an_organization_file(self):
        """code-host, check 1."""
        code, out = run(cc.CMD_SOURCE, str(ORG), "--cache-dir", str(self.dir))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("not a repo contract", out)


class TextFiles(Temp):
    def text(self, content: str) -> tuple[int, str]:
        path = self.write("README.md", content)
        return run(cc.CMD_TEXT, str(path), f"--{cc.ARG_CONTRACT}", str(REPO), f"--{cc.ARG_SOURCE}", str(ORG))

    def test_clean_text_passes_without_identifiers(self):
        """readme, check 1."""
        code, out = self.text("A plain file with no marks.\n")
        self.assertEqual(code, cc.PASS, out)

    def test_pattern_in_text_fails(self):
        """readme, check 1."""
        code, out = self.text("Write to a@example.com\n")
        self.assertEqual(code, cc.FAIL)
        self.assertIn(":1: matches a pattern of text.private_material_patterns", out)


PLAN = """# Milestone: Iteration 4

The goal of the milestone, in free text. Tier: a word of this text is no line of a work item.

## Work items

### #141 The plan of a milestone is a file
Done: a milestone plan is one file in the repo,
  and the merge of the leader approves its work items.
Tier: high

### #142 The reviewer checks an intent against the "done" line
Done: a finding names the part of the "done" line that no check proves.
Needs: #141
Needs: Charter 0.3.23
Needs: the word of the leader
"""


class MilestonePlan(Temp):
    """The plan of a milestone, `milestones/<name>.md`: the reader of its form, the command, and `all`."""

    def check(self, text: str) -> tuple[int, str]:
        return run(cc.CMD_MILESTONE, str(self.write("plan.md", text)))

    def test_a_plan_in_the_form_passes_and_the_command_prints_its_work_items(self):
        """milestone-plan, check 1."""
        code, out = self.check(PLAN)
        self.assertEqual(code, cc.PASS, out)
        self.assertIn("the plan of the milestone 'Iteration 4', 2 work items", out)
        self.assertIn("#141 The plan of a milestone is a file; Tier: high\n", out)
        self.assertIn('#142 The reviewer checks an intent against the "done" line; Needs: #141; Needs: Charter 0.3.23; '
                      "Needs: the word of the leader\n", out)
        self.assertEqual(run(cc.CMD_MILESTONE, str(self.dir / "none.md"))[0], cc.CANNOT_RUN)

    def test_each_fault_of_the_form_fails_with_its_reason(self):
        """milestone-plan, check 2."""
        item = "### #141 The plan of a milestone is a file\n"
        cases = {
            "the first line": (PLAN.replace("# Milestone: Iteration 4", "# Iteration 4"), "line 1 is not `# Milestone: <name>`"),
            "a first line with no name": (PLAN.replace("# Milestone: Iteration 4", "# Milestone: "), "line 1 is not `# Milestone: <name>`"),
            "no work item": ("# Milestone: Iteration 4\n\nA goal.\n", "the plan holds no work item"),
            "a heading with no issue": (PLAN.replace("### #141 The", "### The"), "line 7: a heading of a work item has the form"),
            "a heading with no title": (PLAN.replace(item, "### #141\n"), "line 7: a heading of a work item has the form"),
            "no line Done": (PLAN.replace("Done: a finding names the part of the \"done\" line that no check proves.\n", ""),
                             "#142 has no line `Done:`"),
            "a line Done with no text": (PLAN.replace('Done: a finding names the part of the "done" line that no check proves.', "Done:"),
                                         "#142 has no line `Done:`"),
            "two lines Done": (PLAN + "Done: a second text.\n", "#142 has 2 lines `Done:`, and it can have one"),
            "two lines Tier": (PLAN.replace("Tier: high\n", "Tier: high\nTier: high\n"), "#141 has 2 lines `Tier:`, and it can have one"),
            "another tier": (PLAN.replace("Tier: high", "Tier: low"), "#141: `Tier: low`: the one value of this line is `high`"),
            "an issue two times": (PLAN.replace("### #142", "### #141"), "#141 is a work item of the plan 2 times"),
            "a word that is no line of the form": (PLAN.replace("Tier: high", "Teir: high"), "line 10: #141: `Teir:` is no line of a work item"),
            "a text after a line Needs": (PLAN + "and one more text\n", "line 17: #142: the line starts with no"),
            "a heading of the level of a work item": (PLAN.replace("## Work items", "### Work items"),
                                                      "line 5: a heading of a work item has the form"),
            # A line that starts with `#` and is no heading does not end the work item: the lines after it are read.
            "a line that starts with a number mark": (PLAN.replace("Needs: #141\n", "#141 comes first\nNeeds: #99\n"),
                                                      "#142: `Needs: #99` names no other work item"),
            "a wrong word after such a line": (PLAN.replace("Tier: high", "#140 is merged\nTeir: high"),
                                               "line 11: #141: `Teir:` is no line of a work item"),
        }
        for name, (text, reason) in cases.items():
            with self.subTest(case=name):
                code, out = self.check(text)
                self.assertEqual(code, cc.FAIL, out)
                self.assertIn(f"fail: {self.dir / 'plan.md'}: {reason}", out)
                self.assertNotIn("pass:", out)

    def test_a_line_done_continues_and_a_text_outside_a_work_item_is_free(self):
        """milestone-plan, check 3."""
        name, items, problems = cc.read_milestone(PLAN)
        self.assertEqual((name, problems), ("Iteration 4", []))
        self.assertEqual(items[0].done, ["a milestone plan is one file in the repo, and the merge of the leader approves its work items."])
        self.assertEqual((items[0].issue, items[0].title, items[0].tier, items[0].needs),
                         (141, "The plan of a milestone is a file", ["high"], []))
        # A heading of another level ends the work item: the text under it is free again.
        after = PLAN + "\n## Notes\n\nA free text after the work items.\n"
        self.assertEqual(cc.read_milestone(after)[2], [])
        # A blank line ends the line `Done:`: the text after it continues nothing.
        apart = PLAN.replace("  and the merge of the leader", "\n  and the merge of the leader")
        self.assertIn("line 10: #141: the line starts with no", "\n".join(cc.read_milestone(apart)[2]))

    def test_a_line_needs_names_a_thing_of_one_of_three_forms(self):
        """milestone-plan, check 4."""
        self.assertEqual(cc.read_milestone(PLAN)[1][1].needs, ["#141", "Charter 0.3.23", cc.NEED_WORD])
        for value in ("#99", "#142", "Charter 0.3", "Charter latest", "the first run", "#141 and #99", ""):
            with self.subTest(value=value):
                code, out = self.check(PLAN.replace("Needs: #141\n", f"Needs: {value}\n"))
                self.assertEqual(code, cc.FAIL, out)
                self.assertIn(f"#142: `Needs: {value}` names no other work item of this plan, no `Charter <version>`, and not "
                              "`the word of the leader`", out)

    def test_all_checks_each_plan_of_the_folder(self):
        """milestone-plan, check 5: with no folder and with a plan in the form, `all` passes; a fault names its file."""
        self.write("charter.toml", repo_with())
        contract = [cc.CMD_ALL, str(self.dir / "charter.toml"), f"--{cc.ARG_SOURCE}", str(ORG)]
        self.assertEqual(run(*contract)[0], cc.PASS)
        (self.dir / cc.MILESTONES_DIR).mkdir()
        self.write(f"{cc.MILESTONES_DIR}/iteration-4.md", PLAN)
        code, out = run(*contract)
        self.assertEqual(code, cc.PASS, out)
        self.write(f"{cc.MILESTONES_DIR}/iteration-5.md", PLAN.replace("Tier: high", "Tier: low"))
        code, out = run(*contract)
        self.assertEqual(code, cc.FAIL, out)
        self.assertIn("fail: milestones/iteration-5.md: #141: `Tier: low`", out)
        self.assertNotIn("iteration-4.md", out)

    def test_the_plan_is_in_the_high_tier_and_closed_to_a_run(self):
        """milestone-plan, check 6: the contract of this repo, and the paths that the setup step gives a new contract."""
        import tomllib
        import charter_setup as cs
        data = tomllib.loads((ROOT / "charter.toml").read_text())
        for paths in (data["tiers"]["high"]["paths"], data["boundary"]["no_write"], cs.HIGH_TIER_PATHS):
            self.assertTrue(cc.matches("milestones/iteration-4.md", paths), paths)
        template = (ROOT / "charter" / "templates" / "charter.toml").read_text()
        self.assertIn('"intents/**", "milestones/**"', next(line for line in template.splitlines() if line.startswith("no_write")))

    def test_the_documents_hold_the_form_and_the_approval(self):
        """milestone-plan, check 8."""
        contract = " ".join((ROOT / "docs" / "contract.md").read_text().split())
        for part in ("## The plan of a milestone", "`### #<issue> <title>`", "| `Done:` | one |", "| `Tier: high` | none or one |",
                     "| `Needs:` | none or more |", "`Charter <version>`, or `the word of the leader`",
                     "python3 charter/scripts/charter_check.py milestone milestones/<name>.md",
                     "No code reads the lines `Tier:` and `Needs:` yet",
                     "the change request of an intent still goes to the leader"):
            with self.subTest(part=part):
                self.assertIn(part, contract)
        rule = "The merge of the leader approves its work items; a change of the plan is its own change request."
        for path in (ROOT / "AGENTS.md", ROOT / "charter" / "templates" / "AGENTS.md"):
            self.assertIn(rule, " ".join(path.read_text().split()), path)
        self.assertIn("The leader approves the work items of a milestone with the merge of its plan",
                      (ROOT / "docs" / "product.md").read_text())
        self.assertIn("| C13 | The plan of a milestone is one file, `milestones/<name>.md`.", (ROOT / "docs" / "decisions.md").read_text())

    def test_both_manifests_name_the_version(self):
        """milestone-plan, check 10: 0.3.23 carries the check; a later version carries it too."""
        versions = [json.loads((ROOT / plugin / ".claude-plugin" / "plugin.json").read_text())["version"]
                    for plugin in ("charter", "charter-practices")]
        self.assertEqual(versions[0], versions[1])
        self.assertGreaterEqual(tuple(int(part) for part in versions[0].split(".")), (0, 3, 23))


class AbsentPaths(Temp):
    """A repo in a temporary folder: the sample contract with a set of absent paths, and the files of a case."""

    PATTERNS = '["docs/adr/**", "doc/arch/adr-*.md"]'

    def repo(self, absent: str | None, *files: str) -> tuple[int, str]:
        line = "" if absent is None else f"\nabsent = {absent}"
        self.write("charter.toml", repo_with(**{'code_paths = ["src/**"]': f'code_paths = ["src/**"]{line}'}))
        for name in files:
            path = self.dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# A file of the case\n")
        return run(cc.CMD_ALL, str(self.dir / "charter.toml"), f"--{cc.ARG_SOURCE}", str(ORG))

    def test_the_field_is_in_the_schema_and_in_the_contract_document(self):
        """reason-next-to-the-part, check 1."""
        field = cc.load_schema(cc.DEFAULT_SCHEMA)[cc.FIELD_ABSENT]
        self.assertEqual(field[cc.ATTR_KIND], "set")
        self.assertIn(f"| `{cc.FIELD_ABSENT}` | set |", (ROOT / "docs" / "contract.md").read_text())

    def test_a_file_under_an_absent_path_fails(self):
        """reason-next-to-the-part, check 2."""
        for name in ("docs/adr/adr-001-store.md", "docs/adr/2026/notes.txt", "doc/arch/adr-001.md"):
            with self.subTest(file=name):
                code, out = self.repo(self.PATTERNS, name)
                self.assertEqual(code, cc.FAIL, out)
                (self.dir / name).unlink()

    def test_the_failure_names_the_file_the_field_and_the_remedy(self):
        """reason-next-to-the-part, check 2: one failure for each file, with where the content goes."""
        code, out = self.repo(self.PATTERNS, "docs/adr/adr-001-store.md", "docs/adr/adr-002-model.md")
        self.assertEqual(code, cc.FAIL)
        for name in ("docs/adr/adr-001-store.md", "docs/adr/adr-002-model.md"):
            self.assertIn(f"fail: {name}: the contract forbids this path, a pattern of {cc.FIELD_ABSENT}.", out)
        self.assertIn("Move its content into a necessary document, at the part it concerns, and remove the file.", out)
        self.assertNotIn("all contract checks", out)

    def test_a_file_that_is_not_committed_fails(self):
        """reason-next-to-the-part, check 2: the check reads the folder, not the index of git."""
        self.assertEqual(self.repo(self.PATTERNS)[0], cc.PASS)
        git = ["git", "-C", str(self.dir), "-c", "user.name=test", "-c", "user.email=test@example.com"]
        for command in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "the contract"]):
            subprocess.run(git + command, check=True, capture_output=True)
        code, out = self.repo(self.PATTERNS, "docs/adr/adr-001-store.md")
        tracked = subprocess.run(git + ["ls-files", "docs"], check=True, capture_output=True, text=True).stdout
        self.assertEqual(tracked, "", "git does not track the new file")
        self.assertEqual(code, cc.FAIL, out)
        self.assertIn("fail: docs/adr/adr-001-store.md: the contract forbids this path", out)

    def test_no_file_under_a_pattern_passes(self):
        """reason-next-to-the-part, check 3: one file of decisions, a folder next to a pattern, and a folder
        with no file are not under a pattern."""
        (self.dir / "docs" / "adr").mkdir(parents=True)
        code, out = self.repo(self.PATTERNS, "docs/decisions.md", "docs/adrs/notes.md", "doc/arch/map.md",
                              "src/docs/adr/x.md")
        self.assertEqual(code, cc.PASS, out)

    def test_an_absent_or_empty_field_checks_nothing(self):
        """reason-next-to-the-part, check 3."""
        for absent in (None, "[]"):
            with self.subTest(absent=absent):
                code, out = self.repo(absent, "docs/adr/adr-001-store.md")
                self.assertEqual(code, cc.PASS, out)

    def test_the_decision_is_recorded(self):
        """reason-next-to-the-part, check 7: the rule is an accepted decision, G6, with its reason."""
        text = (ROOT / "docs" / "decisions.md").read_text()
        row = re.search(r"^\| G6 \| (.*) \| (.*) \| 2026-11-18 \|$", text, re.M)
        self.assertIsNotNone(row, "no row G6 dated 2026-11-18")
        self.assertIn("No separate file holds one decision", row.group(1))
        self.assertIn("becomes a check", row.group(1))
        self.assertIn("two homes", row.group(2))
        self.assertNotIn("G6", text.split("## P. Proposed", 1)[1])


if __name__ == "__main__":
    unittest.main()
