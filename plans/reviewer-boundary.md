# Plan: a reviewer in CI writes no file and reads no token (#131)

Intent: `intents/reviewer-boundary.md`, checks 1 to 6.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. A test workflow on its own branch, not for the main branch, on a machine of the code host: Claude Code
   with the flags of the reviewers, a local server in the place of the model that answers with a fixed list
   of tool calls, and false tokens. It showed what the flags of that day allow, and it decided steps 2 and 3.
   The branch is removed after the test.
2. `charter/templates/review-intents.yml` and `charter/templates/review-code.yml`, the argument
   `claude_args`: `--permission-mode dontAsk`, the read tools with their folder, and `--disallowedTools`
   with the refused patterns. A comment above the argument gives the reason.
3. The same two files, the checkout: `persist-credentials: false`. The steps after it use `git show` and
   `git diff` on fetched commits, and `gh` with the token of the environment, so they need no credentials
   in the folder.
4. `.github/workflows/review-intents.yml` and `.github/workflows/review-code.yml`: the same two changes.
5. The test workflow again, with the flags read from the template: check 5. Its record goes to #131.
6. `docs/contract.md`, the section "The intent reviewer": one paragraph. `docs/decisions.md`: the row E14.
7. Both manifests: 0.3.20.
8. Tests: the class `ReviewerBoundary` in `tests/test_workflows.py`, four tests. The constant `READ_ONLY`
   of that file takes the read tools with their folder, so the older tests of the tool list hold.

## Files

- `charter/templates/review-intents.yml`, `charter/templates/review-code.yml`
- `.github/workflows/review-intents.yml`, `.github/workflows/review-code.yml`
- `docs/contract.md`, `docs/decisions.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `tests/test_workflows.py`
- `intents/reviewer-boundary.md`, `plans/reviewer-boundary.md`

## What an adopter does

It names the new version in its contract and copies the two reviewer workflows from the setup step.
