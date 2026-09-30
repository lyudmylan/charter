# Scenario: the acceptance checks live in the repo as scenario files

Work item: #21. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. Each automatic check in a scenario file names a test that exists, or a command whose script exists.
   test: `tests/test_scenarios.py::Scenarios.test_each_automatic_check_names_a_test_or_a_command_that_exists`

## Manual checks

2. The scenario files of the contract, the checker, and the repository instructions match the acceptance
   checks that the leader approved in the work items #1, #2, #3. who: the leader.
