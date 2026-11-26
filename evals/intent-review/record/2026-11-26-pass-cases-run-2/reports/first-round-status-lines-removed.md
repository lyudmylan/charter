<!-- charter-intent-review -->
Commit: 9ecfeac129ae6b96c9ec28c995e636860983d4dc

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
| `intents/planned-intents.md` (not changed) | needs discussion | It still holds the status line, so the removal is incomplete. |

The diff of each of the 23 changed files removes only `Status: done.`. The current test reads a missing line as `done` (`tests/test_intents.py:32`), so these removals don't change how it treats those files.

**1. medium: `intents/planned-intents.md`, line 3**
- **Problem:** The change request says "The status line leaves the 23 intents of this repo that held it". At least 24 held it, because this file still does. #117 decides that the status line leaves the intent, and its scope includes the intents of this repo.
- **Sentence to change:** `Work item: #40. Status: done. Approval: a person merges the change request that adds this file.`
- **Proposed text:** `Work item: #40. Approval: a person merges the change request that adds this file.` In the change request, change "23" to "24" in both places. "No other text changes" can stay.

**2. medium: change request text, order of the work**
- **Problem:** #117 names `intents/no-status-line.md`, which is not among the intent files and comes only in the next change request. This one already does part of the issue's scope, "the intents of this repo", before any acceptance checks for it are approved. It says `Part of #117`, which `AGENTS.md` describes as being for the intent of the Plan phase. The exemption from a plan for intent-only changes is meant for that phase. The stated reason for the split is that code would require plans for older intents it touches.
- **Sentence to change:** "The template, the test of the intents, and the intent of this work item come in the next change request."
- **Proposed text:** "The intent of this work item comes first, in its own change request. The removal of the status lines follows its approval." If the leader accepts the present order, the author can record that with a `Dropped finding: <reason>` line.

**3. low: `intents/planned-intents.md`, "In scope" and check 1, for the next intent**
- **Problem:** These still describe `planned` and `done` as the current behaviour. #117 replaces that with whether the intent's plan exists. Some older intents have no plan, including `intents/review-loop.md` and `intents/charter-version-in-ci.md`. If the new test simply looks for a plan, it would stop checking that their named tests and scripts exist.
- **Sentence to change:** "A status line in the intent: `Status: planned` or `Status: done`."
- **Proposed text:** Leave this sentence unchanged here. Add to `intents/no-status-line.md`: "This intent replaces the status line of `planned-intents`. An intent built before the plans is still checked for the tests and scripts it names." Its acceptance checks should cover both points.

Highest open severity: medium