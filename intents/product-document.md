# Intent: the product document names the source of the organization rules and the intents

Work item: #20. Approved by a person on 2026-09-30, in the work item.

## Goal

`docs/product.md` states where the organization rules live and how the acceptance checks are kept.

## In scope

- One or two sentences in "How it works": the organization rules live in a source outside each repo; a repo holds a reference, not a copy; the checker compares.
- One sentence on the acceptance checks: they live in the repo as intents, approved by a person before the work starts, with a link to `intents/`.
- The name of the instance (`charter-org`) stays out. The product document describes the product, not one organization.

## Out of scope

- Any other change to the document.

## Acceptance checks

## Automatic checks

1. The document contains none of the text patterns of the contract.
   command: `python3 charter/scripts/charter_check.py text docs/product.md --contract charter.toml`

## Manual checks

2. The document names the source of the organization rules and the reference in the repo contract.
   who: the leader.
3. The document links to the intents. who: the leader.
4. The document stays under 100 lines. who: the leader, with `wc -l docs/product.md`.
