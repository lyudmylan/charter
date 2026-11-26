#118 An agent answers the findings of the reviewers on the change request of a run

## Goal

A finding of a reviewer on the change request of a run gets an answer with no session of a person: a correction, or a dropped finding with its reason.

## The gap

The review loop has two sides. The reviewers run on the code host for each push. The author side, the skill `review-loop`, runs in a session of a person. After a run of an agent, no author is there: the run is over when the change request is published. `docs/contract.md` says it: "A finding of a reviewer on it is for a person in this version."

An adopter met it on 2026-11-22, on the first change request that a run built. The reviewer of the code had one low finding. To correct one line, the person opens an issue, writes an intent, merges it, and starts a second run. For a finding at the threshold or above, the loop stays open and nobody answers it.

## In scope

- What starts the author side after a report of a reviewer on the change request of a run, and how the stop rule of the contract counts its rounds.
- The author side works under the boundary and in the sandbox, as the first run does, and holds no token of the code host.
- The record of the run counts each round: the turns, the duration, the cost.

## Out of scope

- The merge by the verdict, #13.
- A finding that the leader marks as false: only a person writes that line.

## Decisions made

- The agent puts its correction in the same change request: a new commit on the branch of the run (leader, 2026-11-22). The two official sources differ on this point; see "Sources".
- The factory starts the author side by itself, after a report of a reviewer with a finding at the threshold or above, within the limit of rounds of the contract (leader, 2026-11-24). The two official sources differ on this point too; see "Sources".
- The start is a rule of the contract: the organization sets it, and a repo can move it toward the start by a person, as with each rule that has a direction (leader, 2026-11-24).
- Without a value from the organization, a person starts each round: a repo that moves to a new version of Charter gets no new use of a subscription without a written choice (leader, 2026-11-24).

## Decided in the intent

- Each round is a new run of the workflow.
- A finding below the threshold: the agent corrects it only when it is one line of work.
- The agent answers the findings of both reviewers, also in the shadow period of the reviewer of the code.
- A finding that needs a change of a closed path, the intent among them, is for a person.

Part of the epic #82.

Intent: intents/answer-findings.md

## Sources

Read on 2026-11-22. Both are official.

- Anthropic, the documentation of Claude Code for GitHub Actions: a person starts each round with a mention in a comment of the change request, and the agent pushes to the same change request. The page shows no loop in which an agent answers a review with no person, and it says that a bot cannot start the agent, to prevent a loop. It advises a limit of turns and a time limit of the workflow.
- OpenAI, the example workflow of the Symphony repository: after review feedback the issue goes to the state `Rework`. There the agent closes the change request and starts again on a new branch from the main branch. The two sources differ on this point, so the leader decides it.
- On the start of the answer, read on 2026-11-24. Anthropic, the same page: a person starts each round. OpenAI, the same workflow: before the agent hands the change request to a person, it answers each reviewer comment, of a person or of a bot, with a change or a reasoned reply, and no person starts that. The two differ, and the leader chose the start by the factory.
