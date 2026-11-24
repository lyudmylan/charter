# Plan: an agent answers the findings of the reviewers on the change request of a run (#118)

Intent: `intents/answer-findings.md`, checks 1 to 14.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. `charter/schema/contract.toml`: the field `run.answer_start`, a choice with the order `factory`, `person`.
2. `charter/scripts/charter_gate.py`: the function `answer_state` on the review loops, the function
   `answer_of` on the change request, and the command `answer`, which prints `name=value` lines and ends
   with 0 for each decision. The fact `run` can hold `agent_runs`; the line of the verdict and the record
   name it. The merge by the verdict gets one more condition: no finding that an agent of a run dropped.
3. `charter/scripts/charter_facts_github.py`: `run_block` reads each block and sums them; the facts
   `head_branch`, `state`, `from_fork`, and `answered_commits`; the option `--comments` of `collect`.
4. `charter/scripts/charter_run.py`: the brief of an answer, `brief --reports`; `result --answer-round`;
   the command `body`, which marks each dropped finding as one of the agent of a run; the outcome of an
   answer, `outcome --answered --answers`.
5. `charter/templates/run.yml` and `.github/workflows/run.yml`: the trigger after a reviewer workflow on a
   branch `run/**` and the input `change_request`; the job `decide`, which `run` needs, written after it in the file; in
   the job `run`, the fetch of the branch in the step that reads the issue, the brief of an answer, the
   open of the branch in the step of the agent, the round for `result`, a step that publishes an answer,
   and the outcome on the change request.
6. `charter/scripts/charter_setup.py`: one sentence in the hand step on the workflow `run`.
7. `charter-practices/skills/review-loop/SKILL.md`: the branch of a run, in three lines, inside the limit
   of lines of a skill.
8. `docs/contract.md`: the field, the section "The answer to the findings of the reviewers", and the sum
   of the blocks in "The record of a run". `docs/product.md`: one sentence.
9. Both manifests: 0.3.19.
10. Tests: the new file `tests/test_answer.py`, with the tests that the intent names. In
    `tests/test_run.py`, the tests of the workflow follow its new form: two jobs, two more steps of the job
    `run`, the token of a person in two steps, the organization source in three. In
    `tests/test_charter_facts_github.py`, the case of two blocks follows the sum.
11. `tests/product.py`: two steps on the decision, in a repo that the setup step made.

## Files

- `charter/schema/contract.toml`
- `charter/scripts/charter_gate.py`
- `charter/scripts/charter_facts_github.py`
- `charter/scripts/charter_run.py`
- `charter/scripts/charter_setup.py`
- `charter/templates/run.yml`
- `.github/workflows/run.yml`
- `charter-practices/skills/review-loop/SKILL.md`
- `docs/contract.md`
- `docs/product.md`
- `charter/.claude-plugin/plugin.json`
- `charter-practices/.claude-plugin/plugin.json`
- `intents/answer-findings.md`
- `plans/answer-findings.md`
- `tests/test_answer.py`
- `tests/test_run.py`
- `tests/test_charter_facts_github.py`
- `tests/product.py`

## Not tested here

The start of a workflow after another one, and the push of an answer by the token of a person: the code
host does both only for a workflow of the main branch. Check 14 of the intent covers them, at an adopter,
after the release.
