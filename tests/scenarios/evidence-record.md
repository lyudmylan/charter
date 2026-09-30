# Scenario: the evidence record on the change request

Work item: #6. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. The record has the documented form; a test builds one from a verdict and checks each field.
   test: `tests/test_charter_gate.py::Record.test_record_has_the_documented_form`
   test: `tests/test_charter_facts_github.py::Text.test_record_comment_round_trip`
2. The false-failure line is read from the text of the change request.
   test: `tests/test_charter_facts_github.py::Text.test_false_failure_lines`
   test: `tests/test_charter_gate.py::Record.test_false_failures_of_the_facts_are_in_the_record`

## Manual checks

3. After a run, the change request shows exactly one record comment, updated on each run. who: the leader.
4. `python3 scripts/charter_facts_github.py records --repo lyudmylan/charter --last 5` prints the records of
   the last merged changes. who: the leader.
