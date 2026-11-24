# Intent: an agent answers the findings of the reviewers on the change request of a run

Work item: #118. Approval: a person merges the change request that adds this file.

## Goal

A finding of a reviewer on the change request of a run gets an answer with no session of a person: a
correction, or a dropped finding with its reason.

## In scope

- The gap. The review loop has two sides. The reviewers run on the code host at each push. The author side
  runs in a session of a person, and after a run of an agent no author is there. At an adopter, each
  finding on the change request of a run waited for a session.
- The decisions of the leader. The agent puts its correction in the same change request, as a new commit
  on the branch of the run (2026-11-22). The factory starts the answer by itself, within the limit of
  rounds of the contract (2026-11-24). The start is a rule of the contract that the organization sets and
  a repo can move toward the start by a person; without a value a person starts each answer, so a repo
  that moves to this version gets no new use of a subscription without a written choice (2026-11-24).
- The sources, both official, differ on the start. The documentation of Claude Code for GitHub Actions: a
  person starts each round, and a bot cannot start the agent, to prevent a loop. The example workflow of
  the Symphony repository of OpenAI: the agent answers each reviewer comment, of a person or of a bot,
  before a person sees the change request. The leader chose. Against a loop with no end, a script counts
  the rounds from the reports of the reviewers, the agent does not, and the limit of the contract ends
  the loop.
- The contract: the field `run.answer_start`, a choice from `factory` to `person`. `person` is the
  stricter value.
- The decision, `charter-gate answer`: it reads the facts of the change request and the contract of the
  main branch, and prints whether an answer starts, with the reason. An answer starts for the open change
  request of a run of this repo, when each reviewer that takes part has its newest report on the head
  commit, a report is open at the threshold or has no severity line, no open loop is at the limit, and no
  answer handled that head commit before. Without a limit of rounds in the contract nothing ends the loop,
  so the factory starts no answer. The findings of the reviewer of the code get an answer also in
  its shadow period. A person can start an answer in each case but the limit.
- The facts collector: the branch, the state, and the fork of the change request; the head commits that an
  answer handled, from the comments; and the fact `run` as the sum of the blocks of the text, one for the
  run and one for each answer. The line of the verdict and the record of a run name the number of the runs
  of an agent. This is a count, not the state of an answer.
- The workflow `run`, in the template and in this repo. It starts also after a run of a reviewer workflow
  on a branch `run/**`, and by hand with the number of a change request. A job `decide` reads the facts
  and says whether an answer starts; it starts no agent. The job `run` then works as for an issue: the
  same sandbox, the same settings from the contract of the main branch, the same gate, and no token of the
  code host for the agent. The steps of the toolchain run on the files of the main branch; the branch of
  the run is opened only for the agent.
- The brief of an answer: the fixed text, then the newest report of each reviewer and the issue, as data.
  The agent corrects a finding at the threshold or above, or drops it with the reason; a finding below it
  only when it is one line of work. A finding that needs a change of a closed path, the intent among
  them, is for a person. The agent marks no finding as false.
- The result of an answer: one commit that names the round. No changed path is a result too, because the
  agent can drop each finding.
- The publishing: a push to the branch of the run with no force; the text of the change request keeps its
  lines and gets each new line `Dropped finding:` and one more block of a run. No other line of the agent
  reaches the text. An answer that changed no path and dropped no finding publishes nothing.
- A finding that the agent dropped. The reviewers read a line `Dropped finding:` as a closed finding, and a
  sentence in a report or in the issue could lead the agent to drop a finding that is right. So the script
  writes the words `by the agent of a run:` into each such line, and the verdict merges no change request
  that holds one: a person reads the reason before the merge.
- The outcome: a comment on the change request, with the head commit that the agent answered, the three
  numbers, and the lines of its answers.
- The skill `review-loop`: on the branch of a run with `factory`, a session answers no finding.
- `docs/contract.md`, `docs/product.md`, and the hand steps that the setup step prints.
- Both manifests: the same version, 0.3.19 or later.

## Out of scope

The start of a run after the merge of an intent with no step by hand. The merge by the verdict. A file for
a team between the organization and the repo. A value of `run.answer_start` for one risk tier. A finding
that the leader marks as false. A line of the verdict on the state of the answer.

## Acceptance checks

## Automatic checks

1. `run.answer_start` is a choice from `factory` to `person`. The organization sets it, a repo moves it
   toward `person` in each case, and a repo cannot move a locked `person` to `factory`.
   test: `tests/test_answer.py::Contract.test_the_start_of_an_answer_is_a_rule_with_a_direction`
