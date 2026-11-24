#!/usr/bin/env python3
"""The product test of Charter. Run it from the root of the repo: python3 tests/product.py

It uses Charter as a user of the installed plugin does: through the commands of charter/bin, in a new repo
of a temporary folder. It needs no network and no secret: the organization source is the sample file of
tests/samples. It prints one line for each step and ends with 1 at the first step that does not behave as
expected, else with 0. It removes its temporary folder.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "charter" / "bin"
ORG = ROOT / "tests" / "samples" / "organization.toml"
CONTRACT = "charter.toml"
APP = "src/app.py"
APP_TEXT = 'print("the sample product works")\n'
PRODUCT_COMMAND = f"python3 {APP}"
OPEN_PATH = APP
CLOSED_PATH = ".github/workflows/tests.yml"
INTENT_TEMPLATE = "intents/_template.md"
SETUP_FLAGS = ["--repo", "sample", "--source", "https://example.com/org/rules", "--source-version", "v1",
               "--leader", "alice", "--code-path", "src/**", "--quality", PRODUCT_COMMAND,
               "--product", PRODUCT_COMMAND]
FACTS = {
    "change_request": 1,
    "linked_issues": [{"number": 1, "state": "open"}],
    "changed_files": [APP, "docs/product.md"],
    "reason_for_no_document_change": None,
    "unresolved_review_threads": 0,
    "checks": {"tests": "pass", "product": "pass", "contract": "pass"},
    "intents": [{"path": "intents/app.md", "plan": True, "removed": False}],
}
SOURCE = ["--source", str(ORG)]
# What an agent of a run wrote for its change request: a line that links the issue, then its text.
AGENT_LINK, AGENT_TEXT = "Fixes #1", "The sample change."
AGENT_ATTRIBUTION = "\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)"


def command(name: str, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN / name), *args], cwd=cwd, capture_output=True, text=True, check=False)


def file(path: Path) -> subprocess.CompletedProcess:
    """The text of a file that a step wrote, in the form of a result: code 1 and the path when it is absent."""
    if path.is_file():
        return subprocess.CompletedProcess([], 0, path.read_text(), "")
    return subprocess.CompletedProcess([], 1, "", f"no file: {path}")


def step(name: str, result: subprocess.CompletedProcess, code: int, *expected: str, absent: tuple = ()) -> bool:
    """One step: the exit code, the texts that the output holds, and the texts that it does not hold."""
    output = result.stdout + result.stderr
    good = (result.returncode == code and all(text in output for text in expected)
            and not any(text in output for text in absent))
    print(f"{'pass' if good else 'fail'}: {name}")
    if not good:
        print(f"  exit code {result.returncode}, expected {code}")
        print("\n".join(f"  {line}" for line in output.splitlines()))
    return good


def steps(repo: Path, work: Path) -> bool:
    (repo / "src").mkdir(parents=True)
    (repo / APP).write_text(APP_TEXT)
    if not step("setup", command("charter-setup", *SETUP_FLAGS, "--target", str(repo), cwd=repo), 0,
                f"written: {CONTRACT}"):
        return False
    if not step("template of an intent", file(repo / INTENT_TEMPLATE), 0, "Work item: #<number>. Approval:",
                absent=("Status:",)):
        return False
    if not step("contract checks", command("charter-check", "all", CONTRACT, *SOURCE, cwd=repo), 0,
                "all contract checks"):
        return False
    if not step("quality gate", command("charter-gate", "quality", "--contract", CONTRACT, "--repo-only", cwd=repo), 0,
                f"passed: {PRODUCT_COMMAND}"):
        return False
    if not step("settings of a run", command("charter-check", "boundary", CONTRACT, *SOURCE, cwd=repo), 0,
                '"autoAllowBashIfSandboxed": true', '"allowUnsandboxedCommands": false', '"attribution": {',
                '"commit": ""', '"pr": ""'):
        return False
    request = work / "change-request.md"
    request.write_text(f"{AGENT_LINK}\n\n{AGENT_TEXT}\n\n{AGENT_ATTRIBUTION}\n")
    if not step("text of a change request of a run", command("charter-run", "text", "--number", "1", "--request",
                                                             str(request), cwd=repo), 0,
                "Closes #1\n\n" + AGENT_TEXT, absent=(AGENT_LINK, "Generated with")):
        return False
    open_list = work / "open.txt"
    open_list.write_text(f"{OPEN_PATH}\n")
    if not step("boundary gate, an open path", command("charter-gate", "boundary", "--contract", CONTRACT, *SOURCE,
                                                       "--changed", str(open_list), cwd=repo), 0, "no changed path"):
        return False
    both = work / "both.txt"
    both.write_text(f"{OPEN_PATH}\n{CLOSED_PATH}\n")
    if not step("boundary gate, a closed path", command("charter-gate", "boundary", "--contract", CONTRACT, *SOURCE,
                                                        "--changed", str(both), cwd=repo), 1,
                f"fail: boundary: {CLOSED_PATH}: a run without a person cannot change this path",
                absent=(f"{OPEN_PATH}:",)):
        return False
    facts = work / "facts.json"
    facts.write_text(json.dumps(FACTS))
    return step("verdict", command("charter-gate", "verdict", "--facts", str(facts), "--contract", CONTRACT, *SOURCE,
                                   cwd=repo), 0, "ready", f"product test: passed: ['{PRODUCT_COMMAND}']",
                absent=("not ready",))


def main() -> int:
    work = Path(tempfile.mkdtemp())
    try:
        return 0 if steps(work / "repo", work) else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
