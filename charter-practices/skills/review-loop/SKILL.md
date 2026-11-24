---
name: review-loop
description: Runs the author side of the review loop on a change request. After each push it waits for the intent reviewer, answers each finding (a correction, or a dropped finding with a reason), pushes, and repeats until the stop rule of the contract ends the loop; then it reports one line to the leader. Use when a change request that touches intents/ is open and the user asks to run the loop, or after the push of such a change request. Do not use for the review itself, for a change request without intents, or after the loop has ended.
---

# Review loop, author side

You are the author. The reviewer is another agent, in CI; at each run it posts a new comment that begins with
`<!-- charter-intent-review -->` and ends with `Highest open severity: <level>`. The contract gives the stop rule: `review.threshold`
(default `medium`) and `limits.review_loop`. Read both with `python3 charter/scripts/charter_check.py check charter.toml --json`, or
from the installed plugin's scripts when this repo has none. On a branch `run/<number>`, which a run of an agent built, read `run.answer_start`
in the contract first: with `factory`, an agent of the factory answers the findings, so answer none and push nothing there; its comment on the
change request says what it did with each finding. With `person` or no value, answer here, or start it: `gh workflow run run.yml -f change_request=<number>`.

## One round

1. Wait for the reviewer: `gh pr checks <number> --watch`. Right after a push it can answer that no checks are reported: ask again. When
   the check `review-intents` fails, rerun it once, `gh run rerun <run-id>`; a failed run is no round. Then read the newest report:
   `gh api repos/<owner>/<repo>/issues/<number>/comments --jq '[.[] | select(.body | startswith("<!-- charter-intent-review -->"))] | last | .body'`.
2. Decide each finding at the threshold or above, in the order of the report:
   - correct: change the intent, in the smallest way that answers the finding;
   - drop: when the finding contradicts a decision of the leader or a fact of the code, add one line `Dropped finding: <reason>` to the
     text of the change request with `gh pr edit <number> --body-file`; name the finding in the reason, so that the reviewer and the leader recognize it.
   A finding below the threshold: correct it when it is one line of work; else leave it.
   Mark nothing as false: only the leader writes `False finding: <reason>`.
3. Run the two commands of `AGENTS.md` ("Before a push"). Commit: `Answer the findings of review round <n>`. Push. The reviewer runs again.

## The stop rule

The loop ends when the report's highest open severity is below the threshold, or when the rounds reach the limit. A round is a report in the
current loop: a loop starts with the first report, and again after a report below the threshold. The verdict prints the round:
`review loop: round <n> of <limit>`. Read the evidence record only after the verdict that follows the run of the reviewer: the time in the
record is later than the newest report. Do not push a round beyond the limit.

## The report to the leader

One line, no more: the rounds, the highest open severity at the end, how many findings were corrected
and how many dropped, and what the leader does now: "merge when ready", or "the limit is reached: <k>
findings are open, decide". The details are on the change request, not in the conversation.
