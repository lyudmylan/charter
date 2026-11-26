#50 A repeat of an open event gets no second message

## Goal
A repeat of an open event gets no second judgement and no second message. product keeps the state of each event that it saw.

## In scope
- The core gets an interface for the store of events, and a store in memory sits outside the core.
- A repeat of an open event starts nothing. The same identity with another start time is a new event. An event that was closed starts nothing again.
- An event whose message failed is judged again at its repeat, so a failed channel loses no knock.
- Three new scenarios in the test of the product.

## Out of scope
- The state of the events after a restart of product: it comes with the record store.
- The result of the agent, the time limit, and the format of a detector: each is a later work item of this epic.

Intent: `intents/event-repeats.md`
