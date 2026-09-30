"""Tests of the contract checker. Run: python3 -m unittest discover -s tests

Each test names the scenario file and the check that it implements, in its docstring.
"""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
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
        path = self.write("r.toml", repo_with(**{"refusals = 2": 'refusals = "two"'}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn("limits.refusals", out)

    def test_unknown_field_fails(self):
        """contract-checker, check 2."""
        path = self.write("r.toml", repo_with(**{"refusals = 2": "refusals = 2\nretries = 9"}))
        code, out = run(cc.CMD_VALIDATE, str(path))
        self.assertEqual(code, cc.FAIL)
        self.assertIn(cc.msg("unknown_field", name=path, field="limits.retries"), out)

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
        code, _ = self.check(repo_with(**{"refusals = 2": "refusals = 2\nacceptance_loop = 9"}))
        self.assertEqual(code, cc.PASS)

    def test_stricter_in_each_direction_passes(self):
        """contract-checker, check 4. Flag stays true; limit 2 < 3; count 2 > 1; set is a superset;
        choice leader > team_lead; text equal."""
        code, _ = self.check(repo_with(**{"refusals = 2": "refusals = 2\n[change]\nperson_approves_contract = true"}))
        self.assertEqual(code, cc.PASS)

    def test_weaker_in_each_direction_fails_and_names_the_rule(self):
        """contract-checker, check 5."""
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
                self.assertEqual(code, cc.FAIL)
                self.assertIn(f"weakens locked rule {rule}", out)

    def test_json_output_is_json_and_redacts_the_pattern_sets(self):
        """contract-checker, check 1: the effective contract merges the source and the repo."""
        code, out = run(cc.CMD_CHECK, str(REPO), f"--{cc.ARG_SOURCE}", str(ORG), f"--{cc.ARG_JSON}")
        self.assertEqual(code, cc.PASS)
        data = json.loads(out)
        effective = data[cc.JSON_KEY_EFFECTIVE]
        self.assertEqual(effective["limits.refusals"], 2)
        self.assertEqual(effective["limits.review_loop"], 3)
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
        code, out = self.instructions("Mail a@example.com [limits.refusals]\nThe Secret-Project [limits.refusals]\nsession_1 [limits.refusals]\n")
        self.assertEqual(code, cc.FAIL)
        self.assertIn(":1: matches a pattern of text.private_material_patterns", out)
        self.assertIn(":2: matches a pattern of text.project_name_patterns", out)
        self.assertIn(":3: matches a pattern of text.session_link_patterns", out)


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


if __name__ == "__main__":
    unittest.main()
