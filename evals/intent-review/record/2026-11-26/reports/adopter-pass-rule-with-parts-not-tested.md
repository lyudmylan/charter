<!-- charter-intent-review -->
Commit: 964366e549d35064d5375197c451c30d9ec145da

| File | Verdict | Finding |
|---|---|---|
| `intents/product-test.md` | needs discussion | The intent adds a command that issue #3 leaves out of scope, and its checks miss several ways the test must fail. The function for unit tests and the separation from `pnpm test` are also unclear. |

The epic #5 could not be read, so consistency with its decisions is not checked.

**1. high** · `intents/product-test.md`, Goal and In scope
- **Sentence:** "The command is `node product-test/run.ts`."
- **Problem:** Issue #3 puts out of scope "A command of its own for this test, and the line in the contract: the next issue of this epic." The intent makes that command its goal and check 1. Its Out of scope defers only the contract line and the package script to #4.
- **Proposed text:** If the issue holds, replace the sentence with "The test of the product runs as the test `tests/product-test/run.test.ts`; a command of its own comes with #4." Then align the Goal, the command's output and exit codes, check 1 and the architecture row. If the command belongs here, the leader changes the scope of issue #3 so that only the contract line and the package script stay with #4.

**2. high** · `intents/product-test.md`, Automatic checks
- **Sentence:** "A scenario passes when each event got the answer 200, the messages equal the known answer in content and in order, and product ended with the exit code 0."
- **Problem:** No check covers an answer other than 200 or a non-zero exit of product. A test that ignores both passes all six checks. A rejected event could then pass the scenario that expects no message. The listed tests also need not check the command's exit code 1, so a command that reports "failed" but exits 0 could pass. Process cleanup after a failure is checked only for the missing address.
- **Proposed text:** Add checks with named tests:
  - "A scenario with an empty known answer whose event gets the answer 400 fails."
  - "A start command whose process writes its address, answers as expected and ends with the exit code 1 after SIGTERM makes the scenario fail."
  - "The command ends with the exit code 1 for a failed scenario and for an empty folder." The test must have a stated way to give the command another folder.
  - "After a scenario that failed on its answer or its messages, its process has ended."

**3. medium** · `intents/product-test.md`, In scope
- **Sentence:** "The code that runs one scenario is a function apart from the start of the command, so a unit test calls it with another folder of scenarios and with another start command."
- **Problem:** A function that runs one scenario does not take a folder, but checks 4 and 6 need folder-level behavior. Check 5 also needs a one-second limit, and the sentence gives no way to pass it.
- **Proposed text:** "The code that runs a folder of scenarios is a function apart from the start of the command. It takes the folder, the start command and the time limit for the address, and returns the result of each scenario, so a unit test can set all three."

**4. medium** · `intents/product-test.md`, In scope and check 2
- **Sentence:** "It is apart from the unit tests, and `pnpm test` does not run it."
- **Problem:** Check 2 is a test under `tests/` that reports both real scenarios as passed. `pnpm test` runs `vitest run`, so it would run them. Check 2 also repeats what check 1 proves.
- **Proposed text:** If the separation matters, remove check 2 and let check 1 say "The command runs the two scenarios of this work item, reports each as passed and ends with the exit code 0." If `pnpm test` should run them, delete the quoted sentence. Settle this together with finding 1.

Highest open severity: high