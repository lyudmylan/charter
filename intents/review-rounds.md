# Intent: a round of the review loop is a report in the current loop, and each report stays on the change request

Work item: #61. Approval: a person merges the change request that adds this file.

## Goal

The count of the review rounds follows the reports of the reviewer, and each report stays readable on
the change request.

## In scope

- The gap, in three cases. A push of one line after the loop closed starts a run of the reviewer, and
  the verdict prints `round 5 of 3` while the loop is closed (#57). With the intent, the plan, and the
  code of a work item in one change request, the intent uses the three rounds before the plan exists; in
  an adopter on 2026-11-20 the first review of a plan was round 4 of 3, and its medium finding was right.
  And the reviewer replaces its one comment at each run, so the report of an earlier round is lost.
- The reviewer posts a new comment for each run and changes no earlier one. The workflow
  `review-intents`, in the template and in this repo, says so; its list of allowed commands loses the
  update of a comment; its last step fails the run when the count of the reports did not grow.
- The facts collector gives the severity line of each report, oldest first, as the fact
  `review_reports`. It asks the code host for no list of workflow runs.
- The gate counts. A loop starts with the first report, and again with the first report after one whose
  highest open severity is below `review.threshold`. The round is the number of the reports in the
  current loop. A report without a severity line counts as open. The line of the verdict and its three
  states stay as they are: open, closed, or at the limit.
- A facts file without `review_reports`, from an older collector, is read as before, by `review_rounds`.
- The evidence record holds the reports, their number under `review_rounds`, as the fact does, and the
  round of the current loop under its own name, `review_round`.
- The skill `review-loop`: the author reads the newest report; right after a push the checks are not
  listed yet, so the skill says to ask again; and the author reads the evidence record only after the
  verdict that follows the run of the reviewer, which the time in the record shows.
- The template of an intent names a test without the form of one language.
- `docs/contract.md`, section "The review loop": what a round is, and that each report stays.
- Both manifests: the same version, 0.3.9 or later.

## Out of scope

What the reviewer says on the change since its last report: #86, in the same change request. A count
for each reviewed document of a change request. A verdict that blocks on an open finding: the loop
changes no verdict in this version. The reviewer of the code: #95; it takes this count.

## Acceptance checks

## Automatic checks

1. The gate counts the round inside the current loop: three open reports are round 3; a report after a
   closed one is round 1; a push after a closed loop that ends with a closed report stays closed.
   test: `tests/test_charter_gate.py::ReviewRounds.test_the_round_is_the_number_of_reports_in_the_current_loop`
   test: `tests/test_charter_gate.py::ReviewRounds.test_a_report_after_a_closed_one_starts_a_new_loop`
2. The case of the adopter: three reports that end with a closed one, then a report with a medium finding,
   give `round 1 of 3` and an open loop. The case of #57: reports after a closed loop that stay closed
   never print a round above the limit.
   test: `tests/test_charter_gate.py::ReviewRounds.test_the_first_review_of_a_plan_is_round_one`
   test: `tests/test_charter_gate.py::ReviewRounds.test_a_push_after_a_closed_loop_is_no_round_above_the_limit`
3. Three open reports in one loop give the state of the limit, and a report without a severity line counts
   as open.
   test: `tests/test_charter_gate.py::ReviewRounds.test_three_open_reports_reach_the_limit`
   test: `tests/test_charter_gate.py::ReviewRounds.test_a_report_without_a_severity_line_counts_as_open`
4. A facts file without `review_reports` is read by `review_rounds`, as before.
   test: `tests/test_charter_gate.py::ReviewRounds.test_older_facts_are_read_as_before`
5. The facts collector gives the severity of each report of the reviewer, oldest first, reads no comment
   of another author, and asks for no list of workflow runs.
   test: `tests/test_charter_facts_github.py::ReviewReports.test_each_report_gives_its_severity_in_order`
   test: `tests/test_charter_facts_github.py::ReviewReports.test_the_collector_lists_no_workflow_runs`
6. The workflow `review-intents`, in the template and in this repo, tells the reviewer to post a new
   comment, allows no update of a comment, and its last step fails when the count of the reports did not
   grow. The step is run with a fake of the code host for both results.
   test: `tests/test_workflows.py::ReviewRounds.test_the_reviewer_posts_a_new_comment_and_updates_none`
   test: `tests/test_workflows.py::ReviewRounds.test_the_run_fails_when_no_report_was_added`
7. The evidence record holds the reports, their number, and the round of the current loop under
   `review_round`.
   test: `tests/test_charter_gate.py::ReviewRounds.test_the_record_holds_the_reports_and_the_round`
8. The skill `review-loop` names the newest report, the wait after a push, and the verdict that follows
   the reviewer. The template of an intent names no file of one language in its test line.
   test: `tests/test_skills.py::ReviewRounds.test_the_author_skill_names_the_wait_and_the_newest_report`
   test: `tests/test_setup.py::ReviewRounds.test_the_intent_template_names_no_language`
9. `docs/contract.md` says what a round is and that each report stays.
   test: `tests/test_charter_gate.py::ReviewRounds.test_the_contract_document_says_what_a_round_is`
10. Both manifests name the same version, 0.3.9 or later.
    test: `tests/test_charter_gate.py::ReviewRounds.test_both_manifests_name_the_version`

## Manual checks

11. On a change request of this repo with two pushes, two reports of the reviewer stay on the change
    request, and the verdict prints the round of the current loop. who: the leader. Not automatic: the
    check needs a model call and a runner.
