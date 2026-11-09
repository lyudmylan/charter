# Intent: the gates run on the code host, and the main branch is protected

Work item: #5. Approved by a person on 2026-09-30, in the work item.

## Goal

The gates run on each change request of this repo, and no change reaches the main branch without them.

## In scope

- A GitHub Actions workflow that runs the checker, the tests, and the four gates on each change request. The merge-readiness verdict is the last step.
- The workflow definition comes from the main branch, so that a change cannot edit its own gate. Verify what GitHub offers for this (rulesets, required workflows).
- Protection of the main branch: no direct push, and the verdict is a required check. Verify what the plan of this repo permits for a private repo.
- The instruction file says what a contributor sees when a gate fails.
- A finding of 2026-10-29, in an adopter (#67): the collecting script read every `#N` in the text of a
  change request as a linked issue, and one sentence that named a later issue made the verdict demand
  the plan of that issue; a complete change request was "not ready". A link is a closing keyword of the
  code host (`close`, `fix`, `resolve`, and their forms in -s and -d, in any case, with an optional colon)
  followed by the number; a bare `#N` is a mention. `docs/contract.md` holds the full list; the instruction
  file gives the form `Closes #N`.

## Out of scope

- Other code hosts. The gate scripts stay host-neutral; only the workflow is specific to GitHub.
- A link form without a closing keyword, such as "Part of #N": a decision for a later work item, if
  it is wanted.

## Acceptance checks

## Automatic checks

1. The collecting script builds the facts file from the API responses: the linked issues with their state,
   the changed files, the recorded reason, the unresolved review threads, and the result of the quality
   job. No network in the tests.
   test: `tests/test_charter_facts_github.py::Facts.test_facts_from_api_data`
   test: `tests/test_charter_check.py::Source.test_source_prints_address_file_version_and_cache_path`
   test: `tests/test_charter_facts_github.py::Text.test_newest_completed_check_run_of_each_name`
   test: `tests/test_charter_gate.py::Quality.test_repo_only_needs_no_source`
   test: `tests/test_charter_facts_github.py::Facts.test_open_change_request_is_preferred_and_closed_never_counts`
   test: `tests/test_charter_check.py::Source.test_source_refuses_an_organization_file`
   test: `tests/test_charter_gate.py::Quality.test_repo_only_refuses_an_organization_file`
2. The text of a change request links an issue only with a closing keyword of the code host, each number
   once, in order; a mention links nothing.
   test: `tests/test_charter_facts_github.py::Text.test_issue_numbers_in_order_each_once`
   test: `tests/test_charter_facts_github.py::Text.test_a_mention_is_not_a_link`

## Manual checks

3. A change request with a failing gate shows a red required check "verdict" and cannot be merged. The
   workflow `verdict` runs from the main branch and never runs the code of the change request.
   who: the leader, with a change request that names no issue, and `gh pr checks <number>`.
4. A direct push to the main branch is refused. who: the leader, or the record of the probe push of 2026-09-30.
5. A change request that passes all gates shows the verdict "ready" in the log of the job "verdict".
   who: the leader, with `gh run view`.
