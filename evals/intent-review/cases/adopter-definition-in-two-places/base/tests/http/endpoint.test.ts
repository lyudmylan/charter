// The HTTP endpoint, with a channel that keeps its messages in a list.
import type { Server } from "node:http";
import type { AddressInfo } from "node:net";

import { afterEach, expect, test } from "vitest";

import type { Channel, Message } from "../../src/core/channel.ts";
import type { Event } from "../../src/core/event.ts";
import { checkEvent, createEndpoint } from "../../src/http/endpoint.ts";
import { urgentGetsKnock } from "../../src/first-rule.ts";

const servers: Server[] = [];

afterEach(async () => {
  for (const server of servers.splice(0)) {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
});

function listChannel(): Channel & { messages: Message[] } {
  const messages: Message[] = [];
  return {
    messages,
    async send(message: Message): Promise<void> {
      messages.push(message);
    },
  };
}

async function start(channel: Channel): Promise<string> {
  const server = createEndpoint({ rules: [urgentGetsKnock], channel });
  servers.push(server);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  return `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
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

function post(url: string, body: string): Promise<Response> {
  return fetch(`${url}/events`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
}

// intents/http-endpoint.md, check 1
test("an urgent event gets a knock through the endpoint", async () => {
  const channel = listChannel();
  const url = await start(channel);
  const response = await post(url, JSON.stringify(event()));
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ message: "knock" });
  expect(channel.messages).toHaveLength(1);
  expect(channel.messages[0]?.level).toBe("knock");
  expect(channel.messages[0]?.identity).toBe("event-1");
  expect(channel.messages[0]?.startTime).toBe("2026-11-20T08:00:00Z");
});

// intents/http-endpoint.md, check 2
test("an event that no rule matches gets no message", async () => {
  const channel = listChannel();
  const url = await start(channel);
  const response = await post(url, JSON.stringify(event({ urgent: false })));
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ message: null });
  expect(channel.messages).toEqual([]);
});

// intents/http-endpoint.md, check 3
test("a missing value gets an error and starts nothing", async () => {
  for (const name of ["state", "identity", "startTime", "urgent"]) {
    const channel = listChannel();
    const url = await start(channel);
    const body: Record<string, unknown> = { ...event() };
    delete body[name];
    const response = await post(url, JSON.stringify(body));
    expect(response.status).toBe(400);
    const answer = (await response.json()) as { error: string };
    expect(answer.error).toContain(name);
    expect(channel.messages).toEqual([]);
  }
});

// intents/http-endpoint.md, check 4
test("a wrong value gets an error and starts nothing", async () => {
  const wrong: unknown[] = [
    { ...event(), state: "pending" },
    { ...event(), identity: "" },
    { ...event(), startTime: 20261120 },
    { ...event(), urgent: "true" },
  ];
  for (const body of wrong) {
    const channel = listChannel();
    const url = await start(channel);
    const response = await post(url, JSON.stringify(body));
    expect(response.status).toBe(400);
    expect(channel.messages).toEqual([]);
  }
});

// intents/http-endpoint.md, check 5
test("a body that is not JSON gets an error", async () => {
  const channel = listChannel();
  const url = await start(channel);
  const response = await post(url, "{not json");
  expect(response.status).toBe(400);
  expect(channel.messages).toEqual([]);
});

// intents/http-endpoint.md, check 6
test("a body that is too large gets an error", async () => {
  const channel = listChannel();
  const url = await start(channel);
  const response = await post(
    url,
    JSON.stringify({ ...event(), filler: "x".repeat(1024 * 1024 + 1) }),
  );
  expect(response.status).toBe(413);
  expect(channel.messages).toEqual([]);
});

// intents/http-endpoint.md, check 7
test("another path or another method gets an error", async () => {
  const url = await start(listChannel());
  expect((await fetch(`${url}/other`, { method: "POST", body: "{}" })).status).toBe(404);
  expect((await fetch(`${url}/events`)).status).toBe(405);
  expect((await fetch(`${url}/events`, { method: "PUT", body: "{}" })).status).toBe(405);
});

// intents/http-endpoint.md, check 8
test("a failure of the channel does not stop the endpoint", async () => {
  let fail = true;
  const messages: Message[] = [];
  const channel: Channel = {
    async send(message: Message): Promise<void> {
      if (fail) {
        throw new Error("the channel failed");
      }
      messages.push(message);
    },
  };
  const url = await start(channel);
  expect((await post(url, JSON.stringify(event()))).status).toBe(500);
  fail = false;
  expect((await post(url, JSON.stringify(event()))).status).toBe(200);
  expect(messages).toHaveLength(1);
});

// intents/http-endpoint.md, check 11
test("a value outside the four is not passed to the core", async () => {
  const channel = listChannel();
  const url = await start(channel);
  const response = await post(url, JSON.stringify({ ...event(), extra: "value" }));
  expect(response.status).toBe(200);
  expect(channel.messages).toHaveLength(1);
  const checked = checkEvent({ ...event(), extra: "value" });
  expect(checked).toStrictEqual({ event: event() });
});
