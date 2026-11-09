# Plan: a change request of the Plan phase links its issue with `Part of #N` (#76)

Intent: `intents/code-host.md`, check 2. Accepted by the leader in the conversation on 2026-11-09, before the
code. This file replaces the plan of #67, which stays in the history and in change request #73.

## Steps

1. `charter/scripts/charter_facts_github.py`: the pattern of a linked issue gains the form `Part of #N`,
   in any case, with an optional colon. It links the issue and does not close it on the merge: the code
   host knows no such keyword. The list `linked_issues` keeps its shape; the gates `link` and `plan` do
   not change. A bare `#N` stays a mention.
2. `tests/test_charter_facts_github.py`, class `Text`: `test_a_mention_is_not_a_link` keeps its cases, and
   `Part of #8` now links; new `test_part_of_links_the_issue`: "Part of #8. part of: #9. See #7." gives
   `[8, 9]`.
3. `intents/code-host.md`: check 2 names the second form and the new test; the out-of-scope line on
   "Part of #N" goes, and one bullet in the scope records the gap (2026-11-09, #76: a change request of
   the Plan phase had no link form that does not close its issue).
4. `AGENTS.md` and `charter/templates/AGENTS.md`: "Open a change request that closes the issue,
   `Closes #N`, or that is a part of it, `Part of #N`, for the intent of the Plan phase."
   `charter-practices/skills/tracker/SKILL.md`: the same two forms in "Changes and closing"; the skill
   stays under 40 lines.
5. `docs/contract.md`: the row of the gate `link` and the paragraph on the facts file name the second
   form and what it is for.
6. Both manifests: 0.3.4. After the merge the leader pushes the tags `charter--v0.3.4` and
   `charter-practices--v0.3.4`.
7. One change request, `Closes #76`, with the line `No document change: the product does not change; a
   second link form in the collecting script`.

## Files

`charter/scripts/charter_facts_github.py`, `tests/test_charter_facts_github.py`, `intents/code-host.md`,
`AGENTS.md`, `charter/templates/AGENTS.md`, `charter-practices/skills/tracker/SKILL.md`,
`docs/contract.md`, the two manifests, and this file.

## Tests

One new test and one changed test, step 2.
