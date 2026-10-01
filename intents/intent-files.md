# Intent: the acceptance checks live in the repo, in the intent of each work item

Work item: #21. Approved by a person on 2026-09-30, in the work item.

## Goal

The acceptance checks of a work item live in the repo as an intent, and the tests cite it.

## In scope

- The directory `intents/` with one Markdown file for each part of epic #8: the contract, the checker, the repository instructions. Each file lists the acceptance checks of its issue, marked automatic or manual, and names the test of each automatic check.
- Each test that implements an automatic check cites the intent and the check number in its docstring.
- The rule for the future: an intent is written at the Plan phase and approved by a person through a change request. Approved intents are protected files, in the high risk tier.
- `charter.toml`: `intents/**` joins the paths of the high tier.

## Out of scope

- A script that checks that each automatic check has a test. That comes with the gates.

## Acceptance checks

## Automatic checks

1. Each automatic check in an intent names a test that exists, or a command whose script exists.
   test: `tests/test_intents.py::Intents.test_each_automatic_check_names_a_test_or_a_command_that_exists`

## Manual checks

2. The intents of the contract, the checker, and the repository instructions match the acceptance
   checks that the leader approved in the work items #1, #2, #3. who: the leader.
