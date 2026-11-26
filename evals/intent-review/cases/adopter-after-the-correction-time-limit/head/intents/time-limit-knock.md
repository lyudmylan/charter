# Intent: an event with no result gets a knock when the time limit passes

Work item: #55. Approval: a person merges the change request that adds this file.

## Goal

An open event that has no knock gets one knock when the time limit passes, so an event with no result
does not stay without a person.

## In scope

An event is named by its identity and its start time, as `docs/architecture.md` defines it. An event
waits while it is open and has no knock. The time limit of an event starts at its arrival, and it passes
when the time limit in seconds is over.

- `src/core/event-store.ts`: the interface `EventStore` changes.
  - `open` takes a third value, the time of the arrival as a `Date`, and stores it with a new event. For
    an event that the store knows, it changes nothing, also not the time of the arrival.
  - `markKnocked` takes the identity and the start time. For an event that waits, it stores that the
    event got a knock and returns true. For each other event, known or not, it changes nothing and
    returns false.
  - `unmarkKnocked` takes the identity and the start time. An open event that is marked waits again.
  - `waitingSince` takes a time as a `Date`. It gives the events that wait and that arrived at this
    time or before it, in the order of their arrival, each as an object with `identity` and
    `startTime`.
  - `close` and `forget` stay as they are.
- `src/store/memory.ts`: `MemoryEventStore` has the new operations.
- `src/core/judge.ts`: `judgeEvent` takes the time of the arrival as its fifth value and gives it to
  `open`. When the rule asks for a knock, the core marks the event before it sends the message. An event
  with a quiet message, and an event with no rule, wait. The rest stays as it is.
- `src/core/time-limit.ts`, new: the judgement at the time limit.
  - `judgeTimeLimit` takes the time of the check as a `Date`, the time limit in seconds, the channel and
    the store. The core holds no clock: the caller gives the time.
  - It asks the store for the events that wait and whose time limit passed. An event is in this list
    from the moment at which its age equals the time limit.
  - For each event it calls `markKnocked`. At true it sends one knock. At false it sends nothing: the
    event closed in the meantime, or another check took it. So two checks at the same time give one
    knock.
  - The knock names the event, and its value `rule` is the text of the constant `TIME_LIMIT_RULE`:
    `the time limit passed with no result`.
  - When the channel fails for an event, the core calls `unmarkKnocked` and goes on with the next event.
    So the next check sends the knock, and one failure does not stop the knock of another event.
  - It gives back two lists of messages: `sent` and `failed`.
- `src/http/endpoint.ts`: the endpoint gives the core the time at which the call arrived. The options
  of the endpoint get an optional value `now`, a function that gives the time as a `Date`. Without it
  the endpoint reads the clock.
- `src/settings.ts`: a fourth setting, `PRODUCT_TIME_LIMIT_SECONDS`, the value `timeLimitSeconds`. It
  takes digits only, from 1 to 86400. The default is 600. A wrong value gives an error that names the
  variable.
- `src/time-limit-checks.ts`, new, outside the core: the function `startTimeLimitChecks`.
  - It takes three values: `intervalMs`, the function `check`, and the function `writeError`. `check`
    takes a time as a `Date` and gives back the lists `sent` and `failed`. `writeError` takes one line.
  - It calls `check` each `intervalMs` milliseconds, with the time of that moment. A check does not
    start while the check before it runs.
  - For each failed message it gives one line to `writeError`. The line names the identity and the start
    time of the event. When `check` throws, it gives one line with the text of the error, and the
    checks go on.
  - It gives back a function that ends the checks: after its call no check starts.
- `src/main.ts`: product starts the checks with an interval of 1000 milliseconds, with `judgeTimeLimit`
  and the setting of the time limit, and with the error output. The stop of the process ends the checks.
- `product-test/run.ts`: a scenario can hold two more values, and both are optional.
  - `settings`: names and values that the runner adds to the environment of the process of this
    scenario. The record file and the port of the runner stay as the runner sets them.
  - `waitMs`: the runner waits this number of milliseconds after the last event, and then it reads the
    messages.
- `product-test/scenarios/`, three new scenarios. Each one sets `PRODUCT_TIME_LIMIT_SECONDS` to `1` and
  `waitMs` to 3000.
  - `06-time-limit-knock.json`: "an event with no result gets a knock when the time limit passes". One
    open event that is not urgent. The known answer is one knock with the rule
    `the time limit passed with no result`.
  - `07-closed-before-time-limit.json`: "an event that closes before the time limit gets no knock". One
    event that is not urgent, as open and then as closed. The known answer is no message.
  - `08-urgent-no-second-knock.json`: "an urgent event gets no second knock at the time limit". One open
    urgent event. The known answer is one knock with the rule `an urgent event gets a knock`.
- `tests/product-test/run.test.ts`: the two tests that run the scenarios of the repository get a time
  limit of 60 seconds each, because the three new scenarios wait.
- `docs/architecture.md`:
  - The section "How the core behaves" gets three sentences. The knock at the time limit goes to an open
    event that has no knock. An event that got a knock at its arrival gets no second knock at the time
    limit. Until the result input exists, no result stops the time limit.
  - The row "Core" names the judgement at the time limit. The row "Test of the product" names the two
    new values of a scenario.
  - The row "Start of the process" names the fourth setting, the file `src/time-limit-checks.ts` and
    the check each second. It says that the default of 600 seconds holds until the lab measures the
    agent. It gives the reason for the check each second: the time limits are in the store, so no
    timer holds state.
