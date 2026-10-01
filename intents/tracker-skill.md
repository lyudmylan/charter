# Intent: the tracker skill, from the practice of iteration 1

Work item: #7. Approved by a person on 2026-10-01, in the work item.

## Goal

A light skill that structures work in the issue tracker the way this iteration did it.

## In scope

- A `SKILL.md` of 30 to 40 lines. It lives in this repo's `.claude/skills/` until the plugin `charter-practices` exists.
- Content: plan from one product document; look for existing items first; milestone, then epic (what we want to do), then issue (an actionable item); issue text with goal, in scope, out of scope, and acceptance checks; decisions are made in the conversation and recorded in the issue they belong to; each change to a source file has a ticket; the epic closes when its last issue closes.
- The skill reads the tool declaration from the contract.
- Three eval cases, one of them a control case where the skill must not act. Run with `claude plugin eval`. Verify that the tool works for a skill outside a plugin; if not, run the cases in this repo's tests.
- Written after the issues of this iteration are made: extraction from practice.

## Out of scope

- Any other practice skill.

## Acceptance checks

## Automatic checks

1. The skill is under 40 lines, and its description says when to use it and when not.
   test: `tests/test_skills.py::TrackerSkill.test_size_and_description`
2. The three eval cases pass with the skill, and the control case shows that the skill does not act on an
   unrelated request. command: `claude plugin eval charter-practices --trust-plugin --max-cost-usd 3`
   The second run of 2026-10-01, after the text of the skill changed: 3 of 3 cases pass, overall score
   1.0, the skill adds 0.56 on average, the control case is silent in 3 of 3 runs. Estimated cost at
   list price 1.59 USD, 394 seconds.

## Manual checks

3. The skill holds only knowledge that the model cannot have: the conventions of this organization, no
   general how-to text. who: the leader. Not automatic: a judgment on the text.
