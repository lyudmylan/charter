# Intent: the setup step

Work item: #38. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

One command sets a repo up for Charter.

## In scope

- `charter/charter/scripts/charter_setup.py`, Python 3.11 and the standard library. It takes flags or asks: the
  name of the repo, the address and the version of the organization source, the issue tracker, the code
  host, the CI, and who holds the roles.
- It writes: `charter.toml` from the template, `AGENTS.md`, the folder `intents/` with a template of an
  intent, the two workflows for GitHub, and `docs/architecture.md` as an empty map. No design spec
  template: the Design phase is on the roadmap.
- The adopter runs it from the folder of the installed plugin, which `claude plugin list` shows, or from
  a clone of the Charter repo at the version. The setup step says this in its help text.
- It refuses to overwrite a file that exists, and says which.
- It prints the manual steps: the secret for the organization source, the ruleset of the main branch
  with the required check "verdict", and the cache command for the computer.

## Out of scope

Other code hosts. A setup through a skill in a session; that comes when the plugin is installed.

## Acceptance checks

## Automatic checks

1. In an empty folder, the setup writes the files, and the written contract validates with the checker.
   test: `tests/test_setup.py::Setup.test_writes_a_valid_repo`
2. In a folder where a file exists, the setup refuses to overwrite it and names it.
   test: `tests/test_setup.py::Setup.test_refuses_to_overwrite`
3. The output names the three manual steps.
   test: `tests/test_setup.py::Setup.test_prints_the_manual_steps`

## Manual checks

None.
