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


class TrackerSkill(unittest.TestCase):
    def test_size_and_description(self):
        """tracker-skill, check 1."""
        check_skill(self, "tracker")


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


if __name__ == "__main__":
    unittest.main()
