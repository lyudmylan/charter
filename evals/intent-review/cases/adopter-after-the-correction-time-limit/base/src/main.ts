// The start of product as one process: `node src/main.ts`.

import type { AddressInfo } from "node:net";

import { RecordingChannel } from "./channel/recording.ts";
import { urgentGetsKnock } from "./first-rule.ts";
import { createEndpoint } from "./http/endpoint.ts";
import { readSettings, type Settings } from "./settings.ts";
import { MemoryEventStore } from "./store/memory.ts";

let settings: Settings;
try {
  settings = readSettings(process.env);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}

const server = createEndpoint({
  rules: [urgentGetsKnock],
  channel: new RecordingChannel(settings.recordFile),
  store: new MemoryEventStore(),
});

server.listen(settings.port, settings.host, () => {
  const { address, port } = server.address() as AddressInfo;
  const host = address.includes(":") ? `[${address}]` : address;
  console.log(`product listens on http://${host}:${port}`);
});

function stop(): void {
  server.close(() => process.exit(0));
  server.closeAllConnections();
}

process.on("SIGTERM", stop);
process.on("SIGINT", stop);
