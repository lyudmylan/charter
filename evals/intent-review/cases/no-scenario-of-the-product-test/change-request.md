An agent run on a machine of the code host runs its commands inside the sandbox

Closes #113

The first agent run at an adopter ended as blocked: the sandbox started no command. A test on machines of the code host found two gaps, and this change request closes both. The results of the test are in a comment on #113.

## What changes

- The run workflow names the image `ubuntu-24.04`, in the template and in the workflow of this repo. The name `ubuntu-latest` is Ubuntu 26.04 now, and there the sandbox of Claude Code fails for each command. This is an open defect of Claude Code.
- `charter-check boundary` adds `sandbox.autoAllowBashIfSandboxed`. Without it each command asked for an approval, a run refuses each question, and no test of a repo could run. The limits of the sandbox stay, and no command runs outside it.
- The brief says that `charter-gate` and `charter-check` do not run in a run, and that the checks of the code host run them.
- `docs/contract.md`, both manifests at 0.3.16, the intent, the plan, and five tests.

## What it weakens

Nothing on Ubuntu 24.04. The test showed each limit with the new key: the closed files, the empty network, no token in the shell, the refused Docker socket.

## For the reviewer

- The intent, the plan, and the code are in one change request.
- Check 6 of the intent is manual, and its evidence is the test run on #113. Check 7 is the next agent run at an adopter.
- The test workflow is on the branch `113-sandbox-experiment`, which is not for the main branch.

No document change: `docs/product.md` names neither the image of the machine nor the keys of the sandbox; `docs/contract.md` holds both.
