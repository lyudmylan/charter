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
  - the read tools with their folder: the folder of the change, and the folder of the Charter scripts,
    where the skill is;
  - a list of refused patterns for the allowed commands: an output file of `git diff` and `git log`,
    `git diff --no-index`, `gh pr comment` with `--edit-last` or `--delete-last`, and `gh api` with a
    method, a field, or an input file;
  - the checkout with `persist-credentials: false`.
- `docs/contract.md`, the section "The intent reviewer", and one row in `docs/decisions.md`.
- Both manifests: the same version, 0.3.20 or later.

## Out of scope

- The workflow `run`: its boundary is the sandbox and the gate, with their own tests.
- A reviewer workflow that takes its file from the main branch and not from the branch of the change
  request. Today each party that can push a branch can change the file. It is a change of design, with
  its own work item.
- The outside actions by a full commit and not by a tag: its own work item.
- A test through the action `claude-code-action`: it starts on no push of a branch. The test ran the
  program that the action runs, with the same flags.

## Acceptance checks

## Automatic checks

1. In the four workflow files the list of tools is closed: the flag `--permission-mode dontAsk`, and no read
   tool without its folder. test: `tests/test_workflows.py::ReviewerBoundary.test_the_list_of_tools_is_closed`
2. The four files refuse the same patterns, each with a space before its flag, so that the name of a repo
   with such letters in it is not refused. test: `tests/test_workflows.py::ReviewerBoundary.test_the_ways_to_write_are_refused`
3. The checkout of each reviewer keeps no credentials. test: `tests/test_workflows.py::ReviewerBoundary.test_the_checkout_keeps_no_credentials`
4. The documents and both manifests carry the boundary. test: `tests/test_workflows.py::ReviewerBoundary.test_the_documents_and_the_version_carry_the_boundary`

## Manual checks

5. The test on the code host, by the author, before the change request: with the flags of the templates,
   each read and each command that a review needs passes, and each refused case is refused. It is manual
   because it needs a machine of the code host and a branch of its own. Its record is a comment on #131.
6. The two reviewers post their reports on the change request of this work item, which runs them with the
   new flags. The leader reads that both reports are there. It is manual because the reviewers run with
   the model.
