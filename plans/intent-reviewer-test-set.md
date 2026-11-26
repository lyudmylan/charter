# Plan: the intent reviewer has a test set of real cases, and one command runs it (#140)

Intent: `intents/intent-reviewer-test-set.md`, checks 1 to 11.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. The source of the cases: each report of the intent reviewer on this repo and on the adopters, 133
   reports on 90 change requests. A newer report names its commit, so the state that the reviewer read can
   be made again.
2. The choice of the cases. `blocks`: a first report at the threshold whose finding the author corrected
   in the next commit, with no line `Dropped finding` for it, in a change request that the leader merged.
   `passes`: a merged state whose report was below the threshold. Seven change requests of this repo were
   one branch on the other; the base of such a case is the commit before its own first commit, so the case
   holds the intent of one work item.
3. `evals/intent-review/run.py`: the command. For each case it makes a repo in a temporary folder, copies
   the skill and the scripts next to it, writes the earlier report with the commit of the new repo, puts
   the stand-in for the command of the code host first on the path, and starts Claude Code with the prompt
   and the flags that it reads from `charter/templates/review-intents.yml`. The flags `--setting-sources
   project` and `--strict-mcp-config` keep the settings of the person out. A try with a local server in the
   place of the model showed that the instruction file of the person is in a request without the first
   flag and is not in a request with it.
4. The grader and the report, in the same file.
5. The cases of an adopter: its files at the base, and the files that the change moved, with the name of
   the product and of its owner replaced by a script, and without the licence files. A search of the
   folder for the names and for private text, by the author, before each push.
6. `tests/test_reviewer_eval.py`: a stand-in for Claude Code records how the command started it and
   answers with a fixed text. No test calls the model.
7. `docs/contract.md`, the section "The intent reviewer"; `docs/product.md`, the row "Test"; `README.md`,
   the table of the folders. `.gitignore`: the folder of the results of a run.
8. After the word of the leader: the full run, and its record in `evals/intent-review/record/`. Then the
   summaries of three cases for the leader, with the skill `evidence-review` before the leader reads them.

## Files

- `evals/intent-review/run.py`, `evals/intent-review/cases/` (25 folders), `evals/intent-review/record/`
- `tests/test_reviewer_eval.py`
- `docs/contract.md`, `docs/product.md`, `README.md`, `.gitignore`
- `intents/intent-reviewer-test-set.md`, `plans/intent-reviewer-test-set.md`

## Tests

- `tests/test_reviewer_eval.py`: `Workspace`, four tests; `TheRun`, five tests; `Grader`, two tests;
  `TheSet`, two tests.

## What the set does not show

The answer of a case comes from what the reviewer said then and from what the author and the leader did
with it. So the set measures whether the reviewer of today gives the same answer on the same change, and
whether it finds the same subject. A finding that the reviewer never gave is in no case. The read of three
cases by the leader, check 11, is the first measure from outside the reviewer.
