"""Tests of the practice skills. Run: python3 -m unittest discover -s tests"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "charter-practices" / "skills"
MAX_LINES = 40
FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class TrackerSkill(unittest.TestCase):
    path = SKILLS / "tracker" / "SKILL.md"

    def test_size_and_description(self):
        """tracker-skill, check 1."""
        text = self.path.read_text()
        self.assertLess(len(text.splitlines()), MAX_LINES)
        front = FRONT_MATTER.match(text)
        self.assertIsNotNone(front, "no front matter")
        self.assertIn("name: tracker", front.group(1))
        description = front.group(1)
        self.assertIn("Use when", description)
        self.assertIn("Do not use", description)


if __name__ == "__main__":
    unittest.main()
