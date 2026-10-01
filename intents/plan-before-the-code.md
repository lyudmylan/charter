# Intent: plan.md, the implementation plan of a work item, accepted before the code

Work item: #35. Status: done. Approval: a person merges the change request that adds this file.

## Goal

Each work item has `plan.md`, the implementation plan, accepted before the code, as the playbook of
Anthropic describes for the Build phase.

## In scope

- The place: `intents/<part>.plan.md`, next to the intent of the work item.
- The content: the steps, the files to change, the tests to add, in the words of the author. Written in
  plan mode, accepted by the person who holds the work item, committed before the code.
- The link: the issue names its intent with one line, `Intent: intents/<part>.md`. The tracker skill
  writes it.
- The gate: the collector reads the intent path from the issue of the change request, and whether
  `intents/<part>.plan.md` exists at the head commit, into the facts file. The verdict checks that the plan
  exists. It checks the result, not the sequence of commits. With the flag on, a change request whose issue
  names no intent is not ready. A change request that changes only files under `intents/` needs no plan:
  that is the Plan phase itself.
- The contract: a flag `build.plan_before_code`, which an organization can lock. This repo and the
  template of the setup step set it. The schema changes, so both plugins become 0.3.0; an adopter takes
  the gate when its contract names that version.

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

3. The real change of the second repo carries its plan before its code. who: the leader. Not automatic: the
   second repo is outside this repo.
