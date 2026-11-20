# Intent: the contract names the test of the product as a whole, and a change request needs its result

Work item: #99. Status: done. Approval: a person merges the change request that adds this file.

## Goal

A repo with code says in its contract how its product is started and tested from the outside, each
change request carries the result of that test, and a repo that has no such test says so with a reason
that each evidence record shows.

## In scope

- The gap: `checks.quality` lists commands, and nothing says that one of them tests the product as a
  whole. A repo passes each gate with unit tests alone. A review reads the change; it does not show that
  the product works. The decision of the leader of 2026-11-20: Charter enforces that a product tests
  itself as a whole, and Charter writes no product test.
- Two fields of the contract. `checks.product`, a set: the commands that start the product and test it
  from the outside, as a user or a caller meets it. `checks.no_product_reason`, a text: why the repo has
  no product test yet.
- The contract checks, `charter-check all`: a contract that declares code paths has a command in
  `checks.product` or a reason in `checks.no_product_reason`. With neither it fails, and the failure says
  what to add. With both it fails too: a repo with a product test has no reason left.
- A gate, `charter-gate product`, in the form of the gate `quality`: it runs the commands and fails when
  one fails. With a reason and no command it passes and prints the reason.
- The workflow `tests`, template and this repo, gets a second job, `product`, that runs the gate after
  the same toolchain block. It runs the code of the change request and holds no secret. The verdict
  workflow reads the check `product` beside the check `tests`, so a failed product test makes the change
  request not ready, and the evidence record holds its state.
- The verdict prints one line, `product test: passed` with the commands, or `product test: none, the
  contract says: <the reason>`, so that a repo without a product test shows it at each merge.
- The run of an agent (#92): the brief tells the agent to run the commands of `checks.product` after the
  quality commands, in its sandbox. So a product test that a run can use needs no network and no secret;
  `docs/contract.md` says so.
- The intent of a work item: the template says that a work item that changes the behaviour of the
  product names the scenario of the product test that shows the change, and the skill `intent-review`
  asks for it.
- The setup step: a flag `--product CMD`, repeatable. Without it the contract gets the reason "no product
  to start yet", and the setup step names the product test among its manual steps.
- The contract of this repo names its own product test: one command that makes a repo with the setup
  step in an empty folder, through the commands of `charter/bin`, and runs the contract checks, the
  quality gate, the boundary gate, and a verdict on it.
- `docs/contract.md`: the two fields, the gate, the job. `docs/product.md`, the Test row of the lifecycle
  map. `docs/decisions.md`: the decision with its reason and its sources.
- Both manifests: the same version, 0.3.15 or later.

## Out of scope

Charter writes no product test for an adopter. Scenarios that are kept outside the repo, so that the
author agent does not see them: a decision of the leader, later. A check of how good a product test is.
Evals for the skills that a product ships. A product test that needs the network or a secret, in a run:
it runs in the job `product` only.

## Acceptance checks

## Automatic checks

1. The schema has the two fields, and `docs/contract.md` lists them.
   test: `tests/test_product.py::Fields.test_the_fields_are_in_the_schema_and_in_the_contract_document`
2. `charter-check all` fails for a contract with code paths and neither a command nor a reason, and for
   one with both; the failure says what to add. It passes with a command, with a reason, and for a
   contract without code paths.
   test: `tests/test_product.py::Fields.test_code_without_a_product_test_or_a_reason_fails`
   test: `tests/test_product.py::Fields.test_a_command_or_a_reason_passes_and_both_fail`
3. The gate runs the commands, fails when one fails, and with a reason and no command passes and prints
   the reason.
   test: `tests/test_product.py::Gate.test_the_gate_runs_the_commands_of_the_product_test`
   test: `tests/test_product.py::Gate.test_a_reason_passes_and_is_printed`
4. The workflow `tests`, template and this repo, has the job `product` with the gate after the toolchain
   block and with no secret, and the verdict workflow reads the check `product`.
   test: `tests/test_product.py::Workflows.test_the_job_product_runs_the_gate_with_no_secret`
   test: `tests/test_product.py::Workflows.test_the_verdict_reads_the_check_product`
5. The verdict prints the line of the product test in both forms, and a failed check `product` makes the
   change request not ready.
   test: `tests/test_product.py::Verdict.test_the_line_names_the_commands_or_the_reason`
   test: `tests/test_product.py::Verdict.test_a_failed_product_test_is_not_ready`
6. The setup step writes the commands of the flag, or the reason without it, and names the product test
   among its manual steps; the written contract passes the contract checks in both cases.
   test: `tests/test_product.py::Setup.test_the_flag_or_the_reason`
7. The brief of a run names the commands of `checks.product`; the template of an intent and the skill
   `intent-review` name the scenario of the product test.
   test: `tests/test_product.py::Texts.test_the_brief_the_template_and_the_skill_name_the_product_test`
8. The product test of this repo makes a repo with the setup step through the commands of `charter/bin`
   and runs the contract checks, the quality gate, the boundary gate, and a verdict on it. The contract
   of this repo names it, and the gate `product` passes here.
   test: `tests/test_product.py::OwnProduct.test_the_contract_of_this_repo_names_its_product_test`
   command: `python3 charter/scripts/charter_gate.py product --contract charter.toml`
9. The decision record holds the decision with its sources, and the Test row of `docs/product.md` names
   the product test.
   test: `tests/test_product.py::Texts.test_the_decision_and_the_product_document`
10. Both manifests name the same version, 0.3.15 or later.
    test: `tests/test_product.py::Texts.test_both_manifests_name_the_version`

## Manual checks

11. An adopter names its product test in its contract, and a change request that breaks the product is
    not ready. who: the leader. Not automatic: the adopter repo is outside this repo.
