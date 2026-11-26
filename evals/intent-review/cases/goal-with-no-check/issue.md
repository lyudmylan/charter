#99 The contract names the test of the product as a whole, and a change request needs its result

## Goal
A repo with code declares how its product is started and tested as a whole, a change request to the code needs that test to pass, and an agent can run it during its work.

`checks.quality` lists commands, and nothing says that one of them tests the product as a whole. A repo passes each gate with unit tests alone. A review of the code reads the change; it does not show that the product works. An adopter in 2026-11 has a design for such a test, the replay of recorded runs with no model call, and nothing in its contract asks for it.

## In scope
- A field of the contract, `checks.product`: the commands that start the product and test it from the outside, as a user or a caller meets it.
- The contract checks fail when a repo declares code paths and names no product test. The intent decides how a repo that has no product to start yet records that, with a reason.
- The product test runs in the workflow `tests`. Its result is a fact of the verdict, and the evidence record names it.
- A run without a person (#92) runs the product test inside the boundary (#91) before it ends, so the test needs no network and no secret, or the contract names the part that runs in the CI only.
- The intent of a work item that changes the behaviour of the product names the scenario of the product test that shows the change. The template of an intent and the tracker skill say so.
- The setup step asks for the product test, and prints it as a manual step when none is given.
- The contract of this repo names its own: the setup step makes a repo in an empty folder, and the checks and the gates run on it.
- `docs/contract.md` and `docs/product.md`, the Test row of the lifecycle map.

## Out of scope
- Charter writes no product test. Each product defines how it starts and what shows that it works.
- Scenarios that are kept outside the repo, so that the author agent does not see them: a decision of the leader, later.
- A check of how good a product test is.
- Evals for the skills that a product ships.

## Sources
- Official: the best practices of Claude Code ("make sure it knows what done looks like, can check its own work"; its command `/verify` builds and runs the app, which "catches the kind of problem that tests and typechecks miss"). "Harness engineering" of OpenAI: the app starts for each change, so that the agent tests its own change.
- Community: the report of StrongDM (scenarios kept outside the repo).

Intent: `intents/product-test.md`
