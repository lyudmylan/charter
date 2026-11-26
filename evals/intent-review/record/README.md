# The record of the full runs of the test set

Each folder is one full run: `report.md` with the numbers, `result.json`, and each report of the reviewer
under `reports/`. The command wrote these files; nobody changed them.

- `2026-11-26/`: the first full run, check 10 of `intents/intent-reviewer-test-set.md`. 25 cases, the model
  `sonnet`. 16 right, 7 false alarms, no miss, 2 on another subject, each case with a report.
- `2026-11-26-pass-cases-run-2/` and `2026-11-26-pass-cases-run-3/`: the 11 cases with the answer `passes`,
  two more times, the model `sonnet`. Over the three runs: 3 cases were never blocked, 4 cases were blocked
  in each run, and 4 cases were blocked in one or two runs of three.
