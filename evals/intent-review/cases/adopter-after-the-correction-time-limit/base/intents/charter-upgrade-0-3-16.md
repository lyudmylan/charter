# Intent: this repo moves to Charter 0.3.16

Work item: #31. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.16 and the run workflow is the one that the setup step of that version
writes, so that a run of an agent runs its commands on a machine of the code host.

## In scope

- Why: the first run of an agent, on issue 2, ended as blocked. The sandbox started no command on the
  image that the workflow asked for, Ubuntu 26.04. A test in the repo of Charter also showed that the
  settings of a run refused each command outside a small read-only set, the tests of this repo among
  them. Charter 0.3.16 corrects both.
- `charter.toml`: the version 0.3.16. The scripts of that version add one key to the settings of a run,
  `sandbox.autoAllowBashIfSandboxed`: a command that runs inside the sandbox needs no approval. The
  contract of this repo gets no new field.
- `.github/workflows/run.yml`: the file of the setup step of 0.3.16, with the image `ubuntu-24.04` by its
  name.
- One change request. The version adds no field to the contract, so the checks of 0.3.15, which run
  from the main branch, read the changed contract.

## Out of scope

The second run of an agent on issue 2: a person starts it after the merge. The other workflows: the
setup step of 0.3.16 writes them as they are. The move to a later image: an issue of Charter holds it.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.16.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The contract names the version 0.3.16.
   command: `grep -q '^version = "0\.3\.16"$' charter.toml`
4. The run workflow names the image.
   command: `grep -q '^    runs-on: ubuntu-24.04$' .github/workflows/run.yml`
5. The settings of a run approve a command that runs inside the sandbox.
   command: `charter-check boundary charter.toml | grep -q '"autoAllowBashIfSandboxed": true'`

## Manual checks

6. Each of the five workflows is the file that the setup step of 0.3.16 writes with the values of this
   repo and its toolchain steps.
   who: the engineer, with a setup in an empty folder and a comparison of the files. Not automatic:
   Charter has no command yet that updates a repo.
7. The next run of an agent on issue 2 publishes a change request; or it ends as blocked, the reason on
   the issue is neither the sandbox nor a refused approval of a command, and that reason shows that at
   least one command of the quality checks started.
   who: the leader. Not automatic: the check needs a model call, a machine of the code host, and the
   label that a person puts.
