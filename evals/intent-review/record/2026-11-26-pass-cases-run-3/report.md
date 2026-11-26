# The test set of the intent reviewer: one run

Cases: 11. Right: 4. The threshold of the contract: medium.
False alarms: 7. Misses: 0. Another subject: 0. No report: 0.
Model: sonnet. Claude Code: 2.1.332 (Claude Code). Cost that the runs report: 2.56 USD.

A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.
A miss: the right answer blocks, and the reviewer gave no such finding.
Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.

| Case | Right answer | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-endpoint` | passes | medium | false alarm | 24 |
| `adopter-after-the-correction-product-test` | passes | low | right | 20 |
| `adopter-after-the-correction-time-limit` | passes | low | right | 26 |
| `after-the-correction-code-reviewer` | passes | medium | false alarm | 26 |
| `after-the-correction-no-status-line` | passes | none | right | 18 |
| `after-the-correction-product-test` | passes | medium | false alarm | 18 |
| `after-the-correction-toolchain` | passes | low | right | 13 |
| `after-the-correction-update-a-repo` | passes | medium | false alarm | 17 |
| `first-round-runs-wait-in-order` | passes | medium | false alarm | 17 |
| `first-round-status-lines-removed` | passes | medium | false alarm | 21 |
| `merged-state-one-closing-line` | passes | medium | false alarm | 24 |
