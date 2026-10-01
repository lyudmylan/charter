# Intent: the review loop, with a severity, a stop rule, an orchestrator, and a visible round count

Work item: #52, and #51 for the lock of a limit. Status: done. Approval: a person merges the change request that adds this file.

## Goal

After a push, an agent answers the findings of the intent reviewer round after round, until the stop rule of
the contract ends the loop; the leader reads one line per change request, not the findings.

## In scope

- Severity. Each finding of the intent reviewer carries `blocker`, `high`, `medium`, or `low`, defined in
  the skill `intent-review`. The report ends with the fixed line `Highest open severity: <level>`, `none`
  when nothing is open. A finding that the change request text drops or marks as false is closed.
- Stop rule. The loop ends when the highest open severity is below `review.threshold` (a choice field of
  the contract; `medium` without a value), or when the rounds reach `limits.review_loop`. Then a person
  decides, with the merge.
- Orchestrator. The skill `review-loop` in `charter-practices`, for the author agent in the session of
  the author: wait for the reviewer, correct or drop each finding at the threshold or above, push, repeat
  by the stop rule, and report one line. It marks no finding as false: that is the leader's line.
- Visible count. The collector counts the completed runs of the reviewer workflow on the change request
  and reads the severity line of its report; the verdict prints the line
  `review loop: round <n> of <limit>, highest open severity <level>: ...` and the record keeps the two
  facts. The workflow `verdict` also starts when `review-intents` completes, so that the record carries
  the last round; its runs for one commit run one after the other. It reads the schema of the change
  request as data, so that a change request can add a field and use it. Shadow mode: the line changes no
  verdict.
- The lock of a limit (#51). A locked limit is exact: a repo cannot set a smaller or a larger number,
  because the number of rounds before a person steps in is a policy of the owner of the lock.

## Out of scope

An autonomous author in CI. The end of the shadow mode: the loop blocks nothing yet. A cost limit per
change request, on the roadmap as #53.

## Acceptance checks

## Automatic checks

1. The reviewer skill defines the four severities and ends its report with the fixed line.
   test: `tests/test_skills.py::IntentReviewSkill.test_severity_and_the_closing_line`
2. The orchestrator skill is under 40 lines, says when to use it and when not, and reads the stop rule
   from the two fields of the contract.
   test: `tests/test_skills.py::ReviewLoopSkill.test_size_and_description`
   test: `tests/test_skills.py::ReviewLoopSkill.test_the_stop_rule_names_the_two_fields`
3. The verdict prints the state of the loop: no review yet, open, the limit reached, or closed; and it
   refuses a wrong severity or count.
   test: `tests/test_charter_gate.py::ReviewLoop.test_no_review_yet`
   test: `tests/test_charter_gate.py::ReviewLoop.test_open_below_the_limit`
   test: `tests/test_charter_gate.py::ReviewLoop.test_limit_reached_a_person_decides`
   test: `tests/test_charter_gate.py::ReviewLoop.test_closed_below_the_threshold`
   test: `tests/test_charter_gate.py::ReviewLoop.test_a_report_without_the_line_still_shows_the_round`
   test: `tests/test_charter_gate.py::ReviewLoop.test_a_wrong_severity_or_count_cannot_run`
4. The collector reads the severity line from the report of the workflow account only, counts the rounds
   since the change request was opened, and writes the two facts only when a reviewer is named; the
   workflow `verdict` starts after the reviewer and names it.
   test: `tests/test_charter_facts_github.py::ReviewLoop.test_highest_severity_from_the_report_of_the_workflow_account`
   test: `tests/test_charter_facts_github.py::ReviewLoop.test_rounds_are_the_successful_runs_since_the_change_request_opened`
   test: `tests/test_charter_facts_github.py::ReviewLoop.test_facts_carry_the_loop_only_when_a_reviewer_is_named`
   test: `tests/test_workflows.py::Verdict.test_runs_after_the_tests_and_after_the_reviewer_and_counts_the_rounds`
5. A locked limit is exact: 2 and 4 under a lock of 3 both fail, with a message that names the rule.
   test: `tests/test_charter_check.py::Check.test_a_locked_limit_is_exact`

## Manual checks

6. On the change request that adds this file, the loop runs once by hand with the skill: the reviewer's
   report carries severities and the closing line, the author agent stops at the threshold and at the
   limit as the skill says, and the leader reads one line. who: the leader. Not automatic: the run needs
   the token of the plan on GitHub.
