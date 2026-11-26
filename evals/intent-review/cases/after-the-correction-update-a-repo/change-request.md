A repo that is set up moves to a new version of Charter with one command

Closes #97

One command, `charter-update`, makes the change of an upgrade in the working folder of a repo that is set up.

- Each generated file gets the text of the new version: the five workflows, and the templates of an intent and of a plan. The toolchain block of the repo stays.
- The command fetches the templates of the version that the contract names and compares. A file that the repo changed by hand is written, named, and its lines are printed. Without the old version, each changed file is named as not compared.
- A file with content of the repo is not changed. In the contract only the version line moves. The command names each field and each rule that the new version adds.
- `--check` writes no file. A contract of a newer version is refused.

A try on copies of two adopters at 0.3.19 gave the same result in both: the two reviewer workflows and the version line change, and no other file.

The intent, the plan, and the code are in this one change request; the merge approves the three. Both manifests: 0.3.21.
