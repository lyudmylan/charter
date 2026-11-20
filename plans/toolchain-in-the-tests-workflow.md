# Plan: the workflows have a declared place for the toolchain of the repo (#88)

Intent: `intents/toolchain-in-the-tests-workflow.md`, checks 1 to 7. Checks 8 and 9 are manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.

## Steps

1. `charter/templates/tests.yml`: after the checkout step, a comment line that says what the block is
   for and that its steps run with no secret, then the placeholder of the setup step for the block
   between the two marker lines, each with the indent of a step. `.github/workflows/tests.yml`: the two
   marker lines with nothing between them.
2. `charter/scripts/charter_setup.py`:
   - The two marker lines and the indent of a step as constants.
   - A flag `--toolchain FILE`. A function reads the file, refuses it when it is missing or holds a
     marker line, and gives each line the indent of a step; an empty line stays empty. Without the flag
     the block holds nothing. The value goes into the rendering of `tests.yml` only.
   - A function `toolchain_of(text)`: the lines between the two markers of a workflow text, without the
     indent of a step, as one text; no step gives an empty text.
   - The refusal comes before any file is written, as the other refusals of the setup step do.
3. The checkout action: `v7` in `charter/templates/tests.yml`, `charter/templates/review-intents.yml`,
   `charter/templates/review-code.yml`, and the three files of the same names in `.github/workflows/`.
   `charter/templates/verdict.yml` and `.github/workflows/verdict.yml` keep `v4`.
4. `docs/contract.md`, section "The setup step": the flag, the form of the file, the two marker lines,
   and one sentence that an update of the repo keeps the block.
5. Both manifests: 0.3.12. `intents/toolchain-in-the-tests-workflow.md`: `Status: done`.

## Files

- `charter/templates/tests.yml`, `.github/workflows/tests.yml`
- `charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`
- `charter/templates/review-code.yml`, `.github/workflows/review-code.yml`
- `charter/scripts/charter_setup.py`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/toolchain-in-the-tests-workflow.md`, `plans/toolchain-in-the-tests-workflow.md`
- `tests/test_workflows.py`

## Tests

A class `Toolchain` in `tests/test_workflows.py`, seven tests, with the names that the intent gives. The
sample of check 2 is three steps: an action that installs a package manager, an action that installs a
runtime with a `with:` block, and a step with a `run:` line. The test of check 1 compares the written
workflow with its template.
