<!-- charter-intent-review -->
Commit: 015bfed3f8b8afe40e38d163f1e7154166f0916c

## Changed since the last report

- `intents/product-test.md`:
  - The Goal says the verdict and the evidence record show the reason at each merge.
  - The scope adds the rules for a blank reason and for `not reported`, and says the record holds the verdict line.
  - It explains why the `tracker` skill is not named and says the issue's CI-only option is replaced.
  - Checks 2 and 5 cover the new rules, and check 5 names two more tests.
- `plans/product-test.md`: step 3 says `not reported` makes the verdict not ready, and the other lines don't change readiness.

## Findings of this round

The five findings of the last report are resolved in the intent. For the first two, `tests/test_product.py` has the two new tests that check 5 names. I read them but did not run them.

| File | Verdict | Finding |
|---|---|---|
| `intents/product-test.md` | approve with a change | The new text says the job `product` runs a test that a run cannot, but that job holds no secret. The scope also leaves out two forms of the verdict line. |
| `plans/product-test.md` | no finding | no finding |

## Findings in detail

1. **medium**, `intents/product-test.md`, "Out of scope".
   - **Sentences:** "A product test that needs the network or a secret, in a run: it runs in the job `product` only. This replaces the option of the issue, a contract that names the part for the CI only: a run then has no product test for that part, and the job `product` of its change request runs it."
   - **Problem:** The scope and check 4 say the job `product` holds no secret, so a test that needs a secret cannot run there. The contract also cannot mark a command as CI only. The brief of a run covers all commands of `checks.product`, and plan step 6 says to run them "until they pass". So a run is not told to skip a command that needs the network. `docs/contract.md`, "The product test", repeats the claim about the job.
   - **Proposed text:** "A product test that needs a secret: neither a run nor the job `product` can run it, so `checks.product` does not name it. A command that needs the network, marked as for the CI only: the contract has no such mark. This replaces that option of the issue. Each command of `checks.product` needs no network and no secret."
   - **Related text:** Make the same correction in `docs/contract.md`. Also align the sentence under "The run of an agent" that speaks of "a product test that a run can use".

2. **low**, `intents/product-test.md`, "In scope", the verdict line.
   - **Sentence:** "The verdict prints one line, `product test: passed` with the commands, or `product test: none, the contract says: <the reason>`, so that a repo without a product test shows it at each merge."
   - **Problem:** Plan step 3 also has `product test: not passed`. `charter_gate.py` and `docs/contract.md` also have `product test: none, the contract names no product test`, for a contract with neither field. The intent names neither form.
   - **Proposed text:** Add after the sentence on `not reported`: "A check `product` that did not pass prints `product test: not passed`. A contract with neither field prints `product test: none, the contract names no product test`."

Highest open severity: medium