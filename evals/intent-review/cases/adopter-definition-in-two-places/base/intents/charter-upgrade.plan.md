# Plan: this repo moves to Charter 0.3.15 (#26)

Intent: `intents/charter-upgrade.md`, checks 1 to 7. The intent and this plan are in the first change
request; each of the two change requests holds its own changes, and the merge by the leader approves
them.

## Steps

1. In an empty folder, run the setup step of Charter 0.3.15 with the values of this repo: the name, the
   organization source, the roles, the code paths, the two quality commands, and a file with the
   toolchain steps of `tests.yml` (pnpm, Node 24, the install of the packages).
2. The first change request. `charter.toml`: the version 0.3.15, and the comment of the table `[build]`.
   From the folder of step 1: `verdict.yml`, `review-intents.yml`, `review-code.yml`, `run.yml`. Check
   the contract with the scripts of 0.3.4: they must pass, because the verdict of the main branch uses
   them on this change request.
3. The second change request, on top of the first. `charter.toml`: the fields of the intent; the risk
   tiers and the list `text_checked` stay as they are. From the folder of step 1: `tests.yml`,
   `AGENTS.md`, `intents/_template.md`, `plans/_template.md`.
4. Run the five commands of the automatic checks with the scripts of 0.3.15.
5. After the merge of the first change request, start the verdict again on the second one.

## Files

- `charter.toml`
- `.github/workflows/verdict.yml`, `.github/workflows/review-intents.yml`,
  `.github/workflows/review-code.yml`, `.github/workflows/run.yml`, `.github/workflows/tests.yml`
- `AGENTS.md`, `intents/_template.md`, `plans/_template.md`
- `intents/charter-upgrade.md`, `intents/charter-upgrade.plan.md`

## Tests

No test of this repo changes. The checks of the intent are commands of Charter.
