# Intent: this repo moves to Charter 0.3.19

Work item: #46. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.19 and the run workflow is the one that the setup step of that version
writes, so that a person can start the answer of an agent to the findings of the reviewers on the change
request of a run, and no answer starts without a person.

## In scope

- Why: after a run of an agent, a session of a person answers each finding of the reviewers. Charter
  0.3.19 adds an agent that answers them: a correction, or a dropped finding with the reason, in a new
  commit on the branch of the run. A script counts the rounds, and the limit of the contract ends the loop.
- `charter.toml`: the version 0.3.19. The contract gets no new field in this work item. The new field of
  that version, `run.answer_start`, has no value here, so a person starts each answer: a start of the
  workflow `run` by hand with the number of the change request.
- `.github/workflows/run.yml`: the file of the setup step of 0.3.19. It starts also after a run of a
  reviewer workflow on a branch `run/**`. A job `decide` then reads the contract and starts no answer,
  because the contract holds no value.
- One change request, with the intent and the plan in it: the change has no code of the product, and the
  merge of a person is the approval of the intent.

## Out of scope

The value `run.answer_start = "factory"`: the leader decides where it lives, and it comes in a change of
its own. The other workflows, `AGENTS.md`, and the two templates: the setup step of 0.3.19 writes them as
they are.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.19.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names the version 0.3.19.
   command: `grep -q '^version = "0\.3\.19"$' charter.toml`
4. The run workflow holds the job that decides on an answer, and the start after a reviewer workflow on a
   branch of a run. The two lines are present; check 6 covers the file as a whole.
   command: `grep -q '^  decide:$' .github/workflows/run.yml`
   command: `grep -q 'branches: \["run/\*\*"\]' .github/workflows/run.yml`
5. The contract of this work item holds no value for the start of an answer; a later work item can change
   this.
   command: `sh -c '! grep -q "answer_start" charter.toml'`

## Manual checks

6. Each of the five workflows, `AGENTS.md`, and the two templates is the file that the setup step of
   0.3.19 writes with the values of this repo and its toolchain steps.
   who: the engineer, with a setup in an empty folder and a comparison of the files. Not automatic:
   Charter has no command yet that updates a repo.
7. After the next report of a reviewer on a branch of a run, the job `decide` of the workflow `run` ends
   with success and the line "no answer: the contract says that a person starts an answer", and the job
   `run` does not start.
   who: the leader. Not automatic: the code host starts a workflow after another one only from the main
   branch, and the check needs a report of a reviewer on a change request of a run.
8. A start of the workflow `run` by hand with the number of a change request of a run, which has a finding
   at the threshold, gives that change request a commit of an agent on its branch and a comment with the
   outcome.
   who: the leader. Not automatic: the check needs a model call, a machine of the code host, and a report
   of a reviewer with such a finding.
