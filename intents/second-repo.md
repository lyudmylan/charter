# Intent: use Charter in the second repo

Work item: #41. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The second repo of the organization uses Charter: the setup step ran, the gates run on its change
requests, and one real change moved through it with the evidence record.

## In scope

- The plugins installed on the computer from the marketplace.
- The setup step in the second repo; the secret and the ruleset; the cache on the computer.
- One real change: an intent, a plan, the change, the tests, the verdict, the merge by the approver.
- The record of that change, listed with the records command.

## Out of scope

Changes to the product of the second repo beyond that one change. Its name in this repo.

## Acceptance checks

## Automatic checks

1. The records command prints the record of the change in the second repo.
   command: `python3 charter/scripts/charter_facts_github.py records --repo <owner>/<second repo> --last 1`

## Manual checks

2. The verdict of the second repo ran from the fetched version of Charter, and the merge was by the approver of the tier.
   who: the leader, in the record. Not automatic: the second repo is outside this repo.
