// The recording channel: it sends no push and writes each message as one line of JSON to a file.

import { appendFile, readFile } from "node:fs/promises";

import type { Channel, Message } from "../core/channel.js";

/** A channel that appends each message to a file, in the order of arrival. */
export class RecordingChannel implements Channel {
  constructor(private readonly path: string) {}

  /** Appends the message to the file as one line of JSON. */
  async send(message: Message): Promise<void> {
    await appendFile(this.path, `${JSON.stringify(message)}\n`, "utf8");
  }
}

/** Reads the messages of a recording file in the order of the lines. Returns an empty list when the file does not exist. */
export async function readMessages(path: string): Promise<Message[]> {
  let text: string;
  try {
    text = await readFile(path, "utf8");
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return [];
    }
    throw error;
  }
  return text
    .split("\n")
    .filter((line) => line !== "")
    .map((line) => JSON.parse(line) as Message);
}
