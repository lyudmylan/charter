<!-- charter-intent-review -->
Commit: 31a2a3f5d5357350711ba36a009a3669c63246ad

| File | Verdict | Finding |
|---|---|---|
| `intents/runs-wait-in-order.md` | needs discussion | It drops an in-scope item of #120 without saying so. No check proves the stop-switch statement for a waiting run, and the queue limit is stated incompletely. |

**1. high: `intents/runs-wait-in-order.md`, In scope and Out of scope**

#120 puts in scope "What the issue of a cancelled run shows" and says that the intent finds it with a test on the code host. The intent has no scope line, check or exclusion for this. The change request text says that such a run "holds no job, so its issue got no comment", but the intent does not record this. Check 3, as written, does not test what an issue shows. Runs can still be cancelled, for example when the queue is full.

Proposed text, to add in scope after the defect: "What the issue of a cancelled run shows: a run that the code host cancels while it waits holds no job, so its issue gets no comment. Check 3 shows this." Extend check 3 to record that no job and no step ran in each cancelled run, with the evidence in the comment on #120. If the tests did not show this, run one that does. To drop the item instead, the leader must agree, and Out of scope and #120 must say so.

**2. medium: `intents/runs-wait-in-order.md`, the stop switch**

Sentence: "The stop switch stays as it is: with the variable `CHARTER_RUNS` at `off`, a run that waited starts no job."

No check proves this for a run that was already waiting when a person set the variable. The test named in check 1 covers the job condition in the workflow file. It cannot show when the code host reads the variable, and check 3 does not change the variable. This matters more when up to 100 runs can wait.

Proposed text, to add as a manual check: "4. On the code host, with one test run working and one waiting, the variable of the job condition is set to `off`; the waiting run then starts no job. who: the leader, from the address of each run in a comment on #120. Not automatic: the check needs the code host." Name this check in the plan too. Otherwise, limit the sentence to what is known and say that the case of a waiting run is not tested.

**3. medium: `intents/runs-wait-in-order.md`, Goal, queue limit**

Sentences: "Each run that a person starts works, one after the other, in the order of the start. No run is cancelled because another one was started after it." and "What the code host does with run number 101 of a group: it cancels it, by its documentation."

- The Goal has two sentences and no limit, although the scope allows only 100 waiting runs.
- If one run works and 100 wait, run number 101 is still one of those waiting. "Run number 101 of a group" is therefore wrong or unclear.
- `run.yml` starts on every `labeled` event. It sets concurrency for the whole workflow and checks the label only in the job condition. So a run for any other label also enters the group, and by this wiring it can take a place in the queue. "Up to 100 runs" does not mean 100 `charter-run` starts. The intent does not say this.

Proposed Goal: "While no more than 100 runs wait, each run that a person starts gets its turn, one at a time, in the order in which it started to wait, and no later run cancels it."

Proposed exclusion: "A run that arrives when the queue is full: the limit and what happens beyond it are those of the code host's documentation." Proposed scope addition: "A run for any other label enters the same group and counts toward the limit until it ends."

**4. low: `intents/runs-wait-in-order.md`, check 3**

Plan step 1 has the test results copied to a comment on #120 but does not say who writes it. If the agent drafts the result that the leader confirms, add: "drafted by the agent, reviewed by an agent that is not the author, confirmed by the leader."

I could not check that comment: the issue output I received showed no comments. I also did not check the code host's documentation, and I could not read epic #82 because it is not available here.

Highest open severity: high