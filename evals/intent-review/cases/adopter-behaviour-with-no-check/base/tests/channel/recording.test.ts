// The recording channel writes messages to a file, and a reader gets them back.
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { expect, test } from "vitest";

import { readMessages, RecordingChannel } from "../../src/channel/recording.ts";
import type { Message } from "../../src/core/channel.ts";

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

// intents/review-corrections.md, check 4
test("a line that is not complete gives an error with its place", async () => {
  const folder = await mkdtemp(join(tmpdir(), "product-recording-"));
  try {
    const path = join(folder, "messages.jsonl");
    await writeFile(path, '{"level":"knock"}\n{"level":"qu', "utf8");
    await expect(readMessages(path)).rejects.toThrow(`${path}: line 2`);
  } finally {
    await rm(folder, { recursive: true, force: true });
  }
});
