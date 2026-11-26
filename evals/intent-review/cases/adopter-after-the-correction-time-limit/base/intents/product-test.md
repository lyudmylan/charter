# Intent: a test starts product, sends events, and checks the messages that came out

Work item: #3. Approval: a person merges the change request that adds this file.

## Goal

One command tests product as a whole from the outside: it starts product as a process, sends the events
of each scenario to its HTTP endpoint, compares the messages that the recording channel wrote with the
known answer of the scenario, and stops product.

## In scope

This work item starts after the code of #2 is on the main branch. It uses what #2 gives: the command
`node src/main.ts`, the three settings, the line with the address, and the address `POST /events`. It
uses the reader of the record file, `readMessages`, that #1 gave.

- `product-test/run.ts`: the test of the product. The command is `node product-test/run.ts`. It is apart
  from the unit tests, and `pnpm test` does not run it.
  - It runs each scenario of the folder `product-test/scenarios/`, in the order of the file names.
  - Each scenario gets its own process of product, with the port 0 and its own record file in a
    temporary folder. So no scenario sees the events of another one.
  - For each scenario it starts product, reads the address from the first line, sends the events in
    their order, reads the messages from the record file, stops product with SIGTERM, and removes the
    temporary folder.
  - A scenario passes when each event got the answer 200, the messages equal the known answer in
    content and in order, and product ended with the exit code 0.
  - It writes one line for each scenario, with its name and "passed" or "failed". A failed scenario
    also shows the known answer and the messages that came out.
  - It ends with the exit code 0 when each scenario passed. It ends with the exit code 1 when one
    scenario failed, and when the folder holds no scenario.
  - When product does not write its address within the time limit, the scenario fails with this
    reason. The test stops the process of product in each case, also after a failure.
  - It needs no other host, no secret and no model call. It calls `127.0.0.1` only.
- `product-test/scenarios/`: one JSON file for each scenario. A scenario is data: its name, the events
  to send, and its known answer. The known answer is the list of the messages, each with its level, the
  identity and the start time of its event, and the name of the rule that decided. A later work item
  adds a scenario as one file, with no change of `product-test/run.ts`.
  - `01-urgent-event-knock.json`: "an urgent event gets one knock". One open urgent event, and the known
    answer is one knock.
  - `02-not-urgent-no-message.json`: "an event that is not urgent gets no message". One open event that
    is not urgent, and the known answer is an empty list.
- The code that runs the scenarios is a function apart from the start of the command. A unit test calls
  it with another folder of scenarios, with another start command, and with another time limit for the
  address. The default of the time limit is 10 seconds.
- `tsconfig.json`: the type check also covers `product-test/`.
- `docs/architecture.md`, the table of parts: a new row, "Test of the product", names `product-test/`,
  the command, and the reason for one process for each scenario.

## Out of scope

The line of the contract that names this command as the product test, and a script in the package file
(#4): this work item changes no package file and no contract. The scenarios of the product lab: they need
the agent that investigates and a model (#12). A scenario for a wrong call, such as a missing value: the
unit tests of #2 cover it. A scenario with more than one process of product.

## Acceptance checks

## Automatic checks

1. The test of the product passes on the code of the main branch with this work item.
   command: `node product-test/run.ts`
2. The folder `product-test/scenarios/` holds the two scenarios of this work item, and the test of the
   product reports each of them as passed.
   test: `tests/product-test/run.test.ts::the two first scenarios pass`
3. A scenario whose known answer differs from the messages that came out fails, and the result names the
   scenario and holds the known answer and the messages. The test uses a folder with one scenario that
   expects a knock for an event that is not urgent.
   test: `tests/product-test/run.test.ts::a wrong known answer makes the scenario fail`
4. A folder with no scenario makes the test of the product fail.
   test: `tests/product-test/run.test.ts::no scenario is a failure`
5. A start command that never writes an address makes the scenario fail with the reason "no address",
   and the process of that command is stopped. The test uses a time limit of one second.
   test: `tests/product-test/run.test.ts::a product that does not start makes the scenario fail`
6. A scenario with two events passes when its known answer holds the two messages in the order of the
   events, and it fails when the known answer holds them in the other order.
   test: `tests/product-test/run.test.ts::the order of the messages counts`
7. Each scenario starts with an empty record file. The test uses a folder with two scenarios, and the
   second one expects no message of the first one.
   test: `tests/product-test/run.test.ts::no scenario sees the events of another one`
8. A scenario fails when the product answers an event with a code that is not 200, and when the product
   ends with an exit code that is not 0. The test uses a start command with a small server that answers
   500, and one with a process that ends with the exit code 1 on SIGTERM.
   test: `tests/product-test/run.test.ts::a wrong answer or a wrong exit code makes the scenario fail`

The type check of the quality gate covers `product-test/`: `pnpm typecheck` fails on a type error in
`product-test/run.ts`.

This work item adds no behaviour to the product. It adds the first two scenarios of the test of the
product, and each later work item that changes the behaviour names its scenario here.

## Manual checks

None.
