# Plan: this repo moves to Charter 0.3.17 (#38)

Intent: `intents/charter-upgrade-0-3-17.md`, checks 1 to 8.
The intent, the plan, and the change are in one change request; the merge of the leader approves the three.

## Steps

1. Run the setup step of Charter 0.3.17 into an empty folder, with the values of this repo and its
   toolchain block. Compare each file with the file of this repo: check 7.
2. `.github/workflows/run.yml` and `intents/_template.md`: take the files of the setup step. The other
   workflows, `AGENTS.md`, and the template of a plan are equal to the output, so they stay.
3. `charter.toml`: the version 0.3.17.
4. The six intents that hold `Status: planned`: remove it from the line of the work item.
5. Run the commands of checks 1 to 6 with the scripts of Charter 0.3.17.

## Files

- `charter.toml`
- `.github/workflows/run.yml`
- `intents/_template.md`
- `intents/charter-upgrade.md`, `intents/charter-upgrade-0-3-16.md`, `intents/http-endpoint.md`,
  `intents/product-test.md`, `intents/review-corrections.md`, `intents/urgent-event-knock.md`
- `intents/charter-upgrade-0-3-17.md`
- `plans/charter-upgrade-0-3-17.md`

## Tests

- None: the change holds no code of the product. Checks 1 to 6 are commands.
