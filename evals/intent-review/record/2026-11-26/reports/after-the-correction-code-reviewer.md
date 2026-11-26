<!-- charter-intent-review -->
Commit: 9fadb0b6e40d97b06eb14b400d0fe2ea1fa50eb9

## Changed since the last report
- `intents/code-reviewer.md`:
  - The goal drops the clause about the flag.
  - Scope now says where the dropped and false findings of both reviewers stay.
  - Check 4 adds the two closing lines and the diff for a later report.
  - Checks 16 (depth from the base contract) and 17 (section in `docs/contract.md`) are new.
  - The manual checks are now 18 and 19.
- `plans/code-reviewer.md`: the check numbers are now 1 to 17, with 18 and 19 manual. The test counts are now twelve for the gate and seven for the workflows.

| File | Verdict | Finding |
|---|---|---|
| `intents/code-reviewer.md` (+ `plans/code-reviewer.md`) | needs discussion | The new review skill contradicts decision D7, which this report's predecessor missed (finding 1). The named test does not prove one new clause of check 4 (finding 2). One term for the branch differs (finding 3). |

The three findings of the last report are addressed in the text. The one remaining test gap from its first finding is finding 2.

## Findings

1. **high**: `intents/code-reviewer.md`, "In scope". This finding does not come from this round's diff.
   - Sentence to change: "The checklist, a skill `change-review` of `charter-practices`."
   - Fault: D7 in `docs/decisions.md` says "Review uses the built-in code review and security review. Charter has no review skill." I found no row that replaces it. That file also says a decision changes only through a reviewed change to it. The "Built-in first" bullet gives a reason for the new skill but does not change D7, and neither the intent nor the plan lists the file.
   - Proposed text, added to "In scope": "`docs/decisions.md`: a new decision replaces the part of D7 that says that review uses the built-in reviews and that Charter has no review skill, with the reason under 'Built-in first'; the row D7 names the new decision. The two instruction lines of D7 stay."
   - Also add `docs/decisions.md` to the plan's steps and files, and add an acceptance check with a test for both rows. The leader decides whether to replace D7.

2. **medium**: `intents/code-reviewer.md`, check 4.
   - Clause: "the diff since the report before for a later report".
   - Fault: `test_the_skill_holds_the_checklist_and_the_form` checks for the two closing lines and the section title "Changed since the last report". It does not check the instruction to run the diff. The skill has that instruction, but the test would still pass if it were removed and the title stayed.
   - Proposed correction: keep the clause. Have the named test also require "`git diff <that commit>..<the head commit>`, and start the findings from that diff". Add this to the plan's description of the skill in step 7: "a later report starts its findings from the diff since the commit of the report before".

3. **low**: `intents/code-reviewer.md`, "In scope".
   - Sentence to change: "which the workflow reads from the contract of the main branch."
   - Proposed text: "which the workflow reads from the contract of the base branch." This matches check 16, plan step 4 and the new test.

Highest open severity: high