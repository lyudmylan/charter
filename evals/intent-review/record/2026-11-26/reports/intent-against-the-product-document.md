<!-- charter-intent-review -->
Commit: 6205d8650be17aa00ed4e4ae456b44852b90a5fa

| File | Verdict | Finding |
|---|---|---|
| `intents/no-status-line.md` | needs discussion | The closed-list rule makes any new intent without a plan fail, so an intent-only change request cannot pass. Check 3 also misses some status lines, and later changes to a built intent are not covered. |
| `intents/planned-intents.md` (removed) | approve | no finding |
| `plans/no-status-line.md` | approve with a change | Step 4 builds the closed-list test as the intent describes it, so it needs the fix in finding 1. |

**1. blocker: `intents/no-status-line.md`, the closed list**

The intent says "An intent with no plan is not built yet, and its named tests may be missing." It also says of the test: "It fails when an intent with no plan is not on the list, so a new intent cannot hide there."

The Plan phase is a change request with only intents, and it needs no plan. Such a new intent has no plan and is not among the thirteen. `test_the_plan_says_that_a_work_item_is_built` asserts `no_plan == set(BEFORE_THE_PLAN)` (`tests/test_intents.py:164`), so the tests turn red. The allowance for missing tests therefore never helps a new intent in this repo.

Proposed text for the second sentence: "The test fails when a name on the list has no intent or has a plan, or when the list does not hold thirteen names. A new intent with no plan passes and is not built."

In check 2, replace "and no other intent of this repo lacks a plan" with "and each of them is an intent of this repo with no plan". The test should then assert that `BEFORE_THE_PLAN` is a subset of `no_plan`, and keep the count. Step 4 of the plan and the test's docstring should follow.

**2. high: `intents/no-status-line.md`, check 3**

The sentence is "No intent of this repo holds a status line, and the template holds none."

The named test uses `^Work items?: .*\bStatus:`. It misses a `Status: done` line of its own. It also misses `Status:` on the second line of a wrapped header, and `intents/contract-checker.md` has a wrapped header. Both would break the goal while the check passes. The product test covers only the template that setup writes.

Proposed text: "No intent of this repo and not the template holds `Status:` at the start of a line, or anywhere before `## Goal`." The test should check both. This leaves the quoted `Status: planned` in the body of this intent alone.

**3. medium: `intents/no-status-line.md`, later changes to a built intent**

The sentence is "An intent with no plan is not built yet, and its named tests may be missing."

A built intent can get a further work item: `intents/intent-reviewer.md` names two. Suppose an intent-only change request adds a check with a test not yet written to an intent that has a plan, or to one of the thirteen. `built` returns true, so the tests fail. Before this change, the header could be set to `planned`. The intent neither covers this case nor excludes it.

Proposed addition under "Out of scope", if the limit is accepted: "A new check on a built intent whose test does not exist yet: it arrives in the change request that adds the test." This puts that check's approval together with its code, so the leader should decide it. The alternative is to put such work in a new intent, which works once finding 1 is fixed.

I could not read epic #82 (`gh issue view 82` failed), so consistency with its decisions is unchecked. I ran no tests; these findings come from reading the files and diffs.

Highest open severity: blocker