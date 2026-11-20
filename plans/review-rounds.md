# Plan: a round of the review loop is a report in the current loop, and each report stays (#61)

Intent: `intents/review-rounds.md`, checks 1 to 10. Check 11 is manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.

## Steps

1. `charter/scripts/charter_facts_github.py`:
   - A function `review_reports(comments, author)`: the severity line of each comment of the reviewer
     that holds the marker, oldest first; a report without the line gives no value for its place.
   - `collect` gives the list to `build_facts`, which writes the fact `review_reports`. It keeps the
     facts `review_rounds`, as the number of the reports, and `review_highest_severity`, from the newest
     report. The request for the runs of the review workflow leaves; the option `--review-workflow` stays
     as the switch that the repo has a reviewer.
   - `review_rounds(runs, pr)` leaves with its test.
2. `charter/scripts/charter_gate.py`:
   - The fact `review_reports` is optional and validated: a list whose items are a severity or no value.
   - A function `current_round(reports, threshold)`: the number of the reports after the last report,
     before the newest one, whose severity is below the threshold. A report with no value counts as open.
   - `review_loop_state` takes the round from `current_round` when the fact is there, and from
     `review_rounds` when it is not. Its messages stay.
   - The evidence record holds `review_reports`, the number of the reports under `review_rounds`, as the
     fact does, and the round of the current loop under `review_round`. The gate reads the round from
     `current_round`; it reads `review_rounds` only in a facts file of an older collector.
3. `charter/templates/review-intents.yml` and `.github/workflows/review-intents.yml`:
   - The instructions: the report is a new comment at each run, posted with `gh pr comment`; the reviewer
     changes no earlier comment.
   - The list of allowed commands loses the `gh api -X PATCH` of a comment.
   - The step before the review notes the number of the comments with the marker; the last step fails
     when the number did not grow, with the message of today.
4. `charter-practices/skills/intent-review/SKILL.md`: the report is a new comment at each run.
   `charter-practices/skills/review-loop/SKILL.md`: the author reads the newest comment with the marker;
   right after a push `gh pr checks` can answer that no checks are reported, and the author asks again;
   the author reads the evidence record only after the verdict that follows the run of the reviewer, and
   the time in the record shows it; a round is a report in the current loop.
5. `charter/templates/intent.md`: the test line becomes `test: <the file of the test, and the name of the
   test in it>`.
6. `docs/contract.md`, section "The review loop": a round is a report of the reviewer in the current loop;
   a loop starts with the first report and again after a report below the threshold; each report stays
   on the change request as its own comment; a run that ends without a new report fails and is no round.
7. Both manifests: 0.3.9.
8. `intents/review-rounds.md`: `Status: done`.

## Files

- `charter/scripts/charter_facts_github.py`, `charter/scripts/charter_gate.py`
- `charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`
- `charter/templates/intent.md`
- `charter-practices/skills/intent-review/SKILL.md`, `charter-practices/skills/review-loop/SKILL.md`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/review-rounds.md`, `plans/review-rounds.md`
- `tests/test_charter_gate.py`, `tests/test_charter_facts_github.py`, `tests/test_workflows.py`,
  `tests/test_skills.py`, `tests/test_setup.py`

## Tests

A class `ReviewRounds` in `tests/test_charter_gate.py` (ten tests), `tests/test_workflows.py` (two),
`tests/test_skills.py` (one), and `tests/test_setup.py` (one), and a class `ReviewReports` in
`tests/test_charter_facts_github.py` (two), with the names that the intent gives. The step of the
workflow is run with `bash -e` and a fake `gh`, as `tests/test_setup.py` runs a step today. The tests
that count the rounds from the runs of a workflow change to the reports; a test whose name an intent that
is done names keeps its name.
