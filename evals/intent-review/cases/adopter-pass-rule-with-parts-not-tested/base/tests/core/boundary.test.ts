// Two checks that hold for each later change of the core.
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "vitest";

const coreFolder = resolve(dirname(fileURLToPath(import.meta.url)), "../../src/core");

// The terms of the on-call use case that the core must not hold.
const terms = [
  "alert",
  "on-call",
  "Alertmanager",
  "Prometheus",
  "severity",
  "severe",
  "incident",
  "engineer",
];

function coreFiles(): string[] {
  const entries = readdirSync(coreFolder, { recursive: true, withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".ts"))
    .map((entry) => join(entry.parentPath, entry.name));
}

// Each source of an import or an export: `import ... from "x"`, `export ... from "x"`,
// `import "x"`, and `import("x")`.
const sourcePatterns = [
  /\b(?:import|export)\s[^;]*?\bfrom\s*["']([^"']+)["']/g,
  /\bimport\s*["']([^"']+)["']/g,
  /\bimport\s*\(\s*["']([^"']+)["']/g,
];

function sources(text: string): string[] {
  return sourcePatterns.flatMap((pattern) =>
    [...text.matchAll(pattern)].map((match) => match[1] ?? ""),
  );
}

function staysInCore(file: string, source: string): boolean {
  if (!source.startsWith("./") && !source.startsWith("../")) {
    return false;
  }
  const target = relative(coreFolder, resolve(dirname(file), source));
  return target !== "" && !target.startsWith(`..${sep}`) && target !== "..";
}

// intents/urgent-event-knock.md, check 8
test("the core imports no file outside the core", () => {
  const files = coreFiles();
  expect(files.length).toBeGreaterThan(0);
  const outside = files.flatMap((file) =>
    sources(readFileSync(file, "utf8"))
      .filter((source) => !staysInCore(file, source))
      .map((source) => `${relative(coreFolder, file)}: ${source}`),
  );
  expect(outside).toEqual([]);
});

// intents/urgent-event-knock.md, check 9
test("the core holds no term of the on-call use case", () => {
  const files = coreFiles();
  expect(files.length).toBeGreaterThan(0);
  const found = files.flatMap((file) => {
    const text = readFileSync(file, "utf8").toLowerCase();
    return terms
      .filter((term) => text.includes(term.toLowerCase()))
      .map((term) => `${relative(coreFolder, file)}: ${term}`);
  });
  expect(found).toEqual([]);
});
