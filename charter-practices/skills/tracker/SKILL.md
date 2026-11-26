---
name: tracker
description: Plans and records work in the issue tracker the way this organization does it, with a milestone and its plan file, epics, issues, and an intent for each work item that holds its goal, its scope, and its acceptance checks. Use when the user wants to plan an iteration, create or update a milestone, an epic, or an issue, or close an epic. Do not use for a code review, for an explanation of code or scripts, or for a change to the code itself.
---

# Tracker

Read `charter.toml` first. `tools.issue_tracker` names the tracker; for `github-issues` use `gh`. The
organization source of the contract holds the text rules for issues: no private material, no names of
other projects, no session links. Plan from `docs/product.md`, not from memory. Before you create: search
the tracker for an item on the same subject and update it; no duplicates. Make a decision in the
conversation and record it in the epic or the work item it belongs to. Never open an issue for a decision.

## Structure

- A milestone is a goal, with its acceptance check in the description. Its plan is one file, `milestones/<name>.md`: line 1 `# Milestone: <name>`; for each work item a heading `### #<issue> <title>` and one line
  `Done: <what done means, in the words of a user>`; where they apply, `Tier: high` (the leader merges its change, whatever its files) and a line `Needs:` for each thing that must be true before it starts: `#<issue>` of the plan,
  `Charter <version>`, or `the word of the leader`. Check it with `python3 charter/scripts/charter_check.py milestone <file>`. The merge of the leader approves its work items; a change of the plan is its own change request.
- An epic is what we want to do. Label `epic`. Body: "What we want", the issues as a task list, "Decisions made". The milestone "Roadmap" holds the epics of parts that are decided but not scheduled; their issues come when the part comes near.
- An issue is one actionable item. Body: goal, in scope, out of scope, and one line that names its intent: `Intent: intents/<part>.md`. Each change to a source file has an issue, also a small one.

## The intent of a work item

`intents/<part>.md`: goal, in scope, out of scope, acceptance checks. An automatic check names its test
or its command. A manual check names who does it and why it is not automatic; automatic is the default.
A manual check whose result the agent drafts, a reading of evidence, carries the clause `drafted by the
agent, reviewed by an agent that is not the author, confirmed by <the role>`; the skill `evidence-review`
runs that review. A person approves the intent through a change request; that merge is the approval, and
the work starts after it. Each test cites the intent and the number of its check. Before the code: the agent writes the plan
`plans/<part>.md` (the steps, the files, the tests), then stops and asks the person who holds the work item to accept it,
in the conversation; the code starts after the acceptance. A work item for a run (the label `charter-run`): one change
request that one run can finish, automatic checks only, no network and no secret during the work. A change of a file that
the boundary closes is its own work item, for a person.

## Changes and closing

A change request names its issue: `Closes #N`; the change request of the Plan phase, the intent alone, says `Part of #N`,
which links without closing. When a file under a code path changes and no necessary document, the change request carries
one line: `No document change: <reason>`. A false failure of a gate: `False failure: <gate>: <reason>`. An epic closes when its last issue closes, with a comment on what it delivered.
