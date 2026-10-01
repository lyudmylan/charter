---
name: review-loop
description: Runs the author side of the review loop on a change request. After each push it waits for the intent reviewer, answers each finding (a correction, or a dropped finding with a reason), pushes, and repeats until the stop rule of the contract ends the loop; then it reports one line to the leader. Use when a change request that touches intents/ is open and the user asks to run the loop, or after the push of such a change request. Do not use for the review itself, for a change request without intents, or after the loop has ended.
---

# Review loop, author side

You are the author. The reviewer is another agent, in CI; it posts one comment that begins with
`<!-- charter-intent-review -->` and ends with `Highest open severity: <level>`. The contract gives
the stop rule: `review.threshold` (default `medium`) and `limits.review_loop`. Read both with
`python3 charter/scripts/charter_check.py check charter.toml --json`, or from the installed plugin's
scripts when this repo has none.

## One round

1. Wait for the reviewer: `gh pr checks <number> --watch`. Then read its comment:
   `gh api repos/<owner>/<repo>/issues/<number>/comments --jq '.[] | select(.body | startswith("<!-- charter-intent-review -->")) | .body'`.
2. Decide each finding at the threshold or above, in the order of the report:
   - correct: change the intent, in the smallest way that answers the finding;
   - drop: when the finding contradicts a decision of the leader or a fact of the code, add one line
     `Dropped finding: <reason>` to the text of the change request with `gh pr edit <number> --body-file`;
     name the finding in the reason, so that the reviewer and the leader recognize it.
   A finding below the threshold: correct it when it is one line of work; else leave it.
   Mark nothing as false: only the leader writes `False finding: <reason>`.
3. Run the two commands of `AGENTS.md` ("Before a push"). Commit: `Answer the findings of review
   round <n>`. Push. The reviewer runs again on the push.

## The stop rule

The loop ends when the report's highest open severity is below the threshold, or when the rounds reach
the limit. Count the rounds as the reviewer's completed runs on this change request; the verdict prints
them: `review loop: round <n> of <limit>`. Do not push a round beyond the limit.

## The report to the leader

One line, no more: the rounds, the highest open severity at the end, how many findings were corrected
and how many dropped, and what the leader does now: "merge when ready", or "the limit is reached: <k>
findings are open, decide". The details are on the change request, not in the conversation.
