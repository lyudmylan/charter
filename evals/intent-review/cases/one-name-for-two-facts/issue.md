#61 A round of the review loop is a review that the author answered, not every run of the reviewer

## What we want

The collector counts every completed run of the reviewer workflow on the change request as a round. A push of one line after the loop closed starts another run, and the verdict prints `round 5 of 3` while the loop is closed (seen on #57). A round should be a review that the author answered with a push.

## Options

- Count only the runs that the author answered: the runs before the last commit that touched `intents/**`, or the runs whose report changed.
- Or let the reviewer write the round number from the previous report, and the collector read it.

## Decisions made

None yet. The stop rule works today, because the author side counts its own rounds.

## Seen in an adopter on 2026-11-20

The leader decided that a work item reaches her as one change request with the intent, the plan, and the code. On the first such change request:

- The intent alone used three runs of the reviewer, the limit. The push of the plan and the code started a fourth run, because the plan is a file that the reviewer reads. That run was the first review of the plan against the intent, and it gave a medium finding that was right. The count said 4 of 3, and the author had to stop.
- So the limit is used up by the intent before the plan exists. The plan is a second document with its own findings, and its first review needs a place in the count that the rounds of the intent do not use up.
- For about 40 seconds the evidence record said "round 3 of 3, highest open severity none: the loop is closed" while the newest report said "Highest open severity: medium". The cause is the order of the workflows: one verdict runs after `tests`, and a second one after the reviewer. The second verdict of that push printed "round 4 of 3, highest open severity medium" and updated the record (checked in the logs of the adopter on 2026-11-20). So the record was right in the end, and a reader who looks between the two verdicts sees the old state.

## In scope, added

- What a round is, for a change request that holds more than one reviewed document: the count per document, or the first review of a new document as no round. The intent decides.
- The skill `review-loop` reads the evidence record only after the verdict that follows the run of the reviewer, and says how the author sees that this verdict ran.
- The skill `review-loop`: right after a push the checks are not listed yet, and the skill says to wait and ask again.
- The template of an intent shows a test name of Python; it gets a form that does not name a language.

Intent: `intents/review-rounds.md`

-----

#86 The intent reviewer says what changed since its last round from the diff, not from its own report

## Goal
A report of the intent reviewer in a later round states what changed since the round before from the diff of the commits, not from memory of its own report.

Found on 2026-11-18 in the change request #85, round 3. The commit `90e838f` changed 12 lines of the intent: the form of the template, and the acceptance check 5. The report of round 3 said: "The text is the one that round 2 approved; the commit that followed changes no intent." The run had read the right commit. The verdict counted the round and closed the loop with no finding. A change of an approved intent can so pass a round that did not see it.

## In scope
- The instructions of the reviewer in `charter/templates/review-intents.yml` and in the workflow of this repo: in a round after the first, the reviewer reads the diff of `intents/` between the commit of its last report and the head, and its report names the changed lines or says that none changed.
- The commit that a report covers, written into the report, so that the next round can find it.
- A test of the template for both.

## Out of scope
- The stop rule and the count of the rounds: #61.
- A check by a script that the report agrees with the diff.

Intent: `intents/reviewer-reads-the-diff-of-a-round.md`
