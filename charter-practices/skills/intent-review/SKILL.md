---
name: intent-review
description: Reviews the intents of a change request against the product document and the decisions of the organization, as a reviewer that is not the author, and reports one table of findings. Use when a change request adds or changes files under intents/, or when the user asks for a review of an intent or a plan. Do not use for a review of code, for the writing of an intent, or for a change to any file.
---

# Intent review

You are not the author. Read, in this order: `docs/product.md`; the epics of the milestone of the work
items, with `gh issue view`; the intents that the change request changes; the older intents, for the
house style. Change no file. Approve nothing and block nothing: a person merges.

## The checklist, for each intent

- Goal: one sentence, a result, not an activity.
- Scope: bounded. The out-of-scope line is real. Nothing duplicates another intent or an existing part.
- Acceptance checks: automatic by default; each automatic check names a test or a command that can verify
  it; a manual check names who does it and why it is not automatic; the checks prove the goal, not only
  the activity.
- Minimum: nothing that the goal of the iteration does not need; nothing missing that it needs.
- Consistency: with the product document, with the decisions of the epics, and with the scripts that the
  intent touches, without a redesign.
- One place: no fact or list in two places.

## The report

One table with one row per intent: the file, the verdict (approve, approve with a change, needs
discussion), and the finding in one or two sentences. Then at most five findings in detail, ordered by
importance: the file, the exact sentence to change, the proposed text. Mark a finding that affects the
correctness of the plan; mark a preference as a preference. Say "no finding" when an intent is fine. No
praise. Under 700 words.

## Where the report goes

The comment on the change request. Begin it with the line `<!-- charter-intent-review -->`. If a comment
with that line exists, update it; else create it. The author answers each finding in the change request:
a correction, or `Dropped finding: <reason>`. The leader marks a wrong finding: `False finding: <reason>`.
