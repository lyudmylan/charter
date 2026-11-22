# Plan: an agent run runs its commands in the sandbox, on a machine of the code host (#113)

Intent: `intents/sandbox-on-the-code-host.md`, checks 1 to 7.
The intent, the plan, and the code reach the leader together, and her merge approves the three.

## Steps

1. A test workflow on its own branch, not for the main branch, on machines of the code host. It installs
   the sandbox in each known way and gives a model a fixed list of commands. Its results decide steps 2
   and 3, and they are the evidence of check 6. The branch is deleted after the merge.
2. `charter/templates/run.yml` and `.github/workflows/run.yml`: `runs-on: ubuntu-24.04`, with the reason
   in a comment.
3. `charter/scripts/charter_check.py`, the function `boundary_settings`: the key
   `autoAllowBashIfSandboxed`, true, in the section of the sandbox, with its reason at the name of the key.
4. `charter/scripts/charter_run.py`, the text of the brief, step 4: the commands `charter-gate` and
   `charter-check` do not run in a run.
5. `docs/contract.md`: the settings in the section "The boundary of a run"; the image and the two
   commands in the section "The run".
6. Both manifests: 0.3.16.
7. Tests: `Settings.test_a_command_in_the_sandbox_needs_no_approval` in `tests/test_boundary.py`;
   `Workflow.test_the_run_names_the_image_of_the_machine`,
   `Brief.test_the_brief_says_which_commands_do_not_run`,
   `Documents.test_the_contract_document_names_the_image_and_the_approval`, and
   `Documents.test_the_version_carries_the_sandbox_correction` in `tests/test_run.py`.

## Files

- `charter/templates/run.yml`
- `.github/workflows/run.yml`
- `charter/scripts/charter_check.py`
- `charter/scripts/charter_run.py`
- `docs/contract.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `intents/sandbox-on-the-code-host.md`
- `plans/sandbox-on-the-code-host.md`
- `tests/test_boundary.py`
- `tests/test_run.py`
