# Intent: this repo moves to Charter 0.3.21

Work item: #52. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.21, and the two reviewer workflows are the ones of that version. A
reviewer in CI then has a closed list of tools and no command that writes to the code host, and a later
version of Charter reaches this repo with one command.

## In scope

- Why: a test of Charter on the code host showed that a reviewer with the tools of 0.3.19 could read each
  file of its machine and write a file at any path. Charter 0.3.20 closes the list: the read tools take
  three folders, the shell has five commands that read, and a step of the workflow posts the report of the
  reviewer. Charter 0.3.21 adds the command `charter-update`, which makes the change of an upgrade.
- `charter.toml`: the version 0.3.21. The contract gets no new field.
- `.github/workflows/review-intents.yml` and `.github/workflows/review-code.yml`: the files that
  `charter-update` of 0.3.21 writes.
- One change request, with the intent and the plan in it: the change has no code of the product, and the
  merge of a person is the approval of the intent.

## Out of scope

The other three workflows and the two templates: the command names them as the same. The rules file and
each other field of the contract: the command changes no file that holds content of this repo.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.21.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names the version 0.3.21.
   command: `grep -q '^version = "0\.3\.21"$' charter.toml`
4. Each reviewer workflow holds the closed list and the step that posts the report.
   command: `grep -q -- '--permission-mode dontAsk' .github/workflows/review-intents.yml`
   command: `grep -q -- '--permission-mode dontAsk' .github/workflows/review-code.yml`
   command: `grep -q 'name: Post the report of the reviewer' .github/workflows/review-intents.yml`
   command: `grep -q 'name: Post the report of the reviewer' .github/workflows/review-code.yml`
5. A second run of the update command finds nothing to change.
   command: `sh -c 'charter-update --check | grep -q "nothing to change"'`

## Manual checks

6. The two reviewers post their reports on the change request of this work item, which runs them with the
   new workflows.
   who: the leader reads that both reports are there. Not automatic: the reviewers run with the model.
