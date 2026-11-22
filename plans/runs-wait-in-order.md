# Plan: each started run waits for its turn (#120)

Intent: `intents/runs-wait-in-order.md`, checks 1 to 3.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. A test workflow on its own branch, not for the main branch: one job that waits 40 seconds, in one
   concurrency group. Five pushes in less than one minute start five runs. One test with `queue: max`, one
   with no option. The results are the evidence of check 3, copied to a comment on #120. The branch is
   deleted after the merge.
2. `charter/templates/run.yml` and `.github/workflows/run.yml`: `queue: max` in the group, with the reason
   in the comment above it.
3. `docs/contract.md`, the section "The run": the sentence on the runs that wait.
4. Tests in `tests/test_run.py`: `Workflow.test_the_start_the_stop_switch_and_one_run_at_a_time` asks for
   the option and for one group; `Documents.test_the_contract_document_says_that_each_run_waits` is new.

## Files

- `charter/templates/run.yml`
- `.github/workflows/run.yml`
- `docs/contract.md`
- `tests/test_run.py`
- `intents/runs-wait-in-order.md`
- `plans/runs-wait-in-order.md`

## Not changed

`docs/product.md`: the product does the same work. The manifests: 0.3.17 has no tag yet, so this change
goes out with it.
