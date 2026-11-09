# Plan: a mention of an issue in the text of a change request is not a link (#67)

Intent: `intents/code-host.md`, check 1. Accepted by the leader in the conversation on 2026-11-09, before
the code.

## Decision

The issue names a new intent, `intents/linked-issues.md`. The fix is one rule of the collecting script,
which `intents/code-host.md` owns (its check 1 names the test of the issue numbers). The issue line
changes to `Intent: intents/code-host.md`; no new intent, no Plan-phase change request. The link form
without a closing keyword ("Part of #N") stays out, as the issue says.

## Steps

1. `charter/scripts/charter_facts_github.py`: the pattern of a linked issue is a closing keyword of the
   code host (`close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`;
   case does not matter; an optional colon) followed by `#N`. `issue_numbers` keeps its name and its
   order, each number once. A bare `#N` is a mention and is not read. The list `linked_issues` of the
   facts file keeps its shape, so the gates `link` and `plan` do not change.
2. `charter/scripts/charter_gate.py`: the reasons of the gate `link` say "links" where they said
   "references", so that the reason names the rule.
3. `tests/test_charter_facts_github.py`, class `Text`: `test_issue_numbers_in_order_each_once` takes a
   text with closing keywords; new `test_a_mention_is_not_a_link`: "Closes #4. The re-run of #81 replaces
   this table. Fixes: #5. resolved #6. See #7." gives `[4, 5, 6]`.
4. `intents/code-host.md`: check 1 says "the issues that the text links with a closing keyword" and
   names the new test; one bullet in the scope records the finding (2026-10-29, an adopter: a complete
   change request was "not ready" because one sentence named a later issue).
5. `AGENTS.md` and `charter/templates/AGENTS.md`: "Open a change request that closes the issue:
   `Closes #N`" where they say "that references the issue".
6. `docs/contract.md`: the row of the gate `link` and the paragraph on the facts file say what links an
   issue and what does not.
7. One change request, `Closes #67`, with the line `No document change: the product does not change;
   the form of the link was already `Closes #N` in the tracker skill`. No version change: see the plan of #70.

## Files

`charter/scripts/charter_facts_github.py`, `charter/scripts/charter_gate.py`,
`tests/test_charter_facts_github.py`, `intents/code-host.md`, `AGENTS.md`, `charter/templates/AGENTS.md`,
`docs/contract.md`, and this file.

## Tests

One new test and one changed test, step 3.
