// An event as the detector gives it to the core.

/** The state of an event: open while it lasts, closed when the detector ends it. */
export type EventState = "open" | "closed";

/** An event with its four values. The core compares the identity and the start time and does not read inside them. */
export interface Event {
  state: EventState;
  identity: string;
  startTime: string;
  urgent: boolean;
}
