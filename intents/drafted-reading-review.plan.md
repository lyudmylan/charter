# Plan: a reading that an agent drafts for a person is reviewed before the person reads it (#69)

Intent: `intents/drafted-reading-review.md`, checks 1 to 3. Accepted by the leader in the conversation on
2026-11-09, before the code.

## Steps

1. `docs/decisions.md`, section C: the row C11. Decision: "A reading that an agent drafts for a person
   (a manual check whose result is a judgment on evidence) reaches the person after a review by an agent
   that is not the author, as a list of disagreements with the evidence on each side; the person decides
   the disagreements and confirms the rest in one word." Reason: "B5: agents praise their own work. C2:
   approval of every item by a person is the bottleneck. C10: the person decides on a sample, and the
   disagreements are that sample." Date 2026-11-03.
2. `charter-practices/skills/evidence-review/SKILL.md`, under 40 lines: the front matter with when to use
   it and when not; the two passes as fresh agents in the session of the author (blind: the evidence and
   the question, not the draft; adversarial: the draft and the evidence, wrong, too kind, too harsh, fixes
   that hide a problem); a severity per finding, on the scale of the intent review; the author corrects
   what it accepts and merges the rest into one list "Disagreements" with the evidence on each side, in
   the text of the change request; the person decides each and confirms the rest in one word.
3. `charter-practices/skills/tracker/SKILL.md`: the clause of a drafted reading in the paragraph on the
   intent, and the name of the skill `evidence-review`; the skill stays under 40 lines, so one paragraph
   is compressed. `charter/templates/intent.md`: a manual check example with the clause.
   `charter-practices/skills/intent-review/SKILL.md`: the checklist asks for the clause when a manual
   check is a reading.
4. `tests/test_skills.py`: `EvidenceReviewSkill.test_size_and_description` and
   `EvidenceReviewSkill.test_the_two_passes_and_the_list`; `TrackerSkill.test_the_clause_of_a_drafted_reading`,
   which reads the skill `tracker`, the intent template, and the skill `intent-review`;
   `DraftedReadingRule.test_the_decision_is_recorded`, which reads `docs/decisions.md`.
5. `docs/product.md`, the Test row: "A reviewer that is not the author, also for a reading that an agent
   drafts for a person." `docs/contract.md`, the section on the intent reviewer: one sentence that names
   the skill `evidence-review` and what it does.
6. `intents/drafted-reading-review.md`: the status becomes done.
7. Both manifests: 0.3.3, so that an adopter can name the version that carries the skill. After the merge
   the leader pushes the tags `charter--v0.3.3` and `charter-practices--v0.3.3`.
8. One change request, `Closes #69`, with this intent, this plan, and steps 1 to 7. The plan first said
   two change requests, the intent alone first; but a change request of the Plan phase has no link form
   that does not close its issue (`Closes #N` closes it on the merge), so the link gate would refuse it.
   That gap has its own issue. The product document changes, so no `No document change` line.

## Files

`docs/decisions.md`, `charter-practices/skills/evidence-review/SKILL.md`,
`charter-practices/skills/tracker/SKILL.md`, `charter-practices/skills/intent-review/SKILL.md`,
`charter/templates/intent.md`, `tests/test_skills.py`, `docs/product.md`, `docs/contract.md`,
`intents/drafted-reading-review.md`, the two manifests, and this file.

## Tests

Four new tests, step 4. The skills have no eval case: the precedent of the skills `intent-review` and
`review-loop`, whose checks are the size, the description, and the fixed lines.
