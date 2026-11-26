# Plan: the HTTP endpoint accepts an event and passes it to the core (#2)

Intent: `intents/http-endpoint.md`, checks 1 to 12.

## Steps

1. Change each relative import in `src/` and `tests/` to end in `.ts`. Add `allowImportingTsExtensions` and
   `erasableSyntaxOnly` to `tsconfig.json`. Change the constructor of the recording channel to a plain field.
2. Add `src/first-rule.ts` with the first rule as data, and `src/settings.ts` with one function that reads
   the three settings from an environment.
3. Add `src/http/endpoint.ts`: `createEndpoint` with the rules and the channel, the run time check of the
   four values, the limit of 1 MB, and the answers 200, 400, 404, 405, 413 and 500.
4. Add `src/main.ts`: read the settings, start the server, write the address line, close on SIGTERM and SIGINT.
5. Write the tests of the intent. Update `docs/architecture.md` and `docs/product.md`.
6. Run `pnpm typecheck` and `pnpm test`.

## Files

- `src/first-rule.ts`, `src/settings.ts`, `src/http/endpoint.ts`, `src/main.ts` (new)
- `src/channel/recording.ts`, `tsconfig.json`, the imports in `src/` and `tests/` (changed)
- `docs/architecture.md`, `docs/product.md`

## Tests

- `tests/http/endpoint.test.ts`: the tests of checks 1 to 8 and 11, with a channel that keeps a list.
- `tests/settings.test.ts`: check 12, and the port, the host and the wrong values.
- `tests/process.test.ts`: checks 9 and 10, with `node src/main.ts` as a child process.
