# Intent: the two small findings of the review on the test of the product are corrected

Work item: #40. Approval: a person merges the change request that adds this file.

## Goal

The test of the product ends with one line and the exit code 1 for an error outside a scenario, and it
reads the address of product only from a complete line, and a test shows each correction.

## In scope

- `product-test/run.ts`, the start of the command.
  - Today an error outside a scenario ends the command with a stack trace. A scenario file that is not
    valid JSON is such an error, and a folder of scenarios that does not exist is another one.
  - A new function, `runCommand`, runs the scenarios and writes the report. It takes the same options as
    `runScenarios` and the same function for a line as `report`, and it gives the exit code. For an error
    outside a scenario it writes one line, `failed: <the text of the error>`, and gives the exit code 1.
  - The start of the command calls `runCommand` and sets the exit code. It holds no other logic.
  - A scenario file that is not valid JSON gives an error whose text names the file. So the line says
    which file to correct.
- `product-test/run.ts`, the reading of the address.
  - Today the test takes the address from the text that came so far. When the line with the address
    arrives in two parts, the test takes a part of the address, and the scenario fails with no fault of
    product.
  - The test takes the address only from a line that ends with a line break. The time limit for the
    address stays as it is.
- The answers 200, the comparison of the messages, the exit code of product and the form of the line of a
  scenario stay as they are.

## Out of scope

New behaviour of the product, and each change under `src/`. A check of the values in a scenario file that
is valid JSON: such a scenario fails as a scenario today, with its reason. New scenarios. A change of a
package file, of the contract, or of an intent that is already merged.

## Acceptance checks

## Automatic checks

1. A folder with one scenario file that is not valid JSON: `runCommand` gives the exit code 1 and writes
   exactly one line. The line starts with `failed:` and holds the name of the file.
   test: `tests/product-test/run.test.ts::a file that is not valid JSON gives one failed line`
2. A folder of scenarios that does not exist: `runCommand` gives the exit code 1 and writes exactly one
   line, and the line starts with `failed:`.
   test: `tests/product-test/run.test.ts::a missing folder gives one failed line`
3. A start command that writes the line with its address in two parts, with a pause between them, and
   then answers each event with 200: a scenario with one event passes. The first part ends inside the
   number of the port, so a part of the address is no address that answers.
   test: `tests/product-test/run.test.ts::an address that arrives in two parts is read complete`
4. A start command that writes its address with no line break and then waits: the test does not take the
   address, and the scenario fails with the reason "no address" at the time limit. The test uses a time
   limit of one second.
   test: `tests/product-test/run.test.ts::an address with no line break is not taken`
5. With the scenarios of the repository, `runCommand` gives the exit code 0 and writes one line with
   "passed" for each scenario.
   test: `tests/product-test/run.test.ts::the command passes on the scenarios of the repository`
6. The test of the product passes on the code with this work item.
   command: `node product-test/run.ts`

The checks of the earlier intents stay as they are and still pass with `pnpm test`.

This work item adds no behaviour that a scenario of the test of the product can show.

## Manual checks

None.
