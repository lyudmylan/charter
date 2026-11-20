# Intent: a ready issue starts an agent run, and the run ends as a change request

Work item: #92. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A person marks an issue whose intent is merged, and with no session of a person an agent builds the
work item inside the boundary of the contract, and a script publishes the result as a change request.

## In scope

- The gap: a person starts each agent session by hand and stays in it. Charter has the gates, the
  reviews, and the merge by tier, and nothing that takes a ready work item and runs an agent on it.
- A workflow `run`, as a template that the setup step writes, and in this repo. It always runs from the
  main branch, as the verdict does.
- The start. A person puts the label `charter-run` on an issue, or starts the workflow by hand with the
  number of an issue. Only a person with write access can do either on the code host.
- The stop switch (decision of #12): one variable of the repo, `CHARTER_RUNS`. With the value `off` no
  run starts. A run that works is stopped with the cancel of the code host. One run works at a time; a
  second one waits.
- Ready. A script decides, before any agent starts: the issue is open, it names one intent with the
  line `Intent: intents/<part>.md`, and that intent is a file of the main branch. Else the run ends as
  blocked, with the reason on the issue.
- The steps of the run, in this order. Each one but the agent is a script.
  1. The checkout of the main branch, with no credential left in the folder, and a new branch
     `run/<number of the issue>`.
  2. The toolchain of the repo, from the marked block (#88).
  3. The sandbox of Linux, as the documentation of Claude Code gives it for Ubuntu: the two packages,
     and the profile that lets the sandbox start. Claude Code at one version, which the workflow names.
  4. The settings of the run, from `charter-check boundary` on the contract of the main branch with the
     organization source (#91, decision E8). The clone of the source is removed before the agent starts:
     the shell of the agent can read most of the disk, and the source of an organization can be private.
  5. The brief: a script writes it from the issue and from a fixed text. The text of the issue is data
     in it, marked as such.
  6. The agent: `claude -p` with the brief, with the settings given on the command line as text, not as
     a file that the agent could change, with no list of allowed tools, with a limit of turns, and with
     a time limit of the step. Its
     environment holds one secret, the token of the model. The agent writes the plan `plans/<part>.md`,
     the code, and the tests, and runs the quality commands in its sandbox. It leaves its changes in the
     folder and commits nothing. It writes the text of the change request, or the reason why it cannot
     finish, into a file of the folder `.charter-run/`, which is never committed.
  7. The result: a script takes the folder `.charter-run/` out, commits what the agent left, lists each
     changed path with a NUL character between the paths, and runs `charter-gate boundary` (#91, #101).
     A failed gate, an agent that ended in an error or wrote a reason, or a branch with no change ends
     the run as blocked.
  8. The publishing, only after step 7 passed (decision E7): a script pushes the branch and opens the
     change request that closes the issue, with the secret `CHARTER_RUN_TOKEN`. A person creates that
     token: a change request that the token of the workflow opens starts no workflow on the code host.
  9. The outcome on the issue, in each case: the change request, or the word blocked with the reason,
     and the turns, the duration, and the cost that Claude Code reports.
- The settings of `charter-check boundary` (#91) get three more values, after a test on a Mac on
  2026-11-20. With a list of allowed tools on the command line, the Read tool read a file outside the
  folder and the Write tool wrote one. So the settings now hold the mode that lets the file tools change
  a file of the folder with no question, in which a path outside the folder needs a question and is
  refused; the block of writes outside the folder, which holds in every mode; and a read denial for the
  environment of other processes. The same test with these settings alone refused the three cases.
- The agent step holds no token of the code host, and no step after it gives the agent a second turn.
  No step after the agent runs a file of the folder that the agent wrote in: the scripts come from a
  copy of Charter that was made before the agent started, the quality commands run in the workflow
  `tests` of the change request, and the push runs no hook of the folder. A later step holds a token,
  and a file that the agent wrote must not run beside it.
  The workflows `tests`, `review-intents`, `review-code`, and `verdict` run on the change request as on
  any other, and the merge follows the tier (#66).
- The plan. The run writes it with the code. In a tier whose approver is `agent`, the review of the
  intent reviewer is its acceptance (#66); in a tier of a person, the merge of that person is. So in a
  run the acceptance follows the code and does not come before it: the verdict checks that the plan
  exists, not the order (`intents/plan-before-the-code.md`). The Build row of `docs/product.md` and the
  section on the plan of `AGENTS.md` and of its template say so.
- The run can use no other settings than the ones of the boundary: one step writes them, and the command
  of the agent takes them as text. A test of the workflow proves this wiring; it is the check that the
  intent of #91 left to this work item.
- The findings of a reviewer on the change request of a run: in this version a person decides, by a
  correction in a session or by a new run on a new branch.
- The skill `tracker` says what a work item for a run looks like: one change request that one run can
  finish, automatic checks only, no network and no secret during the work, and a change of a file that
  the boundary closes as its own work item of a person.
- The setup step writes the workflow, fills its toolchain block from the same file as the block of
  `tests`, creates nothing on the code host, and names among its manual steps the label, the variable,
  and the secret `CHARTER_RUN_TOKEN`.
- `docs/contract.md`: a section "The run". `docs/product.md`: the Build row of the lifecycle map, and
  one sentence in "Who does the work". `docs/decisions.md`: the start by a label, the stop switch as a
  variable, and the token of the publishing step.
- Both manifests: the same version, 0.3.13 or later.

## Out of scope

More than one run at a time, a retry, and a run whose issue changed while it worked: later steps of
#82. The stop rules of the contract inside a run, which the issue lists: the run has a limit of turns and
a time limit, a person decides at the findings of a reviewer, and the count of the refusals is a later
issue of #12. The order of the first work items of a new product in the skill `tracker`, which the issue
lists: a later change. A run that answers the findings of a reviewer. The identity of the agent on the code host: the
change request is opened in the name of the owner of the run token (#13). The outcome and the cost in
the evidence record of the change request: #93; here they are on the issue. A product that needs the
network or a secret in its tests. A limit of cost: #53.

## Acceptance checks

## Automatic checks

1. The setup step writes the workflow `run`. It starts on the label `charter-run` and by hand, runs from
   the main branch, lets one run work at a time, and starts nothing when the variable `CHARTER_RUNS` is
   `off`.
   test: `tests/test_run.py::Workflow.test_the_setup_writes_the_workflow`
   test: `tests/test_run.py::Workflow.test_the_start_the_stop_switch_and_one_run_at_a_time`
2. The steps stand in the order of the scope: the gate on the result before the publishing, and the
   publishing only when the gate passed.
   test: `tests/test_run.py::Workflow.test_the_gate_stands_before_the_publishing`
3. The agent step holds the token of the model and no other secret, no token of the code host, and the
   checkout leaves no credential. The run token is in the publishing step only. The token of the
   organization source is in the two steps that read the contract with it, the settings step and the gate
   step, and the settings step removes the clone of the source.
   test: `tests/test_run.py::Workflow.test_each_secret_is_in_one_step`
4. No step after the agent runs a file of the folder of the repo: each such step calls the scripts of
   the copy of Charter, `git`, or `gh`, and the push names no hook folder of the repo.
   test: `tests/test_run.py::Workflow.test_no_step_after_the_agent_runs_a_file_of_the_folder`
5. The agent gets the settings of `charter-check boundary` as text on the command line, with a limit of
   turns and no list of allowed tools, and the step has a time limit. The settings hold the mode, the
   block of writes outside the folder, and the read denial for the environment of other processes.
   test: `tests/test_run.py::Workflow.test_the_agent_runs_under_the_settings_and_the_limits`
   test: `tests/test_boundary.py::Settings.test_the_file_tools_stay_inside_the_folder`
6. The readiness script passes an open issue with one intent that is a file of the main branch, and
   blocks, with the reason, a closed issue, an issue with no intent line, with two, and with an intent
   that is no file of the main branch.
   test: `tests/test_run.py::Ready.test_an_open_issue_with_a_merged_intent_is_ready`
   test: `tests/test_run.py::Ready.test_each_other_case_is_blocked_with_its_reason`
7. The brief holds the fixed text, the path of the intent, and the text of the issue marked as data.
   test: `tests/test_run.py::Brief.test_the_brief_marks_the_text_of_the_issue_as_data`
8. The result step, run in a git repo with a fake agent result: a change of an open path passes and
   lists its paths with NUL; a change of a closed path fails and names the path; no change is blocked;
   an agent result that is an error is blocked.
   test: `tests/test_run.py::Result.test_a_change_inside_the_boundary_passes`
   test: `tests/test_run.py::Result.test_a_change_of_a_closed_path_is_blocked`
   test: `tests/test_run.py::Result.test_no_change_and_an_agent_error_are_blocked`
9. The publishing step, run with a fake of the code host: it pushes the branch and opens a change request
   whose text closes the issue; without the run token it publishes nothing and the run is blocked.
   test: `tests/test_run.py::Publish.test_the_branch_is_pushed_and_the_change_request_closes_the_issue`
   test: `tests/test_run.py::Publish.test_without_the_token_nothing_is_published`
10. The outcome step writes one comment on the issue in each case, with the outcome, the reason when
   blocked, and the turns, the duration, and the cost of the agent result.
   test: `tests/test_run.py::Outcome.test_the_issue_gets_the_outcome_in_each_case`
11. The workflow of this repo follows the template, but for the place of the scripts of Charter.
    test: `tests/test_run.py::Workflow.test_the_workflow_of_this_repo_follows_the_template`
12. The setup step names the label, the variable, and the run token among its manual steps, and fills
    the toolchain block of the run from the file of the flag.
    test: `tests/test_run.py::Setup.test_the_manual_steps_and_the_toolchain_block`
13. The skill `tracker` says what a work item for a run looks like; `docs/contract.md` holds the section
    "The run"; `docs/product.md` names the run and says that in a run the acceptance of the plan follows
    the code; the instructions say the same; the decision record holds the three decisions.
    test: `tests/test_run.py::Documents.test_the_skill_and_the_documents_name_the_run`
14. Both manifests name the same version, 0.3.13 or later.
    test: `tests/test_run.py::Documents.test_both_manifests_name_the_version`

## Manual checks

15. The first run, in an adopter repo with the two secrets: a labelled issue becomes a change request
    with a plan, code, and tests; no session of a person drove it; the outcome is on the issue. who:
    the leader. Not automatic: the run needs the code host, a runner, and a model.
16. The manual check 16 of `intents/boundary-of-a-run.md`, in that first run on a Linux runner, and three
    points more: the agent reads and writes no file outside the folder of the repo, with a file tool or
    with the shell; a shell command cannot read the environment of the process of the agent; and a shell
    command cannot write a file of the temporary folder of the runner. who: the leader. Not automatic:
    as above.
