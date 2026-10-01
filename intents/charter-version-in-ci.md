# Intent: the version of Charter in the contract, and the scripts fetched at that version in CI

Work item: #37. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A workflow of an adopter repo fetches the scripts of Charter at the version that its contract names, so
that the gates run in CI from one source and an organization can lock the version.

## In scope

- A field `charter.version` in the repo contract: the version of the core plugin that the repo uses. The
  schema declares it; the checker validates it.
- The workflow templates fetch the Charter repo at the tag of that version into a folder of the runner,
  and run `charter/scripts/...` from there. The tag follows the convention of Claude Code for plugins in
  one repo: `charter--v<version>`.
- The two workflows of this repo keep their current form: this repo is the source itself.

## Out of scope

A copy of the scripts into an adopter repo.

## Acceptance checks

## Automatic checks

1. The checker accepts a contract with `charter.version` and refuses one with a wrong type.
   test: `tests/test_charter_check.py::Validate.test_charter_version_field`
2. The workflow templates name the tag from the version and run the scripts from the fetched folder.
   test: `tests/test_setup.py::Templates.test_workflow_templates_fetch_charter_at_the_version`

## Manual checks

3. A run of the verdict in the second repo shows the fetch of Charter at the version. who: the leader, in the log of the run.
   Not automatic: the second repo is outside this repo.
