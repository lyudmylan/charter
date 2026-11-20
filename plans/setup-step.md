# Plan: the verdict publishes its check also when it could not run (#68)

Intent: `intents/setup-step.md`, check 8. Accepted by the leader in the conversation on 2026-11-09, before
the code. This file replaces the plan of #63, which stays in the history and in change request #64.

## Decision

The issue names a new intent, `intents/verdict-fallback-check.md`. The fix is one more check of the
verdict workflow template, which `intents/setup-step.md` owns (check 7 is the precedent, #63). The issue
line changes to `Intent: intents/setup-step.md`; no new intent, no Plan-phase change request.

## Steps

1. `charter/templates/verdict.yml` and `.github/workflows/verdict.yml`, the step "Publish the check":
   the two reads of `verdict.txt` end with `|| true`, so that a missing file does not end the step under
   the `-e` shell of the host; the fallback title "the verdict could not run" and its summary then apply,
   and the step still ends with a failure when the conclusion is not success. The commit of the check,
   `PR_SHA`, falls back to `github.event.workflow_run.head_sha` when the step "Find the change request"
   did not run, so that a failure before that step still publishes the check on the commit of the run.
2. `tests/test_setup.py`, class `Templates`: `test_the_check_is_published_when_the_verdict_could_not_run`.
   The test takes the `run:` text of the step from the written `verdict.yml` and runs it with `bash -e`
   in an empty folder, with a `gh` on the path that records its arguments. Without `verdict.txt`: the
   recorded call carries `conclusion=failure` and the title "the verdict could not run", and the step
   exits with a failure. With a `verdict.txt` that says `ready` and `VERDICT_CODE=0`: exit 0 and
   `conclusion=success`. The test also asserts that the step has the same text in the template and in
   the workflow of this repo, and that the text of `PR_SHA` names `steps.pr.outputs.sha` and
   `github.event.workflow_run.head_sha`: an expression that the host evaluates.
3. `intents/setup-step.md`: one bullet in the scope records the finding (2026-11-02: the fetch of the
   organization source failed on an expired token; the author saw two green checks and no verdict);
   check 8 names the test; the manual check becomes 9.
4. `docs/contract.md`, the table "On the code host", row `verdict`: it publishes the check "verdict"
   also when the verdict could not run, with the reason in the check.
5. One change request, `Closes #68`, with the line `No document change: the product does not change;
   one step of a workflow template`. No version change: the versions move once, in the last change
   request of the four (#70). An adopter copies the step into its own `verdict.yml`: the setup writes
   the workflows once and does not overwrite them.

## Files

`charter/templates/verdict.yml`, `.github/workflows/verdict.yml`, `tests/test_setup.py`,
`intents/setup-step.md`, `docs/contract.md`, and this file.

## Tests

One new test, step 2. It runs the shell of the step, not a text match: the defect was in what `bash -e`
does with a failed command substitution, which a text match does not see.
