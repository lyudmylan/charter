#116 The change request of a run holds the line that closes its issue one time

## Goal

The text of the change request of a run holds the line `Closes #N` one time.

## The defect

The first run that ended with a change request, at an adopter on 2026-11-22, wrote the line two times. The publishing step of the run workflow writes it as the first line. The agent reads in `AGENTS.md` that a change request closes its issue, so the text that it wrote starts with the same line. The brief does not say that the workflow adds the line.

## In scope

- The publishing step writes the line only when the text of the agent does not hold it, or the brief tells the agent to leave the line out. The intent chooses.
- A test with a text of the agent that holds the line.

## Out of scope

Other parts of the text that the agent writes for the change request.

Part of the epic #82.

Intent: intents/one-closing-line.md
