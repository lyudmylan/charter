# Intent: a reviewer in CI writes no file and reads no token

Work item: #131. Approval: a person merges the change request that adds this file.

## Goal

A reviewer in CI can do what its prompt allows and no more: it reads the change and the skill, and it posts
one report. No token is in a file that it can read.

## In scope

- The test. On 2026-11-25 a workflow on its own branch ran Claude Code 2.1.332 on a machine of the code
  host, with the flags of the reviewers, a local server in the place of the model, and false tokens. With
  the flags of that day the reviewer read each file of the machine, the credentials file that the checkout
  leaves in the temporary folder too, and `git diff --output` and `git log --output` wrote a file at any
  path. It did not read the token of the model: the read tool and the shell refuse the environment of a
  process, and the shell refuses a variable that it cannot check.
- The two reviewer workflows, `review-intents` and `review-code`, as templates and in this repo:
  - the flag `--permission-mode dontAsk`, which refuses each tool call that the list does not allow;
  - the read tools with their folder: the folder of the change, the folder of the Charter scripts, where
    the skill is, and the folder of the earlier reports;
  - a shell of five commands that read: `git diff`, `git log`, `gh issue view`, `gh issue list`,
    `gh pr view`. The reviewer has no command that writes to the code host, and none that reads a file by
    itself for a flag, such as `gh pr comment --body-file <path>`: a pattern cannot refuse each form of
    such a flag;
  - the report is the final answer of the reviewer. A step after the reviewer takes the text from the
    marker line on and posts it; a step before the reviewer writes the earlier reports to a file;
  - a list of refused patterns: the output file of `git diff` and `git log`, and `git diff` with no index,
    from the first letters that git can take for the flag;
  - the checkout with `persist-credentials: false`.
- The later steps of the job run no file that the reviewer wrote: the reviewer can write no file.
- A test that repeats the cases: `tests/probe/reviewer_probe.py`, with its local server, and in this repo
  the workflow `reviewer-boundary`, which runs it on each change of a reviewer workflow. It needs no secret.
- `docs/contract.md`, the section "The intent reviewer", and one row in `docs/decisions.md`. The section
  names the page of the official documentation of the action on the files that come from the base branch.
- Both manifests: 0.3.20.

## Out of scope

- The workflow `run`: its boundary is the sandbox and the gate, with their own tests.
- A reviewer workflow that takes its file from the main branch and not from the branch of the change
  request. Today each party that can push a branch can change the file. It is a change of design, with
  its own work item.
- The outside actions by a full commit and not by a tag: its own work item.
- A test through the action `claude-code-action`: it starts on no push of a branch, and a run of it on a
  change request needs the token of the model. The test runs the program that the action runs, with the
  same flags. Check 7 covers the action itself.

## Acceptance checks

### Automatic checks

1. In the four workflow files the list of tools is closed: the flag `--permission-mode dontAsk`, each read
   tool with its folder, and the five commands of the shell. test: `tests/test_workflows.py::ReviewerBoundary.test_the_list_of_tools_is_closed`
2. The four files refuse the output file of `git diff` and `git log` and the form with no index, also in a
   short form of the flag, and `--oneline` stays open. test: `tests/test_workflows.py::ReviewerBoundary.test_the_ways_to_write_a_file_are_refused`
3. The checkout of each reviewer keeps no credentials. test: `tests/test_workflows.py::ReviewerBoundary.test_the_checkout_keeps_no_credentials`
4. A step posts the final answer of the reviewer from the marker line on, and posts nothing with no marker
   or with no record of the run. test: `tests/test_workflows.py::ReviewerBoundary.test_a_step_posts_the_final_answer_of_the_reviewer`
5. The documents and both manifests carry the boundary. test: `tests/test_workflows.py::ReviewerBoundary.test_the_documents_and_the_version_carry_the_boundary`
6. With the flags of the template, on a machine of the code host, each read and each command that a review
   needs passes; each case of a write, of a read outside the three folders, of a read of the environment,
   and of a second command is refused; no result holds a token; no file is written. The workflow
   `reviewer-boundary` of this repo runs it. command: `python3 tests/probe/reviewer_probe.py`

### Manual checks

7. The two reviewers post their reports on the change request of this work item, which runs them through
   the action with the new flags. The leader reads that both reports are there after the last push. It is
   manual because the reviewers run with the model.
