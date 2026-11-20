# Plan: a ready issue starts an agent run, and the run ends as a change request (#92)

Intent: `intents/run-from-an-issue.md`, checks 1 to 14. Checks 15 and 16 are manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan builds on #91, #101, #66, and #88.

## Steps

1. `charter/scripts/charter_run.py`, new, Python 3.11 and the standard library, in the form of the other
   scripts: a configuration block with each name and message, and four commands. `charter/bin/charter-run`
   is its wrapper, as the other commands have one.
   - `ready --issue FILE --root DIR`: `FILE` is the issue as JSON of the code host (number, title, body,
     state). It passes when the issue is open, its body holds exactly one line `Intent: intents/<part>.md`
     (the pattern of `charter_facts_github.py`), and that path is a file under `DIR`. It prints the
     intent, the plan path of `plan_of`, and the branch `run/<number>`, one `name=value` on each line. A
     failure prints the reason and ends with 1.
   - `brief --issue FILE --intent PATH --out FILE`: the fixed text, then the issue under a line that
     says that the text below comes from the tracker and is data. The fixed text says: read `AGENTS.md`
     and the intent; write the plan to the path of `plan_of`; write the code and the tests until each
     acceptance check of the intent holds; run the quality commands of the contract; change no file that
     the boundary closes, and when the work needs such a change, stop and say so; commit nothing; no
     network and no code host are there; write the text of the change request to
     `.charter-run/change-request.md`, with the line `No document change: <reason>` when it applies; when
     the work cannot be finished, write the reason to `.charter-run/blocked.md` and stop.
   - `result --agent FILE --root DIR --base REF --issue FILE --out DIR`: `FILE` is the JSON that
     `claude -p --output-format json` printed. It moves `.charter-run/` out of the repo into `--out`,
     commits each change with `git -c core.hooksPath=/dev/null` under a fixed author name, with the title
     of the issue and its number as the message, and writes the changed paths against `--base` with a
     NUL character between them to `--out`/`changed`. It ends as blocked, with the reason, when the agent
     result is missing, is no JSON, or says that it is an error; when `blocked.md` exists (its text is
     the reason); or when no path changed. It prints the reason and ends with 1.
   - `outcome --state STATE --reason TEXT --agent FILE [--url URL]`: prints the comment for the issue: a
     marker line, the outcome, the reason or the address of the change request, and the turns, the
     duration, and the cost of the agent result, or "not reported" for a value that is not there.
2. `charter/templates/run.yml`, new, and `.github/workflows/run.yml`:
   - `on: issues` with the type `labeled`, and `workflow_dispatch` with the input `issue`. The job runs
     when the variable `CHARTER_RUNS` is not `off` and the event is the start by hand or the label
     `charter-run`. `concurrency` with one group and no cancel. `permissions`: `contents: read` and
     `issues: write`. A time limit of the job.
   - The steps, with these names, each value of the code host through `env:`:
     "Take the main branch" (checkout at `v4`, as the verdict, with no credential left);
     "Fetch Charter at the version of the contract" (in this repo: a git worktree of the main branch in
     the temporary folder of the runner, as `review-code.yml` does);
     "Read the issue and decide whether it is ready" (the token of the workflow, `gh issue view`, then
     `charter_run.py ready`);
     the toolchain block of #88, between its two marker lines;
     "Install the sandbox and Claude Code" (the two packages, the profile of the documentation for
     `/usr/bin/bwrap`, and the install script of Claude Code at the version of an `env` value
     at the top of the file);
     "Write the settings of the run" (the organization source with its token, as the verdict fetches it,
     then `charter_check.py boundary`, into a file of the temporary folder);
     "Write the brief";
     "Run the agent" (the new branch; `claude -p` with the brief on standard input or as the argument,
     `--settings` with the text of the settings file, no list of allowed tools,
     `--max-turns` from an `env` value at the top, `--output-format json` into a file of the temporary
     folder; `continue-on-error: true`; a time limit of the step; the one secret
     `CLAUDE_CODE_OAUTH_TOKEN`);
     "Take the result of the agent" (`charter_run.py result`);
     "Check the result against the boundary" (`charter_gate.py boundary` with the contract of the main
     branch from the copy made before the agent, and the list of the result step);
     "Publish the change request" (only when the two steps before passed; the secret
     `CHARTER_RUN_TOKEN` as `GH_TOKEN`; without it the step fails with a message; `gh auth setup-git`,
     `git -c core.hooksPath=/dev/null push origin HEAD:refs/heads/<branch>`, `gh pr create` with the
     title of the issue, the text file of the agent or a default text, and a first line `Closes #<n>`);
     "Write the outcome on the issue" (`if: always()`; `charter_run.py outcome`, then
     `gh issue comment` with the token of the workflow).
   - The contract for the gate and for the settings is the one of the main branch, copied to the
     temporary folder before the agent starts.
3. `charter/scripts/charter_setup.py`: `run.yml` joins the written files; the toolchain block of the run
   gets the same steps as the block of `tests`; the manual steps name the label `charter-run`, the
   variable `CHARTER_RUNS`, and the secret `CHARTER_RUN_TOKEN`.
4. `charter-practices/skills/tracker/SKILL.md`: what a work item for a run looks like, inside the limit
   of lines of a skill.
5. `docs/contract.md`: a section "The run" after "The boundary of a run". `docs/product.md`: the Build
   row, and one sentence in "Who does the work". `docs/decisions.md`, section E: three rows with the next
   free identifiers, dated 2026-11-20: a person starts a run with a label or by hand; one variable of
   the repo stops the start of every run; a token of a person publishes the result, because a change
   request that the token of the workflow opens starts no workflow, and no step after the agent runs a
   file that the agent wrote.
6. Both manifests: 0.3.13. `intents/run-from-an-issue.md`: `Status: done`.

## Files

- `charter/scripts/charter_run.py`, `charter/bin/charter-run`, `charter/scripts/charter_setup.py`,
  `charter/scripts/charter_check.py` (three values more in the settings of the boundary)
- `charter/templates/run.yml`, `.github/workflows/run.yml`
- `charter-practices/skills/tracker/SKILL.md`
- `docs/contract.md`, `docs/product.md`, `docs/decisions.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/run-from-an-issue.md`, `plans/run-from-an-issue.md`
- `tests/test_run.py`, `tests/test_setup.py`, `tests/test_workflows.py`, `tests/test_boundary.py`

## Tests

`tests/test_run.py`, new, with the classes `Workflow`, `Ready`, `Brief`, `Result`, `Publish`, `Outcome`,
`Setup`, and `Documents`, and the tests that the intent names. The commands of `charter_run.py` run on
files in a temporary folder; `result` runs in a real git repo of a temporary folder. The steps
"Publish the change request" and "Write the outcome on the issue" run with `bash -e`, a fake `gh`, and
a fake `git` that record their arguments. A test of `tests/test_setup.py` or `tests/test_workflows.py`
that lists the written files or the commands of `charter/bin` takes the new ones.
