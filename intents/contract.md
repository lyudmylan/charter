# Intent: the organization rules and the contract of this repo

Work item: #1. Approved by a person on 2026-09-30, in the work item.

## Goal

The organization rules exist in their own source, and this repo has a contract that references them and states the repo rules.

## In scope

- The private repo `charter-org` with one TOML file: the organization rules. Each rule has a locked flag and a one-line comment. First rules: the text rules for commits and issues (no private material, no names of other projects, no session links); a person approves each change to an organization rule and to a repo contract; the author of a change is not its reviewer; each change to a source file has a ticket.
- Protection of the main branch of `charter-org`, as far as the plan permits: a person approves each change.
- The contract of this repo, one TOML file: the reference to the source (address and version), and the repo rules: the tool declaration (issue tracker, code host, CI); the roles and who holds them; two risk tiers (high: the contract, the gate scripts, the repository instructions; low: everything else) with the review depth and the approver for each; the limits (acceptance-check loop, author-reviewer loop, repeated refusals; default 3); the necessary documents (`docs/product.md`); the lifecycle map with the built-in abilities of Claude Code that this repo uses; the quality checks (the tests of the scripts).
- The schema of the two files, documented on one page in the repo.

## Out of scope

- A copy of the organization file in the repo. The checker resolves the reference from a cache outside the repo, or from a fetch in CI.
- The owners "team" and "person".
- Settings written from the contract.
- The fetch of the source in CI. That is part of the workflow issue.

## Acceptance checks

## Automatic checks

1. The organization source exists, is private, and holds the organization file.
   command: `gh repo view lyudmylan/charter-org --json visibility,isEmpty`
2. The contract of this repo parses as TOML with the Python standard library.
   command: `python3 charter/scripts/charter_check.py validate charter.toml`
3. The contract references the source by address and version, and the checker resolves the reference.
   command: `python3 charter/scripts/charter_check.py check charter.toml`
4. Each rule in both files has an owner and a locked flag. The file that holds a rule is its owner;
   `[locks]` in the organization file marks the locked rules.
   command: `python3 charter/scripts/charter_check.py check charter.toml`
5. The checker accepts the pair: the source and the contract.
   command: `python3 charter/scripts/charter_check.py check charter.toml`

## Manual checks

6. `docs/product.md` and the contract agree: each term of the document has a field in the schema.
   who: the leader, with the table of terms in `docs/contract.md`.
