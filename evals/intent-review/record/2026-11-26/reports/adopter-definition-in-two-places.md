<!-- charter-intent-review -->
Commit: ca492284434cdc54293ccf7a13926e9cd1aae3cf

| File | Verdict | Finding |
|---|---|---|
| `intents/event-repeats.md` | approve with a change | `forget` can erase a closed state, which breaks "A closed event stays closed". The reason for no product document change is only partly true, the checks do not require the new scenarios, and the scenario list appears twice. |

The epic was not checked. Issue #50 mentions it without a number, and the attempt to read #6, which earlier intents cite for this behaviour, failed.

**1. high**, `intents/event-repeats.md`

Sentences: "`forget` removes the event, so the store does not know it any more." and "So the next call with this event is judged again, and a failed channel loses no knock."

- **Closed state:** an open call stores the event and waits for the channel. A close call then stores it as closed. If the send fails, `forget` removes that closed state, so a later open call can knock. No check covers this order.
- **Overlapping repeat:** a repeat that arrives during the send gets 200 with `null`, even if that send then fails. The knock then depends on the sender sending the event again.

Proposed text:
- For `forget`: "`forget` removes an event that the store knows as open. A closed event stays closed."
- For the second sentence: "So the next call with this event is judged again, unless the event was closed in the meantime. A repeat that arrives during the send gets no message, so after a failed send the knock needs a later call from the sender."
- In check 8, replace the `close` and `forget` sequence: "After `forget` of an open event, `open` tells "stored" again. After `close`, `open` tells "not stored", also after a later `forget`."
- Add a check: "The event is closed while its send waits, and the send then fails: a later open call sends no message. test: `tests/core/judge.test.ts::a failed send does not reopen a closed event`"

**2. medium**, `intents/event-repeats.md`

Sentence: "The change request has the line `No document change: the product document states this behaviour`."

`docs/product.md` says only that a repeat sends no second message. It does not say that a closed event stays closed, or that an event is judged again after a failed send. Its section "Parts" says of the core: "Its first code judges an event with one rule, and the rest is not built yet." That would omit the new handling of repeats.

Proposed text: "`docs/product.md`, the section "Parts": the sentence about the first code of the core becomes "Its first code judges an event with one rule and sends no second message for a repeat of an open event, and the rest is not built yet.""

**3. medium**, `intents/event-repeats.md`

Sentences: "The test of the product passes with the five scenarios." and "They hold no count of the scenarios, so a later scenario file needs no change of a test."

The command in check 11 also passes with only the two old scenarios. So does the test in check 12 once it expects one line per file. Passing with five files also cannot show that neither test holds a fixed count; a count of five would pass.

Proposed text:
- Add a check: "The results for the scenarios of the repository hold `03-repeat-no-second-message.json`, `04-new-start-time-new-knock.json` and `05-closed-event-stays-closed.json`, each as passed. test: `tests/product-test/run.test.ts::the scenarios of the repeats pass`"
- In check 12, keep the first sentence. Replace the second with a manual check: "Neither of the two tests holds a count of the scenarios. who: the reviewer of the code. Not automatic: a passing run cannot show that a later file needs no change of a test." Replace "None." under "Manual checks" with it.

**4. medium**, `intents/event-repeats.md`

Sentence: "The scenarios of the test of the product that show this work item are the three new ones: `03-repeat-no-second-message.json`, `04-new-start-time-new-knock.json` and `05-closed-event-stays-closed.json`."

This repeats the list under "In scope". If the check proposed in finding 3 names the files, it adds another copy that this sentence does not need.

Proposed text: "The three new scenarios under "In scope" show this work item."

Highest open severity: high