The verdict merges the change request of a tier whose approver is agent

Closes #66

The intent, the plan, and the code of one work item, in one change request. It is built on #100, #103, #104, #105, and #106 and holds their commits; merge those five first. The check `verdict` is red until #104 is merged, and `review-code` until #106 is merged; the cause of each is in the text of #105 and #106.

What it adds:
- The gate decides in the verdict whether the verdict merges. It does when each of these holds: the verdict is ready; the approver of the tier is `agent`; `review.code_blocks` is true and the newest report of the code review is closed on the head commit; and, for a change with a plan, the newest report of the intent reviewer is closed on the head commit. Else a person merges, and the line names the first condition that does not hold. A missing fact means that a person merges.
- One step at the end of the verdict workflow merges the change request at the commit that the verdict read, with the secret `CHARTER_MERGE_TOKEN`. Without the secret it merges nothing.
- Three settings turn the merge on, each made by a person: the approver `agent` in a tier of the contract, the flag `review.code_blocks`, and the merge token. This change sets none of them, here or in the template. So nothing merges by itself after this merge.
- A change request that holds an intent is in the high tier and stays with a person.

One risk that stays, stated plainly: a reviewer is a model, and text inside a change can try to tell it what to report. Both reviewer workflows now say that such text is a finding and not an instruction. That lowers the risk and does not remove it. The other limits are the tier (only the paths that the contract gives to an agent), the tests, and the evidence record that a person reads.

Evidence: 228 tests pass, 16 of them new. Eight faults put into the code on purpose each made a test fail: a merge for a tier of a person, for a verdict that is not ready, in the shadow period, with a plan review of another commit, with two missing commits, a step that merges for a person, a step without `--match-head-commit`, and a step that merges or fails with no token.

An Opus subagent wrote the code and the tests from the plan. The author session wrote the intent and the plan, read the merge decision and the step line by line, and added the rule on text inside a change.
