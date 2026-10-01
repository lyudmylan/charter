"""Tests of the workflow files, read as text: the standard library has no YAML parser.
Run: python3 -m unittest discover -s tests"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
READ_ONLY = {"Read", "Glob", "Grep"}
# A command that only reads or only posts the one comment.
ALLOWED_COMMANDS = re.compile(
    r"^Bash\((git diff|git log|gh issue view|gh issue list|gh pr view|gh pr comment):\*\)$|"
    r"^Bash\(gh api repos/\$\{\{ github\.repository \}\}/issues/\*/comments\*\)$|"
    r"^Bash\(gh api -X PATCH repos/\$\{\{ github\.repository \}\}/issues/comments/\*\)$"
)


class ReviewIntents(unittest.TestCase):
    text = (WORKFLOWS / "review-intents.yml").read_text()

    def test_paths_and_tools(self):
        """intent-reviewer, check 1."""
        self.assertIn('paths: ["intents/**"]', self.text)
        self.assertIn("on:\n  pull_request:", self.text)
        self.assertNotIn("pull_request_target", self.text)
        tools = re.search(r'--allowedTools "([^"]+)"', self.text)
        self.assertIsNotNone(tools, "no allowed tools")
        for tool in tools.group(1).split(","):
            with self.subTest(tool=tool):
                self.assertTrue(tool in READ_ONLY or ALLOWED_COMMANDS.match(tool), f"tool not read-only or comment: {tool}")
        for forbidden in ("Write", "Edit", "NotebookEdit", "WebFetch"):
            self.assertNotIn(forbidden, tools.group(1))
        self.assertIn("contents: read", self.text)


class Verdict(unittest.TestCase):
    text = (WORKFLOWS / "verdict.yml").read_text()

    def test_runs_after_the_tests_and_after_the_reviewer_and_counts_the_rounds(self):
        """review-loop, check 4."""
        self.assertIn("workflows: [tests, review-intents]", self.text)
        self.assertIn("--review-workflow review-intents.yml", self.text)


if __name__ == "__main__":
    unittest.main()
