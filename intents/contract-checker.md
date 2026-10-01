# Intent: the contract checker

Work item: #2. Approved by a person on 2026-09-30, in the work item. From now on, an intent
is approved through a change request before the work starts.

An automatic check names the test that implements it. A manual check names who does it.

## Goal

A script reports if a contract is valid, and if the repo rules obey the locked rules of the organization source that the contract references.

## In scope

- One Python file, standard library only, no installation.
- Mode 1: validate one file, organization or repo (fields, types, owners, locked flags).
- Mode 2: check a repo contract against its organization source. The script resolves the reference: from a cache outside the repo, or from a path that CI gives after a fetch. A repo can add a rule or make a rule stricter. It cannot remove or weaken a locked rule.
- "Stricter" is defined in the schema, for each field: for some numbers smaller is stricter (a limit), for others larger is stricter (a number of approvals); for a list, a superset is stricter; for a role, the schema gives the order. The script reads the direction from the schema. No rule is a special case in the code.
- Exit codes: 0 pass; 1 fail; 2 the check could not run. With exit code 2 the message names the cause: no file, not TOML, source not found, access denied, version not found.
- Clear messages that name the rule and the reason.
- The version of the source that was used is part of the output, for the evidence record.
- Tests with sample files, not the real rules of this organization.

## Out of scope

- Fetching a source over the network inside the script. The fetch is the job of the cache or of CI.
- Rules of the owners "team" and "person".

## Acceptance checks

## Automatic checks

1. A valid file passes. test: `tests/test_charter_check.py::Validate.test_valid_files_pass`
2. A file with a missing field, a wrong type, an unknown field, or a lock without a value fails, and
   the message names the field. test: `tests/test_charter_check.py::Validate.test_missing_field_names_the_field`
3. A repo that adds an unlocked rule passes. test: `tests/test_charter_check.py::Check.test_repo_adds_an_unlocked_rule`
4. A repo that makes a locked rule stricter passes, for each direction that the schema defines.
   test: `tests/test_charter_check.py::Check.test_stricter_in_each_direction_passes`
5. A repo that removes or weakens a locked rule fails, and the message names the rule.
   test: `tests/test_charter_check.py::Check.test_weaker_in_each_direction_fails_and_names_the_rule`
6. Each case where the check cannot run gives exit code 2 and a message that names the cause: no file,
   not TOML, source not found, access denied, version not found. test: `tests/test_charter_check.py::CannotRun.test_no_file`
7. The output names the version of the source that was used.
   test: `tests/test_charter_check.py::CannotRun.test_cache_resolves_and_names_the_version`
8. The tests run with one command and pass. command: `python3 -m unittest discover -s tests`

## Manual checks

None.
