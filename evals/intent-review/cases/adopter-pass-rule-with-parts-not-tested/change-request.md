Intent: a test starts product, sends events, and checks the messages that came out

Part of #3

This change request adds the intent of the third work item of the thin path (#5): the test of the product. It changes no code. The work on it starts after the code of #2 is on the main branch.

## What the intent says
- One command, `node product-test/run.ts`, starts product as a process, sends the events of each scenario, compares the messages that came out with the known answer, and stops product.
- A scenario is one JSON file: its name, its events, and its known answer. A later work item adds a scenario as one file.
- The first two scenarios: "an urgent event gets one knock" and "an event that is not urgent gets no message".
- Six automatic checks and no manual check. Three of them show that the test of the product fails when it must.

## Choices that need a decision at the review
- Each scenario gets its own process of product and its own record file. So no scenario sees the events of another one.
- The scenarios of this test are in `product-test/scenarios/`. They are apart from the scenarios of the product lab, which need the agent that investigates and a model (#12).
- The known answer of a scenario holds each message in full: its level, the identity and the start time of its event, and the name of the rule that decided.
- The line of the contract that names this command comes with #4.
