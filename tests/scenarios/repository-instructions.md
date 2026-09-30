# Scenario: the repository instructions

Work item: #3. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. Each identifier in the file exists in the contract or in the organization source.
   test: `tests/test_charter_check.py::Instructions.test_known_identifiers_pass`
2. The file contains no private material and no session links.
   test: `tests/test_charter_check.py::Instructions.test_private_material_and_project_names_fail`
3. The file contains no names of other projects. The list of names lives in the private organization
   source, and the checker reads it from there.
   test: `tests/test_charter_check.py::Instructions.test_private_material_and_project_names_fail`
4. The real file passes. command: `python3 scripts/charter_check.py instructions AGENTS.md --contract charter.toml`

## Manual checks

5. Claude Code loads the file at the start of a session. who: the leader, with `/context` in a session.
