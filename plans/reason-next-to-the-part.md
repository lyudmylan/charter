# Plan: the architecture map holds each choice with its reason, and no file holds one decision (#84)

Intent: `intents/reason-next-to-the-part.md`, checks 1 to 11. The leader merged the intent on 2026-11-18.
Accepted by the leader in the conversation on 2026-11-18, before the code.

## Steps

1. `charter/schema/contract.toml`: the field `documents.absent`, kind `set`, with the note "Path
   patterns that the repo must not hold. The contract checks fail when a file is under one of them."
   The schema version stays 1: the field is an addition, as `build.plan_before_code` was.
2. `charter/scripts/charter_check.py`:
   - The path matcher (`glob_to_regex`, `matches`) moves here from `charter_gate.py`, because `all`
     needs it and the gate already imports the checker. `charter_gate.py` calls the checker's functions
     and keeps no copy.
   - A function `absent_hits(e, root)`: for each pattern of `documents.absent` it walks the folder of
     the contract from the fixed start of the pattern (for `docs/adr/**` that is `docs/adr`), never
     into `.git`, and returns one failure for each file whose path matches. It reads the files of the
     folder, not the index of git, so a file that is not committed also fails, and a repo without git
     is checked too. A folder with no file passes.
   - The message, one place: "`{path}`: the contract forbids this path, a pattern of `{field}`. Move
     its content into a necessary document, at the part it concerns, and remove the file."
   - `cmd_all` adds these failures after the text check. An absent or empty field adds none.
   - The text at the top of the script and the help of `all` name the new step.
3. `charter/templates/charter.toml`, the table `[documents]`: the line
   `absent = ["docs/adr/**", "doc/adr/**", "doc/arch/adr-*.md", "docs/decisions/**"]`, with a comment:
   no file for one decision; the choice and its reason go into the architecture map. The value is fixed
   text in the template; the setup step asks nothing new, so `charter_setup.py` does not change.
4. `charter.toml` of this repo: the same line. This is a change of a contract, and the merge by the
   leader approves it.
5. `charter/templates/architecture.md`: the first sentence becomes "The parts of this system. Each
   change request that adds a part adds a row, with the reason of each choice in the row." The table of
   parts has the columns Part, "What it does, and why it is built this way", Where, Since. The sections
   "What runs on a change request" and "Decisions" leave. The template then no longer names Charter.
6. `charter/templates/AGENTS.md` and `AGENTS.md`, under "Before a push", one rule line: "A choice of
   the architecture and its reason go into `docs/architecture.md`, in the row of the part. No separate
   file holds one decision; a choice that must always hold becomes a check. [documents.absent]"
7. `docs/decisions.md`, section G, the row G6, accepted, 2026-11-18. Decision: "A choice of the
   architecture and its reason live in the architecture map, next to the part, in one or two sentences.
   A choice that must always hold becomes a check. The history is in git. No separate file holds one
   decision; this record of the process decisions is one file and is not affected." Reason: "With one
   file for each decision a fact has two homes. A rule that only a document holds does not hold: the
   rule of 2026-10-01 lived in an epic, and an agent wrote eight decision files while both contract
   checks passed. Official: the design spec holds the decisions of a work item (Anthropic, the AI-native
   SDLC playbook); 'When documentation falls short, we promote the rule into code' (OpenAI, Harness
   engineering). Community: one file for each decision (Nygard, 2011); neither official source asks
   for it."
8. `docs/contract.md`: the row `documents.absent` in the table of fields; the paragraph on `all` names
   the new step; one sentence says that the field needs the version 0.3.5 of the core.
9. `docs/product.md`, the Design row: "The design spec of the work item. The architecture map, kept
   current, with each choice and its reason at the part."
10. `tests/test_charter_check.py`, a class `AbsentPaths`, seven tests:
    `test_the_field_is_in_the_schema_and_in_the_contract_document`,
    `test_a_file_under_an_absent_path_fails`,
    `test_the_failure_names_the_file_the_field_and_the_remedy`,
    `test_a_file_that_is_not_committed_fails` (a git repo with one commit, and a new file that git does
    not track),
    `test_no_file_under_a_pattern_passes` (also: a file `docs/decisions.md` passes, and a file in a
    folder next to a pattern passes), `test_an_absent_or_empty_field_checks_nothing`,
    `test_the_decision_is_recorded`.
    `tests/test_setup.py`, a class `DecisionFiles`, six tests:
    `test_the_new_contract_carries_the_default_patterns`,
    `test_a_decision_file_fails_the_check_of_a_new_repo` (one file under each of the four patterns, one
    at a time), `test_the_architecture_template_holds_the_choice_at_the_part`,
    `test_the_instructions_carry_the_rule`, `test_both_manifests_name_the_version`,
    `test_the_design_row_of_the_product_document_names_the_choice`.
    Each test names the intent and the number of its check. The tests of the gate still pass after the
    move of the matcher.
11. Both manifests: 0.3.5. `intents/reason-next-to-the-part.md`: the status becomes done.
12. One change request, `Closes #84`, with this plan and steps 1 to 11. The product document changes, so
    no `No document change` line. The tier is high: a deep review, and the leader merges.

## After the merge

- The leader pushes the tags `charter--v0.3.5` and `charter-practices--v0.3.5`.
- An adopter gets the check by one change of its contract that a person approves: the version 0.3.5 and
  the line of step 3. A contract at 0.3.4 that carries the field fails with "unknown field", so the two
  go together. The manual check 12 of the intent is this first use.

## Files

`charter/schema/contract.toml`, `charter/scripts/charter_check.py`, `charter/scripts/charter_gate.py`,
`charter/templates/charter.toml`, `charter/templates/architecture.md`, `charter/templates/AGENTS.md`,
`AGENTS.md`, `charter.toml`, `docs/decisions.md`, `docs/contract.md`, `docs/product.md`,
`tests/test_charter_check.py`, `tests/test_setup.py`, the two manifests,
`intents/reason-next-to-the-part.md`, and this file.

## Tests

Thirteen new tests, step 10. The existing test `Patterns.test_star_stays_in_one_segment_and_double_star_crosses`
of the gate covers the matcher after its move, and it now calls the matcher of the checker (check 11).

## What this plan does not do

- It does not put the default into the organization source. A repo that exists keeps its contract until
  a person changes it.
- It does not check the content of an architecture map: a row with no reason passes.
- It does not change `charter_setup.py`, and it does not touch the architecture map of an adopter that
  already exists; the setup step writes the template only when the file is missing.
