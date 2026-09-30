# Scenario: the organization rules and the contract of this repo

Work item: #1. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. The organization source exists, is private, and holds the organization file.
   command: `gh repo view lyudmylan/charter-org --json visibility,isEmpty`
2. The contract of this repo parses as TOML with the Python standard library.
   command: `python3 scripts/charter_check.py validate charter.toml`
3. The contract references the source by address and version, and the checker resolves the reference.
   command: `python3 scripts/charter_check.py check charter.toml`
4. Each rule in both files has an owner and a locked flag. The file that holds a rule is its owner;
   `[locks]` in the organization file marks the locked rules.
   command: `python3 scripts/charter_check.py check charter.toml`
5. The checker accepts the pair: the source and the contract.
   command: `python3 scripts/charter_check.py check charter.toml`

## Manual checks

6. `docs/product.md` and the contract agree: each term of the document has a field in the schema.
   who: the leader, with the table of terms in `docs/contract.md`.
