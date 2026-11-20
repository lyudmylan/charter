# Intent: the workflows have a declared place for the toolchain of the repo

Work item: #88. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A repo whose quality commands need an install step gets a `tests` workflow that works from the setup
step, and the install steps have one marked place that a function reads back, so that a later update
can keep it.

## In scope

- The gap: the template of the workflow `tests` checks out the code, fetches Charter, and runs the
  quality commands. That is enough for a repo with no install step, such as this one. In 2026-11 an
  adopter with a TypeScript toolchain added three steps by hand: the package manager, the runtime, and
  the install of the dependencies. Nothing marks these steps as the ones of the repo, so a new version
  of the template does not know them.
- The form: a marked block in the workflow, between the line `# charter:toolchain:start` and the line
  `# charter:toolchain:end`, after the checkout and before the quality step. It holds steps of the
  workflow, because a toolchain needs actions of the code host, for example the one that installs a
  runtime, and a command of the contract cannot express them. The contract gets no field.
- The setup step: a flag `--toolchain FILE`. The file holds the steps as they stand in a workflow, with
  no indent before the first `- `. The setup step puts them into the block with the indent of the
  steps. Without the flag the block is empty, and the workflow is the one of today plus the two lines.
  A file that holds one of the two marker lines is refused.
- A function that reads the block of a written workflow, for the update of a repo (#97) and for the
  workflow of a run (#92), which takes the same steps before the agent starts.
- The steps of the block run in the workflow `tests`, which runs the code of the change request and
  holds no secret. The template says so beside the block.
- The checkout action. The templates and the workflows of this repo that run on a change request move
  from `actions/checkout@v4` to `actions/checkout@v7`, the current major version on 2026-11-20:
  `tests`, `review-intents`, and `review-code`. They run from the branch of the change request, so this
  change request proves them. The verdict workflow stays at `v4` here: it runs from the main branch, a
  fault in it would block each change request, and it moves in a change of its own after this proof.
- `docs/contract.md`, section "The setup step": the flag, the block, and the rule that an update keeps
  the block.
- Both manifests: the same version, 0.3.12 or later.

## Out of scope

The update of a repo that is set up: #97; it keeps the block. The workflow of a run: #92. A cache of the
dependencies. A CI other than GitHub Actions. One template for each language. The move of the verdict
workflow to the new checkout action.

## Acceptance checks

## Automatic checks

1. Without the flag, the setup step writes a `tests` workflow with an empty block after the checkout and
   before the quality step. The `tests` workflow of this repo has the same empty block. The template
   holds the comment line that says that the steps run with no secret.
   test: `tests/test_workflows.py::Toolchain.test_the_block_is_empty_without_the_flag`
2. With the flag, the steps of the file stand in the block with the indent of the steps, in their order,
   and the lines outside the block are the ones of the template.
   test: `tests/test_workflows.py::Toolchain.test_the_steps_of_the_file_stand_in_the_block`
3. The function reads the steps back from the written workflow as the file gave them, and reads an
   empty block as no step.
   test: `tests/test_workflows.py::Toolchain.test_the_block_is_read_back`
4. A file with a marker line is refused, and a missing file is refused; the setup step then writes
   nothing.
   test: `tests/test_workflows.py::Toolchain.test_a_file_with_a_marker_or_no_file_is_refused`
5. The templates and the workflows of this repo that run on a change request use the checkout action at
   `v7`, and the verdict workflow keeps `v4`. The later change that moves the verdict workflow changes
   this test.
   test: `tests/test_workflows.py::Toolchain.test_the_checkout_action_of_each_workflow`
6. `docs/contract.md` names the flag, the two marker lines, and the rule for an update.
   test: `tests/test_workflows.py::Toolchain.test_the_contract_document_names_the_block`
7. Both manifests name the same version, 0.3.12 or later.
   test: `tests/test_workflows.py::Toolchain.test_both_manifests_name_the_version`

## Manual checks

8. The checks `tests`, `review-intents`, and `review-code` of the change request that carries this intent
   run with the new checkout action. who: the leader, by a look at the three checks. Not automatic: the
   runs are on the code host. `review-code` passes only after #106 is merged.
9. An adopter with a TypeScript toolchain writes its three steps through the flag, and its `tests`
   workflow passes with no step added by hand. who: the leader. Not automatic: the adopter repo is
   outside this repo.
