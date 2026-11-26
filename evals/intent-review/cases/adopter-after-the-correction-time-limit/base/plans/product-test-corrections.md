# Plan: the two small corrections of the test of the product (#40)

Intent: `intents/product-test-corrections.md`, checks 1 to 6.

## Steps

1. In `readAddress`, search for the address only in the text up to the last line break.
2. In `runScenarios`, wrap the read and parse of a scenario file so the error text names the file.
3. Add `runCommand`: it runs the scenarios and the report, and for an error outside a scenario writes one
   line `failed: <text>` and gives 1.
4. The start of the command calls `runCommand` and sets the exit code.
5. Add the tests.

## Files

- `product-test/run.ts`
- `tests/product-test/run.test.ts`

## Tests

- `tests/product-test/run.test.ts`: the five tests named in the checks 1 to 5 of the intent.
