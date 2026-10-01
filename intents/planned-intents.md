# Intent: intents can be planned before their tests exist

Work item: #40. Status: done. Approval: a person merges the change request that adds this file.

## Goal

An intent can be written and approved before its tests exist, and the intent test knows the difference.

## In scope

- A status line in the intent: `Status: planned` or `Status: done`.
- For a planned intent, the test verifies the four fields and that each automatic check names a test or a
  command. For a done intent, it verifies that the named tests and scripts exist too.

## Out of scope

A gate that forces the status to change when the work item closes.

## Acceptance checks

## Automatic checks

1. A planned intent with a test that does not exist yet passes; a done intent with the same reference fails.
   test: `tests/test_intents.py::PlannedIntents.test_planned_intents_need_no_existing_test`

## Manual checks

None.
