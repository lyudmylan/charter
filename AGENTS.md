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
- On GitHub, the workflows `tests` and `verdict` run on each change request. A red check "verdict"
  blocks the merge; its reasons are in the check and in the job log. [checks.quality]

## Before a push

Two commands must pass: `python3 scripts/charter_gate.py quality --contract charter.toml` runs the
quality checks that the contract lists, and `python3 scripts/charter_check.py all charter.toml` runs the
contract checks. [checks.quality] [instructions.file] [documents.text_checked]

When a file under a declared code path changes, `docs/product.md` changes too, or the change request
has one line in this exact form: `No document change: <reason>`. [documents.code_paths]
A false failure of a gate is recorded with one line: `False failure: <gate>: <reason>`. [checks.quality]

## Text of commits, change requests, and issues

- No private material: no file paths of a computer, no mail addresses, no tokens. [text.private_material_patterns]
- No session links, and no names of other projects of this organization. [text.session_link_patterns]
  [text.project_name_patterns]

## Review and limits

In a review, look also for broken contracts between parts of the system, and for documents that the
change made stale. [documents.necessary]
Stop and ask a person after 3 failed runs of the acceptance checks, 3 review rounds, or 3 refusals in
sequence. [limits.acceptance_loop] [limits.review_loop] [limits.refusals]
