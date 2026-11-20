# Plan: the intent reviewer says what changed since its last report, from the diff (#86)

Intent: `intents/reviewer-reads-the-diff-of-a-round.md`, checks 1 to 3. Check 4 is manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan builds on the plan of #61, in the same change request: each report is its own comment.

## Steps

1. `charter/templates/review-intents.yml` and `.github/workflows/review-intents.yml`:
   - The instructions give the identifier of the head commit, `${{ github.event.pull_request.head.sha }}`,
     and ask for one line `Commit: <that identifier>` in the report.
   - The instructions for a run after the first report: read the line `Commit:` of the newest earlier
     report, run `git diff <that commit>..<the head commit> -- intents/ plans/`, write the section "Changed since the
     last report", and start the findings of the round from that diff. `git diff` is in the list of
     allowed commands already.
   - The last step also fails when the newest comment with the marker holds no line `Commit:` with the
     head commit. The message says which commit the step looked for.
2. `charter-practices/skills/intent-review/SKILL.md`, section "The report": the line `Commit:`, and the
   section "Changed since the last report" for each report after the first: each changed file of
   `intents/` and `plans/` with its changed lines in a few words, or the sentence that no file of the two
   folders changed.
3. `intents/reviewer-reads-the-diff-of-a-round.md`: `Status: done`.

## Files

- `charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`
- `charter-practices/skills/intent-review/SKILL.md`
- `intents/reviewer-reads-the-diff-of-a-round.md`, `plans/reviewer-reads-the-diff-of-a-round.md`
- `tests/test_workflows.py`, `tests/test_skills.py`

## Tests

A class `ReviewerDiff` in `tests/test_workflows.py` (three tests) and in `tests/test_skills.py` (one), with
the names that the intent gives. The last step of the workflow is run with `bash -e` and a fake `gh` for
a report with the head commit, and for a report with another commit.
