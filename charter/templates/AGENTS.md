# Rules for work in this repo

Read `docs/product.md` for what this repo builds. The contract is `charter.toml`; it references the
organization source. Each rule below ends with the identifier of its rule in the contract. The scripts of
Charter come with the plugin `charter`: `charter-check`, `charter-gate`, and `charter-setup` are on the
path of the shell while the plugin is enabled.

## How a change moves

- Each change to a source file (code, config, doc) has an issue in the tracker. [change.ticket_per_change]
- Work on a branch. Open a change request that references the issue. A person merges. [tiers.high.approver]
- The author of a change is not its reviewer. [change.author_not_reviewer]
- The contract, this file, the intents, and the workflows are in the high risk tier: a deep review, and
  the leader approves. [tiers.high.paths]
- A person approves each change to a contract. [change.person_approves_contract]
- On GitHub, the workflows `tests` and `verdict` run on each change request. A red check "verdict"
  blocks the merge; its reasons are in the check and in the job log. [checks.quality]

## Plan before the code

A work item has an intent in `intents/<part>.md`: the goal, what is in scope, what is out of scope, and
the acceptance checks. `intents/_template.md` is the form. A person approves the intent through a change
request before the work starts. The skill `tracker` writes the issue and the intent; the issue names the
intent with one line, `Intent: intents/<part>.md`. [tiers.high.paths]
Before the code, the plan `intents/<part>.plan.md`: the steps, the files to change, the tests to add, in
the words of the author, accepted by the person who holds the work item. The verdict checks that the
plan exists; a change request that changes only intents needs no plan. [build.plan_before_code]

## Before a push

Two commands must pass: `charter-gate quality --contract charter.toml` runs the quality checks that the
contract lists, and `charter-check all charter.toml` runs the contract checks. [checks.quality]
[instructions.file] [documents.text_checked]

When a file under a declared code path changes, `docs/product.md` changes too, or the change request
has one line in this exact form: `No document change: <reason>`. [documents.code_paths]
A false failure of a gate: `False failure: <gate>: <reason>`. A finding of the intent reviewer that the
author drops: `Dropped finding: <reason>`. One that the leader marks as wrong: `False finding: <reason>`. [checks.quality]

## Text of commits, change requests, and issues

- No private material: no file paths of a computer, no mail addresses, no tokens. [text.private_material_patterns]
- No session links, and no names of other projects of this organization. [text.session_link_patterns]
  [text.project_name_patterns]

## Review and limits

In a review, look also for broken contracts between parts of the system, and for documents that the
change made stale. [documents.necessary]
Stop and ask a person after the limits of the contract: failed runs of the acceptance checks, review
rounds, or refusals in sequence. [limits.acceptance_loop] [limits.review_loop] [limits.refusals]
The intent reviewer gives each finding a severity. A finding at the threshold or above keeps the
author-reviewer loop open; below it, or at the limit, the loop ends and a person decides. The author side
is the skill `review-loop`. [review.threshold] [limits.review_loop]
