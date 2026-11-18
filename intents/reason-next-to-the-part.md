# Intent: the architecture map holds each choice with its reason, and no file holds one decision

Work item: #84. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A choice of the architecture and its reason live in the architecture map, next to the part that the
choice concerns, and a repo that keeps a file for each decision fails the contract checks.

## In scope

- The decision, in `docs/decisions.md`, section G, accepted on 2026-11-18: the architecture map holds
  each choice with its reason, next to the part; a choice that must always hold becomes a check; no
  separate file holds one decision. The record of the process decisions, `docs/decisions.md`, is one
  file and is not affected. The text, its reason, and its sources are in section G.
- Why a check, and not the decision alone: the leader decided "no separate decision records" on
  2026-10-01. The sentence lived in an epic of the tracker and in no file that an agent or a check
  reads. On 2026-11-16 an agent wrote eight decision files in an adopter repo, and both contract checks
  passed.
- A field of the contract, `documents.absent`: a set of path patterns, of the same form as the paths of
  a risk tier. `charter-check all` fails when the repo holds a file under one of them. The failure
  names the file and the field, and says where the content goes: into a necessary document, at the part
  it concerns. An absent or empty field checks nothing. The schema, `docs/contract.md`, and the checker
  carry the field. The path matcher moves from `charter_gate.py` to `charter_check.py`, and the gate calls
  it there; the tests of the gate still pass.
- The default, in `charter/templates/charter.toml`, which the setup step writes: the folders of the
  common conventions for decision files, `docs/adr/**`, `doc/adr/**`, `doc/arch/adr-*.md`, and
  `docs/decisions/**`. A repo or its organization can change the set, as for each field.
- `charter/templates/architecture.md`, in the form that the leader approved for the architecture map of
  an adopter repo on 2026-11-18. The section "Decisions" leaves. The column "What it does" becomes "What
  it does, and why it is built this way", so that the choice and its reason are in the row of the part.
  The section "What runs on a change request" leaves, and the first sentence of the template no longer
  says "and what runs when": that section is the process, not the architecture. The repository
  instructions hold the process, and `docs/contract.md` holds the table of the workflows.
- The rule line, with the identifier `documents.absent` and the wording of section G ("no separate file
  holds one decision"), in `charter/templates/AGENTS.md` and in the `AGENTS.md` of this repo. The
  contract of this repo, `charter.toml`, carries the field with the default.
- `docs/product.md`, the Design row of the lifecycle map: the architecture map holds each choice with
  its reason.
- Both manifests: 0.3.5, so that an adopter can name the version that carries the check.

## Out of scope

The decision record of Charter itself, `docs/decisions.md`: it holds decisions on the process, which
belong to no part, and it is one file, not a file for each decision. The method for a choice of a
technology or a tool (the purpose, the requirements, the options, then the choice): an open point of
the epic #17. A check that reads the content of the architecture map. The architecture map of Charter
itself: #60. The move of the default into the organization source: a later change of that source, with
its own version.

## Acceptance checks

## Automatic checks

1. The schema has the field `documents.absent` as a set, and `docs/contract.md` lists it.
   test: `tests/test_charter_check.py::AbsentPaths.test_the_field_is_in_the_schema_and_in_the_contract_document`
2. `charter-check all` fails when the repo holds a file under a pattern of `documents.absent`; the
   failure names the file and the field, and says where the content goes. The file need not be
   committed: the check reads the folder.
   test: `tests/test_charter_check.py::AbsentPaths.test_a_file_under_an_absent_path_fails`
   test: `tests/test_charter_check.py::AbsentPaths.test_the_failure_names_the_file_the_field_and_the_remedy`
   test: `tests/test_charter_check.py::AbsentPaths.test_a_file_that_is_not_committed_fails`
3. `charter-check all` passes when no file is under a pattern, and when the field is absent or empty.
   test: `tests/test_charter_check.py::AbsentPaths.test_no_file_under_a_pattern_passes`
   test: `tests/test_charter_check.py::AbsentPaths.test_an_absent_or_empty_field_checks_nothing`
4. The contract that the setup step writes carries the default patterns, and a repo that the setup step
   made fails the check after a file is added under each of the four default patterns, one at a time:
   `docs/adr/adr-001-store.md`, `doc/adr/0001-store.md`, `doc/arch/adr-001.md`, and
   `docs/decisions/0001-store.md`.
   test: `tests/test_setup.py::DecisionFiles.test_the_new_contract_carries_the_default_patterns`
   test: `tests/test_setup.py::DecisionFiles.test_a_decision_file_fails_the_check_of_a_new_repo`
5. The template of the architecture map has no section "Decisions" and no section "What runs on a
   change request", and its table of parts has the column "What it does, and why it is built this way".
   test: `tests/test_setup.py::DecisionFiles.test_the_architecture_template_holds_the_choice_at_the_part`
6. The instruction template and the `AGENTS.md` of this repo carry the rule line with the identifier
   `documents.absent`.
   test: `tests/test_setup.py::DecisionFiles.test_the_instructions_carry_the_rule`
7. The decision record holds the rule in section G, accepted, with its reason.
   test: `tests/test_charter_check.py::AbsentPaths.test_the_decision_is_recorded`
8. The contract of this repo carries the field, and its contract checks pass.
   command: `python3 charter/scripts/charter_check.py all charter.toml`
9. Both manifests name the version 0.3.5.
   test: `tests/test_setup.py::DecisionFiles.test_both_manifests_name_the_version`
10. The Design row of the lifecycle map in `docs/product.md` says that the architecture map holds each
    choice with its reason.
    test: `tests/test_setup.py::DecisionFiles.test_the_design_row_of_the_product_document_names_the_choice`
11. The gate matches paths as before the move of the matcher.
    test: `tests/test_charter_gate.py::Patterns.test_star_stays_in_one_segment_and_double_star_crosses`

## Manual checks

12. The first use, in an adopter repo: with the version 0.3.5 and the default patterns, the contract
    checks fail while the folder of decision files exists, and pass after its content is in the
    architecture map. who: the leader. Not automatic: the adopter repo is outside this repo.