- The change request has the line `No document change: the product document states this behaviour`.

## Out of scope

The result of the agent: it is a later work item. Until it exists, each open event with no knock gets a
knock at the time limit. The time limit as a setting of a team, and its default from a measurement in
the lab: the number 600 holds until then. The time limits after a restart: they come with the record
store. A limit on the number of tries of a failed knock: it comes with the channel to a phone. A late
result. A change of a package file, of the contract, or of an intent that is already merged.

## Acceptance checks

## Automatic checks

In checks 1 to 9 the time limit is 600 seconds, and the event arrives at the time T.

1. An open event that is not urgent: a check at T plus 599 seconds sends nothing. A check at T plus 600
   seconds sends one knock with the rule `the time limit passed with no result`, and gives it in `sent`.
   test: `tests/core/time-limit.test.ts::an event with no result gets a knock when the time limit passes`
2. After that knock, a later check sends nothing.
   test: `tests/core/time-limit.test.ts::the time limit gives one knock for one event`
3. An urgent event that got its knock at the arrival: a check at T plus 600 seconds sends nothing.
   test: `tests/core/time-limit.test.ts::an event with a knock gets no second knock at the time limit`
4. An event that is not urgent, as open and then as closed: a check at T plus 600 seconds sends nothing.
   test: `tests/core/time-limit.test.ts::an event that closed gets no knock at the time limit`
5. An open event that is not urgent, and its repeat at T plus 599 seconds: a check at T plus 600 seconds
   sends one knock.
   test: `tests/core/time-limit.test.ts::a repeat does not start the time limit again`
6. An open event that got a quiet message at its arrival: a check at T plus 600 seconds sends one knock.
   test: `tests/core/time-limit.test.ts::an event with a quiet message gets a knock at the time limit`
7. Two checks start at the same time at T plus 600 seconds, with a channel that answers after a pause:
   the channel holds one knock.
   test: `tests/core/time-limit.test.ts::two checks at the same time give one knock`
8. A channel that fails at the first message and works after it: the first check sends nothing and
   gives the message in `failed`. The second check sends one knock.
   test: `tests/core/time-limit.test.ts::a knock that failed is sent at the next check`
9. Two events wait, and the channel fails for the first one only: the same check sends the knock of the
   second event.
   test: `tests/core/time-limit.test.ts::a failed knock does not stop the knock of another event`
10. The store in memory. `waitingSince` gives the events that wait and that arrived at the given time or
    before it, in the order of their arrival. It does not give an event that arrived later, an event
    that closed, a marked event, or an event that the store forgot. `markKnocked` returns true at the
    first call and false at the second one, and false for an event that is closed or not known. After
    `unmarkKnocked` the list holds the event again.
    test: `tests/store/memory.test.ts::the store gives the events that wait since a given time`
11. The setting `PRODUCT_TIME_LIMIT_SECONDS`: no value gives 600, `90` gives 90, and `86400` gives
    86400. Each of `0`, `86401`, `1.5`, `-5` and `abc` gives an error that names the variable.
    test: `tests/settings.test.ts::the time limit is a number of seconds from 1 to 86400`
12. A scenario with `settings`: its process has each name with its value in its environment.
    test: `tests/product-test/run.test.ts::a scenario gives its settings to its process`
13. A scenario with `waitMs` of 1000, and a process that writes its message 300 milliseconds after the
    event: the scenario passes.
    test: `tests/product-test/run.test.ts::a scenario waits before it reads the messages`
14. The two checks on the core still pass with the new file of the core.
    test: `tests/core/boundary.test.ts::the core imports no file outside the core`
    test: `tests/core/boundary.test.ts::the core holds no term of the on-call use case`
15. The test of the product passes with the scenarios of the folder, the three new ones included.
    command: `node product-test/run.ts`
16. The two tests that run the scenarios of the repository pass with the three new scenarios.
    test: `tests/product-test/run.test.ts::the command passes on the scenarios of the repository`
    test: `tests/product-test/run.test.ts::the two first scenarios pass`
17. An endpoint with a `now` that gives a fixed time, and one open event: the store gets this time as
    the time of the arrival.
    test: `tests/http/endpoint.test.ts::the endpoint gives the core the time of the arrival`
18. An interval of 10 milliseconds and a check that runs 100 milliseconds: no check starts while another
    one runs.
    test: `tests/time-limit-checks.test.ts::a check does not start while the check before it runs`
19. A check that gives two failed messages: `writeError` gets two lines, and each line names its event.
    test: `tests/time-limit-checks.test.ts::each failed message gives one line`
20. A check that throws at its first call: `writeError` gets one line with the text of the error, and a
    second check runs.
    test: `tests/time-limit-checks.test.ts::a check that throws does not end the checks`
21. After the call of the function that ends the checks, no check starts.
    test: `tests/time-limit-checks.test.ts::the checks end at the stop`

The checks of the earlier intents stay as they are and still pass with `pnpm test`, with one change: each
test that calls `judgeEvent` or `open` gives it a time of arrival.

The scenarios of the test of the product that show this work item are the three new ones:
`06-time-limit-knock.json`, `07-closed-before-time-limit.json` and `08-urgent-no-second-knock.json`.

## Manual checks

None.
