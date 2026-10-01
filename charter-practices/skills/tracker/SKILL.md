---
name: tracker
description: Plans and records work in the issue tracker the way this organization does it, with a milestone, epics, issues, and an intent for each work item that holds its goal, its scope, and its acceptance checks. Use when the user wants to plan an iteration, create or update a milestone, an epic, or an issue, or close an epic. Do not use for a code review, for an explanation of code or scripts, or for a change to the code itself.
---

# Tracker

Read `charter.toml` first. `tools.issue_tracker` names the tracker; for `github-issues` use `gh`. The
organization source of the contract holds the text rules for issues: no private material, no names of
other projects, no session links. Plan from `docs/product.md`, not from memory.

## Before you create
Search the tracker for an item on the same subject and update it. No duplicates. Make a decision in the
conversation and record it in the epic or the work item it belongs to. Never open an issue for a decision.

## Structure

- A milestone is a goal, with its acceptance check in the description.
- An epic is what we want to do. Label `epic`. Body: "What we want", the issues as a task list,
  "Decisions made". The milestone "Roadmap" holds the epics of parts that are decided but not scheduled;
  their issues come when the part comes near.
- An issue is one actionable item. Body: goal, in scope, out of scope, and one line that names its
  intent: `Intent: intents/<part>.md`. Each change to a source file has an issue, also a small one.

## The intent of a work item

`intents/<part>.md`: goal, in scope, out of scope, acceptance checks. An automatic check names
its test or its command. A manual check names who does it and why it is not automatic; automatic is the
default. A person approves the intent through a change request; that merge is the approval, and the work
starts after it. Each test cites the intent and the number of its check. Before the code: the agent writes
the plan `intents/<part>.plan.md` (the steps, the files, the tests), then stops and asks the person who
holds the work item to accept it, in the conversation; the code starts after the acceptance.

## Changes and closing

A change request names its issue: `Closes #N`. When a file under a code path changes and no necessary
document, the change request carries one line: `No document change: <reason>`. A false failure of a
gate: `False failure: <gate>: <reason>`. An epic closes when its last issue closes, with a comment that
names what it delivered.
