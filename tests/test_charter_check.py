"""Tests of the contract checker. Run: python3 -m unittest discover -s tests"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import charter_check  # noqa: E402

SAMPLES = ROOT / "tests" / "samples"
ORG = SAMPLES / "organization.toml"
REPO = SAMPLES / "repo.toml"


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = charter_check.main(list(argv))
    return code, out.getvalue()


def repo_with(**changes: str) -> str:
    """The sample repo contract with one or more lines replaced. Keys are the exact lines."""
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
        self.assertEqual(run("validate", str(ORG))[0], 0)
        self.assertEqual(run("validate", str(REPO))[0], 0)

    def test_missing_field_names_the_field(self):
        path = self.write("r.toml", repo_with(**{'version = "v1"\n': ""}))
        code, out = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("source.version", out)

    def test_wrong_type_names_the_field(self):
        path = self.write("r.toml", repo_with(**{"refusals = 2": 'refusals = "two"'}))
        code, out = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("limits.refusals", out)

    def test_unknown_field_fails(self):
        path = self.write("r.toml", repo_with(**{"refusals = 2": "refusals = 2\nretries = 9"}))
        code, out = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("unknown field limits.retries", out)

    def test_locked_field_without_value_fails(self):
        text = ORG.read_text().replace('code_host = "github"\n', "")
        path = self.write("o.toml", text)
        code, out = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("locked field without value: tools.code_host", out)


class Check(Temp):
    def check(self, repo_text: str) -> tuple[int, str]:
        path = self.write("r.toml", repo_text)
        return run("check", str(path), "--source", str(ORG))

    def test_valid_pair_passes_and_names_the_source(self):
        code, out = run("check", str(REPO), "--source", str(ORG))
        self.assertEqual(code, 0)
        self.assertIn("source: ", out)
        self.assertIn("pass:", out)

    def test_repo_adds_an_unlocked_rule(self):
        code, _ = self.check(repo_with(**{"refusals = 2": "refusals = 2\nacceptance_loop = 9"}))
        self.assertEqual(code, 0)

    def test_stricter_in_each_direction_passes(self):
        # flag stays true, limit 2 < 3, count 2 > 1, set is a superset, choice leader > team_lead, text equal
        code, _ = self.check(repo_with(**{"refusals = 2": "refusals = 2\n[change]\nperson_approves_contract = true"}))
        self.assertEqual(code, 0)

    def test_weaker_in_each_direction_fails_and_names_the_rule(self):
        cases = {
            "change.person_approves_contract": {"refusals = 2": "refusals = 2\n[change]\nperson_approves_contract = false"},
            "limits.refusals": {"refusals = 2": "refusals = 5"},
            "tiers.high.approvals": {"approvals = 2": "approvals = 0"},
            "documents.necessary": {'necessary = ["docs/product.md", "docs/architecture.md"]': 'necessary = ["docs/architecture.md"]'},
            "tiers.high.approver": {'approver = "leader"': 'approver = "engineer"'},
            "tools.code_host": {'code_host = "github"': 'code_host = "gitlab"'},
        }
        for rule, change in cases.items():
            with self.subTest(rule=rule):
                code, out = self.check(repo_with(**change))
                self.assertEqual(code, 1)
                self.assertIn(f"weakens locked rule {rule}", out)

    def test_json_output_has_effective_values(self):
        code, out = run("check", str(REPO), "--source", str(ORG), "--json")
        self.assertEqual(code, 0)
        self.assertIn('"limits.refusals": 2', out)
        self.assertIn('"limits.review_loop": 3', out)


class CannotRun(Temp):
    def test_no_file(self):
        code, out = run("validate", str(self.dir / "none.toml"))
        self.assertEqual(code, 2)
        self.assertIn("cannot run: no file", out)

    def test_not_toml(self):
        path = self.write("bad.toml", "schema = [unclosed")
        code, out = run("validate", str(path))
        self.assertEqual(code, 2)
        self.assertIn("cannot run: not TOML", out)

    def test_source_not_found(self):
        code, out = run("check", str(REPO), "--cache-dir", str(self.dir))
        self.assertEqual(code, 2)
        self.assertIn("cannot run: source not found: https://example.com/org/rules", out)
        self.assertIn("git clone", out)

    def make_cache(self) -> Path:
        cache = self.dir / "example.com" / "org" / "rules"
        cache.mkdir(parents=True)
        shutil.copy(ORG, cache / "organization.toml")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        for cmd in (["git", "init", "-q"], ["git", "add", "."], ["git", "commit", "-q", "-m", "rules"], ["git", "tag", "v1"]):
            subprocess.run(cmd, cwd=cache, check=True, env=env, capture_output=True)
        return cache

    def test_cache_resolves_and_names_the_version(self):
        self.make_cache()
        code, out = run("check", str(REPO), "--cache-dir", str(self.dir))
        self.assertEqual(code, 0, out)
        self.assertIn("source: https://example.com/org/rules version v1", out)

    def test_version_not_found(self):
        self.make_cache()
        path = self.write("r.toml", repo_with(**{'version = "v1"': 'version = "v9"'}))
        code, out = run("check", str(path), "--cache-dir", str(self.dir))
        self.assertEqual(code, 2)
        self.assertIn("cannot run: version not found: v9", out)

    @unittest.skipIf(os.name == "nt" or os.geteuid() == 0, "file permissions")
    def test_access_denied(self):
        path = self.write("r.toml", REPO.read_text())
        path.chmod(0)
        try:
            code, out = run("validate", str(path))
        finally:
            path.chmod(0o600)
        self.assertEqual(code, 2)
        self.assertIn("cannot run: access denied", out)


class Instructions(Temp):
    def instructions(self, text: str) -> tuple[int, str]:
        path = self.write("AGENTS.md", text)
        return run("instructions", str(path), "--contract", str(REPO), "--source", str(ORG))

    def test_known_identifiers_pass(self):
        code, out = self.instructions("Refusals stop at the limit. [limits.refusals]\nOne approver. [tiers.high.approver]\n")
        self.assertEqual(code, 0, out)
        self.assertIn("2 identifiers", out)

    def test_unknown_identifier_fails(self):
        code, out = self.instructions("Rule. [limits.retries]\n")
        self.assertEqual(code, 1)
        self.assertIn("[limits.retries] has no value", out)

    def test_no_identifiers_fails(self):
        code, out = self.instructions("No marks here.\n")
        self.assertEqual(code, 1)
        self.assertIn("no rule identifiers", out)

    def test_private_material_and_project_names_fail(self):
        code, out = self.instructions("Mail a@example.com [limits.refusals]\nThe Secret-Project [limits.refusals]\nsession_1 [limits.refusals]\n")
        self.assertEqual(code, 1)
        self.assertIn(":1: matches a pattern of text.private_material_patterns", out)
        self.assertIn(":2: matches a pattern of text.project_name_patterns", out)
        self.assertIn(":3: matches a pattern of text.session_link_patterns", out)


if __name__ == "__main__":
    unittest.main()
