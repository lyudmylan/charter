<!-- charter-intent-review -->
Commit: f4d5461dd20348435bfb0d753853c29ddc130782

| Intent | Verdict | Finding |
|---|---|---|
| `intents/runs-wait-in-order.md` | needs discussion | It drops a scope item of #120 about cancelled runs. The Goal, the queue limit and the stop switch also claim more than the intent and its checks show. |

**1. high: `intents/runs-wait-in-order.md`, "In scope" and "Acceptance checks"**
#120 puts this in scope: "What the issue of a cancelled run shows. The documentation does not say whether a step of such a run works, so the intent finds it with a test on the code host." The intent has no such item, check or exclusion, and the plan has no such step. The change request says "Closes #120" and that such a run "holds no job, so its issue got no comment", but the intent records no test of this. Run 101 is still cancelled. `docs/contract.md` also promises an outcome comment "in each case".
Add to "In scope": "What the issue of a cancelled run shows: <result of the test on the code host, with its date>; `docs/contract.md` says it beside the limit of 100." Add a manual check naming the leader, the test run and why it is not automatic. If the item is dropped instead, change the issue and state the exclusion and its reason under "Out of scope".

**2. medium: same file, "Goal"**
"Each run that a person starts works, one after the other, in the order of the start. No run is cancelled because another one was started after it." This is two sentences. The first also conflicts with "Out of scope", where run 101 is cancelled; a stopped run does not work either.
Proposed: "While no more than 100 runs wait and the stop switch is not `off`, each run that a person starts works in its turn, and no later start cancels it."

**3. medium: same file, "Up to 100 runs then wait, in the order in which they started to wait."**
The workflow starts on every `issues: labeled` event. The group is set for the whole workflow, while the label filter is on the job. So a run started by any other label on any issue should also enter `charter-run`. Without the option, it could cancel a waiting run. With the option, it could take one of the 100 places, even though its job is skipped. This follows from the workflow file; I did not test it on the code host. Check 3 does not cover this case.
Proposed addition: "A run of any other label also enters the group and counts toward the 100 while it waits." Confirm this on the code host, and say the same in `docs/contract.md`. Changing where the group is set would be a separate scope decision.

**4. medium: same file, "with the variable `CHARTER_RUNS` at `off`, a run that waited starts no job."**
No check proves this for a person who sets `off` after a run is already waiting. The test for check 1 evaluates the job's `if` with values it supplies itself. It cannot show when the code host reads the variable. Check 3 does not use the switch. If the value is read when the run is queued, up to 100 waiting runs could still start. This would contradict E12, "stops the start of every run".
Proposed check: "On the code host, a run waits, the variable that its job's `if` reads is then set to `off`, and the run starts no job. who: the leader. Not automatic: the check needs the code host."

**5. medium: same file, check 3, "who: the leader, from the results of the two tests, which a comment on #120 holds"**
The check does not say who drafts the reading of the results. Plan step 1 has the results copied to the comment, also without naming who does it. The change request says the evidence is already there, but my view of #120 showed no comment, so I could not verify it.
If the agent drafted it, replace "who: the leader" with "drafted by the agent, reviewed by an agent that is not the author, confirmed by the leader", and keep the source of the results and the reason it is not automatic.

Highest open severity: high