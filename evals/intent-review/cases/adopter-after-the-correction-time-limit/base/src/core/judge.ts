// The judgement at the moment the event arrives.

import type { Channel, Message } from "./channel.ts";
import type { Event } from "./event.ts";
import type { EventStore } from "./event-store.ts";
import { matches, type Rule } from "./rule.ts";

/**
 * Judges an event with the given rules. A closed event is stored as closed and gets no message. An open
 * event that the store knows is a repeat, or was closed, and starts nothing. For a new open event the
 * core stores it first, then the first rule that matches decides, and the core sends one message to the
 * channel. When the channel fails, the core forgets the event and passes the failure on, so a repeat is
 * judged again. Returns the message, or undefined when nothing was sent.
 */
export async function judgeEvent(
  event: Event,
  rules: readonly Rule[],
  channel: Channel,
  store: EventStore,
): Promise<Message | undefined> {
  if (event.state === "closed") {
    await store.close(event.identity, event.startTime);
    return undefined;
  }
  if (!(await store.open(event.identity, event.startTime))) {
    return undefined;
  }
  const rule = rules.find((candidate) => matches(candidate, event));
  if (rule === undefined) {
    return undefined;
  }
  const message: Message = {
    level: rule.action,
    identity: event.identity,
    startTime: event.startTime,
    rule: rule.name,
  };
  try {
    await channel.send(message);
  } catch (error) {
    await store.forget(event.identity, event.startTime);
    throw error;
  }
  return message;
}
