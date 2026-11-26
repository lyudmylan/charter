<!-- charter-intent-review -->
Commit: 51f45157eeb8b3adffc54ed06a67474a1a150858

| File | Verdict | Finding |
|---|---|---|
| `intents/record-of-a-run.md` | needs discussion | The fields depart from work item #93 without saying so: there is no look at a real run, and tokens are dropped. The outcome rules also omit a case that the plan treats as `flawed`. |

Not read: issues #83 and #92 could not be opened, so this review does not check the epic's decisions. `docs/product.md` names no product test, so no scenario is asked for.

**1. high: `intents/record-of-a-run.md`, the fields of the run**
#93 says: "The intent names the fields after a look at a real run." It also lists tokens among what the runner reports. The intent fixes turns, duration and cost, reports no look at a real run, and neither includes tokens nor puts them out of scope. Check 8 says the first run is still needed. As a result, no check shows that these are the fields a real run reports.
Sentence to change: "A value that Claude Code did not report is written as `none`."
Proposed: keep it and add one of these:
- "The fields come from the result of a real run: <which run, what it reported>. Tokens are left out: <reason>."
- If there has been no real run: "This departs from #93: the fields are named before a look at a real run, and tokens are left out, because <reason>. Check 8 compares the fields with the result of the first run."

The leader decides whether to accept this departure. For the second option, check 8 also needs that comparison.

**2. medium: `intents/record-of-a-run.md`, the rules for `flawed` and `manual`**
Under the intent, `flawed` needs a verdict that is not ready or an open finding at the threshold. A ready change whose newest report has no severity line therefore reads as `success`. Plan step 4, `docs/contract.md` and `run_outcome` make it `flawed`, and check 3's test expects that too, although check 3 says "by the rules of the scope". They also give `manual` when the head commit is missing, which the intent does not say.
Sentence to change: "`flawed`: the head commit is the commit of the run, and the verdict is not ready or a reviewer has an open finding at the threshold, also in the shadow period of that reviewer;"
Proposed: "`flawed`: the head commit is the commit of the run, and the verdict is not ready, or the newest report of a reviewer is open at the threshold or has no severity line, also in the shadow period of that reviewer;". Add "and no such report" to the `success` rule. For `manual`, write "the head commit is missing or is not the commit of the run".

**3. low: `intents/record-of-a-run.md`, `success` before a review**
With no report yet, "no reviewer has an open finding" is true. A ready change whose code review is in its shadow period and has not reported, or has failed, can therefore be recorded as `success`.
Sentence to change: "`success`: the head commit is the commit of the run, the verdict is ready, and no reviewer has an open finding at the threshold;"
Proposed: add "A reviewer with no report counts as having no finding.", or define a different result if that is not what is meant.

**4. low: `intents/record-of-a-run.md`, a block that is not written**
In both workflow files, if reading the commit or writing the block fails, the change request is still published without the block. The verdict then prints "no agent run built this change request", which is false for that run. Neither the intent nor plan step 2 covers this case.
Sentence to change: "The publishing step of the workflow `run` adds it to the text of the change request: …"
Proposed: add "If the block cannot be written, the step still publishes and logs this; the record then holds no run, although a run built the change request."

Highest open severity: high