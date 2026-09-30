# Scenario: the README and the description of this repo

Work item: #19. Approved by a person on 2026-09-30, in the work item.

## Automatic checks

1. The README exists, is under 40 lines, and contains none of the text patterns of the contract.
   test: `tests/test_charter_check.py::TextFiles.test_pattern_in_text_fails`
   command: `python3 scripts/charter_check.py text README.md --contract charter.toml`

## Manual checks

2. The description of the repo on GitHub equals the first sentence of `docs/product.md`. who: the leader.
3. The README says nothing about a version or a release. who: the leader.
