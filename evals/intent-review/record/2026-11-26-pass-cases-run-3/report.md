# The test set of the intent reviewer: one run

Cases: 3. Right: 3. The threshold of the contract: medium.
False alarms: 0. Misses: 0. Another subject: 0. No report: 0.
Model: sonnet. Claude Code: 2.1.332 (Claude Code). Cost that the runs report: 2.56 USD.

A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.
A miss: the right answer blocks, and the reviewer gave no such finding.
Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.

| Case | Right answer | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-product-test` | passes | low | right | 20 |
| `adopter-after-the-correction-time-limit` | passes | low | right | 26 |
| `after-the-correction-no-status-line` | passes | none | right | 18 |

Contested cases: 8, no part of the count. The reviewer blocked 7 of them.
The answer of a contested case waits for a person: the case says why.

| Case | Answer that is contested | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-endpoint` | passes | medium | not counted | 24 |
| `after-the-correction-code-reviewer` | passes | medium | not counted | 26 |
| `after-the-correction-product-test` | passes | medium | not counted | 18 |
| `after-the-correction-toolchain` | passes | low | not counted | 13 |
| `after-the-correction-update-a-repo` | passes | medium | not counted | 17 |
| `first-round-runs-wait-in-order` | passes | medium | not counted | 17 |
| `first-round-status-lines-removed` | passes | medium | not counted | 21 |
| `merged-state-one-closing-line` | passes | medium | not counted | 24 |
