# The test set of the intent reviewer: one run

Cases: 3. Right: 3. The threshold of the contract: medium.
False alarms: 0. Misses: 0. Another subject: 0. Form not read: 0. No report: 0.
Model: sonnet. Claude Code: 2.1.332 (Claude Code). Cost that the runs report: 2.47 USD.

A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.
A miss: the right answer blocks, and the reviewer gave no such finding.
Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.
Form not read: the reviewer blocks, and the command reads no finding at the threshold in the report.

| Case | Right answer | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-product-test` | passes | none | right | 20 |
| `adopter-after-the-correction-time-limit` | passes | low | right | 23 |
| `after-the-correction-no-status-line` | passes | low | right | 14 |

Contested cases: 8, no part of the count. The reviewer blocked 5 of them.
The answer of a contested case waits for a person: the case says why.

| Case | Answer that is contested | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-endpoint` | passes | none | not counted | 23 |
| `after-the-correction-code-reviewer` | passes | medium | not counted | 21 |
| `after-the-correction-product-test` | passes | medium | not counted | 22 |
| `after-the-correction-toolchain` | passes | none | not counted | 15 |
| `after-the-correction-update-a-repo` | passes | none | not counted | 16 |
| `first-round-runs-wait-in-order` | passes | high | not counted | 22 |
| `first-round-status-lines-removed` | passes | medium | not counted | 15 |
| `merged-state-one-closing-line` | passes | medium | not counted | 18 |
