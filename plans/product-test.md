# Plan: the contract names the test of the product as a whole, and a change request needs its result (#99)

Intent: `intents/product-test.md`, checks 1 to 10. Check 11 is manual, in an adopter repo.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.

## Steps

1. `charter/schema/contract.toml`: the fields `checks.product`, kind `set`, and
   `checks.no_product_reason`, kind `text`, each with a note.
2. `charter/scripts/charter_check.py`: a function `product_problems(e)`, called by `all` after the check of
   the forbidden paths. With no pattern in `documents.code_paths` it returns nothing. Else: no command and
   no reason gives the failure "the contract declares code paths and names no product test: add the
   commands to `checks.product`, or the reason to `checks.no_product_reason`"; a command and a reason
   together give the failure "the contract names a product test and a reason for none: remove
   `checks.no_product_reason`". A reason of blanks only is no reason. The text at the top of the script
   names the step.
3. `charter/scripts/charter_gate.py`:
   - A command `product --contract C [--repo-only]`, built on the function that runs the commands of
     `quality`, with the field as a parameter. With no command and a reason it passes with the line "no
     product test, the contract says: <reason>". With neither it fails with the message of the checker.
   - `gate_verdict` adds one line after the line of the checks: `product test: passed: <the commands>`
     when the check `product` passed, `product test: not passed` when the facts hold the check and it did
     not pass, `product test: none, the contract says: <reason>` for a contract with a reason, and
     `product test: not reported` when the facts hold no check `product` for a contract with commands.
     The readiness changes in no new way: a check that did not pass makes the verdict not ready already.
4. `charter/templates/tests.yml` and `.github/workflows/tests.yml`: a second job `product`, with the
   checkout, the toolchain block with the same steps as the job `tests`, the fetch of Charter, and the
   step that runs `charter_gate.py product --contract charter.toml --repo-only`. No secret, and
   `permissions: contents: read` for the workflow as today. `charter_setup.py` fills both blocks from the
   one file of the flag, and `toolchain_of` reads the first block.
   `charter/templates/verdict.yml` and `.github/workflows/verdict.yml`: the collect step reads the check
   run `product` beside `tests`.
5. `charter/scripts/charter_setup.py`: a flag `--product CMD`, repeatable. With it the contract gets the
   commands; without it the contract gets `no_product_reason = "no product to start yet"`, and the manual
   steps name the product test. `charter/templates/charter.toml` carries both lines through placeholders.
6. `charter/scripts/charter_run.py`: the brief gets one step after the quality commands: run the commands
   of `checks.product` in `charter.toml` until they pass, when the contract names any.
7. `charter/templates/intent.md`: one line under the automatic checks: a work item that changes the
   behaviour of the product names the scenario of the product test that shows the change.
   `charter-practices/skills/intent-review/SKILL.md`: the same point in the checklist, inside the limit
   of lines.
8. `tests/product.py`, new: the product test of this repo, a script with no test framework. In a
   temporary folder it runs `charter/bin/charter-setup` with flags, then, through the commands of
   `charter/bin`, the contract checks with the sample organization file of `tests/samples`, the quality
   gate with `--repo-only`, the boundary gate on a list with one open and one closed path (the closed one
   must fail), and a verdict on a facts file that the script writes. It prints one line for each step and
   ends with 1 at the first step that does not behave as expected.
   `charter.toml`: `product = ["python3 tests/product.py"]` in the table `[checks]`.
9. `docs/contract.md`: the two fields; a section "The product test" after "The gates"; the job in the table
   of the workflows. `docs/product.md`, the Test row. `docs/decisions.md`: one row in section D with the
   next free identifier, dated 2026-11-20: the decision, the reason, and the sources. Official: the best
   practices of Claude Code ("can check its own work"; a run of the app catches what tests and typechecks
   miss) and "Harness engineering" of OpenAI (the app starts for each change). Community: the report of
   StrongDM, for scenarios outside the repo, which stay out of scope.
10. Both manifests: 0.3.15. `intents/product-test.md`: `Status: done`.

## Files

- `charter/schema/contract.toml`, `charter.toml`, `charter/templates/charter.toml`
- `charter/scripts/charter_check.py`, `charter/scripts/charter_gate.py`,
  `charter/scripts/charter_setup.py`, `charter/scripts/charter_run.py`
- `charter/templates/tests.yml`, `.github/workflows/tests.yml`
- `charter/templates/verdict.yml`, `.github/workflows/verdict.yml`
- `charter/templates/intent.md`, `charter-practices/skills/intent-review/SKILL.md`
- `docs/contract.md`, `docs/product.md`, `docs/decisions.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/product-test.md`, `plans/product-test.md`
- `tests/product.py`, `tests/test_product.py`, and the tests of other files that compare a written
  workflow or contract with its template, or that list the checks of the verdict

## Tests

`tests/test_product.py`, new, with the classes `Fields`, `Gate`, `Workflows`, `Verdict`, `Setup`, `Texts`,
and `OwnProduct`, and the tests that the intent names. `OwnProduct` runs `tests/product.py` once and
checks that it ends with 0 and names its steps. The unit test discovery must not run `tests/product.py`
as a test module: its name does not start with `test_`.
