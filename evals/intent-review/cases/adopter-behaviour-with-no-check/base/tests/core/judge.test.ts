// The judgement of the core, with a channel that keeps its messages in a list.
import { expect, test } from "vitest";

import type { Channel, Message } from "../../src/core/channel.ts";
import type { Event } from "../../src/core/event.ts";
import { judgeEvent } from "../../src/core/judge.ts";
import type { Rule } from "../../src/core/rule.ts";
import { MemoryEventStore } from "../../src/store/memory.ts";

const urgentGetsKnock: Rule = {
  name: "an urgent event gets a knock",
  when: { value: "urgent", equals: true },
  action: "knock",
};

function listChannel(): Channel & { messages: Message[] } {
  const messages: Message[] = [];
  return {
    messages,
    async send(message: Message): Promise<void> {
      messages.push(message);
    },
  };
}

function event(values: Partial<Event> = {}): Event {
  return {
    state: "open",
    identity: "event-1",
    startTime: "2026-11-20T08:00:00Z",
    urgent: true,
    ...values,
  };
}

// intents/urgent-event-knock.md, check 1
test("an open urgent event gets one knock", async () => {
  const channel = listChannel();
  await judgeEvent(event(), [urgentGetsKnock], channel, new MemoryEventStore());
  expect(channel.messages).toHaveLength(1);
  expect(channel.messages[0]?.level).toBe("knock");
});

// intents/urgent-event-knock.md, check 2
test("an event that is not urgent gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event({ urgent: false }), [urgentGetsKnock], channel, new MemoryEventStore());
  expect(sent).toBeUndefined();
  expect(channel.messages).toEqual([]);
});

// intents/urgent-event-knock.md, check 3
test("a closed event gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event({ state: "closed" }), [urgentGetsKnock], channel, new MemoryEventStore());
  expect(sent).toBeUndefined();
  expect(channel.messages).toEqual([]);
});

// intents/urgent-event-knock.md, check 4
test("with no rule an urgent event gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event(), [], channel, new MemoryEventStore());
  expect(sent).toBeUndefined();
  expect(channel.messages).toEqual([]);
});

// intents/urgent-event-knock.md, check 5
test("a rule with the action quiet message sends a quiet message", async () => {
  const quiet: Rule = {
    name: "an urgent event gets a quiet message",
    when: { value: "urgent", equals: true },
    action: "quiet message",
  };
  const channel = listChannel();
  await judgeEvent(event(), [quiet], channel, new MemoryEventStore());
  expect(channel.messages.map((message) => message.level)).toEqual(["quiet message"]);
});

// intents/urgent-event-knock.md, check 10
test("the first matching rule decides", async () => {
  const quiet: Rule = {
    name: "an urgent event gets a quiet message",
    when: { value: "urgent", equals: true },
    action: "quiet message",
  };
  const channel = listChannel();
  await judgeEvent(event(), [quiet, urgentGetsKnock], channel, new MemoryEventStore());
  expect(channel.messages.map((message) => message.level)).toEqual(["quiet message"]);
});

// intents/urgent-event-knock.md, check 6
test("a knock names its event and its rule", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(
    event({ identity: "event-42", startTime: "2026-11-20T09:30:00Z" }),
    [urgentGetsKnock],
    channel,
    new MemoryEventStore(),
  );
  const expected: Message = {
    level: "knock",
    identity: "event-42",
    startTime: "2026-11-20T09:30:00Z",
    rule: "an urgent event gets a knock",
  };
  expect(sent).toEqual(expected);
  expect(channel.messages).toEqual([expected]);
});

const rules = [urgentGetsKnock];

// intents/event-repeats.md, check 1
test("a repeat of an open event gets no message", async () => {
  const channel = listChannel();
  const store = new MemoryEventStore();
  expect(await judgeEvent(event(), rules, channel, store)).toBeDefined();
  expect(await judgeEvent(event(), rules, channel, store)).toBeUndefined();
  expect(channel.messages).toHaveLength(1);
});

// intents/event-repeats.md, check 2
test("a repeat is not judged again when its value urgent differs", async () => {
  const channel = listChannel();
  const store = new MemoryEventStore();
  await judgeEvent(event({ urgent: false }), rules, channel, store);
  await judgeEvent(event({ urgent: true }), rules, channel, store);
  expect(channel.messages).toEqual([]);
});

// intents/event-repeats.md, check 3
test("the same identity with another start time is a new event", async () => {
  const channel = listChannel();
  const store = new MemoryEventStore();
  await judgeEvent(event(), rules, channel, store);
  await judgeEvent(event({ startTime: "2026-11-20T09:00:00Z" }), rules, channel, store);
  expect(channel.messages.map((message) => message.startTime)).toEqual([
    "2026-11-20T08:00:00Z",
    "2026-11-20T09:00:00Z",
  ]);
});

// intents/event-repeats.md, check 4
test("an event that was closed starts nothing again", async () => {
  const channel = listChannel();
  const store = new MemoryEventStore();
  await judgeEvent(event(), rules, channel, store);
  await judgeEvent(event({ state: "closed" }), rules, channel, store);
  await judgeEvent(event(), rules, channel, store);
  expect(channel.messages).toHaveLength(1);
});

// intents/event-repeats.md, check 5
test("an event that arrives closed first starts nothing", async () => {
  const channel = listChannel();
  const store = new MemoryEventStore();
  await judgeEvent(event({ state: "closed" }), rules, channel, store);
  await judgeEvent(event(), rules, channel, store);
  expect(channel.messages).toEqual([]);
});

// intents/event-repeats.md, check 6
test("two calls with the same new event at the same time give one message", async () => {
  const messages: Message[] = [];
  const channel: Channel = {
    async send(message: Message): Promise<void> {
      await new Promise((resolve) => setTimeout(resolve, 20));
      messages.push(message);
    },
  };
  const store = new MemoryEventStore();
  await Promise.all([
    judgeEvent(event(), rules, channel, store),
    judgeEvent(event(), rules, channel, store),
  ]);
  expect(messages).toHaveLength(1);
});

// intents/event-repeats.md, check 7
test("an event whose message failed is judged again at its repeat", async () => {
  const messages: Message[] = [];
  let fail = true;
  const channel: Channel = {
    async send(message: Message): Promise<void> {
      if (fail) {
        fail = false;
        throw new Error("the channel failed");
      }
      messages.push(message);
    },
  };
  const store = new MemoryEventStore();
  await expect(judgeEvent(event(), rules, channel, store)).rejects.toThrow("the channel failed");
  expect(await judgeEvent(event(), rules, channel, store)).toBeDefined();
  expect(messages).toHaveLength(1);
});
