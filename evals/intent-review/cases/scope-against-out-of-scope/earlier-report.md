<!-- charter-intent-review -->
Commit: 402458b5270b0c8fe86bbeabb381662c9a621c36

## Changed since the last report

No earlier report exists. This is the first round; the whole of `intents/answer-findings.md` and `plans/answer-findings.md` is new.

## Verdicts

| File | Verdict | Finding |
|---|---|---|
| `intents/answer-findings.md` | approve with a change | Check 3 asks for the verdict and the record to name the number of runs, but the scope lists neither. Check 14 is manual and covers the one thing the automatic checks cannot prove. |
| `plans/answer-findings.md` | approve with a change | Step 2 says the line of the verdict and the record name `agent_runs`. The intent's scope does not say so. The plan otherwise follows the intent's checks 1 to 14. |

## Findings

1. **low**, `intents/answer-findings.md`, scope, the bullet "The facts collector": "and the fact `run` as the sum of the blocks of the text, one for the run and one for each answer."
   The verdict and the record that name the number of runs of an agent are in check 3 and in plan step 2, but not in the scope. They are a visible change of the product, and the out-of-scope line ("A line of the verdict on the state of the answer") sits close to them.
   Proposed text: add "The line of the verdict and the record of a run name the number of runs of an agent. This is a count, not the state of an answer." to that bullet.

2. **low**, `intents/answer-findings.md`, scope, the sentence "An answer starts for the open change request of a run of this repo, when each reviewer that takes part has its newest report on the head commit, a report is open at the threshold or has no severity line, ..."
   The text of the change request says "a report is open at the threshold" and leaves out "or has no severity line". Two descriptions of one rule differ. The rule is stated in the intent and in the tests, so the text of the change request should follow the intent.
   Proposed text: in the text of the change request, "a report is open at the threshold or has no severity line".

3. **low**, `plans/answer-findings.md`, step 5: "the job `decide`, after the job `run` in the file".
   A job that decides whether `run` starts is listed after `run` in the file. Say that this is only the order in the file, and that `run` needs `decide`, so no reader takes it for the order of the execution. If the order is not needed, drop the phrase.
   Proposed text: "the job `decide`, which `run` needs, written after it in the file".

## Checked, no finding

- Goal: one sentence, a result.
- Out-of-scope line: concrete and not in conflict with the scope.
- Checks 1 to 13: each names a test or a command. Check 12 names the product-test steps for the changed behaviour.
- Check 14: manual, with a named role and a reason it is not automatic.
- House style: the headings match the older intents.
- `docs/architecture.md` does not exist, so the rule on the row of a choice does not apply.

Highest open severity: low
