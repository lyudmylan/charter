# Intent: this repo moves to Charter 0.3.15

Work item: #26. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The contract names Charter 0.3.15, each workflow is the one that the setup step of that version writes,
the contract holds the fields that the version asks for, and the contract checks of that version pass.

## In scope

- The order: two change requests. The verdict runs from the main branch and checks a changed contract
  with the scripts of the version that the main branch names. The scripts of 0.3.4 refuse a field that
  they do not know. So the first change request holds no new field.
- The first change request: this intent and its plan; `charter.toml` with the version 0.3.15; the
  workflows `verdict` and `review-intents` in the form of 0.3.15; the new workflows `review-code`, the
  reviewer of the code, and `run`, the run of an agent from an issue.
- The second change request: the new fields of the contract; `tests.yml` with the marked block for the
  toolchain and the job `product`; `AGENTS.md`; `intents/_template.md`; the new `plans/_template.md`.
- The fields, and the decision in each:
  - `checks.no_product_reason`: the repo has no product to start yet. The reason leaves the contract
    when issues 3 and 4 add the product test.
  - `boundary.no_write`: a run of an agent without a person never changes the contract, `AGENTS.md`,
    `CLAUDE.md`, the intents, the workflows, the settings of Claude Code, `package.json`, or the lock
    file. A person adds a package or a script, in a change request of a person.
  - `boundary.no_read`: such a run never reads a `.env` file.
  - `review.code_blocks = false`: the reviewer of the code reports and blocks nothing. The leader ends
    this trial period with a change of the contract.
  - `documents.absent`: `docs/adr/**`, `doc/adr/**`, `doc/arch/adr-*.md`, and `docs/decisions/**`. They
    stay absent because a choice of the architecture and its reason go into `docs/architecture.md`, and
    no separate file holds one decision.
- The plan of this work item is at `intents/charter-upgrade.plan.md`. The verdict of 0.3.4 reads a plan
  only there, and the verdict of 0.3.15 reads both places. Each later plan is `plans/<part>.md`.
- Between the two merges the contract checks of 0.3.15 fail on the main branch: the contract declares
  code paths and names no product test and no reason. The second merge ends this state.

## Out of scope

The product test itself: issues 3 and 4. A risk tier whose approver is an agent. The label and the
secrets of a run and of a merge by the verdict: a person sets them. The move of a plan that exists
at the old place.

## Acceptance checks

## Automatic checks

Each command is the one of Charter 0.3.15, and each one runs on the result of the second change request.

1. The contract passes the contract checks.
   command: `charter-check all charter.toml`
2. The quality checks pass.
   command: `charter-gate quality --contract charter.toml`
3. The gate of the product test passes.
   command: `charter-gate product --contract charter.toml`
4. The contract gives the settings of a run of an agent.
   command: `charter-check boundary charter.toml`
5. The contract names the version 0.3.15.
   command: `grep -q '^version = "0\.3\.15"$' charter.toml`

## Manual checks

6. Each of the five workflows is the file that the setup step of 0.3.15 writes with the values of this
   repo and its toolchain steps. who: the engineer, with a setup in an empty folder and a comparison of
   the files. Not automatic: Charter has no command yet that updates a repo.
7. After the two merges, the evidence record of the next change request names the scripts
   `charter--v0.3.15` and holds the line of the product test with the reason of the contract. who: the leader. Not automatic: the check
   needs the code host.
