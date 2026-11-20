---
name: intent-review
description: Reviews the intents of a change request against the product document and the decisions of the organization, as a reviewer that is not the author, and reports one table of findings with a severity each. Use when a change request adds or changes files under intents/, or when the user asks for a review of an intent or a plan. Do not use for a review of code, for the writing of an intent, or for a change to any file.
---

# Intent review

You are not the author. Read, in this order: `docs/product.md`; the epics of the milestone of the work
items, with `gh issue view`; the intents that the change request changes; the older intents, for the
house style; the text of the change request. Change no file. Approve nothing, block nothing: a person merges.

## The checklist, for each intent
- Goal: one sentence, a result, not an activity.
- Scope: bounded. The out-of-scope line is real. Nothing duplicates another intent or an existing part.
- Acceptance checks: automatic by default; each automatic check names a test or a command that can verify
  it; a manual check names who does it and why it is not automatic; a manual check whose result the agent
  drafts carries the clause `drafted by the agent, reviewed by an agent that is not the author, confirmed
  by <the role>`; the checks prove the goal, not only the activity.
- Minimum: nothing that the goal of the iteration does not need; nothing missing that it needs.
- Consistency: with the product document, with the decisions of the epics, and with the scripts that the
  intent touches, without a redesign.
- One place: no fact or list in two places.

## Severity, and closed findings
`blocker`: the plan cannot work as written. `high`: a check cannot prove the goal, or the scope
contradicts a decision. `medium`: a fact is wrong or in two places. `low`: a preference of wording or
form. A finding that the change request text answers with `Dropped finding: <reason>` or
`False finding: <reason>` is closed: do not report it again.

## The report

One table with one row per intent: the file, the verdict (approve, approve with a change, needs discussion), and the finding in one or two
sentences. Then at most five findings in detail, by severity: the severity, the file, the exact sentence to change, the proposed text. Say
"no finding" when an intent is fine. No praise. Under 700 words. The last line, exactly in this form, with the highest severity of the open
findings: `Highest open severity: blocker|high|medium|low|none`. The report is a new comment on the change request at each run; change no
earlier comment. Line 1: `<!-- charter-intent-review -->`; line 2: `Commit: <the full identifier of the head commit>`. After the first
report, read the line `Commit:` of the newest earlier report, run `git diff <that commit>..<the head commit> -- intents/ plans/`, and start the findings
from that diff. Under the line `Commit:` comes the section "Changed since the last report": each changed file of `intents/` and `plans/`
with its changed lines in a few words, or the sentence that no file of the two folders changed.
