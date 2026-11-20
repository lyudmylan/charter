# Plan: the plan of a work item lives in `plans/`, and a change request takes the tier of its code (#65)

Intent: `intents/plan-tier.md`, checks 1 to 11. Check 12 is manual, in an adopter repo.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan stays at the old place: the verdict runs the gates of the main branch, which read the old
place until this change is merged.

## Steps

1. `charter/scripts/charter_check.py`: a constant `PLANS_DIR = "plans/"`, and the old suffix under the
   name `OLD_PLAN_SUFFIX`. The special rule for a plan leaves the boundary: `PLAN_PROBE` and `is_plan`
   go, and `closed_paths` keeps two cases: for the sandbox, a pattern with a wildcard that is no trailing
   `/**` becomes the files that match it now; each other pattern stays as it is.
2. `charter/scripts/charter_gate.py`:
   - `plan_of("intents/<part>.md")` gives `plans/<part>.md`, also for a part with folders in it. A new
     function `old_plan_of` gives `intents/<part>.plan.md`.
   - The message of a missing plan: "`{plan}` is missing. A plan at the old place, `{old}`, counts too."
   - `gate_boundary` has no rule for a plan.
3. `charter/scripts/charter_facts_github.py`: the plan of an intent exists when the file of `plan_of` or
   the file of `old_plan_of` is at the head commit.
4. `charter/templates/review-intents.yml` and `.github/workflows/review-intents.yml`: the trigger paths
   are `intents/**` and `plans/**`, and the line of the instructions that lists the changed files reads
   both folders.
5. `charter/templates/plan.md`, new: the title line with the work item, the line that names the intent,
   and the sections "Steps", "Files", and "Tests". `charter/scripts/charter_setup.py` writes it as
   `plans/_template.md`, in the list of the written files. The high tier paths stay as they are.
6. The texts that name the place: `AGENTS.md`, `charter/templates/AGENTS.md`,
   `charter-practices/skills/tracker/SKILL.md`, the notes of `build.plan_before_code` and
   `boundary.no_write` in `charter/schema/contract.toml`, the comments in `charter.toml` and in
   `charter/templates/charter.toml`, and `docs/contract.md`: the row of `build.plan_before_code`, the
   paragraph on the facts, the section on the boundary, and one new paragraph on the move of a repo with
   the command `git mv intents/<part>.plan.md plans/<part>.md`.
7. `docs/decisions.md`: a row D18, dated 2026-11-20, with the decision and the reason of the intent. The
   row E10 gets one sentence: "Replaced by D18: the plan lives in `plans/`, outside the closed patterns."
8. The eight plans of this repo move with `git mv` from `intents/<part>.plan.md` to `plans/<part>.md`.
   `intents/plan-tier.plan.md` stays.
9. `intents/boundary-of-a-run.md`: the bullet on the plan and check 9 say that a plan in `plans/` passes
   and each file under `intents/` fails, with a pointer to this intent. `intents/plan-before-the-code.md`:
   one line that points to this intent. `intents/plan-tier.md`: `Status: done`.
10. Both manifests: 0.3.8.

## Files

- `charter/scripts/charter_check.py`, `charter/scripts/charter_gate.py`,
  `charter/scripts/charter_facts_github.py`, `charter/scripts/charter_setup.py`
- `charter/templates/review-intents.yml`, `charter/templates/plan.md`, `charter/templates/AGENTS.md`,
  `charter/templates/charter.toml`, `charter/schema/contract.toml`
- `.github/workflows/review-intents.yml`, `AGENTS.md`, `charter.toml`
- `charter-practices/skills/tracker/SKILL.md`
- `docs/contract.md`, `docs/decisions.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/plan-tier.md`, `intents/plan-tier.plan.md`, `intents/boundary-of-a-run.md`,
  `intents/plan-before-the-code.md`
- `plans/**`: eight files that move from `intents/`
- `tests/test_charter_gate.py`, `tests/test_charter_facts_github.py`, `tests/test_setup.py`,
  `tests/test_workflows.py`, `tests/test_boundary.py`, `tests/test_intents.py`

## Tests

The new tests, in a class `PlanPlace` of each file, with the names that the intent gives:

- `tests/test_charter_gate.py`: `test_the_plan_of_an_intent_is_in_the_plans_folder`,
  `test_the_missing_plan_names_the_new_place`, `test_a_change_with_its_plan_takes_the_tier_of_its_code`
  (the tiers of the contract that the setup step writes, through `tier_of`),
  `test_the_decision_is_recorded`, `test_both_manifests_name_the_version`.
- `tests/test_charter_facts_github.py`: `test_the_plan_is_found_in_the_plans_folder`,
  `test_a_plan_at_the_old_place_still_counts`, `test_a_plan_at_neither_place_is_missing`, with the fake
  of the code host that the file has.
- `tests/test_setup.py`: `test_the_setup_writes_the_template_of_a_plan`,
  `test_the_instructions_and_the_documents_name_the_new_place`.
- `tests/test_workflows.py`: `test_the_reviewer_runs_on_a_change_of_a_plan`.
- `tests/test_intents.py`: `test_the_plans_of_this_repo_are_in_the_plans_folder`.

The tests that change: in `tests/test_boundary.py` the two tests of check 9 of the boundary intent keep
their names and prove the new rule; in `tests/test_charter_gate.py` and
`tests/test_charter_facts_github.py` the expected place of a plan; in `tests/test_intents.py` the test
that a plan is no intent.
