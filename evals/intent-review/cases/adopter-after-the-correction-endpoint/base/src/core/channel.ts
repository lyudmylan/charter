// The interface through which the core sends a message. The channels live outside the core.

import type { Action } from "./rule.js";

/** The level of a message: a knock or a quiet message. */
export type Level = Action;

/** A message: its level, the identity and start time of its event, and the name of the rule that decided. */
export interface Message {
  level: Level;
  identity: string;
  startTime: string;
  rule: string;
}

/** A channel takes a message from the core and delivers it. */
export interface Channel {
  send(message: Message): Promise<void>;
}
