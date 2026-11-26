# The record of the full runs of the test set

Each folder is one run: `report.md` with the numbers, `result.json`, and each report of the reviewer under
`reports/`. The command wrote these files; nobody changed a report. The numbers were graded again on
2026-11-26 with `--reports`, after the match of the subject became stricter and 8 cases became contested.

- `2026-11-26/`: the first full run, check 12 of `intents/intent-reviewer-test-set.md`. 25 cases, the model
  `sonnet`. Of the 17 counted cases 14 are right: each of the 14 `blocks` cases was blocked, 11 on the
  subject of the case and 3 on another subject, and each of the 3 `passes` cases passed. Of the 8 contested
  cases the reviewer blocked 7.
- `2026-11-26-pass-cases-run-2/` and `2026-11-26-pass-cases-run-3/`: the 11 cases with the answer `passes`,
  two more times. Over the three runs: 3 cases were never blocked, 4 cases were blocked in each run, and 4
  cases were blocked in one or two runs of three.
