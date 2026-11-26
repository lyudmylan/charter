# Intent: the HTTP endpoint accepts an event and passes it to the core

Work item: #2. Approval: a person merges the change request that adds this file.

## Goal

A sender posts an event to one address of product, the core judges it, and product runs as one process
that Node starts with one command.

## In scope

- `src/http/`: the HTTP endpoint. It is outside the core and uses the HTTP server of Node, with no new
  package.
  - One address accepts an event: `POST /events`. The body is JSON with the four values of an event:
    `state` (`"open"` or `"closed"`), `identity` (text, not empty), `startTime` (text, not empty) and
    `urgent` (true or false). The endpoint passes these four values to the core and no other value of
    the body.
  - The endpoint checks the input at run time. A call with a missing value, a wrong value, a body that
    is not JSON, or a body of more than 1 MB gets an error answer and starts nothing. The error answer
    is JSON and names the reason.
  - A valid event goes to the judgement of the core with the rules and the channel that the endpoint
    received when it was created. The answer is 200. Its JSON body has one value, `message`: the level
    of the message that went out, `"knock"` or `"quiet message"`, or `null` when no message went out.
  - When the channel fails, the answer is 500, and product keeps running.
- `src/main.ts`: the start of product as a process.
  - It reads three settings from the environment: `PRODUCT_RECORD_FILE`, the path of the file of the
    recording channel; `PRODUCT_PORT`, with the default 8080; and `PRODUCT_HOST`, with the default
    `127.0.0.1`. With the port 0 the system selects a free port. One function in `src/settings.ts` reads
    the settings, so a test checks the defaults with no process.
  - Without `PRODUCT_RECORD_FILE` the process does not start. It names the variable and ends with the
    exit code 1.
  - At start it writes one line that ends with its address, in the form `http://<host>:<port>`. A test
    reads the address from this line.
  - On the signal SIGTERM or SIGINT it closes the server and ends with the exit code 0.
  - It uses the first rule, "an urgent event gets a knock", until the configuration exists (#7). The
    rule is data in `src/first-rule.ts`, and `src/main.ts` and the tests of this work item import it
    from there. The core still holds no rule. The tests of the core keep their own rules, because
    they test the core with any rule.
- The command that starts product is `node src/main.ts`. Node runs the TypeScript files as they are, so
  there is no build step and no new package.
  - Each relative import ends in `.ts`, in `src/` and in `tests/`.
  - `tsconfig.json` gets `allowImportingTsExtensions` and `erasableSyntaxOnly`. The second one makes the
    type check refuse syntax that Node cannot run as it is.
  - `src/channel/recording.ts` has one such place, the constructor of the recording channel, and it
    changes its form with no change of behaviour.
- `docs/architecture.md`, the table of parts: the row "HTTP endpoint" names `src/http/` and what exists.
  A new row, "Start of the process", names `src/main.ts` and `src/settings.ts`, the three settings and
  the choice "Node runs the TypeScript files as they are, with no build step", with its reason: one
  command starts product with nothing to build first.
- `docs/product.md`, the section "Parts": the sentence about what the repository holds today becomes
  "The repository holds the first code of the core, an HTTP endpoint for events and a recording channel
  today, and product starts as one process."

## Out of scope

The token of a sender, the format of Alertmanager, and the steps and the result of the agent (#6). The
state of an event across calls (#6). The file format of the configuration (#7). The test of the product
as its own command (#3). A script in the package file that starts product (#4): this work item changes
no package file. The Docker Compose file (#12). HTTPS: it belongs to the installation.

## Acceptance checks

## Automatic checks

1. A `POST /events` with an open urgent event gets the answer 200, the JSON body of the answer has
   `message` with the value `"knock"`, and the channel holds one knock with the identity and the start
   time of that event.
   test: `tests/http/endpoint.test.ts::an urgent event gets a knock through the endpoint`
2. An open event that is not urgent gets the answer 200, the JSON body of the answer has `message` with
   the value `null`, and the channel holds no message.
   test: `tests/http/endpoint.test.ts::an event that no rule matches gets no message`
3. A body with one of the four values missing gets the answer 400, the answer names the value, and the
   channel holds no message. The test does this for each of the four values.
   test: `tests/http/endpoint.test.ts::a missing value gets an error and starts nothing`
4. A wrong value gets the answer 400 and the channel holds no message: a state that is not `"open"` or
   `"closed"`, an identity that is empty, a start time that is a number, and `urgent` as text.
   test: `tests/http/endpoint.test.ts::a wrong value gets an error and starts nothing`
5. A body that is not JSON gets the answer 400, and the channel holds no message.
   test: `tests/http/endpoint.test.ts::a body that is not JSON gets an error`
6. A body of more than 1 MB gets the answer 413, and the channel holds no message.
   test: `tests/http/endpoint.test.ts::a body that is too large gets an error`
7. A call to another path gets the answer 404, and a call to `/events` with a method that is not POST
   gets the answer 405.
   test: `tests/http/endpoint.test.ts::another path or another method gets an error`
8. When the channel fails, the answer is 500, and the next valid call gets the answer 200.
   test: `tests/http/endpoint.test.ts::a failure of the channel does not stop the endpoint`
9. The command `node src/main.ts`, with the port 0 and a record file in a temporary folder, writes the
   line with its address. A `POST /events` to that address with an open urgent event gets the answer
   200, and a reader gets one knock back from the record file. On the signal the process ends with the
   exit code 0. The test does this for SIGTERM and for SIGINT.
   test: `tests/process.test.ts::product starts, takes an event, and stops`
10. Without `PRODUCT_RECORD_FILE` the process ends with the exit code 1, and its output names the
    variable.
    test: `tests/process.test.ts::product does not start without the path of its record file`
11. A valid event with one more value in the body gets the answer 200, and the core receives only the
    four values.
    test: `tests/http/endpoint.test.ts::a value outside the four is not passed to the core`
12. With `PRODUCT_RECORD_FILE` only, the settings have the port 8080 and the host `127.0.0.1`.
    test: `tests/settings.test.ts::the settings have their defaults`

The type check of the quality gate proves the `.ts` imports and `erasableSyntaxOnly`: with the two
settings in `tsconfig.json`, `pnpm typecheck` fails on an import that it cannot resolve and on syntax that
Node cannot run as it is.

This work item changes the behaviour of the product. The test of the product comes with #3, and its first
scenario, "an urgent event gets a knock", shows this behaviour. Until then check 9 shows it.

## Manual checks

None.
