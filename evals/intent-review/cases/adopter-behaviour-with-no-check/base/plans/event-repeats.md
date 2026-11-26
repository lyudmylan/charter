# Plan: a repeat of an open event gets no second message (#50)

Intent: `intents/event-repeats.md`, checks 1 to 12.

## Steps

1. Add `src/core/event-store.ts` with the interface `EventStore`: `open`, `close`, `forget`, each asynchronous.
2. Add `src/store/memory.ts` with `MemoryEventStore`, a map from identity and start time to the state.
3. Change `judgeEvent` to take the store as its fourth value. A closed event is stored as closed. An open
   event is stored with `open` before the judgement; when `open` returns false, nothing starts. When the
   channel fails, the core forgets the event and passes the failure on.
4. Give the options of the endpoint the store and pass it to the core. Start `src/main.ts` with one
   `MemoryEventStore`.
5. Add the three scenario files. Change the two tests of `tests/product-test/run.test.ts` that hold a count.
6. Update `docs/architecture.md`. Run `pnpm typecheck`, `pnpm test`, and `node product-test/run.ts`.

## Files

- `src/core/event-store.ts`, `src/store/memory.ts` (new)
- `src/core/judge.ts`, `src/http/endpoint.ts`, `src/main.ts` (changed)
- `product-test/scenarios/03-repeat-no-second-message.json`, `04-new-start-time-new-knock.json`,
  `05-closed-event-stays-closed.json` (new)
- `docs/architecture.md` (changed)

## Tests

- `tests/core/judge.test.ts`: checks 1 to 7; the earlier tests give `judgeEvent` a store.
- `tests/store/memory.test.ts`: check 8.
- `tests/http/endpoint.test.ts`: check 9; the earlier tests give the endpoint a store.
- `tests/product-test/run.test.ts`: the two tests that read the scenarios of the repository hold no count.
