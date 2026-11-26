# Intent: the contract names the test of the product

Work item: #4. Approval: a person merges the change request that adds this file.

## Goal

The contract names the command of the test of the product as its product test, so each change request
runs the test of the product.

## In scope

One command starts product, and one command runs the test of the product. Both exist on the main branch:
`node src/main.ts` and `node product-test/run.ts`. So this work item adds no script and no code. It changes
one line of the contract.

- `charter.toml`, the section `[checks]`. One line replaces the line `no_product_reason`:
  - `product = ["node product-test/run.ts"]`
  - The contract then holds no `no_product_reason`. The contract takes a command or a reason, not both.
  - The comment above the line says what the test does: it starts product for each scenario, sends the
    events, and compares the messages with the known answer.
- `docs/architecture.md`, the row "Test of the product": one sentence says that the contract names the
  command as its product test, so each change request runs it.
- No agent run builds this work item: the contract is closed to a run of an agent with no person present.
  The intent, the plan and the change are in one change request, and the merge of the leader approves the
  three.

After the merge, the job `product` of each change request runs the test of the product. Before, the job
passed with the reason for no product test.

## Out of scope

A script in the package file: the package file stays closed to an agent run, and the two commands need no
short name. New scenarios, and each change of `src/`, of `product-test/` or of a test. A change of a
workflow: the job `product` exists and reads the contract. The two small findings on the test of the
product (#40).

## Acceptance checks

## Automatic checks

1. The contract names the command as its product test.
   command: `grep -qx 'product = \["node product-test/run.ts"\]' charter.toml`
2. The checks of the contract pass on the changed contract. They fail when the contract holds a command
   and a reason for no product test, so this check also shows that the reason is gone.
   command: `charter-check all charter.toml`
3. The gate of the product test runs the command of the contract and passes.
   command: `charter-gate product --contract charter.toml`

This work item adds no behaviour to the product, so it names no new scenario of the test of the product.

## Manual checks

4. The job `product` on the change request of this work item runs the test of the product and passes.
   who: the leader, at the merge, with the link to the job from the author. Not automatic: the job exists
   only on the code host, after the checks ran.
