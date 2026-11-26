<!-- charter-intent-review -->
Commit: df86e04c0c0d0846b480961a143583eebdc56577

| File | Verdict | Finding |
|---|---|---|
| `intents/one-closing-line.md` | approve with a change | The scope says any list marker is covered, but the script and plan handle it as `-`, `*` or `+` only. The manual check can also pass without exercising the fix. |

The plan, `plans/one-closing-line.md`, has one finding below. The epic #82 could not be read (`gh issue view 82` says it is not in this case), so consistency with its decisions is not checked.

**1. medium: `intents/one-closing-line.md`, list markers**
- **Problem:** `LIST_MARKER` in `charter/scripts/charter_run.py` is `^[-*+]\s+`. A line such as `1. Closes #7` therefore stays in the published text. The scope promises that a list marker makes no difference. Check 1 says "with a list marker", but its test cases use only `-` and `*`.
- **Sentence to change:** "A list marker before the link, marks of emphasis around it, and a full stop after it do not change this."
- **Proposed text:** "A bullet marker (`-`, `*` or `+`) before the link, marks of emphasis around it, and a full stop after it do not change this. A line in a numbered list stays."
- **Also change:** in check 1, replace "with a list marker" with "with a bullet marker". If numbered lists should be covered instead, keep the scope sentence, say that it includes numbered markers, and add that case to the script and the check 1 test.

**2. medium: `plans/one-closing-line.md`, acceptance of the plan**
- **Problem:** `AGENTS.md` [build.plan_before_code] says the code starts after the plan is accepted. The exception for code that comes with the plan is a run with no person present. The plan does not say this was such a run, or that the leader accepted this order in advance. `plans/boundary-gate-reads-any-path.md` records an advance acceptance with its date, for the plans of its own milestone. This plan cites nothing like it.
- **Sentence to change:** "The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three."
- **Proposed text:** "The leader accepted this order in advance, on <date and place of the acceptance>: the intent, the plan, and the code reach the leader together, and the merge of the leader approves the three." Use this only if that acceptance happened. If it did not, the person who holds the work item needs to decide on the order, and the plan should record what they decide.

**3. low: `intents/one-closing-line.md`, check 6**
- **Problem:** If the agent in the next run does not write the closing line, check 6 passes even though nothing had to be left out.
- **Sentence to change:** "The next run at an adopter, with this version, publishes a change request whose text holds the closing line one time."
- **Proposed text:** "The first run at an adopter, with this version, in which the agent's file holds a line that only links the issue of the run, publishes a change request whose text holds the closing line one time."

Highest open severity: medium