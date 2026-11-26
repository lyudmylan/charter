// The interface through which the core keeps the state of the events it saw. The stores live outside the core.

/**
 * The store of events. An event is named by its identity and its start time. Each operation is
 * asynchronous, because the record store comes later behind the same interface.
 */
export interface EventStore {
  /** Stores the event as open when the store does not know it, and returns true. Otherwise changes nothing and returns false. */
  open(identity: string, startTime: string): Promise<boolean>;
  /** Stores the event as closed, also when the store did not know it. */
  close(identity: string, startTime: string): Promise<void>;
  /** Removes the event, so the store does not know it any more. */
  forget(identity: string, startTime: string): Promise<void>;
}
