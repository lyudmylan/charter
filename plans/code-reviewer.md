# Plan: an agent that is not the author reviews the code of a change request (#95)

Intent: `intents/code-reviewer.md`, checks 1 to 17. Checks 18 and 19 are manual.
The leader decided on 2026-11-20 that the intent, the plan, and the code of a work item of this
milestone reach her in one change request; her merge is the acceptance of the three.
This plan builds on #61 and #86: each report is its own comment and names its commit.

## Steps

1. `charter/schema/contract.toml`: the field `review.code_blocks`, kind `flag`, with a note.
   `charter.toml` and `charter/templates/charter.toml`: `code_blocks = false` in the table `[review]`,
   with a comment that the reviewer of the code is in its shadow period.
2. `charter/scripts/charter_facts_github.py`:
   - The marker `<!-- charter-code-review -->` as a constant. `review_reports` takes the marker, so one
     function reads both kinds of report.
   - A function that reads the line `Commit:` of the newest report of a kind.
   - A new option `--code-review-workflow FILE`, the switch that the repo has the reviewer of the code.
     With it the facts hold `code_review_reports` and `code_review_commit`. The facts hold the head
     commit that they describe under `head_commit`.
3. `charter/scripts/charter_gate.py`:
   - The three facts are optional and validated.
   - A function `is_code(path)`: a path outside `intents/` and `plans/`.
   - A function `code_review_state(facts, e)` that returns the line of the verdict and whether it
     blocks. No changed file is code: the line says that no review of code is needed. The facts hold no
     code review: the line says so. Else the round comes from `current_round`, the state from the newest
     severity, and the words of the three states are the ones of the intent review, with the name of the
     code review in front. It blocks only when `review.code_blocks` is true, and then in four cases: the
     facts hold no code review, no report exists, the newest report is open at the threshold or has no
     severity line, or `code_review_commit` is not `head_commit`.
   - `gate_verdict` adds the line, and is not ready when the state blocks.
   - The evidence record holds `code_review_reports`, the round, and the newest severity.
   - A command `tier --contract C --changed FILE [--repo-only]`: it reads the list with `changed_paths`,
     and prints the name of the tier and the depth of its review, one on each line. No tier matches: it
     fails with the message of the verdict.
4. `charter/templates/review-code.yml`, new, in the form of `review-intents.yml`:
   - `on: pull_request` with the four types and `paths: ["**", "!intents/**", "!plans/**"]`; the same
     permissions; no review for a fork.
   - Steps: the checkout with the full history; the fetch of Charter at the version of the contract; a
     step that writes the changed paths of the change request with `git diff --name-only -z` and reads
     the depth with `charter-gate tier --repo-only` on the contract of the base branch, taken with
     `git show`; the count of the reports before; the reviewer; the last step that fails without a new
     report of the head commit, as in `review-intents.yml`.
   - The instructions: follow the skill `change-review`; the depth; the head commit; the diff since the
     report before; the intent and the plan of the linked issue; the allowed commands, which read and
     post one comment. The reviewer changes no file, approves nothing, blocks nothing.
   `.github/workflows/review-code.yml`: the same, with the skill from this repo.
5. `charter/templates/verdict.yml` and `.github/workflows/verdict.yml`: `review-code` joins the list of
   the workflows that start the verdict, and the collect step passes `--code-review-workflow
   review-code.yml`.
6. `charter/scripts/charter_setup.py`: `review-code.yml` joins the written files.
7. `charter-practices/skills/change-review/SKILL.md`, new, under 40 lines, with the front matter of the
   other skills: the reading order, the checklist of the intent, the two depths, the four severities with
   their meaning for code, the closed findings, and the form of the report (marker, `Commit:`, the
   section "Changed since the last report" after the first report, one table, the findings, the last
   line).
8. `AGENTS.md` and `charter/templates/AGENTS.md`, section "Review and limits": one sentence on the
   reviewer of the code, with the identifier `review.code_blocks`.
9. `docs/contract.md`: the field; a section "The reviewer of the code" after the section of the intent
   reviewer, with the workflow, the flag, the four blocking cases, the facts, the command `tier`, and one
   sentence that a repo can run the review of Claude Code beside it. `docs/product.md`, the Test row: an
   agent that is not the author reviews the code.
10. Both manifests: 0.3.10. `intents/code-reviewer.md`: `Status: done`.

## Files

- `charter/schema/contract.toml`, `charter.toml`, `charter/templates/charter.toml`
- `charter/scripts/charter_facts_github.py`, `charter/scripts/charter_gate.py`,
  `charter/scripts/charter_setup.py`
- `charter/templates/review-code.yml`, `.github/workflows/review-code.yml`
- `charter/templates/verdict.yml`, `.github/workflows/verdict.yml`
- `charter-practices/skills/change-review/SKILL.md`
- `AGENTS.md`, `charter/templates/AGENTS.md`
- `docs/contract.md`, `docs/product.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `intents/code-reviewer.md`, `plans/code-reviewer.md`
- `tests/test_charter_gate.py`, `tests/test_charter_facts_github.py`, `tests/test_workflows.py`,
  `tests/test_skills.py`, `tests/test_setup.py`

## Tests

A class `CodeReview` in `tests/test_charter_gate.py` (twelve tests) and in
`tests/test_charter_facts_github.py` (two), a class `CodeReviewer` in `tests/test_workflows.py` (seven) and
in `tests/test_setup.py` (one), and a class `ChangeReviewSkill` in `tests/test_skills.py` (two), with the
names that the intent gives. The last step of the new workflow is run with `bash -e` and a fake `gh`. A
test that lists the files that the setup step writes takes the new workflow.
