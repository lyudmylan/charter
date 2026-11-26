The contract names the test of the product as a whole, and a change request needs its result

Closes #99

The intent, the plan, and the code of one work item, in one change request. It is built on #100 and #103 to #110 and holds their commits; merge those first. The check `verdict` is red until #104 is merged, and `review-code` until #106 is merged.

What it adds:
- Two fields of the contract: `checks.product`, the commands that start the product and test it from the outside, and `checks.no_product_reason`, why a repo has no such test yet.
- The contract checks fail for a repo with code paths that names neither. So each repo with code says one of the two.
- A gate `charter-gate product` and a second job, `product`, in the workflow `tests`. It runs the code of the change request with no secret. The verdict reads the check `product`, so a failed product test makes the change request not ready.
- The verdict prints one line for the product test. A repo without one shows its reason at each merge.
- The brief of an agent run tells the agent to run the product test in its sandbox.
- The template of an intent and the reviewer of intents ask a work item that changes the behaviour of the product for its scenario of the product test.
- This repo names its own product test: one script makes a repo with the setup step in an empty folder, through the commands of `charter/bin`, and runs the contract checks, the quality gate, the boundary gate, and a verdict on it.

Charter writes no product test for an adopter. Each product says how it starts and what shows that it works.

Evidence: 283 tests pass, 14 of them new. Ten faults put into the code on purpose each made a test or the product test fail. The job `product` runs on this change request itself, from its branch.

One effect on the day of the merge: the verdict then reads the check `product` on each open change request. A change request that was opened before needs the main branch merged in, so that its workflow `tests` has the new job.

An Opus subagent wrote the code and the tests from the plan. The author session wrote the intent and the plan, read the change, and ran the product test.
