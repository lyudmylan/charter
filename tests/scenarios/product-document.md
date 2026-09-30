# Scenario: the product document names the source of the organization rules and the scenario files

Work item: #20. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. The document contains none of the text patterns of the contract.
   command: `python3 scripts/charter_check.py text docs/product.md --contract charter.toml`

## Manual checks

2. The document names the source of the organization rules and the reference in the repo contract.
   who: the leader.
3. The document links to the scenario files. who: the leader.
4. The document stays under 100 lines. who: the leader, with `wc -l docs/product.md`.
