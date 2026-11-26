<!-- charter-intent-review -->
Commit: 1021dc636b0bdb47f89c108ac7566bc96437d79d

| File | Verdict | Finding |
|---|---|---|
| `intents/product-test.md` (with `plans/product-test.md`) | needs discussion | The rule for a product test that needs the network or a secret does not work. A missing result can still be ready, the tracker skill is dropped, and the intent names no product test scenario. |

I found no epic for #99: its text names none, and `gh issue list` returned nothing. I could not check the intent against epic decisions.

**1. high: `intents/product-test.md`, Out of scope**
- **Sentence:** "A product test that needs the network or a secret, in a run: it runs in the job `product` only."
- **Problem:**
  - In scope, the job `product` "holds no secret", so a test that needs a secret cannot run there.
  - #99 allows such a test if "the contract names the part that runs in the CI only". Neither new field can do that.
  - The brief tells the agent to run the commands of `checks.product` until they pass (plan step 6), with no exception. A command that needs the network cannot pass in a run.
  - `docs/contract.md` and plan step 4 follow the same no-secret job.
- **Proposed text:** "Each command of `checks.product` needs no network and no secret, in a run and in the job `product`. A product test that needs either, and a field for a part that runs in the CI only: a later work item."
- This drops an alternative that #99 allows, so the leader should decide. The other choice is to add a way to name the CI-only part, and to keep it out of the brief. Correct the matching sentence in `docs/contract.md` too.

**2. medium: `intents/product-test.md`, In scope**
- **Sentence:** "The verdict prints one line, `product test: passed` with the commands, or `product test: none, the contract says: <the reason>`, so that a repo without a product test shows it at each merge."
- **Problem:** Plan step 3 adds `not passed` and `not reported`, and the code adds a form for a contract with neither field. With commands but no `product` entry in the facts, the verdict can be ready; check 5's test expects this. The GitHub collector marks a requested but missing run as pending. An older `verdict.yml` without `--check-run product` requests none. A change request can then be ready with no result, against the goal.
- **Proposed text:** "For a contract with commands, a check `product` that did not pass or is not in the facts makes the change request not ready. The verdict prints one line: `passed` with the commands, `not passed`, `not reported`, `none` with the reason, or `none, the contract names no product test`." Align plan step 3 and check 5. If `not reported` should stay ready, say so and say why.

**3. medium: `intents/product-test.md`, In scope**
- **Sentence:** "the template says that a work item that changes the behaviour of the product names the scenario of the product test that shows the change, and the skill `intent-review` asks for it."
- **Problem:** #99 says "The template of an intent and the tracker skill say so." The intent swaps in `intent-review` without a reason. `charter-practices/skills/tracker/SKILL.md`, which guides how intents are written, says nothing about the scenario. Check 7 cannot catch this.
- **Proposed text:** "the template and the skill `tracker` say that a work item that changes the behaviour of the product names the scenario of the product test that shows the change, and the skill `intent-review` asks for it." Add the tracker skill to check 7, plan step 7 and the plan's file list.

**4. medium: `intents/product-test.md`, check 8**
- **Sentence:** "The product test of this repo makes a repo with the setup step through the commands of `charter/bin` and runs the contract checks, the quality gate, the boundary gate, and a verdict on it."
- **Problem:** This work item changes product behaviour but names no scenario showing the change, which its own new rule requires. `tests/product.py` never runs `charter-gate product`. Its verdict step reads a handwritten `"product": "pass"`. So the outside test does not show that the new gate works in a new repo.
- **Proposed text:** "The product test of this repo makes a repo with the setup step through the commands of `charter/bin` and runs the contract checks, the quality gate, the gate `product`, the boundary gate, and a verdict on it. The scenario that shows this change: the gate `product` runs the command that `--product` wrote, and the verdict prints `product test: passed`." Align the In scope bullet and plan step 8.

Highest open severity: high