// The judgement at the moment the event arrives.

import type { Channel, Message } from "./channel.js";
import type { Event } from "./event.js";
import { matches, type Rule } from "./rule.js";

/**
 * Judges an event with the given rules. A closed event gets no message. For an open event the first
 * rule that matches decides, and the core sends one message to the channel. Returns the message, or
 * undefined when nothing was sent.
 */
export async function judgeEvent(
  event: Event,
  rules: readonly Rule[],
  channel: Channel,
): Promise<Message | undefined> {
  if (event.state === "closed") {
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
  await channel.send(message);
  return message;
}
