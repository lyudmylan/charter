# Plan: the boundary gate reads a changed path with any character in its name (#101)

Intent: `intents/boundary-gate-reads-any-path.md`, checks 1 to 6.
The leader gave the acceptance of the plans of this milestone in advance, in the conversation on
2026-11-20: the intent, the plan, and the code of a work item reach her together, and her merge
approves the three.

## Steps

1. `charter/scripts/charter_gate.py`:
   - A function `changed_paths(text)`: when the text holds a NUL character, the paths are the parts
     between the NUL characters, each as it is; else they are the lines, without the blanks around a
     line, as before. It also says which form it read.
   - `gate_boundary` takes that answer. In a list of lines, a line that starts with a double quote
     fails with the message "`{line}`: git wrote this path in quotes, and the gate cannot read it. Write
     the list with a NUL character between the paths: the option `-z` of git." In the NUL form a name
     that starts with a double quote is a name.
   - The help text and the text at the top of the script name the two forms.
2. `charter/scripts/charter_check.py`, the function `matches`: the pattern `**` also crosses a line
   break in a name. Without this, a file with a line break in its name under a closed folder matches no
   pattern. The change holds for each use of the matcher: tiers, code paths, forbidden paths.
3. `docs/contract.md`, section "The boundary of a run": the two forms of the list, and that the workflow
   of a run writes the form with NUL.
4. Both manifests: 0.3.7.
5. `intents/boundary-gate-reads-any-path.md`: `Status: done`.
6. `tests/test_boundary.py`, class `Gate`, five tests:
   `test_a_list_with_nul_between_the_paths_is_read` (five names, each under a closed folder and outside:
   a letter outside ASCII, a space, a line break, a double quote at the start, a backslash),
   `test_a_path_in_the_quotes_of_git_fails`,
   `test_the_contract_document_names_the_two_forms_of_the_list`,
   `test_the_version_carries_the_correction`,
   `test_double_star_crosses_a_line_break_in_a_name`.

## Files

- `charter/scripts/charter_gate.py`
- `charter/scripts/charter_check.py`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `intents/boundary-gate-reads-any-path.md`
- `intents/boundary-gate-reads-any-path.plan.md`
- `tests/test_boundary.py`
