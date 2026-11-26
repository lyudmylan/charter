#93 The evidence record holds the outcome and the cost of an agent run

## Goal
Each agent run without a person leaves a record of how it ended and what it cost. The record is on the change request, or on the issue when the run opened no change request.

The evidence record of a change holds the gates, the review, and the approvals. It says nothing of the run that wrote the change: whether the run finished alone, where it stopped, how long it worked, and at what cost. Without it, the leader cannot see which work items go through a run well, and the grant of more autonomy by evidence (#13) has no evidence of the runs.

## In scope
- The outcome of a run, one of a fixed list. A model with four values is in the report of Vercel on its factory: success, flawed, blocked, manual. The intent fixes the names and the meaning of each.
- The cost of a run: what the runner reports, such as the duration, the number of turns, the tokens, and the cost figure when the host gives one. The intent names the fields after a look at a real run.
- The place: fields of the evidence record. A run with no change request writes its record on the issue.
- The facts collector reads the fields, and the verdict prints them.
- `docs/contract.md` and `docs/product.md`: the fields and where they come from.
- Tests: a record with the fields; a run without a change request; a run that reports no cost.

## Out of scope
- A limit on the cost: #53.
- What a failed run teaches: a new check or a new eval case. A later issue of #83.
- A view across many runs.

## Sources
- Community only: the report of Vercel on its factory (the four outcomes). No official source gives a list of outcomes.

Intent: `intents/record-of-a-run.md`
