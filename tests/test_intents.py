"""Each intent has acceptance checks, and each automatic check names a test that exists or a command
whose script exists. Intent: intent-files, check 1. Run: python3 -m unittest discover -s tests
"""

import importlib.util
import re
import shlex
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTENTS = ROOT / "intents"
TEST_REF = re.compile(r"test: `([^`:]+)::([A-Za-z_][A-Za-z0-9_]*)\.([a-z_][a-z0-9_]*)`")
COMMAND_REF = re.compile(r"command: `([^`]+)`")
CHECK_LINE = re.compile(r"^(\d+)\. ")
PYTHON = "python3"
HEADING_AUTOMATIC = "## Automatic checks"
HEADING_MANUAL = "## Manual checks"
STATUS_LINE = re.compile(r"^Work item: #\d+\. Status: (planned|done)\.", re.M)
STATUS_DONE = "done"


def status_of(text: str) -> str:
    """planned: the tests may not exist yet. done, the default: they must exist."""
    m = STATUS_LINE.search(text)
    return m.group(1) if m else STATUS_DONE


def check_blocks(section: str) -> list[tuple[str, str]]:
    """Split a section into (number, text) blocks, one for each numbered check."""
    blocks: list[tuple[str, str]] = []
    for line in section.splitlines():
        m = CHECK_LINE.match(line)
        if m:
            blocks.append((m.group(1), line))
        elif blocks:
            blocks[-1] = (blocks[-1][0], blocks[-1][1] + "\n" + line)
    return blocks


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problems_of(name: str, text: str) -> list[str]:
    """The faults of one intent text. Empty when the intent is well formed and, for a done intent,
    each named test and script exists."""
    problems: list[str] = []
    for heading in ("## Goal", "## In scope", "## Out of scope", "## Acceptance checks", HEADING_AUTOMATIC, HEADING_MANUAL):
        if heading not in text:
            problems.append(f"{name}: no heading {heading!r}")
    if problems:
        return problems
    automatic = text.split(HEADING_AUTOMATIC, 1)[1].split(HEADING_MANUAL, 1)[0]
    blocks = check_blocks(automatic)
    if not blocks:
        problems.append(f"{name}: no automatic checks")
    done = status_of(text) == STATUS_DONE
    for number, block in blocks:
        refs = TEST_REF.findall(block)
        commands = COMMAND_REF.findall(block)
        if not (refs or commands):
            problems.append(f"{name}: check {number} names no test and no command")
        if not done:
            continue
        for file, cls, method in refs:
            path = ROOT / file
            if not path.is_file():
                problems.append(f"{name}: check {number}: missing test file {file}")
                continue
            module = load_module(path)
            if not hasattr(getattr(module, cls, None), method):
                problems.append(f"{name}: check {number}: missing test {file}::{cls}.{method}")
        for command in commands:
            words = shlex.split(command)
            if words and words[0] == PYTHON and len(words) > 1 and words[1].endswith(".py"):
                if not (ROOT / words[1]).is_file():
                    problems.append(f"{name}: check {number}: missing script {words[1]}")
    return problems


class Intents(unittest.TestCase):
    def test_intent_files_exist(self):
        self.assertTrue(list(INTENTS.glob("*.md")), "no intent files")

    def test_each_automatic_check_names_a_test_or_a_command_that_exists(self):
        for intent in sorted(INTENTS.glob("*.md")):
            with self.subTest(intent=intent.name):
                self.assertEqual(problems_of(intent.name, intent.read_text()), [])


INTENT_WITH_A_FUTURE_TEST = """# Intent: x

Work item: #9. Status: {status}. Approval: later.

## Goal

A goal.

## In scope

A scope.

## Out of scope

Nothing more.

## Acceptance checks

## Automatic checks

1. A check. test: `tests/test_not_written_yet.py::Future.test_one`

## Manual checks

None.
"""


class PlannedIntents(unittest.TestCase):
    def test_planned_intents_need_no_existing_test(self):
        """planned-intents, check 1: a planned intent with a test that does not exist yet passes; a done one fails."""
        self.assertEqual(problems_of("x", INTENT_WITH_A_FUTURE_TEST.format(status="planned")), [])
        done = problems_of("x", INTENT_WITH_A_FUTURE_TEST.format(status="done"))
        self.assertEqual(len(done), 1)
        self.assertIn("missing test file", done[0])
        self.assertEqual(status_of("# Intent: x\n\nWork item: #9. Approved by a person.\n"), STATUS_DONE)


if __name__ == "__main__":
    unittest.main()
