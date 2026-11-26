# Intent: the intent reviewer blocks only on a failed question of a closed list

Work item: #153. Approval: a person merges the change request that adds this file.

## Goal

The intent reviewer answers a closed list of questions for each intent, only a question of the list that
does not hold blocks, and code gives the severity.

## In scope

- The skill `intent-review`. Its checklist becomes eight questions, Q1 to Q8, each with its severity in the
  list. An answer is `holds`, `does not hold` with the sentence that fails, `unknown`, or `closed` for a
  finding that a line `Dropped finding:` or `False finding:` answers. A question that does not hold is a
  finding. The reviewer chooses no severity.
- Each other thing that the reviewer sees is a note of severity `low`, and it blocks nothing. The leader
  decided two kinds on 2026-11-26: a check that proves less than its full sentence, in a detail or a rare
  case, is a note; a fact or a list in two places is a note. The skill names the other kinds. Five of them
  are a choice of the author that the leader confirms with this change request: a contradiction that shows
  only in a rare case or a rare order of events; one name for two things; a sentence that names a proof
  that cannot fail, when another check tries that behaviour; a part of an item of the issue that the intent
  narrows; and, in a later round after a report with no answers, a sentence that did not change.
- The form of the report: a heading for each intent, and under it one line for each question. The report
  answers for each intent that the change adds, for the intent of each plan that it adds or changes, and
  for each intent whose goal, scope, or checks it changes. A later round answers again each question that
  did not hold or was unknown, and each question for a changed line, and keeps each other answer.
- The script `charter/scripts/charter_review.py`, with the command `charter-review` of the plugin. It holds
  the number and the severity of each question. It reads the answers of a report, it says why a report is
  not complete, and it writes the line of the highest open severity: the highest severity of a question
  that does not hold; `low` with a note or an answer `unknown` and no such question; `none` with neither.
- Code answers the part of Q3 that code can answer: each automatic check names a test or a command, and
  each named test file is in the repo when the plan of the intent is.
- The workflow `review-intents` and its template. A step before the reviewer gives it the answers of code.
  The step that posts the report closes it first: it adds each answer of code that does not hold and writes
  the severity line. A report that lacks an answer is not posted, so the run fails and is no round. The two
  steps run the scripts of the fetched Charter, and in this repo the scripts of the base branch.
- The verdict reads the severity line as before, with no change of its code: code wrote that line from
  the answers.
- The test set of the intent reviewer. Its command closes each report as the workflow does, and it looks
  for the subject of a case in the answers that do not hold. A report that lacks an answer is "form not
  read". A report of before this change is graded as before.
- The 8 contested cases of the test set get their answer from the rule of this intent, and the field
  `contested` leaves them: `blocks` when a finding of their reports is right in fact and is a question
  that does not hold, else `passes`. A `blocks` case whose finding is now a note becomes `passes`. The set
  then holds 14 cases with the answer `blocks` and 11 with the answer `passes`.
- The skill `review-loop`, `AGENTS.md` and its template, `docs/contract.md`, `docs/product.md`, `README.md`,
  and both manifests: 0.3.22.

## Out of scope

- The check of an intent against the "done" line of its work item: #142. It adds one question to the list.
- The reviewer of the code. It gets the form after its own test set, #147.
- Two runs of the reviewer for each change, with a block only when both agree.
- A change to the cases of the test set beyond their answer and their subject.
- An answer of code to another question than Q3. The issue asks for each question that code can answer;
  the form of a manual check and of an issue differs between repos, so code reads the names of Q3 only.

## Acceptance checks

## Automatic checks

1. The skill holds eight questions, each with the severity that the code holds; each severity is at the
   default threshold or above, and a note is below it; the skill names the four answers, the notes, the
   form of the report, and the rule of a later round.
   test: `tests/test_review.py::TheList.test_the_skill_holds_each_question_with_the_severity_of_the_code`
2. Code reads the line of an answer with and without the marks of a list and of emphasis, and the text of
   an answer up to the next answer.
   test: `tests/test_review.py::Answers.test_the_forms_of_an_answer_line`
