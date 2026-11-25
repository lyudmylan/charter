# Intent: a repo that is set up moves to a new version of Charter with one command

Work item: #97. Approval: a person merges the change request that adds this file.

## Goal

In a repo that is set up, one command makes the change of an upgrade in the working folder: the new
version number in the contract, and each generated file in the text of the new version. No step of a
workflow is copied by hand, and no change that the repo made by hand is lost without notice.

## In scope

- The command `charter-update`, the script `charter/scripts/charter_update.py`, with its entry in `charter/bin/`.
- A file that holds no content of the repo gets the text of the new version: the five workflows, and the
  templates of an intent and of a plan. The block of the toolchain of the repo stays.
- The command fetches the templates of the version that the contract names, at its tag, and compares. A
  file that the repo changed by hand is written too, and the command prints the lines of the repo. When the
  old version cannot be fetched, each changed file is named as not compared.
- A file that holds content of the repo is not changed: the contract but for its version line, the rules
  file, the documents. The command names each field that the contract template of the new version adds and
  each rule that its rules file adds.
- A form that writes nothing, `--check`.
- The command refuses a contract that names a newer version than the installed Charter, and one whose
  version line it cannot change. A refusal comes before the first write.
- `docs/contract.md`, `docs/product.md`, `README.md`, and both manifests: 0.3.21.

## Out of scope

- The change request: a person or an agent opens it. A run of an agent that opens the update is later work.
- A change of the schema version of the contract.
- A change of the contract or of the rules file of the repo by the command: it names what is new.
- The plugins on the computer of a person: `claude plugin update` moves them.
- A check on the code host that a repo is behind the newest version.

## Acceptance checks

### Automatic checks

1. In a repo that the setup step made from an older version, each generated file has the text of the new
   version after the update, and the toolchain of the repo is in `tests` and in `run`. test: `tests/test_update.py::Update.test_the_generated_files_move_and_the_block_of_the_repo_stays`
2. A workflow that the repo changed by hand is written, named, and its line is printed. test: `tests/test_update.py::Update.test_a_file_that_the_repo_changed_by_hand_is_named`
3. In the contract only the version line moves; the rules file and the documents stay; the new field and the
   new rule are named. test: `tests/test_update.py::Update.test_a_file_with_content_of_the_repo_keeps_it`
4. The check form writes no file. test: `tests/test_update.py::Update.test_the_check_form_writes_no_file`
5. Nothing to change after an update; a newer contract and a version line that cannot be changed are
   refused before the first write; a folder with no contract and a version that is no row of numbers
   cannot run. test: `tests/test_update.py::Update.test_the_command_refuses_and_ends`
6. Without the older templates each changed file is named as not compared. test: `tests/test_update.py::Update.test_without_the_older_templates_each_changed_file_is_named`
7. The command is in `charter/bin/`, and the documents and both manifests carry it. test: `tests/test_update.py::Update.test_the_command_the_documents_and_the_version`
8. The installed command runs on a new repo and finds nothing to change. command: `python3 tests/product.py`, step "update of a repo".

### Manual checks

9. Two adopters move from 0.3.20 to this version with the command, each in one change request. The leader
   reads that each change request holds the version line and the changed workflows only, and that its
   verdict is ready. It is manual because it runs in other repos, after the release of this version. The
   check follows the merge; a failure opens a new issue and does not reopen this change request.
