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


if __name__ == "__main__":
    unittest.main()
