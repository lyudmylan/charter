# Intent: plan.md, the implementation plan of a work item, accepted before the code

Work item: #35. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

Each work item has `plan.md`, the implementation plan, accepted before the code, as the playbook of
Anthropic describes for the Build phase.

## In scope

- The place: `intents/<part>.plan.md`, next to the intent of the work item.
- The content: the steps, the files to change, the tests to add, in the words of the author. Written in
  plan mode, accepted by the person who holds the work item, committed before the code.
- The gate: the collector finds the intent of a change request through its issue, and the verdict checks
  that the plan of that intent exists in the repo at the head of the change request. It checks the
  result, not the sequence of commits.
- The contract: a flag `build.plan_before_code`, which an organization can lock.

## Out of scope

A check of the content of the plan by a model.

## Acceptance checks

## Automatic checks

1. The verdict is "not ready" for a change request whose intent has no plan, and "ready" with it, when the
   flag is on; with the flag off, the plan is not checked.
   test: `tests/test_charter_gate.py::Verdict.test_plan_before_code`
2. The collector reads the intent path from the issue of the change request.
   test: `tests/test_charter_facts_github.py::Text.test_intent_path_from_issue`

## Manual checks

3. The real change of the second repo carries its plan before its code. who: the leader.
