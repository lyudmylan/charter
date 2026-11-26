<!-- charter-intent-review -->
Commit: 1f629dc31b60afb07c61d5969b19a5f755ee5cf8

| File | Verdict | Finding |
|---|---|---|
| `intents/time-limit-knock.md` | approve with a change | The promise about earlier tests cannot hold with the fourth setting. A `product.md` statement would become stale, and some stated behaviour has no check. |

**1. blocker**: `intents/time-limit-knock.md`, earlier checks

Sentence: "The checks of the earlier intents stay as they are and still pass with `pnpm test`, with one change: each test that calls `judgeEvent` or `open` gives it a time of arrival."

The test `the settings have their defaults` in `tests/settings.test.ts` uses `toEqual` on an object with only `recordFile`, `port` and `host`. With `timeLimitSeconds: 600` in the result, it fails, and the sentence does not allow that change.

Proposed text: "The checks of the earlier intents still pass with `pnpm test`, with two changes: each test that calls `judgeEvent` or `open` gives it a time of arrival, and the test `the settings have their defaults` also expects `timeLimitSeconds` with the value 600."

**2. medium**: `intents/time-limit-knock.md`, document change

Sentence: "The change request has the line `No document change: the product document states this behaviour`."

`docs/product.md` does state the behaviour. Its section "Parts" also says of the core: "Its first code judges an event with one rule, and the rest is not built yet." After this work item, the core also judges at the time limit, so that statement would be wrong.

Proposed text: "`docs/product.md`, section "Parts": the entry of the core says that its first code judges an event at its arrival with one rule and judges at the time limit, and that the rest is not built yet." Remove the `No document change` line from the scope.

**3. medium**: `intents/time-limit-knock.md`, check 10

Sentence: "After `unmarkKnocked` the list holds the event again."

The check covers no event that closes between `markKnocked` and `unmarkKnocked`, as can happen while a failing send runs. A store whose `unmarkKnocked` reopens a closed event would pass this sentence, and the next check would knock for a closed event.

Proposed text: "After `unmarkKnocked` the list holds the open event again. For a marked event that then closed, and for an event that the store does not know, `unmarkKnocked` changes nothing: the list does not hold it, and `open` for the closed one returns false." Add to the scope of `unmarkKnocked`: "For each other event it changes nothing."

**4. medium**: `intents/time-limit-knock.md`, `src/main.ts`

Sentence: "A check does not start while the check before it runs. For each failed message it writes one line to the error output. The stop of the process ends the checks."

No listed check proves the no-overlap rule or the error line. Scenario 06 shows that the periodic check runs, but not how it handles a slow or failing channel. The existing stop path calls `process.exit(0)`, so a clean exit alone does not show that the checks were ended.

Proposed text, as a new automatic check: "A process with a time limit of 1 second and a channel that fails: an event that is not urgent gives a line on the error output after the time limit, the process keeps running, and SIGTERM ends it with the code 0. test: `tests/process.test.ts::a failed knock at the time limit writes an error line`". Also add an automatic check with a named test: while one check waits on a slow channel, no second check starts. If that needs the loop in its own file outside the core, name the file in the scope.

The issue list returned nothing, so no epic of the milestone was reviewed. The consistency review used issue #55, the documents, the earlier intents that were read or searched, and the code.

Highest open severity: blocker