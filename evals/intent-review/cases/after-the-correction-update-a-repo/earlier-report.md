<!-- charter-intent-review -->
Commit: 75129092587c5e1c37c4a6e75a1737ff6acfa6e5

## Changed since the last report

No earlier report exists on change request #136. This is the first round, so the whole of `intents/update-a-repo.md` and `plans/update-a-repo.md` was reviewed.

## Table

| File | Verdict | Finding |
|---|---|---|
| `intents/update-a-repo.md` | approve with a change | The goal, scope, and automatic checks 1 to 7 are sound. Each check names a test, and the seven test functions exist in `tests/test_update.py`. Check 8 does not name the scenario of the product test. Check 9 cannot run before the merge. |
| `plans/update-a-repo.md` | approve | The steps, files, and tests match the intent: seven tests, and checks 1 to 9 are cited. No finding. |

## Findings in detail

1. **low**, `intents/update-a-repo.md`, check 8: "The installed command runs on a new repo and finds nothing to change. command: `python3 tests/product.py`".
   - The skill requires a work item that changes the behaviour of the product to name the scenario of the product test. Only the plan names it, as the step "update of a repo".
   - Proposed text: "The installed command runs on a new repo and finds nothing to change. command: `python3 tests/product.py`, step "update of a repo"." This also keeps the name in one place.

2. **low**, `intents/update-a-repo.md`, check 9: "Two adopters move from 0.3.20 to this version…".
   - The check needs a release that follows the merge, so the merge cannot depend on it. The intent does not say who decides if it fails, or that it follows the merge.
   - Proposed text, appended: "The check follows the merge; a failure opens a new issue and does not reopen this change request."

Both findings are below the threshold (medium).

Highest open severity: low
