<!-- charter-intent-review -->
Commit: aee44211ef61cd64194b2780450f9bd7b8d5f19a

| Intent | Verdict | Finding |
|---|---|---|
| `intents/sandbox-on-the-code-host.md` | approve with a change | The intent leaves out a limit of the sandbox that matters more with automatic approval. Checks 6 and 7 have gaps in their evidence or proof, and no product test scenario is named. |

`gh issue view 113` showed no milestone, and `gh issue list` returned nothing. I therefore checked no epic decisions; I used `docs/decisions.md`.

**1. medium**, `intents/sandbox-on-the-code-host.md`, In scope
- **Sentence:** "The limits of such a command are the limits of the sandbox, which the operating system holds: the closed files, the empty network, the tokens that leave the environment."
- **Problem:** Decision E9 says that on Linux the sandbox closes no file that does not exist yet. `docs/contract.md` says the same for new files that match some wildcard patterns. The intent says that a run refused commands outside the read-only set. With automatic approval, such a command now runs, so the shell may create a closed file that the sandbox does not cover. The gate still stops publication, but "closed files" does not state this limit.
- **Proposed text:** Add after it: "On Linux the sandbox does not close every path under `boundary.no_write` that does not exist yet (decision E9). A command with automatic approval can create such a file; the gate `boundary` then refuses the result, and nothing is published."

**2. medium**, same file, check 7
- **Sentence:** "The next agent run at an adopter, with this version, publishes a change request, or ends as blocked for a reason that is not the sandbox and not a refused approval."
- **Problem:** A run blocked before any shell command would pass. A published change request alone also does not show that the quality commands ran in the sandbox. The check therefore cannot show the goal at an adopter.
- **Proposed text:** "In the next agent run at an adopter, with this version, the agent runs the quality commands of the contract in its sandbox: they start, and neither the sandbox nor a refused approval stops them. A run that ends before these commands does not settle this check." Keep the `who:` line, and name the record that shows the commands ran. The intent leaves the record of each agent step to #83, so confirm that the leader has such a record.

**3. medium**, same file, Acceptance checks
- **Sentence:** "The settings hold `sandbox.autoAllowBashIfSandboxed` with the value true, also with an empty section of the boundary, and keep `allowUnsandboxedCommands` false and `failIfUnavailable` true."
- **Problem:** The work item changes the product's behaviour but names no product test scenario that shows the change. `tests/product.py` has no step that runs `charter-check boundary`.
- **Proposed text:** Add an automatic check: "The product test runs `charter-check boundary` in the new repo, and the printed settings hold `autoAllowBashIfSandboxed` true and `allowUnsandboxedCommands` false. command: `python3 tests/product.py`". Add that step to the product test.

**4. medium**, same file, check 6
- **Sentence:** "who: the leader, from the log of the test run that #113 names."
- **Problem:** The text of #113 that `gh issue view` returned names no test run and holds no results, including with `--json comments`. This also leaves "The results of the test are on #113" unconfirmed. The command may have omitted comments. The plan also deletes the test branch after the merge.
- **Proposed text:** "who: the leader, from the log of the test run <link to the run>; a comment on #113 holds the link and the result of each point of this check." If that comment already exists, confirm that it holds both.

**5. low**, same file, check 6
- **Sentence:** "an agent runs the tests of this repo, the two commands of a package manager, and a test that starts a child process and calls it on the loopback address."
- **Problem:** The package manager and its commands are not named. "The two commands" elsewhere in the intent means `charter-gate` and `charter-check`.
- **Proposed text:** Replace "the two commands of a package manager" with the two exact commands that the test ran.

Highest open severity: medium