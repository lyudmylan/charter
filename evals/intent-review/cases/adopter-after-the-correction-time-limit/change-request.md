Intent: an event with no result gets a knock when the time limit passes

Part of #55

The intent of the work item: an open event that has no knock gets one knock when the time limit passes.

## What the intent decides

- The time limit starts at the arrival of the event. A repeat does not start it again.
- The knock at the time limit goes to an open event that has no knock. An event that got a knock at its
  arrival gets no second one, and an event that closed gets none.
- The time limits are in the store of events. The core takes the time of a check as a value and holds
  no clock. product checks each second.
- The setting `PRODUCT_TIME_LIMIT_SECONDS` has the default 600, until the lab measures the agent.
- A knock that failed at the time limit is sent at the next check.
- A scenario of the test of the product can carry settings for its process and a wait.

Until the result input exists, no result stops the time limit: each open event with no knock gets a
knock when the time limit passes.
