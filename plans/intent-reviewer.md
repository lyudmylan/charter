# Plan: a run of the intent reviewer ends with a report, or it fails (#70)

Intent: `intents/intent-reviewer.md`, checks 4 and 5. Accepted by the leader in the conversation on
2026-11-09, before the code.

## Decisions

The issue lists three options. This plan takes the first two: the run fails when no report was posted
or updated, and the prompt names the exact commands. The third, a change of the round count in the
collector, is not needed: the collector counts only the successful runs, so a failed run is no round.
The verdict stays in shadow mode: "no report" changes no verdict. The cause of the denials, found on the
first run of this change request with the new step and reproduced in a local run: the permission rules
refuse `gh pr comment --body "<report>"` when the report carries escaped backticks; a report on standard
input between two marker lines passes. The decisions go on the issue.

## Steps

1. `charter/templates/review-intents.yml` and `.github/workflows/review-intents.yml`:
   a. A step before the reviewer notes the time of the last update of the report comment on the change
      request, or `none`.
   b. The reviewer step gets an id.
   c. A step after it, with `if: always()`: it prints the denied commands from the execution file that
      the action outputs (`execution_file`), so that the cause is in the log; then it reads the report
      comment again and fails the run with the line "the reviewer posted no report" when there is no
      report comment or its time did not change.
   d. The prompt names the reading tools, says that a denied command is no reason to stop, and names the
      one command that posts the report, `gh pr comment <n> --body-file - <<'REPORT'`, and the two that
      update it: the id from `gh api repos/<repo>/issues/<n>/comments`, then
      `gh api -X PATCH repos/<repo>/issues/comments/<id> -F body=@- <<'REPORT'`. The report goes in through
      standard input, between two marker lines, with no escaping. No other command, no file. The allowed
      tools do not change.
2. `charter-practices/skills/review-loop/SKILL.md`, step 1: when the check `review-intents` fails with
   "the reviewer posted no report", rerun it once with `gh run rerun <run-id>`; a failed run is no
   round. The skill stays under 40 lines.
3. `tests/test_workflows.py`, class `ReviewIntents`: `test_a_run_without_a_report_fails` runs the shell
   of the guard step with `bash -e` and a `gh` on the path that answers with a given time: no report
   gives exit 1 and the line; the same time gives exit 1; a new time gives exit 0. It also asserts that
   the guard step has the same text in the template and in the workflow of this repo.
   `test_the_prompt_names_the_tools_and_the_posting_command` reads the prompt;
   `test_the_denied_commands_are_printed` runs the print of the denied commands on a sample execution file.
4. `intents/intent-reviewer.md`: one bullet in the scope (the decisions, the reason, the cause); checks 4 and 5 name the two tests; the manual checks become 6 and 7.
5. `docs/contract.md`, the review loop: a round is one successful run of the reviewer; a run that ends
   without a report fails, is no round, and prints the denied commands.
6. `charter/.claude-plugin/plugin.json` and `charter-practices/.claude-plugin/plugin.json`: 0.3.2. This
   is the last change request of the four (#68, #67, #71, #70), so one version carries all four. After
   the merge the leader pushes the tags `charter--v0.3.2` and `charter-practices--v0.3.2`. An adopter
   then names 0.3.2 in its contract for the fixes of #67 and #71, and copies the steps of #68 and #70
   into its own two workflows.
7. One change request, `Closes #70`, with the line `No document change: the product does not change;
   two steps of a workflow template and one line of a skill`.

## Files

`charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`,
`charter-practices/skills/review-loop/SKILL.md`, `tests/test_workflows.py`,
`intents/intent-reviewer.md`, `docs/contract.md`, the two manifests, and this file.

## Tests

Three new tests, step 3. The existing `Commands.test_the_four_commands_exist_and_the_manifests_agree`
covers step 6.
