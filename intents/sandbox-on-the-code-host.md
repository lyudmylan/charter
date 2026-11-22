# Intent: an agent run runs its commands in the sandbox, on a machine of the code host

Work item: #113. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A run of an agent on a machine of the code host runs the quality commands of the repo inside the sandbox,
with no question to a person, and each limit of the sandbox holds.

## In scope

- Two gaps. The first run at an adopter showed the first one, and a test on machines of the code host
  showed the second one. The results of the test are on #113.
  - The image. The run workflow asked for `ubuntu-latest`, which is Ubuntu 26.04 now. On that image the
    helper of the sandbox of Claude Code fails for each command; this is an open defect of Claude Code,
    issues 43454 and 93130 of its repo. On Ubuntu 24.04, with the profile that the workflow installs, the
    sandbox starts each command.
  - The approval. The settings turned the sandbox on in the mode in which each command still asks for an
    approval. A run refuses each question, so a command outside the read-only set was refused, the tests
    of the repo among them.
- The run workflow names the image `ubuntu-24.04`, in the template and in the workflow of this repo, with
  the reason in a comment.
- `charter-check boundary` adds the key `sandbox.autoAllowBashIfSandboxed`, with the value true: a command
  that runs inside the sandbox needs no approval. The other keys stay. The limits of such a command are
  the limits of the sandbox, which the operating system holds: the closed files, the empty network, the
  tokens that leave the environment. No command runs outside the sandbox, `allowUnsandboxedCommands` stays
  false. The name of the key comes from the documentation of Claude Code, the page on the sandbox, read
  on 2026-11-22. Claude Code gives no message for a key that it does not know: when the name changes, a
  run refuses its commands again and ends as blocked, and check 8 shows it.
- The brief of a run says that the commands `charter-gate` and `charter-check`, which `AGENTS.md` names,
  do not run in a run: the machine holds no organization source while the agent works. The agent runs the
  quality commands as the contract writes them, and the checks of the code host run the two commands on
  the change request. `AGENTS.md` stays as it is: a run is the exception to its rule "Before a push", and
  the script that publishes makes the push, not the agent.
- `docs/contract.md`: the image, the approval, and the two commands.
- Both manifests: the same version, 0.3.16 or later.

## Out of scope

Ubuntu 26.04: the workflow moves to it when Claude Code corrects the defect. Each correction that is known
today weakens a limit. The setting that opens every Unix socket let a command reach the Docker service of
the machine in the test, and the system setting that the maintainers name did not correct the error. The
other workflows keep `ubuntu-latest`: they run no sandbox. A step that tests the sandbox before the agent
starts: a run whose sandbox fails ends as blocked after a few turns, and publishes nothing. The record of
each step of the agent: #83.

## Acceptance checks

## Automatic checks

1. The settings hold `sandbox.autoAllowBashIfSandboxed` with the value true, also with an empty section of
   the boundary, and keep `allowUnsandboxedCommands` false and `failIfUnavailable` true.
   test: `tests/test_boundary.py::Settings.test_a_command_in_the_sandbox_needs_no_approval`
2. The run workflow names the image `ubuntu-24.04`, in the template and in the workflow of this repo.
   test: `tests/test_run.py::Workflow.test_the_run_names_the_image_of_the_machine`
3. The brief says that the two commands do not run in a run, that the agent runs the quality commands as
   the contract writes them, and that the checks of the code host run the two commands.
   test: `tests/test_run.py::Brief.test_the_brief_says_which_commands_do_not_run`
4. `docs/contract.md` names the image, the approval, and the two commands.
   test: `tests/test_run.py::Documents.test_the_contract_document_names_the_image_and_the_approval`
5. Both manifests name the same version, 0.3.16 or later.
   test: `tests/test_run.py::Documents.test_the_version_carries_the_sandbox_correction`
6. In the product test, in a repo that the setup step made, the settings that `charter-check boundary`
   prints hold the key `autoAllowBashIfSandboxed` with the value true and `allowUnsandboxedCommands`
   with the value false.
   command: `python3 tests/product.py`, the step "settings of a run"

## Manual checks

7. On a machine of the code host with the image `ubuntu-24.04`, with the settings of the command and the
   key of this intent, an agent runs the tests of this repo, the two commands of a package manager, and a
   test that starts a child process and calls it on the loopback address. In the same run: a read of
   `.env` is refused, a write to `AGENTS.md` and a write outside the folder are refused, a host is not
   reached, the Unix socket of the Docker service is refused, and no process that the shell sees holds a
   token in its environment.
   who: the leader, from the results of the test run, which a comment on #113 holds with the address of
   each run; the comment stays when the branch of the test and the logs are gone. Not automatic: the
   check needs a model call and a machine of the code host.
8. The next agent run at an adopter, with this version, publishes a change request, or ends as blocked for
   a reason that is not the sandbox and not a refused approval.
   who: the leader. Not automatic: the check needs a model call, a machine of the code host, and a work
   item of the adopter.
