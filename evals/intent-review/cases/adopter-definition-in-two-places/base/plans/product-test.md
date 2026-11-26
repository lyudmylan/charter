# Plan: the test of the product (#3)

Intent: `intents/product-test.md`, checks 1 to 8.

## Steps

1. Add `product-test/run.ts`. A function `runScenarios` takes the folder of scenarios, the start command,
   the folder to run in, and the time limit for the address. For each scenario file, in the order of the
   names, it makes a temporary folder, starts product with port 0 and its own record file, reads the
   address from the first line, posts the events, reads the record with `readMessages`, stops the process
   with SIGTERM (SIGKILL after a grace time), and removes the folder. The process is also stopped after a
   failure.
2. A function `report` writes one line for each scenario and returns the exit code: 1 for a failed
   scenario or for no scenario. The start of the command runs both when the file is the main module.
3. Add the two scenario files as data in `product-test/scenarios/`.
4. Add `product-test` to `include` in `tsconfig.json`.
5. Add the row "Test of the product" to the table of parts in `docs/architecture.md`.
6. Add the unit tests, then run `pnpm typecheck`, `pnpm test`, and `node product-test/run.ts`.

## Files

- `product-test/run.ts`, `product-test/scenarios/01-urgent-event-knock.json`,
  `product-test/scenarios/02-not-urgent-no-message.json`
- `tests/product-test/run.test.ts`
- `tsconfig.json`, `docs/architecture.md`

## Tests

- `tests/product-test/run.test.ts`: the two first scenarios pass; a wrong known answer makes the scenario
  fail; no scenario is a failure; a product that does not start makes the scenario fail; the order of the
  messages counts; no scenario sees the events of another one; a wrong answer or a wrong exit code makes
  the scenario fail.
