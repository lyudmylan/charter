// The test of the product, tested: intents/product-test.md, checks 2 to 8.
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, beforeEach, expect, test } from "vitest";

import { defaultOptions, report, runCommand, runScenarios, type RunOptions, type Scenario } from "../../product-test/run.ts";

let folder: string;

beforeEach(async () => {
  folder = await mkdtemp(join(tmpdir(), "product-product-test-unit-"));
});

afterEach(async () => {
  await rm(folder, { recursive: true, force: true });
});

function event(identity: string, urgent: boolean): Record<string, unknown> {
  return { state: "open", identity, startTime: "2026-11-20T08:00:00Z", urgent };
}

function knock(identity: string): Record<string, unknown> {
  return {
    level: "knock",
    identity,
    startTime: "2026-11-20T08:00:00Z",
    rule: "an urgent event gets a knock",
  };
}

async function scenarioFolder(scenarios: Scenario[]): Promise<string> {
  const dir = join(folder, "scenarios");
  await mkdir(dir, { recursive: true });
  for (const [index, scenario] of scenarios.entries()) {
    await writeFile(join(dir, `${String(index + 1).padStart(2, "0")}.json`), JSON.stringify(scenario));
  }
  return dir;
}

async function scriptCommand(name: string, source: string, ...args: string[]): Promise<string[]> {
  const path = join(folder, name);
  await writeFile(path, source);
  return ["node", path, ...args];
}

function options(scenariosDir: string, extra: Partial<RunOptions> = {}): RunOptions {
  return { ...defaultOptions, scenariosDir, ...extra };
}

function scenario(name: string, events: unknown[], messages: unknown[]): Scenario {
  return { name, events, messages } as Scenario;
}

// A small server that answers each event with the given status, and ends with the given code on SIGTERM.
const fakeServer = `
import { createServer } from "node:http";
const status = Number(process.argv[2]);
const exitCode = Number(process.argv[3]);
const server = createServer((req, res) => {
  req.resume();
  req.on("end", () => { res.writeHead(status); res.end("{}"); });
});
server.listen(0, "127.0.0.1", () => {
  console.log("product listens on http://127.0.0.1:" + server.address().port);
});
process.on("SIGTERM", () => process.exit(exitCode));
`;

// intents/product-test.md, check 2
test("the two first scenarios pass", async () => {
  const results = await runScenarios(defaultOptions);
  expect(results.map((result) => [result.file, result.passed])).toEqual([
    ["01-urgent-event-knock.json", true],
    ["02-not-urgent-no-message.json", true],
  ]);
  expect(report(results, () => {})).toBe(0);
});

// intents/product-test.md, check 3
test("a wrong known answer makes the scenario fail", async () => {
  const dir = await scenarioFolder([
    scenario("a wrong expectation", [event("event-1", false)], [knock("event-1")]),
  ]);
  const results = await runScenarios(options(dir));
  expect(results).toHaveLength(1);
  expect(results[0]?.passed).toBe(false);
  const lines: string[] = [];
  expect(report(results, (line) => lines.push(line))).toBe(1);
  const text = lines.join("\n");
  expect(text).toContain("a wrong expectation: failed");
  expect(text).toContain(JSON.stringify([knock("event-1")]));
  expect(text).toContain("messages: []");
});

// intents/product-test.md, check 4
test("no scenario is a failure", async () => {
  const dir = await scenarioFolder([]);
  const results = await runScenarios(options(dir));
  expect(results).toEqual([]);
  expect(report(results, () => {})).toBe(1);
});

// intents/product-test.md, check 5
test("a product that does not start makes the scenario fail", async () => {
  const pidFile = join(folder, "pid");
  const command = await scriptCommand(
    "silent.mjs",
    `import { writeFileSync } from "node:fs";
writeFileSync(process.argv[2], String(process.pid));
setInterval(() => {}, 1000);`,
    pidFile,
  );
  const dir = await scenarioFolder([scenario("silent", [event("event-1", true)], [])]);
  const results = await runScenarios(options(dir, { command, addressTimeoutMs: 1000 }));
  expect(results[0]?.passed).toBe(false);
  expect(results[0]?.reason).toContain("no address");
  const pid = Number(await readFile(pidFile, "utf8"));
  expect(() => process.kill(pid, 0)).toThrow();
});

