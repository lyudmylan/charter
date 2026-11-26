<!-- charter-intent-review -->
Commit: 6d04aa149496c212940d4a3e84622d927a15fcbb

## Changed since the last report
No earlier report exists on this change request. This is the first round; all changes of `intents/` and `plans/` are reviewed below.

| File | Verdict | Finding |
|---|---|---|
| `intents/no-status-line.md` | approve with a change | The claim "A plan arrives together with the code, in a session and in a run" contradicts the product document and AGENTS.md: in a session the plan is accepted before the code. |
| `intents/planned-intents.md` (deleted) | approve | No finding. The intent says why it leaves, and check 1 keeps its rule. |
| `plans/no-status-line.md` | approve | No finding. Steps, files and tests match the intent and the diff of `tests/test_intents.py`. |

## Findings

1. **medium**, `intents/no-status-line.md`, in scope, the sentence "A plan arrives together with the code, in a session and in a run. An intent with no plan is not built yet, and its named tests may be missing."
   `docs/product.md` (Build row) and AGENTS.md say that in a session the plan is accepted before the code. Only a run has the plan with the code. If a plan is merged alone, its intent counts as built (`built()` reads the plan), and the test fails on main for a test that does not exist yet.
   Proposed text: "In a run, the plan arrives together with the code. In a session, the plan is accepted before the code, so a plan that is merged alone makes its intent count as built: the plan, its tests and its code go in one change request, or the named tests exist first." If a plan on its own must be allowed, the fact that says "built" needs another source than the plan; then say so in the intent.

2. **low**, `intents/no-status-line.md`, "The version stays 0.3.17: no tag names it yet."
   This fact goes stale at the next tag, and the plan states it again ("Not changed"). Keep it in the change request text only, or in one place.

3. **low**, `intents/no-status-line.md`, "Thirteen intents of this repo are older than the plans" and check 2, "The thirteen older intents".
   The number is in the intent, in the plan, in the test (`len(BEFORE_THE_PLAN) == 13`) and in the text of the change request. The test already makes the list the fact; the intent can say "the intents older than the plans, which a closed list in the test names" without the number.

Checked with no finding: goal is one result sentence; the out-of-scope line is real; checks 1 to 4 each name a test or a command; check 4 names the product-test step for the changed template; there are no manual checks and none are needed. The count of 13 older intents matches the folder (34 intents, 21 with a plan).

Highest open severity: medium
