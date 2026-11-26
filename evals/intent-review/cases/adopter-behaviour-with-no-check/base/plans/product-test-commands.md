# Plan: the contract names the test of the product (#4)

Intent: `intents/product-test-commands.md`, checks 1 to 4.
The intent, the plan, and the change are in one change request; the merge of the leader approves the three.

## Steps

1. `charter.toml`, the section `[checks]`: the line `product = ["node product-test/run.ts"]` replaces the
   line `no_product_reason`, and the comment above it says what the test does.
2. `docs/architecture.md`, the row "Test of the product": one sentence on the contract.
3. Run the commands of checks 1 to 3, and the two commands before a push.
4. After the push, read the job `product` of the change request and give the leader its link: check 4.

## Files

- `charter.toml`
- `docs/architecture.md`
- `intents/product-test-commands.md`
- `plans/product-test-commands.md`

## Tests

- None: the change holds no code of the product. Checks 1 to 3 are commands.
