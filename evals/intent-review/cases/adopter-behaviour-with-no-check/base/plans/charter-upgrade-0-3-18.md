# Plan: this repo moves to Charter 0.3.18 (#42)

Intent: `intents/charter-upgrade-0-3-18.md`, checks 1 to 6.
The intent, the plan, and the change are in one change request; the merge of the leader approves the three.

## Steps

1. Run the setup step of Charter 0.3.18 into an empty folder, with the values of this repo and its
   toolchain block. Compare each file with the file of this repo: check 5. All are equal, so they stay.
2. `charter.toml`: the version 0.3.18.
3. Run the commands of checks 1 to 4 with the scripts of Charter 0.3.18.

## Files

- `charter.toml`
- `intents/charter-upgrade-0-3-18.md`
- `plans/charter-upgrade-0-3-18.md`

## Tests

- None: the change holds no code of the product. Checks 1 to 4 are commands.
