// The recording channel writes messages to a file, and a reader gets them back.
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { expect, test } from "vitest";

import { readMessages, RecordingChannel } from "../../src/channel/recording.js";
import type { Message } from "../../src/core/channel.js";

// intents/urgent-event-knock.md, check 7
test("a reader gets the messages back in the order of arrival", async () => {
  const folder = await mkdtemp(join(tmpdir(), "product-recording-"));
  try {
    const path = join(folder, "messages.jsonl");
    const knock: Message = {
      level: "knock",
      identity: "event-1",
      startTime: "2026-11-20T08:00:00Z",
      rule: "an urgent event gets a knock",
    };
    const quiet: Message = {
      level: "quiet message",
      identity: "event-2",
      startTime: "2026-11-20T08:05:00Z",
      rule: "an event gets a quiet message",
    };
    expect(await readMessages(path)).toEqual([]);
    const channel = new RecordingChannel(path);
    await channel.send(knock);
    await channel.send(quiet);
    expect(await readMessages(path)).toEqual([knock, quiet]);
  } finally {
    await rm(folder, { recursive: true, force: true });
  }
});
