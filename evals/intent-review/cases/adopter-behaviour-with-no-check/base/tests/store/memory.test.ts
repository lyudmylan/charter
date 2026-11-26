// The store of events in memory.
import { expect, test } from "vitest";

import { MemoryEventStore } from "../../src/store/memory.ts";

const start = "2026-11-20T08:00:00Z";

// intents/event-repeats.md, check 8
test("the store knows an event by its identity and its start time", async () => {
  const store = new MemoryEventStore();
  expect(await store.open("event-1", start)).toBe(true);
  expect(await store.open("event-1", start)).toBe(false);
  await store.close("event-1", start);
  expect(await store.open("event-1", start)).toBe(false);
  await store.forget("event-1", start);
  expect(await store.open("event-1", start)).toBe(true);
  expect(await store.open("event-1", "2026-11-20T09:00:00Z")).toBe(true);
  expect(await store.open("event-2", start)).toBe(true);
  await store.close("event-3", start);
  expect(await store.open("event-3", start)).toBe(false);
});
