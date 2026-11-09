# Intent: a reading that an agent drafts for a person is reviewed before the person reads it

Work item: #69. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A reading that an agent drafts for a person reaches the person after a review by an agent that is not
the author, as a list of disagreements; the person decides the disagreements and confirms the rest in
one word.

## In scope

- The reading: a manual check whose result is a judgment on evidence, such as the error analysis of an
  eval round (per failed case: the gate, the case, the work) or the reading of what a number measures.
  The first case is the error analysis of an eval round in an adopter, where the agent drafts the
  false-fail table for the leader.
- The decision, in `docs/decisions.md`: the rule above with its reason. B5: agents praise their own
  work. C2: approval of every item by a person is the bottleneck. C10: the person decides on a sample,
  and the disagreements are that sample. The issue named section P; the leader accepted the rule on
  2026-11-03, so it enters section C as an accepted decision, C11.
- The form of the check, in the skill `tracker` and in `charter/templates/intent.md`: a manual check
  whose result the agent drafts carries the clause "drafted by the agent, reviewed by an agent that is
  not the author, confirmed by <the role>". The skill `intent-review` asks for the clause when a manual
  check is a reading.
- The review, as the skill `evidence-review` in `charter-practices`, under 40 lines, because the text
  does not fit in the skills `tracker` and `review-loop` at their size limit. Two passes by fresh agents
  in the session of the author: a blind pass, where the agent gets the evidence and the question but not
  the draft, and writes its own reading per item; an adversarial pass, where the agent gets the draft
  and the evidence, and looks for items where the author is wrong, too kind, or too harsh, and for fixes
  that hide a problem. Each finding carries a severity of the scale of the intent review. The author
  corrects what it accepts, and merges the rest into one list of disagreements with the evidence on each
  side, in the text of the change request, so that the evidence record holds it (C9). The person decides
  each disagreement and confirms the rest in one word.
- `docs/product.md`, the Test phase: the reviewer that is not the author also reviews a reading that an
  agent drafts for a person. `docs/contract.md` names the skill.

## Out of scope

A CI workflow for the review: the two passes run in the session of the author, and the intent reviewer
stays the only reviewer in CI. A change to the contract schema. A check of the content of a reading by
a gate.

## Acceptance checks

## Automatic checks

1. The skill `evidence-review` is under 40 lines, says when to use it and when not, and names the two
   passes, the severity, the list of disagreements with the evidence on each side, and the one-word
   confirmation.
   test: `tests/test_skills.py::EvidenceReviewSkill.test_size_and_description`
   test: `tests/test_skills.py::EvidenceReviewSkill.test_the_two_passes_and_the_list`
2. The skill `tracker` and the intent template carry the clause of a drafted reading, and the skill
   `intent-review` asks for it; the three skills stay under 40 lines.
   test: `tests/test_skills.py::TrackerSkill.test_the_clause_of_a_drafted_reading`
3. The decision record holds the rule as C11, accepted, with its reason.
   test: `tests/test_skills.py::DraftedReadingRule.test_the_decision_is_recorded`

## Manual checks

4. The first use, on the error analysis of an eval round in an adopter: the two passes run, the list of
   disagreements reaches the leader, and the leader decides them and confirms the rest in one word.
   who: the leader. Not automatic: the first case is in an adopter, outside this repo.
