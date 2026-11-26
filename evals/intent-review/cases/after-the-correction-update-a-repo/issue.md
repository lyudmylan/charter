#97 A repo that is set up moves to a new version of Charter with one command

## Goal
A repo that is set up moves to a new version of Charter with one command and one change request, and no step of a workflow is copied by hand.

The setup step refuses a file that exists, so it serves the first day only. A later version of Charter that changes a workflow reaches an adopter as a hand copy: one version in 2026-11 needed two workflow steps copied by hand. The issues of this milestone change the workflow `tests`, add a workflow for the run, and change the verdict workflow.

## In scope
- An update command. For a file that holds no content of the repo, such as a workflow, it writes the file of the new version and shows the difference. For a file that holds content of the repo (the contract, the instructions, a document) it changes nothing and names what the new version adds: a field with its default, a rule line.
- The declared place for the toolchain of the repo (#88) stays through an update.
- The version in the contract moves with the update.
- The result is a change of the repo like any other: an issue, a branch, a change request in the tier of its files.
- Tests: an update from the version before to this one in a repo that the setup step made; a workflow that the repo changed by hand is named and not lost without notice.

## Out of scope
- A change of the schema version of the contract.
- A run of an agent that opens the update as a change request.

Intent: `intents/update-a-repo.md`
