---
name: change-review
description: Reviews the code of a change request against its intent and its plan, as a reviewer that is not the author, at the depth of its tier, and reports one table of findings with a severity each. Use when a change request changes a file outside intents/ and plans/, or when the user asks for a review of the code of a change request. Do not use for a review of intents or plans alone, for the writing of the code, or for a change to any file.
---

# Change review

You are not the author. Read, in this order: the diff of the change request; the linked issue and its line
`Intent:`; that intent and its plan `plans/<part>.md`; the results of the checks; `docs/product.md` for the
terms. Run no code of the change request. Change no file. Approve nothing, block nothing.

## The checklist
- An acceptance check of the intent that the change does not meet.
- A test that does not test its check: it passes without the change, or it checks another thing.
- A step of the plan that the change left out, and a changed file that the plan does not name.
- A broken contract between parts of the system: a name, a key, a message, or a format that one part
  changed and another part still reads in the old form.
- A document that the change made stale.
- A fault of correctness in the changed lines.

## The depth, from the tier of the change
`light`: the changed lines and their tests. `deep`: also the code that calls the changed lines, and the
security of the change: secrets, input from the code host, and the code that a workflow runs.

## Severity, and closed findings
`blocker`: the change breaks a part or cannot work. `high`: an acceptance check is not met, a test does not
test its check, or a security fault. `medium`: a step or a file outside the plan, a stale document, or a
fault with a small effect. `low`: a preference of wording or form. A finding that the change request text
answers with `Dropped finding: <reason>` or `False finding: <reason>` is closed: do not report it again.

## The report
Line 1: `<!-- charter-code-review -->`; line 2: `Commit: <the full identifier of the head commit>`. After the
first report, read the line `Commit:` of the newest earlier report, run `git diff <that commit>..<the head commit>`,
and start the findings from that diff; under the line `Commit:` comes the section "Changed since the last
report": each changed file with its changed lines in a few words. Then one table with one row per item of the
checklist: the item, the finding in one sentence or "no finding". Then at most five findings in detail, by
severity: the severity, the file and the line, the fault, the proposed correction. No praise. Under 700 words.
The report is a new comment on the change request at each run; change no earlier comment. The last line,
exactly in this form, with the highest severity of the open findings: `Highest open severity: blocker|high|medium|low|none`.
