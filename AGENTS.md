# Rules for work in this repo

Read `docs/product.md` for what Charter is. The contract is `charter.toml`; it references the organization
source. Each rule below ends with the identifier of its rule in the contract.

## How a change moves

- Each change to a source file (code, config, doc) has an issue in the tracker. [change.ticket_per_change]
- Work on a branch. Open a change request that references the issue. A person merges. [tiers.high.approver]
- The author of a change is not its reviewer. [change.author_not_reviewer]
- The contract, the schema, the scripts, the tests, the workflows, and this file are in the high risk
  tier: a deep review, and the leader approves. [tiers.high.paths]
- A person approves each change to a contract. [change.person_approves_contract]
- On GitHub, the workflow `gates` runs the checks and the verdict on each change request. A red verdict
  blocks the merge; its reasons are in the log of the job `verdict`. [checks.quality]

## Before a push

All quality checks of the contract must pass. [checks.quality]

- `python3 -m unittest discover -s tests`
- `python3 scripts/charter_check.py check charter.toml`
- `python3 scripts/charter_check.py instructions AGENTS.md --contract charter.toml`
- `python3 scripts/charter_check.py text README.md --contract charter.toml`
- `python3 scripts/charter_check.py text docs/product.md --contract charter.toml`

When a file under a declared code path changes, `docs/product.md` changes too, or the change request
states why not. [documents.code_paths]

## Text of commits, change requests, and issues

- No private material: no file paths of a computer, no mail addresses, no tokens. [text.private_material_patterns]
- No session links, and no names of other projects of this organization. [text.session_link_patterns]
  [text.project_name_patterns]

## Review and limits

In a review, look also for broken contracts between parts of the system, and for documents that the
change made stale. [documents.necessary]
Stop and ask a person after 3 failed runs of the acceptance checks, 3 review rounds, or 3 refusals in
sequence. [limits.acceptance_loop] [limits.review_loop] [limits.refusals]
