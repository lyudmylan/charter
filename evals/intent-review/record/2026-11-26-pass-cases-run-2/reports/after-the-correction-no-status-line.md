<!-- charter-intent-review -->
Commit: 0d79e823cf004cd85a3dac7040b948e2343e9a26

## Changed since the last report
- `intents/no-status-line.md`:
  - The sentence that a plan arrives with the code in a session and in a run is gone.
  - A new bullet says how a plan reaches the main branch, in a run and in a session, and what happens when it is merged before its code.
  - The bullet on the older intents no longer gives their number. It now says the list cannot grow.
  - The version sentence is gone.
  - Check 2 now covers the fault for a missing test, and the fixed size of the list.
- `plans/no-status-line.md`: step 4 no longer gives the number of older intents. It adds a test case with a plan that is merged before its code.

| File | Verdict | Finding |
|---|---|---|
| `intents/no-status-line.md` | approve | One low finding: the sentence on a plan that is merged early says the test always fails. |
| `intents/planned-intents.md` (deleted) | approve | No finding. |
| `plans/no-status-line.md` | approve | No finding. |

## Findings

1. **low**, `intents/no-status-line.md`, in scope: "A plan that is merged before its code makes its intent count as built: the test then fails and names each test that does not exist."
   The test fails only if a named test file, test or Python script is missing. An intent whose checks name only things that already exist would pass.
   Proposed text: "A plan that is merged before its code makes its intent count as built: the test then fails for each named test or script that does not exist."

The three findings of the last report are addressed in the intent:
- **Session and run:** the new text matches `docs/product.md` and `AGENTS.md`. No tier in `charter.toml` has the approver `agent`, so a person accepts the plan in a session.
- **Version:** the sentence is gone from the intent. The plan still states it under "Not changed".
- **Number of older intents:** it is gone from the intent and the plan. The test still holds it.

The new text of check 2 matches `test_the_plan_says_that_a_work_item_is_built`, and step 4 of the plan matches the tests. I read the tests but did not run them. I could not read epic #82, so consistency with its decisions is not checked. The intent agrees with the decision in issue #117 to remove the status line.

Highest open severity: low