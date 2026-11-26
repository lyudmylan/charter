<!-- charter-intent-review -->
Commit: c0986dacd521b93c7aed3ed09dfe0c582e43e1cc

## Changed since the last report

No earlier report exists on this change request. This is the first round.

## Scope of this review

The change request is stacked on #100 and #103 to #110, so the diff against main holds 13 intents and 16 plans. The intent and the plan of this work item (#99) are `intents/product-test.md` and `plans/product-test.md`. I reviewed those two in full. The other files belong to the base change requests and are reviewed there; I did not review them here.

| File | Verdict | Finding |
|---|---|---|
| `intents/product-test.md` | approve with a change | The goal says each evidence record shows the reason, and the scope says the evidence record holds the state of the check `product`. No check proves either. |
| `plans/product-test.md` | approve with a change | The plan adds a verdict state `product test: not reported`, and a rule that a reason of blanks is no reason. The intent has no check for either. |
| the other intents and plans of the diff | not reviewed here | They belong to the base change requests. |

## Findings

1. **high**, `intents/product-test.md`, check 5. The Goal says "a reason that each evidence record shows" and the scope says "the evidence record holds its state". Check 5 covers only the line the verdict prints. No check shows that the evidence record holds the state of the check `product` or the reason. Either add a test that reads the record, or change the Goal and the scope to say that the verdict line is where the reason shows.
   Proposed text for the Goal: "…and a repo that has no such test says so with a reason that the verdict shows at each merge."

2. **medium**, `intents/product-test.md`, check 5. The plan adds the verdict state `product test: not reported`, for a contract with commands and no check `product` in the facts. The intent lists two forms of the line and one failure case. The third state is a behaviour that no check names. Add it to check 5: "a contract with commands and no check `product` in the facts prints `product test: not reported`, and the change request is not ready." Add a test name for it.

3. **low**, `intents/product-test.md`, check 2. The plan says a reason of blanks only is no reason. The intent checks do not name it. Add it to check 2, or drop the sentence from step 2 of the plan.

4. **low**, `intents/product-test.md`, "In scope", intent of a work item. The issue (#99) says "the template of an intent and the tracker skill say so". The intent names the skill `intent-review` instead. Say in the text of the change request why the tracker skill is not named, or add it.

5. **low**, `intents/product-test.md`, "Out of scope". Issue #99 allows "or the contract names the part that runs in the CI only". The intent drops that option and says a product test that needs the network or a secret runs in the job `product` only. State that this replaces the option of the issue. A run then has no product test for that part.

## Other checklist points

Goal, scope, and the out-of-scope line are real and bounded. Manual check 11 names who does it and why it is not automatic. Each automatic check names a test or a command. Both new fields are in the schema, in `docs/contract.md`, and in the checks. The plan matches the intent otherwise.

Highest open severity: high
