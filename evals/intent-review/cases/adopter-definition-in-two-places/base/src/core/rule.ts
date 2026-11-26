// A rule as plain data. The core holds no rule; it receives the list of rules with each call.

import type { Event } from "./event.ts";

/** The name of one value of an event that a condition can compare. */
export type EventValue = keyof Event;

/** A condition: one value of the event must equal the given value. */
export interface Condition {
  value: EventValue;
  equals: string | boolean;
}

/** What a rule asks for: a knock for the person, or a quiet message. */
export type Action = "knock" | "quiet message";

/** A rule: a name, one condition, and an action. */
export interface Rule {
  name: string;
  when: Condition;
  action: Action;
}

/** Tells whether the condition of the rule holds for the event. */
export function matches(rule: Rule, event: Event): boolean {
  return event[rule.when.value] === rule.when.equals;
}
