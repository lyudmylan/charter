#131 A reviewer in CI can write no file and can read no token

## Goal

A reviewer in CI can do what its prompt allows and no more: it reads the change, and it posts one report.

## The gap

The workflows `review-intents` and `review-code` give the reviewer this tool list: `Read`, `Glob`, `Grep`, `Bash(git diff:*)`, `Bash(git log:*)`, three read commands of `gh`, `Bash(gh pr comment:*)`, and one `gh api` path. The prompt says "change no file". The tool list does not enforce it:

- `git diff --output=<path>` writes a file on the runner. A later step of the same job runs scripts from the runner with the token of the workflow.
- `gh pr comment --body-file <path>` posts any file that the reviewer can read. `Read` plus a comment with a typed body does the same, so the flag is not the root: the root is what the reviewer can read on the runner.
- The checkout of both workflows keeps its credentials (`persist-credentials` has its default), so the token of the workflow stands in the git configuration of the folder that the reviewer reads. The token has `pull-requests: write`.

The reviewer reads text that it did not write: the change request. Since the workflow `run`, an agent with no person present writes such a change request. The workflows start only for a branch of the same repo, never for a fork.

The reviewer of the code of an adopter gave this finding on its own workflow, with severity low, on 2026-11-25. The mechanism is confirmed in the templates of 0.3.19. The effect is not tested.

## In scope

- `persist-credentials: false` on the checkout of both reviewers, when the steps after it need no git credentials (they use `git show`, `git diff`, and `gh` with a token from the environment).
- A test of what the reviewer can read on the runner: the git configuration, the environment of its process, the folder of the Charter scripts. The official documentation of the action says what it hides from the tools; the intent names the page.
- The tool list, or the settings of the reviewer, refuse a write: `git diff --output`, and a read of a path outside the checkout.
- The later steps of the job do not run a file that the reviewer could write.

## Out of scope

The workflow `run`: its boundary is the sandbox and the gate, and it has its own tests.

Part of the epic #82.


Intent: `intents/reviewer-boundary.md`
