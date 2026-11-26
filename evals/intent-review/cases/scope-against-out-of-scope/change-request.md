An agent answers the findings of the reviewers on the change request of a run

Closes #118

A finding of a reviewer on the change request of a run gets an answer with no session of a person. An agent corrects it or drops it with the reason, in a new commit on the branch of the run.

## What starts an answer

A rule of the contract, `run.answer_start`, a choice from `factory` to `person`. With `factory`, the workflow `run` starts after each run of a reviewer workflow on a branch `run/**`. With `person`, or without a value, a person starts each answer by hand with the number of the change request. So a repo that moves to this version gets no new use of a subscription without a written choice. The organization sets the value, and a repo can move it toward `person`.

## What changes

- `charter-gate answer`: the decision. An answer starts for the open change request of a run of this repo, when each reviewer that takes part reported on the head commit, a report is open at the threshold or has no severity line, no open loop is at the limit of rounds, and no answer handled that commit before. Without a limit of rounds in the contract, the factory starts no answer. A script counts the rounds from the reports of the reviewers; the agent does not.
- The workflow `run`: a job `decide` that starts no agent, and the job `run` in a second mode. The agent of an answer works under the same sandbox and the same settings, and holds no token of the code host. The steps of the toolchain run on the files of the main branch; the branch of the run is opened only for the agent.
- `charter-run`: the brief of an answer, with the reports of the reviewers as data; a commit that names the round; the command `body`, which adds each new line `Dropped finding:` to the text of the change request, with the words `by the agent of a run:` in it, and no other line of the agent; the outcome of an answer as a comment on the change request.
- The facts: the branch and the state of the change request, the head commits that an answer handled, and the fact `run` as the sum of the blocks of the text. The verdict and the record name the number of the runs of an agent.
- The merge by the verdict: one more condition. The verdict merges no change request that holds a finding that an agent of a run dropped; a person reads the reason.
- The skill `review-loop`: on the branch of a run with `factory`, a session answers no finding.
- `docs/contract.md`, `docs/product.md`, the hand steps of the setup step. Both manifests: 0.3.19.

Intent: `intents/answer-findings.md`. Plan: `plans/answer-findings.md`.

## Checks

Checks 1 to 13 pass on this branch. The code host read the new workflow file on a test branch, which is removed: both jobs were skipped for a push, as the file says.

Check 14 is manual and open: an answer at an adopter with `run.answer_start = "factory"`. The code host starts a workflow after another one only from the main branch, so it follows the release.
