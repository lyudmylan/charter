<!-- charter-intent-review -->
Commit: ce5f97cf41d5dd1be8128a26b6b28df47aff8668

## Changed since the last report

- `intents/update-a-repo.md`:
  - The scope now also refuses a contract whose version line cannot be changed, and says a refusal comes before the first write.
  - Check 5 adds that case and a version that is not a row of numbers.
  - Check 8 names the step "update of a repo".
  - Check 9 says it follows the merge, and that a failure opens a new issue.
- `plans/update-a-repo.md`: no change.

## Table

| File | Verdict | Finding |
|---|---|---|
| `intents/update-a-repo.md` | approve with a change | The new scope line agrees with `charter_update.py`, and both earlier findings are fixed. The test named by check 5 cannot show that the newer-contract refusal comes before generated files are written. |
| `plans/update-a-repo.md` | approve | no finding |

## Findings in detail

1. **medium**, `intents/update-a-repo.md`, check 5: "Nothing to change after an update; a newer contract and a version line that cannot be changed are refused before the first write; a folder with no contract and a version that is no row of numbers cannot run."
   - In `test_the_command_refuses_and_ends`, the newer-contract case runs right after successful updates, so every generated file already has the new text. `generated()` skips files that match. If the command updated generated files before this refusal, the file comparison would still pass.
   - The version-line case does prove the order, because the test first adds a hand-written line to `verdict.yml`. The code now returns before any write in both refusal cases, so the gap is in what the check proves. I found this by reading the code and test; I did not run the test.
   - Proposed text: "Nothing to change after an update; a newer contract and a version line that cannot be changed are each refused while a generated file differs from the new version, and no file changes; a folder with no contract and a version that is no row of numbers cannot run."
   - The named test should then add its hand-written line before the `99.0.0` case.

Limit of this review: `gh issue list` returned no output, so I checked no milestone epic. I did read work item #97.

Highest open severity: medium