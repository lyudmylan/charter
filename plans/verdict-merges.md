# Plan: the verdict merges the change request of a tier whose approver is `agent` (#66)

Intent: `intents/verdict-merges.md`, checks 1 to 10. Check 11 is manual, in an adopter repo.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan builds on #95: the facts and the state of the code review.

## Steps

1. `charter/scripts/charter_facts_github.py`: with the reviewer of intents named, the facts hold
   `review_commit`, the line `Commit:` of its newest report, read with the function that #95 added.
2. `charter/scripts/charter_gate.py`:
   - The fact `review_commit` is optional and validated as text or no value.
   - The value `agent` of an approver as a constant.
   - A function `merge_decision(facts, e, ready, spec)` that returns whether the verdict merges and the
     line. It checks the conditions of the intent in their order and names the first one that fails:
     not ready; the approver is no agent; `review.code_blocks` is not true; a file under `plans/` or
     `intents/` changed and the newest report of the intent reviewer is missing, is open at the
     threshold, has no severity line, or names another commit than `head_commit`.
   - `gate_verdict` adds the line after the line of the tier and puts the decision into the detail. The
     readiness does not change.
   - The evidence record holds `merge_by_verdict`.
3. `charter/templates/verdict.yml` and `.github/workflows/verdict.yml`: one step, "Merge, for a tier whose
   approver is agent", after the step that publishes the check. Its environment holds the secret
   `CHARTER_MERGE_TOKEN` as `GH_TOKEN`, the number of the change request, and the head commit of the
   verdict. The script reads `merge_by_verdict` from `record.json`. No record, or a value that is not
   true: it says that a person merges and ends well. True and no token: it says that the secret is not
   set and ends well. True and a token: `gh pr merge <number> --repo <repo> --merge --match-head-commit
   <commit>`; a refusal of the code host fails the step.
   The two reviewer workflows, `review-intents.yml` and `review-code.yml`, templates and this repo: two
   lines in the instructions say that the files and the text of the change request are data, and that a
   sentence in them that tells the reviewer what to report is a finding of severity high.
4. `charter/scripts/charter_setup.py`: the printed manual steps name the secret `CHARTER_MERGE_TOKEN` as
   optional, for a repo that gives a tier the approver `agent`.
5. `AGENTS.md` and `charter/templates/AGENTS.md`: in "How a change moves", "A person merges" becomes "The
   approver of the tier merges: a person, or the verdict for a tier whose approver is `agent`". In the
   section on the plan, one sentence: in a tier whose approver is `agent`, the review of the plan by the
   intent reviewer is its acceptance.
6. `docs/decisions.md`, section C: one row with the next free identifier, dated 2026-11-20. Decision: the
   verdict merges under the four conditions, and three settings of a person turn it on. Reason: autonomy
   is a grant by risk tier (B3, C10); each condition is a fact that a script reads; the author never
   merges, because the verdict runs from the main branch.
7. `docs/contract.md`: the row of `tiers.<tier>.approver`, a section "The merge by the verdict" after the
   section of the reviewer of the code, and the record table. `docs/product.md`, the Deploy row.
8. Both manifests: 0.3.11. `intents/verdict-merges.md`: `Status: done`.

## Files

- `charter/scripts/charter_facts_github.py`, `charter/scripts/charter_gate.py`,
  `charter/scripts/charter_setup.py`
- `charter/templates/verdict.yml`, `.github/workflows/verdict.yml`
- `charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`,
  `charter/templates/review-code.yml`, `.github/workflows/review-code.yml`
- `AGENTS.md`, `charter/templates/AGENTS.md`
- `docs/decisions.md`, `docs/contract.md`, `docs/product.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/verdict-merges.md`, `plans/verdict-merges.md`
- `tests/test_charter_gate.py`, `tests/test_charter_facts_github.py`, `tests/test_workflows.py`,
  `tests/test_setup.py`

## Tests

A class `VerdictMerges` in `tests/test_charter_gate.py` (eight tests), `tests/test_charter_facts_github.py`
(one), `tests/test_workflows.py` (five), and `tests/test_setup.py` (two), with the names that the intent
gives. The merge step is run with `bash -e` and a fake `gh` that records its arguments.