2. The decision. An open finding on the head commit starts an answer and names the issue, the branch, the
   commit, the round, and the threshold. Each other state starts none and names its reason. The factory
   starts an answer only when the contract says so; a person starts one in each case but the limit. A
   facts file that cannot be read is no decision.
   test: `tests/test_answer.py::Decision.test_an_open_finding_on_the_head_commit_starts_an_answer`
   test: `tests/test_answer.py::Decision.test_each_other_state_starts_no_answer_and_names_its_reason`
   test: `tests/test_answer.py::Decision.test_the_factory_starts_an_answer_only_when_the_contract_says_so`
   test: `tests/test_answer.py::Decision.test_a_facts_file_that_cannot_be_read_is_no_decision`
   test: `tests/test_answer.py::Decision.test_without_a_limit_of_rounds_the_factory_starts_no_answer`
3. The facts hold the branch, the state, the fork, and the answered commits. The fact `run` sums the
   blocks, and the verdict and the record name the number of the runs of an agent.
   test: `tests/test_answer.py::Facts.test_the_facts_hold_the_branch_and_the_answered_commits`
   test: `tests/test_answer.py::Facts.test_the_run_of_the_record_sums_the_blocks`
   test: `tests/test_answer.py::Facts.test_the_verdict_and_the_record_name_the_runs_of_an_agent`
4. The brief of an answer marks the reports and the issue as data, and names the rules of an answer.
   Comments with no report give no brief.
   test: `tests/test_answer.py::Brief.test_the_brief_of_an_answer_marks_the_reports_and_the_issue_as_data`
   test: `tests/test_answer.py::Brief.test_no_report_and_a_wrong_file_give_no_brief`
5. The commit of an answer names its round, and an answer with no changed path is a result.
   test: `tests/test_answer.py::Result.test_the_commit_of_an_answer_names_its_round`
   test: `tests/test_answer.py::Result.test_an_answer_with_no_changed_path_is_a_result`
6. The text of the change request gets each new dropped finding, with the words that name the agent of a
   run, and no other line of the agent. No changed path and no dropped finding is no answer. A link in the
   place of the answers is not followed. The verdict merges no change request with such a dropped finding.
   test: `tests/test_answer.py::Text.test_the_text_gets_each_new_dropped_finding_and_no_other_line`
   test: `tests/test_answer.py::Text.test_no_changed_path_and_no_dropped_finding_is_no_answer`
   test: `tests/test_answer.py::Text.test_the_answers_file_is_read_as_data`
   test: `tests/test_answer.py::Merge.test_the_verdict_merges_no_change_request_with_a_finding_that_an_agent_dropped`
7. The comment of an answer names the answered commit, in the form that the facts collector reads back,
   and the answers of the agent.
   test: `tests/test_answer.py::Outcome.test_the_comment_of_an_answer_names_the_commit_and_the_answers`
8. The workflow. A report on a branch of a run and a person start the decision. "No answer" ends the
   decision with success for the factory and with a failure for a person. The branch of the run is fetched
   before the toolchain block and opened for the agent.
   test: `tests/test_answer.py::Workflow.test_a_report_on_a_branch_of_a_run_and_a_person_start_the_decision`
   test: `tests/test_answer.py::Workflow.test_no_answer_ends_the_decision_with_success_for_the_factory`
   test: `tests/test_answer.py::Workflow.test_the_branch_of_the_run_is_fetched_before_the_toolchain_and_opened_for_the_agent`
9. The publishing step of an answer pushes to the branch with no force and changes the text of the change
   request. An answer that is none, and a missing token, publish nothing.
   test: `tests/test_answer.py::Workflow.test_the_answer_goes_to_the_branch_and_to_the_text_of_the_change_request`
   test: `tests/test_answer.py::Workflow.test_an_answer_that_is_none_and_a_missing_token_publish_nothing`
10. The outcome of an answer goes on the change request, with the answered commit in each case.
    test: `tests/test_answer.py::Workflow.test_the_outcome_of_an_answer_goes_on_the_change_request`
11. The documents, the skill, and both manifests carry the answer and one version, 0.3.19 or later.
    test: `tests/test_answer.py::Documents.test_the_documents_the_skill_and_the_version_carry_the_answer`
12. In the product test, in a repo that the setup step made, the factory starts no answer, because the
    contract holds no value, and a person starts one.
    command: `python3 tests/product.py`, the steps "answer to a finding, the factory" and "answer to a finding, a person"
13. The steps of the workflow `run` that existed before keep their rules: the start, the secrets, the
    order, and no step after the agent that runs a file of the folder.
    test: `tests/test_run.py::Workflow.test_the_start_the_stop_switch_and_one_run_at_a_time`
    test: `tests/test_run.py::Workflow.test_each_secret_is_in_one_step`
    test: `tests/test_run.py::Workflow.test_no_step_after_the_agent_runs_a_file_of_the_folder`

## Manual checks

14. At an adopter with `run.answer_start = "factory"`, a change request of a run with a finding at the
    threshold gets a commit of an agent on its branch and a comment with the outcome, with no step of a
    person, and the reviewers report again on that commit. With the stop switch off, no answer starts.
    who: the leader. Not automatic: the check needs a model call, machines of the code host, the secrets
    of the adopter, and a workflow on the main branch; the code host starts a workflow after another one
    only from the main branch.
