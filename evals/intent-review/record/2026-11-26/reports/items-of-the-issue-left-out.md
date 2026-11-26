<!-- charter-intent-review -->
Commit: ae4e976cd5bd25ac5c9bff3919e51d809d1b01c4

| File | Verdict | Finding |
|---|---|---|
| `intents/run-from-an-issue.md` | needs discussion | It drops the settings check and two stop limits, and check 16 and the waiting rule fail as designed. It also omits two items of #92 without excluding them: the order of a new product's first work items, and a manual check that ends in a merged change (check 15 ends at the change request). |
| `plans/run-from-an-issue.md` | approve with a change | It omits the `.git` replacement. Its header also lets intent, plan and code be accepted in one merge, against D5 (checks approved before the code); `docs/decisions.md` records no such exception. |

**1. high**, `intents/run-from-an-issue.md`: the settings check is missing.
- Sentence: "The agent: `claude -p` with the brief, with the settings given on the command line as text, not as a file that the agent could change, with no list of allowed tools, with a limit of turns, and with a time limit of the step."
- Problem: #92 and E8 require the workflow to check that the run used the printed settings, and the boundary intent assigns this to #92. The intent has no such step or check, and neither has `run.yml`. Check 5 uses a fake `claude`, so it proves only which arguments are passed.
- Proposed addition: "After the agent, a script checks that the run used the settings of `charter-check boundary`; else the run is blocked." Name how it observes this, and add an automatic check with its test. If this cannot be observed, the leader changes E8 and excludes the check here.

**2. high**, same file: stop limits are missing.
- Sentence: "with a limit of turns, and with a time limit of the step."
- Problem: #92 requires the acceptance-loop, review-loop and refusal limits to hold in the run. A run answers no review findings, but the other two limits are neither in scope nor excluded. The brief says to run the quality commands "until they pass". The boundary intent defers the refusal count to later issues of #12.
- Proposed addition: "The brief tells the agent to stop and write `blocked.md` after `limits.acceptance_loop` failed runs or `limits.refusals` refusals in sequence", with a test. Any limit left for later goes under "Out of scope" with its issue, as a stated change to #92.

**3. high**, same file: check 16 cannot be done as written.
- Sentence: "The manual check 16 of `intents/boundary-of-a-run.md`, in that first run on a Linux runner, and three points more"
- Problem: that check needs the job log to name the refused write and network access. The agent step sends its JSON output to `agent.json`, and no step prints that file. The first run also builds an ordinary work item, and its brief forbids changing closed files. Nothing makes it attempt the forbidden actions.
- Proposed text: "Check 16 runs in a separate probe on a Linux runner, with the run's settings and a brief that asks for each forbidden action." Define the probe and the log or artifact that shows each refusal.

**4. high**, same file: a waiting run can be lost.
- Sentence: "One run works at a time; a second one waits."
- Problem: by default, the code host keeps only one pending run per concurrency group, and a newer one cancels it. `run.yml` sets the group for the whole workflow and triggers on every label. So a third start, or even an unrelated label, can cancel the waiting run. Its outcome step never runs. Check 1 only needs the group setting.
- Proposed text: "One run works at a time. A waiting run is not cancelled by another label. A later start either waits too or its cancellation is reported on the issue." Check this with a test of the grouping or queue setting.

**5. medium**, both files: the `.git` protection is missing.
- Sentences: "a script takes the folder `.charter-run/` out, commits what the agent left" (intent) and "`result --agent FILE --root DIR --base REF --issue FILE --out DIR`" (plan).
- Problem: the script and PR also replace the agent's `.git` with a copy made before the agent ran, and require `--git-dir`. Disabling hooks alone does not neutralize the rest of the agent's Git configuration. Check 4's text would pass without the replacement, although its test looks for `--git-dir`.
- Proposed text: in the intent, "a script first replaces `.git` with the copy made before the agent started", and add this requirement to check 4. In the plan, add `--git-dir DIR` and the copy and replace steps.

Highest open severity: high