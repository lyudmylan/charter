Intent: a repeat of an open event gets no second message

Part of #50

The intent of the work item, alone. A run of an agent builds the work item from the issue after the merge of this intent.

- The core keeps the state of each event through an interface, and a store in memory sits outside the core.
- A repeat of an open event starts nothing. An event that was closed starts nothing again. The same identity with another start time is a new event.
- An event whose message failed is judged again at its repeat, so a failed channel loses no knock.
- Three new scenarios in the test of the product.
