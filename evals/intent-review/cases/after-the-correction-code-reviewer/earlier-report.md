<!-- charter-intent-review -->
Commit: a53480afcb1848e5955da5cc7b37bcacf06ceba3

## Changed since the last report
No earlier report exists on this change request. This is the first report. It covers the whole diff of `intents/` and `plans/` against the main branch. That diff holds the work items of #100, #103, #104, and #105 (stacked here), and the intent and plan of #95.

| File | Verdict | Finding |
|---|---|---|
| `intents/code-reviewer.md` (+ `plans/code-reviewer.md`) | approve with a change | Four things in scope have no acceptance check (finding 1). The goal holds two results (finding 2). |
| `intents/review-rounds.md`, `intents/reviewer-reads-the-diff-of-a-round.md` (+ plans) | approve | no finding |
| `intents/plan-tier.md`, `intents/plan-tier.plan.md` | approve | no finding. The plan stays at the old place, with a stated reason. |
| `intents/boundary-of-a-run.md`, `intents/boundary-gate-reads-any-path.md` (+ plans) | approve | no finding |
| `intents/plan-before-the-code.md` | approve | no finding. One pointer line to `plan-tier.md`. |
| moved plans (`plans/code-host.md`, `drafted-reading-review.md`, `intent-reviewer.md`, `plan-before-the-code.md`, `reason-next-to-the-part.md`, `setup-step.md`) | approve | no finding. Renames only. |

## Findings

1. **medium** — `intents/code-reviewer.md`, "Acceptance checks". Four things in scope have no check or test:
   - The depth is read "from the contract of the main branch". Check 15 proves only that `charter-gate tier` prints a tier and a depth. The reason for the command, that a change request cannot pick its own depth, is not proven. Plan step 4 builds it (`git show` of the base contract).
   - The lines `Dropped finding:` and `False finding:` hold for the code reviewer.
   - A later report starts from the diff since the commit of the report before it. Check 4 asks for the form only.
   - `docs/contract.md` names the workflow, the facts, the command `tier`, and that a repo can run the built-in review beside it. Only the field is checked (check 6).

   Proposed text, added after check 15: `16. The workflow reads the depth from the contract of the base branch, not from the head: a change request that edits its own tiers gets the depth of the base. test: tests/test_workflows.py::CodeReviewer.test_the_depth_comes_from_the_base_contract`. Add to check 4 that the skill names the diff for a later report and the two closed-finding lines. Add one check that `docs/contract.md` holds a section "The reviewer of the code" with the command `tier` and the built-in review. Renumber the manual checks.

2. **low** — `intents/code-reviewer.md`, "Goal". Sentence to change: "…gets a report from an agent that is not its author, under the rules of the review loop, and the contract says whether an open finding of that report makes the change request not ready." Proposed: "Each change request that changes a file outside `intents/` and `plans/` gets a report from an agent that is not its author, under the rules of the review loop." The flag is a means, and it is in scope and in checks 7 and 8.

3. **low** — `intents/code-reviewer.md`. The issue says "the evidence record holds the findings and each dropped one with its reason". The intent (check 10) says "the reports and the round". The change request text names only the missing eval cases as a difference from the issue. Say in scope that the dropped reasons stay in the text of the change request, or add them to check 10.

Highest open severity: medium
