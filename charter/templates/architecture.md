# Architecture map

The parts of this system, and what runs when. Each change request that adds a part adds a row.

## Parts

| Part | What it does | Where | Since |
|---|---|---|---|
| | | | |

## What runs on a change request

| Workflow | Trust | What it does |
|---|---|---|
| `tests` | Runs the code of the change request; no secret | The quality checks of the contract |
| `verdict` | Runs from the main branch with the scripts of Charter; holds the secret of the organization source | The contract checks, the gates, the evidence record, the check "verdict" |
| `review-intents` | Reads files and posts one comment; no code of the change runs | The intent reviewer, in shadow mode |

## Decisions

A short list of the decisions that shaped the system, newest first, each with its date and its work item.
