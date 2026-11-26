// The HTTP endpoint: it accepts an event, checks it, and passes it to the core. It sits outside the core.

import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";

import type { Channel } from "../core/channel.ts";
import type { Event } from "../core/event.ts";
import { judgeEvent } from "../core/judge.ts";
import type { Rule } from "../core/rule.ts";

/** The largest body that the endpoint reads, in bytes. */
export const MAX_BODY_BYTES = 1024 * 1024;

/** What the endpoint needs: the rules and the channel for the judgement. */
export interface EndpointOptions {
  rules: readonly Rule[];
  channel: Channel;
}

type Checked = { event: Event } | { error: string };

/** Checks a parsed body at run time and returns the four values of an event, and no other value. */
export function checkEvent(body: unknown): Checked {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return {
      error: "the body must be a JSON object with the values state, identity, startTime and urgent",
    };
  }
  const values = body as Record<string, unknown>;
  for (const name of ["state", "identity", "startTime", "urgent"]) {
    if (!Object.hasOwn(values, name) || values[name] === undefined) {
      return { error: `the value ${name} is missing` };
    }
  }
  const { state, identity, startTime, urgent } = values;
  if (state !== "open" && state !== "closed") {
    return { error: 'the value state must be "open" or "closed"' };
  }
  if (typeof identity !== "string" || identity === "") {
    return { error: "the value identity must be text that is not empty" };
  }
  if (typeof startTime !== "string" || startTime === "") {
    return { error: "the value startTime must be text that is not empty" };
  }
  if (typeof urgent !== "boolean") {
    return { error: "the value urgent must be true or false" };
  }
  return { event: { state, identity, startTime, urgent } };
}

function answer(
  res: ServerResponse,
  status: number,
  body: unknown,
  headers: Record<string, string> = {},
): void {
  const text = JSON.stringify(body);
  res.writeHead(status, {
    "content-type": "application/json",
    "content-length": Buffer.byteLength(text),
    ...headers,
  });
  res.end(text);
}

/** Reads the body. Returns undefined when it is larger than the limit; the rest is read and dropped. */
function readBody(req: IncomingMessage, onTooLarge: () => void): Promise<string | undefined> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    let tooLarge = false;
    req.on("data", (chunk: Buffer) => {
      if (tooLarge) {
        return;
      }
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        tooLarge = true;
        chunks.length = 0;
        onTooLarge();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => resolve(tooLarge ? undefined : Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

/** Creates the server of the endpoint. The caller starts it with listen. */
export function createEndpoint(options: EndpointOptions): Server {
  return createServer((req, res) => {
    handle(req, res, options).catch(() => {
      if (!res.headersSent) {
        answer(res, 500, { error: "the request failed" });
      } else {
        res.destroy();
      }
    });
  });
}

async function handle(
  req: IncomingMessage,
  res: ServerResponse,
  options: EndpointOptions,
): Promise<void> {
  const path = (req.url ?? "").split("?")[0];
  if (path !== "/events") {
    req.resume();
    answer(res, 404, { error: "no such address" });
    return;
  }
  if (req.method !== "POST") {
    req.resume();
    answer(res, 405, { error: "the method must be POST" }, { allow: "POST" });
    return;
  }
  let sent = false;
  const text = await readBody(req, () => {
    sent = true;
    answer(res, 413, { error: "the body is larger than 1 MB" });
  });
  if (sent || text === undefined) {
    return;
  }
  let body: unknown;
  try {
    body = JSON.parse(text);
  } catch {
    answer(res, 400, { error: "the body is not JSON" });
    return;
  }
  const checked = checkEvent(body);
  if ("error" in checked) {
    answer(res, 400, { error: checked.error });
    return;
  }
  try {
    const message = await judgeEvent(checked.event, options.rules, options.channel);
    answer(res, 200, { message: message?.level ?? null });
  } catch {
    answer(res, 500, { error: "the channel failed" });
  }
}
