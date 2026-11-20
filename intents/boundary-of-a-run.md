# Intent: the boundary of a run without a person

Work item: #91. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A run of an agent with no person present works inside a boundary that the contract declares, and a script
refuses the result of a run that crossed it, before anything is published.

## In scope

- Two fields of the contract, both sets of path patterns in the form of the paths of a risk tier:
  `boundary.no_write`, the files that a run never changes, adds, or deletes, and `boundary.no_read`, the
  files that a run never reads. An organization can set a minimum and lock it, and a repo can add
  patterns: the rule of each set. The paths of the high tier say who approves a change; these fields say
  what a run cannot do. A repo can list one path in both.
- A command, `charter-check boundary CONTRACT`. It prints the settings of Claude Code for a run, as JSON,
  from the effective contract. The settings hold:
  - the sandbox of the shell, on; no command runs outside it; the run does not start when the sandbox
    cannot start;
  - no network for the shell: the list of allowed hosts is empty;
  - for each pattern of `boundary.no_write`, a deny rule for the edit tools and a write denial of the
    sandbox;
  - for each pattern of `boundary.no_read`, a deny rule for the read tool and a read denial of the sandbox;
  - the removal of the token of the model and of the tokens of the code host from the environment of
    each shell command;
  - the refusal of each call that would need a question to a person (decision E6).
  The names of the keys come from the documentation of Claude Code (the pages on the sandbox, the
  permissions, and the settings, read on 2026-11-20). With an empty or absent section the settings hold
  no path rule, and the sandbox, the empty network, and the refusal stay.
- A gate, `charter-gate boundary --contract C --changed FILE`. The file lists the paths that a run
  changed, one on each line: each added, changed, or deleted path, and both names of a rename. The gate
  fails when a path is under a pattern of `boundary.no_write`. The failure names the path and the field,
  and says what to do: a person makes this change, in its own change request. The gate reads a path with
  dot segments as the path it points to, and refuses a path that leaves the repo.
- The plan of a work item, `intents/<part>.plan.md`: a run writes it, so the gate and the deny rules let
  it pass also when `intents/**` is in `boundary.no_write`. Each other file under `intents/` stays refused.
  This is decided here, because the gate needs the answer. How a person accepts the plan stays in #92.
- Four decisions, in `docs/decisions.md`, section E:
  - A run holds no credential of the code host. A step that is a script pushes the branch and opens the
    change request, after the gate passed. So "a run never pushes to the main branch and never merges"
    needs no rule on the text of a command (decision E2): the agent has nothing to do it with.
  - The settings of a run are written from the contract at the start of each run. They are not a file of
    the repo. A file can differ from the contract, and a change request can change it. The documentation
    of Claude Code gives settings from the command line the precedence over the files of a repo, and a
    sandbox that is set there ignores a file of the repo that loosens it.
  - For `boundary.no_write` there are two layers. The sandbox and the deny rules stop the agent
    (decision E5). The gate reads the result, whatever wrote it, and runs between the run and the push; a
    gate that fails or does not run publishes nothing. The gate is the layer for a writer that the
    sandbox and the permission rules do not cover: in Claude Code the sandbox covers the shell, and the
    permission rules cover the file tools.
  - A run can write the plan of a work item, also under a pattern of `boundary.no_write`. The run is the
    author of the plan. The approved intent holds the acceptance checks, and it stays closed to the run.
- The default, in `charter/templates/charter.toml`, which the setup step writes. `boundary.no_write`: the
  contract, `AGENTS.md`, `CLAUDE.md`, `intents/**`, `.github/**`, `.claude/**`. `boundary.no_read`: `.env`
  and `.env.*`, at the root and in each folder. The contract of this repo carries the same section.
  The package files of a language, for example `package.json` and its lock file, are not in the default:
  they differ from repo to repo, and a repo adds its own.
- The rule line with the identifier `boundary.no_write`, in `charter/templates/AGENTS.md` and in the
  `AGENTS.md` of this repo, so that an agent knows the boundary before it meets a refusal.
- `docs/contract.md`: the two fields, the command, and the gate. `docs/product.md`, section "Who does the
  work": what the boundary of a run is, in two sentences.
- Both manifests: the same version, 0.3.6 or later.

## Out of scope

The workflow of the run, #92: the install of the sandbox on the runner, the step that passes the
settings, the call of the gate, the step that publishes, and the test that the agent step holds no token
of the code host. The stop switch and the count of the refusals: later issues of #12. A field for hosts
that the shell can reach: when a run needs one. A platform without a sandbox. A person who works with an
agent in a session: the sandbox is optional there (decision E3). The minimum of the organization in its
source: a later change of that source, with its own version. A test of the sandbox and of the
permission rules of Claude Code themselves, except the manual check below. The conformance check of
decision E4: the settings are written from the contract at the start of each run, so no file can differ
from it; the check that a run used them is in #92.

