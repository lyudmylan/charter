#113 An agent run on a machine of the code host runs its commands inside the sandbox

## Goal

An agent run on a machine of the code host runs its shell commands inside the sandbox.

## What happened

The first agent run at an adopter, with Charter 0.3.15, ended blocked after 2 minutes. Each shell command of the agent failed before it started:

```
apply-seccomp: write /proc/self/setgroups (nested userns is capability-restricted; caller must provide CAP_SYS_ADMIN): Permission denied
```

The agent wrote files with the file tools, could not run the quality commands, and reported "blocked". The run published nothing and wrote its outcome on the issue. That part is correct.

Facts of the run:
- The image of the machine is `ubuntu-26.04`: the name `ubuntu-latest` of the workflow gives this image now.
- Claude Code 2.1.329, the packages `bubblewrap` and `socat`, and the AppArmor profile for `/usr/bin/bwrap` from the documentation of Claude Code.
- The setting `failIfUnavailable` did not stop the run at its start: the check at the start passed, and each command failed later.

The error is an open defect of Claude Code on Ubuntu 24.04 and 26.04 (issues 43454 and 93130 of its repo). A maintainer wrote there that the helper needs a nested user namespace with capabilities, and that the profile of the documentation covers bubblewrap only.

## In scope

- A test on machines of the code host that shows which correction lets a command run, and that the limits of the sandbox still hold: the closed files, the closed network, the closed variables.
- The image of the machine has a fixed name in the run workflow.
- A command that runs inside the sandbox needs no approval. The test showed this second gap: without it, a run refuses the tests of the repo.
- The brief of a run says which commands of `AGENTS.md` do not run in a run.

## Out of scope

- A sandbox other than the one of Claude Code.
- A machine that the adopter hosts.
- A step that tests the sandbox before the agent starts: a run whose sandbox fails ends as blocked after a few turns, and publishes nothing.

Intent: intents/sandbox-on-the-code-host.md
