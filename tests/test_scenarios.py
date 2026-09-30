"""Each scenario file has checks, and each automatic check names a test that exists or a command
whose script exists. Scenario: scenario-files, check 1. Run: python3 -m unittest discover -s tests
"""

import importlib.util
import re
import shlex
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "tests" / "scenarios"
TEST_REF = re.compile(r"test: `([^`:]+)::([A-Za-z_][A-Za-z0-9_]*)\.([a-z_][a-z0-9_]*)`")
COMMAND_REF = re.compile(r"command: `([^`]+)`")
CHECK_LINE = re.compile(r"^(\d+)\. ")
PYTHON = "python3"
HEADING_AUTOMATIC = "## Automatic checks"
HEADING_MANUAL = "## Manual checks"


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


class Scenarios(unittest.TestCase):
    def test_scenario_files_exist(self):
        self.assertTrue(list(SCENARIOS.glob("*.md")), "no scenario files")

    def test_each_automatic_check_names_a_test_or_a_command_that_exists(self):
        for scenario in sorted(SCENARIOS.glob("*.md")):
            text = scenario.read_text()
            self.assertIn(HEADING_AUTOMATIC, text, f"{scenario.name}: no heading {HEADING_AUTOMATIC!r}")
            self.assertIn(HEADING_MANUAL, text, f"{scenario.name}: no heading {HEADING_MANUAL!r}")
            automatic = text.split(HEADING_AUTOMATIC, 1)[1].split(HEADING_MANUAL, 1)[0]
            blocks = check_blocks(automatic)
            self.assertTrue(blocks, f"{scenario.name}: no automatic checks")
            for number, block in blocks:
                refs = TEST_REF.findall(block)
                commands = COMMAND_REF.findall(block)
                with self.subTest(scenario=scenario.name, check=number):
                    self.assertTrue(refs or commands, f"{scenario.name}: check {number} names no test and no command")
                for file, cls, method in refs:
                    with self.subTest(scenario=scenario.name, check=number, test=f"{cls}.{method}"):
                        module = load_module(ROOT / file)
                        self.assertTrue(hasattr(getattr(module, cls), method), f"missing test {file}::{cls}.{method}")
                for command in commands:
                    words = shlex.split(command)
                    if words and words[0] == PYTHON and len(words) > 1 and words[1].endswith(".py"):
                        with self.subTest(scenario=scenario.name, check=number, command=command):
                            self.assertTrue((ROOT / words[1]).is_file(), f"missing script {words[1]}")


if __name__ == "__main__":
    unittest.main()
