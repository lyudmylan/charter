// product as a process: `node src/main.ts`.
import { spawn, spawnSync } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { expect, test } from "vitest";

import { readMessages } from "../src/channel/recording.ts";

const root = join(import.meta.dirname, "..");

async function run(signal: "SIGTERM" | "SIGINT"): Promise<void> {
  const folder = await mkdtemp(join(tmpdir(), "product-process-"));
  const recordFile = join(folder, "messages.jsonl");
  const child = spawn("node", ["src/main.ts"], {
    cwd: root,
    env: { ...process.env, PRODUCT_RECORD_FILE: recordFile, PRODUCT_PORT: "0" },
  });
  try {
    const address = await new Promise<string>((resolve, reject) => {
      let output = "";
      child.stdout.on("data", (chunk: Buffer) => {
        output += chunk.toString();
        const found = /(http:\/\/\S+)\s*$/m.exec(output);
        if (found?.[1] !== undefined) {
          resolve(found[1]);
        }
      });
      child.on("error", reject);
      child.on("exit", () => reject(new Error(`the process ended early: ${output}`)));
    });
    const response = await fetch(`${address}/events`, {
      method: "POST",
      body: JSON.stringify({
        state: "open",
        identity: "event-1",
        startTime: "2026-11-20T08:00:00Z",
        urgent: true,
      }),
    });
    expect(response.status).toBe(200);
    const messages = await readMessages(recordFile);
    expect(messages).toHaveLength(1);
    expect(messages[0]?.level).toBe("knock");
    const exited = new Promise<number | null>((resolve) => child.on("exit", (code) => resolve(code)));
    child.kill(signal);
    expect(await exited).toBe(0);
  } finally {
    child.kill("SIGKILL");
    await rm(folder, { recursive: true, force: true });
  }
}

// intents/http-endpoint.md, check 9
test("product starts, takes an event, and stops", async () => {
  await run("SIGTERM");
  await run("SIGINT");
});

// intents/http-endpoint.md, check 10
test("product does not start without the path of its record file", () => {
  const env = { ...process.env };
  delete env["PRODUCT_RECORD_FILE"];
  const result = spawnSync("node", ["src/main.ts"], { cwd: root, env, encoding: "utf8" });
  expect(result.status).toBe(1);
  expect(result.stdout + result.stderr).toContain("PRODUCT_RECORD_FILE");
});
