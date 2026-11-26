// Finds the sources of the imports in a text, for the check on the imports of the core.
//
// It removes no comment and reads the whole text. So a comment that holds the text of an import counts
// as an import, and the check fails on it. This is on purpose: a rule that removes comments can hide an
// import, a missed import is a false pass, and a false pass is worse than a false failure. When the check
// fails on a comment, write the comment in other words.

// Each source of an import or an export: `import ... from "x"`, `export ... from "x"`,
// `import "x"`, `import("x")`, and `require("x")`. The last also covers `import x = require("x")`.
const sourcePatterns = [
  /\b(?:import|export)\s[^;]*?\bfrom\s*["']([^"']+)["']/g,
  /\bimport\s*["']([^"']+)["']/g,
  /\bimport\s*\(\s*["']([^"']+)["']/g,
  /\brequire\s*\(\s*["']([^"']+)["']/g,
];

export function sources(text: string): string[] {
  return sourcePatterns.flatMap((pattern) =>
    [...text.matchAll(pattern)].map((match) => match[1] ?? ""),
  );
}
