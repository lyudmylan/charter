An intent holds no status line

Closes #117

An intent holds no status line. The template of an intent gives the line of the work item without it, and the test of the intents reads from the plan whether a work item is built.

- `charter/templates/intent.md`: the line of the work item ends after the approval.
- `tests/test_intents.py`: an intent with a plan is built, and each of its automatic checks names a test that exists. Thirteen intents are older than the plans; a closed list holds their names, and a test fails when a name outside that list has no plan and claims to be built. One test fails when an intent or the template holds a status line.
- `tests/product.py`: one new step reads the template in the repo that the setup wrote.
- `intents/planned-intents.md` leaves the repo: it described the status line. `intents/no-status-line.md` holds the rule that stays, an intent that is not built needs no existing test.

The 23 intents of this repo lost the line in the change request before this one.

Intent: `intents/no-status-line.md`. Plan: `plans/no-status-line.md`. The manifests stay at 0.3.17, which has no tag yet.

No document change: no text of `docs/` names the status line, and the product did not change for a user.
