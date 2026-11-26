An agent that is not the author reviews the code of a change request

Closes #95

The intent, the plan, and the code of one work item, in one change request. It is built on #100, #103, #104, and #105 and holds their commits; merge those four first.

Two checks of this change request are red until then, and both have a known cause:
- `verdict`: the plan is in `plans/`, and the verdict runs the gates of the main branch, which read the old place until #104 is merged.
- `review-code`, the new workflow: it takes the scripts of Charter from the main branch, and the main branch has no command `charter-gate tier` before this merge. Its first good run is on the first change request after the merge.

What it adds:
- A workflow `review-code`: on a change request with a file outside `intents/` and `plans/`, an agent that is not the author reads the diff, the intent, the plan, and the results of the checks, and posts one report at each run. It runs no code of the change request.
- A skill `change-review` with the checklist, two depths by the tier of the change, and the form of the report.
- The verdict prints one line for the review of the code. A field of the contract, `review.code_blocks`, decides whether it blocks. It is `false` here and in the template: the reviewer starts in its shadow period, reports, and blocks nothing. The leader ends the period with a change of the contract.
- With the flag, the verdict is not ready in four cases: no code review in the facts, no report, an open finding at the threshold or a report without a severity line, and a newest report that names another commit than the head commit.
- A command `charter-gate tier` gives the workflow the depth of the review from the contract of the base branch, so that a change request cannot pick its own depth.

Evidence: 210 tests pass, 22 of them new. Eight faults put into the code on purpose each made a test fail; the list is in the report of the author on the first commit of this work item.

An Opus subagent wrote the code and the tests from the plan. The author session wrote the intent and the plan, read the whole change, and merged the correction of #105 into it.

The intent differs from the issue in one place: it has no eval cases for the skill. They wait for the two defects of the eval cases, #79 and #80.
