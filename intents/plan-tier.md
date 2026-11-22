# Intent: the plan of a work item lives in `plans/`, and a change request takes the tier of its code

Work item: #65. Approval: a person merges the change request that adds this file.

## Goal

A change request that carries the code of a work item and its plan is in the tier of the code, because
the plan lives in a folder of its own, `plans/<part>.md`, outside the high tier.

## In scope

- The gap: `intents/**` is in the high tier of each repo, and the plan `intents/<part>.plan.md` lives
  there. With `build.plan_before_code`, each change request with code carries its plan, so each one is in
  the high tier and a person merges all of them. No change reaches the low tier, and the approver `agent`
  of a tier has no effect.
- The decision, in `docs/decisions.md`, section D: the plan of the intent `intents/<part>.md` is the file
  `plans/<part>.md`. The reason: the path patterns of a tier have no exclusion, so a file under
  `intents/` cannot leave the high tier; a folder of its own needs no special rule. The plan is the words
  of the author, and it is no rule: the intent holds the acceptance checks and stays in the high tier.
- `plan_of` in `charter_gate.py` gives the new place. The message of a missing plan names it.
- The facts collector: the plan of an intent exists when `plans/<part>.md` is at the head commit. A plan
  at the old place, `intents/<part>.plan.md`, still counts, so that a repo moves in steps and an open
  change request does not turn red on the day of the new version. A plan at the old place stays in the
  high tier, which is the reason to move it.
- The reviewer of intents still reads a plan: the trigger of the workflow `review-intents`, in the
  template and in this repo, covers `plans/**`, and its instructions list the changed files of both
  folders.
- The setup step writes `plans/_template.md`, a template of a plan with the three parts that the
  instructions name: the steps, the files, the tests. The high tier paths that it writes do not hold
  `plans/**`.
- The boundary of a run (#91): the special rule for a plan leaves the gate and the settings. A plan in
  `plans/` is under no closed pattern, and `intents/**` is closed as one folder in both layers. The row
  E10 of the decision record says that this decision replaces it. The boundary changes here because the
  special rule of E10 exists only while the plan is under `intents/`.
- The texts that name the place: `AGENTS.md` and its template, the skill `tracker`, the notes of the
  schema, the comments of the two contracts, and `docs/contract.md`, which also says how a repo moves:
  `git mv intents/<part>.plan.md plans/<part>.md`.
- This repo: the eight plans of the work items that are done move to `plans/`. The plan of this work
  item stays at the old place, `intents/plan-tier.plan.md`: the verdict runs the gates of the main
  branch, which read the old place until this change is merged.
- Both manifests: the same version, 0.3.8 or later.

## Out of scope

Who accepts a plan in each tier, and the merge by the verdict: #66. A check that fails when a plan is at
the old place. The update of an adopter repo by a command: #97. The intents of work items that are done
keep their text, with the old place in it; one line in `intents/plan-before-the-code.md` points to this
intent. The move of `intents/plan-tier.plan.md` to `plans/plan-tier.md`: the first change after this one.

## Acceptance checks

## Automatic checks

1. The plan of `intents/app.md` is `plans/app.md`, and the plan of `intents/sub/app.md` is
   `plans/sub/app.md`.
   test: `tests/test_charter_gate.py::PlanPlace.test_the_plan_of_an_intent_is_in_the_plans_folder`
2. The facts collector finds a plan at `plans/<part>.md`. A plan at the old place still counts. With a
   plan at neither place the fact says that the plan is missing, and the gate names the new place.
   test: `tests/test_charter_facts_github.py::PlanPlace.test_the_plan_is_found_in_the_plans_folder`
   test: `tests/test_charter_facts_github.py::PlanPlace.test_a_plan_at_the_old_place_still_counts`
   test: `tests/test_charter_facts_github.py::PlanPlace.test_a_plan_at_neither_place_is_missing`
   test: `tests/test_charter_gate.py::PlanPlace.test_the_missing_plan_names_the_new_place`
3. With the tiers that the setup step writes, a change of a code file and its plan in `plans/` is in the
   low tier, and the same change with the plan at the old place is in the high tier.
   test: `tests/test_charter_gate.py::PlanPlace.test_a_change_with_its_plan_takes_the_tier_of_its_code`
4. The setup step writes `plans/_template.md` with the three parts, and the high tier paths of the
   contract that it writes do not match a file under `plans/`.
   test: `tests/test_setup.py::PlanPlace.test_the_setup_writes_the_template_of_a_plan`
5. The workflow `review-intents`, in the template and in this repo, runs on a change under `plans/`, and
   its instructions list the changed files of `intents/` and of `plans/`.
   test: `tests/test_workflows.py::PlanPlace.test_the_reviewer_runs_on_a_change_of_a_plan`
6. The boundary gate passes a changed `plans/<part>.md` and fails each changed file under `intents/`, a
   file `intents/<part>.plan.md` among them. The settings close `intents/**` as one folder in both layers.
   test: `tests/test_boundary.py::Gate.test_the_plan_file_passes_and_the_intent_fails`
   test: `tests/test_boundary.py::Settings.test_the_plan_file_is_not_denied`
7. The instruction template, the `AGENTS.md` of this repo, the skill `tracker`, and `docs/contract.md` name
   the place `plans/<part>.md`, and `docs/contract.md` holds the command of the move.
   test: `tests/test_setup.py::PlanPlace.test_the_instructions_and_the_documents_name_the_new_place`
8. In this repo, `plans/` holds the plans of the work items that are done, and `intents/` holds no plan but
   the one of this work item.
   test: `tests/test_intents.py::PlanPlace.test_the_plans_of_this_repo_are_in_the_plans_folder`
9. The decision record holds the decision in section D with its reason, and the row E10 names it.
   test: `tests/test_charter_gate.py::PlanPlace.test_the_decision_is_recorded`
10. Both manifests name the same version, 0.3.8 or later.
    test: `tests/test_charter_gate.py::PlanPlace.test_both_manifests_name_the_version`
11. The contract checks of this repo pass.
    command: `python3 charter/scripts/charter_check.py all charter.toml`

## Manual checks

12. In an adopter repo with the version 0.3.8, a change request with a code file of the low tier and its
    plan in `plans/` shows the low tier in the verdict. who: the leader. Not automatic: the adopter repo
    is outside this repo.
