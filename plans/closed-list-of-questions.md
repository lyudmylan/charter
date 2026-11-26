# Plan: the intent reviewer blocks only on a failed question of a closed list (#153)

Intent: `intents/closed-list-of-questions.md`, checks 1 to 13.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. The source of the list: the findings at medium or above in the old reports of the reviewer, sorted by
   kind. Eight kinds are a question; the leader said for two more kinds that they are a note.
2. `charter-practices/skills/intent-review/SKILL.md`: the questions with their severity, the notes, the form
   of the report, the rule of a later round. The file stays under the limit of lines.
3. `charter/scripts/charter_review.py`, new, with `charter/bin/charter-review`: the list of the questions,
   the reader of the answers, the reasons why a report is not complete, the severity, the answers of code on
   the names of the checks, and the commands `intents`, `before`, `close`, and `severity`.
4. `charter/templates/review-intents.yml` and `.github/workflows/review-intents.yml`: the step "Give the
   answers of code to the reviewer"; the prompt names the file of these answers; the step "Post the report
   of the reviewer" closes the report before it posts it. In this repo a step takes the folder of the
   scripts from the base branch, so no step runs code of the change. A version of Charter that has no such
   script posts the report as the reviewer wrote it.
5. `evals/intent-review/run.py`: the workspace of a case gets the file of the answers of code; the command
   closes each report as the workflow does and keeps that text; the grader reads the severity of code and
   looks for the subject in the answers that do not hold. A report with no answer of the list and with a
   severity line of its own is a report of before this change.
6. The cases: the field `contested` leaves the 8 cases, and each gets its answer and, for `blocks`, its
   subject: 2 block and 6 pass. Two cases with the answer `blocks` become `passes`, and two more get other
   ways to name their subject. The skill `evidence-review` reviews this reading before the leader sees it;
   where the two agents and the author read the rule in two ways, the rule gets a sentence for that kind.
7. `tests/test_review.py`, new. `tests/test_reviewer_eval.py`: the reports of the stand-in get the new
   form. `tests/test_skills.py`, `tests/test_setup.py`: the lines that the change moves. `tests/product.py`:
   the scenario "severity of a report of the reviewer".
8. `charter-practices/skills/review-loop/SKILL.md`, `AGENTS.md`, `charter/templates/AGENTS.md`,
   `docs/contract.md`, `docs/product.md`, `README.md`, both manifests.
9. After the word of the leader: the full run and the two more runs of the `passes` cases, with their
   record in `evals/intent-review/record/`.

## Files

- `charter-practices/skills/intent-review/SKILL.md`, `charter-practices/skills/review-loop/SKILL.md`
- `charter/scripts/charter_review.py`, `charter/bin/charter-review`
- `charter/templates/review-intents.yml`, `.github/workflows/review-intents.yml`
- `evals/intent-review/run.py`, `evals/intent-review/cases/` (the `case.toml` of 12 cases)
- `tests/test_review.py`, `tests/test_reviewer_eval.py`, `tests/test_skills.py`, `tests/test_setup.py`,
  `tests/product.py`
- `AGENTS.md`, `charter/templates/AGENTS.md`, `docs/contract.md`, `docs/product.md`, `README.md`, both
  manifests
- `intents/closed-list-of-questions.md`, `plans/closed-list-of-questions.md`

## Tests

- `tests/test_review.py`: `TheList`, two tests; `Answers`, three tests; `TheChange`, four tests;
  `TheWorkflow`, three tests.
- `tests/test_reviewer_eval.py`: the tests of `TheRun` and of `Grader` that the intent names.

## What this change does not show

The first report of the reviewer on this change request has the old steps of the workflow: the script is
not on the base branch yet, so the reviewer writes the severity line itself, by the rule of the skill. The
two new steps run in this repo from the first change request after the merge.

The questions Q1, Q2, Q5, Q6, and Q7, and the second part of Q3, stay a judgment of the model. The border
between a question that does not hold and a note, the "main case" of a sentence, is a judgment too. The
test set shows how stable they are, with 25 cases and one model.
