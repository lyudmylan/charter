#120 Each started run waits for its turn: a new run cancels no run that waits

## Goal

Each run that a person starts waits for its turn. No run is cancelled because another one was started after it.

## The defect

The run workflow has one concurrency group, with `cancel-in-progress: false`. Its comment and `docs/contract.md` say: "One run works at a time, and a second one waits." This holds for two runs. The documentation of the code host, read on 2026-11-22, says that a group holds at most one waiting run by default, and that a new run cancels the run that waits and takes its place. A person who puts the label `charter-run` on ten issues gets two runs: the first one works, the last one waits, and the code host cancels the eight between them.

The same documentation names an option of the group, `queue: max`: up to 100 runs wait, in the order in which they started to wait.

## In scope

- The option in the template of the run workflow and in the workflow of this repo, with a test.
- The sentence of `docs/contract.md` and the comment of the workflow.
- What the issue of a cancelled run shows. The documentation does not say whether a step of such a run works, so the intent finds it with a test on the code host.

## Out of scope

More than one run at the same time. A limit on the cost of a day.

Part of the epic #82.

Intent: intents/runs-wait-in-order.md
