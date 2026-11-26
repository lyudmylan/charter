# Intent: the intent reviewer has a test set of real cases, and one command runs it

Work item: #140. Approval: a person merges the change request that adds this file.

## Goal

About 20 real cases run with one command, and a report says in how many cases the intent reviewer gave
the right answer.

## In scope

- The folder `evals/intent-review/cases/`. A case is one real change request: the repo before the change,
  the changed intents and plans, the text of the issue and of the change request, the report of the earlier
  round when the case is a later round, and the answer that is right. The answer is `blocks`, a finding at
  the threshold of the contract or above, or `passes`. Each case says where its answer comes from.
- Two forms of a case. A case of this repo names its commits. A case of an adopter holds its files, with the
  name of the product replaced.
- At this change the set holds 25 cases: 18 of this repo and 7 of an adopter; 9 of a later round. 17 are
  counted: 14 with the answer `blocks` and 3 with the answer `passes`. Check 8 holds the lower bounds, so a
  later case needs no change of this intent. A `blocks` case is a finding that the author corrected and the
  leader merged. A `passes` case is a state that the leader merged with a report below the threshold, and
  that the reviewer passed again in each of three runs of the set.
- 8 cases are contested. Each is a merged state with a report below the threshold then, and the reviewer of
  today blocked it in one run of three or more, with a finding that two agents that are not the author
  found right in fact. The reviewer does not grade itself: such a case keeps its answer, the command runs
  it and shows it apart, and it is no part of the count until the leader says its answer.
- The command `python3 evals/intent-review/run.py`. It gives each case to the reviewer in the form of the
  workflow `review-intents`: the prompt, the limit of turns, and the tool list come from the template of
  the workflow, and the skill comes from the folder of the repo.
- The reviewer reads nothing on the code host: a stand-in for its command answers from the files of the
  case. The answers of the set are in no folder that the reviewer reads. The settings and the instruction
  file of the person who starts the command stay out of the run.
- A grader in code. It reads the line of the highest open severity against `review.threshold`. Each
  `blocks` case names its subject: one or more ways to name it, each a list of patterns, and one finding at
  the threshold must hold each pattern of a way. A match of words is a rough measure of the subject.
- The command grades the reports of an earlier run again, with no run of the model: `--reports <folder>`.
  It prints the result, and it writes files only when `--out` names a folder.
- A report that blocks in a form that the grader cannot read gets its own result, "form not read".
- No case holds private material or the name of another project. A test holds the forms of private
  material. The names of other projects are in the source of the organization, so the command
  `python3 evals/intent-review/run.py --text` checks each file of the cases against the text patterns of
  the contract.
- The report: the number of right answers, of false alarms, of misses, of answers on another subject, and
  of runs with no report, with one row for each case. The command keeps each report of the reviewer.
- `docs/contract.md`, `docs/product.md`, and `README.md` name the command.

## Out of scope

- The eval cases of the skill `tracker` and their run: #79, #80.
- A test set for another skill, and for the reviewer of the code.
- A change to the text of the reviewer. Each defect that the set shows becomes an issue.
- A run of the set in a workflow: each case is a run of the model on the account of a person.
- A grader that is a model.
- A case of a finding that the reviewer missed and that showed later as a defect. The record of the three
  repos names no such case yet.
- The answer of the 8 contested cases. The work item on the closed list of questions, #153, settles them:
  the leader says for each kind of finding whether it blocks.

## Acceptance checks

### Automatic checks

1. A case in each of the two forms becomes a repo with the base on `origin/main` and the change on its
   branch, and a later round has the earlier report with the commit of the earlier state. test: `tests/test_reviewer_eval.py::Workspace.test_a_case_becomes_a_repo_with_the_base_and_the_change`
   and `tests/test_reviewer_eval.py::Workspace.test_a_case_of_commits_of_this_repo`
2. The answers of the set are in no folder that the reviewer reads. test: `tests/test_reviewer_eval.py::Workspace.test_the_answers_of_the_test_set_are_in_no_folder_that_the_reviewer_reads`
3. The reviewer starts with the prompt, the limit of turns, and the tool list of the template, and without
   the settings of the person. test: `tests/test_reviewer_eval.py::TheRun.test_the_reviewer_starts_in_the_form_of_the_workflow`
4. The stand-in for the command of the code host answers a read of the issue from the case, and it refuses
   each other command. test: `tests/test_reviewer_eval.py::TheRun.test_the_stand_in_of_the_code_host_answers_from_the_case`
5. The grader gives the right result for each pair of an answer and a severity line, for a report with no
   severity line, and for a finding on another subject. test: `tests/test_reviewer_eval.py::Grader.test_the_severity_line_against_the_threshold`
   and `tests/test_reviewer_eval.py::Grader.test_the_subject_of_a_finding_at_the_threshold`
6. A case with a missing part cannot run, and the command names the part; a template of the workflow that
   the command cannot read cannot run. test: `tests/test_reviewer_eval.py::Workspace.test_a_case_with_a_missing_part_cannot_run`
   and `tests/test_reviewer_eval.py::Template.test_a_template_that_the_command_cannot_read_cannot_run`
7. The report counts each kind of result and keeps each report; a run with no report ends the command with
   1; one case runs by its name. test: `tests/test_reviewer_eval.py::TheRun.test_the_result_counts_each_kind_and_keeps_each_report`,
   `tests/test_reviewer_eval.py::TheRun.test_a_case_with_no_report_ends_the_command_with_1`, and
   `tests/test_reviewer_eval.py::TheRun.test_one_case_by_its_name_and_a_name_that_is_no_case`
8. Each case of the set has its parts: 18 cases or more; among the counted ones 8 or more with `blocks`
   and 3 or more with `passes`; 4 or more of an adopter; 3 or more of a later round; each `blocks` case
   names its subject. test: `tests/test_reviewer_eval.py::TheSet.test_each_case_of_the_set_has_its_parts_and_the_set_is_balanced`
9. The documents name the command. test: `tests/test_reviewer_eval.py::TheSet.test_the_documents_name_the_command`
10. A contested case runs, its report is kept, and it is no part of the count. test: `tests/test_reviewer_eval.py::TheRun.test_a_contested_case_runs_and_is_no_part_of_the_count`
11. The reports of an earlier run are graded again with no run of the model, and without `--out` no file
    changes. test: `tests/test_reviewer_eval.py::TheRun.test_the_reports_of_an_earlier_run_are_graded_again_with_no_model_call`
12. No file of a case holds a path of a computer, a mail address, a token, or a link to a session. test: `tests/test_reviewer_eval.py::TheSet.test_no_file_of_a_case_holds_private_material`
13. No file of a case holds a text pattern of the contract, the names of other projects too. The command
    needs the source of the organization, so the author runs it before each push.
    command: `python3 evals/intent-review/run.py --text`

### Manual checks

14. One full run of the set with the reviewer itself, and two more runs of the cases with the answer
    `passes`. The author starts them after the word of the leader, because the runs of the model are on the
    account of the leader. Their record is the folder `evals/intent-review/record/` of this change request:
    the report, the result file, and each report of the reviewer. Code writes the record. It is manual
    because no test may call the model.
15. The leader reads three cases and says for each whether the answer that the case holds is right: one
    `blocks` case, one `passes` case, and one contested case. The summary of each case is drafted by the
    agent, reviewed by an agent that is not the author, confirmed by the leader. It is manual because it
    sets the measure for the grader. Its record is a comment on #140.
