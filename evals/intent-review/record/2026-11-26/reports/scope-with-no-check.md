<!-- charter-intent-review -->
Commit: 7a4d6b0c4b85110e682ec26ac2be072340e75d7a

This is the first report. I could not read epic #13 or issues #66 and #82, so I checked decisions against `docs/decisions.md`.

| Intent | Verdict | Finding |
|---|---|---|
| `intents/code-reviewer.md` | needs discussion | It conflicts with decisions D7 and C7, check 5 does not prove that the two reviews stay apart, and the blocking and finding-line rules are incomplete. Also, no check proves that the depth comes from the base branch's contract: checks 1 and 15 would still pass if the workflow read the change request's `charter.toml`, so check 1 should assert the base-branch read. |

**1. high: `intents/code-reviewer.md`, "Built-in first"**
D7 says: "Review uses the built-in code review and security review. Charter has no review skill." The intent adds one without naming or replacing D7. The skill also checks correctness and security, so it does not only cover what the built-ins miss. Eval cases are also deferred, although F2 requires three for each skill.
Change: "So the checklist of Charter covers what the built-in does not, and `docs/contract.md` says that a repo can run the built-in review beside it."
To: "The checklist adds the checks against the intent and the plan, and a severity line; it also covers correctness and, at depth `deep`, security. `docs/decisions.md` replaces D7 with a decision that says so and records when the eval cases that F2 requires follow. `docs/contract.md` says that a repo can run the built-in review beside it." The leader decides this, and the plan adds the file.

**2. high: `intents/code-reviewer.md`, check 3**
This repo's workflow reads the skill from the change request. With `code_blocks` true, a change can rewrite the checklist whose severity line gates it. C7 says a change must not change its own gate.
Change: "The workflow of this repo follows the template, but for the place of the skill and the address of Charter."
To: "The workflow of this repo follows the template, but for the way to Charter: it takes the skill and the scripts from the base branch." Update the prompt, header comment and test to match. Also state that the workflow file still comes from the change request.

**3. high: `intents/code-reviewer.md`, check 5**
`review_reports` and `report_commit` accept a marker anywhere in a comment from the workflow account. An intent report that quotes the code-review marker therefore counts as a code report. Its commit and severity lines could satisfy the gate. The reverse can also happen. The test uses no cross-quoted marker.
Change: "and keeps the reports of the two reviews apart."
To: "and keeps the reports of the two reviews apart: a comment is a report of a review only when it begins with that review's marker, also when it quotes the other one." Require this in the collector and add the case to `test_the_two_reviews_stay_apart`.

**4. medium: `intents/code-reviewer.md`, "In scope", `review.code_blocks`**
The intent gives three blocking conditions. The plan, `docs/contract.md` and the code also block on missing code-review facts and on a report without a severity line.
Change: "With `true`, the verdict is not ready while a finding at `review.threshold` or above is open, while a change of code has no report, and while the newest report names another commit than the head commit"
To: "With `true`, a change of code is not ready in four cases: the facts hold no code review; no report exists; the newest report is open at `review.threshold` or above, or has no severity line; or it names another commit than the head commit". Add the two missing cases to check 8.

**5. medium: `intents/code-reviewer.md`, "In scope", finding lines**
No check covers how dropped or false code findings are recorded. `docs/contract.md` still assigns both record fields to the intent reviewer, and `AGENTS.md` describes these lines only for that reviewer. The fields do not identify the reviewer, although the leader needs this evidence when judging the code reviewer's shadow period.
Change: "The lines `Dropped finding: <reason>` and `False finding: <reason>` hold for the reviewer of the code too."
To: "The lines `Dropped finding: <reason>` and `False finding: <reason>` hold for the reviewer of the code too; each reason names the reviewer and the finding. `AGENTS.md`, its template and the record fields in `docs/contract.md` say so." Add an automatic check, with a named test, that a code-review reason reaches the record and that these documents cover both reviewers.

Highest open severity: high