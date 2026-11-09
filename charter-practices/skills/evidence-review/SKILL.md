---
name: evidence-review
description: Reviews a reading that an agent drafted for a person, a judgment on evidence such as the error analysis of an eval round, with two fresh agents that are not the author, and hands the person one list of disagreements with the evidence on each side. Use when a manual check carries the clause "drafted by the agent, reviewed by an agent that is not the author", before the draft reaches the person. Do not use for a review of intents or of code, for the writing of the draft, or after the person has read the draft.
---

# Evidence review

You are the author of a draft: a judgment on evidence, item by item, that a person will confirm. The
person reads the disagreements, not the whole draft (decision C11). Run two passes, each as a fresh
agent with no memory of your session, in the session of the author, not in CI.

## The two passes

1. Blind pass. Give the agent the evidence and the question, item by item, and not your draft. It writes
   its own reading per item, in the same form as yours.
2. Adversarial pass. Give the agent your draft and the evidence. It looks for items where the author is
   wrong, too kind, or too harsh, and for a proposed fix that hides a problem instead of solving it.

Each finding carries a severity of the intent review: `blocker`, `high`, `medium`, or `low`.

## The list of disagreements

Compare the three readings per item. Where you accept a finding, correct the draft and say so in one
line. Where you keep your reading, the item is a disagreement: your reading, the other reading, the
evidence on each side, the severity. Put the list in the text of the change request under the heading
`## Disagreements`, by severity, so that it stays with the change as evidence. An empty list says so.

## What the person does

The person decides each disagreement and confirms the rest in one word. A decision that changes an item
goes into the draft before the merge. Mark nothing as confirmed yourself.
