# Intent: the repository instructions

Work item: #3. Approved by a person on 2026-09-30, in the work item.

## Goal

An agent that works in this repo knows the rules of the repo from the first turn.

## In scope

- One instruction file at the root: `AGENTS.md`, so that other runtimes read it too. This repo has no `CLAUDE.md`, so Claude Code reads `AGENTS.md`.
- Written by hand from the contract. Content: how a change moves (a branch, a ticket for each change to a source file, a change request, a person merges); the text rules for commits and issues; the two review lines (broken contracts between parts of the system; documents that the change made stale); the quality checks to run; a pointer to the contract and to `docs/product.md`.
- Each rule line ends with the identifier of its rule in the contract, for example `[text.private_material_patterns]`.
- Short: under 40 lines.

## Out of scope

- Generation of the file from the contract. That is on the roadmap.

## Acceptance checks

## Automatic checks

1. Each identifier in the file exists in the contract or in the organization source.
   test: `tests/test_charter_check.py::Instructions.test_known_identifiers_pass`
2. The file contains no private material and no session links.
   test: `tests/test_charter_check.py::Instructions.test_private_material_and_project_names_fail`
3. The file contains no names of other projects. The list of names lives in the private organization
   source, and the checker reads it from there.
   test: `tests/test_charter_check.py::Instructions.test_private_material_and_project_names_fail`
4. The real file passes. command: `python3 charter/scripts/charter_check.py instructions AGENTS.md --contract charter.toml`

## Manual checks

5. Claude Code loads the file at the start of a session. who: the leader, with `/context` in a session.
