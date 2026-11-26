<!-- charter-intent-review -->
Commit: f05c670c365a5231b523d13a604cb5027127ef6c

Each of the 23 diffs removes only `Status: done.`. By reading `tests/test_intents.py:29-32`, an intent without the line counts as done, so these edits keep the existence checks. I ran no tests. Epic #82 could not be read, so consistency with its decisions is unchecked.

| File (`intents/`) | Verdict | Finding |
|---|---|---|
| `boundary-gate-reads-any-path.md` | approve | no finding |
| `boundary-of-a-run.md` | approve | no finding |
| `charter-version-in-ci.md` | approve | no finding |
| `code-reviewer.md` | approve | no finding |
| `default-lifecycle-map.md` | approve | no finding |
| `drafted-reading-review.md` | approve | no finding |
| `install-from-the-marketplace.md` | approve | no finding |
| `intent-reviewer.md` | approve | no finding |
| `one-closing-line.md` | approve | no finding |
| `plan-before-the-code.md` | approve | no finding |
| `plan-tier.md` | approve | no finding |
| `product-test.md` | approve | no finding |
| `reason-next-to-the-part.md` | approve | no finding |
| `record-of-a-run.md` | approve | no finding |
| `review-loop.md` | approve | no finding |
| `review-rounds.md` | approve | no finding |
| `reviewer-reads-the-diff-of-a-round.md` | approve | no finding |
| `run-from-an-issue.md` | approve | no finding |
| `runs-wait-in-order.md` | approve | no finding |
| `sandbox-on-the-code-host.md` | approve | no finding |
| `toolchain-in-the-tests-workflow.md` | approve | no finding |
| `setup-step.md` | approve | no finding |
| `verdict-merges.md` | approve | no finding |

The findings below concern the change request as a whole.

**1. high: `intents/planned-intents.md` still has the status line and requires it**
- **Problem:** #117 says "The status line leaves the intent" and includes this repo's intents. This file was not changed, so the description's "23 intents of this repo that held it" is incomplete: 24 held it. Its scope also says the status and the issue state "are not the same fact", which contradicts the leader's decision in #117.
- **Change:** on line 3, delete `Status: done.`. Replace the sentences from "A status line in the intent" through "the two are not the same fact." with:
  > "An intent holds no status line; the state of the issue says whether the work item is built. For an intent without a plan, the test verifies the four fields and that each automatic check names a test or a command. For an intent with a plan, it also verifies that the named tests and scripts exist."
- **Also:** change "A status in the intent" wherever the rewrite leaves it, including "A gate that forces the status to change when the work item closes", to "A gate on the state of the issue." Reword check 1 to match. Keep its current test reference until the code change replaces that test.

**2. high: `intents/no-status-line.md` is missing**
- **Problem:** #117 names this intent, but the description defers it to the change request with the template and test. This one already carries out the "intents of this repo" part of the scope, using `Part of #117`, which is meant for the Plan phase. There is no intent for #117 to approve first. The code's intent would also arrive with the code, although `AGENTS.md` requires approval before it.
- **Description sentence to change:** "The template, the test of the intents, and the intent of this work item come in the next change request."
- **Proposed text:** "This change request adds `intents/no-status-line.md` for approval. The template and the test come in a later change request, with the plan." Add that file here, with scope, out of scope and acceptance checks.

**3. medium: `intents/no-status-line.md`, the planned rule would skip checks on built intents**
- **Problem:** #117 says the test will use plan existence instead of the status line. Some built intents have no plan, including `charter-version-in-ci.md`, `default-lifecycle-map.md`, `install-from-the-marketplace.md` and `review-loop.md`. Under that rule alone, their missing tests or scripts would pass unnoticed. `plan-tier.md` has its plan only at the old path, `intents/plan-tier.plan.md`.
- **Sentence to settle (#117):** "The test of the intents of this repo reads another fact in its place: the plan of the intent exists, and a plan arrives together with the code."
- **Proposed text for the new intent:** "The named tests and scripts must exist for each intent with a plan, at either plan path, and for each older built intent without one, from an explicit list in the test." Add an automatic check that a listed intent with a missing test fails. The leader should confirm this addition to the decision.

Highest open severity: high