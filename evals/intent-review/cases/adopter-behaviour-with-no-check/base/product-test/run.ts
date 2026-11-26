// The test of the product: it starts product as a process for each scenario, sends the events of the
// scenario to its HTTP endpoint, and compares the messages that the recording channel wrote with the
// known answer. Run it with `node product-test/run.ts`.

import { spawn, type ChildProcess } from "node:child_process";
import { mkdtemp, readdir, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { isDeepStrictEqual } from "node:util";

import { readMessages } from "../src/channel/recording.ts";
import type { Message } from "../src/core/channel.ts";

/** A scenario is data: its name, the events to send, and the known answer. */
export interface Scenario {
  name: string;
  events: unknown[];
  messages: Message[];
}

/** The result of one scenario. */
export interface ScenarioResult {
  file: string;
  name: string;
  passed: boolean;
  /** Why the scenario failed. */
  reason?: string;
  expected: Message[];
  actual: Message[];
}

export interface RunOptions {
  /** The folder with the scenario files. */
  scenariosDir: string;
  /** The command that starts product: the program and its arguments. */
  command: string[];
  /** The folder where the command runs. */
  cwd: string;
  /** How long to wait for the address, in milliseconds. */
  addressTimeoutMs: number;
}

/** The defaults: the scenarios of this folder, and `node src/main.ts` with a time limit of 10 seconds. */
export const defaultOptions: RunOptions = {
  scenariosDir: join(import.meta.dirname, "scenarios"),
  command: ["node", "src/main.ts"],
  cwd: join(import.meta.dirname, ".."),
  addressTimeoutMs: 10_000,
};

const STOP_GRACE_MS = 3000;

function hasEnded(child: ChildProcess): boolean {
  return child.exitCode !== null || child.signalCode !== null;
}

/** Stops the process with SIGTERM, and with SIGKILL when it does not end in time. Returns its exit code. */
async function stopProcess(child: ChildProcess): Promise<number | null> {
  if (hasEnded(child)) {
    return child.exitCode;
  }
  const exited = new Promise<number | null>((resolve) => child.once("exit", (code) => resolve(code)));
  child.kill("SIGTERM");
  const timer = setTimeout(() => child.kill("SIGKILL"), STOP_GRACE_MS);
  try {
    return await exited;
  } finally {
    clearTimeout(timer);
  }
}

function readAddress(child: ChildProcess, timeoutMs: number): Promise<string> {
  return new Promise((resolve, reject) => {
    let output = "";
    const timer = setTimeout(() => finish(new Error("no address")), timeoutMs);
    function finish(error: Error | undefined, address?: string): void {
      clearTimeout(timer);
      child.stdout?.off("data", onData);
      child.off("error", onError);
      child.off("exit", onExit);
      if (error !== undefined) {
        reject(error);
      } else {
        resolve(address as string);
      }
    }
    function onData(chunk: Buffer): void {
      output += chunk.toString();
      // Only a complete line counts: the text after the last line break may be a part of an address.
      const complete = output.slice(0, output.lastIndexOf("\n") + 1);
      const found = /(http:\/\/\S+)\s*$/m.exec(complete);
      if (found?.[1] !== undefined) {
        finish(undefined, found[1]);
      }
    }
    function onError(error: Error): void {
      finish(new Error(`no address: the process did not start: ${error.message}`));
    }
    function onExit(): void {
      finish(new Error(`no address: the process ended early: ${output.trim()}`));
    }
    child.stdout?.on("data", onData);
    child.on("error", onError);
    child.on("exit", onExit);
  });
}

async function runScenario(file: string, scenario: Scenario, options: RunOptions): Promise<ScenarioResult> {
  const result: ScenarioResult = {
    file,
    name: scenario.name,
    passed: false,
    expected: scenario.messages,
    actual: [],
  };
  const folder = await mkdtemp(join(tmpdir(), "product-product-test-"));
  const recordFile = join(folder, "messages.jsonl");
  const [program, ...args] = options.command;
  const child = spawn(program as string, args, {
    cwd: options.cwd,
    env: { ...process.env, PRODUCT_RECORD_FILE: recordFile, PRODUCT_PORT: "0" },
    stdio: ["ignore", "pipe", "inherit"],
  });
  // A spawn error reaches readAddress; this listener keeps a later one from going unhandled.
  child.on("error", () => {});
  let code: number | null | undefined;
  try {
    const address = await readAddress(child, options.addressTimeoutMs);
    for (const event of scenario.events) {
      const response = await fetch(`${address}/events`, { method: "POST", body: JSON.stringify(event) });
      await response.arrayBuffer();
      if (response.status !== 200) {
        result.reason = `an event got the answer ${response.status}, not 200`;
        return result;
      }
    }
    result.actual = await readMessages(recordFile);
    code = await stopProcess(child);
    if (code !== 0) {
      result.reason = `product ended with the exit code ${String(code)}, not 0`;
      return result;
    }
    if (!isDeepStrictEqual(result.actual, scenario.messages)) {
      result.reason = "the messages differ from the known answer";
      return result;
    }
    result.passed = true;
    return result;
  } catch (error) {
    result.reason = error instanceof Error ? error.message : String(error);
    return result;
  } finally {
    if (code === undefined) {
      await stopProcess(child);
    }
    await rm(folder, { recursive: true, force: true });
  }
}

/** Runs each scenario of the folder, in the order of the file names, each with its own process. */
export async function runScenarios(options: RunOptions): Promise<ScenarioResult[]> {
  const files = (await readdir(options.scenariosDir)).filter((name) => name.endsWith(".json")).sort();
  const results: ScenarioResult[] = [];
  for (const file of files) {
    let scenario: Scenario;
    try {
      scenario = JSON.parse(await readFile(join(options.scenariosDir, file), "utf8")) as Scenario;
    } catch (error) {
      throw new Error(`the scenario file ${file} is not valid: ${error instanceof Error ? error.message : String(error)}`);
    }
    results.push(await runScenario(file, scenario, options));
  }
  return results;
}

/** Writes one line for each scenario, and the known answer and the messages for a failed one. Returns the exit code. */
export function report(results: ScenarioResult[], write: (line: string) => void = console.log): number {
  if (results.length === 0) {
    write("failed: the folder holds no scenario");
    return 1;
  }
  for (const result of results) {
    if (result.passed) {
      write(`${result.name}: passed`);
    } else {
      write(`${result.name}: failed: ${result.reason ?? "unknown reason"}`);
      write(`  known answer: ${JSON.stringify(result.expected)}`);
      write(`  messages: ${JSON.stringify(result.actual)}`);
    }
  }
  return results.every((result) => result.passed) ? 0 : 1;
}

/** Runs the scenarios and writes the report. An error outside a scenario gives one line. Returns the exit code. */
export async function runCommand(
  options: RunOptions,
  write: (line: string) => void = console.log,
): Promise<number> {
  try {
    return report(await runScenarios(options), write);
  } catch (error) {
    const text = error instanceof Error ? error.message : String(error);
    write(`failed: ${text.replace(/\s*\n\s*/g, " ")}`);
    return 1;
  }
}

if (import.meta.main) {
  process.exitCode = await runCommand(defaultOptions);
}
