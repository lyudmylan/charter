<!-- charter-intent-review -->
Commit: 8ac2f55191c1b0f7f9ca32ea388f185c4750a415

| Intent | Verdict | Finding |
|---|---|---|
| `intents/reviewer-boundary.md` (with `plans/reviewer-boundary.md`) | needs discussion | The listed refusals and checks do not show that the reviewer reads and posts only what the goal allows. Parts of #131 and the product test scenario are missing, one list and one fact do not match the workflows, and the plan's order of acceptance conflicts with the rule. |

**1. high**: `intents/reviewer-boundary.md`, Goal and check 5.
- **Sentence:** "with the flags of the templates, each read and each command that a review needs passes, and each refused case is refused."
- **Problem:** The check does not name the refused cases, and the static tests of checks 1 to 4 cannot show behaviour. Two routes match no refused pattern:
  - `gh pr comment --body-file <path>` (or `-F <path>`) has `gh` read the file itself. #131 names this route.
  - `git diff` with a path outside the working tree works as `--no-index` without the flag. This is git's behaviour; I did not run it here.
- **Not shown:** The intent does not say whether Claude Code refuses these paths. `gh issue view 131` showed me no comment with the test record.
- **Proposed text:** "…each of these cases is refused: a read outside the two folders, by the read tools, by `git diff <outside path> <path>` and by `gh pr comment --body-file <path>` or `-F <path>`; each pattern of the refused list. `--body-file -` passes." Close any route that passes, or narrow the Goal and name the gap under Out of scope. "One report" also needs this, since `gh pr comment` can post any number of comments.

**2. medium**: `intents/reviewer-boundary.md`, In scope and Out of scope.
- **Sentence:** "A test through the action `claude-code-action`: it starts on no push of a branch. The test ran the program that the action runs, with the same flags."
- **Problem:** The test does not show what the action itself leaves in files the reviewer can read, so "No token is in a file that it can read" is unproven. #131 also asks for two things the intent silently omits: the official documentation page on what the action hides, and that later job steps run no file the reviewer could write.
- **Proposed text:** Add to the Out of scope line: "So what the action itself writes to files is not tested." Add to In scope: "The documentation of the action on what it hides from the tools: <page>. No later step of the job runs a file that the reviewer could write", with a check for the latter. If either is dropped, say why.

**3. medium**: `intents/reviewer-boundary.md`, Acceptance checks.
- **Sentence:** "4. The documents and both manifests carry the boundary."
- **Problem:** The work changes what the shipped reviewer workflows can do, and `charter.toml` names a product test. The intent names no scenario and does not say there is none.
- **Proposed text:** Name the scenario that shows the change. If there is none, add after the automatic checks: "The product test has no scenario for this change: <reason>, for example that it runs no reviewer workflow on the code host." Confirm that reason against `tests/product.py`, which I did not read.

**4. medium**: `intents/reviewer-boundary.md`, In scope.
- **Sentences:** "a list of refused patterns for the allowed commands: …" and "the folder of the Charter scripts, where the skill is".
- **Problem:**
  - All four workflows also refuse `Read(//proc/**)` and `Read(./.git/**)`, and the test requires both. The scope omits them. Check 2's "each with a space before its flag" cannot apply to them.
  - In this repo's two workflows, the prompt reads the skill from `charter-practices/skills/…` in the change's folder, not from the Charter scripts folder.
- **Proposed text:** Add "two refused reads: `//proc/**` and `./.git/**`". In check 2, write "each command pattern with a space before its flag". Write "the folder of the Charter scripts, where the templates find the skill; the workflows of this repo read it in the folder of the change".

**5. medium**: `plans/reviewer-boundary.md`, header.
- **Sentence:** "The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three."
- **Problem:** `AGENTS.md` requires an intent approved through a change request, and a plan accepted before the code. Its exception for a plan arriving with the code covers runs with no person present. Such a run cannot change `.github/**`, which this change does, and the plan records no earlier acceptance. This is a high-tier change.
- **Proposed text:** If the acceptance happened, write "<the holder of the work item> accepted this plan on <date>, before the code" and say where the intent was approved. If not, the leader needs to decide this before the merge, for example by taking the intent through its own change request first.

Highest open severity: high