// intents/product-test.md, check 6
test("the order of the messages counts", async () => {
  const events = [event("event-1", true), event("event-2", true)];
  const dir = await scenarioFolder([
    scenario("in order", events, [knock("event-1"), knock("event-2")]),
    scenario("in the other order", events, [knock("event-2"), knock("event-1")]),
  ]);
  const results = await runScenarios(options(dir));
  expect(results.map((result) => result.passed)).toEqual([true, false]);
});

// intents/product-test.md, check 7
test("no scenario sees the events of another one", async () => {
  const dir = await scenarioFolder([
    scenario("first", [event("event-1", true)], [knock("event-1")]),
    scenario("second", [event("event-2", false)], []),
  ]);
  const results = await runScenarios(options(dir));
  expect(results.map((result) => result.passed)).toEqual([true, true]);
});

// intents/product-test.md, check 8
test("a wrong answer or a wrong exit code makes the scenario fail", async () => {
  const dir = await scenarioFolder([scenario("one event", [event("event-1", false)], [])]);

  const answers500 = await scriptCommand("server500.mjs", fakeServer, "500", "0");
  const wrongAnswer = await runScenarios(options(dir, { command: answers500 }));
  expect(wrongAnswer[0]?.passed).toBe(false);
  expect(wrongAnswer[0]?.reason).toContain("500");

  const exits1 = await scriptCommand("exit1.mjs", fakeServer, "200", "1");
  const wrongCode = await runScenarios(options(dir, { command: exits1 }));
  expect(wrongCode[0]?.passed).toBe(false);
  expect(wrongCode[0]?.reason).toContain("exit code 1");

  const fine = await scriptCommand("fine.mjs", fakeServer, "200", "0");
  const control = await runScenarios(options(dir, { command: fine }));
  expect(control[0]?.passed).toBe(true);
});

// intents/product-test-corrections.md, checks 1 to 5
test("a file that is not valid JSON gives one failed line", async () => {
  const dir = join(folder, "bad");
  await mkdir(dir);
  await writeFile(join(dir, "broken.json"), "{ not json");
  const lines: string[] = [];
  expect(await runCommand(options(dir), (line) => lines.push(line))).toBe(1);
  expect(lines).toHaveLength(1);
  expect(lines[0]).toMatch(/^failed:/);
  expect(lines[0]).toContain("broken.json");
});

test("a missing folder gives one failed line", async () => {
  const lines: string[] = [];
  expect(await runCommand(options(join(folder, "missing")), (line) => lines.push(line))).toBe(1);
  expect(lines).toHaveLength(1);
  expect(lines[0]).toMatch(/^failed:/);
});

test("an address that arrives in two parts is read complete", async () => {
  const source = fakeServer.replace(
    /server\.listen\(.*\n.*\n\}\);/,
    `server.listen(0, "127.0.0.1", () => {
  const address = "http://127.0.0.1:" + server.address().port;
  process.stdout.write("product listens on http://127.0.0.1:" + String(server.address().port).slice(0, 1));
  setTimeout(() => process.stdout.write(String(server.address().port).slice(1) + "\\n"), 300);
});`,
  );
  const command = await scriptCommand("split.mjs", source, "200", "0");
  const dir = await scenarioFolder([scenario("split", [event("a", true)], [])]);
  const results = await runScenarios(options(dir, { command }));
  expect(results[0]?.reason).not.toBe("the messages differ from the known answer");
  expect(results[0]?.reason).toBeUndefined();
});

test("an address with no line break is not taken", async () => {
  const source = `
console.log = () => {};
process.stdout.write("product listens on http://127.0.0.1:1");
setInterval(() => {}, 1000);
process.on("SIGTERM", () => process.exit(0));
`;
  const command = await scriptCommand("nobreak.mjs", source);
  const dir = await scenarioFolder([scenario("nobreak", [], [])]);
  const results = await runScenarios(options(dir, { command, addressTimeoutMs: 1000 }));
  expect(results[0]?.passed).toBe(false);
  expect(results[0]?.reason).toBe("no address");
});

test("the command passes on the scenarios of the repository", async () => {
  const lines: string[] = [];
  expect(await runCommand(defaultOptions, (line) => lines.push(line))).toBe(0);
  expect(lines).toHaveLength(2);
  expect(lines.every((line) => line.includes("passed"))).toBe(true);
});
