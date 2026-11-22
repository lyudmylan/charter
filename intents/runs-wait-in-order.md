# Intent: each started run waits for its turn

Work item: #120. Approval: a person merges the change request that adds this file.

## Goal

Each run that a person starts works, one after the other, in the order of the start. No run is cancelled
because another one was started after it.

## In scope

- The defect. The run workflow has one concurrency group with `cancel-in-progress: false`, and
  `docs/contract.md` said that a second run waits. The code host keeps one waiting run in a group by
  default, and a new run cancels the run that waits and takes its place. A person who puts the label
  `charter-run` on ten issues got two runs: the first one, and the last one.
- The option `queue: max` in the group of the run workflow, in the template and in the workflow of this
  repo. Up to 100 runs then wait, in the order in which they started to wait. The name of the option comes
  from the documentation of the code host, the page on the concurrency of workflows, read on 2026-11-22.
- One run works at a time, as before. The stop switch stays as it is: with the variable `CHARTER_RUNS` at
  `off`, a run that waited starts no job.
- `docs/contract.md` and the comment of the workflow say what waits and why the option is there.
- The version stays 0.3.17: no tag names it yet.

## Out of scope

More than one run at the same time. A limit on the cost of a day. The order of runs whose change requests
touch the same files: each run starts from the main branch, and the person who merges resolves a conflict.
What the code host does with run number 101 of a group: it cancels it, by its documentation.

## Acceptance checks

## Automatic checks

1. The run workflow holds one concurrency group, with `cancel-in-progress: false` and `queue: max`, in the
   template and in the workflow of this repo.
   test: `tests/test_run.py::Workflow.test_the_start_the_stop_switch_and_one_run_at_a_time`
2. `docs/contract.md` says that the other runs wait in the order of their start, with the option, and
   holds the old sentence no more.
   test: `tests/test_run.py::Documents.test_the_contract_document_says_that_each_run_waits`

The product test has no scenario for this change: it runs the commands of the plugin in a temporary
folder, and the option is read by the code host alone.

## Manual checks

3. On the code host, five runs of a test workflow with the option, started in less than one minute, each
   end with success, one at a time, in the order of their start. The same five runs with no option: the
   code host cancels the runs that waited when a new one came.
   who: the leader, from the results of the two tests, which a comment on #120 holds with the address of
   each run; the comment stays when the branch of the test and the logs are gone. Not automatic: the
   check needs machines of the code host and several minutes.
