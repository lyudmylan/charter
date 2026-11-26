# Plan: this repo moves to Charter 0.3.21 (#52)

Intent: `intents/charter-upgrade-0-3-21.md`, checks 1 to 6.
The intent, the plan, and the change are in one change request; the merge of the leader approves the three.

## Steps

1. Run `charter-update` of Charter 0.3.21 in the root of the repo. It compares each generated file with
   the text of Charter 0.3.19 and with the text of 0.3.21.
2. Its output: the two reviewer workflows are updated, and no file of this repo was changed by hand; the
   other three workflows and the two templates are the same; the version line of the contract moves.
3. Run the commands of checks 1 to 5 with the scripts of Charter 0.3.21.

## Files

- `charter.toml`
- `.github/workflows/review-intents.yml`
- `.github/workflows/review-code.yml`
- `intents/charter-upgrade-0-3-21.md`
- `plans/charter-upgrade-0-3-21.md`

## Tests

- None: the change holds no code of the product. Checks 1 to 5 are commands.
