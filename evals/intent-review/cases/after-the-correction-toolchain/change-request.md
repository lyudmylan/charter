The workflows have a declared place for the toolchain of the repo

Closes #88

The intent, the plan, and the code of one work item, in one change request. It is built on #100 and #103 to #107 and holds their commits; merge those first. The check `verdict` is red until #104 is merged, and `review-code` until #106 is merged; the cause of each is in the text of #105 and #106.

What it adds:
- A marked block in the workflow `tests`, between `# charter:toolchain:start` and `# charter:toolchain:end`, after the checkout and before the quality step. It holds the steps that install what the quality commands of a repo need.
- The setup step takes `--toolchain FILE` and puts the steps of the file into the block. Without the flag the block is empty.
- A function reads the block back, for the update of a repo (#97) and for the workflow of a run (#92).
- The three workflows that run on a change request use the checkout action at `v7`. The verdict workflow stays at `v4`: it runs from the main branch, and it moves in a change of its own after this proof.

Evidence: 238 tests pass, 7 of them new. Seven faults put into the code on purpose each made a test fail. The author also wrote a workflow with three steps of a TypeScript toolchain through the setup step and read it with a YAML parser: it is valid, with six steps in the right order.

The checks `tests` and `review-intents` of this change request run with the new checkout action; that is the manual check 8 of the intent.

An Opus subagent wrote the code and the tests from the plan. The author session wrote the intent and the plan and read the change.

No document change: the product document does not describe the setup of a toolchain; `docs/contract.md` does, and it changes here.
