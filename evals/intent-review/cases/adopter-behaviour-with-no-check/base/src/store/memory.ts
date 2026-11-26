// The store of events in memory. It sits outside the core. The events do not survive a restart.

import type { EventStore } from "../core/event-store.ts";

/** Holds the state of each event in a map, by the identity and the start time. */
export class MemoryEventStore implements EventStore {
  private readonly states = new Map<string, "open" | "closed">();

  private key(identity: string, startTime: string): string {
    return JSON.stringify([identity, startTime]);
  }

  async open(identity: string, startTime: string): Promise<boolean> {
    const key = this.key(identity, startTime);
    if (this.states.has(key)) {
      return false;
    }
    this.states.set(key, "open");
    return true;
  }

  async close(identity: string, startTime: string): Promise<void> {
    this.states.set(this.key(identity, startTime), "closed");
  }

  async forget(identity: string, startTime: string): Promise<void> {
    this.states.delete(this.key(identity, startTime));
  }
}
