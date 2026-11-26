A review round is a report in the current loop, and a later report starts from the diff

Closes #61
Closes #86

Two work items in one change request, each with its intent, its plan, and its code. Both change the workflow of the intent reviewer, and the second needs the first. The change request is built on #100, #103, and #104 and holds their commits; merge those three first.

The verdict of this change request is not ready until #104 is merged: the two plans are in `plans/`, and the verdict runs the gates of the main branch, which read the old place until then. After the merge of #104, start the workflow `verdict` again for this change request.

#61, the count of the rounds:
- The reviewer posts a new comment at each run, so each report stays on the change request.
- A round is a report in the current loop. A loop starts with the first report, and again with the first report after one with no finding at the threshold. The first review of a plan that arrives after the loop of its intent closed is round 1, not round 4.
- The facts collector reads the severity line of each report and asks for no list of workflow runs.
- The skill `review-loop` names the wait after a push and the verdict that follows the reviewer. The template of an intent names no language in its test line.

#86, the diff of a round:
- Each report holds the line `Commit:` with the head commit, and the last step of the workflow, a script, fails the run without it.
- A report after the first starts from the diff of `intents/` and `plans/` between the commit of the report before it and the head commit, and has a section "Changed since the last report".

Evidence: 188 tests pass, 20 of them new. Five faults put into the code on purpose each made a test fail: a count that never starts a new loop, a report without a severity line read as closed, a last step that passes with no new report, a last step that passes with another commit, and a collector that still lists the workflow runs.

An Opus subagent wrote the code and the tests from the two plans. The author session wrote the intents and the plans, read the whole change, and corrected one point: the diff ends at the head commit of the change request, not at the merge commit of the code host.

No document change: the product document says that a reviewer that is not the author works in a loop with a limit; what a round is belongs to `docs/contract.md`, which changes here.
