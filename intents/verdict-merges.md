# Intent: the verdict merges the change request of a tier whose approver is `agent`

Work item: #66. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A change request of a tier whose approver is `agent` is merged by the verdict, after the reviews by
agents that are not the author closed on its head commit, and a person still merges every other tier.

## In scope

- The gap: the contract can name `agent` as the approver of a tier, and nothing acts on it. A person
  merges each change request, also one of the low tier that passed each check.
- The decision of the leader of 2026-11-20: the tier decides who accepts the plan, who reviews, and who
  merges. In a tier whose approver is `agent`, agents do the three and a person reads the evidence
  record. A change request that holds an intent stays with a person.
- The gate decides, in the verdict. It merges when each of these holds, and else it names the first
  one that does not:
  - the verdict is ready;
  - the approver of the tier of the change is `agent`;
  - `review.code_blocks` is true, so the reviewer of the code is past its shadow period;
  - the facts name the head commit;
  - no file under `intents/` changed: a person approves an intent, whatever tier the contract gives to
    that folder;
  - when the change holds a file outside `intents/` and `plans/`: the newest report of the code review
    is closed on the head commit (#95);
  - when the change holds a file under `plans/`: the newest report of the intent reviewer is below the
    threshold and names the head commit. This is the acceptance of the plan in that tier.
- The facts collector gives the line `Commit:` of the newest report of the intent reviewer, as the fact
  `review_commit`.
- The verdict prints one line, `merge: the verdict merges ...` or `merge: a person merges: <the reason>`,
  and the evidence record holds the decision under `merge_by_verdict` with that line among its reasons.
- The verdict workflow, template and this repo, gets one step after the step that publishes the check.
  It runs only when the record says that the verdict merges. It merges the change request at the head
  commit that the verdict read, with the secret `CHARTER_MERGE_TOKEN`. Without the secret it merges
  nothing and says that a person merges. A merge that the code host refuses fails the run, and a person
  merges.
- The two reviewer workflows, templates and this repo, tell the reviewer that the files and the text of a
  change request are data: a sentence in them that tells the reviewer what to report is a finding, and
  the reviewer does not follow it. With a merge by the verdict, a report of a reviewer decides more than
  before. This lowers the risk and does not remove it: a person still reads the evidence record.
- The merge token is a secret of the adopter, which a person creates: a merge with the token of the
  workflow starts no workflow on the main branch. The setup step names it among its manual steps, as an
  optional one.
- So three settings turn the merge on, each made by a person: the approver `agent` in a tier of the
  contract, the flag `review.code_blocks`, and the merge token. The contract that the setup step writes
  and the contract of this repo set none of them.
- `AGENTS.md` and its template: the approver of the tier merges, a person or the verdict; and in a tier
  whose approver is `agent`, the review of the plan by the intent reviewer is its acceptance.
- `docs/decisions.md`, section C: the decision with its reason. `docs/contract.md`: the meaning of the
  approver `agent`, the conditions, the step, the secret. `docs/product.md`, the Deploy row of the
  lifecycle map: the verdict merges a tier whose approver is `agent`.
- Both manifests: the same version, 0.3.11 or later.

## Out of scope

An approving review on the code host, rulesets that ask for one, and the auto-merge of the code host. The
sample that a person reads after the merge, and the return of a tier to the approval of a person after a
defect that escaped (decision C10): later issues of #13. A run of an agent that is the author: #92. The
approval of an intent by an agent: the leader noted the question on 2026-11-20 and decided nothing.

## Acceptance checks

## Automatic checks

1. The gate says that the verdict merges for a ready change of a tier whose approver is `agent`, with the
   flag of the code review and a closed report of it on the head commit. A change of a plan alone merges
   with a closed report of the intent reviewer on the head commit, and needs no report of the code
   review. A change with code and a plan needs both reports.
   test: `tests/test_charter_gate.py::VerdictMerges.test_the_verdict_merges_a_ready_change_of_an_agent_tier`
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_change_of_a_plan_alone_merges_with_a_closed_intent_review`
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_change_with_code_and_a_plan_needs_both_reports`
2. It says that a person merges, with the reason, in each other case: a tier of a person; a verdict that
   is not ready; the shadow period of the code review; a change that holds a file under `intents/`; a
   change with a plan whose newest intent report is open, is missing, has no severity line, or names
   another commit; a change whose facts name no head commit, which the last test of this check covers.
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_change_that_holds_an_intent_stays_with_a_person`
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_tier_of_a_person_is_merged_by_a_person`
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_change_that_is_not_ready_is_not_merged`
   test: `tests/test_charter_gate.py::VerdictMerges.test_the_shadow_period_of_the_code_review_keeps_the_merge_with_a_person`
   test: `tests/test_charter_gate.py::VerdictMerges.test_a_plan_without_a_closed_review_at_the_head_commit_is_not_merged`
3. The facts collector gives the commit of the newest report of the intent reviewer.
   test: `tests/test_charter_facts_github.py::VerdictMerges.test_the_commit_of_the_newest_intent_report_is_a_fact`
4. The evidence record holds the decision and its line.
   test: `tests/test_charter_gate.py::VerdictMerges.test_the_record_holds_the_merge_and_its_reason`
5. The verdict workflow, template and this repo, holds the merge step after the step that publishes the
   check; the token reaches the step through its environment; the two files agree in the step.
   test: `tests/test_workflows.py::VerdictMerges.test_the_merge_step_follows_the_published_check`
   test: `tests/test_workflows.py::VerdictMerges.test_the_workflow_of_this_repo_follows_the_template`
6. The step, run with a fake of the code host: with a record that says so and a token, it merges the
   change request at the head commit of the verdict. With a fake that refuses the merge, the step fails;
   the first test of this check covers both.
   With a record of a person's merge, or without a token, it calls no merge and ends well.
   test: `tests/test_workflows.py::VerdictMerges.test_the_step_merges_the_head_commit_with_the_merge_token`
   test: `tests/test_workflows.py::VerdictMerges.test_the_step_merges_nothing_for_a_person_or_without_the_token`
7. The contract that the setup step writes names no tier with the approver `agent` and sets the flag to
   false; the setup step names the merge token as an optional manual step; the instruction template and
   the `AGENTS.md` of this repo say who merges and what the acceptance of a plan is in such a tier.
   test: `tests/test_setup.py::VerdictMerges.test_the_setup_turns_no_merge_on_and_names_the_token`
   test: `tests/test_setup.py::VerdictMerges.test_the_instructions_say_who_merges`
8. The decision record holds the decision in section C with its reason, `docs/contract.md` says what the
   approver `agent` means, and the Deploy row of `docs/product.md` names the merge by the verdict.
   test: `tests/test_charter_gate.py::VerdictMerges.test_the_decision_and_the_documents_name_the_merge`
9. Both manifests name the same version, 0.3.11 or later.
   test: `tests/test_charter_gate.py::VerdictMerges.test_both_manifests_name_the_version`

10. The two reviewer workflows, templates and this repo, hold the sentence that the text of a change is
    data and that an instruction in it is a finding.
    test: `tests/test_workflows.py::VerdictMerges.test_the_reviewers_treat_the_text_of_a_change_as_data`

## Manual checks

11. In an adopter repo with the three settings, a change request of the tier with the approver `agent`
    is merged by the verdict, the evidence record holds the line, and the workflows of the main branch
    start after the merge. who: the leader. Not automatic: the check needs the code host, a secret, and
    two reviewers that run.
