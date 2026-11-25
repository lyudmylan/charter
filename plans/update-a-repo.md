# Plan: a repo that is set up moves to a new version of Charter with one command (#97)

Intent: `intents/update-a-repo.md`, checks 1 to 9.
The intent, the plan, and the code reach the leader together, and the merge of the leader approves the three.

## Steps

1. `charter/scripts/charter_update.py`: the command. It reads the version of the contract, fetches the
   templates of that version at its tag into a temporary folder (or takes `--old-templates`), and for each
   generated file compares three texts: the file of the repo, the text of the old version, the text of the
   new version, each with the toolchain block of the repo. It uses the functions of the setup step for the
   block and for the templates.
2. The version line: one substitution in the table `[charter]`, checked by a read of the result.
3. The names of what is new: the fields of the contract template of the new version that the old one does
   not hold and the contract of the repo does not hold; the rule identifiers of the new rules file that the
   old one and the rules file of the repo do not cite.
4. `charter/bin/charter-update`.
5. A try on a copy of an adopter at 0.3.19, by the author: the two reviewer workflows and the version line
   change, and no other file.
6. `docs/contract.md`: the section "The update of a repo" under "The setup step". `docs/product.md` and
   `README.md`: one line each. Both manifests: 0.3.21.
7. Tests: `tests/test_update.py`, seven tests, with no network. `tests/test_setup.py`: the list of the
   commands. `tests/product.py`: the step "update of a repo". `tests/test_workflows.py`: one test read the
   version as an exact number; it reads "this version or later" now.

## Files

- `charter/scripts/charter_update.py`, `charter/bin/charter-update`
- `docs/contract.md`, `docs/product.md`, `README.md`
- `charter/.claude-plugin/plugin.json`, `charter-practices/.claude-plugin/plugin.json`
- `tests/test_update.py`, `tests/test_setup.py`, `tests/product.py`, `tests/test_workflows.py`
- `intents/update-a-repo.md`, `plans/update-a-repo.md`

## What an adopter does

It updates the two plugins on the computer, runs `charter-update` in the root of the repo, reads the
output, and opens one change request.
