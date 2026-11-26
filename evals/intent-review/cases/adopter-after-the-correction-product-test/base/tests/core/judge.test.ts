// The judgement of the core, with a channel that keeps its messages in a list.
import { expect, test } from "vitest";

import type { Channel, Message } from "../../src/core/channel.js";
import type { Event } from "../../src/core/event.js";
import { judgeEvent } from "../../src/core/judge.js";
import type { Rule } from "../../src/core/rule.js";

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
  await judgeEvent(event(), [urgentGetsKnock], channel);
  expect(channel.messages).toHaveLength(1);
  expect(channel.messages[0]?.level).toBe("knock");
});

// intents/urgent-event-knock.md, check 2
test("an event that is not urgent gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event({ urgent: false }), [urgentGetsKnock], channel);
  expect(sent).toBeUndefined();
  expect(channel.messages).toEqual([]);
});

// intents/urgent-event-knock.md, check 3
test("a closed event gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event({ state: "closed" }), [urgentGetsKnock], channel);
  expect(sent).toBeUndefined();
  expect(channel.messages).toEqual([]);
});

// intents/urgent-event-knock.md, check 4
test("with no rule an urgent event gets no message", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(event(), [], channel);
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
  await judgeEvent(event(), [quiet], channel);
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
  await judgeEvent(event(), [quiet, urgentGetsKnock], channel);
  expect(channel.messages.map((message) => message.level)).toEqual(["quiet message"]);
});

// intents/urgent-event-knock.md, check 6
test("a knock names its event and its rule", async () => {
  const channel = listChannel();
  const sent = await judgeEvent(
    event({ identity: "event-42", startTime: "2026-11-20T09:30:00Z" }),
    [urgentGetsKnock],
    channel,
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
