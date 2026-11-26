# Plan: the plan of a milestone is a file, and the merge of the leader approves its work items (#141)

Intent: `intents/milestone-plan.md`, checks 1 to 10.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. `charter/scripts/charter_check.py`: the reader `read_milestone`, which gives the name, the work items,
   and each fault of the form; the command `milestone <file>`; in `all`, the check of each file of
   `milestones/`. The folder has a fixed name, as `intents/` and `plans/` have: no new field of the
   contract, so the schema does not change.
2. `charter.toml`, `charter/templates/charter.toml`, and `charter/scripts/charter_setup.py`: the pattern
   `milestones/**` in the paths of the high tier and in `boundary.no_write`.
3. `charter-practices/skills/tracker/SKILL.md`: the form of the plan, the command, and the rule of the
   merge. The file stays under the limit of lines.
4. `docs/contract.md`, `docs/product.md`, `docs/decisions.md`, `AGENTS.md`, `charter/templates/AGENTS.md`.
5. `tests/product.py`: the scenario "plan of a milestone".
6. Both manifests: 0.3.23. The version 0.3.22 is the one of the change for #153, which is open.

## Files

- `charter/scripts/charter_check.py`, `charter/scripts/charter_setup.py`
- `charter.toml`, `charter/templates/charter.toml`
- `charter-practices/skills/tracker/SKILL.md`
- `docs/contract.md`, `docs/product.md`, `docs/decisions.md`, `AGENTS.md`, `charter/templates/AGENTS.md`
- `tests/test_charter_check.py`, `tests/test_skills.py`, `tests/test_boundary.py`, `tests/product.py`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/milestone-plan.md`, `plans/milestone-plan.md`

## Tests

- `tests/test_charter_check.py`: the class `MilestonePlan`, eight tests.
- `tests/test_skills.py`: `TrackerSkill.test_the_skill_holds_the_form_of_a_milestone_plan`.
- `tests/test_boundary.py`: the default list of `boundary.no_write` gets the new pattern.
- `tests/product.py`: four steps of the scenario "plan of a milestone".

## Choices of the author that the leader confirms with the merge

- The name of the folder and of the file: `milestones/<name>.md`.
- A work item is a heading `### #<issue> <title>`, and its lines start with `Done:`, `Tier:`, `Needs:`.
- A need has three forms. The check asks that an issue of a need is a work item of the same plan; a need
  on a work item of another milestone has no form yet.
- A line under a work item that starts with another word and a colon is a fault, so that a wrong word such
  as `Teir:` does not pass as a part of the line `Done:`.
- This repo gets no plan file for the milestone in work.

## What this change does not show

No code reads the lines `Tier:` and `Needs:` yet. The plan is a file that the leader approves and that a
check reads; the reviewer, the start of the work, and the tiers use it in the work items #142, #144, and
#148.
