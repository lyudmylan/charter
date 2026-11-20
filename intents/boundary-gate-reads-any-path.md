# Intent: the boundary gate reads a changed path with any character in its name

Work item: #101. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The gate `charter-gate boundary` refuses a changed path under a pattern of `boundary.no_write`, whatever
characters the name of the file holds.

## In scope

- The gap: the gate reads one path on each line. git writes a path that holds a special character, for
  example a letter outside ASCII, inside double quotes and with escapes. Such a line matches no pattern,
  so the file passes, also under a closed folder. A file name can hold a line break too, and a list of
  lines cannot carry it.
- The gate reads a second form of the list: the paths with a NUL character between them, as git writes
  them with `-z`. That form has no quotes and no escapes. When the file holds a NUL character, the gate
  reads this form; else it reads lines, as today.
- In a list of lines, a line that starts with a double quote fails. The failure says that git quoted the
  path, and that the list is to be written with `-z`.
- `docs/contract.md`, section "The boundary of a run": the two forms, and which one the workflow of a run
  writes.
- Both manifests: the same version, 0.3.7 or later.

## Out of scope

How the workflow of a run collects the changed paths, with the files that git does not track yet: #92;
its issue carries the line that the list is written with `-z`. The case of the letters of a path on a
file system that ignores it. A change of the settings that `charter-check boundary` prints: they hold
paths of files that exist, read from the folder, with no quotes.

## Acceptance checks

## Automatic checks

1. In a list with a NUL character between the paths, a path under a closed folder fails and the failure
   names it, for a name with a letter outside ASCII, a name with a space, and a name with a line break.
   The same names outside the patterns pass.
   test: `tests/test_boundary.py::Gate.test_a_list_with_nul_between_the_paths_is_read`
2. In a list of lines, a line in the quotes of git fails, and the failure says to write the list with
   `-z`.
   test: `tests/test_boundary.py::Gate.test_a_path_in_the_quotes_of_git_fails`
3. A list of lines without quotes gives the results of before.
   test: `tests/test_boundary.py::Gate.test_a_path_under_no_write_fails`
   test: `tests/test_boundary.py::Gate.test_paths_outside_the_patterns_pass`
4. `docs/contract.md` names the two forms of the list.
   test: `tests/test_boundary.py::Gate.test_the_contract_document_names_the_two_forms_of_the_list`
5. Both manifests name the same version, 0.3.7 or later.
   test: `tests/test_boundary.py::Gate.test_the_version_carries_the_correction`

## Manual checks

None.
