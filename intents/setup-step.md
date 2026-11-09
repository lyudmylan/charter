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
- The first change request of the second repo (#58): GitHub refused the written `tests.yml` and
  `verdict.yml`, because they set a variable from the `runner` context in a job-level `env`, where that
  context is not available. The fetch step now writes the variable to `$GITHUB_ENV`, and a test refuses
  the old form. The lesson stands: a test of a template must look at what the host accepts.
- Two findings of the first setup of the second repo (#55, #56): the checker skips the repo's own name
  in the project name patterns, because the organization lists every project and a repo names itself;
  and both manifests carry the same version, because the adopter workflows fetch Charter at the tag of the version.
- A finding of the first adopter on a private repo (#63): the written `verdict.yml` declared no
  `actions: read`, and the facts step got 403 when it listed the runs of the review workflow to count the
  rounds. A public repo serves that listing without the scope, which is why the verdict of this repo passed
  with the same block. The template and the `verdict.yml` of this repo declare the scope, and a test refuses
  a written verdict workflow without it. Version 0.3.1 carries the fix.
- A finding of 2026-11-02, in an adopter (#68): the fetch of the organization source failed on an expired
  token, and the change request showed two green checks and no check "verdict". The step "Publish the
  check" runs under the `-e` shell of the host, and its read of the missing `verdict.txt` ended the step
  before the fallback title. The two reads now tolerate a missing file, the commit of the check falls
  back to the head commit of the run, and a test runs the step without the file.

## Out of scope

Other code hosts. A setup through a skill in a session; that comes when the plugin is installed. The
expiry of the token of the organization source: an operation of the adopter. A message that names the
expired token in the fetch step: later.

## Acceptance checks

## Automatic checks

1. In an empty folder, the setup writes the files, and the written contract validates with the checker.
   test: `tests/test_setup.py::Setup.test_writes_a_valid_repo`
2. In a folder where a file exists, the setup refuses to overwrite it and names it.
   test: `tests/test_setup.py::Setup.test_refuses_to_overwrite`
3. The output names the manual steps of the scope: the secrets, the ruleset with the check "verdict", the
   cache command, the quality command when none was given, the `@AGENTS.md` line when `CLAUDE.md` exists,
   and the first intent.
   test: `tests/test_setup.py::Setup.test_prints_the_manual_steps`
4. A repo that carries one of the project names of the organization passes the text check on its own name.
   test: `tests/test_charter_check.py::OwnName.test_the_name_of_the_repo_is_not_a_foreign_project_name`
5. Each of the four commands exists in `charter/bin/` and is executable, and both manifests carry the same
   version.
   test: `tests/test_setup.py::Commands.test_the_four_commands_exist_and_the_manifests_agree`
6. The written `tests.yml` and `verdict.yml` set no `runner` context in a job-level `env`, and write the
   variable of the scripts folder to `$GITHUB_ENV` in a step.
   test: `tests/test_setup.py::Templates.test_no_runner_context_in_a_job_env`

7. The written `verdict.yml` and the `verdict.yml` of this repo both declare `actions: read` in their
   permissions block.
   test: `tests/test_setup.py::Templates.test_verdict_template_declares_actions_read`
8. The step "Publish the check" of the written `verdict.yml` publishes the check with the conclusion
   failure and the title "the verdict could not run" when `verdict.txt` is missing, and then fails the
   job; with a verdict, the conclusion is success. The step has the same text in the `verdict.yml` of
   this repo. The commit of the check is `steps.pr.outputs.sha`, or `github.event.workflow_run.head_sha`
   when the step "Find the change request" did not run: an expression that the host evaluates, which the
   test reads as text.
   test: `tests/test_setup.py::Templates.test_the_check_is_published_when_the_verdict_could_not_run`

## Manual checks

9. The setup runs in the second repo, and its first change request gets the three checks. who: the leader.
   Not automatic: the second repo is outside this repo.
