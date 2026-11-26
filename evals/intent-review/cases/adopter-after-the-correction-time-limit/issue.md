#55 An event with no result gets a knock when the time limit passes

## Goal
An open event that has no knock gets a knock when the time limit passes. The time limit starts when the event arrives at product.

## In scope
- The store of events keeps the time at which each event arrived, and whether the event got a knock.
- The core judges at the time limit: an open event with no knock gets one knock. An event that closed gets none, and an event that got a knock at its arrival gets no second one.
- The time limit is a setting of the process, in seconds, with a default.
- product checks the time limits each second.
- A scenario of the test of the product can carry settings for its process and a wait before the messages are read. Three new scenarios.

## Out of scope
- The result of the agent: it is a later work item of this epic. Until it exists, no result stops the time limit.
- The time limit as a setting of a team, and its default from a measurement in the lab.
- The time limits after a restart of product: they come with the record store.

Intent: `intents/time-limit-knock.md`
