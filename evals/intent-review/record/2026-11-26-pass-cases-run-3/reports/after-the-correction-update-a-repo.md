<!-- charter-intent-review -->
Commit: e194a41d11367449e70ba5e591819e1a61236844

## Changed since the last report

- `intents/update-a-repo.md`:
  - In scope and check 5 now refuse a version line that cannot be changed, with each refusal before the first write.
  - Check 5 adds that a version that is no row of numbers cannot run.
  - Check 8 names the step "update of a repo".
  - Check 9 says that it follows the merge, and that a failure opens a new issue.
- `plans/update-a-repo.md`: no change.

Both findings of the last report are fixed. I read the tests and ran none. `gh issue list` returned nothing, so I read no milestone epic, only issue #97.

## Table

| File | Verdict | Finding |
|---|---|---|
| `intents/update-a-repo.md` | approve with a change | The test for check 5 cannot show that the newer-contract refusal comes before the first write. In scope also shows less of the difference than issue #97 asks for. |
| `plans/update-a-repo.md` | approve with a change | It sends the intent, plan and code to one merge, and does not say that this was a run with no person present. |

## Findings in detail

1. **medium**, `intents/update-a-repo.md`, check 5: "a newer contract and a version line that cannot be changed are refused before the first write".
   - In `Update.test_the_command_refuses_and_ends`, the newer-contract case follows a full update, so every generated file is already current. A command that wrote those files and then refused would leave them identical, and the test would pass.
   - The version-line case does prove the order, because it first adds a line by hand to `verdict.yml`. The script as written refuses a newer contract before any write; the gap is in the proof.
   - Proposed text, added after that clause: "for each refusal, the test starts with a generated file that the update would change". In the test, add the line to `verdict.yml` and take the file snapshot before the `99.0.0` run.

2. **low**, `intents/update-a-repo.md`, In scope: "A file that the repo changed by hand is written too, and the command prints the lines of the repo."
   - Issue #97 says that for a file with no content of the repo, the command "writes the file of the new version and shows the difference". The intent shows a difference only for a file changed by hand, between the old version and the repo. Other updated files get only their names, and the intent does not state this narrowing.
   - Proposed text, appended: "For other files the command prints no difference, which narrows issue #97; the person reads it in the working folder." The alternative is to change the issue.

3. **low**, `plans/update-a-repo.md`: "The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three."
   - `docs/product.md` says that a person approves the acceptance checks before the work starts, and that the plan is accepted before the code. Its exception for the plan covers a run with no person present. The plan does not say that this was such a run, and the exception does not mention the intent.
   - Proposed text: state when the leader accepted the intent and the plan. If they did not accept them before the code, write "They were not accepted before the code: <reason>", so that the leader decides knowingly.

Highest open severity: medium