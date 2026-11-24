"""Each intent has acceptance checks, and each automatic check names a test that exists or a command
whose script exists. Intent: intent-files, check 1. Run: python3 -m unittest discover -s tests
"""

import importlib.util
import re
import shlex
import tempfile
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
STATUS_LINE = re.compile(r"^Work items?: .*\bStatus:", re.M)   # no-status-line: no intent holds it
PLAN_SUFFIX = ".plan.md"   # plan-tier: a plan at the old place, next to its intent, is not an intent
PLANS = ROOT / "plans"
TEMPLATE = ROOT / "charter" / "templates" / "intent.md"
# The intents that were built before a work item had a plan. The list is closed: a new intent has a plan
# when its code arrives.
BEFORE_THE_PLAN = frozenset((
    "charter-version-in-ci.md", "contract-checker.md", "contract.md", "default-lifecycle-map.md",
    "evidence-record.md", "gates.md", "install-from-the-marketplace.md", "intent-files.md",
    "product-document.md", "readme.md", "repository-instructions.md", "review-loop.md", "tracker-skill.md"))


def intent_files() -> list:
    return [p for p in sorted(INTENTS.glob("*.md")) if not p.name.endswith(PLAN_SUFFIX)]


def has_a_plan(intent: Path, plans: Path = PLANS) -> bool:
    """The plan of the intent exists, at the place of today or at the old place, next to the intent."""
    return (plans / intent.name).is_file() or intent.with_name(intent.stem + PLAN_SUFFIX).is_file()


def built(intent: Path, plans: Path = PLANS) -> bool:
    """The work item of the intent is built: its plan exists, or the intent is older than the plans. In
    this repo a plan reaches the main branch in the change request that holds its code, so no line of the
    intent says it. An intent that is not built yet may name a test that does not exist."""
    return intent.name in BEFORE_THE_PLAN or has_a_plan(intent, plans)


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


def problems_of(name: str, text: str, done: bool = True) -> list[str]:
    """The faults of one intent text. Empty when the intent is well formed and, for an intent whose work
    item is built, each named test and script exists."""
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
        self.assertTrue(intent_files(), "no intent files")

    def test_each_automatic_check_names_a_test_or_a_command_that_exists(self):
        for intent in intent_files():
            with self.subTest(intent=intent.name):
                self.assertEqual(problems_of(intent.name, intent.read_text(), built(intent)), [])


INTENT_WITH_A_FUTURE_TEST = """# Intent: x

Work item: #9. Approval: later.

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
    def test_a_plan_file_is_not_an_intent(self):
        """plan-before-the-code, check 3: a plan is not read as an intent. plan-tier: the plans live in
        `plans/`, and a plan at the old place, `intents/<part>.plan.md`, is skipped."""
        names = [p.name for p in intent_files()]
        self.assertNotIn("plan-tier.plan.md", names)
        self.assertIn("plan-tier.md", names)
        self.assertTrue((PLANS / "setup-step.md").is_file())

    def test_an_intent_that_is_not_built_needs_no_existing_test(self):
        """no-status-line, check 1: an intent whose work item is not built passes with a test that does not
        exist yet; the same intent fails when its work item is built."""
        self.assertEqual(problems_of("x", INTENT_WITH_A_FUTURE_TEST, done=False), [])
        done = problems_of("x", INTENT_WITH_A_FUTURE_TEST, done=True)
        self.assertEqual(len(done), 1)
        self.assertIn("missing test file", done[0])
        self.assertEqual(problems_of("x", INTENT_WITH_A_FUTURE_TEST), done)

    def test_the_plan_says_that_a_work_item_is_built(self):
        """no-status-line, check 2: an intent with a plan is built, at the place of today or at the old
        place, and then a named test that does not exist is a fault; the same intent with no plan is not
        built and has no fault. An intent that is older than the plans is built. The list of the older
        intents is closed: its size is fixed, and each name on it is an intent with no plan."""
        with tempfile.TemporaryDirectory() as folder:
            intents, plans = Path(folder) / "intents", Path(folder) / "plans"
            intents.mkdir()
            plans.mkdir()
            intent = intents / "an-intent-of-tomorrow.md"
            intent.write_text(INTENT_WITH_A_FUTURE_TEST)
            self.assertFalse(built(intent, plans))
            self.assertEqual(problems_of(intent.name, intent.read_text(), built(intent, plans)), [])
            (plans / intent.name).write_text("# Plan\n")
            self.assertTrue(built(intent, plans))
            merged_first = problems_of(intent.name, intent.read_text(), built(intent, plans))
            self.assertEqual(len(merged_first), 1)
            self.assertIn("missing test file", merged_first[0])
            (plans / intent.name).unlink()
            intent.with_name(intent.stem + PLAN_SUFFIX).write_text("# Plan\n")
            self.assertTrue(built(intent, plans))
        self.assertTrue(built(INTENTS / "no-status-line.md"))
        self.assertTrue(built(INTENTS / "plan-tier.md"))
        self.assertTrue(built(INTENTS / "contract.md"))
        self.assertEqual(len(BEFORE_THE_PLAN), 13)
        for name in sorted(BEFORE_THE_PLAN):
            with self.subTest(intent=name):
                self.assertTrue((INTENTS / name).is_file())
                self.assertFalse(has_a_plan(INTENTS / name))

    def test_no_intent_holds_a_status_line(self):
        """no-status-line, check 3: no intent of this repo and no line of the template holds a status."""
        for path in (*intent_files(), TEMPLATE):
            with self.subTest(file=path.name):
                self.assertIsNone(STATUS_LINE.search(path.read_text()))
        self.assertIn("Work item: #<number>. Approval: a person merges", TEMPLATE.read_text())


class PlanPlace(unittest.TestCase):
    def test_the_plans_of_this_repo_are_in_the_plans_folder(self):
        """plan-tier, check 8: the eight plans that moved are in `plans/`, each plan there belongs to an
        intent, and `intents/` holds no plan but the one of this work item."""
        plans = sorted(PLANS.glob("**/*.md"))
        names = {plan.name for plan in plans}
        for moved in ("boundary-gate-reads-any-path.md", "boundary-of-a-run.md", "code-host.md",
                      "drafted-reading-review.md", "intent-reviewer.md", "plan-before-the-code.md",
                      "reason-next-to-the-part.md", "setup-step.md"):
            self.assertIn(moved, names)
        for plan in plans:
            with self.subTest(plan=plan.name):
                self.assertTrue((INTENTS / plan.relative_to(PLANS)).is_file(), plan)
        self.assertEqual([p.name for p in INTENTS.glob("**/*" + PLAN_SUFFIX)], ["plan-tier.plan.md"])


if __name__ == "__main__":
    unittest.main()
