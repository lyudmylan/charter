# Intent: the evidence record on the change request

Work item: #6. Approved by a person on 2026-09-30, in the work item.

## Goal

Each change request carries a structured record of what the gates found.

## In scope

- The record is the JSON form of the verdict (`charter_gate.py verdict --json`): the verdict, the source and its version, the tier, who merges, each gate with its reasons, and the checks. Two fields join it: the version of the scripts that made the record (the commit of main), and the time.
- One comment on the change request holds the record, updated on each run, with a marker line so that the script finds its own comment. The check "verdict" keeps the short text.
- A person records a false failure of a gate with one line in the text of the change request: `False failure: <gate>: <reason>`. The collector copies it into the record.
- The field for dropped findings exists and stays empty until the agent reviewer comes (roadmap).
- `charter_facts_github.py records --repo owner/name --last N` prints the records of the last merged change requests, for a sample review.
- The form is documented in `docs/contract.md`. It is host-neutral; the comment is the GitHub adapter.

## Out of scope

- The cost of each change (roadmap). Export to a store.

## Acceptance checks

## Automatic checks

1. The record has the documented form; a test builds one from a verdict and checks each field.
   test: `tests/test_charter_gate.py::Record.test_record_has_the_documented_form`
   test: `tests/test_charter_facts_github.py::Text.test_record_comment_round_trip`
   test: `tests/test_charter_facts_github.py::Text.test_three_backticks_inside_a_reason_survive_the_round_trip`
   test: `tests/test_charter_facts_github.py::Text.test_only_a_comment_by_the_workflow_account_is_the_record`
2. The false-failure line is read from the text of the change request.
   test: `tests/test_charter_facts_github.py::Text.test_false_failure_lines`
   test: `tests/test_charter_gate.py::Record.test_false_failures_of_the_facts_are_in_the_record`

## Manual checks

3. After a run, the change request shows exactly one record comment, updated on each run. who: the leader.
4. `python3 charter/scripts/charter_facts_github.py records --repo lyudmylan/charter --last 5` prints the records of
   the last merged changes. who: the leader.
