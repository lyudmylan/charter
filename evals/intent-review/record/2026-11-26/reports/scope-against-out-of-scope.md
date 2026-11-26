<!-- charter-intent-review -->
Commit: 7e9d4c725fa7b39e26dd669f30cac2c52b81a4ce

## Changed since the last report

- `intents/answer-findings.md`:
  - With no limit of rounds, the factory starts no answer. A new test in check 2 covers this.
  - The scope now says that the verdict line and the record name the number of agent runs.
  - A new bullet and check 6 mark each finding that an agent dropped. The verdict merges no change request that holds one. Check 6 has a new test for this.
- `plans/answer-findings.md`: step 2 adds the merge condition, step 4 adds the mark on dropped findings, and step 5 rewords the order of the job `decide`.

The three findings of the last report are fixed, including the one on the change request text. Epic #82 could not be read, so nothing was checked against it.

## Verdicts

| File | Verdict | Finding |
|---|---|---|
| `intents/answer-findings.md` | approve with a change | The new merge condition contradicts the out-of-scope line. The statement of what a person can start is wrong. |
| `plans/answer-findings.md` | approve with a change | Step 8 leaves out the documentation of the new merge condition. |

## Findings

1. **high**, `intents/answer-findings.md`, "Out of scope": "The merge by the verdict."
   The new scope bullet, check 6 and plan step 2 change the merge by the verdict. The out-of-scope line excludes it, and so does issue #118 ("The merge by the verdict, #13"). "The decisions of the leader" records no decision for this exception.
   Proposed text: "The merge by the verdict, except one condition: it merges no change request that holds a finding that an agent of a run dropped." The leader should confirm this exception, and a person should make issue #118 agree. If the leader has already decided it, add the decision and its date to the intent.

2. **medium**, `intents/answer-findings.md`, scope: "A person can start an answer in each case but the limit." Check 2 says: "a person starts one in each case but the limit."
   This is wrong. In `answer_state` and the code that calls it, a person skips only three conditions: the `factory` value, the presence of a limit in the contract, and an earlier answer for the head commit. A person still gets no answer while a reviewer's report is missing for the head commit or when no finding is open. The tests also expect no answer for a closed change request or a fork. The new no-limit sentence also makes "but the limit" unclear: it can mean a missing limit or a loop that has reached it. I missed this sentence in the last report.
   Proposed scope text: "A person can also start an answer without `factory`, without a limit of rounds in the contract, and for a head commit that has an answer. Each other condition holds for a person too, including that no open loop is at the limit."
   Proposed check 2 text: "The factory starts an answer only when the contract says so and holds a limit of rounds. A person needs neither, and can start a second answer for a commit; each other condition holds."

3. **low**, `plans/answer-findings.md`, step 8: "`docs/contract.md`: the field, the section "The answer to the findings of the reviewers", and the sum of the blocks in "The record of a run"."
   The change also adds the new condition to the section "The merge by the verdict", which the step does not name.
   Proposed text: "`docs/contract.md`: the field, the section "The answer to the findings of the reviewers", the new condition in "The merge by the verdict", and the sum of the blocks in "The record of a run"."

Highest open severity: high