# Intent: this repo moves to Charter 0.3.17

Work item: #38. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.17, and the run workflow and the template of an intent are the files that
the setup step of that version writes, so that the faults that the first runs of an agent showed here are
gone.

## In scope

- Why: the first runs of an agent in this repo showed three faults of Charter. The text of the change
  request of a run held the line `Closes #N` two times, one from the workflow and one from the agent. A run
  that waited was cancelled when a person started one more run. The line `Status: planned` of an intent
  stayed after a run built the work item, because a run cannot change a file under `intents/`. Charter
  0.3.17 corrects the three.
- `charter.toml`: the version 0.3.17. The contract of this repo gets no new field.
- `.github/workflows/run.yml`: the file of the setup step of 0.3.17. A script of Charter writes the text of
  the change request, with the closing line one time. The group of the workflow has `queue: max`, so each
  started run waits in the order of its start.
- `intents/_template.md`: the file of the setup step of 0.3.17. The line of the work item holds no status.
- The six intents of this repo that held `Status: planned` lose it. No other text of them changes. The
  state of the issue says whether a work item is built.
- One change request. The version adds no field to the contract, so the checks of 0.3.16, which run from
  the main branch, read the changed contract.

## Out of scope

The change requests of runs that are open at the time of this change: their text stays as it is. The
other workflows: the setup step of 0.3.17 writes them as they are.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.17.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names the version 0.3.17.
   command: `grep -q '^version = "0\.3\.17"$' charter.toml`
4. The group of the run workflow keeps each run that waits.
   command: `grep -q '^  queue: max$' .github/workflows/run.yml`
5. A script of Charter writes the text of the change request of a run.
   command: `grep -qF 'charter_run.py" text --number' .github/workflows/run.yml`
6. No intent and no line of the template holds a status.
   command: `sh -c '! grep -rq "^Work item.*Status:" intents'`

## Manual checks

7. Each of the five workflows, `AGENTS.md`, and the two templates is the file that the setup step of
   0.3.17 writes with the values of this repo and its toolchain steps.
   who: the engineer, with a setup in an empty folder and a comparison of the files. Not automatic:
   Charter has no command yet that updates a repo.
8. The text of the change request of the next run of an agent holds the line that closes its issue one
   time.
   who: the leader. Not automatic: the check needs a model call, a machine of the code host, and the
   label that a person puts.
