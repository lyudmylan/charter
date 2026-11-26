# The test set of the intent reviewer: one run

Cases: 17. Right: 14. The threshold of the contract: medium.
False alarms: 0. Misses: 0. Another subject: 3. No report: 0.
Model: sonnet. Claude Code: 2.1.332 (Claude Code). Cost that the runs report: 7.21 USD.

A false alarm: the right answer passes, and the reviewer gave a finding at the threshold or above.
A miss: the right answer blocks, and the reviewer gave no such finding.
Another subject: the reviewer blocks, and no finding at the threshold names the subject of the case.

| Case | Right answer | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-product-test` | passes | none | right | 21 |
| `adopter-after-the-correction-time-limit` | passes | low | right | 20 |
| `adopter-behaviour-with-no-check` | blocks | blocker | right | 27 |
| `adopter-definition-in-two-places` | blocks | high | right | 34 |
| `adopter-pass-rule-with-parts-not-tested` | blocks | high | right | 24 |
| `adopter-scope-sentence-with-no-check` | blocks | high | right | 27 |
| `after-the-correction-no-status-line` | passes | none | right | 18 |
| `condition-stated-without-its-limit` | blocks | high | right | 22 |
| `goal-with-no-check` | blocks | high | other subject | 28 |
| `intent-against-the-product-document` | blocks | blocker | other subject | 23 |
| `items-of-the-issue-left-out` | blocks | high | right | 24 |
| `manual-check-with-no-review-clause` | blocks | high | right | 26 |
| `no-scenario-of-the-product-test` | blocks | medium | right | 27 |
| `one-name-for-two-facts` | blocks | high | other subject | 26 |
| `rule-differs-between-intent-and-plan` | blocks | high | right | 23 |
| `scope-against-out-of-scope` | blocks | high | right | 25 |
| `scope-with-no-check` | blocks | high | right | 30 |

Contested cases: 8, no part of the count. The reviewer blocked 7 of them.
The answer of a contested case waits for a person: the case says why.

| Case | Answer that is contested | Highest open severity | Result | Turns |
|---|---|---|---|---|
| `adopter-after-the-correction-endpoint` | passes | medium | not counted | 23 |
| `after-the-correction-code-reviewer` | passes | high | not counted | 25 |
| `after-the-correction-product-test` | passes | low | not counted | 24 |
| `after-the-correction-toolchain` | passes | medium | not counted | 17 |
| `after-the-correction-update-a-repo` | passes | medium | not counted | 17 |
| `first-round-runs-wait-in-order` | passes | high | not counted | 16 |
| `first-round-status-lines-removed` | passes | high | not counted | 21 |
| `merged-state-one-closing-line` | passes | medium | not counted | 17 |
