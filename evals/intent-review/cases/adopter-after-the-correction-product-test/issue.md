#3 A test starts product, sends events, and checks the messages that came out

## Goal
The product tests itself as a whole. One test starts product as a process, sends events to its HTTP endpoint, reads what the recording channel wrote, and stops product.

## In scope
- The scenario "an urgent event gets one knock".
- The scenario "an event that is not urgent gets no message".
- The test starts and stops product by itself. It needs no other host, no secret and no model call.
- The place for the scenarios of later work items.

## Out of scope
- A command of its own for this test, and the line in the contract: the next issue of this epic.
- The scenarios of the product lab. They need the agent that investigates and a model.

Intent: `intents/product-test.md`
