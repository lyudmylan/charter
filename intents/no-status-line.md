# Intent: an intent holds no status line

Work item: #117. Approval: a person merges the change request that adds this file.

## Goal

No line of an intent says whether its work item is built, so no such line can be wrong after a run of an
agent.

## In scope

- The gap. The template of an intent held `Status: planned`, and the author changed it to `done` in the
  change request that built the work item. A run of an agent cannot do that: the boundary closes
  `intents/**` to a run. After a run at an adopter the line said `planned` for a work item that was
  built, and the reviewers marked the line, in both directions.
- The line leaves the template `charter/templates/intent.md`. It left each intent of this repo in a
  change request of its own, which changes intents alone. The state of the issue says whether the work
  item is built.
- The test of the intents of this repo used the line: an intent with `planned` may name a test that does
  not exist yet. The test now reads a fact that no person writes by hand: the plan of the intent exists,
  `plans/<part>.md`, or `intents/<part>.plan.md` for the one plan at the old place. An intent with no plan
  is not built yet, and its named tests may be missing.
- In this repo a plan reaches the main branch in the change request that holds its code. In a run, the
  agent writes both. In a session, the person accepts the plan in the conversation before the code, and
  one change request holds the plan, the tests, and the code. A plan that is merged before its code makes
  its intent count as built: the test then fails and names each test that does not exist.
- Some intents of this repo are older than the plans and have none. The test holds their names in a
  closed list and treats them as built. The list cannot grow: the test holds its size, and each name on it
  is an intent with no plan. A new intent with no plan is not on the list, so it is not built.
- `intents/planned-intents.md` leaves the repo: it described the status line, and this intent holds the
  check on an intent that is not built yet.

## Out of scope

The intents of an adopter that hold the line: nothing reads it there, and the adopter removes it when it
wants. A check of `charter-check` that refuses the line. The plans of this repo that name the line as a
past step: they are records of that work.

## Acceptance checks

## Automatic checks

1. An intent whose work item is not built passes with a test that does not exist yet. The same intent
   fails when its work item is built.
   test: `tests/test_intents.py::PlannedIntents.test_an_intent_that_is_not_built_needs_no_existing_test`
2. An intent with a plan is built, at the place of today or at the old place, and then a named test that
   does not exist is a fault. The same intent with no plan is not built and has no fault. The older
   intents are built; their list has a fixed size, and each name on it is an intent with no plan.
   test: `tests/test_intents.py::PlannedIntents.test_the_plan_says_that_a_work_item_is_built`
3. No intent of this repo holds a status line, and the template holds none.
   test: `tests/test_intents.py::PlannedIntents.test_no_intent_holds_a_status_line`
4. In the product test, the setup step writes the template of an intent with no status line.
   command: `python3 tests/product.py`, the step "template of an intent"

## Manual checks

None.
