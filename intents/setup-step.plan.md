# Plan: the verdict template declares `actions: read` (#63)

Intent: `intents/setup-step.md`, check 7. Accepted by the leader in the conversation on 2026-10-29, before
the code.

## Steps

1. `charter/templates/verdict.yml` and `.github/workflows/verdict.yml`: the line `actions: read` in the
   permissions block, so that the template and the workflow of this repo stay identical. The scope states
   what the facts step does: it lists the runs of the review workflow to count the rounds. A public repo
   serves that listing without the scope; a private repo does not. One template for both: the permissions
   block of a workflow has no conditions, and a read scope widens nothing.
2. `tests/test_setup.py`, class `Templates`: `test_verdict_template_declares_actions_read`. The written
   `verdict.yml` has a permissions block, and the block contains `actions: read`.
3. `intents/setup-step.md`: one bullet in the scope records the finding and its cause; check 7 names the
   test, which reads both verdict files. Found while running the checks: the tests of the intents read this plan file as an intent, because
   no plan file had existed next to an intent before. `tests/test_intents.py` skips `*.plan.md`, and
   `intents/plan-before-the-code.md` records it as check 3.
4. `charter/.claude-plugin/plugin.json` and `charter-practices/.claude-plugin/plugin.json`: version 0.3.1,
   so that an adopter can name the version that carries the fix.
5. One change request, `Closes #63`, with the line `No document change`: the product does not change. After
   the merge the leader pushes the tags `charter--v0.3.1` and `charter-practices--v0.3.1`.

## Files

`charter/templates/verdict.yml`, `.github/workflows/verdict.yml`, `tests/test_setup.py`,
`intents/setup-step.md`, the two manifests, and this file.

## Tests

One new test, step 2. The existing test `Commands.test_the_four_commands_exist_and_the_manifests_agree`
covers step 4.
