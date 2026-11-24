# Intent: the intent reviewer says what changed since its last report, from the diff

Work item: #86. Approval: a person merges the change request that adds this file.

## Goal

A report of the intent reviewer names the commit that it covers, and a report after the first one states
what changed since the report before it, from the diff of the commits.

## In scope

- The gap: on 2026-11-18, in the change request #85, a commit changed 12 lines of an intent after round
  2. The report of round 3 said that the commit changed no intent. The run had read the right commit. A
  change of an approved text passed a round that did not see it.
- Each report holds one line, `Commit: <the full identifier of the head commit>`. The workflow gives the
  identifier to the reviewer, and its last step fails the run when the newest report does not hold that
  line. A script checks this, not the reviewer.
- In a run after the first report, the reviewer reads the `Commit:` line of the newest earlier report and
  runs `git diff <that commit>..<the head commit> -- intents/ plans/`. The second end is the head commit
  of the change request, not the commit that the code host makes for the merge, which also holds the
  changes of the main branch. Its report has a section "Changed since the
  last report" that lists each changed file with its changed lines in a few words, or says that no file
  of the two folders changed. The findings of the round start from that diff.
- The skill `intent-review` holds the two rules and the place of the section in the report. The workflow
  `review-intents`, in the template and in this repo, gives the command and allows it.
- Both manifests: the version of #61 (see `intents/review-rounds.md`).

## Out of scope

The count of the rounds and the new comment for each run: #61, in the same change request; this intent
needs that each report stays. A check by a script that the section agrees with the diff. The reviewer of
the code: #95.

## Acceptance checks

## Automatic checks

1. The workflow, in the template and in this repo, gives the reviewer the identifier of the head commit,
   and the skill asks for the line `Commit:` in each report.
   test: `tests/test_workflows.py::ReviewerDiff.test_the_report_names_its_commit`
2. The last step of the workflow fails when the newest report holds no line with the head commit, and
   passes when it holds it. The step is run with a fake of the code host.
   test: `tests/test_workflows.py::ReviewerDiff.test_the_run_fails_when_the_report_names_another_commit`
3. The instructions of the workflow and the skill tell the reviewer, after the first report, to read the
   commit of the newest earlier report, to run the diff of `intents/` and `plans/` from it to the head,
   and to write the section "Changed since the last report". The list of allowed commands covers the
   diff.
   test: `tests/test_workflows.py::ReviewerDiff.test_a_later_round_starts_from_the_diff`
   test: `tests/test_skills.py::ReviewerDiff.test_the_skill_holds_the_section_and_the_commit_line`

## Manual checks

4. In the second round of a change request of this repo, the report holds the section with the changed
   lines of that push. drafted by the agent, reviewed by an agent that is not the author, confirmed by
   the leader. Not automatic: a judgment on a report of a model.
