<!-- charter-intent-review -->
Commit: cf698f77a4469f966fe4e7acc7b8a438df9a0125

## Changed since the last report

- `intents/product-test.md`:
  - The Goal now says the verdict and the evidence record show the reason.
  - A reason of blanks only now counts as none, in the scope and in check 2.
  - The scope and check 5 add the line in the evidence record and the not-ready state `product test: not reported`. Check 5 also adds the state of the check `product` in the record, and two tests.
  - The scope explains why the template and `intent-review` are used instead of the skill `tracker`.
  - "Out of scope" says it replaces the issue's option for a part that runs in the CI only.
- `plans/product-test.md`: step 3 now says `not reported` makes the verdict not ready, and the other lines change no readiness.

| File | Verdict | Finding |
|---|---|---|
| `intents/product-test.md` | approve with a change | The scope sends a test that needs a secret to a job that has none. The list of verdict lines is incomplete, and no check names this work item's product test scenario as showing the change. |
| `plans/product-test.md` | approve | no finding |

## Findings

1. **medium**, `intents/product-test.md`, "Out of scope".
   - **Sentence:** "A product test that needs the network or a secret, in a run: it runs in the job `product` only. This replaces the option of the issue, a contract that names the part for the CI only: a run then has no product test for that part, and the job `product` of its change request runs it."
   - **Problem:** "In scope" says the job `product` holds no secret, and `.github/workflows/tests.yml` gives it none, so a test that needs a secret cannot run there. The contract also has only the one set `checks.product`, with no way to mark a part for the CI only. The run's brief tells the agent to run the commands of that set until they pass, so the run does not leave such a part out.
   - **Proposed text:** "A product test that needs a secret: neither a run nor the job `product` can run it. A part for the CI only, the option of the issue: the contract cannot mark one. So each command of `checks.product` needs no secret, and for use in a run, no network."
   - `docs/contract.md`, "The run", says that a test needing either "runs in the job `product` only". It needs the same correction.

2. **low**, `intents/product-test.md`, check 5.
   - **Sentence:** "The verdict prints the line of the product test in both forms, and a failed check `product` makes the change request not ready."
   - **Problem:** "Both forms" no longer covers the lines. The same check adds `not reported`, and a test expects `product test: not passed`. `docs/contract.md` also lists `product test: none, the contract names no product test`.
   - **Proposed text:** "The verdict prints one line of the product test: `passed` with the commands, `not passed`, `not reported`, `none` with the reason, or, with neither field, `none, the contract names no product test`. A failed check `product` makes the change request not ready."

3. **low**, `intents/product-test.md`, check 8.
   - **Sentence:** "…and runs the contract checks, the quality gate, the boundary gate, and a verdict on it."
   - **Problem:** this work item changes the product's behaviour, but the check does not say which scenario of the product test shows the change. `tests/product.py` already expects the new line from the verdict.
   - **Proposed text:** "…and a verdict on it. The scenario that shows this change: the verdict is ready and prints `product test: passed` with the command."

Highest open severity: medium