# Intent: the setup step

Work item: #38. Status: done. Approval: a person merges the change request that adds this file.

## Goal

One command sets a repo up for Charter.

## In scope

- `charter/scripts/charter_setup.py`, Python 3.11 and the standard library. It takes flags or asks: the
  name of the repo, the address and the version of the organization source, the issue tracker, the code
  host, the CI, and who holds the roles. Optional: the quality commands, the code paths, more high-tier paths.
- It writes: `charter.toml` from the template, `AGENTS.md`, the folder `intents/` with a template of an
  intent, the three workflows for GitHub (tests, verdict, review-intents), and `docs/architecture.md`
  as an empty map. It writes `docs/product.md` as a stub only when the repo has none. No design spec
  template: the Design phase is on the roadmap. The templates live in `charter/templates/`.
- The adopter runs it as `charter-setup`: the plugin ships the commands `charter-setup`, `charter-check`,
  `charter-gate`, and `charter-facts-github` in its `bin/` folder, which Claude Code puts on the path of
  the shell while the plugin is enabled. Or from a clone of the Charter repo at the version. The help
  text says this.
- It refuses to overwrite a file that exists, and says which; then it writes nothing.
- It prints the manual steps: the secrets, the ruleset of the main branch with the required check
  "verdict", the cache command for the computer, the quality command when none was given, the line
  `@AGENTS.md` for a repo that has a `CLAUDE.md`, and the first intent.
- Two findings of the first setup of the second repo (#55, #56): the checker skips the repo's own name
  in the project name patterns, because the organization lists every project and a repo names itself;
  and both manifests say 0.2.0, because the adopter workflows fetch Charter at the tag of the version.

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
4. A repo that carries one of the project names of the organization passes the text check on its own name.
   test: `tests/test_charter_check.py::OwnName.test_the_name_of_the_repo_is_not_a_foreign_project_name`

## Manual checks

5. The setup runs in the second repo, and its first change request gets the three checks. who: the leader.
   Not automatic: the second repo is outside this repo.
