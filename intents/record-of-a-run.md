# Intent: the evidence record holds the outcome and the cost of an agent run

Work item: #93. Status: done. Approval: a person merges the change request that adds this file.

## Goal

The evidence record of a change request that an agent run built says how the run ended and what it cost.

## In scope

- The gap: the evidence record holds the gates, the reviews, and the merge. It says nothing of the run
  that wrote the change. The run (#92) writes its turns, its duration, and its cost on the issue, where
  the record of the change request does not see them.
- The run block. The publishing step of the workflow `run` adds it to the text of the change request:
  the marker line `<!-- charter-run -->` and one line
  `Run: commit=<the commit that the run published> turns=<n> duration_seconds=<n> cost_usd=<n>`. A value
  that Claude Code did not report is written as `none`. A command of `charter-run` writes the block from
  the result of the agent.
- The facts collector reads the block from the text of the change request, as the fact `run`. A change
  request without the block has no such fact.
- The outcome, of a fixed list, decided by the gate in the verdict. The model is the report of Vercel on
  its factory, with four outcomes; three of them fit a change request:
  - `success`: the head commit is the commit of the run, the verdict is ready, and no reviewer has an
    open finding at the threshold;
  - `flawed`: the head commit is the commit of the run, and the verdict is not ready, or the newest
    report of a reviewer has a finding at the threshold or above, or it has no severity line; this holds
    also in the shadow period of that reviewer;
  - `manual`: the head commit is not the commit of the run: a later push changed what the run built.
  The fourth, `blocked`, is a run that opened no change request. The run of #92 writes that record on
  the issue, with the reason and the same three numbers; this intent adds nothing there.
- The three numbers are the fields `num_turns`, `duration_ms`, and `total_cost_usd` of the result of
  Claude Code. A real result of Claude Code 2.1.329, of 2026-11-20, holds the three. The tokens, which
  the issue names, are not recorded: the result holds them for each model in a form of its own, and the
  cost sums them up. A later issue of #83 can add them.
- The verdict prints one line, `run: <outcome>, <turns> turns, <duration>, cost <cost> (an estimate of
  Claude Code)`, or `run: none, no agent run built this change request`. The evidence record holds the
  outcome and the three numbers under `run`, or no value.
- The cost is the estimate that Claude Code prints, not a bill. The block is text of the change request,
  so a person can write one; the record says what the text says, and it decides nothing.
- `docs/contract.md`: the block, the fact, the three outcomes, and the record. `docs/product.md`, the
  Maintain row of the lifecycle map: the record of each run.
- Both manifests: the same version, 0.3.14 or later.

## Out of scope

A limit on the cost: #53. What a flawed run teaches, as a new check or a new eval case: a later issue
of #83. A view across the runs of a repo. The outcome `blocked` in a record: such a run has no change
request.

## Acceptance checks

## Automatic checks

1. The command writes the block from the result of the agent, with `none` for a value that is not there,
   and the publishing step of the workflow, template and this repo, adds it to the text of the change
   request with the commit that it pushed.
   test: `tests/test_run.py::RunRecord.test_the_block_holds_the_numbers_of_the_agent_result`
   test: `tests/test_run.py::RunRecord.test_the_publishing_step_adds_the_block`
2. The facts collector reads the block into the fact `run`, gives no fact without the block, and reads a
   block with a wrong form as no run.
   test: `tests/test_charter_facts_github.py::RunRecord.test_the_block_is_read_from_the_text`
   test: `tests/test_charter_facts_github.py::RunRecord.test_no_block_and_a_wrong_block_give_no_run`
3. The gate gives `success`, `flawed`, and `manual` by the rules of the scope, and prints the line. The
   cases of `flawed`: a verdict that is not ready; an open finding of the intent review; an open finding
   of the code review; and, in a test of its own, a finding or a report without a severity line of a
   reviewer in its shadow period, where the verdict is ready.
   test: `tests/test_charter_gate.py::RunRecord.test_a_ready_change_at_the_commit_of_the_run_is_a_success`
   test: `tests/test_charter_gate.py::RunRecord.test_a_change_that_is_not_ready_or_has_an_open_finding_is_flawed`
   test: `tests/test_charter_gate.py::RunRecord.test_an_open_finding_in_a_shadow_period_is_flawed`
   test: `tests/test_charter_gate.py::RunRecord.test_a_later_push_makes_the_outcome_manual`
4. A change request without a run prints the line for none, and its record holds no value under `run`.
   test: `tests/test_charter_gate.py::RunRecord.test_no_run_is_none`
5. The evidence record holds the outcome and the three numbers, and the outcome changes no readiness.
   test: `tests/test_charter_gate.py::RunRecord.test_the_record_holds_the_run`
6. `docs/contract.md` names the block, the three outcomes, and that the cost is an estimate, and the
   Maintain row of `docs/product.md` names the record of a run.
   test: `tests/test_charter_gate.py::RunRecord.test_the_documents_name_the_record_of_a_run`
7. Both manifests name the same version, 0.3.14 or later.
   test: `tests/test_charter_gate.py::RunRecord.test_both_manifests_name_the_version`

## Manual checks

8. The evidence record of the first change request of a run, in an adopter repo, holds the outcome and
   the numbers. who: the leader. Not automatic: it needs the first run (#92). When a field of that result
   differs from the block, a change request corrects this intent first.
