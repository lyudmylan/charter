<!-- charter-intent-review -->
Commit: 01012dcfe736188be2c28ffc9ccf78e6f011a074

Epic #13 could not be read (`gh issue view 13` is not available here). I checked epic decisions against `docs/decisions.md`, issue #66 and the intent.

| File | Verdict | Finding |
|---|---|---|
| `intents/verdict-merges.md` | needs discussion | The code-review condition doesn't fit a change with only plans or intents. Nothing in the merge conditions keeps an intent with a person. Checks 2 and 6 leave stated behaviour out. |
| `plans/verdict-merges.md` | approve with a change | Step 2 repeats the intent's merge conditions but leaves out the one for the code-review report. |

**1. high: `intents/verdict-merges.md`, the code-review condition**
Sentence: "`review.code_blocks` is true, so the reviewer of the code is past its shadow period, and its newest report is closed on the head commit (#95);"

The code reviewer reviews only files outside `intents/` and `plans/`. As written, a change with only plans needs a report that this reviewer does not owe. `merge_decision` instead skips the report and can merge such a change. C12 and `docs/contract.md` also state the condition without this exception.

Proposed: "`review.code_blocks` is true, so the reviewer of the code is past its shadow period; when the change holds a file outside `intents/` and `plans/`, its newest report is closed on the head commit (#95);"

Align C12 and `docs/contract.md`, and make check 1 cover a ready change with only plans.

**2. high: `intents/verdict-merges.md`, intents and the agent tier**
Sentence: "A change request that holds an intent is in the high tier and stays with a person."

This depends on each contract's tier paths and approvers, and the gate does not enforce it. If an intent falls in an `agent` tier, a closed intent review lets the verdict merge it. The test with `intents/app.md` runs against such a tier. That conflicts with D5 (a person approves acceptance checks) and with this intent's out-of-scope line, which leaves agent approval of intents undecided.

Proposed: "A change request that holds a file under `intents/` stays with a person, whatever its tier: the gate names this as the reason." Limit the intent-review merge condition to what remains eligible, add an automatic check for this case, and align the gate, C12 and `docs/contract.md`.

**3. medium: `intents/verdict-merges.md`, check 2**
Sentence: "It says that a person merges, with the reason, in each other case: …"

The list omits a code report that is missing, open or on another commit, and facts with no head commit. Check 1 covers only success, so the listed cases do not require the goal's "reviews closed on its head commit".

Proposed: add "a change of code whose newest code report is missing, is open, or names another commit; facts with no head commit", with a named test for each. Where readiness already fails, the expected reason is "the verdict is not ready".

**4. medium: `intents/verdict-merges.md`, check 6**
Sentence: "With a record of a person's merge, or without a token, it calls no merge and ends well."

The scope says a merge refused by the code host fails the run, but no check says so. The named merge test already exercises a refusal.

Proposed: add "When the code host refuses the merge, the step fails."

**5. medium: `plans/verdict-merges.md`, step 2**
Sentence: "It checks the conditions of the intent in their order and names the first one that fails: not ready; … or names another commit than `head_commit`."

This second copy of the conditions omits the code report being closed on the head commit. An author following the list could leave out that condition.

Proposed: "It checks the conditions of the intent, section In scope, in their order and names the first one that fails; a missing fact, including `head_commit`, means that a person merges."

Highest open severity: high