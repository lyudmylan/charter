# Plan: this repo moves to Charter 0.3.16 (#31)

Intent: `intents/charter-upgrade-0-3-16.md`, checks 1 to 7.
The intent, the plan, and the change are in one change request; the merge of the leader approves the three.

## Steps

1. Run the setup step of Charter 0.3.16 into an empty folder, with the values of this repo and its
   toolchain block. Compare each file with the file of this repo: check 6.
2. `.github/workflows/run.yml`: take the file of the setup step. The other workflows, `AGENTS.md`, and
   the two templates are equal to the output, so they stay.
3. `charter.toml`: the version 0.3.16.
4. Run the commands of checks 1 to 5 with the scripts of Charter 0.3.16.

## Files

- `charter.toml`
- `.github/workflows/run.yml`
- `intents/charter-upgrade-0-3-16.md`
- `plans/charter-upgrade-0-3-16.md`

## Tests

- None: the change holds no code of the product. Checks 1 to 5 are commands.
