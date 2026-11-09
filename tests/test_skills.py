"""Tests of the practice skills. Run: python3 -m unittest discover -s tests"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "charter-practices" / "skills"
MAX_LINES = 40
FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def check_skill(test: unittest.TestCase, name: str) -> None:
    text = (SKILLS / name / "SKILL.md").read_text()
    test.assertLess(len(text.splitlines()), MAX_LINES)
    front = FRONT_MATTER.match(text)
    test.assertIsNotNone(front, "no front matter")
    test.assertIn(f"name: {name}", front.group(1))
    test.assertIn("Use when", front.group(1))
    test.assertIn("Do not use", front.group(1))


CLAUSE = "drafted by the agent, reviewed by an agent that is not the author, confirmed by <the role>"


def one_line(text: str) -> str:
    return " ".join(text.split())


class TrackerSkill(unittest.TestCase):
    def test_size_and_description(self):
        """tracker-skill, check 1."""
        check_skill(self, "tracker")

    def test_the_two_link_forms_are_named(self):
        """code-host, check 3 (#76): the instruction file, its template, the tracker skill, and the contract
        document name both link forms."""
        for path in (ROOT / "AGENTS.md", ROOT / "charter" / "templates" / "AGENTS.md", SKILLS / "tracker" / "SKILL.md",
                     ROOT / "docs" / "contract.md"):
            with self.subTest(file=str(path.relative_to(ROOT))):
                text = path.read_text()
                self.assertIn("`Closes #N`", text)
                self.assertIn("`Part of #N`", text)

    def test_the_clause_of_a_drafted_reading(self):
        """drafted-reading-review, check 2: the tracker skill and the intent template carry the clause, the
        intent reviewer asks for it, and the skills stay under the size limit."""
        files = {"tracker": SKILLS / "tracker" / "SKILL.md", "intent template": ROOT / "charter" / "templates" / "intent.md",
                 "intent-review": SKILLS / "intent-review" / "SKILL.md"}
        for name, path in files.items():
            with self.subTest(file=name):
                self.assertIn(CLAUSE, one_line(path.read_text()))
        self.assertIn("`evidence-review`", files["tracker"].read_text())
        for name in ("tracker", "intent-review", "review-loop", "evidence-review"):
            with self.subTest(skill=name):
                check_skill(self, name)


class IntentReviewSkill(unittest.TestCase):
    def test_size_and_description(self):
        """intent-reviewer, check 2."""
        check_skill(self, "intent-review")

    def test_severity_and_the_closing_line(self):
        """review-loop, check 1: each severity is defined, and the report ends with the fixed line."""
        text = (SKILLS / "intent-review" / "SKILL.md").read_text()
        for level in ("blocker", "high", "medium", "low"):
            self.assertIn(f"`{level}`", text)
        self.assertIn("`Highest open severity: blocker|high|medium|low|none`", text)
        self.assertIn("Dropped finding:", text)


class ReviewLoopSkill(unittest.TestCase):
    def test_size_and_description(self):
        """review-loop, check 2."""
        check_skill(self, "review-loop")

    def test_the_stop_rule_names_the_two_fields(self):
        """review-loop, check 2: the skill reads the threshold and the limit from the contract."""
        text = (SKILLS / "review-loop" / "SKILL.md").read_text()
        self.assertIn("`review.threshold`", text)
        self.assertIn("`limits.review_loop`", text)
        self.assertIn("Do not push a round beyond the limit", text)


class EvidenceReviewSkill(unittest.TestCase):
    def test_size_and_description(self):
        """drafted-reading-review, check 1."""
        check_skill(self, "evidence-review")

    def test_the_two_passes_and_the_list(self):
        """drafted-reading-review, check 1: the blind pass, the adversarial pass, a severity per finding, the list
        of disagreements with the evidence on each side, and the one-word confirmation."""
        text = (SKILLS / "evidence-review" / "SKILL.md").read_text()
        for part in ("Blind pass", "Adversarial pass", "`blocker`, `high`, `medium`, or `low`", "## Disagreements",
                     "evidence on each side", "confirms the rest in one word"):
            with self.subTest(part=part):
                self.assertIn(part, text)


class DraftedReadingRule(unittest.TestCase):
    def test_the_decision_is_recorded(self):
        """drafted-reading-review, check 3: the rule is an accepted decision, C11, with its reason."""
        text = (ROOT / "docs" / "decisions.md").read_text()
        row = re.search(r"^\| C11 \| (.*) \| (.*) \| 2026-11-03 \|$", text, re.M)
        self.assertIsNotNone(row, "no row C11 dated 2026-11-03")
        self.assertIn("disagreements", row.group(1))
        self.assertIn("B5", row.group(2))
        self.assertNotIn("C11", text.split("## P. Proposed", 1)[1])


if __name__ == "__main__":
    unittest.main()
