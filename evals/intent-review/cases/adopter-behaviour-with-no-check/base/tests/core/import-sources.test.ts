// The finder of the sources of the imports.
import { expect, test } from "vitest";

import { sources } from "./import-sources.ts";

// intents/review-corrections.md, check 1
test("a comment with the text of an import counts as an import", () => {
  expect(sources('// import x from "./a.ts"\n')).toEqual(["./a.ts"]);
  expect(sources('/* import "./b.ts" */\n')).toEqual(["./b.ts"]);
});

// intents/review-corrections.md, check 2
test("a require form is an import", () => {
  expect(sources('const fs = require("node:fs");')).toEqual(["node:fs"]);
  expect(sources('import fs = require("node:fs");')).toEqual(["node:fs"]);
});

// intents/review-corrections.md, check 3
test("the four known forms keep their sources", () => {
  const text = [
    'import { a } from "./a.ts";',
    'export { b } from "./b.ts";',
    'import "./c.ts";',
    'const d = await import("./d.ts");',
  ].join("\n");
  expect(sources(text).sort()).toEqual(["./a.ts", "./b.ts", "./c.ts", "./d.ts"]);
});
