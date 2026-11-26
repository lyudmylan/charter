# Plan: the three small review findings corrected (#34)

Intent: `intents/review-corrections.md`, checks 1 to 6.

## Steps

1. Move the finder of import sources to `tests/core/import-sources.ts`, add the `require` pattern, and
   put the comment on the comment rule there.
2. Make `boundary.test.ts` use it, and assert that the core gives at least one source.
3. Make `readMessages` throw an error with the path and the line number for a line that is not valid JSON.
4. Make the port setting accept digits only, with the range 0 to 65535.

## Files

- `tests/core/import-sources.ts` (new), `tests/core/boundary.test.ts`
- `src/channel/recording.ts`, `src/settings.ts`

## Tests

- `tests/core/import-sources.test.ts`: the three tests of checks 1 to 3.
- `tests/channel/recording.test.ts`: the line that is not complete.
- `tests/settings.test.ts`: the port is a plain number in the range.
- `tests/core/boundary.test.ts`: the added assertion.
