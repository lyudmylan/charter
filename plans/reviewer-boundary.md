# Plan: a reviewer in CI writes no file and reads no token (#131)

Intent: `intents/reviewer-boundary.md`, checks 1 to 7.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. A test workflow on its own branch, not for the main branch, on a machine of the code host: Claude Code
   with the flags of the reviewers, a local server in the place of the model that answers with a fixed list
   of tool calls, and false tokens. It showed what the flags of that day allow, and it decided steps 2 and 3.
   The branch is removed after the test. Its record is a comment on #131.
2. `charter/templates/review-intents.yml` and `charter/templates/review-code.yml`, the argument
   `claude_args`: `--permission-mode dontAsk`, the read tools with their folder, the five commands of the
   shell, and `--disallowedTools` with the refused patterns. A comment above the argument gives the reason.
3. The same two files, the checkout: `persist-credentials: false`. The steps after it use `git show` and
   `git diff` on fetched commits, and `gh` with the token of the environment.
4. The same two files, two new steps. "Give the earlier reports to the reviewer", before the reviewer:
   it writes the reports of the change request to a file of the folder `review`. "Post the report of the
   reviewer", after it: it reads the final answer from the record of the run, takes the text from the
   marker line on, and posts it with `gh pr comment --body-file`. The prompt says that the report is the
   final answer, and names the file of the earlier reports. This step came from round 1 of the review of
   the code: with `gh pr comment` in its shell, the reviewer could post any file.
5. `.github/workflows/review-intents.yml` and `.github/workflows/review-code.yml`: the same changes.
6. `tests/probe/server.py` and `tests/probe/reviewer_probe.py`: the test of step 1 as a script that reads
   the flags from the template and fails on a wrong case. `.github/workflows/reviewer-boundary.yml`, for
   this repo only: it runs the script on a change of a reviewer workflow.
7. `docs/contract.md`, the section "The intent reviewer": two paragraphs. `docs/decisions.md`: the row E14.
8. Both manifests: 0.3.20.
9. Tests: the class `ReviewerBoundary` in `tests/test_workflows.py`, five tests. The constants of that file
   take the read tools with their folder and the five commands, and three older tests of the tool list
   and of the prompt read the posting command from the new step.

## Files

- `charter/templates/review-intents.yml`, `charter/templates/review-code.yml`
- `.github/workflows/review-intents.yml`, `.github/workflows/review-code.yml`
- `.github/workflows/reviewer-boundary.yml`
- `tests/probe/server.py`, `tests/probe/reviewer_probe.py`
- `docs/contract.md`, `docs/decisions.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `tests/test_workflows.py`
- `intents/reviewer-boundary.md`, `plans/reviewer-boundary.md`

## What an adopter does

It names the new version in its contract and copies the two reviewer workflows from the setup step.
