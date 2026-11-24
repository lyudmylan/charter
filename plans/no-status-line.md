# Plan: an intent holds no status line (#117)

Intent: `intents/no-status-line.md`, checks 1 to 4.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. `charter/templates/intent.md`: the line of the work item with no status.
2. Each intent of this repo that held the line lost it in a change request of its own, which changes
   intents alone. Four of those intents are older than the plans, and a change request with code needs a
   plan for each intent that it touches.
3. `intents/planned-intents.md` is removed.
4. `tests/test_intents.py`: the function `built` in the place of `status_of`; `problems_of` gets the fact
   as an argument; the closed list of the older intents; the three tests of the intent,
   one of them with a plan that is merged before its code.
5. `tests/product.py`: the step "template of an intent", after the setup step.

## Files

- `charter/templates/intent.md`
- `intents/planned-intents.md` removed, and `intents/no-status-line.md` new
- `plans/no-status-line.md`
- `tests/test_intents.py`
- `tests/product.py`

## Not changed

`docs/product.md` and the skills: no text of them names the line. The manifests: 0.3.17 has no tag yet,
so this change goes out with it.
