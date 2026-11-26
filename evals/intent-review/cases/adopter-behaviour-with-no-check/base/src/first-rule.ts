// The first rule, as data, until the configuration exists. The core holds no rule.

import type { Rule } from "./core/rule.ts";

/** An urgent event gets a knock. */
export const urgentGetsKnock: Rule = {
  name: "an urgent event gets a knock",
  when: { value: "urgent", equals: true },
  action: "knock",
};
