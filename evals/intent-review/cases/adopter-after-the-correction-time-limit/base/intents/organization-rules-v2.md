# Intent: this repo follows version 2 of the organization rules

Work item: #48. Approval: a person merges the change request that adds this file.

## Goal

The contract names version 2 of the organization rules, so that the factory starts the agent that answers
the findings of the reviewers on the change request of a run, with no step of a person.

## In scope

- Why: version 2 of the organization rules holds one new rule, `run.answer_start = "factory"`. The leader
  decided on 2026-11-24 that the rule lives in the organization file, for each repo of the organization.
- `charter.toml`: the version of the source, `v2`. The contract of this repo holds no value for
  `run.answer_start`; the value comes from the organization.
- The behaviour of the answer is the one of that rule: the contract document of Charter says when an
  answer starts, and the organization rules give the threshold and the limit of rounds. This intent does
  not repeat them.
- What this repo decides: it follows the version; each merge stays with a person, because no tier of this
  contract has the approver `agent`; and the stop is the variable `CHARTER_RUNS` of the repo with the
  value `off`, which stops each run and each answer.
- A later change request can give the start back to a person in this repo, with one line in this contract.
  That change is not a part of this work item, and no check here covers it.
- One change request, with the intent and the plan in it: the change is one line and has no code of the
  product, and the merge of a person is the approval of the intent.

## Out of scope

A tier whose approver is `agent`. The start of a run after the merge of an intent with no step by hand.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.19.

1. The contract passes the contract checks, with version 2 of the organization rules.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names version 2 of the source.
   command: `grep -q '^version = "v2"$' charter.toml`
4. The contract of this repo holds no value of its own for the start of an answer.
   command: `sh -c '! grep -q "answer_start" charter.toml'`
5. The effective contract says that the factory starts an answer. The command reads the JSON form that
   Charter 0.3.19 prints.
   command: `sh -c 'charter-check check charter.toml --json | grep -q "\"run.answer_start\": \"factory\""'`

## Manual checks

6. On the change request of a run with a finding at the threshold, an answer starts with no step of a
   person: the job `decide` of the workflow `run` prints `start=true`, an agent pushes a commit to the
   branch or drops the finding, a comment on the change request holds the outcome and the line
   `Answered commit:`, and the reviewers report again on the new commit.
   who: the leader. Not automatic: the check needs a model call, machines of the code host, and a report of
   a reviewer with such a finding.
7. With the variable `CHARTER_RUNS` set to `off`, no answer starts after a report of a reviewer.
   who: the leader. Not automatic: the check needs a variable of the repo on the code host.
