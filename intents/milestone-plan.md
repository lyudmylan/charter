# Intent: the plan of a milestone is a file, and the merge of the leader approves its work items

Work item: #141. Approval: a person merges the change request that adds this file.

## Goal

The plan of a milestone is one file in the repo, each work item in it has one line that says what "done"
means, a check reads the form of the file, and the file is in the high tier, so that the merge of the
leader approves its work items.

## In scope

- The file `milestones/<name>.md`, one for each milestone. Line 1 is `# Milestone: <name>`. A work item is
  a heading `### #<issue> <title>`. Under it stand one line `Done:`, which can continue on the next lines,
  and the two lines that a work item can have: one line `Tier: high`, and a line `Needs:` for each thing
  that must be true before the work item starts. A need has one of three forms: `#<issue>` of another work
  item of this plan, `Charter <version>` with three numbers, or `the word of the leader`. A text outside a
  work item is free: the goal of the milestone stands there.
- The check, in `charter/scripts/charter_check.py`. The command `milestone <file>` checks one plan and
  prints its name and its work items, each with its lines `Tier:` and `Needs:`. The command `all` checks
  each plan of the folder `milestones/` and names the file of a fault; with no such folder it passes as
  before. A fault is: a first line in another form; a plan with no work item; a heading of a work item in
  another form; a work item with no text in a line `Done:`, with two lines `Done:`, or with two lines
  `Tier:`; an issue that the plan holds two times; a value of `Tier:` that is not `high`; a need in none of
  the three forms, or one that names the work item itself or an issue that is no work item of the plan; a
  line under a work item that starts with another word and a colon, or that continues no line `Done:`.
  A heading of another level ends the work item; a line that starts with `#` and is no heading does not.
- The tier. The contract of this repo holds `milestones/**` in `tiers.high.paths` and in
  `boundary.no_write`, and so does each contract that the setup step writes: the leader merges each change
  of a plan, and a run of an agent without a person does not change it.
- The skill `tracker` writes a plan in this form and names the command that checks it.
- The documents say where the approval of the leader stands: `docs/contract.md`, a section "The plan of a
  milestone" with the form, the check, and the two limits of this version; `docs/product.md`, the row of
  the Plan phase; `AGENTS.md` and its template; `docs/decisions.md`, the decision C13.
- Both manifests: 0.3.23.

## Out of scope

- The check of an intent against the line `Done:`: #142.
- The start of the work, and whether a need holds: #144. No code reads the lines `Needs:` yet.
- The tier of a change from the line `Tier: high`: #148. The tier of a change still comes from its file
  paths.
- The state of a release from the plan: #149.
- Whether an issue exists in the tracker, and whether a Charter version exists. The check reads the file
  only and needs no network; a plan can name a version that a later work item makes.
- The contract of a repo that has it from an earlier version. The update command writes no contract; a
  person adds the pattern to the two fields. `docs/contract.md` says so.
- A plan file for the milestone that is in work in this repo. The leader approved that milestone on the
  tracker; the first plan in this form comes with the next milestone.
- The approval of an intent. Its change request still goes to the leader, because `intents/**` stays in
  the high tier.

This intent narrows the issue #141 in two points, and the leader confirms the narrowing with the merge.
The issue says that each line `Needs:` names a thing that exists: the check reads the form of a need and
the work items of the same plan, not the tracker and not the versions of Charter. The issue says that
`Tier: high` sends the change of the work item to the leader: this work item gives the line and its check,
and #148 makes the verdict read it.

## Acceptance checks

## Automatic checks

1. A plan in the form passes, and the command `milestone` prints the name of the milestone and each work
   item with its lines `Tier:` and `Needs:`. A file that is not there ends the command with the code 2.
   test: `tests/test_charter_check.py::MilestonePlan.test_a_plan_in_the_form_passes_and_the_command_prints_its_work_items`
2. Each fault of the form that the scope lists fails with a reason that names it, except the faults of a
   need, which check 4 holds. A line that starts with `#` and is no heading does not end the work item: the
   lines after it are read.
   test: `tests/test_charter_check.py::MilestonePlan.test_each_fault_of_the_form_fails_with_its_reason`
3. A line `Done:` continues on the next lines up to a blank line, and a text outside a work item is free,
   before the first work item and after a heading of another level.
   test: `tests/test_charter_check.py::MilestonePlan.test_a_line_done_continues_and_a_text_outside_a_work_item_is_free`
4. A need in one of the three forms passes. A need fails when it names an issue that is no work item of
   the plan, the work item itself, a version in another form, or another text.
   test: `tests/test_charter_check.py::MilestonePlan.test_a_line_needs_names_a_thing_of_one_of_three_forms`
5. The command `all` passes with no folder `milestones/` and with a plan in the form, and it fails for a
   plan with a fault and names its file.
   test: `tests/test_charter_check.py::MilestonePlan.test_all_checks_each_plan_of_the_folder`
6. A plan is in the high tier and closed to a run: the contract of this repo and each contract of the
   setup step hold `milestones/**` in `tiers.high.paths` and in `boundary.no_write`.
   test: `tests/test_charter_check.py::MilestonePlan.test_the_plan_is_in_the_high_tier_and_closed_to_a_run`
   test: `tests/test_boundary.py::Defaults.test_the_new_contract_carries_the_default_patterns`
7. The skill `tracker` holds the file, each line of the form, the three forms of a need, the command of
   the check, and the rule that the merge of the leader approves the work items; it stays under the limit
   of lines.
   test: `tests/test_skills.py::TrackerSkill.test_the_skill_holds_the_form_of_a_milestone_plan`
   test: `tests/test_skills.py::TrackerSkill.test_size_and_description`
8. `docs/contract.md` holds the section with each line of the form, the command, and the two limits;
   `AGENTS.md` and its template hold the rule of the merge; `docs/product.md` names the approval in the
   row of the Plan phase; `docs/decisions.md` holds the decision C13.
   test: `tests/test_charter_check.py::MilestonePlan.test_the_documents_hold_the_form_and_the_approval`
9. The product test shows the change in a new repo, the scenario "plan of a milestone": the command prints
   the work items of a plan, the contract checks pass with it, the boundary gate refuses a change of the
   plan in a run, and a need that names no work item fails the contract checks.
   command: `python3 tests/product.py`
10. Both manifests name the version 0.3.23 or a later one.
    test: `tests/test_charter_check.py::MilestonePlan.test_both_manifests_name_the_version`

## Manual checks

None. Each result of this work item is a result of code or a text of a file.
