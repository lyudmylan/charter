The evidence record holds the outcome and the cost of an agent run

Closes #93

The intent, the plan, and the code of one work item, in one change request. It is built on #100 and #103 to #109 and holds their commits; merge those first. The check `verdict` is red until #104 is merged, and `review-code` until #106 is merged.

What it adds:
- The publishing step of the workflow `run` adds one block to the text of the change request: the commit that the run published, and the turns, the duration, and the cost that Claude Code reports.
- The facts collector reads the block, and the gate gives the run one of three outcomes: `success` (the head commit is the one of the run, the verdict is ready, no reviewer has an open finding at the threshold), `flawed` (the head commit is the one of the run, and the verdict is not ready or a reviewer has such a finding, also in its shadow period), `manual` (a later push changed what the run built). The fourth outcome of the model, `blocked`, is a run with no change request; it stays on the issue.
- The verdict prints one line for the run, and the evidence record holds the outcome and the three numbers.
- The outcome is information. It changes no readiness and no merge decision. The cost is the estimate of Claude Code, not a bill.

Evidence: 269 tests pass, 11 of them new. Nine faults put into the code on purpose each made a test fail.

An Opus subagent wrote the code and the tests from the plan. The author session wrote the intent and the plan and read the change.
