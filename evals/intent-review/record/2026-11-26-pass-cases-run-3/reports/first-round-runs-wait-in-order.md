<!-- charter-intent-review -->
Commit: a77a15d797a44a31dd6a5102dfa2af0ed46513b4

| File | Verdict | Finding |
|---|---|---|
| `intents/runs-wait-in-order.md` (read with `plans/runs-wait-in-order.md`) | approve with a change | The intent drops an in-scope item of #120, and no check proves that the stop switch stops a run that already waits. The Goal also promises more than the 100-run limit allows. |

**1. medium: `intents/runs-wait-in-order.md`, an item of the issue is missing**

#120 puts this in scope: "What the issue of a cancelled run shows. […] the intent finds it with a test on the code host." The intent lists it neither in scope nor out of scope, and has no result or check for it. The plan's test records nothing about it either. The change request text gives a result, "A cancelled run of this kind holds no job, so its issue got no comment", but the intent does not.

Add under "In scope": "What the issue of a cancelled run shows. By the test on the code host, a run that is cancelled while it waits holds no job, so its issue gets no comment. This change adds no comment for such a run." Add to check 3: "The results also show that each cancelled run held no job." Have step 1 of the plan record this, and confirm that the comment on #120 shows it.

**2. medium: `intents/runs-wait-in-order.md`, the stop switch for a waiting run has no proof**

The sentence is "The stop switch stays as it is: with the variable `CHARTER_RUNS` at `off`, a run that waited starts no job." Check 1 names a test of the workflow text, including the job condition. That test cannot show when the code host reads the variable for a run that is already waiting. Check 3 does not change the variable. I have not verified the host's behavior either way. This matters more now that up to 100 runs can wait.

Add a manual check: "4. On the code host, with a test workflow that has the option and the same job condition on a variable: set the variable to `off` while runs wait. Each run that waited starts no job. who: the leader, from the result of the test, which a comment on #120 holds with the address of each run. Not automatic: the check needs the code host." Add this test to step 1 of the plan. If a waiting run still starts its job, change the sentence in scope and handle the stop of waiting runs.

**3. medium: `intents/runs-wait-in-order.md`, the Goal and the limit disagree**

The Goal says "No run is cancelled because another one was started after it." The intent also says that up to 100 runs wait and that the code host cancels a run beyond its limit. The Goal also has two sentences, not one.

"Run number 101 of a group" is also unclear. If one run works and 100 can wait, the 101st run overall still fits.

- Replace the Goal with: "Each run that a person starts waits for its turn in the order in which it started to wait, and within the code host's limit of 100 waiting runs, a new run cancels none of them."
- Replace the last sentence of "Out of scope" with: "What the code host does with a further run when 100 runs of the group already wait: by its documentation, it cancels a run."

Before the merge, check in that documentation which run is cancelled, and name it in this sentence.

Highest open severity: medium