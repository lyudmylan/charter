<!-- charter-intent-review -->
Commit: 43cf677feff91d7fe1c43932af3c3b63605dddca

## Changed since the last report

No earlier report exists on this change request. This is the first round.

## Scope of this review

The change request is stacked on #100 and #103 to #107, so the diff against main holds 10 intents and 13 plans. The intent and the plan of this work item (#88) are `intents/toolchain-in-the-tests-workflow.md` and `plans/toolchain-in-the-tests-workflow.md`. The other files belong to the change requests that the text names; I did not re-review them here. I read them only to check that the plan location (`plans/`) is used consistently. `intents/plan-tier.plan.md` stays at the old place on purpose, as `intents/plan-tier.md` says.

## Table

| File | Verdict | Finding |
|---|---|---|
| intents/toolchain-in-the-tests-workflow.md | approve with a change | The goal promises that a later version of the workflow keeps the block, but the update is out of scope (#97), so no check here proves it. Checks 6 and 5 pin the text and a transient version state. |
| plans/toolchain-in-the-tests-workflow.md | approve | no finding |
| other intents and plans of the stack | not reviewed here | They belong to the change requests that introduced them. |

## Findings

1. low, `intents/toolchain-in-the-tests-workflow.md`, Goal: "...and the install steps have one marked place that a later version of the workflow keeps."
   The keeping is #97. Check 3 proves only that the block can be read back.
   Proposed: "...and the install steps have one marked place that a function can read back, so that a later update can keep it."

2. low, `intents/toolchain-in-the-tests-workflow.md`, check 5: "and the verdict workflow keeps `v4`."
   The test pins a state that the intent itself calls temporary. When the verdict workflow moves, this test must change in a change that has no intent of its own.
   Proposed: add to check 5 "The follow-up change that moves the verdict workflow changes this test."

3. low, `intents/toolchain-in-the-tests-workflow.md`, In scope, the last bullet but one: "the rule that an update keeps the block."
   The template line that says the steps run with no secret (plan step 1) has no check. Check 1 compares the written workflow with its template, which covers the comment only if the test compares the comment line.
   Proposed: add to check 1 "The template holds the comment line that says the steps run with no secret."

The issue says the checkout date is 2026-11-19 and the intent says 2026-11-20 for "v7". This is not a finding: both are the same major version.

Highest open severity: low
