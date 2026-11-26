// The test runner runs and the package imports. The first real tests come with the first intent.
import { expect, test } from "vitest";

import { name } from "../src/index.js";

test("the package imports", () => {
  expect(name).toBe("product");
});