3. The severity comes from the list: the highest severity of a question that does not hold; `low` with a
   note or an answer `unknown`; `none` with neither; a closed answer blocks nothing; the line that the
   reviewer wrote does not count.
   test: `tests/test_review.py::Answers.test_the_severity_comes_from_the_list`
4. A report that lacks an answer, a heading of an expected intent, the sentence of a question that does
   not hold, or the section "Answers" is not complete.
   test: `tests/test_review.py::Answers.test_a_report_that_lacks_an_answer_is_not_complete`
5. A report answers for each intent that the change adds and for the intent of each plan that it adds or
   changes.
   test: `tests/test_review.py::TheChange.test_the_intents_that_a_report_answers_for`
6. Code answers the names of the checks, and the command `before` prints these answers for the reviewer.
   test: `tests/test_review.py::TheChange.test_code_answers_the_names_of_the_checks`
   test: `tests/test_review.py::TheChange.test_the_text_for_the_reviewer`
7. The command `close` adds the answer of code under the heading of its intent, also when another intent
   holds the same answer; it writes the severity line as the last line; it leaves a report that is not
   complete as it is, with the exit code 1. The verdict reads the severity line of each report.
   test: `tests/test_review.py::TheChange.test_the_command_closes_a_report`
   test: `tests/test_charter_facts_github.py::ReviewReports.test_each_report_gives_its_severity_in_order`
8. In the workflow and in its template, the step before the reviewer writes the answers of code, the step
   that posts the report closes it and posts no report that is not complete, and no step runs code of the
   change. With a version of Charter that has no such script, the report is posted as the reviewer wrote it.
   test: `tests/test_review.py::TheWorkflow.test_the_step_posts_a_report_with_the_severity_of_code`
   test: `tests/test_review.py::TheWorkflow.test_code_answers_before_the_reviewer_and_runs_no_code_of_the_change`
   test: `tests/test_review.py::TheWorkflow.test_the_scripts_of_the_base_branch`
9. The command of the test set grades a report in the form of the closed list: the severity of code, the
   subject in an answer that does not hold, and "form not read" for a report that lacks an answer.
   test: `tests/test_reviewer_eval.py::TheRun.test_the_result_counts_each_kind_and_keeps_each_report`
   test: `tests/test_reviewer_eval.py::Grader.test_the_subject_of_a_finding_at_the_threshold`
10. No case of the test set is contested, and each case with the answer `blocks` names its subject.
    test: `tests/test_reviewer_eval.py::TheSet.test_each_case_of_the_set_has_its_parts_and_the_set_is_balanced`
11. The command `charter-review` is a command of the plugin, both manifests name the version 0.3.22 or a
    later one, and the product test runs the command on a report: the scenario "severity of a report of the
    reviewer".
    test: `tests/test_review.py::TheList.test_both_manifests_name_the_version`
    test: `tests/test_setup.py::Commands.test_the_four_commands_exist_and_the_manifests_agree`
    command: `python3 tests/product.py`

## Manual checks

12. The answer of the 12 cases whose answer or subject this change sets: the 8 contested cases, and 4 cases
    with the answer `blocks` whose finding changes its kind. The five kinds that the author chose are in
    that reading. Drafted by the agent, reviewed by an agent that
    is not the author, confirmed by the leader. Not automatic: it sets the measure for the grader. Its
    record is the section "Disagreements" of the change request.
13. One full run of the test set with the reviewer itself, and two more runs of the cases with the answer
    `passes`. The author starts them after the word of the leader, because the runs of the model are on the
    account of the leader. The bar: no case with the answer `blocks` is a miss; fewer runs of a `passes`
    case are blocked than on 2026-11-26; fewer `passes` cases get two different answers in their three
    runs than on that day; no more than 2 runs give a report that is not complete. On 2026-11-26, 9 of the
    11 cases that have the answer `passes` today had three runs: 14 of these 27 runs were blocked, and 3 of
    the 9 cases got two different answers. Code writes the record, `evals/intent-review/record/`. Not
    automatic: no test may call the model.