## Acceptance checks

## Automatic checks

1. The schema has the fields `boundary.no_write` and `boundary.no_read` as sets, and `docs/contract.md`
   lists them, the command, and the gate.
   test: `tests/test_boundary.py::Fields.test_the_fields_are_in_the_schema_and_in_the_contract_document`
2. A repo contract that drops a pattern which the organization locked fails the check of the contract.
   test: `tests/test_boundary.py::Fields.test_a_repo_cannot_drop_a_locked_pattern`
3. The settings turn the sandbox on, let no command run outside it, refuse the start without it, and give
   the shell no host.
   test: `tests/test_boundary.py::Settings.test_the_sandbox_is_on_and_the_run_fails_without_it`
   test: `tests/test_boundary.py::Settings.test_the_shell_has_no_network`
4. The settings hold, for each pattern of `boundary.no_write`, a deny rule for the edit tools and a write
   denial of the sandbox; for each pattern of `boundary.no_read`, a deny rule for the read tool and a
   read denial of the sandbox.
   test: `tests/test_boundary.py::Settings.test_each_no_write_pattern_is_denied_in_both_layers`
   test: `tests/test_boundary.py::Settings.test_each_no_read_pattern_is_denied_in_both_layers`
5. The settings remove the token of the model and the tokens of the code host from the environment of a
   shell command, and refuse a call that would need a question.
   test: `tests/test_boundary.py::Settings.test_the_tokens_leave_the_environment_of_the_shell`
   test: `tests/test_boundary.py::Settings.test_a_call_that_needs_a_question_is_refused`
6. With an empty or absent section, the settings hold no path rule and keep the sandbox, the empty
   network, and the refusal.
   test: `tests/test_boundary.py::Settings.test_an_empty_section_keeps_the_sandbox`
7. The gate fails when a changed path is under a pattern of `boundary.no_write`; the failure names the
   path and the field, and says that a person makes the change. It passes when no path is under a pattern.
   test: `tests/test_boundary.py::Gate.test_a_path_under_no_write_fails`
   test: `tests/test_boundary.py::Gate.test_the_failure_names_the_path_the_field_and_the_remedy`
   test: `tests/test_boundary.py::Gate.test_paths_outside_the_patterns_pass`
8. The gate refuses the forms that go around a pattern: a path with dot segments, a file at depth under a
   folder pattern, a deleted file, a rename from a path under a pattern, a rename to one, and a path that
   leaves the repo.
   test: `tests/test_boundary.py::Gate.test_the_forms_that_go_around_a_pattern_fail`
9. With `intents/**` in `boundary.no_write`, the gate passes a changed `intents/<part>.plan.md` and fails
   a changed `intents/<part>.md`; the deny rules of the settings make the same difference.
   test: `tests/test_boundary.py::Gate.test_the_plan_file_passes_and_the_intent_fails`
   test: `tests/test_boundary.py::Settings.test_the_plan_file_is_not_denied`
10. The contract that the setup step writes carries the default patterns, and in a repo that the setup
    step made, the gate fails for a change of each path of the default.
    test: `tests/test_boundary.py::Defaults.test_the_new_contract_carries_the_default_patterns`
    test: `tests/test_boundary.py::Defaults.test_the_gate_refuses_each_default_path_in_a_new_repo`
11. The instruction template and the `AGENTS.md` of this repo carry the rule line with the identifier
    `boundary.no_write`.
    test: `tests/test_boundary.py::Defaults.test_the_instructions_carry_the_rule`
12. The decision record holds the four decisions in section E, each with its reason.
    test: `tests/test_boundary.py::Defaults.test_the_decisions_are_recorded`
13. The contract of this repo carries the section, and its contract checks pass.
    command: `python3 charter/scripts/charter_check.py all charter.toml`
14. Both manifests name a version of 0.3.6 or later, and the same one.
    test: `tests/test_boundary.py::Defaults.test_both_manifests_name_the_version`
15. The section "Who does the work" of `docs/product.md` says what a run without a person cannot do.
    test: `tests/test_boundary.py::Defaults.test_the_product_document_states_the_boundary_of_a_run`

## Manual checks

16. On a runner of the code host, in the first run of #92, with the settings that the command printed:
    the run starts with the sandbox, the edit tool refuses a write to the contract, a shell command
    reaches no host, and the log of the run names both refusals. who: the leader. Not automatic: the
    check needs a model call and a runner, and the workflow of the run comes with #92. The issue #92
    carries a line for this check, and the leader closes it there.
