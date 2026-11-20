# Intent: an agent that is not the author reviews the code of a change request

Work item: #95. Status: done. Approval: a person merges the change request that adds this file.

## Goal

Each change request that changes a file outside `intents/` and `plans/` gets a report from an agent that
is not its author, under the rules of the review loop.

## In scope

- The gap: an agent reviews the intents and the plans, and the person who merges reads the code. #66
  lets the verdict merge a change of a tier whose approver is `agent`. Without a reviewer of the code,
  such a change reaches the main branch after no review but the checks, and the contract says that the
  author of a change is not its reviewer.
- A workflow `review-code`, as a template and in this repo, in the form of the workflow
  `review-intents`. It runs on a change request that changes a file outside `intents/` and `plans/`. The
  reviewer reads files and runs no code of the change request. Each run posts a new comment that begins
  with `<!-- charter-code-review -->`, holds the line `Commit:` with the head commit, and ends with the
  line `Highest open severity: <level>`. The last step, a script, fails a run that added no such report.
  A change request from a fork gets no secret and no review.
- The checklist, a skill `change-review` of `charter-practices`. The name `code-review` is the name of a
  command of Claude Code. The reviewer reads the diff, the intent and the plan of the linked issue, and
  the results of the checks. It looks for: an acceptance check of the intent that the change does not
  meet; a test that does not test its check; a step of the plan that the change left out, and a changed
  file that the plan does not name; a broken contract between parts of the system; a document that the
  change made stale; a fault of correctness in the changed lines. Each finding has a severity of the four
  levels and a proposed correction. A report after the first starts from the diff since the commit of
  the report before it, as the reviewer of intents does.
- The depth follows `tiers.<tier>.review` of the tier of the change, which the workflow reads from the
  contract of the main branch. `light`: the changed lines and their tests. `deep`: also the code that
  calls the changed lines, and the security of the change.
- Built-in first. Claude Code has a review of its own for pull requests, the plugin `code-review` of
  the official marketplace, and the command `/security-review`. They report faults of correctness as
  inline comments. They do not know the intent and the plan, and they write no severity line that the
  verdict reads. So the checklist of Charter covers what the built-in does not, and `docs/contract.md`
  says that a repo can run the built-in review beside it.
