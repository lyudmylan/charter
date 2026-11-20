# Plan: the evidence record holds the outcome and the cost of an agent run (#93)

Intent: `intents/record-of-a-run.md`, checks 1 to 7. Check 8 is manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan builds on #92: the result of the agent and the publishing step.

## Steps

1. `charter/scripts/charter_run.py`: a command `record --agent FILE --commit COMMIT`. It prints the two
   lines of the block: the marker, and the line `Run:` with the commit, the turns as a whole number, the
   duration in whole seconds, and the cost with two decimals; `none` for a value that the result does
   not hold. The marker and the names of the four values are constants that the facts collector reads
   from this script, or that both scripts read from one place.
2. `charter/templates/run.yml` and `.github/workflows/run.yml`, the step "Publish the change request":
   after the push, the step reads the commit that it pushed with a `git` call that runs no hook, calls
   the command from the copy of the scripts, and adds the block at the end of the text file of the
   change request, before `gh pr create`.
3. `charter/scripts/charter_facts_github.py`: a function reads the block from the text of the change
   request: the marker line, then the line `Run:` right after it, with the four values in any order. A
   value `none` gives no value. A block with a missing name, a value that is no number, or a commit that
   is no identifier gives no run. `build_facts` writes the fact `run` when the block is there.
4. `charter/scripts/charter_gate.py`:
   - The fact `run` is optional and validated: a table with the commit as text and three numbers or no
     value.
   - A function `run_outcome(facts, e, ready)`: no fact gives no run. Else `manual` when `head_commit`
     is not the commit of the run or is missing; else `flawed` when the verdict is not ready, or the
     newest report of the intent review or of the code review is at the threshold or above or has no
     severity line; else `success`.
   - `gate_verdict` adds the line after the line of the merge. The readiness does not change.
   - The evidence record holds `run`: the outcome and the three numbers, or no value.
5. `docs/contract.md`: a section "The record of a run" after "The run", and the record table.
   `docs/product.md`, the Maintain row.
6. Both manifests: 0.3.14. `intents/record-of-a-run.md`: `Status: done`.

## Files

- `charter/scripts/charter_run.py`, `charter/scripts/charter_facts_github.py`,
  `charter/scripts/charter_gate.py`
- `charter/templates/run.yml`, `.github/workflows/run.yml`
- `docs/contract.md`, `docs/product.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/record-of-a-run.md`, `plans/record-of-a-run.md`
- `tests/test_run.py`, `tests/test_charter_facts_github.py`, `tests/test_charter_gate.py`

## Tests

A class `RunRecord` in `tests/test_run.py` (two tests), `tests/test_charter_facts_github.py` (two), and
`tests/test_charter_gate.py` (seven), with the names that the intent gives. The publishing step runs
with the fakes of `gh` and `git` that `tests/test_run.py` has.
