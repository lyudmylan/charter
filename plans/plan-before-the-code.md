# Plan: an intent that the change request removes or renames needs no plan (#71)

Intent: `intents/plan-before-the-code.md`, check 4. Accepted by the leader in the conversation on 2026-11-09,
before the code.

## Correction of the issue

The gate does not read the intents from the diff. The collecting script reads the `Intent:` line of each
linked issue, and the verdict asks for the plan of each intent so named. In the adopter's case a linked
issue named the old path. The fix below keeps that mechanism and adds one fact: whether the change
request removes the intent. A comment on the issue records the correction.

## Steps

1. `charter/scripts/charter_facts_github.py`: a pure function `removed_paths(files)`: the files with the
   status `removed`, and the previous name of the files with the status `renamed`. `build_facts` takes
   that set and writes, for each intent, `removed: true` when the change request removes the intent or
   renames it away. `collect` passes the set. The plan is still looked up: a fact stays a fact.
2. `charter/scripts/charter_gate.py`: the shape of an intent accepts the optional key `removed` (a
   bool). The gate `plan` asks no plan for a removed intent and prints the reason
   `intents/<old>.md is removed by the change request, no plan needed`. The other intents are checked
   as before. An intent that a linked issue names with a path that the change request does not touch
   still needs its plan, so a wrong path in an issue still fails.
3. `tests/test_charter_facts_github.py`, class `Facts`: `test_a_renamed_or_removed_intent_is_marked`,
   with files that carry `status` and `previous_filename`. `tests/test_charter_gate.py`, class
   `Verdict`: `test_a_removed_intent_needs_no_plan`: the facts of a rename, the old intent removed and
   the new one with its plan, give "ready", and the reasons name both files.
4. `intents/plan-before-the-code.md`: one bullet in the scope (the finding of 2026-11-08 and the fact
   `removed`); check 4 names the two tests; the manual check becomes 5.
5. `docs/contract.md`: the sample of the facts file, the paragraph on the field `intents`, and the row
   of the record.
6. One change request, `Closes #71`, with the line `No document change: the product does not change;
   one fact of the collector and one reason of the plan gate`. No version change: see the plan of #70.

## Files

`charter/scripts/charter_facts_github.py`, `charter/scripts/charter_gate.py`,
`tests/test_charter_facts_github.py`, `tests/test_charter_gate.py`, `intents/plan-before-the-code.md`,
`docs/contract.md`, and this file.

## Tests

Two new tests, step 3. The existing `Verdict.test_plan_before_code` keeps its cases.