- The facts collector gives the severity line of each report of the code review, oldest first, as the
  fact `code_review_reports`, apart from the reports of the intent review. The gate counts the round in
  the current loop, as for the intents (#61), and the verdict prints one line for the review of the code.
- A field of the contract, `review.code_blocks`, a flag. Without it, or with `false`, the reviewer is in
  its shadow period (decision C10): the verdict prints the state and blocks nothing. With `true`, the
  verdict is not ready while a finding at `review.threshold` or above is open, while a change of code
  has no report, and while the newest report names another commit than the head commit: a push after
  the last report is not reviewed yet. At the limit of the rounds the verdict stays not ready and says
  that a person decides. The leader ends the shadow period with a change of the contract. The contract
  of this repo and the template set the field to `false`.
- A command `charter-gate tier --contract C --changed FILE`: it prints the tier of a list of changed
  paths and the depth of its review. The workflow gives the reviewer the depth with it.
- The lines `Dropped finding: <reason>` and `False finding: <reason>` hold for the reviewer of the code
  too. The evidence record holds the reports and the round of the code review; the dropped and the false
  findings of both reviewers stay in the two lists that the record has, with their reasons.
- The verdict workflow, template and this repo: it runs again after a run of `review-code`, and it tells
  the facts collector that the repo has the reviewer of the code.
- The setup step writes the workflow. `AGENTS.md` and its template name the reviewer of the code in the
  section "Review and limits". `docs/contract.md`: the workflow, the field, the facts. `docs/product.md`,
  the Test row of the lifecycle map: an agent that is not the author reviews the code.
- Both manifests: the same version, 0.3.10 or later.

## Out of scope

Eval cases for the skill, which the issue lists: after the two defects of the eval cases, #79 and #80.
A reviewer for the product document and the architecture map: #98. A run that answers the findings: the
next step of #82; until then the author of the change answers, a person or an agent in a session. The
merge by the verdict: #66. A change request from a fork under the flag: it gets no report, so it is not
ready; its handling is a later issue. The sample that a person reads after the shadow period, and the
return of a tier to the approval of a person after a defect that escaped: later issues of #13. A run of
the code or of the tests by the reviewer: the workflow `tests` runs them, and the reviewer reads their
result.

## Acceptance checks

## Automatic checks

1. The setup step writes the workflow `review-code`. It runs on a change request with a file outside
   `intents/` and `plans/`, and not for a change of those two folders alone. A fork gets no review. The
   allowed tools read files and post one comment, and no step runs the code of the change request.
   test: `tests/test_workflows.py::CodeReviewer.test_the_setup_writes_the_workflow`
   test: `tests/test_workflows.py::CodeReviewer.test_the_workflow_runs_on_code_and_not_on_intents_alone`
   test: `tests/test_workflows.py::CodeReviewer.test_the_reviewer_reads_and_posts_and_runs_no_code`
2. The last step of the workflow fails when no new report with the marker was added, and when the newest
   one does not name the head commit. The step is run with a fake of the code host.
   test: `tests/test_workflows.py::CodeReviewer.test_the_run_fails_without_a_new_report_of_the_head_commit`
3. The workflow of this repo follows the template, but for the place of the skill and the address of
   Charter.
   test: `tests/test_workflows.py::CodeReviewer.test_the_workflow_of_this_repo_follows_the_template`
4. The skill `change-review` holds the checklist of the scope, the two depths, the four severities, the
   two lines that close a finding, the diff since the report before for a later report, and the form of
   the report with the marker, the line `Commit:`, and the last line.
   test: `tests/test_skills.py::ChangeReviewSkill.test_size_and_description`
   test: `tests/test_skills.py::ChangeReviewSkill.test_the_skill_holds_the_checklist_and_the_form`
5. The facts collector gives the severity of each report of the code review, oldest first, and keeps the
   reports of the two reviews apart.
   test: `tests/test_charter_facts_github.py::CodeReview.test_each_report_gives_its_severity_in_order`
   test: `tests/test_charter_facts_github.py::CodeReview.test_the_two_reviews_stay_apart`
6. The schema has the field `review.code_blocks` as a flag, and `docs/contract.md` lists it.
   test: `tests/test_charter_gate.py::CodeReview.test_the_field_is_in_the_schema_and_in_the_contract_document`
7. Without the flag, the verdict prints the state of the code review and stays ready with an open
   finding at the threshold.
   test: `tests/test_charter_gate.py::CodeReview.test_the_shadow_period_blocks_nothing`
8. With the flag, the verdict is not ready with an open finding at the threshold or above, and not ready
   when a change of code has no report. It is ready with an open finding below the threshold. At the
   limit of the rounds it is not ready and says that a person decides.
   test: `tests/test_charter_gate.py::CodeReview.test_an_open_finding_at_the_threshold_blocks`
   test: `tests/test_charter_gate.py::CodeReview.test_a_change_of_code_without_a_report_blocks`
   test: `tests/test_charter_gate.py::CodeReview.test_a_finding_below_the_threshold_does_not_block`
   test: `tests/test_charter_gate.py::CodeReview.test_the_limit_of_the_rounds_goes_to_a_person`
9. A change of intents and plans alone needs no report of the code review, with the flag too.
   test: `tests/test_charter_gate.py::CodeReview.test_a_change_of_intents_alone_needs_no_code_review`
10. The evidence record holds the reports and the round of the code review.
    test: `tests/test_charter_gate.py::CodeReview.test_the_record_holds_the_code_review`
11. The verdict workflow, template and this repo, runs after `review-code` and names that workflow to the
    facts collector.
    test: `tests/test_workflows.py::CodeReviewer.test_the_verdict_runs_after_the_code_review`
12. The instruction template and the `AGENTS.md` of this repo name the reviewer of the code, and the Test
    row of the lifecycle map in `docs/product.md` names it.
    test: `tests/test_setup.py::CodeReviewer.test_the_instructions_and_the_product_document_name_the_reviewer`
13. Both manifests name the same version, 0.3.10 or later.
    test: `tests/test_charter_gate.py::CodeReview.test_both_manifests_name_the_version`

14. With the flag, the verdict is not ready when the newest report names another commit than the head
    commit.
    test: `tests/test_charter_gate.py::CodeReview.test_a_report_of_an_older_commit_blocks`
15. `charter-gate tier` prints the tier of a list of changed paths and the depth of its review.
    test: `tests/test_charter_gate.py::CodeReview.test_the_tier_command_prints_the_tier_and_the_depth`

16. The workflow reads the depth from the contract of the base branch, not from the head: a change
    request that edits its own tiers gets the depth of the base. The step runs in a git repo.
    test: `tests/test_workflows.py::CodeReviewer.test_the_depth_comes_from_the_base_contract`
17. `docs/contract.md` holds the section "The reviewer of the code", with the workflow, the facts, the
    command `tier`, the flag, and the review of Claude Code beside it.
    test: `tests/test_charter_gate.py::CodeReview.test_the_contract_document_holds_the_section`

## Manual checks

18. On a change request of this repo that changes code, the workflow posts one report in the form of the
    skill, and the verdict prints the line of the code review. who: the leader. Not automatic: the check
    needs a model call and a runner.
19. The reading of the first three reports: are the findings real, and is the severity right.
    drafted by the agent, reviewed by an agent that is not the author, confirmed by the leader. Not
    automatic: a judgment on evidence, and it decides the end of the shadow period.
