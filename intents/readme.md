# Intent: the README and the description of this repo

Work item: #19. Approved by a person on 2026-09-30, in the work item.

## Goal

A reader of this repo on GitHub sees what Charter is, what the files are, and how to run the checks.

## In scope

- `README.md`: what Charter is in two sentences; the documents (`docs/product.md`, `docs/contract.md`, `AGENTS.md`); the layout of the repo; how to run the checks; the license.
- The description of the repo on GitHub: the first sentence of `docs/product.md`.
- No version number and no release statement. The version lives in the plugin manifest only.

## Out of scope

- Installation instructions. There is no plugin yet.

## Acceptance checks

## Automatic checks

1. The README exists, is under 40 lines, and contains none of the text patterns of the contract.
   test: `tests/test_charter_check.py::TextFiles.test_pattern_in_text_fails`
   command: `python3 charter/scripts/charter_check.py text README.md --contract charter.toml`

## Manual checks

2. The description of the repo on GitHub equals the first sentence of `docs/product.md`. who: the leader.
3. The README says nothing about a version or a release. who: the leader.
