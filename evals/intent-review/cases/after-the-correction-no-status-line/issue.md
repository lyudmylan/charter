#117 The status line of an intent is true after a run of an agent

## Goal

The status line of an intent is true after a run of an agent built its work item.

## The gap

The template of an intent holds `Status: planned`. In a session with a person, the author changes it to `done` in the change request that builds the work item; the plan names that step. A run of an agent cannot do it: the boundary closes `intents/**` to a run. An adopter met it on 2026-11-22: after a run, the intent says `planned` for a work item that is built, and the reviewer of the code marks the line as stale on each such change request.

In this repo the line also has a function: the test of the intents lets an intent with `planned` name a test that does not exist yet.

## Decisions made

The status line leaves the intent (leader, 2026-11-22). The state of the issue says whether the work item is built. The test of the intents of this repo reads another fact in its place: the plan of the intent exists, and a plan arrives together with the code.

## In scope

The template of an intent, the test of the intents, and the intents of this repo.

## Out of scope

Other closed paths that a run may need to change.

Part of the epic #82.

Intent: intents/no-status-line.md
