# Intent: a repeat of an open event gets no second message

Work item: #50. Approval: a person merges the change request that adds this file.

## Goal

product keeps the state of each event that it saw, so a repeat of an open event starts no second
judgement and sends no second message.

## In scope

Two events are the same when they have the same identity and the same start time. This pair names an
event in each rule below.

- `src/core/event-store.ts`: the interface `EventStore`, through which the core keeps the state of the
  events. It has three operations, and each one takes the identity and the start time.
  - `open` stores the event as open when the store does not know it, and it tells whether it stored it.
    For an event that the store knows, open or closed, it changes nothing and tells so.
  - `close` stores the event as closed, also when the store did not know it.
  - `forget` removes the event, so the store does not know it any more.
  - Each operation is asynchronous, because the record store comes later behind the same interface.
- `src/store/memory.ts`: the class `MemoryEventStore`, a store in memory. It sits outside the core.
- `src/core/judge.ts`: `judgeEvent` takes the store as its fourth value.
  - An open event that the store does not know: the core stores it as open and then judges it with the
    rules, as today. The event stays open also when no rule matched.
  - An open event that the store knows as open is a repeat. The core does not judge it and sends no
    message. This holds also when the value `urgent` of the repeat differs from the first call.
  - An open event that the store knows as closed starts nothing. A closed event stays closed.
  - A closed event: the core stores it as closed and sends no message, as today.
  - The core stores the event before it sends the message. So two calls with the same new event at the
    same time give one message.
  - When the channel fails, the core forgets the event and passes the failure on. So the next call with
    this event is judged again, and a failed channel loses no knock.
- `src/http/endpoint.ts`: the options of the endpoint get the store, and the endpoint passes it to the
  core. A repeat gets the answer 200 with `{"message": null}`. The other answers stay as they are.
- `src/main.ts`: product starts with one `MemoryEventStore`.
- `product-test/scenarios/`, three new scenarios. Each event in them is urgent.
  - `03-repeat-no-second-message.json`: "a repeat of an open event gets no second message". The same
    open event two times, and the known answer is one knock.
  - `04-new-start-time-new-knock.json`: "the same identity with a later start time gets a new knock".
    Two open events with the same identity and two start times, and the known answer is two knocks.
  - `05-closed-event-stays-closed.json`: "an event that was closed starts nothing again". One event as
    open, as closed, and as open again, and the known answer is one knock.
- `tests/product-test/run.test.ts`: two tests hold the count of the scenarios of the repository today.
  They change, so that a new scenario file needs no change of a test. The test `the two first scenarios
  pass` finds its two files by name in the results. The test `the command passes on the scenarios of
  the repository` expects one line with "passed" for each scenario file of the folder.
- `docs/architecture.md`:
  - The section "How the core behaves" gets two sentences: an event that was closed starts nothing
    again, and an event whose message failed is judged again at its repeat.
  - The row "Core" names the interface of the store. The row "Record store" says that
    `src/store/memory.ts` holds the events in memory until the record store exists, and that the events
    do not survive a restart until then.
- The change request has the line `No document change: the product document states this behaviour`.

## Out of scope

The state of the events after a restart: it comes with the record store. A limit on the number of events
in memory. The result of the agent, the time limit, the format of a detector and the token of a sender:
each is a later work item. A second try of a failed push by product itself: it comes with the channel to
a phone. A change of a package file, of the contract, or of an intent that is already merged.

## Acceptance checks

## Automatic checks

1. The same open urgent event two times: the first call sends one knock, and the second call sends no
   message and gives no message back.
   test: `tests/core/judge.test.ts::a repeat of an open event gets no message`
2. An open event that is not urgent, and then the same event as urgent: no call sends a message.
   test: `tests/core/judge.test.ts::a repeat is not judged again when its value urgent differs`
3. Two open urgent events with the same identity and two start times: each one gets its knock.
   test: `tests/core/judge.test.ts::the same identity with another start time is a new event`
4. One urgent event as open, as closed, and as open again: the channel holds one knock.
   test: `tests/core/judge.test.ts::an event that was closed starts nothing again`
5. An urgent event that arrives closed first and open after it: the channel holds no message.
   test: `tests/core/judge.test.ts::an event that arrives closed first starts nothing`
6. Two calls with the same new urgent event start at the same time, with a channel that answers after a
   pause: the channel holds one knock.
   test: `tests/core/judge.test.ts::two calls with the same new event at the same time give one message`
7. A channel that fails at the first message and works after it: the first call with an urgent event
   fails, and the second call with the same event sends one knock.
   test: `tests/core/judge.test.ts::an event whose message failed is judged again at its repeat`
8. The store in memory: `open` tells "stored" at the first call and "not stored" at the second one. After
   `close`, `open` tells "not stored". After `forget`, `open` tells "stored" again. An event with the
   same identity and another start time is another event.
   test: `tests/store/memory.test.ts::the store knows an event by its identity and its start time`
9. Two calls of `POST /events` with the same open urgent event: each gets the answer 200, the first with
   `{"message": "knock"}` and the second with `{"message": null}`.
   test: `tests/http/endpoint.test.ts::a repeat of an open event gets the answer null`
10. The check on the imports of the core still passes: the core imports no file outside the core, and
    `src/store/memory.ts` is outside the core.
    test: `tests/core/boundary.test.ts::the core imports no file outside the core`
11. The test of the product passes with the five scenarios.
    command: `node product-test/run.ts`
12. With the five scenarios in the folder, the two tests of `tests/product-test/run.test.ts` that read the
    scenarios of the repository pass. They hold no count of the scenarios, so a later scenario file needs
    no change of a test.
    test: `tests/product-test/run.test.ts::the command passes on the scenarios of the repository`

The checks of the earlier intents stay as they are and still pass with `pnpm test`, with one change: each
test that calls `judgeEvent` or creates the endpoint gives it a store.

The scenarios of the test of the product that show this work item are the three new ones:
`03-repeat-no-second-message.json`, `04-new-start-time-new-knock.json` and
`05-closed-event-stays-closed.json`.

## Manual checks

None.
