<!-- charter-intent-review -->
Commit: 874ecf1aa22eefbed8e9b2869782b62522d9d4a1

| Intent | Verdict | Finding |
|---|---|---|
| `intents/review-rounds.md` | needs discussion | It leaves statements in older done intents, `docs/contract.md` and the `verdict` workflow wrong. It also does not say what happens after a loop ends at the limit with a finding still open. |
| `intents/reviewer-reads-the-diff-of-a-round.md` | needs discussion | A report that the last step rejects stays on the change request. It is still counted as a round and can be the base of the next diff. |

**1. high: `intents/reviewer-reads-the-diff-of-a-round.md`**
Sentence: "The workflow gives the identifier to the reviewer, and its last step fails the run when the newest report does not hold that line."

The step runs after the comment is posted. `review_reports` counts every comment from the workflow account that has the marker, and does not read `Commit:`. `verdict` starts when `review-intents` completes, including after a failure.

So a rejected report counts as a round, and a rerun adds another. This can use up the limit. A rejected report with a severity below the threshold also closes the loop. The next run may read a missing or wrong `Commit:` line from it. This contradicts "a failed run is no round" in plan #61, step 6, and in `docs/contract.md`. The listed tests of the last step check whether the run passes, not what is counted afterwards.

Proposed text, added after that sentence: "When the step rejects the line, the script replaces the marker of that comment with `<!-- charter-intent-review-rejected -->` and keeps its text, so that neither the count nor the next diff reads it." Add an automatic check with a test for this, and give the step the one command it needs. The reviewer still changes no comment.

**2. medium: `intents/review-rounds.md`**
Sentence: "The reviewer posts a new comment for each run and changes no earlier one."

`intents/intent-reviewer.md` is marked done and still requires one comment, updated on each run, including in checks 4–6. `intents/review-loop.md` still says the collector counts completed workflow runs. The intents therefore give two conflicting rules.

Proposed text, added to In scope: "This replaces the one updated comment of `intents/intent-reviewer.md` and the count of runs of `intents/review-loop.md`; both intents get this change at those sentences and checks, with a pointer to this intent." Add both files to the plan.

**3. medium: `intents/review-rounds.md`**
Sentence: "`docs/contract.md`, section "The review loop": what a round is, and that each report stays."

The section "The intent reviewer", just above it, still says the reviewer "posts one comment". The change leaves that statement wrong.

Proposed text: "`docs/contract.md`, sections "The intent reviewer" and "The review loop": the reviewer posts a new comment at each run, what a round is, and that each report stays." Add the first section to plan step 6.

**4. medium: `intents/review-rounds.md`**
Sentence: "It asks the code host for no list of workflow runs."

`.github/workflows/verdict.yml` still grants `actions: read`, with the comment "the facts step lists the runs of the review workflow". The search of the workflows also covered `verdict.yml`, which neither the intent nor the plan lists for change. The template `charter/templates/verdict.yml` was not checked for this comment.

Proposed text, added after the sentence: "The workflow `verdict`, in the template and in this repo, loses the comment on that list, and the permission `actions: read` if no other step needs it." Add the files to the plan. A person must approve this change to high-tier files.

**5. low: `intents/review-rounds.md`**
Sentence: "The round is the number of the reports in the current loop."

If a loop reaches the limit with a finding still open and a person decides to go on, no new loop starts. The next report is round 4 of 3, even if it is the first review of a plan. Issue #61 asks for the plan's first review to have room in the count. Check 2 covers only an intent loop that closed.

Proposed text, added after the sentence: "A loop that reaches the limit while open does not start again: a later report counts above the limit until one is below the threshold, also when it is the first review of a plan."

Highest open severity: high