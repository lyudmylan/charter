# The test set of the intent reviewer: one run

Cases: 11. Right: 6. The threshold of the contract: medium.
False alarms: 5. Misses: 0. Another subject: 0. No report: 0.
Model: sonnet. Claude Code: 2.1.332 (Claude Code). Cost that the runs report: 2.47 USD.

A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.
A miss: the right answer blocks, and the reviewer gave no such finding.
Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.

| Case | Right answer | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-endpoint` | passes | none | right | 23 |
| `adopter-after-the-correction-product-test` | passes | none | right | 20 |
| `adopter-after-the-correction-time-limit` | passes | low | right | 23 |
| `after-the-correction-code-reviewer` | passes | medium | false alarm | 21 |
| `after-the-correction-no-status-line` | passes | low | right | 14 |
| `after-the-correction-product-test` | passes | medium | false alarm | 22 |
| `after-the-correction-toolchain` | passes | none | right | 15 |
| `after-the-correction-update-a-repo` | passes | none | right | 16 |
| `first-round-runs-wait-in-order` | passes | high | false alarm | 22 |
| `first-round-status-lines-removed` | passes | medium | false alarm | 15 |
| `merged-state-one-closing-line` | passes | medium | false alarm | 18 |
