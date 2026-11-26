<!-- charter-intent-review -->
Commit: e7ac5d91c6827edafece1fcff080c4bb5225cfdc

This is the first report. Each of the 23 changed lines only removes `Status: done.`. I could not read epic #82, and the command for it was denied. I checked the decision against the text of #117.

| File | Verdict | Finding |
|---|---|---|
| `intents/boundary-gate-reads-any-path.md` | approve | no finding |
| `intents/boundary-of-a-run.md` | approve | no finding |
| `intents/charter-version-in-ci.md` | approve | no finding |
| `intents/code-reviewer.md` | approve | no finding |
| `intents/default-lifecycle-map.md` | approve | no finding |
| `intents/drafted-reading-review.md` | approve | no finding |
| `intents/install-from-the-marketplace.md` | approve | no finding |
| `intents/intent-reviewer.md` | approve | no finding |
| `intents/one-closing-line.md` | approve | no finding |
| `intents/plan-before-the-code.md` | approve | no finding |
| `intents/plan-tier.md` | approve | no finding |
| `intents/product-test.md` | approve | no finding |
| `intents/reason-next-to-the-part.md` | approve | no finding |
| `intents/record-of-a-run.md` | approve | no finding |
| `intents/review-loop.md` | approve | no finding |
| `intents/review-rounds.md` | approve | no finding |
| `intents/reviewer-reads-the-diff-of-a-round.md` | approve | no finding |
| `intents/run-from-an-issue.md` | approve | no finding |
| `intents/runs-wait-in-order.md` | approve | no finding |
| `intents/sandbox-on-the-code-host.md` | approve | no finding |
| `intents/setup-step.md` | approve | no finding |
| `intents/toolchain-in-the-tests-workflow.md` | approve | no finding |
| `intents/verdict-merges.md` | approve | no finding |
| `intents/planned-intents.md` (not changed) | approve with a change | It still holds `Status: done`, so the change is incomplete and the change request's count is wrong. |

### Findings

**1. medium: `intents/planned-intents.md` keeps the status line**
- **Problem:** #117 says "The status line leaves the intent" and puts the intents of this repo in scope. The change request says it leaves "the 23 intents of this repo that held it". At least 24 held it: line 3 of this file still does.
- **Sentence to change:** `Work item: #40. Status: done. Approval: a person merges the change request that adds this file.`
- **Proposed text:** `Work item: #40. Approval: a person merges the change request that adds this file.`
- **Change request text:** Correct the count to 24. This intent also has no file in `plans/`, so "Four of the 23 intents are older than the plans" becomes five of 24. If a change request with code would also need a plan for this file, this is the place to edit it.
- **Next change request:** The in-scope text of this intent still requires "A status line in the intent: `Status: planned` or `Status: done`". Its second in-scope item and its automatic check also depend on that line. `intents/no-status-line.md` should say that it replaces this behaviour. It should also say what happens to `PlannedIntents.test_planned_intents_need_no_existing_test`, which this intent names.

**2. low: these edits come before the intent of #117**
- **Problem:** The edits carry out part of the in-scope work of #117. The change request says that `intents/no-status-line.md` comes in the next one, and the file is not in this checkout. The repo rules describe `Part of #N` as being for the intent of the Plan phase. A person should decide whether this order is acceptable.
- **Sentence to change (change request text):** "The template, the test of the intents, and the intent of this work item come in the next change request."
- **Proposed text:** Add `intents/no-status-line.md` to this change request, then change the sentence to "The template and the test of the intents come in the next change request."

**Effect on the intent test, from reading `tests/test_intents.py` (not run):** it treats an intent with no status line as `done`. Removing `done` therefore does not change how these intents are checked.

Highest open severity: medium